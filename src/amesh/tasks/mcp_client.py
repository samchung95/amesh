from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from amesh.domain import McpDiscoveryResult, McpToolImpact, McpToolPin, canonical_hash
from amesh.tasks.http import HttpTaskPolicy, validate_http_destination

McpTargetResolver = Callable[[str], Any]


class McpToolApplicationError(RuntimeError):
    """An MCP server ran the tool and returned an application-level error."""

    def __init__(self, tool: str, payload: dict[str, Any]) -> None:
        super().__init__(f"MCP tool {tool!r} returned an application error")
        self.payload = payload


async def discover_mcp_server(
    endpoint: str,
    credential: str,
    *,
    timeout_seconds: float | None = 30,
    target_resolver: McpTargetResolver | None = None,
    http_policy: HttpTaskPolicy | None = None,
) -> McpDiscoveryResult:
    tools: list[McpToolPin] = []
    server_name = "unknown"
    server_version = ""
    async with _client(
        endpoint,
        credential,
        timeout_seconds=timeout_seconds,
        target_resolver=target_resolver,
        http_policy=http_policy,
    ) as mcp_client:
        cursor: str | None = None
        while True:
            result = await mcp_client.list_tools(cursor=cursor)
            for tool in result.tools:
                annotations = tool.annotations
                impact = (
                    McpToolImpact.READ_ONLY
                    if annotations is not None and annotations.read_only_hint is True
                    else (
                        McpToolImpact.IDEMPOTENT_WRITE
                        if annotations is not None and annotations.idempotent_hint is True
                        else McpToolImpact.HIGH_IMPACT
                    )
                )
                tools.append(
                    McpToolPin(
                        name=tool.name,
                        description=tool.description or "",
                        inputSchema=tool.input_schema,
                        outputSchema=tool.output_schema,
                        impact=impact,
                    )
                )
            cursor = result.next_cursor
            if cursor is None:
                break
            if len(tools) >= 1000:
                raise RuntimeError("MCP discovery exceeded 1,000 tools")
        if mcp_client.server_info is not None:
            server_name = mcp_client.server_info.name
            server_version = mcp_client.server_info.version
    ordered = tuple(sorted(tools, key=lambda tool: tool.name))
    digest = "sha256:" + canonical_hash(
        {
            "serverName": server_name,
            "serverVersion": server_version,
            "tools": [
                {
                    "name": tool.name,
                    "inputSchema": tool.input_schema,
                    "outputSchema": tool.output_schema,
                }
                for tool in ordered
            ],
        }
    )
    return McpDiscoveryResult(
        serverName=server_name,
        serverVersion=server_version,
        tools=ordered,
        digest=digest,
    )


async def _call_legacy_tool(
    endpoint: str,
    tool: str,
    arguments: dict[str, Any],
    *,
    timeout_seconds: float | None,
    target_resolver: McpTargetResolver | None,
) -> dict[str, Any]:
    target = target_resolver(endpoint) if target_resolver is not None else endpoint
    async with Client(
        target,
        raise_exceptions=True,
        read_timeout_seconds=timeout_seconds,
    ) as mcp_client:
        result = await mcp_client.call_tool(tool, arguments)
    return _tool_result(tool, result)


async def _call_tool(
    endpoint: str,
    credential: str,
    tool: str,
    arguments: dict[str, Any],
    *,
    timeout_seconds: float | None,
    target_resolver: McpTargetResolver | None,
    http_policy: HttpTaskPolicy | None,
) -> dict[str, Any]:
    async with _client(
        endpoint,
        credential,
        timeout_seconds=timeout_seconds,
        target_resolver=target_resolver,
        http_policy=http_policy,
    ) as mcp_client:
        result = await mcp_client.call_tool(tool, arguments)
    return _tool_result(tool, result)


def _tool_result(tool: str, result: Any) -> dict[str, Any]:
    payload = result.model_dump(mode="json", by_alias=True)
    if result.is_error:
        raise McpToolApplicationError(tool, payload)
    return {
        "content": payload.get("content", []),
        "structuredContent": payload.get("structuredContent"),
    }


@asynccontextmanager
async def _client(
    endpoint: str,
    credential: str,
    *,
    timeout_seconds: float | None,
    target_resolver: McpTargetResolver | None,
    http_policy: HttpTaskPolicy | None,
) -> AsyncIterator[Client]:
    if target_resolver is not None:
        async with Client(
            target_resolver(endpoint),
            raise_exceptions=True,
            read_timeout_seconds=timeout_seconds,
        ) as mcp_client:
            yield mcp_client
        return
    validate_http_destination(endpoint, http_policy or HttpTaskPolicy(), resolve_dns=True)
    timeout = (
        None if timeout_seconds is None else httpx2.Timeout(timeout_seconds, read=timeout_seconds)
    )
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {credential}"},
        timeout=timeout,
        follow_redirects=False,
    ) as http_client:
        transport = streamable_http_client(endpoint, http_client=http_client)
        async with Client(
            transport,
            raise_exceptions=True,
            read_timeout_seconds=timeout_seconds,
        ) as mcp_client:
            yield mcp_client
