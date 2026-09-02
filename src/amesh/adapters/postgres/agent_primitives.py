from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.agent_primitives import (
    AgentInvocationAccounting,
    AgentInvocationClaim,
    AgentInvocationKind,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    McpConnectionRevision,
    McpConnectionSpec,
)
from amesh.domain.model_continuations import ProtectedModelContinuation
from amesh.ports.agent_primitives import AgentPrimitiveRepository

from .tenant_context import tenant_transaction


class PostgresAgentPrimitiveRepository(AgentPrimitiveRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def save_mcp_connection(
        self,
        tenant_id: str,
        spec: McpConnectionSpec,
        *,
        actor_id: str,
    ) -> McpConnectionRevision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            current = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT connection_id, revision
                            FROM agent_mcp_connection_revisions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND connection_key = :connection_key
                            ORDER BY revision DESC
                            LIMIT 1
                            FOR UPDATE
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": spec.namespace,
                            "connection_key": spec.key,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            connection_id = (
                UUID(str(current["connection_id"])) if current is not None else new_runtime_id()
            )
            revision = int(current["revision"]) + 1 if current is not None else 1
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO agent_mcp_connection_revisions (
                                connection_id, revision, tenant_id, namespace_name,
                                connection_key, digest, spec, created_by
                            ) VALUES (
                                :connection_id, :revision, :tenant_id, :namespace,
                                :connection_key, :digest, CAST(:spec AS jsonb), :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "connection_id": connection_id,
                            "revision": revision,
                            "tenant_id": tenant_uuid,
                            "namespace": spec.namespace,
                            "connection_key": spec.key,
                            "digest": spec.digest,
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
                action="agent.mcp_connection.revision.save",
                resource_type="agent_mcp_connection",
                resource_id=str(connection_id),
                reason=f"saved {spec.namespace}.{spec.key}@{revision}",
                evidence={
                    "namespace": spec.namespace,
                    "connectionKey": spec.key,
                    "revision": revision,
                    "digest": spec.digest,
                    "toolAllowlist": list(spec.tool_allowlist),
                    "credentialRef": spec.credential_ref,
                },
            )
        return _connection_revision(row, tenant_id)

    async def get_mcp_connection(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        *,
        revision: int | None = None,
    ) -> McpConnectionRevision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM agent_mcp_connection_revisions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND connection_key = :connection_key
                              AND (
                                  CAST(:revision AS integer) IS NULL
                                  OR revision = CAST(:revision AS integer)
                              )
                            ORDER BY revision DESC
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
            suffix = f"@{revision}" if revision is not None else ""
            raise LookupError(f"MCP connection {namespace}.{key}{suffix} does not exist")
        return _connection_revision(row, tenant_id)

    async def list_mcp_connections(
        self,
        tenant_id: str,
        namespace: str,
    ) -> tuple[McpConnectionRevision, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT DISTINCT ON (connection_key) *
                            FROM agent_mcp_connection_revisions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                            ORDER BY connection_key, revision DESC
                            """
                        ),
                        {"tenant_id": tenant_uuid, "namespace": namespace},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_connection_revision(row, tenant_id) for row in rows)

    async def begin_invocation(self, start: AgentInvocationStart) -> AgentInvocationClaim:
        async with tenant_transaction(self._engine, start.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            inserted = await connection.scalar(
                text(
                    """
                    INSERT INTO agent_invocations (
                        invocation_id, tenant_id, namespace_name, execution_id,
                        task_run_id, attempt, kind, operation, state,
                        request_hash, request_metadata
                    ) VALUES (
                        :invocation_id, :tenant_id, :namespace, :execution_id,
                        :task_run_id, :attempt, :kind, :operation, 'STARTED',
                        :request_hash, CAST(:request_metadata AS jsonb)
                    )
                    ON CONFLICT DO NOTHING
                    RETURNING invocation_id
                    """
                ),
                {
                    "invocation_id": start.invocation_id,
                    "tenant_id": tenant_uuid,
                    "namespace": start.namespace,
                    "execution_id": start.execution_id,
                    "task_run_id": start.task_run_id,
                    "attempt": start.attempt,
                    "kind": start.kind.value,
                    "operation": start.operation,
                    "request_hash": start.request_hash,
                    "request_metadata": json.dumps(start.request_metadata),
                },
            )
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM agent_invocations
                            WHERE tenant_id = :tenant_id
                              AND invocation_id = :invocation_id
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "invocation_id": start.invocation_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT *
                                FROM agent_invocations
                                WHERE tenant_id = :tenant_id
                                  AND task_run_id = :task_run_id
                                  AND attempt = :attempt
                                  AND kind = :kind
                                  AND operation = :operation
                                """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "task_run_id": start.task_run_id,
                                "attempt": start.attempt,
                                "kind": start.kind.value,
                                "operation": start.operation,
                            },
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
            if row is None:
                raise LookupError("agent invocation conflict could not be recovered")
            if any(
                (
                    row["namespace_name"] != start.namespace,
                    row["execution_id"] != start.execution_id,
                    row["task_run_id"] != start.task_run_id,
                    row["kind"] != start.kind.value,
                    row["operation"] != start.operation,
                    row["request_hash"] != start.request_hash,
                )
            ):
                raise ValueError("agent invocation identity was reused with a different request")
        return AgentInvocationClaim(
            record=_invocation_record(row, start.tenant_id),
            created=inserted is not None,
        )

    async def record_invocation_accounting(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        accounting: AgentInvocationAccounting,
    ) -> AgentInvocationRecord:
        encoded = json.dumps(
            accounting.model_dump(mode="json", by_alias=True),
            sort_keys=True,
            separators=(",", ":"),
        )
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE agent_invocations
                            SET accounting = CAST(:accounting AS jsonb)
                            WHERE invocation_id = :invocation_id
                              AND tenant_id = :tenant_id
                              AND state = 'STARTED'
                              AND accounting IS NULL
                            RETURNING *
                            """
                        ),
                        {
                            "invocation_id": invocation_id,
                            "tenant_id": tenant_uuid,
                            "accounting": encoded,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                await _write_audit(
                    connection,
                    tenant_uuid,
                    actor_id=f"execution:{row['execution_id']}",
                    action="agent.invocation.accounting.record",
                    resource_type="agent_invocation",
                    resource_id=str(invocation_id),
                    outcome="SUCCESS",
                    reason=f"{row['kind']} {row['operation']} recorded provider accounting",
                    evidence={
                        "executionId": str(row["execution_id"]),
                        "taskRunId": str(row["task_run_id"]),
                        "attempt": row["attempt"],
                        "kind": row["kind"],
                        "operation": row["operation"],
                        "state": row["state"],
                        "requestHash": row["request_hash"],
                        "costState": accounting.cost_state.value,
                    },
                )
                return _invocation_record(row, tenant_id)

            existing = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM agent_invocations
                            WHERE invocation_id = :invocation_id
                              AND tenant_id = :tenant_id
                            """
                        ),
                        {"invocation_id": invocation_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is None:
                raise LookupError(f"agent invocation {invocation_id} does not exist")
            record = _invocation_record(existing, tenant_id)
            if record.accounting == accounting:
                return record
            if record.accounting is not None:
                raise RuntimeError(f"agent invocation {invocation_id} accounting conflicts")
            raise RuntimeError(
                f"agent invocation {invocation_id} accounting must be recorded while state is STARTED"
            )

    async def complete_invocation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        state: AgentInvocationState,
        result: dict[str, Any] | None = None,
        error: str | None = None,
        protected_continuation: ProtectedModelContinuation | None = None,
    ) -> AgentInvocationRecord:
        if state is AgentInvocationState.STARTED:
            raise ValueError("completed agent invocation cannot remain STARTED")
        if state is AgentInvocationState.SUCCEEDED and result is None:
            raise ValueError("successful agent invocation requires a result")
        if state in {AgentInvocationState.FAILED, AgentInvocationState.IN_DOUBT} and not error:
            raise ValueError("failed or in-doubt agent invocation requires an error")
        if protected_continuation is not None and state is not AgentInvocationState.SUCCEEDED:
            raise ValueError("model continuation requires a successful invocation")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE agent_invocations
                            SET state = :state,
                                result = CAST(:result AS jsonb),
                                error = :error,
                                continuation_provider_id = :continuation_provider_id,
                                continuation_provider_revision = :continuation_provider_revision,
                                continuation_key_id = :continuation_key_id,
                                continuation_token_digest = :continuation_token_digest,
                                continuation_ciphertext = :continuation_ciphertext,
                                completed_at = clock_timestamp()
                            WHERE invocation_id = :invocation_id
                              AND tenant_id = :tenant_id
                              AND state = 'STARTED'
                            RETURNING *
                            """
                        ),
                        {
                            "invocation_id": invocation_id,
                            "tenant_id": tenant_uuid,
                            "state": state.value,
                            "result": json.dumps(result) if result is not None else None,
                            "error": error,
                            "continuation_provider_id": (
                                protected_continuation.provider_id
                                if protected_continuation is not None
                                else None
                            ),
                            "continuation_provider_revision": (
                                protected_continuation.provider_revision
                                if protected_continuation is not None
                                else None
                            ),
                            "continuation_key_id": (
                                protected_continuation.key_id
                                if protected_continuation is not None
                                else None
                            ),
                            "continuation_token_digest": (
                                protected_continuation.token_digest
                                if protected_continuation is not None
                                else None
                            ),
                            "continuation_ciphertext": (
                                protected_continuation.ciphertext
                                if protected_continuation is not None
                                else None
                            ),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT * FROM agent_invocations
                                WHERE invocation_id = :invocation_id
                                  AND tenant_id = :tenant_id
                                """
                            ),
                            {"invocation_id": invocation_id, "tenant_id": tenant_uuid},
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    raise LookupError(f"agent invocation {invocation_id} does not exist")
                if row["state"] != state.value:
                    raise RuntimeError(
                        f"agent invocation {invocation_id} is already {row['state']}"
                    )
                if _protected_continuation(row) != protected_continuation:
                    raise RuntimeError(
                        f"agent invocation {invocation_id} continuation result conflicts"
                    )
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=f"execution:{row['execution_id']}",
                action="agent.invocation.complete",
                resource_type="agent_invocation",
                resource_id=str(invocation_id),
                outcome="SUCCESS" if state is AgentInvocationState.SUCCEEDED else "FAILED",
                reason=f"{row['kind']} {row['operation']} ended as {state.value}",
                evidence={
                    "executionId": str(row["execution_id"]),
                    "taskRunId": str(row["task_run_id"]),
                    "attempt": row["attempt"],
                    "kind": row["kind"],
                    "operation": row["operation"],
                    "state": state.value,
                    "requestHash": row["request_hash"],
                },
            )
        return _invocation_record(row, tenant_id)

    async def get_model_continuation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
    ) -> ProtectedModelContinuation | None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT kind, state,
                                   continuation_provider_id,
                                   continuation_provider_revision,
                                   continuation_key_id,
                                   continuation_token_digest,
                                   continuation_ciphertext
                            FROM agent_invocations
                            WHERE invocation_id = :invocation_id
                              AND tenant_id = :tenant_id
                            """
                        ),
                        {"invocation_id": invocation_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"agent invocation {invocation_id} does not exist")
        if row["kind"] != AgentInvocationKind.MODEL.value:
            raise ValueError("continuation source is not a model invocation")
        if row["state"] != AgentInvocationState.SUCCEEDED.value:
            raise RuntimeError("continuation source model invocation is not successful")
        return _protected_continuation(row)


def _connection_revision(row: RowMapping, tenant_id: str) -> McpConnectionRevision:
    return McpConnectionRevision(
        connectionId=row["connection_id"],
        tenantId=tenant_id,
        revision=row["revision"],
        digest=row["digest"],
        spec=McpConnectionSpec.model_validate(row["spec"]),
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )


def _invocation_record(row: RowMapping, tenant_id: str) -> AgentInvocationRecord:
    return AgentInvocationRecord(
        invocationId=row["invocation_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        attempt=row["attempt"],
        kind=AgentInvocationKind(row["kind"]),
        operation=row["operation"],
        requestHash=row["request_hash"],
        requestMetadata=row["request_metadata"],
        state=AgentInvocationState(row["state"]),
        accounting=row["accounting"],
        result=row["result"],
        error=row["error"],
        startedAt=row["started_at"],
        completedAt=row["completed_at"],
    )


def _protected_continuation(row: RowMapping) -> ProtectedModelContinuation | None:
    if row["continuation_ciphertext"] is None:
        return None
    return ProtectedModelContinuation(
        providerId=row["continuation_provider_id"],
        providerRevision=row["continuation_provider_revision"],
        keyId=row["continuation_key_id"],
        tokenDigest=row["continuation_token_digest"],
        ciphertext=bytes(row["continuation_ciphertext"]),
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
    outcome: str = "SUCCESS",
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, reason, correlation_id, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, :resource_type,
                :resource_id, :outcome, :reason, :correlation_id,
                '{"component":"agent-primitive-repository"}'::jsonb,
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
            "outcome": outcome,
            "reason": reason,
            "correlation_id": new_runtime_id(),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
