from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import ExecutionState, FailureCategory, ResourceMetadata, TaskRunState
from amesh.dsl import FlowDefinition


class TaskStateConflictError(RuntimeError):
    """Raised when persisted task state no longer permits the requested transition."""


class ExecutionStateConflictError(RuntimeError):
    """Raised when an execution transition uses a stale epoch or illegal state."""


class ExecutionLaunchSource(StrEnum):
    """Supported origins for a durable execution launch."""

    MANUAL = "manual"
    API = "api"
    SCHEDULED = "scheduled"
    EVENT = "event"
    SUBFLOW = "subflow"


class ExecutionInterventionAction(StrEnum):
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    REQUEST_CANCEL = "REQUEST_CANCEL"
    CONFIRM_CANCEL = "CONFIRM_CANCEL"
    FORCE_CANCEL = "FORCE_CANCEL"
    RESTART = "RESTART"


class PersistedExecution(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    tenant_id: str
    state: ExecutionState
    epoch: int = Field(ge=1)
    version: int = Field(ge=0)
    namespace: str
    flow_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    trigger: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    timeout_at: datetime | None = None
    cancel_deadline_at: datetime | None = None


class PersistedFlow(BaseModel):
    model_config = ConfigDict(frozen=True)

    resource_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    revision: int = Field(ge=1)
    semantic_hash: str
    metadata: ResourceMetadata
    etag: str


class PersistedTaskRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_run_id: UUID
    execution_id: UUID
    task_id: str
    state: TaskRunState
    current_attempt: int = Field(ge=0)
    version: int = Field(ge=0)
    retry_at: datetime | None = None
    result: dict[str, Any] | None = None
    failure_category: FailureCategory | None = None


class ExecutionInterventionPreview(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    action: ExecutionInterventionAction
    current_state: ExecutionState
    predicted_state: ExecutionState
    current_version: int = Field(ge=0)
    current_epoch: int = Field(ge=1)
    checkpoint_task_id: str | None = None
    impacted_task_ids: tuple[str, ...] = ()
    preserved_task_ids: tuple[str, ...] = ()
    invalidates_active_claims: bool = False
    destructive: bool = False
    force_available_at: datetime | None = None
    consequences: tuple[str, ...] = ()


class ExecutionInterventionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    sequence: int = Field(ge=1)
    action: ExecutionInterventionAction
    event_type: str
    actor_id: str
    reason: str | None = None
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionRepository(Protocol):
    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        expected_etag: str | None = None,
        actor_id: str = "system:flow-manager",
    ) -> PersistedFlow: ...

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> FlowDefinition: ...

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]: ...

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, Any],
        trigger: dict[str, Any] | None = None,
        launch_source: ExecutionLaunchSource = ExecutionLaunchSource.MANUAL,
        idempotency_key: str | None = None,
        actor_id: str = "system:executor",
    ) -> PersistedExecution: ...

    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> PersistedExecution: ...

    async def list_executions(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> list[PersistedExecution]: ...

    async def list_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]: ...

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
    ) -> PersistedTaskRun: ...

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, Any],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun: ...

    async def retry_task(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.RETRYABLE,
    ) -> PersistedTaskRun: ...

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
    ) -> PersistedTaskRun: ...

    async def cancel_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun: ...

    async def complete_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution: ...

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution: ...

    async def database_time(self) -> datetime: ...

    async def apply_execution_intervention(
        self,
        execution_id: UUID,
        action: ExecutionInterventionAction,
        *,
        tenant_id: str,
        expected_version: int,
        expected_epoch: int,
        actor_id: str,
        reason: str,
        grace_period: timedelta = timedelta(seconds=30),
        reset_task_ids: tuple[str, ...] = (),
        checkpoint_task_id: str | None = None,
        restart_timeout: timedelta | None = None,
    ) -> PersistedExecution: ...

    async def list_execution_interventions(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionInterventionRecord]: ...

    async def timeout_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution: ...
