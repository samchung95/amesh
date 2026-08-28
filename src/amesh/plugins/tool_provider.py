from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from amesh.domain import (
    ToolDescriptor,
    ToolDiscovery,
    ToolImpact,
    ToolInvocationEvidence,
    ToolInvocationRequest,
    ToolInvocationResult,
    ToolInvocationState,
    ToolProviderKind,
    ToolProviderRef,
)
from amesh.plugin_sdk import ExtensionType, PluginManifest

PluginToolInvoker = Callable[[ToolInvocationRequest], Awaitable[dict[str, Any]]]
PluginToolCanceller = Callable[[str], Awaitable[None]]


class IsolatedPluginToolProvider:
    """Provider adapter for an isolated RPC entry point.

    The callbacks are deliberately narrow: callers bind them to the existing
    ``IsolatedPluginRuntime`` process/session boundary, so no in-process plugin
    code is accepted by this contract.
    """

    def __init__(
        self,
        identity: ToolProviderRef,
        tools: tuple[ToolDescriptor, ...],
        invoke: PluginToolInvoker,
        *,
        cancel: PluginToolCanceller | None = None,
    ) -> None:
        if identity.kind is not ToolProviderKind.PLUGIN:
            raise ValueError("isolated plugin providers require a plugin identity")
        if any(tool.provider != identity for tool in tools):
            raise ValueError("plugin tool descriptors must use the provider identity")
        self._identity = identity
        self._tools = tuple(sorted(tools, key=lambda item: item.name))
        self._invoke = invoke
        self._cancel = cancel

    @classmethod
    def from_manifest(
        cls,
        identity: ToolProviderRef,
        manifest: PluginManifest,
        invoke: PluginToolInvoker,
        *,
        cancel: PluginToolCanceller | None = None,
    ) -> IsolatedPluginToolProvider:
        """Build descriptors from a signed manifest without loading plugin code."""

        tools = tuple(
            ToolDescriptor(
                provider=identity,
                name=entry.name,
                description=entry.documentation.description,
                inputSchema=entry.configuration_schema,
                outputSchema=entry.output_schema,
                impact=ToolImpact.HIGH_IMPACT,
                secretScopes=manifest.capabilities.secret_scopes,
                allowedEgress=manifest.capabilities.allowed_egress,
                filesystemReadRoots=(
                    ("workspace",)
                    if manifest.capabilities.filesystem_access.value
                    in {"workspace-read", "workspace-write"}
                    else ()
                ),
                filesystemWriteRoots=(
                    ("workspace",)
                    if manifest.capabilities.filesystem_access.value == "workspace-write"
                    else ()
                ),
            )
            for entry in manifest.entry_points
            if entry.type is ExtensionType.TASK
        )
        return cls(identity, tools, invoke, cancel=cancel)

    @property
    def identity(self) -> ToolProviderRef:
        return self._identity

    async def discover(self) -> ToolDiscovery:
        return ToolDiscovery.from_tools(self._identity, self._tools)

    async def invoke(self, request: ToolInvocationRequest) -> ToolInvocationResult:
        output = await self._invoke(request)
        return ToolInvocationResult(
            output=output,
            evidence=ToolInvocationEvidence(
                provider=self._identity,
                toolName=request.tool_name,
                schemaDigest="sha256:" + "0" * 64,
                invocationId=request.invocation_id,
                requestHash="0" * 64,
                policyDigest="sha256:" + "0" * 64,
                state=ToolInvocationState.SUCCEEDED,
            ),
        )

    async def cancel(self, invocation_id: str) -> None:
        if self._cancel is not None:
            await self._cancel(invocation_id)


PluginToolProvider = IsolatedPluginToolProvider
