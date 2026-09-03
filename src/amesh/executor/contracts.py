from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from amesh.domain import ExecutionState, FailureCategory, PolicyDecision
from amesh.dsl import FlowDefinition
from amesh.dsl.models import RetryPolicy, TaskDefinition
from amesh.ports import (
    AssetAccessMode,
    ExecutionRepository,
    LogLevel,
    LogSourceStream,
    MetricKind,
    PersistedExecution,
    PersistedTaskRun,
)

from .loops import LoopIterationContext


class TaskLogRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    level: LogLevel = LogLevel.INFO
    logger: str = Field(default="task", min_length=1, max_length=256)
    message: str
    fields: dict[str, Any] = Field(default_factory=dict)
    source_stream: LogSourceStream = Field(default=LogSourceStream.TASK, alias="sourceStream")
    trace_id: str | None = Field(default=None, alias="traceId", max_length=256)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="occurredAt")
    redacted: bool = False


class TaskMetricRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=256)
    kind: MetricKind = MetricKind.GAUGE
    value: Decimal
    unit: str | None = Field(default=None, max_length=64)
    labels: dict[str, str] = Field(default_factory=dict)


class TaskArtifactRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    uri: str = Field(min_length=1, max_length=4096)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    media_type: str | None = Field(default=None, alias="mediaType", max_length=255)
    checksum_sha256: str | None = Field(
        default=None,
        alias="checksumSha256",
        pattern=r"^[0-9a-f]{64}$",
    )
    logical_path: str | None = Field(default=None, alias="logicalPath", max_length=4096)
    lineage: tuple[str, ...] = ()

    @field_validator("uri")
    @classmethod
    def require_internal_storage_uri(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"local", "s3", "azure", "gs"}
            or not parsed.netloc
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("artifact URI must use internal object storage")
        return value


class TaskAssetRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    provider: str = Field(min_length=1, max_length=128)
    account: str = Field(default="default", min_length=1, max_length=255)
    location: str = Field(default="global", min_length=1, max_length=512)
    asset_type: str = Field(alias="assetType", min_length=1, max_length=128)
    external_key: str = Field(alias="externalKey", min_length=1, max_length=1024)
    display_name: str = Field(alias="displayName", min_length=1, max_length=512)
    access_mode: AssetAccessMode = Field(alias="accessMode")
    description: str = Field(default="", max_length=4096)
    owner: str | None = Field(default=None, max_length=255)
    contacts: tuple[str, ...] = ()
    domain_group: str | None = Field(default=None, alias="domainGroup", max_length=255)
    tags: tuple[str, ...] = ()
    custom_metadata: dict[str, Any] = Field(default_factory=dict, alias="customMetadata")
    artifact_uri: str | None = Field(default=None, alias="artifactUri", max_length=4096)


class TaskExitMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    status: str = Field(default="SUCCESS", min_length=1, max_length=64)
    code: int | None = None
    reason: str | None = Field(default=None, max_length=4096)
    duration_ms: float | None = Field(default=None, alias="durationMs", ge=0)


