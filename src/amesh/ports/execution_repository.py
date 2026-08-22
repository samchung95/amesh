from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import (
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionResourceType,
    ExecutionState,
    FailureCategory,
    FlowLifecycle,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    ResolvedAdmissionPolicy,
    ResourceMetadata,
    TaskRunLifecyclePhase,
    TaskRunState,
)
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
    BACKFILL = "backfill"
    REPLAY = "replay"


class ExecutionInterventionAction(StrEnum):
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    REQUEST_CANCEL = "REQUEST_CANCEL"
    CONFIRM_CANCEL = "CONFIRM_CANCEL"
    FORCE_CANCEL = "FORCE_CANCEL"
    RESTART = "RESTART"


class SubflowMode(StrEnum):
    SYNC = "SYNC"
    ASYNC = "ASYNC"
    DETACHED = "DETACHED"


class SubflowPropagation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    success: bool = True
    failure: bool = True
    cancellation: bool = True
    pause: bool = True
    restart: bool = True


class SubflowLaunchContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    parent_execution_id: UUID
    parent_task_run_id: UUID
    parent_attempt: int = Field(ge=1)
    invocation_key: str = Field(min_length=1, max_length=512)
    mode: SubflowMode
    depth: int = Field(ge=1)
    target_revision: int = Field(ge=1)
    propagation: SubflowPropagation = Field(default_factory=SubflowPropagation)
    output_mapping: dict[str, str] = Field(default_factory=dict)


class PersistedExecution(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    tenant_id: str
    state: ExecutionState
    epoch: int = Field(ge=1)
    version: int = Field(ge=0)
    namespace: str
    flow_id: str
    flow_revision: int = Field(default=1, ge=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    trigger: dict[str, Any] = Field(default_factory=dict)
    created_by: str = "system:executor"
    created_at: datetime
    updated_at: datetime
    timeout_at: datetime | None = None
    cancel_deadline_at: datetime | None = None
    lifecycle_evidence: dict[str, Any] = Field(default_factory=dict)


class PersistedFlow(BaseModel):
    model_config = ConfigDict(frozen=True)

    resource_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    revision: int = Field(ge=1)
    semantic_hash: str
    lifecycle: FlowLifecycle = FlowLifecycle.ACTIVE
    metadata: ResourceMetadata
    etag: str


class PersistedTaskRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_run_id: UUID
    execution_id: UUID
    task_id: str
    iteration_key: str | None = None
    state: TaskRunState
    current_attempt: int = Field(ge=0)
    version: int = Field(ge=0)
    retry_at: datetime | None = None
    result: dict[str, Any] | None = None
    failure_category: FailureCategory | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    lifecycle_phase: TaskRunLifecyclePhase = TaskRunLifecyclePhase.MAIN


class PersistedIterationSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    loop_id: str
    task_id: str
    iteration_count: int = Field(ge=0)
    waiting: int = Field(ge=0)
    running: int = Field(ge=0)
    succeeded: int = Field(ge=0)
    failed: int = Field(ge=0)
    cancelled: int = Field(ge=0)


class PersistedTaskDeferral(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_run_id: UUID
    attempt: int = Field(ge=1)
    state: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    expires_at: datetime | None = None
    deferred_at: datetime
    resumed_at: datetime | None = None


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


class PersistedSubflow(BaseModel):
    model_config = ConfigDict(frozen=True)

    relationship_id: UUID
    parent_execution_id: UUID
    parent_task_run_id: UUID
    parent_attempt: int = Field(ge=1)
    child_execution_id: UUID
    invocation_key: str
    mode: SubflowMode
    depth: int = Field(ge=1)
    target_revision: int = Field(ge=1)
    propagation: SubflowPropagation
    output_mapping: dict[str, str] = Field(default_factory=dict)
    parent_namespace: str
    parent_flow_id: str
    parent_flow_revision: int = Field(ge=1)
    child_namespace: str
    child_flow_id: str
    child_state: ExecutionState
    created_by: str
    created_at: datetime


class ExecutionRepository(Protocol):
    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        expected_etag: str | None = None,
        actor_id: str = "system:flow-manager",
        revision_source: FlowRevisionSource | None = None,
    ) -> PersistedFlow: ...

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> FlowDefinition: ...

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]: ...

    async def list_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> list[FlowRevisionRecord]: ...

    async def diff_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        from_revision: int,
        to_revision: int,
        *,
        tenant_id: str,
    ) -> FlowRevisionDiff: ...

    async def promote_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        lifecycle: FlowLifecycle,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
        reason: str | None = None,
    ) -> PersistedFlow: ...

    async def restore_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
        reason: str | None = None,
    ) -> PersistedFlow: ...

    async def delete_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
    ) -> None: ...

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
        labels: dict[str, str] | None = None,
        subflow: SubflowLaunchContext | None = None,
        priority: int | None = None,
    ) -> PersistedExecution: ...

    async def request_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
        *,
        tenant_id: str,
        priority: int = 0,
    ) -> AdmissionDecision: ...

    async def get_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
    ) -> AdmissionDecision | None: ...

    async def release_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
        reason: str = "resource completed",
    ) -> bool: ...

    async def reconcile_admission(self, *, tenant_id: str, limit: int = 100) -> int: ...

    async def admission_diagnostics(self, *, tenant_id: str) -> AdmissionDiagnostics: ...

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
        include_iterations: bool = True,
    ) -> list[PersistedTaskRun]: ...

    async def list_iteration_summaries(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedIterationSummary]: ...

    async def ensure_iteration_task_runs(
        self,
        execution_id: UUID,
        iteration_key: str,
        task_ids: tuple[str, ...],
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]: ...

    async def task_attempt_started_at(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
    ) -> datetime: ...

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
        priority: int = 0,
        worker_group: str | None = None,
    ) -> PersistedTaskRun: ...

    async def record_task_control(
        self,
        task_run_id: UUID,
        attempt: int,
        evidence: dict[str, object],
        *,
        tenant_id: str,
    ) -> PersistedTaskRun: ...

    async def skip_task(
        self,
        task_run_id: UUID,
        result: dict[str, Any],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
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
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun: ...

    async def defer_task(
        self,
        task_run_id: UUID,
        attempt: int,
        resume_token: str,
        *,
        tenant_id: str,
        metadata: dict[str, object],
        expires_at: datetime | None = None,
    ) -> PersistedTaskDeferral: ...

    async def get_task_deferral(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedTaskDeferral | None: ...

    async def resume_deferred_task(
        self,
        task_run_id: UUID,
        resume_token: str,
        result: dict[str, object],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
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
        result: dict[str, object] | None = None,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
        evidence: dict[str, object] | None = None,
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

    async def record_execution_lifecycle(
        self,
        execution_id: UUID,
        evidence: dict[str, object],
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

    async def list_subflows(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedSubflow]: ...

    async def get_parent_subflow(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedSubflow | None: ...
