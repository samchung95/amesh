from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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


class InvalidTransition(ValueError):
    """Raised when an event is not legal for the current execution state."""


class ExecutionEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=new_runtime_id)
    event_type: ExecutionEventType
    schema_version: int = Field(default=1, ge=1)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=new_runtime_id)
    causation_id: UUID | None = None
    actor_id: str = "system"
    reason: str | None = None
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
    last_event_at: datetime | None = None

    @property
    def terminal(self) -> bool:
        return self.state in {
            ExecutionState.CANCELLED,
            ExecutionState.SUCCESS,
            ExecutionState.FAILED,
            ExecutionState.WARNING,
        }
