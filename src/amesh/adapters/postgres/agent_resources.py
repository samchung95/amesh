from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.agent_primitives import McpConnectionRevision, McpConnectionSpec
from amesh.domain.agent_resources import (
    AGENT_RESOURCE_ADAPTER,
    AgentCapabilityPin,
    AgentDefinitionSpec,
    AgentEnvelopePreview,
    AgentEvaluationSpec,
    AgentResolutionRequest,
    AgentResourceKind,
    AgentResourceRevision,
    AgentResourceSpec,
    EffectiveCapabilityEnvelope,
    agent_resource_digest,
    resolve_capability_envelope,
)

from .tenant_context import tenant_transaction


class PostgresAgentResourceRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def save_resource(
        self,
        tenant_id: str,
        spec: AgentResourceSpec,
        *,
        actor_id: str,
    ) -> AgentResourceRevision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"),
                {"lock_key": f"{tenant_uuid}:{spec.namespace}:{spec.kind}:{spec.key}"},
            )
            current = await _select_resource_row(
                connection,
                tenant_uuid,
                spec.namespace,
                spec.kind,
                spec.key,
            )
            resource_id = (
                UUID(str(current["resource_id"])) if current is not None else new_runtime_id()
            )
            revision = int(current["revision"]) + 1 if current is not None else 1
            digest = agent_resource_digest(spec)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO agent_resource_revisions (
                                resource_id, revision, tenant_id, namespace_name,
                                resource_kind, resource_key, digest, spec, created_by
                            ) VALUES (
                                :resource_id, :revision, :tenant_id, :namespace,
                                :resource_kind, :resource_key, :digest,
                                CAST(:spec AS jsonb), :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "resource_id": resource_id,
                            "revision": revision,
                            "tenant_id": tenant_uuid,
                            "namespace": spec.namespace,
                            "resource_kind": spec.kind.value,
                            "resource_key": spec.key,
                            "digest": digest,
                            "spec": spec.model_dump_json(by_alias=True),
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
                action="agent.resource.revision.save",
                resource_type=f"agent_{spec.kind.value.lower()}",
                resource_id=str(resource_id),
                reason=f"saved {spec.namespace}.{spec.key}@{revision}",
                evidence={
                    "namespace": spec.namespace,
                    "kind": spec.kind.value,
                    "key": spec.key,
                    "revision": revision,
                    "digest": digest,
                },
            )
        return _resource_revision(row, tenant_id)

    async def get_resource(
        self,
        tenant_id: str,
        namespace: str,
        kind: AgentResourceKind,
        key: str,
        *,
        revision: int | None = None,
    ) -> AgentResourceRevision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await _select_resource_row(
                connection,
                tenant_uuid,
                namespace,
                kind,
                key,
                revision=revision,
            )
        if row is None:
            suffix = f"@{revision}" if revision is not None else ""
            raise LookupError(f"{kind.value} resource {namespace}.{key}{suffix} does not exist")
        return _resource_revision(row, tenant_id)

    async def list_resources(
        self,
        tenant_id: str,
        namespace: str,
        *,
        kind: AgentResourceKind | None = None,
    ) -> tuple[AgentResourceRevision, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT DISTINCT ON (resource_kind, resource_key) *
                            FROM agent_resource_revisions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND (
                                  CAST(:resource_kind AS text) IS NULL
                                  OR resource_kind = CAST(:resource_kind AS text)
                              )
                            ORDER BY resource_kind, resource_key, revision DESC
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "resource_kind": kind.value if kind is not None else None,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_resource_revision(row, tenant_id) for row in rows)

    async def resolve_agent(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        request: AgentResolutionRequest,
        *,
        actor_id: str,
    ) -> AgentCapabilityPin:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            agent, envelope = await _resolve_agent_envelope(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                key,
                request.agent_revision,
            )
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"),
                {"lock_key": f"{tenant_uuid}:{namespace}:{request.subject_ref}"},
            )
            existing = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_capability_pins
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND subject_ref = :subject_ref
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "subject_ref": request.subject_ref,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is not None:
                if existing["envelope_digest"] != envelope.digest:
                    raise ValueError("subjectRef is already pinned to a different envelope")
                return _capability_pin(existing, tenant_id)

            pin_id = new_runtime_id()
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO agent_capability_pins (
                                pin_id, tenant_id, namespace_name, agent_resource_id,
                                agent_revision, subject_ref, envelope_digest, envelope,
                                created_by
                            ) VALUES (
                                :pin_id, :tenant_id, :namespace, :agent_resource_id,
                                :agent_revision, :subject_ref, :envelope_digest,
                                CAST(:envelope AS jsonb), :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "pin_id": pin_id,
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "agent_resource_id": agent.resource_id,
                            "agent_revision": agent.revision,
                            "subject_ref": request.subject_ref,
                            "envelope_digest": envelope.digest,
                            "envelope": envelope.model_dump_json(by_alias=True),
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
                action="agent.capability_envelope.pin",
                resource_type="agent_capability_pin",
                resource_id=str(pin_id),
                reason=f"pinned {namespace}.{key}@{agent.revision}",
                evidence={
                    "namespace": namespace,
                    "agentKey": key,
                    "agentRevision": agent.revision,
                    "subjectRef": request.subject_ref,
                    "envelopeDigest": envelope.digest,
                },
            )
        return _capability_pin(row, tenant_id)

    async def preview_agent(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        *,
        agent_revision: int,
    ) -> AgentEnvelopePreview:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            agent, envelope = await _resolve_agent_envelope(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                key,
                agent_revision,
            )
        return AgentEnvelopePreview(
            agentRevision=agent.revision,
            envelopeDigest=envelope.digest,
            envelope=envelope,
        )


