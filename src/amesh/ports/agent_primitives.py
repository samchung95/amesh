from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from amesh.domain.agent_primitives import (
    AgentInvocationAccounting,
    AgentInvocationClaim,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    McpConnectionRevision,
    McpConnectionSpec,
)
from amesh.domain.agent_progress import (
    AgentProgressActivity,
    AgentProgressDetail,
    AgentProgressStatus,
)
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.domain.model_continuations import ProtectedModelContinuation
from amesh.ports.model_engines import ModelEngineAccess


class ModelProviderContinuationBinding(BaseModel):
    """Private provider continuation bound to one model message index."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    message_index: int = Field(alias="messageIndex", ge=0)
    token: SecretStr = Field(exclude=True, repr=False)


ModelProviderAccess = ModelEngineAccess
# Compatibility import for adapters that only need to type-check the former string marker.
ModelEngineRef = str


class ModelProviderRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    operation: str = Field(min_length=1, max_length=128)
    endpoint: str | None = Field(default=None, min_length=1, max_length=4096)
    model: str = Field(min_length=1, max_length=512)
    payload: dict[str, Any]
    timeout_seconds: float | None = Field(alias="timeoutSeconds", gt=0)
    tenant_id: str | None = Field(default=None, alias="tenantId", min_length=1, max_length=255)
    namespace: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        exclude=True,
        repr=False,
    )
    continuation: SecretStr | None = Field(default=None, exclude=True, repr=False)
    continuation_bindings: tuple[ModelProviderContinuationBinding, ...] = Field(
        default=(),
        alias="continuationBindings",
        exclude=True,
        repr=False,
        max_length=64,
    )


class ModelProviderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    payload: dict[str, Any]
    continuation: SecretStr | None = Field(default=None, exclude=True, repr=False)


class ModelProviderProgressDelta(BaseModel):
    """One safe, provider-neutral progress delta emitted during a model stream.

    Adapters may only classify text as a public summary when the upstream provider explicitly
    authorizes that field. Raw reasoning and provider-specific payloads are intentionally absent.
    The caller supplies AMESH session identities before converting this delta into a journal frame.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    activity: AgentProgressActivity
    status: AgentProgressStatus
    activity_id: str = Field(alias="activityId", min_length=1, max_length=255)
    segment_id: UUID | None = Field(default=None, alias="segmentId")
    source_sequence: int = Field(alias="sourceSequence", ge=1)
    detail: AgentProgressDetail | None = None


class ModelProviderStreamEvent(BaseModel):
    """A safe progress, accounting, or terminal response event from one provider stream."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: Literal["progress", "accounting", "response"]
    progress: ModelProviderProgressDelta | None = None
    accounting_payload: dict[str, Any] | None = Field(
        default=None,
        alias="accountingPayload",
        exclude=True,
        repr=False,
    )
    response: ModelProviderResponse | None = None

    @classmethod
    def progress_event(cls, progress: ModelProviderProgressDelta) -> ModelProviderStreamEvent:
        return cls(kind="progress", progress=progress)

    @classmethod
    def response_event(cls, response: ModelProviderResponse) -> ModelProviderStreamEvent:
        return cls(kind="response", response=response)

    @classmethod
    def accounting_event(cls, payload: dict[str, Any]) -> ModelProviderStreamEvent:
        return cls(kind="accounting", accountingPayload=payload)

    @model_validator(mode="after")
    def validate_event(self) -> ModelProviderStreamEvent:
        values = {
            "progress": self.progress is not None,
            "accounting": self.accounting_payload is not None,
            "response": self.response is not None,
        }
        if not values[self.kind] or sum(values.values()) != 1:
            raise ValueError(f"{self.kind} stream events must contain only {self.kind}")
        return self


class ImageArtifactResolver(Protocol):
    """Tenant-authorized image byte resolver used only at the provider I/O boundary."""

    async def resolve_image(self, image: ImageArtifactRef, *, tenant_id: str) -> bytes: ...


class ModelProvider(Protocol):
    async def invoke(
        self,
        request: ModelProviderRequest,
        access: ModelProviderAccess,
    ) -> ModelProviderResponse: ...


class StreamingModelProvider(ModelProvider, Protocol):
    """Optional additive stream capability; unary ``invoke`` remains the compatibility path."""

    def stream(
        self,
        request: ModelProviderRequest,
        access: ModelProviderAccess,
    ) -> AsyncIterator[ModelProviderStreamEvent]: ...


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

    async def record_invocation_accounting(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        accounting: AgentInvocationAccounting,
    ) -> AgentInvocationRecord: ...

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
