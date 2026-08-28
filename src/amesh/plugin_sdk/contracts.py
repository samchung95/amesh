from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from amesh.observability import current_trace_context, normalize_trace_context

from .errors import PluginErrorDetail
from .manifest import PLUGIN_PROTOCOL_VERSION


class PluginOperation(StrEnum):
    VALIDATE = "validate"
    EXECUTE = "execute"
    POLL = "poll"
    EVALUATE = "evaluate"
    RUN = "run"
    CANCEL = "cancel"
    GET = "get"
    PUT = "put"
    DELETE = "delete"
    RESOLVE = "resolve"
    SEND = "send"


class PluginSession(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    invocation_id: str = Field(alias="invocationId", min_length=1, max_length=255)
    deadline: datetime | None = None
    capability_tokens: dict[str, SecretStr] = Field(
        default_factory=dict,
        alias="capabilityTokens",
        repr=False,
    )


class PluginRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    protocol_version: str = Field(
        default=PLUGIN_PROTOCOL_VERSION,
        alias="protocolVersion",
    )
    plugin: str = Field(min_length=1, max_length=255)
    entry_point: str = Field(alias="entryPoint", min_length=1, max_length=255)
    operation: PluginOperation
    session: PluginSession
    configuration: dict[str, Any] = Field(default_factory=dict)
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    trace_context: dict[str, str] = Field(
        default_factory=current_trace_context,
        alias="traceContext",
    )

    @field_validator("trace_context", mode="before")
    @classmethod
    def validate_trace_context(cls, value: object) -> dict[str, str]:
        return normalize_trace_context(value)


class PluginLog(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR)$")
    message: str = Field(min_length=1, max_length=65_536)
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="occurredAt",
    )
    fields: dict[str, Any] = Field(default_factory=dict)


class PluginResponse(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    protocol_version: str = Field(
        default=PLUGIN_PROTOCOL_VERSION,
        alias="protocolVersion",
    )
    invocation_id: str = Field(alias="invocationId", min_length=1, max_length=255)
    output: dict[str, Any] = Field(default_factory=dict)
    logs: tuple[PluginLog, ...] = ()
    errors: tuple[PluginErrorDetail, ...] = ()
    checkpoint: dict[str, Any] | None = None

    @property
    def succeeded(self) -> bool:
        return not self.errors


class TaskResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    output: dict[str, Any] = Field(default_factory=dict)
    logs: tuple[PluginLog, ...] = ()
    metrics: dict[str, float] = Field(default_factory=dict)
    artifacts: tuple[str, ...] = ()


class TriggerResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    occurrences: tuple[dict[str, Any], ...] = ()
    checkpoint: dict[str, Any] = Field(default_factory=dict)


class ConditionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    matched: bool
    details: dict[str, Any] = Field(default_factory=dict)


class RunnerExtensionResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    status: str = Field(pattern=r"^(SUCCESS|FAILED|CANCELLED|TIMED_OUT)$")
    exit_code: int | None = Field(default=None, alias="exitCode")
    output: dict[str, Any] = Field(default_factory=dict)


class StorageResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: dict[str, Any] = Field(default_factory=dict)
    content: bytes | None = None


class SecretResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: SecretStr = Field(repr=False)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExpressionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: Any


class NotificationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    delivered: bool
    provider_id: str | None = Field(default=None, alias="providerId")


class ExtensionContract(Protocol):
    async def validate(self, configuration: dict[str, Any]) -> tuple[PluginErrorDetail, ...]: ...


@runtime_checkable
class TaskExtension(ExtensionContract, Protocol):
    async def execute(self, request: PluginRequest) -> TaskResult: ...


@runtime_checkable
class TriggerExtension(ExtensionContract, Protocol):
    async def poll(self, request: PluginRequest) -> TriggerResult: ...


@runtime_checkable
class ConditionExtension(ExtensionContract, Protocol):
    async def evaluate(self, request: PluginRequest) -> ConditionResult: ...


@runtime_checkable
class RunnerExtension(ExtensionContract, Protocol):
    async def run(self, request: PluginRequest) -> RunnerExtensionResult: ...

    async def cancel(self, invocation_id: str) -> None: ...


@runtime_checkable
class StorageExtension(ExtensionContract, Protocol):
    async def get(self, request: PluginRequest) -> StorageResult: ...

    async def put(self, request: PluginRequest) -> StorageResult: ...

    async def delete(self, request: PluginRequest) -> StorageResult: ...


@runtime_checkable
class SecretExtension(ExtensionContract, Protocol):
    async def resolve(self, request: PluginRequest) -> SecretResult: ...


@runtime_checkable
class ExpressionExtension(ExtensionContract, Protocol):
    async def evaluate(self, request: PluginRequest) -> ExpressionResult: ...


@runtime_checkable
class NotificationExtension(ExtensionContract, Protocol):
    async def send(self, request: PluginRequest) -> NotificationResult: ...
