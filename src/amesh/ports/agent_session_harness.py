from __future__ import annotations

from decimal import Decimal
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain.image_inputs import InputModality
from amesh.ports.agent_progress import AgentProgressContext, AgentProgressSink

_SAFE_HARNESS_METADATA_KEYS = frozenset({"modelGateway", "routeId", "workerProtocol"})


class AgentSessionModelCall(BaseModel):
    """One AMESH-authorized model call exposed to a session harness."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

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
    max_total_tokens: int = Field(alias="maxTotalTokens", ge=1)
    max_completion_tokens: int = Field(alias="maxCompletionTokens", ge=1)
    max_cost_usd: Decimal = Field(alias="maxCostUsd", ge=0)
    timeout_seconds: float = Field(alias="timeoutSeconds", gt=0)
    invocation_key: str = Field(alias="invocationKey", min_length=1, max_length=1024)
    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")
    continuation_from_invocation_id: UUID | None = Field(
        default=None,
        alias="continuationFromInvocationId",
    )


class AgentSessionHarnessRequest(BaseModel):
    """A single bounded turn offered to a replaceable session harness."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    turn: int = Field(ge=1)
    envelope_digest: str = Field(alias="envelopeDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    model_call: AgentSessionModelCall = Field(alias="modelCall")


class AgentSessionHarnessResult(BaseModel):
    """The model result and public provenance returned by a session harness."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    adapter: str = Field(min_length=1, max_length=128)
    adapter_version: str = Field(alias="adapterVersion", min_length=1, max_length=128)
    model_output: dict[str, Any] = Field(alias="modelOutput")
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


class AgentSessionModelGateway(Protocol):
    async def invoke(self, call: AgentSessionModelCall) -> dict[str, Any]: ...


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
