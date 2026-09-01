from __future__ import annotations

from decimal import Decimal
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from amesh.domain.agent_context import AgentContextReceipt, AgentHarnessContextBudget
from amesh.domain.agent_sessions import AgentModelContinuationBinding
from amesh.domain.image_inputs import InputModality
from amesh.ports.agent_progress import AgentProgressContext, AgentProgressSink

_SAFE_HARNESS_METADATA_KEYS = frozenset({"modelGateway", "routeId", "workerProtocol"})


class AgentSessionModelCall(BaseModel):
    """One AMESH-authorized model call exposed to a session harness."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def normalize_continuation_aliases(cls, value: object) -> object:
        if not isinstance(value, dict) or "continuationBindings" in value:
            return value
        normalized = dict(value)
        for alias in (
            "modelContinuations",
            "modelContinuationBindings",
            "continuation_bindings",
            "model_continuation_bindings",
        ):
            if alias in normalized:
                normalized["continuationBindings"] = normalized.pop(alias)
                break
        return normalized

    route_id: str = Field(alias="routeId", min_length=1, max_length=128)
    provider: dict[str, Any]
    model: str = Field(min_length=1, max_length=512)
    messages: tuple[dict[str, Any], ...]
    input_modalities: frozenset[InputModality] = Field(
        default=frozenset({InputModality.TEXT}),
        alias="inputModalities",
    )
    output_schema: dict[str, Any] = Field(alias="outputSchema")
    parameters: dict[str, Any] = Field(default_factory=dict)
    max_total_tokens: int | None = Field(alias="maxTotalTokens", ge=1)
    max_completion_tokens: int = Field(alias="maxCompletionTokens", ge=1)
    max_cost_usd: Decimal | None = Field(alias="maxCostUsd", ge=0)
    timeout_seconds: float | None = Field(alias="timeoutSeconds", gt=0)
    invocation_key: str = Field(alias="invocationKey", min_length=1, max_length=1024)
    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")
    engine_scopes: tuple[str, ...] = Field(
        default=(),
        alias="engineScopes",
        exclude_if=lambda value: not value,
    )
    continuation_from_invocation_id: UUID | None = Field(
        default=None,
        alias="continuationFromInvocationId",
    )
    continuation_bindings: tuple[AgentModelContinuationBinding, ...] = Field(
        default=(),
        alias="continuationBindings",
        max_length=64,
    )

    @model_validator(mode="after")
    def validate_continuation_bindings(self) -> AgentSessionModelCall:
        indexes = tuple(item.source_message_index for item in self.continuation_bindings)
        if indexes != tuple(sorted(set(indexes))):
            raise ValueError("continuation bindings must be ordered by unique sourceMessageIndex")
        return self

    @property
    def model_continuations(self) -> tuple[AgentModelContinuationBinding, ...]:
        return self.continuation_bindings

    @property
    def model_continuation_bindings(self) -> tuple[AgentModelContinuationBinding, ...]:
        return self.continuation_bindings


class AgentSessionHarnessRequest(BaseModel):
    """A single bounded turn offered to a replaceable session harness."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    turn: int = Field(ge=1)
    envelope_digest: str = Field(alias="envelopeDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    model_call: AgentSessionModelCall = Field(alias="modelCall")
    context_budget: AgentHarnessContextBudget = Field(alias="contextBudget")


class AgentSessionHarnessResult(BaseModel):
    """The model result and public provenance returned by a session harness."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str = Field(min_length=1, max_length=128)
    adapter_version: str = Field(alias="adapterVersion", min_length=1, max_length=128)
    model_output: dict[str, Any] = Field(alias="modelOutput")
    context_receipt: AgentContextReceipt = Field(alias="contextReceipt")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def evidence(self) -> dict[str, Any]:
        safe_metadata = {
            key: value
            for key, value in self.metadata.items()
            if key in _SAFE_HARNESS_METADATA_KEYS
            and isinstance(value, str)
            and 0 < len(value) <= 256
        }
        return {
            "adapter": self.adapter,
            "adapterVersion": self.adapter_version,
            "metadata": safe_metadata,
        }


class AgentHarnessContextSelection(BaseModel):
    """Messages selected by a harness plus their content-addressed proof."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    messages: tuple[dict[str, Any], ...]
    receipt: AgentContextReceipt


class AgentSessionModelGateway(Protocol):
    async def invoke(
        self,
        call: AgentSessionModelCall,
        *,
        context_selection: AgentHarnessContextSelection,
    ) -> dict[str, Any]: ...


class AgentSessionHarness(Protocol):
    @property
    def adapter_id(self) -> str: ...

    @property
    def adapter_version(self) -> str: ...

    @property
    def protocol(self) -> str: ...

    @property
    def input_modalities(self) -> frozenset[InputModality]: ...

    async def next_action(
        self,
        request: AgentSessionHarnessRequest,
        *,
        model_gateway: AgentSessionModelGateway,
        progress_sink: AgentProgressSink | None = None,
        progress_context: AgentProgressContext | None = None,
    ) -> AgentSessionHarnessResult: ...