class TaskCompletion(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    output: dict[str, Any] = Field(default_factory=dict)
    sensitive_output_keys: tuple[str, ...] = Field(default=(), alias="sensitiveOutputKeys")
    logs: tuple[TaskLogRecord, ...] = ()
    metrics: tuple[TaskMetricRecord, ...] = ()
    artifacts: tuple[TaskArtifactRecord, ...] = ()
    assets: tuple[TaskAssetRecord, ...] = Field(default=(), max_length=1000)
    exit: TaskExitMetadata = Field(default_factory=TaskExitMetadata)


class TaskDeferral(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    resume_token: str = Field(alias="resumeToken", min_length=16, max_length=4096)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskContextRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")
    namespace: str
    execution_id: str = Field(alias="executionId")
    task_run_id: str = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    task_type: str = Field(alias="taskType")
    secret_scopes: tuple[str, ...] = Field(alias="secretScopes")
    declared_files: dict[str, str] = Field(alias="declaredFiles")
    key_values_required: bool = Field(default=False, alias="keyValuesRequired")


class TaskFileReference(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    uri: str = Field(min_length=1, max_length=4096)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    checksum_sha256: str = Field(
        alias="checksumSha256",
        pattern=r"^[0-9a-f]{64}$",
    )


class TaskContextResources(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    secrets: dict[str, str] = Field(default_factory=dict)
    files: dict[str, str] = Field(default_factory=dict)
    key_values: dict[str, Any] = Field(default_factory=dict, alias="keyValues")
    file_references: dict[str, TaskFileReference] = Field(
        default_factory=dict,
        alias="fileReferences",
    )


class TaskContextProvider(Protocol):
    async def resolve(self, request: TaskContextRequest) -> TaskContextResources: ...


TaskHandlerResult = dict[str, Any] | TaskCompletion | TaskDeferral


class TaskCancellationChannel:
    """Typed, polling cancellation signal backed by durable execution state."""

    def __init__(
        self,
        repository: ExecutionRepository | None = None,
        *,
        tenant_id: str | None = None,
        execution_id: UUID | None = None,
    ) -> None:
        self._repository = repository
        self._tenant_id = tenant_id
        self._execution_id = execution_id

    async def requested(self) -> bool:
        if self._repository is None or self._tenant_id is None or self._execution_id is None:
            return False
        execution = await self._repository.get_execution(
            self._execution_id,
            tenant_id=self._tenant_id,
        )
        return execution.state in {ExecutionState.CANCELLING, ExecutionState.CANCELLED}

    async def wait(self, *, poll_interval: float = 0.05) -> None:
        while not await self.requested():
            await asyncio.sleep(poll_interval)


@dataclass(frozen=True)
class TaskExecutionContext:
    tenant_id: str
    execution_id: UUID
    task_run_id: UUID
    attempt: int
    attempt_id: UUID
    inputs: Mapping[str, Any]
    outputs: Mapping[str, dict[str, Any]]
    variables: Mapping[str, Any]
    namespace: str = "default"
    task_types: Mapping[str, str] = field(default_factory=dict)
    labels: Mapping[str, str] = field(default_factory=dict)
    trigger: Mapping[str, Any] = field(default_factory=dict)
    iteration: LoopIterationContext | None = None
    secret_scopes: tuple[str, ...] = ()
    secrets: Mapping[str, str] = field(default_factory=dict)
    files: Mapping[str, str] = field(default_factory=dict)
    file_references: Mapping[str, TaskFileReference] = field(default_factory=dict)
    key_values: Mapping[str, Any] = field(default_factory=dict)
    workspace_scope_id: str | None = None
    workspace_quota_bytes: int | None = None
    cancellation: TaskCancellationChannel = field(default_factory=TaskCancellationChannel)


TaskHandler = Callable[[TaskDefinition, TaskExecutionContext], Awaitable[TaskHandlerResult]]
DispatchPolicyEnforcer = Callable[
    [FlowDefinition, PersistedExecution, PersistedTaskRun, TaskDefinition],
    Awaitable[PolicyDecision],
]


class ExecutionBlockedError(RuntimeError):
    """Raised when an unfinished execution has no runnable task."""


class TaskExecutionError(RuntimeError):
    """Raised after a task failure has been persisted."""


class TaskExecutionFailure(RuntimeError):
    """Handler failure carrying the normalized task failure category."""

    def __init__(
        self,
        message: str,
        category: FailureCategory,
        *,
        result: dict[str, object] | None = None,
        evidence: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.result = result
        self.evidence = evidence


class TaskConfigurationError(TaskExecutionFailure):
    def __init__(self, message: str) -> None:
        super().__init__(message, FailureCategory.CONFIGURATION)


class TaskUserCodeError(TaskExecutionFailure):
    def __init__(self, message: str) -> None:
        super().__init__(message, FailureCategory.USER_CODE)


class TaskPlatformError(TaskExecutionFailure):
    def __init__(self, message: str) -> None:
        super().__init__(message, FailureCategory.PLATFORM)


class TaskResourceLimitError(TaskUserCodeError):
    """Raised when task-produced evidence exceeds its declared contract limits."""


class LoopExecutionFailure(TaskUserCodeError):
    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


class TaskExecutionPaused(RuntimeError):
    """Signal that a handler durably paused its execution and kept its attempt live."""


def classify_task_failure(exc: Exception) -> FailureCategory:
    """Normalize handler failures into the retry contract's stable categories."""

    if isinstance(exc, TaskExecutionFailure):
        return exc.category
    if isinstance(exc, TimeoutError):
        return FailureCategory.TIMED_OUT
    if isinstance(exc, (TypeError, ValueError)):
        return FailureCategory.NON_RETRYABLE
    if isinstance(exc, OSError):
        return FailureCategory.INFRASTRUCTURE
    return FailureCategory.RETRYABLE


def retry_delay_seconds(
    policy: RetryPolicy,
    task_run_id: UUID,
    attempt: int,
) -> float:
    """Calculate bounded exponential delay with deterministic per-attempt jitter."""

    delay = policy.delay_seconds * policy.backoff_multiplier ** (attempt - 1)
    if policy.jitter_ratio:
        digest = hashlib.sha256(f"{task_run_id}:{attempt}".encode()).digest()
        unit = int.from_bytes(digest[:8], "big") / (2**64 - 1)
        delay *= 1 - policy.jitter_ratio + (2 * policy.jitter_ratio * unit)
    if policy.max_interval_seconds is not None:
        delay = min(delay, policy.max_interval_seconds)
    return delay


class ExecutionProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    state: ExecutionState
    tasks_run: int = Field(ge=0)
    task_runs: tuple[PersistedTaskRun, ...]


class OrchestrationDecision(BaseModel):
    """Pure decision derived from one committed execution plan and task snapshot."""

    model_config = ConfigDict(frozen=True)

    runnable_task_ids: tuple[str, ...] = ()
    retry_at: datetime | None = None
    terminal_state: ExecutionState | None = None
    diagnostic: str | None = None


@dataclass(frozen=True)
class TaskRunOutcome:
    claimed: bool
    failure: str | None = None


@dataclass(frozen=True)
class ConditionDecision:
    matched: bool
    evidence: dict[str, object]
    error: Exception | None = None


@dataclass(frozen=True)
class BranchDecision:
    selected_branch: str | None
    evidence: dict[str, object]
    error: Exception | None = None
