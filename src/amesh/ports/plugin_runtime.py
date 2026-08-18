from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class PluginInvocation(BaseModel):
    model_config = ConfigDict(frozen=True)

    package_digest: str
    plugin_type: str
    tenant_id: str
    invocation_id: str
    configuration: dict[str, Any]
    context: dict[str, Any] = Field(default_factory=dict)
    capability_tokens: dict[str, str] = Field(default_factory=dict)


class PluginRuntime(Protocol):
    async def validate(self, invocation: PluginInvocation) -> list[dict[str, Any]]: ...

    async def invoke(self, invocation: PluginInvocation) -> dict[str, Any]: ...

    async def cancel(self, invocation_id: str) -> None: ...
