from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain.promotion import (
    EvidenceArtifact,
    PromotionConcurrencyError,
    PromotionPolicy,
    PromotionTargetKind,
    ReleaseAction,
    ReleaseHistoryEntry,
    ReleaseState,
    ReleaseTarget,
)
from amesh.ports.errors import NotFoundError
from amesh.ports.promotion_repository import PromotionRepository

from .repository_support import PostgresRepositoryBase


class PostgresPromotionRepository(PostgresRepositoryBase, PromotionRepository):
    """Tenant-isolated immutable evidence and command/event release state."""

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def put_policy(self, policy: PromotionPolicy) -> PromotionPolicy:
        payload = policy.model_dump(mode="json", by_alias=True)
        async with self._services.transactions.tenant(policy.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        INSERT INTO promotion_policies (
                            policy_id, tenant_id, target_kind, target_key, target_revision,
                            configuration_digest, policy_digest, policy, created_by, created_at
                        ) VALUES (
                            :policy_id, :tenant_id, :target_kind, :target_key, :target_revision,
                            :configuration_digest, :policy_digest, CAST(:policy AS jsonb),
                            :created_by, :created_at
                        )
                        ON CONFLICT (tenant_id, target_kind, target_key, policy_digest) DO NOTHING
                        RETURNING policy_id, tenant_id, policy
                        """
                        ),
                        {
                            "policy_id": policy.policy_id,
                            "tenant_id": tenant_uuid,
                            "target_kind": policy.target_kind.value,
                            "target_key": policy.target_key,
                            "target_revision": policy.target_revision,
                            "configuration_digest": policy.configuration_digest,
                            "policy_digest": policy.digest,
                            "policy": self._services.codec.dumps(payload),
                            "created_by": policy.created_by,
                            "created_at": policy.created_at,
                        },
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                            SELECT policy_id, tenant_id, policy
                            FROM promotion_policies
                            WHERE tenant_id = :tenant_id AND policy_digest = :policy_digest
                            """
                            ),
                            {"tenant_id": tenant_uuid, "policy_digest": policy.digest},
                        )
                    )
                    .mappings()
                    .first()
                )
            if row is None:
                raise NotFoundError(
                    "promotion policy",
                    policy.policy_id,
                    message="promotion policy was not stored",
                )
            stored = _policy(row["policy"])
            if stored.digest != policy.digest:
                raise ValueError("immutable promotion policy conflicts with stored policy")
            return stored

    async def get_policy(self, tenant_id: str, policy_id: UUID) -> PromotionPolicy:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            "SELECT policy FROM promotion_policies WHERE tenant_id = :tenant_id AND policy_id = :policy_id"
                        ),
                        {"tenant_id": tenant_uuid, "policy_id": policy_id},
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            raise NotFoundError(
                "promotion policy",
                policy_id,
                message="promotion policy does not exist",
            )
        return _policy(row["policy"])

    async def put_evidence(self, artifact: EvidenceArtifact) -> EvidenceArtifact:
        payload = artifact.model_dump(mode="json", by_alias=True)
        async with self._services.transactions.tenant(artifact.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        INSERT INTO promotion_evidence (
                            evidence_id, tenant_id, kind, evidence_key, evidence_digest,
                            configuration_digest, passed, captured_at, expires_at, details
                        ) VALUES (
                            :evidence_id, :tenant_id, :kind, :evidence_key, :evidence_digest,
                            :configuration_digest, :passed, :captured_at, :expires_at,
                            CAST(:details AS jsonb)
                        )
                        ON CONFLICT (tenant_id, evidence_digest) DO NOTHING
                        RETURNING *
                        """
                        ),
                        {
                            "evidence_id": artifact.evidence_id,
                            "tenant_id": tenant_uuid,
                            "kind": artifact.kind.value,
                            "evidence_key": artifact.key,
                            "evidence_digest": artifact.digest,
                            "configuration_digest": artifact.configuration_digest,
                            "passed": artifact.passed,
                            "captured_at": artifact.captured_at,
                            "expires_at": artifact.expires_at,
                            "details": self._services.codec.dumps(payload.get("details", {})),
                        },
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                "SELECT * FROM promotion_evidence WHERE tenant_id = :tenant_id AND evidence_digest = :digest"
                            ),
                            {"tenant_id": tenant_uuid, "digest": artifact.digest},
                        )
                    )
                    .mappings()
                    .first()
                )
            if row is None:
                raise NotFoundError(
                    "promotion evidence",
                    artifact.evidence_id,
                    message="promotion evidence was not stored",
                )
            stored = _evidence(row, artifact.tenant_id)
            if stored.model_dump(mode="json", by_alias=True) != artifact.model_dump(
                mode="json", by_alias=True
            ):
                raise ValueError("immutable promotion evidence conflicts with stored evidence")
            return stored

    async def list_evidence(
        self, tenant_id: str, *, configuration_digest: str
    ) -> Sequence[EvidenceArtifact]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM promotion_evidence
                        WHERE tenant_id = :tenant_id AND configuration_digest = :configuration_digest
                        ORDER BY captured_at, evidence_id
                        """
                        ),
                        {"tenant_id": tenant_uuid, "configuration_digest": configuration_digest},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_evidence(row, tenant_id) for row in rows)

    async def get_target(self, tenant_id: str, target_kind: str, target_key: str) -> ReleaseTarget:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM release_targets
                        WHERE tenant_id = :tenant_id AND target_kind = :target_kind AND target_key = :target_key
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "target_kind": target_kind,
                            "target_key": target_key,
                        },
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            return ReleaseTarget(
                tenantId=tenant_id,
                targetKind=PromotionTargetKind(target_kind),
                targetKey=target_key,
            )
        return _target(row, tenant_id)

    async def apply_target(
        self,
        target: ReleaseTarget,
        *,
        action: str,
        to_revision: int | None,
        to_configuration_digest: str | None,
        gate_digest: str | None,
        expected_version: int,
        actor_id: str,
        reason: str,
    ) -> tuple[ReleaseTarget, ReleaseHistoryEntry]:
        if expected_version != target.version:
            raise PromotionConcurrencyError("release target version is stale")
        if action == ReleaseAction.PROMOTE.value and (
            to_revision is None or to_configuration_digest is None
        ):
            raise ValueError("promotion requires a target revision and configuration digest")
        next_version = expected_version + 1
        now = self._services.clock.now()
        async with self._services.transactions.tenant(target.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            current = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM release_targets
                        WHERE tenant_id = :tenant_id AND target_kind = :target_kind AND target_key = :target_key
                        FOR UPDATE
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "target_kind": target.target_kind.value,
                            "target_key": target.target_key,
                        },
                    )
                )
                .mappings()
                .first()
            )
            current_version = int(current["version"]) if current is not None else 0
            if current_version != expected_version:
                raise PromotionConcurrencyError("release target changed during the action")
            await connection.execute(
                text(
                    """
                    INSERT INTO release_targets (
                        tenant_id, target_kind, target_key, active_revision,
                        active_configuration_digest, state, version, updated_at
                    ) VALUES (
                        :tenant_id, :target_kind, :target_key, :active_revision,
                        :active_configuration_digest, :state, :version, :updated_at
                    )
                    ON CONFLICT (tenant_id, target_kind, target_key) DO UPDATE SET
                        active_revision = EXCLUDED.active_revision,
                        active_configuration_digest = EXCLUDED.active_configuration_digest,
                        state = EXCLUDED.state,
                        version = EXCLUDED.version,
                        updated_at = EXCLUDED.updated_at
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "target_kind": target.target_kind.value,
                    "target_key": target.target_key,
                    "active_revision": to_revision
                    if action != ReleaseAction.KILL_SWITCH.value
                    else target.active_revision,
                    "active_configuration_digest": to_configuration_digest
                    if action != ReleaseAction.KILL_SWITCH.value
                    else target.active_configuration_digest,
                    "state": ReleaseState.KILLED.value
                    if action == ReleaseAction.KILL_SWITCH.value
                    else ReleaseState.ACTIVE.value,
                    "version": next_version,
                    "updated_at": now,
                },
            )
            entry = ReleaseHistoryEntry(
                tenantId=target.tenant_id,
                targetKind=target.target_kind,
                targetKey=target.target_key,
                action=ReleaseAction(action),
                fromRevision=target.active_revision,
                toRevision=to_revision,
                gateDigest=gate_digest,
                toConfigurationDigest=to_configuration_digest,
                actorId=actor_id,
                reason=reason,
                version=next_version,
                occurredAt=now,
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO release_history (
                        event_id, tenant_id, target_kind, target_key, action,
                        from_revision, to_revision, to_configuration_digest, gate_digest, actor_id, reason, version, occurred_at
                    ) VALUES (
                        :event_id, :tenant_id, :target_kind, :target_key, :action,
                        :from_revision, :to_revision, :to_configuration_digest, :gate_digest, :actor_id, :reason, :version, :occurred_at
                    )
                    """
                ),
                {
                    "event_id": entry.event_id,
                    "tenant_id": tenant_uuid,
                    "target_kind": target.target_kind.value,
                    "target_key": target.target_key,
                    "action": action,
                    "from_revision": entry.from_revision,
                    "to_revision": entry.to_revision,
                    "to_configuration_digest": entry.to_configuration_digest,
                    "gate_digest": gate_digest,
                    "actor_id": actor_id,
                    "reason": reason,
                    "version": next_version,
                    "occurred_at": now,
                },
            )
            return (
                ReleaseTarget(
                    tenantId=target.tenant_id,
                    targetKind=target.target_kind,
                    targetKey=target.target_key,
                    activeRevision=(
                        target.active_revision
                        if action == ReleaseAction.KILL_SWITCH.value
                        else to_revision
                    ),
                    activeConfigurationDigest=(
                        target.active_configuration_digest
                        if action == ReleaseAction.KILL_SWITCH.value
                        else to_configuration_digest
                    ),
                    state=(
                        ReleaseState.KILLED
                        if action == ReleaseAction.KILL_SWITCH.value
                        else ReleaseState.ACTIVE
                    ),
                    version=next_version,
                    updatedAt=now,
                ),
                entry,
            )

    async def history(
        self, tenant_id: str, target_kind: str, target_key: str
    ) -> Sequence[ReleaseHistoryEntry]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM release_history
                        WHERE tenant_id = :tenant_id AND target_kind = :target_kind AND target_key = :target_key
                        ORDER BY version
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "target_kind": target_kind,
                            "target_key": target_key,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_history(row, tenant_id) for row in rows)


