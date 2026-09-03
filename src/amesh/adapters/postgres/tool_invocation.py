from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain import (
    ToolInvocationEvidence,
    ToolInvocationRequest,
    ToolInvocationResult,
    ToolInvocationState,
    ToolProviderRef,
)
from amesh.ports import ToolInvocationJournal
from amesh.ports.errors import NotFoundError

from .repository_support import PostgresRepositoryBase


class PostgresToolInvocationJournal(PostgresRepositoryBase, ToolInvocationJournal):
    """Tenant-isolated durable journal for MCP and isolated plugin tool calls."""

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def begin(
        self,
        request: ToolInvocationRequest,
        *,
        request_hash: str,
        metadata: dict[str, object],
    ) -> ToolInvocationResult | None:
        schema_digest = _digest(metadata, "schemaDigest")
        policy_digest = _digest(metadata, "policyDigest")
        async with self._services.transactions.tenant(request.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            inserted = await connection.scalar(
                text(
                    """
                    INSERT INTO tool_invocations (
                        invocation_id, tenant_id, namespace_name, execution_id,
                        task_run_id, attempt, provider_kind, provider_key,
                        provider_revision, tool_name, schema_digest, policy_digest,
                        state, request_hash, request_metadata
                    ) VALUES (
                        :invocation_id, :tenant_id, :namespace, :execution_id,
                        :task_run_id, :attempt, :provider_kind, :provider_key,
                        :provider_revision, :tool_name, :schema_digest, :policy_digest,
                        'STARTED', :request_hash, CAST(:request_metadata AS jsonb)
                    )
                    ON CONFLICT DO NOTHING
                    RETURNING invocation_id
                    """
                ),
                {
                    "invocation_id": request.invocation_id,
                    "tenant_id": tenant_uuid,
                    "namespace": request.namespace,
                    "execution_id": request.execution_id,
                    "task_run_id": request.task_run_id,
                    "attempt": request.attempt,
                    "provider_kind": request.provider.kind.value,
                    "provider_key": request.provider.key,
                    "provider_revision": request.provider.revision,
                    "tool_name": request.tool_name,
                    "schema_digest": schema_digest,
                    "policy_digest": policy_digest,
                    "request_hash": request_hash,
                    "request_metadata": self._services.codec.dumps(metadata),
                },
            )
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM tool_invocations
                            WHERE tenant_id = :tenant_id
                              AND task_run_id = :task_run_id
                              AND attempt = :attempt
                              AND provider_kind = :provider_kind
                              AND provider_key = :provider_key
                              AND provider_revision = :provider_revision
                              AND tool_name = :tool_name
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "task_run_id": request.task_run_id,
                            "attempt": request.attempt,
                            "provider_kind": request.provider.kind.value,
                            "provider_key": request.provider.key,
                            "provider_revision": request.provider.revision,
                            "tool_name": request.tool_name,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "tool invocation",
                    request.invocation_id,
                    message=f"tool invocation {request.invocation_id} does not exist",
                )
            if row["request_hash"] != request_hash:
                raise ValueError("tool invocation identity was reused with a different request")
        return None if inserted is not None else _result(row)

    async def complete(self, request: ToolInvocationRequest, result: ToolInvocationResult) -> None:
        state = result.evidence.state
        if state is ToolInvocationState.AMBIGUOUS:
            # Keep STARTED durable; a restart must report ambiguity instead of retrying.
            return
        if state is ToolInvocationState.SUCCEEDED and result.output is None:
            raise ValueError("successful tool invocation requires output")
        if state is ToolInvocationState.FAILED and not result.evidence.error:
            raise ValueError("failed tool invocation requires an error")
        async with self._services.transactions.tenant(request.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            updated = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE tool_invocations
                            SET state = :state,
                                result = CAST(:result AS jsonb),
                                error = :error,
                                completed_at = clock_timestamp()
                            WHERE invocation_id = :invocation_id
                              AND tenant_id = :tenant_id
                              AND state = 'STARTED'
                            RETURNING *
                            """
                        ),
                        {
                            "state": state.value,
                            "result": self._services.codec.dumps(result.output)
                            if state is ToolInvocationState.SUCCEEDED
                            else None,
                            "error": result.evidence.error
                            if state is ToolInvocationState.FAILED
                            else None,
                            "invocation_id": result.evidence.invocation_id,
                            "tenant_id": tenant_uuid,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            row = updated
            if row is None:
                row = (
                    (
                        await connection.execute(
                            text(
                                "SELECT * FROM tool_invocations "
                                "WHERE invocation_id = :invocation_id AND tenant_id = :tenant_id"
                            ),
                            {
                                "invocation_id": result.evidence.invocation_id,
                                "tenant_id": tenant_uuid,
                            },
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    raise NotFoundError(
                        "tool invocation",
                        result.evidence.invocation_id,
                        message=(f"tool invocation {result.evidence.invocation_id} does not exist"),
                    )
                if row["state"] != state.value:
                    raise RuntimeError(f"tool invocation is already {row['state']}")


def _digest(metadata: dict[str, object], key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"tool invocation metadata requires {key}")
    return value


def _result(row: RowMapping) -> ToolInvocationResult:
    state = ToolInvocationState(str(row["state"]))
    return ToolInvocationResult(
        output=dict(row["result"] or {}),
        evidence=ToolInvocationEvidence(
            provider=ToolProviderRef(
                kind=row["provider_kind"],
                key=row["provider_key"],
                revision=row["provider_revision"],
            ),
            toolName=row["tool_name"],
            schemaDigest=row["schema_digest"],
            invocationId=row["invocation_id"],
            requestHash=row["request_hash"],
            policyDigest=row["policy_digest"],
            state=state,
            startedAt=row["started_at"],
            completedAt=row["completed_at"],
            ambiguousExternalOutcome=state is ToolInvocationState.STARTED,
            error=row["error"],
        ),
    )
