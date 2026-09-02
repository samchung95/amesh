from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.agent_session_policy import (
    AgentSessionPolicy,
    AgentSessionPolicyRevision,
)
from amesh.domain.identity import NamespaceId
from amesh.ports.agent_session_policy import (
    AgentSessionPolicyRepository,
    AgentSessionPolicyVersionConflict,
)

from .tenant_context import tenant_transaction

_NAMESPACE_ADAPTER = TypeAdapter(NamespaceId)


class PostgresAgentSessionPolicyRepository(AgentSessionPolicyRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def save_revision(
        self,
        tenant_id: str,
        policy: AgentSessionPolicy,
        *,
        actor_id: str,
        namespace: str | None = None,
        application_id: str | None = None,
        expected_revision: int | None = None,
    ) -> AgentSessionPolicyRevision:
        validated_namespace = _validate_namespace(namespace)
        validated_application = _validate_application(application_id, validated_namespace)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"),
                {
                    "lock_key": (
                        f"{tenant_uuid}:agent-session-policy:"
                        f"{validated_namespace or '<tenant>'}:{validated_application or '<all>'}"
                    )
                },
            )
            current = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT policy_id, revision
                            FROM agent_session_policy_revisions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name IS NOT DISTINCT FROM :namespace
                              AND application_id IS NOT DISTINCT FROM :application_id
                              AND active
                            FOR UPDATE
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": validated_namespace,
                            "application_id": validated_application,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            current_revision = None if current is None else int(current["revision"])
            if expected_revision is not None and expected_revision != (current_revision or 0):
                raise AgentSessionPolicyVersionConflict(
                    "agent session policy revision changed or is unavailable"
                )
            policy_id = UUID(str(current["policy_id"])) if current is not None else new_runtime_id()
            revision = (current_revision or 0) + 1
            if current is not None:
                await connection.execute(
                    text(
                        """
                        UPDATE agent_session_policy_revisions
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
                            INSERT INTO agent_session_policy_revisions (
                                policy_id, revision, tenant_id, namespace_name, active,
                                application_id,
                                ceiling_mode, admission_enabled, max_concurrency, max_total_tokens,
                                max_cost_usd, max_duration_seconds, retention_seconds,
                                allowed_provider_ids, allowed_harness_ids, allowed_tool_ids,
                                digest, created_by, created_at
                            ) VALUES (
                                :policy_id, :revision, :tenant_id, :namespace, true,
                                :application_id,
                                :ceiling_mode, :admission_enabled, :max_concurrency, :max_total_tokens,
                                :max_cost_usd, :max_duration_seconds, :retention_seconds,
                                :allowed_provider_ids, :allowed_harness_ids, :allowed_tool_ids,
                                :digest, :created_by, :created_at
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "policy_id": policy_id,
                            "revision": revision,
                            "tenant_id": tenant_uuid,
                            "namespace": validated_namespace,
                            "application_id": validated_application,
                            "ceiling_mode": policy.ceiling_mode.value,
                            "admission_enabled": policy.admission_enabled,
                            "max_concurrency": policy.max_concurrency,
                            "max_total_tokens": policy.max_total_tokens,
                            "max_cost_usd": policy.max_cost_usd,
                            "max_duration_seconds": policy.max_duration_seconds,
                            "retention_seconds": policy.retention_seconds,
                            "allowed_provider_ids": list(policy.allowed_provider_ids),
                            "allowed_harness_ids": list(policy.allowed_harness_ids),
                            "allowed_tool_ids": list(policy.allowed_tool_ids),
                            "digest": policy.digest,
                            "created_by": actor_id,
                            "created_at": datetime.now(UTC),
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
                action="agent-session.policy.revision.save",
                resource_id=f"{policy_id}@{revision}",
                reason="agent session policy revision saved",
                evidence={
                    "policyId": str(policy_id),
                    "revision": revision,
                    "namespace": validated_namespace,
                    "applicationId": validated_application,
                    "digest": policy.digest,
                },
            )
        return _to_revision(row, tenant_id)

    async def get_revision(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
        application_id: str | None = None,
        revision: int | None = None,
        policy_id: UUID | None = None,
    ) -> AgentSessionPolicyRevision:
        validated_namespace = _validate_namespace(namespace)
        validated_application = _validate_application(application_id, validated_namespace)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM agent_session_policy_revisions
                            WHERE tenant_id = :tenant_id
                              AND (
                                  CAST(:policy_id AS uuid) IS NOT NULL
                                  OR namespace_name IS NOT DISTINCT FROM :namespace
                              )
                              AND (
                                  CAST(:policy_id AS uuid) IS NOT NULL
                                  OR application_id IS NOT DISTINCT FROM :application_id
                              )
                              AND (
                                  CAST(:policy_id AS uuid) IS NULL
                                  OR policy_id = CAST(:policy_id AS uuid)
                              )
                              AND (
                                  CAST(:revision AS integer) IS NULL
                                  OR revision = CAST(:revision AS integer)
                              )
                              AND (CAST(:revision AS integer) IS NOT NULL OR active)
                            ORDER BY revision DESC
                            LIMIT 1
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": validated_namespace,
                            "revision": revision,
                            "application_id": validated_application,
                            "policy_id": policy_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError("agent session policy does not exist")
        return _to_revision(row, tenant_id)

    async def effective_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str,
        application_id: str | None = None,
    ) -> tuple[AgentSessionPolicyRevision, ...]:
        validated_namespace = _validate_namespace(namespace)
        validated_application = _validate_application(application_id, validated_namespace)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM agent_session_policy_revisions
                            WHERE tenant_id = :tenant_id
                              AND active
                              AND (
                                  namespace_name IS NULL
                                  OR namespace_name = :namespace
                              )
                              AND (
                                  application_id IS NULL
                                  OR application_id = :application_id
                              )
                            ORDER BY CASE WHEN namespace_name IS NULL THEN 0 ELSE 1 END,
                                     CASE WHEN application_id IS NULL THEN 0 ELSE 1 END
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": validated_namespace,
                            "application_id": validated_application,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_to_revision(row, tenant_id) for row in rows)

    async def list_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
        application_id: str | None = None,
        limit: int = 100,
    ) -> tuple[AgentSessionPolicyRevision, ...]:
        validated_namespace = _validate_namespace(namespace)
        validated_application = _validate_application(application_id, validated_namespace)
        bounded_limit = max(1, min(limit, 100))
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM agent_session_policy_revisions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name IS NOT DISTINCT FROM :namespace
                              AND application_id IS NOT DISTINCT FROM :application_id
                            ORDER BY revision DESC
                            LIMIT :limit
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": validated_namespace,
                            "application_id": validated_application,
                            "limit": bounded_limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_to_revision(row, tenant_id) for row in rows)


def _validate_namespace(namespace: str | None) -> str | None:
    if namespace is None:
        return None
    return _NAMESPACE_ADAPTER.validate_python(namespace)


def _validate_application(application_id: str | None, namespace: str | None) -> str | None:
    if application_id is None:
        return None
    if namespace is None:
        raise ValueError("application session policies require a namespace")
    return application_id


def _to_revision(row: RowMapping, tenant_id: str) -> AgentSessionPolicyRevision:
    policy = AgentSessionPolicy(
        ceilingMode=row["ceiling_mode"],
        admissionEnabled=row["admission_enabled"],
        maxConcurrency=row["max_concurrency"],
        maxTotalTokens=row["max_total_tokens"],
        maxCostUsd=row["max_cost_usd"],
        maxDurationSeconds=row["max_duration_seconds"],
        retentionSeconds=row["retention_seconds"],
        allowedProviderIds=tuple(row["allowed_provider_ids"] or ()),
        allowedHarnessIds=tuple(row["allowed_harness_ids"] or ()),
        allowedToolIds=tuple(row["allowed_tool_ids"] or ()),
    )
    return AgentSessionPolicyRevision(
        policyId=row["policy_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        applicationId=row["application_id"],
        revision=row["revision"],
        spec=policy,
        digest=row["digest"],
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
    evidence: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, reason, correlation_id, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, 'agent_session_policy',
                :resource_id, 'SUCCESS', :reason, :correlation_id,
                '{"component":"agent-session-policy-repository"}'::jsonb,
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
            "reason": reason,
            "correlation_id": new_runtime_id(),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
