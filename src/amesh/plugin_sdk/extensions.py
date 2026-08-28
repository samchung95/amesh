from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Literal, Protocol, TypeVar, cast, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from .errors import PluginContractError, PluginErrorDetail, PluginErrorPhase
from .manifest import ExtensionType, PluginManifest
from .schema import validate_configuration

_ResultT = TypeVar("_ResultT")
PLUGIN_EXTENSION_VERSION: Literal["amesh.plugin.extension/v1"] = "amesh.plugin.extension/v1"


class ExtensionCallPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_attempts: int = Field(default=1, alias="maxAttempts", ge=1, le=100)
    timeout_seconds: float = Field(default=30, alias="timeoutSeconds", gt=0, le=3600)
    retry_delay_seconds: float = Field(default=0, alias="retryDelaySeconds", ge=0, le=300)
    max_in_flight: int = Field(default=1, alias="maxInFlight", ge=1, le=100_000)


class ExtensionCallContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    attempt: int = Field(ge=1)
    deadline: datetime
    secrets: dict[str, SecretStr] = Field(default_factory=dict, repr=False)


class ExtensionRetryableError(RuntimeError):
    """Signals a connector failure that the declared extension policy may retry."""


class ExtensionCancelledError(RuntimeError):
    """Signals cancellation observed by the shared extension call controller."""