async def _resolve_agent_envelope(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    tenant_id: str,
    namespace: str,
    key: str,
    agent_revision: int,
) -> tuple[AgentResourceRevision, EffectiveCapabilityEnvelope]:
    agent_row = await _select_resource_row(
        connection,
        tenant_uuid,
        namespace,
        AgentResourceKind.AGENT,
        key,
        revision=agent_revision,
    )
    if agent_row is None:
        raise LookupError(f"AGENT resource {namespace}.{key}@{agent_revision} does not exist")
    agent = _resource_revision(agent_row, tenant_id)
    if not isinstance(agent.spec, AgentDefinitionSpec):
        raise ValueError("resolved resource is not an agent definition")

    model_policy = await _required_resource(
        connection,
        tenant_uuid,
        tenant_id,
        namespace,
        AgentResourceKind.MODEL_POLICY,
        agent.spec.model_policy.key,
        agent.spec.model_policy.revision,
    )
    prompts = tuple(
        [
            await _required_resource(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                AgentResourceKind.PROMPT,
                ref.key,
                ref.revision,
            )
            for ref in agent.spec.prompts
        ]
    )
    skills = tuple(
        [
            await _required_resource(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                AgentResourceKind.SKILL,
                ref.key,
                ref.revision,
            )
            for ref in agent.spec.skills
        ]
    )
    evaluations = tuple(
        [
            await _required_resource(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                AgentResourceKind.EVALUATION,
                ref.key,
                ref.revision,
            )
            for ref in agent.spec.evaluation_policy.evaluations
        ]
    )
    judge_refs = {
        (
            evaluation.spec.judge.model_policy.key,
            evaluation.spec.judge.model_policy.revision,
        )
        for evaluation in evaluations
        if isinstance(evaluation.spec, AgentEvaluationSpec) and evaluation.spec.judge is not None
    }
    judge_model_policies = tuple(
        [
            await _required_resource(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                AgentResourceKind.MODEL_POLICY,
                judge_key,
                revision,
            )
            for judge_key, revision in sorted(judge_refs)
        ]
    )
    connections = tuple(
        [
            await _required_connection(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
                ref.connection_key,
                ref.connection_revision,
            )
            for ref in agent.spec.tools
        ]
    )
    envelope = resolve_capability_envelope(
        agent,
        model_policy,
        prompts,
        skills,
        connections,
        evaluations,
        judge_model_policies,
    )
    return agent, envelope


async def _select_resource_row(
    connection: AsyncConnection,
    tenant_id: UUID,
    namespace: str,
    kind: AgentResourceKind,
    key: str,
    *,
    revision: int | None = None,
) -> RowMapping | None:
    return (
        (
            await connection.execute(
                text(
                    """
                    SELECT * FROM agent_resource_revisions
                    WHERE tenant_id = :tenant_id
                      AND namespace_name = :namespace
                      AND resource_kind = :resource_kind
                      AND resource_key = :resource_key
                      AND (
                          CAST(:revision AS integer) IS NULL
                          OR revision = CAST(:revision AS integer)
                      )
                    ORDER BY revision DESC
                    LIMIT 1
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "namespace": namespace,
                    "resource_kind": kind.value,
                    "resource_key": key,
                    "revision": revision,
                },
            )
        )
        .mappings()
        .one_or_none()
    )


async def _required_resource(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    tenant_id: str,
    namespace: str,
    kind: AgentResourceKind,
    key: str,
    revision: int,
) -> AgentResourceRevision:
    row = await _select_resource_row(
        connection,
        tenant_uuid,
        namespace,
        kind,
        key,
        revision=revision,
    )
    if row is None:
        raise LookupError(f"{kind.value} resource {namespace}.{key}@{revision} is unavailable")
    return _resource_revision(row, tenant_id)


async def _required_connection(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    tenant_id: str,
    namespace: str,
    key: str,
    revision: int,
) -> McpConnectionRevision:
    row = (
        (
            await connection.execute(
                text(
                    """
                    SELECT * FROM agent_mcp_connection_revisions
                    WHERE tenant_id = :tenant_id
                      AND namespace_name = :namespace
                      AND connection_key = :connection_key
                      AND revision = :revision
                    LIMIT 1
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace": namespace,
                    "connection_key": key,
                    "revision": revision,
                },
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise LookupError(f"MCP connection {namespace}.{key}@{revision} is unavailable")
    return McpConnectionRevision(
        connectionId=row["connection_id"],
        tenantId=tenant_id,
        revision=row["revision"],
        digest=row["digest"],
        spec=McpConnectionSpec.model_validate(row["spec"]),
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )


def _resource_revision(row: RowMapping, tenant_id: str) -> AgentResourceRevision:
    spec = AGENT_RESOURCE_ADAPTER.validate_python(row["spec"])
    return AgentResourceRevision(
        resourceId=row["resource_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        kind=AgentResourceKind(row["resource_kind"]),
        key=row["resource_key"],
        revision=row["revision"],
        digest=row["digest"],
        spec=spec,
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )


def _capability_pin(row: RowMapping, tenant_id: str) -> AgentCapabilityPin:
    return AgentCapabilityPin(
        pinId=row["pin_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        subjectRef=row["subject_ref"],
        envelopeDigest=row["envelope_digest"],
        envelope=EffectiveCapabilityEnvelope.model_validate(row["envelope"]),
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )


async def _write_audit(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    actor_id: str,
    action: str,
    resource_type: str,
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
                :event_id, :tenant_id, :actor_id, :action, :resource_type,
                :resource_id, 'SUCCESS', :reason, :correlation_id,
                '{"component":"agent-resource-repository"}'::jsonb,
                CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "reason": reason,
            "correlation_id": new_runtime_id(),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
