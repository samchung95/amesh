from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.policy import (
    PolicyDecision,
    PolicyDocument,
    PolicyRevision,
    PolicyScope,
)

from .tenant_context import tenant_transaction


class PostgresAdmissionPolicyRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def effective_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str,
    ) -> tuple[PolicyRevision, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM admission_policy_revisions
                            WHERE active
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                              AND (scope <> 'NAMESPACE' OR namespace_name = :namespace)
                            ORDER BY
                                CASE scope
                                    WHEN 'INSTANCE' THEN 1
                                    WHEN 'TENANT' THEN 2
                                    ELSE 3
                                END,
                                policy_key,
                                revision
                            """
                        ),
                        {"tenant_id": tenant_uuid, "namespace": namespace},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_policy_revision(row, tenant_id) for row in rows)

    async def save_revision(
        self,
        tenant_id: str,
        document: PolicyDocument,
        *,
        actor_id: str,
    ) -> PolicyRevision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            policy_tenant_id = (
                None if document.scope is PolicyScope.INSTANCE else tenant_uuid
            )
            current = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT policy_id, revision
                            FROM admission_policy_revisions
                            WHERE active
                              AND policy_key = :policy_key
                              AND scope = :scope
                              AND tenant_id IS NOT DISTINCT FROM :policy_tenant_id
                              AND namespace_name IS NOT DISTINCT FROM :namespace
                            FOR UPDATE
                            """
                        ),
                        {
                            "policy_key": document.policy_key,
                            "scope": document.scope.value,
                            "policy_tenant_id": policy_tenant_id,
                            "namespace": document.namespace,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            policy_id = (
                UUID(str(current["policy_id"])) if current is not None else new_runtime_id()
            )
            revision = int(current["revision"]) + 1 if current is not None else 1
            if current is not None:
                await connection.execute(
                    text(
                        """
                        UPDATE admission_policy_revisions
                        SET active = false
                        WHERE policy_id = :policy_id AND active
                        """
                    ),
                    {"policy_id": policy_id},
                )
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO admission_policy_revisions (
                                policy_id, revision, tenant_id, namespace_name, policy_key,
                                scope, active, digest, document, created_by
                            ) VALUES (
                                :policy_id, :revision, :tenant_id, :namespace,
                                :policy_key, :scope, true, :digest,
                                CAST(:document AS jsonb), :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "policy_id": policy_id,
                            "revision": revision,
                            "tenant_id": policy_tenant_id,
                            "namespace": document.namespace,
                            "policy_key": document.policy_key,
                            "scope": document.scope.value,
                            "digest": document.digest,
                            "document": document.model_dump_json(by_alias=True),
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="admission.policy.revision.save",
                resource_id=str(policy_id),
                reason=f"saved {document.policy_key}@{revision}",
                evidence={
                    "policyKey": document.policy_key,
                    "revision": revision,
                    "digest": document.digest,
                    "scope": document.scope.value,
                },
            )
        return _policy_revision(row, tenant_id)

    async def get_revision(
        self,
        tenant_id: str,
        policy_key: str,
        *,
        revision: int | None = None,
    ) -> PolicyRevision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM admission_policy_revisions
                            WHERE policy_key = :policy_key
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                              AND (
                                  CAST(:revision AS integer) IS NULL
                                  OR revision = CAST(:revision AS integer)
                              )
                              AND (CAST(:revision AS integer) IS NOT NULL OR active)
                            ORDER BY
                                CASE scope
                                    WHEN 'NAMESPACE' THEN 1
                                    WHEN 'TENANT' THEN 2
                                    ELSE 3
                                END,
                                revision DESC
                            LIMIT 1
                            """
                        ),
                        {
                            "policy_key": policy_key,
                            "tenant_id": tenant_uuid,
                            "revision": revision,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"admission policy {policy_key!r} does not exist")
        return _policy_revision(row, tenant_id)

    async def record_decision(
        self,
        decision: PolicyDecision,
        *,
        actor_id: str,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        async with tenant_transaction(self._engine, decision.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            await connection.execute(
                text(
                    """
                    INSERT INTO admission_policy_decisions (
                        id, tenant_id, namespace_name, stage, outcome, allowed,
                        actor_id, flow_key, flow_revision, execution_id, task_run_id,
                        decision, decided_at
                    ) VALUES (
                        :id, :tenant_id, :namespace, :stage, :outcome, :allowed,
                        :actor_id, :flow_id, :flow_revision, :execution_id, :task_run_id,
                        CAST(:decision AS jsonb), :decided_at
                    )
                    """
                ),
                {
                    "id": decision.decision_id,
                    "tenant_id": tenant_uuid,
                    "namespace": decision.namespace,
                    "stage": decision.stage.value,
                    "outcome": decision.outcome.value,
                    "allowed": decision.allowed,
                    "actor_id": actor_id,
                    "flow_id": decision.flow_id,
                    "flow_revision": decision.flow_revision,
                    "execution_id": execution_id,
                    "task_run_id": task_run_id,
                    "decision": decision.model_dump_json(by_alias=True),
                    "decided_at": decision.decided_at,
                },
            )
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="admission.policy.evaluate",
                resource_id=str(decision.decision_id),
                outcome="SUCCESS" if decision.allowed else "DENIED",
                reason=(
                    f"{decision.stage.value} policy decision: {decision.outcome.value}"
                ),
                evidence={
                    "decisionId": str(decision.decision_id),
                    "stage": decision.stage.value,
                    "outcome": decision.outcome.value,
                    "allowed": decision.allowed,
                    "flowId": decision.flow_id,
                    "flowRevision": decision.flow_revision,
                    "executionId": str(execution_id) if execution_id is not None else None,
                    "taskRunId": str(task_run_id) if task_run_id is not None else None,
                    "policyPins": [
                        item.model_dump(mode="json", by_alias=True)
                        for item in decision.pinned_policies
                    ],
                    "matchedRules": [
                        item.model_dump(mode="json", by_alias=True)
                        for item in decision.matched_rules
                    ],
                    "inputHash": decision.input_hash,
                },
            )
        return decision

    async def list_decisions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[PolicyDecision, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT decision
                            FROM admission_policy_decisions
                            WHERE tenant_id = :tenant_id
                            ORDER BY decided_at DESC, id DESC
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(PolicyDecision.model_validate(row["decision"]) for row in rows)


def _policy_revision(row: RowMapping, tenant_id: str) -> PolicyRevision:
    document = PolicyDocument.model_validate(row["document"])
    return PolicyRevision(
        policyId=row["policy_id"],
        tenantId=None if row["tenant_id"] is None else tenant_id,
        revision=row["revision"],
        digest=row["digest"],
        document=document,
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )


async def _write_audit(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    actor_id: str,
    action: str,
    resource_id: str,
    reason: str,
    outcome: str = "SUCCESS",
    evidence: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, reason, correlation_id, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, 'admission_policy',
                :resource_id, :outcome, :reason, :correlation_id,
                '{"component":"admission-policy-repository"}'::jsonb,
                CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "action": action,
            "resource_id": resource_id,
            "outcome": outcome,
            "reason": reason,
            "correlation_id": new_runtime_id(),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