class ExtensionCallController:
    """Applies one timeout, retry and cancellation contract to every extension type."""

    def __init__(self, policy: ExtensionCallPolicy) -> None:
        self.policy = policy

    async def call(
        self,
        operation: Callable[[ExtensionCallContext], Awaitable[_ResultT]],
        *,
        secrets: Mapping[str, str] | None = None,
        cancellation: asyncio.Event | None = None,
    ) -> _ResultT:
        last_error: ExtensionRetryableError | TimeoutError | None = None
        for attempt in range(1, self.policy.max_attempts + 1):
            if cancellation is not None and cancellation.is_set():
                raise ExtensionCancelledError("extension call was cancelled")
            context = ExtensionCallContext(
                attempt=attempt,
                deadline=datetime.now(UTC) + timedelta(seconds=self.policy.timeout_seconds),
                secrets={name: SecretStr(value) for name, value in (secrets or {}).items()},
            )

            async def run_operation(
                call_context: ExtensionCallContext = context,
            ) -> object:
                return await operation(call_context)

            async def wait_for_cancellation() -> object:
                if cancellation is not None:
                    await cancellation.wait()
                return None

            running = asyncio.create_task(run_operation())
            cancelled = asyncio.create_task(wait_for_cancellation()) if cancellation else None
            try:
                async with asyncio.timeout(self.policy.timeout_seconds):
                    if cancelled is None:
                        return cast(_ResultT, await running)
                    done, _ = await asyncio.wait(
                        {running, cancelled},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if running in done:
                        return cast(_ResultT, await running)
                    running.cancel()
                    raise ExtensionCancelledError("extension call was cancelled")
            except (ExtensionRetryableError, TimeoutError) as exc:
                last_error = exc
                if attempt >= self.policy.max_attempts:
                    raise
            finally:
                if cancelled is not None:
                    cancelled.cancel()
                    with suppress(asyncio.CancelledError):
                        await cancelled
                if not running.done():
                    running.cancel()
                    with suppress(asyncio.CancelledError):
                        await running
            if self.policy.retry_delay_seconds:
                await _cancellable_delay(self.policy.retry_delay_seconds, cancellation)
        if last_error is None:
            raise RuntimeError("extension call completed without a result")
        raise last_error


class PluginTriggerOccurrence(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source_key: str = Field(alias="sourceKey", min_length=1, max_length=1024)
    partition: str | None = Field(default=None, max_length=512)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="observedAt")

    @field_validator("source_key", "partition")
    @classmethod
    def require_printable_identity(cls, value: str | None) -> str | None:
        if value is not None and (
            value.strip() != value or any(ord(character) < 32 for character in value)
        ):
            raise ValueError("trigger identity values must be trimmed and printable")
        return value

    @property
    def occurrence_key(self) -> str:
        return normalize_occurrence_key(self.source_key, partition=self.partition)


class PluginTriggerCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    checkpoint: dict[str, Any] = Field(default_factory=dict)
    cursor: str | None = Field(default=None, max_length=4096)


class PluginPollingRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    definition: dict[str, Any]
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    cursor: str | None = Field(default=None, max_length=4096)
    limit: int = Field(ge=1, le=100_000)


class PluginTriggerPollResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    occurrences: tuple[PluginTriggerOccurrence, ...] = ()
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    cursor: str | None = Field(default=None, max_length=4096)
    next_evaluation_at: datetime | None = Field(default=None, alias="nextEvaluationAt")


class PluginRealtimeRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    definition: dict[str, Any]
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    cursor: str | None = Field(default=None, max_length=4096)
    max_in_flight: int = Field(alias="maxInFlight", ge=1, le=100_000)


@runtime_checkable
class PluginPollingTriggerExtension(Protocol):
    async def poll(
        self,
        request: PluginPollingRequest,
        context: ExtensionCallContext,
    ) -> PluginTriggerPollResult: ...

    async def acknowledge(
        self,
        checkpoint: PluginTriggerCheckpoint,
        context: ExtensionCallContext,
    ) -> None: ...


@runtime_checkable
class PluginRealtimeTriggerConnection(Protocol):
    def __aiter__(self) -> AsyncIterator[PluginTriggerOccurrence]: ...

    async def acknowledge(self, source_key: str) -> None: ...

    async def close(self) -> None: ...


@runtime_checkable
class PluginRealtimeTriggerExtension(Protocol):
    async def connect(
        self,
        request: PluginRealtimeRequest,
        context: ExtensionCallContext,
    ) -> PluginRealtimeTriggerConnection: ...


class PluginConditionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    configuration: dict[str, Any] = Field(default_factory=dict)
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class PluginConditionResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    matched: bool
    reason: str = Field(min_length=1, max_length=4096)
    evidence: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class PluginConditionExtension(Protocol):
    async def evaluate(
        self,
        request: PluginConditionRequest,
        context: ExtensionCallContext,
    ) -> PluginConditionResult: ...


class PluginLifecycleEventType(StrEnum):
    EXECUTION_STARTED = "execution.started"
    EXECUTION_SUCCEEDED = "execution.succeeded"
    EXECUTION_FAILED = "execution.failed"
    EXECUTION_CANCELLED = "execution.cancelled"
    TASK_STARTED = "task.started"
    TASK_SUCCEEDED = "task.succeeded"
    TASK_FAILED = "task.failed"
    CHECK_TRIGGERED = "check.triggered"


class PluginLifecycleEvent(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    event_id: str = Field(alias="eventId", min_length=1, max_length=255)
    type: PluginLifecycleEventType
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: str = Field(min_length=1, max_length=255)
    flow_id: str = Field(alias="flowId", min_length=1, max_length=255)
    execution_id: str = Field(alias="executionId", min_length=1, max_length=255)
    task_run_id: str | None = Field(default=None, alias="taskRunId", max_length=255)
    occurred_at: datetime = Field(alias="occurredAt")
    payload: dict[str, Any] = Field(default_factory=dict)


class PluginNotificationDeliveryPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    delivery_key: str = Field(alias="deliveryKey", min_length=1, max_length=512)
    channel: str = Field(min_length=1, max_length=255)
    severity: str = Field(default="INFO", pattern=r"^(INFO|WARNING|ERROR|CRITICAL)$")
    max_attempts: int = Field(default=3, alias="maxAttempts", ge=1, le=100)
    timeout_seconds: float = Field(default=30, alias="timeoutSeconds", gt=0, le=3600)
    retry_delay_seconds: float = Field(default=1, alias="retryDelaySeconds", ge=0, le=300)


class PluginNotificationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    event: PluginLifecycleEvent
    policy: PluginNotificationDeliveryPolicy
    configuration: dict[str, Any] = Field(default_factory=dict)


class PluginNotificationResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    delivered: bool
    provider_id: str | None = Field(default=None, alias="providerId", max_length=1024)
    evidence: dict[str, Any] = Field(default_factory=dict)


class PluginExtensionContract(BaseModel):
    """Schema bundle for extension SDK generation and compatibility checks."""

    api_version: Literal["amesh.plugin.extension/v1"] = Field(
        default=PLUGIN_EXTENSION_VERSION,
        alias="apiVersion",
    )
    call_policy: ExtensionCallPolicy
    polling_request: PluginPollingRequest
    polling_result: PluginTriggerPollResult
    checkpoint: PluginTriggerCheckpoint
    realtime_request: PluginRealtimeRequest
    condition_request: PluginConditionRequest
    condition_result: PluginConditionResult
    lifecycle_event: PluginLifecycleEvent
    notification_request: PluginNotificationRequest
    notification_result: PluginNotificationResult


@runtime_checkable
class PluginNotificationExtension(Protocol):
    async def send(
        self,
        request: PluginNotificationRequest,
        context: ExtensionCallContext,
    ) -> PluginNotificationResult: ...


def normalize_occurrence_key(source_key: str, *, partition: str | None = None) -> str:
    payload = json.dumps(
        {"partition": partition, "sourceKey": source_key},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "plugin:v1:sha256:" + hashlib.sha256(payload).hexdigest()


def validate_extension_configuration(
    manifest: PluginManifest,
    entry_point_name: str,
    configuration: Mapping[str, Any],
    *,
    allowed_types: frozenset[ExtensionType] = frozenset(
        {ExtensionType.TRIGGER, ExtensionType.CONDITION}
    ),
) -> tuple[PluginErrorDetail, ...]:
    entry_point = next(
        (item for item in manifest.entry_points if item.name == entry_point_name),
        None,
    )
    if entry_point is None:
        return (
            PluginErrorDetail(
                code="plugin.configuration.entry_point_unknown",
                message="plugin entry point is not declared",
                phase=PluginErrorPhase.CONFIGURATION,
            ),
        )
    if entry_point.type not in allowed_types:
        return (
            PluginErrorDetail(
                code="plugin.configuration.extension_type",
                message="plugin entry point has an incompatible extension type",
                phase=PluginErrorPhase.CONFIGURATION,
            ),
        )
    return validate_configuration(entry_point, configuration)


def scope_extension_secrets(
    declared_scopes: tuple[str, ...],
    requested_scopes: tuple[str, ...],
    available: Mapping[str, str],
) -> dict[str, str]:
    undeclared = sorted(set(requested_scopes).difference(declared_scopes))
    unavailable = sorted(set(requested_scopes).difference(available))
    errors: list[PluginErrorDetail] = []
    if undeclared:
        errors.append(
            PluginErrorDetail(
                code="plugin.capability.secret_scope_undeclared",
                message="extension requested undeclared secret scopes",
                phase=PluginErrorPhase.CAPABILITY,
                details={"scopes": undeclared},
            )
        )
    if unavailable:
        errors.append(
            PluginErrorDetail(
                code="plugin.capability.secret_scope_unavailable",
                message="extension requested unavailable secret scopes",
                phase=PluginErrorPhase.CAPABILITY,
                details={"scopes": unavailable},
            )
        )
    if errors:
        raise PluginContractError(*errors)
    return {scope: available[scope] for scope in requested_scopes}


async def _cancellable_delay(seconds: float, cancellation: asyncio.Event | None) -> None:
    if cancellation is None:
        await asyncio.sleep(seconds)
        return
    try:
        async with asyncio.timeout(seconds):
            await cancellation.wait()
    except TimeoutError:
        return
    raise ExtensionCancelledError("extension call was cancelled")
