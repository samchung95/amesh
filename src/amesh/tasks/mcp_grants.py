from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from pydantic import ValidationError

from amesh.domain.agent_primitives import McpConnectionRevision
from amesh.domain.mcp_grants import McpExecutionGrantContext, McpExecutionGrantToken
from amesh.domain.resources import canonical_hash
from amesh.executor.contracts import TaskExecutionContext
from amesh.networking import HttpTaskPolicy, validate_http_destination


def execution_grant_context(
    connection: McpConnectionRevision,
    context: TaskExecutionContext,
    *,
    tool: str,
    invocation_id: UUID,
) -> McpExecutionGrantContext | None:
    if connection.spec.execution_grant is None:
        return None
    grants = context.trigger.get("ameshToolGrants")
    grant_ref = grants.get(connection.spec.key) if isinstance(grants, Mapping) else None
    try:
        return McpExecutionGrantContext.model_validate(
            {
                "grantRef": grant_ref,
                "audience": connection.spec.endpoint,
                "tenantId": context.tenant_id,
                "namespace": context.namespace,
                "actorId": context.trigger.get("ameshActorId"),
                "sessionId": context.trigger.get("ameshAgentSessionId"),
                "executionId": context.execution_id,
                "taskRunId": context.task_run_id,
                "invocationId": invocation_id,
                "attemptId": context.attempt_id,
                "attempt": context.attempt,
                "connection": connection.spec.key,
                "connectionRevision": connection.revision,
                "connectionDigest": connection.digest,
                "tool": tool,
            }
        )
    except ValidationError:
        raise PermissionError("MCP connection requires a bound canonical session grant") from None


async def exchange_execution_grant(
    endpoint: str,
    credential: str,
    context: McpExecutionGrantContext,
    *,
    http_policy: HttpTaskPolicy,
    timeout_seconds: float | None,
    client: httpx.AsyncClient | None = None,
) -> McpExecutionGrantToken:
    validate_http_destination(endpoint, http_policy, resolve_dns=client is None)
    payload = context.model_dump(mode="json", by_alias=True)
    try:
        if client is None:
            async with httpx.AsyncClient(follow_redirects=False) as owned_client:
                token = await _request_token(
                    owned_client, endpoint, credential, payload, timeout_seconds
                )
        else:
            token = await _request_token(client, endpoint, credential, payload, timeout_seconds)
        token.require_valid(context.audience, canonical_hash(payload), datetime.now(UTC))
        return token
    except (httpx.HTTPError, ValueError, PermissionError):
        # Gateway responses can contain credentials or consumer authority details.
        raise PermissionError("MCP execution grant exchange was rejected or unavailable") from None


async def _request_token(
    client: httpx.AsyncClient,
    endpoint: str,
    credential: str,
    payload: dict[str, Any],
    timeout_seconds: float | None,
) -> McpExecutionGrantToken:
    async with client.stream(
        "POST",
        endpoint,
        headers={"Authorization": f"Bearer {credential}"},
        json=payload,
        timeout=timeout_seconds,
        follow_redirects=False,
    ) as response:
        response.raise_for_status()
        content = bytearray()
        async for chunk in response.aiter_bytes():
            content.extend(chunk)
            if len(content) > 32768:
                raise ValueError("MCP grant response exceeds its contract size")
    return McpExecutionGrantToken.model_validate_json(content)
