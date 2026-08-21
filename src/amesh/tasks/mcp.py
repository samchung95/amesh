from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mcp import Client

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskHandler


def agent_mcp_handler(
    target_resolver: Callable[[str], Any] | None = None,
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        extra = task.model_extra or {}
        endpoint = extra.get("endpoint")
        tool = extra.get("tool")
        arguments = extra.get("arguments", {})
        if not isinstance(endpoint, str) or not endpoint:
            raise ValueError(f"task {task.id!r} requires endpoint")
        if not isinstance(tool, str) or not tool:
            raise ValueError(f"task {task.id!r} requires tool")
        if not isinstance(arguments, dict):
            raise ValueError(f"task {task.id!r} arguments must be an object")
        target = target_resolver(endpoint) if target_resolver is not None else endpoint
        async with Client(
            target,
            raise_exceptions=True,
            read_timeout_seconds=task.timeout_seconds,
        ) as mcp_client:
            result = await mcp_client.call_tool(tool, arguments)
        if result.is_error:
            raise RuntimeError(f"MCP tool {tool!r} returned an error")
        payload = result.model_dump(mode="json", by_alias=True)
        return {
            "content": payload.get("content", []),
            "structuredContent": payload.get("structuredContent"),
        }

    return run
