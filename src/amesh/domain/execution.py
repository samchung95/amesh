from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import new_runtime_id


class ExecutionState(StrEnum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"
    RESTARTING = "RESTARTING"


class FailureCategory(StrEnum):
    RETRYABLE = "RETRYABLE"
    NON_RETRYABLE = "NON_RETRYABLE"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    INFRASTRUCTURE = "INFRASTRUCTURE"


class ExecutionEventType(StrEnum):
    CREATED = "ExecutionCreated"
    QUEUED = "ExecutionQueued"
    STARTED = "ExecutionStarted"
    PAUSED = "ExecutionPaused"
    RESUMED = "ExecutionResumed"
    CANCEL_REQUESTED = "ExecutionCancelRequested"
    CANCELLED = "ExecutionCancelled"
    SUCCEEDED = "ExecutionSucceeded"
    FAILED = "ExecutionFailed"
    WARNED = "ExecutionWarned"
    RESTART_REQUESTED = "ExecutionRestartRequested"


class ExecutionCommandType(StrEnum):
    CREATE = "CreateExecution"
    QUEUE = "QueueExecution"
    START = "StartExecution"
    PAUSE = "PauseExecution"
    RESUME = "ResumeExecution"
    REQUEST_CANCEL = "RequestExecutionCancellation"
    CONFIRM_CANCEL = "ConfirmExecutionCancellation"
    SUCCEED = "SucceedExecution"
    FAIL = "FailExecution"
    WARN = "WarnExecution"
    REQUEST_RESTART = "RequestExecutionRestart"


class TaskRunState(StrEnum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    RETRY_DELAY = "RETRY_DELAY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskRunEventType(StrEnum):
    CREATED = "TaskRunCreated"
    STARTED = "TaskRunStarted"
    RETRY_SCHEDULED = "TaskRunRetryScheduled"
    SUCCEEDED = "TaskRunSucceeded"
    FAILED = "TaskRunFailed"
    CANCELLED = "TaskRunCancelled"
    RESTARTED = "TaskRunRestarted"


class TaskRunCommandType(StrEnum):
    CREATE = "CreateTaskRun"
    START = "StartTaskRun"
    SCHEDULE_RETRY = "ScheduleTaskRunRetry"
    SUCCEED = "SucceedTaskRun"
    FAIL = "FailTaskRun"
    CANCEL = "CancelTaskRun"
    RESTART = "RestartTaskRun"


class TransitionRejectionCode(StrEnum):
    ILLEGAL_TRANSITION = "ILLEGAL_TRANSITION"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    EPOCH_CONFLICT = "EPOCH_CONFLICT"


class InvalidTransition(ValueError):
    """Raised when an event is not legal for the current execution state."""


class UnsupportedEventSchema(ValueError):
    """Raised when an event cannot be upgraded to the current schema."""


CURRENT_EXECUTION_EVENT_SCHEMA_VERSION = 2
CURRENT_TASK_RUN_EVENT_SCHEMA_VERSION = 1


class ExecutionEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=new_runtime_id)
    event_type: ExecutionEventType
    schema_version: Literal[2] = 2
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=256)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=new_runtime_id)
    causation_id: UUID | None = None
    actor_id: str = "system"
    reason: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    @property
    def deduplication_key(self) -> str:
        return self.idempotency_key or str(self.event_id)


class ExecutionCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    command_id: UUID = Field(default_factory=new_runtime_id)
    command_type: ExecutionCommandType
    schema_version: Literal[1] = 1
    idempotency_key: str = Field(min_length=1, max_length=256)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=new_runtime_id)
    causation_id: UUID | None = None
    actor_id: str = "system"
    reason: str | None = None
    expected_version: int | None = Field(default=None, ge=0)
    expected_epoch: int | None = Field(default=None, ge=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    flow_revision: int = Field(ge=1)
    state: ExecutionState = ExecutionState.CREATED
    version: int = Field(default=0, ge=0)
    epoch: int = Field(default=1, ge=1)
    applied_event_ids: tuple[UUID, ...] = ()
    applied_idempotency_keys: tuple[str, ...] = ()
    last_event_at: datetime | None = None

    @property
    def terminal(self) -> bool:
        return self.state in {
            ExecutionState.CANCELLED,
            ExecutionState.SUCCESS,
            ExecutionState.FAILED,
            ExecutionState.WARNING,
        }


class TaskRunEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=new_runtime_id)
    event_type: TaskRunEventType
    schema_version: Literal[1] = 1
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=256)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=new_runtime_id)
    causation_id: UUID | None = None
    actor_id: str = "system"
    reason: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    @property
    def deduplication_key(self) -> str:
        return self.idempotency_key or str(self.event_id)


class TaskRunCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    command_id: UUID = Field(default_factory=new_runtime_id)
    command_type: TaskRunCommandType
    schema_version: Literal[1] = 1
    idempotency_key: str = Field(min_length=1, max_length=256)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=new_runtime_id)
    causation_id: UUID | None = None
    actor_id: str = "system"
    reason: str | None = None
    expected_version: int | None = Field(default=None, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskRunSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_run_id: UUID
    execution_id: UUID
    task_id: str
    state: TaskRunState = TaskRunState.WAITING
    current_attempt: int = Field(default=0, ge=0)
    version: int = Field(default=0, ge=0)
    applied_event_ids: tuple[UUID, ...] = ()
    applied_idempotency_keys: tuple[str, ...] = ()
    last_event_at: datetime | None = None

    @property
    def terminal(self) -> bool:
        return self.state in {
            TaskRunState.SUCCESS,
            TaskRunState.FAILED,
            TaskRunState.CANCELLED,
        }


class TransitionRejection(BaseModel):
    model_config = ConfigDict(frozen=True)

    rejection_id: UUID
    command_id: UUID
    idempotency_key: str
    schema_version: Literal[1] = 1
    aggregate_type: Literal["execution", "task_run"]
    aggregate_id: UUID
    code: TransitionRejectionCode
    current_state: ExecutionState | TaskRunState
    current_version: int = Field(ge=0)
    current_epoch: int | None = Field(default=None, ge=1)
    actor_id: str
    reason: str
    correlation_id: UUID
    causation_id: UUID | None = None
    occurred_at: datetime


class ExecutionTransition(BaseModel):
    model_config = ConfigDict(frozen=True)

    snapshot: ExecutionSnapshot
    events: tuple[ExecutionEvent, ...] = ()
    rejection: TransitionRejection | None = None
    duplicate: bool = False

    @model_validator(mode="after")
    def exactly_one_outcome(self) -> Self:
        if self.events and self.rejection is not None:
            raise ValueError("a transition cannot be accepted and rejected")
        return self


class TaskRunTransition(BaseModel):
    model_config = ConfigDict(frozen=True)

    snapshot: TaskRunSnapshot
    events: tuple[TaskRunEvent, ...] = ()
    rejection: TransitionRejection | None = None
    duplicate: bool = False

    @model_validator(mode="after")
    def exactly_one_outcome(self) -> Self:
        if self.events and self.rejection is not None:
            raise ValueError("a transition cannot be accepted and rejected")
        return self
