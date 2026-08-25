"""Minimal provider-neutral tool implementation used by the ToolProvider docs."""

from __future__ import annotations

import asyncio

from amesh.domain import (
    ToolDescriptor,
    ToolImpact,
    ToolInvocationRequest,
    ToolPolicy,
    ToolProviderKind,
    ToolProviderRef,
)
from amesh.plugins import IsolatedPluginToolProvider
from amesh.tasks import GovernedToolInvoker, InMemoryToolInvocationJournal


async def isolated_echo(request: ToolInvocationRequest) -> dict[str, object]:
    return {"value": request.arguments["value"]}


async def main() -> None:
    identity = ToolProviderRef(kind=ToolProviderKind.PLUGIN, key="example.neutral", revision=1)
    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object"},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        isolated_echo,
    )
    invoker = GovernedToolInvoker(provider, InMemoryToolInvocationJournal())
    result = await invoker.invoke(
        ToolInvocationRequest(
            provider=identity,
            toolName="example.echo",
            arguments={"value": "hello"},
        ),
        ToolPolicy(allowedTools=("example.echo",)),
    )
    assert result.output == {"value": "hello"}


if __name__ == "__main__":
    asyncio.run(main())
