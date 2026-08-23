from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres.tenant_context import tenant_admin_transaction
from amesh.domain import (
    SYSTEM_TENANT_ID,
    AdministrationAuditEntry,
    FeatureFlag,
    FeatureFlagDecision,
    FeatureFlagScope,
    new_runtime_id,
    resolve_feature_flag,
)
from amesh.ports import FeatureFlagRepository, FeatureFlagVersionConflict

_FLAG_COLUMNS = """
    f.id,
    f.flag_key,
    f.scope,
    t.slug AS tenant_slug,
    f.namespace,
    f.enabled,
    f.description,
    f.version,
    f.updated_by,
    f.created_at,
    f.updated_at
"""


class PostgresFeatureFlagRepository(FeatureFlagRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def upsert(
        self,
        flag: FeatureFlag,
        *,
        actor_id: str,
        expected_version: int | None = None,
        administration_audit: dict[str, object] | None = None,
    ) -> FeatureFlag:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, flag.tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO feature_flags (
                                id, flag_key, scope, tenant_id, namespace, enabled,
                                description, version, updated_by, created_at, updated_at
                            ) VALUES (
                                :id, :flag_key, :scope, :tenant_id, :namespace, :enabled,
                                :description, 1, :actor_id, :created_at, :updated_at
                            )
                            ON CONFLICT ON CONSTRAINT feature_flags_scope_identity DO UPDATE SET
                                enabled = EXCLUDED.enabled,
                                description = EXCLUDED.description,
                                version = feature_flags.version + 1,
                                updated_by = EXCLUDED.updated_by,
                                updated_at = EXCLUDED.updated_at
                            WHERE CAST(:expected_version AS bigint) IS NULL
                               OR feature_flags.version = CAST(:expected_version AS bigint)
                            RETURNING *
                            """
                        ),
                        {
                            "id": flag.id,
                            "flag_key": flag.key,
                            "scope": flag.scope.value,
                            "tenant_id": tenant_uuid,
                            "namespace": flag.namespace,
                            "enabled": flag.enabled,
                            "description": flag.description,
                            "actor_id": actor_id,
                            "created_at": flag.created_at,
                            "updated_at": datetime.now(UTC),
                            "expected_version": expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise FeatureFlagVersionConflict("feature flag version changed")
            persisted = _to_feature_flag(row, tenant_slug=flag.tenant_id)
            await _write_audit(
                connection,
                tenant_id=tenant_uuid or SYSTEM_TENANT_ID,
                actor_id=actor_id,
                action="feature-flag.upsert",
                resource_id=f"{flag.scope.value}:{flag.key}",
                outcome="SUCCESS",
                reason="feature flag scope updated",
                evidence={
                    "scope": flag.scope.value,
                    "namespace": flag.namespace,
                    "enabled": flag.enabled,
                    "version": persisted.version,
                },
            )
            if administration_audit is not None:
                evidence = administration_audit["evidence"]
                if not isinstance(evidence, dict):
                    raise TypeError("administration audit evidence must be an object")
                await _write_audit(
                    connection,
                    tenant_id=tenant_uuid or SYSTEM_TENANT_ID,
                    actor_id=actor_id,
                    action=str(administration_audit["action"]),
                    resource_id=str(administration_audit["resourceId"]),
                    outcome="SUCCESS",
                    reason=str(administration_audit["reason"]),
                    evidence=evidence,
                    resource_type="administration_control",
                )
            return persisted

    async def list_for_context(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
    ) -> tuple[FeatureFlag, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_FLAG_COLUMNS}
                            FROM feature_flags f
                            LEFT JOIN tenants t ON t.id = f.tenant_id
                            WHERE f.scope = 'INSTANCE'
                               OR (f.scope = 'TENANT' AND t.slug = :tenant_id)
                               OR (
                                    f.scope = 'NAMESPACE'
                                    AND t.slug = :tenant_id
                                    AND f.namespace = :namespace
                               )
                            ORDER BY f.flag_key, f.scope
                            """
                        ),
                        {"tenant_id": tenant_id, "namespace": namespace},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_to_feature_flag(row) for row in rows)

    async def evaluate(
        self,
        key: str,
        tenant_id: str,
        *,
        namespace: str | None = None,
        default: bool = False,
    ) -> FeatureFlagDecision:
        flags = await self.list_for_context(tenant_id, namespace=namespace)
        return resolve_feature_flag(key, flags, default=default)

    async def audit_configuration_reload(
        self,
        *,
        actor_id: str,
        outcome: str,
        changed_fields: tuple[str, ...],
        reason: str,
    ) -> None:
        async with tenant_admin_transaction(self._engine) as connection:
            await _write_audit(
                connection,
                tenant_id=SYSTEM_TENANT_ID,
                actor_id=actor_id,
                action="configuration.reload",
                resource_id="process-configuration",
                outcome=outcome,
                reason=reason,
                evidence={"changedFields": list(changed_fields)},
            )

    async def audit_administration_action(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        action: str,
        resource_id: str,
        outcome: str,
        reason: str,
        evidence: dict[str, object],
    ) -> None:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            if tenant_uuid is None:
                raise LookupError("tenant unavailable")
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action=action,
                resource_id=resource_id,
                outcome=outcome,
                reason=reason,
                evidence=evidence,
                resource_type="administration_control",
            )

    async def list_administration_audit(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[AdministrationAuditEntry, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            if tenant_uuid is None:
                raise LookupError("tenant unavailable")
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT event_id, actor_id, action, resource_id, outcome,
                                   reason, evidence, occurred_at
                            FROM audit_events
                            WHERE tenant_id = :tenant_id
                              AND resource_type = 'administration_control'
                            ORDER BY occurred_at DESC, event_id DESC
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(
            AdministrationAuditEntry(
                eventId=str(row["event_id"]),
                actorId=str(row["actor_id"]),
                action=str(row["action"]),
                resourceId=str(row["resource_id"]),
                outcome=str(row["outcome"]),
                reason=str(row["reason"]),
                evidence=dict(row["evidence"]),
                occurredAt=row["occurred_at"],
            )
            for row in rows
        )


async def _resolve_tenant_uuid(
    connection: AsyncConnection,
    tenant_slug: str | None,
) -> UUID | None:
    if tenant_slug is None:
        return None
    value = await connection.scalar(
        text(
            """
            SELECT id
            FROM tenants
            WHERE slug = :tenant_slug AND status = 'ACTIVE' AND lifecycle = 'ACTIVE'
            """
        ),
        {"tenant_slug": tenant_slug},
    )
    if value is None:
        raise LookupError("tenant unavailable")
    return UUID(str(value))


def _to_feature_flag(
    row: RowMapping,
    *,
    tenant_slug: str | None = None,
) -> FeatureFlag:
    return FeatureFlag(
        id=UUID(str(row["id"])),
        key=str(row["flag_key"]),
        scope=FeatureFlagScope(str(row["scope"])),
        tenant_id=tenant_slug if tenant_slug is not None else row.get("tenant_slug"),
        namespace=row["namespace"],
        enabled=bool(row["enabled"]),
        description=str(row["description"]),
        version=int(row["version"]),
        updated_by=str(row["updated_by"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def _write_audit(
    connection: AsyncConnection,
    *,
    tenant_id: UUID,
    actor_id: str,
    action: str,
    resource_id: str,
    outcome: str,
    reason: str,
    evidence: dict[str, object],
    resource_type: str = "configuration",
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                tenant_id, event_id, actor_id, action, resource_type, resource_id,
                outcome, reason, source, evidence, occurred_at
            ) VALUES (
                :tenant_id, :event_id, :actor_id, :action, :resource_type, :resource_id,
                :outcome, :reason, CAST(:source AS jsonb), CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "event_id": new_runtime_id(),
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "outcome": outcome,
            "reason": reason,
            "source": json.dumps({"component": "configuration-repository"}),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
