from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol

from amesh.domain.tool_provider import (
    ToolDiscovery,
    ToolInvocationRequest,
    ToolInvocationResult,
    ToolProviderRef,
)


class ToolProvider(Protocol):
    """Discovery and invocation port implemented by MCP and isolated plugins."""

    @property
    def identity(self) -> ToolProviderRef: ...

    async def discover(self) -> ToolDiscovery: ...

    async def invoke(self, request: ToolInvocationRequest) -> ToolInvocationResult: ...

    async def cancel(self, invocation_id: str) -> None: ...


class ToolInvocationJournal(Protocol):
    """Durable invocation journal seam; implementations own persistence and fencing."""

    async def begin(
        self,
        request: ToolInvocationRequest,
        *,
        request_hash: str,
        metadata: dict[str, object],
    ) -> ToolInvocationResult | None: ...

    async def complete(
        self,
        request: ToolInvocationRequest,
        result: ToolInvocationResult,
    ) -> None: ...


ToolPolicyDecision = Callable[[ToolProviderRef, str], Awaitable[bool]]
