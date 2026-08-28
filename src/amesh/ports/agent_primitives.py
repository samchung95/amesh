from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from amesh.domain.agent_primitives import (
    AgentInvocationClaim,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    McpConnectionRevision,
    McpConnectionSpec,
)
from amesh.domain.model_continuations import ProtectedModelContinuation


class ModelProviderRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    operation: str = Field(min_length=1, max_length=128)
    endpoint: str = Field(min_length=1, max_length=4096)
    model: str = Field(min_length=1, max_length=512)
    payload: dict[str, Any]
    timeout_seconds: float = Field(alias="timeoutSeconds", gt=0)
    continuation: SecretStr | None = Field(default=None, exclude=True, repr=False)


class ModelProviderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    payload: dict[str, Any]
    continuation: SecretStr | None = Field(default=None, exclude=True, repr=False)


class ModelProvider(Protocol):
    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse: ...


class AgentPrimitiveRepository(Protocol):
    async def save_mcp_connection(
        self,
        tenant_id: str,
        spec: McpConnectionSpec,
        *,
        actor_id: str,
    ) -> McpConnectionRevision: ...

    async def get_mcp_connection(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        *,
        revision: int | None = None,
    ) -> McpConnectionRevision: ...

    async def list_mcp_connections(
        self,
        tenant_id: str,
        namespace: str,
    ) -> tuple[McpConnectionRevision, ...]: ...

    async def begin_invocation(self, start: AgentInvocationStart) -> AgentInvocationClaim: ...

    async def complete_invocation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        state: AgentInvocationState,
        result: dict[str, Any] | None = None,
        error: str | None = None,
        protected_continuation: ProtectedModelContinuation | None = None,
    ) -> AgentInvocationRecord: ...

    async def get_model_continuation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
    ) -> ProtectedModelContinuation | None: ...