def _json(value: Any) -> Any:
    return json.loads(value) if isinstance(value, str) else value


def _policy(value: Any) -> PromotionPolicy:
    return PromotionPolicy.model_validate(_json(value))


def _evidence(row: RowMapping, tenant_id: str) -> EvidenceArtifact:
    return EvidenceArtifact(
        evidenceId=row["evidence_id"],
        tenantId=tenant_id,
        kind=row["kind"],
        key=row["evidence_key"],
        digest=row["evidence_digest"],
        configurationDigest=row["configuration_digest"],
        passed=row["passed"],
        capturedAt=row["captured_at"],
        expiresAt=row["expires_at"],
        details=_json(row["details"]),
    )


def _target(row: RowMapping, tenant_id: str) -> ReleaseTarget:
    return ReleaseTarget(
        tenantId=tenant_id,
        targetKind=row["target_kind"],
        targetKey=row["target_key"],
        activeRevision=row["active_revision"],
        activeConfigurationDigest=row["active_configuration_digest"],
        state=row["state"],
        version=row["version"],
        updatedAt=row["updated_at"],
    )


def _history(row: RowMapping, tenant_id: str) -> ReleaseHistoryEntry:
    return ReleaseHistoryEntry(
        eventId=row["event_id"],
        tenantId=tenant_id,
        targetKind=row["target_kind"],
        targetKey=row["target_key"],
        action=row["action"],
        fromRevision=row["from_revision"],
        toRevision=row["to_revision"],
        toConfigurationDigest=row["to_configuration_digest"],
        gateDigest=row["gate_digest"],
        actorId=row["actor_id"],
        reason=row["reason"],
        version=row["version"],
        occurredAt=row["occurred_at"],
    )


__all__ = ["PostgresPromotionRepository"]
