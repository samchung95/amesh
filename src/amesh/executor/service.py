from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections.abc import Awaitable, Callable, Iterable, Mapping
from contextlib import suppress
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, cast
from uuid import UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field

from amesh import __version__
from amesh.admission_policy import AdmissionPolicyDenied, policy_decision_metadata
from amesh.backoff import bounded_exponential_backoff
from amesh.domain import (
    AdmissionOutcome,
    AdmissionResourceType,
    AgentMeshDefinition,
    AgentMeshSessionBudget,
    ExecutionState,
    FailureCategory,
    PolicyDecision,
    resolve_admission_policies,
)
from amesh.dsl import (
    ConditionErrorPolicy,
    ErrorSelector,
    FlowableFailurePolicy,
    FlowDefinition,
    LifecyclePhase,
    PlannedTask,
    ResourceKind,
    ResourceSchemaRegistry,
    TaskResourceLimits,
    compile_execution_tasks,
    compile_flow_tasks,
    default_resource_registry,
    visible_output_ids,
)
from amesh.dsl.models import RetryPolicy, TaskDefinition
from amesh.expressions import (
    ExpressionContext,
    ExpressionEngine,
    NativeExpressionEngine,
    redact_secret_values,
)
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    LogSourceStream,
    ObjectStore,
    PersistedExecution,
    PersistedTaskRun,
    TaskCacheDecision,
    TaskCacheKey,
    TaskCacheLookup,
    TaskCacheMode,
    TaskCacheRepository,
    TaskRunState,
    TaskStateConflictError,
    redact_runner_payload,
)
from amesh.workflow.data_contracts import render_flow_outputs, validate_flow_inputs
from amesh.workflow.working_directory import WorkingDirectoryManager

from .contracts import (
    TaskArtifactRecord,
    TaskCompletion,
    TaskContextProvider,
    TaskContextRequest,
    TaskContextResources,
    TaskDeferral,
    TaskFileReference,
    TaskHandlerResult,
    TaskLogRecord,
)
from .loops import (
    LOOP_TASK_TYPES,
    LoopItem,
    LoopIterationContext,
    LoopSpec,
    iter_foreach_items,
    parse_loop_spec,
)

LOGGER = logging.getLogger("amesh.task.core.log")


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
class _TaskRunOutcome:
    claimed: bool
    failure: str | None = None


@dataclass(frozen=True)
class _ConditionDecision:
    matched: bool
    evidence: dict[str, object]
    error: Exception | None = None


@dataclass(frozen=True)
class _BranchDecision:
    selected_branch: str | None
    evidence: dict[str, object]
    error: Exception | None = None


class InProcessExecutor:
    """Runs the MVP top-level DAG while PostgreSQL remains authoritative for progress."""

    def __init__(
        self,
        repository: ExecutionRepository,
        handlers: Mapping[str, TaskHandler] | None = None,
        expressions: ExpressionEngine | None = None,
        recover_running_types: frozenset[str] | None = None,
        context_provider: TaskContextProvider | None = None,
        resource_registry: ResourceSchemaRegistry | None = None,
        object_store: ObjectStore | None = None,
        task_cache: TaskCacheRepository | None = None,
        workspace_manager: WorkingDirectoryManager | None = None,
        dispatch_policy_enforcer: DispatchPolicyEnforcer | None = None,
        admission_poll_initial_seconds: float = 0.05,
        admission_poll_max_seconds: float = 1.0,
    ) -> None:
        if admission_poll_initial_seconds <= 0:
            raise ValueError("admission_poll_initial_seconds must be positive")
        if admission_poll_max_seconds < admission_poll_initial_seconds:
            raise ValueError(
                "admission_poll_max_seconds must be at least admission_poll_initial_seconds"
            )
        self._repository = repository
        self._handlers = _core_handlers()
        self._handlers.update(handlers or {})
        self._expressions = expressions or NativeExpressionEngine()
        self._recover_running_types = (recover_running_types or frozenset()) | LOOP_TASK_TYPES
        self._context_provider = context_provider
        self._resource_registry = resource_registry or default_resource_registry()
        self._object_store = object_store
        self._task_cache = task_cache
        self._workspace_manager = workspace_manager
        self._dispatch_policy_enforcer = dispatch_policy_enforcer
        self._admission_poll_initial_seconds = admission_poll_initial_seconds
        self._admission_poll_max_seconds = admission_poll_max_seconds

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, Any] | None = None,
        launch_source: ExecutionLaunchSource = ExecutionLaunchSource.MANUAL,
    ) -> UUID:
        if flow.disabled:
            raise ValueError(f"flow {flow.namespace}.{flow.id} is disabled")
        _validate_registered_task_schemas(flow, self._resource_registry)
        validated_inputs = validate_flow_inputs(flow, inputs or {})
        execution = await self._repository.create_execution(
            flow,
            tenant_id=tenant_id,
            inputs=validated_inputs,
            launch_source=launch_source,
        )
        return execution.execution_id

    async def run_ready(
        self,
        flow: FlowDefinition,
        execution_id: UUID,
        *,
        tenant_id: str,
        max_tasks: int | None = None,
    ) -> ExecutionProgress:
        if max_tasks is not None and max_tasks < 1:
            raise ValueError("max_tasks must be at least 1")

        execution = await self._repository.get_execution(execution_id, tenant_id=tenant_id)
        task_runs = await self._repository.list_task_runs(execution_id, tenant_id=tenant_id)
        execution_plan = compile_execution_tasks(flow)
        if execution.state is not ExecutionState.RUNNING:
            if execution_lifecycle_pending(flow, execution, task_runs):
                return await self._advance_execution_lifecycle(
                    flow,
                    execution,
                    execution_plan,
                    task_runs,
                    primary_decision=None,
                    max_tasks=max_tasks,
                )
            return ExecutionProgress(
                execution_id=execution_id,
                state=execution.state,
                tasks_run=0,
                task_runs=tuple(task_runs),
            )

        now = await self._repository.database_time()
        if execution.timeout_at is not None and now >= execution.timeout_at:
            timed_out = await self._repository.timeout_execution(
                execution_id,
                tenant_id=tenant_id,
                expected_epoch=execution.epoch,
            )
            timed_out_runs = await self._repository.list_task_runs(
                execution_id,
                tenant_id=tenant_id,
            )
            if execution_lifecycle_pending(flow, timed_out, timed_out_runs):
                return await self._advance_execution_lifecycle(
                    flow,
                    timed_out,
                    execution_plan,
                    timed_out_runs,
                    primary_decision=None,
                    max_tasks=max_tasks,
                )
            return ExecutionProgress(
                execution_id=execution_id,
                state=timed_out.state,
                tasks_run=0,
                task_runs=tuple(timed_out_runs),
            )
        deferred_task_run_ids: set[UUID] = set()
        expired_deferral = False
        for task_run in task_runs:
            if task_run.state is not TaskRunState.RUNNING:
                continue
            deferral = await self._repository.get_task_deferral(
                task_run.task_run_id,
                tenant_id=tenant_id,
            )
            if deferral is None:
                continue
            if deferral.state == "EXPIRED" or (
                deferral.state == "WAITING"
                and deferral.expires_at is not None
                and now >= deferral.expires_at
            ):
                with suppress(TaskStateConflictError):
                    await self._repository.fail_task(
                        task_run.task_run_id,
                        deferral.attempt,
                        "asynchronous task deferral expired",
                        tenant_id=tenant_id,
                        failure_category=FailureCategory.TIMED_OUT,
                    )
                expired_deferral = True
            elif deferral.state == "WAITING":
                deferred_task_run_ids.add(task_run.task_run_id)
        if expired_deferral:
            task_runs = await self._repository.list_task_runs(
                execution_id,
                tenant_id=tenant_id,
            )

        plan = compile_flow_tasks(flow)
        task_runs = await self._advance_flowables(
            flow,
            execution,
            plan,
            task_runs,
            tenant_id=tenant_id,
        )
        decision = reduce_orchestration(flow, _main_task_runs(task_runs), now=now)
        if decision.terminal_state is not None:
            if _lifecycle_plan(execution_plan):
                return await self._advance_execution_lifecycle(
                    flow,
                    execution,
                    execution_plan,
                    task_runs,
                    primary_decision=decision,
                    max_tasks=max_tasks,
                )
            execution = await self._finish_execution(flow, execution, decision, task_runs)
            return ExecutionProgress(
                execution_id=execution_id,
                state=execution.state,
                tasks_run=0,
                task_runs=tuple(task_runs),
            )

        task_runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
        runnable_ids = set(decision.runnable_task_ids)
        ready = _select_ready_tasks(
            plan,
            task_runs_by_id,
            runnable_ids,
            self._recover_running_types,
            deferred_task_run_ids,
            max_tasks=max_tasks,
        )

        outputs = {
            task_id: task_run.result or {}
            for task_id, task_run in task_runs_by_id.items()
            if task_run.state is TaskRunState.SUCCESS
        }
        plan_by_id = {node.task.id: node for node in plan}
        task_coroutines = tuple(
            self._run_task(
                flow,
                execution,
                task_runs_by_id[node.task.id],
                node.task,
                {
                    task_id: output
                    for task_id, output in outputs.items()
                    if task_id in visible_output_ids(node.task.id, plan)
                },
                workspace_parent=_working_directory_ancestor(node, plan_by_id),
            )
            for node in ready
        )
        try:
            if execution.timeout_at is None:
                outcomes = await asyncio.gather(*task_coroutines)
            else:
                remaining = max((execution.timeout_at - now).total_seconds(), 0)
                async with asyncio.timeout(remaining):
                    outcomes = await asyncio.gather(*task_coroutines)
        except TimeoutError as exc:
            await self._repository.timeout_execution(
                execution_id,
                tenant_id=tenant_id,
                expected_epoch=execution.epoch,
            )
            raise TaskExecutionError("execution deadline exceeded") from exc

        updated_task_runs = await self._repository.list_task_runs(
            execution_id,
            tenant_id=tenant_id,
        )
        updated_task_runs = await self._advance_flowables(
            flow,
            execution,
            plan,
            updated_task_runs,
            tenant_id=tenant_id,
        )
        updated_decision = reduce_orchestration(
            flow,
            _main_task_runs(updated_task_runs),
            now=await self._repository.database_time(),
        )
        if updated_decision.terminal_state is not None:
            if _lifecycle_plan(execution_plan):
                return await self._advance_execution_lifecycle(
                    flow,
                    execution,
                    execution_plan,
                    updated_task_runs,
                    primary_decision=updated_decision,
                    max_tasks=max_tasks,
                    claimed_tasks=sum(outcome.claimed for outcome in outcomes),
                    primary_failure=next(
                        (outcome.failure for outcome in outcomes if outcome.failure),
                        None,
                    ),
                )
            execution = await self._finish_execution(
                flow,
                execution,
                updated_decision,
                updated_task_runs,
            )
        else:
            execution = await self._repository.get_execution(execution_id, tenant_id=tenant_id)
        progress = ExecutionProgress(
            execution_id=execution_id,
            state=execution.state,
            tasks_run=sum(outcome.claimed for outcome in outcomes),
            task_runs=tuple(updated_task_runs),
        )
        failure = next((outcome.failure for outcome in outcomes if outcome.failure), None)
        if failure is not None and updated_decision.terminal_state is not None:
            raise TaskExecutionError(updated_decision.diagnostic or failure)
        return progress

    async def _advance_execution_lifecycle(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        execution_plan: tuple[PlannedTask, ...],
        task_runs: list[PersistedTaskRun],
        *,
        primary_decision: OrchestrationDecision | None,
        max_tasks: int | None,
        claimed_tasks: int = 0,
        primary_failure: str | None = None,
    ) -> ExecutionProgress:
        lifecycle_plan = _lifecycle_plan(execution_plan)
        if not lifecycle_plan:
            if primary_decision is None:
                return ExecutionProgress(
                    execution_id=execution.execution_id,
                    state=execution.state,
                    tasks_run=claimed_tasks,
                    task_runs=tuple(task_runs),
                )
            finished = await self._finish_execution(
                flow,
                execution,
                primary_decision,
                task_runs,
            )
            if primary_failure is not None:
                raise TaskExecutionError(primary_decision.diagnostic or primary_failure)
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=finished.state,
                tasks_run=claimed_tasks,
                task_runs=tuple(task_runs),
            )

        evidence = deepcopy(execution.lifecycle_evidence)
        primary = evidence.get("primary")
        if not isinstance(primary, Mapping):
            primary_state = (
                primary_decision.terminal_state if primary_decision is not None else execution.state
            )
            if primary_state not in {
                ExecutionState.SUCCESS,
                ExecutionState.FAILED,
                ExecutionState.CANCELLED,
                ExecutionState.WARNING,
            }:
                raise ExecutionBlockedError(
                    f"execution {execution.execution_id} has no terminal primary outcome"
                )
            errors = _main_error_items(execution_plan, task_runs)
            diagnostic = (
                primary_decision.diagnostic
                if primary_decision is not None
                else primary_failure or _primary_error_message(errors)
            )
            primary = {
                "state": primary_state.value,
                "diagnostic": diagnostic,
                "errors": errors,
            }
            evidence = {
                "schemaVersion": 1,
                "status": LifecyclePhase.ERROR.value,
                "primary": primary,
                "phases": {},
            }
            execution = await self._repository.record_execution_lifecycle(
                execution.execution_id,
                evidence,
                tenant_id=execution.tenant_id,
                expected_epoch=execution.epoch,
            )

        primary_state = ExecutionState(str(primary["state"]))
        phases = evidence.get("phases")
        phase_evidence = dict(phases) if isinstance(phases, Mapping) else {}
        handler_errors = _handler_error_contexts(execution_plan, task_runs, primary_state)

        error_plan = _phase_plan(lifecycle_plan, LifecyclePhase.ERROR)
        if not _phase_was_completed(phase_evidence, LifecyclePhase.ERROR):
            skip_ids = {
                node.task.id
                for node in error_plan
                if primary_state not in {ExecutionState.FAILED, ExecutionState.CANCELLED}
                or not _error_handler_is_applicable(
                    node,
                    primary_state,
                    handler_errors.get(node.task.id),
                )
            }
            if skip_ids:
                task_runs = await self._skip_lifecycle_tasks(
                    task_runs,
                    skip_ids,
                    LifecyclePhase.ERROR,
                    tenant_id=execution.tenant_id,
                    reason=f"error handler not selected for {primary_state.value}",
                )
            phase_progress = await self._run_lifecycle_phase(
                flow,
                execution,
                error_plan,
                task_runs,
                handler_errors=handler_errors,
                max_tasks=max_tasks,
            )
            task_runs = list(phase_progress.task_runs)
            claimed_tasks += phase_progress.tasks_run
            if not _phase_is_complete(error_plan, task_runs):
                return phase_progress.model_copy(update={"tasks_run": claimed_tasks})
            phase_evidence[LifecyclePhase.ERROR.value] = _completed_phase_evidence(
                error_plan,
                task_runs,
            )
            evidence.update(
                {
                    "status": LifecyclePhase.FINALLY.value,
                    "phases": phase_evidence,
                }
            )
            execution = await self._repository.record_execution_lifecycle(
                execution.execution_id,
                evidence,
                tenant_id=execution.tenant_id,
                expected_epoch=execution.epoch,
            )
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=execution.state,
                tasks_run=claimed_tasks,
                task_runs=tuple(task_runs),
            )

        finally_plan = _phase_plan(lifecycle_plan, LifecyclePhase.FINALLY)
        if not _phase_was_completed(phase_evidence, LifecyclePhase.FINALLY):
            phase_progress = await self._run_lifecycle_phase(
                flow,
                execution,
                finally_plan,
                task_runs,
                handler_errors={},
                max_tasks=max_tasks,
            )
            task_runs = list(phase_progress.task_runs)
            claimed_tasks += phase_progress.tasks_run
            if not _phase_is_complete(finally_plan, task_runs):
                return phase_progress.model_copy(update={"tasks_run": claimed_tasks})
            phase_evidence[LifecyclePhase.FINALLY.value] = _completed_phase_evidence(
                finally_plan,
                task_runs,
            )
            evidence.update(
                {
                    "status": LifecyclePhase.AFTER_EXECUTION.value,
                    "phases": phase_evidence,
                }
            )
            execution = await self._repository.record_execution_lifecycle(
                execution.execution_id,
                evidence,
                tenant_id=execution.tenant_id,
                expected_epoch=execution.epoch,
            )
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=execution.state,
                tasks_run=claimed_tasks,
                task_runs=tuple(task_runs),
            )

        if execution.state is ExecutionState.RUNNING:
            terminal_decision = OrchestrationDecision(
                terminal_state=primary_state,
                diagnostic=(str(primary.get("diagnostic")) if primary.get("diagnostic") else None),
            )
            execution = await self._finish_execution(
                flow,
                execution,
                terminal_decision,
                task_runs,
            )
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=execution.state,
                tasks_run=claimed_tasks,
                task_runs=tuple(task_runs),
            )

        after_plan = _phase_plan(lifecycle_plan, LifecyclePhase.AFTER_EXECUTION)
        if not _phase_was_completed(phase_evidence, LifecyclePhase.AFTER_EXECUTION):
            terminal_errors = _handler_error_contexts(
                execution_plan,
                task_runs,
                primary_state,
            )
            phase_progress = await self._run_lifecycle_phase(
                flow,
                execution,
                after_plan,
                task_runs,
                handler_errors=terminal_errors,
                max_tasks=max_tasks,
            )
            task_runs = list(phase_progress.task_runs)
            claimed_tasks += phase_progress.tasks_run
            if not _phase_is_complete(after_plan, task_runs):
                return phase_progress.model_copy(update={"tasks_run": claimed_tasks})
            phase_evidence[LifecyclePhase.AFTER_EXECUTION.value] = _completed_phase_evidence(
                after_plan,
                task_runs,
            )
            evidence.update({"status": "COMPLETE", "phases": phase_evidence})
            execution = await self._repository.record_execution_lifecycle(
                execution.execution_id,
                evidence,
                tenant_id=execution.tenant_id,
                expected_epoch=execution.epoch,
            )
        return ExecutionProgress(
            execution_id=execution.execution_id,
            state=execution.state,
            tasks_run=claimed_tasks,
            task_runs=tuple(task_runs),
        )

    async def _run_lifecycle_phase(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        plan: tuple[PlannedTask, ...],
        task_runs: list[PersistedTaskRun],
        *,
        handler_errors: Mapping[str, Mapping[str, Any]],
        max_tasks: int | None,
    ) -> ExecutionProgress:
        if not plan:
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=execution.state,
                tasks_run=0,
                task_runs=tuple(task_runs),
            )
        task_runs = await self._advance_flowables(
            flow,
            execution,
            plan,
            task_runs,
            tenant_id=execution.tenant_id,
            handler_errors=handler_errors,
        )
        now = await self._repository.database_time()
        decision = _reduce_lifecycle_phase(plan, task_runs, now=now)
        if decision.terminal_state is not None:
            waiting_ids = {
                node.task.id
                for node in plan
                if next(
                    (task_run.state for task_run in task_runs if task_run.task_id == node.task.id),
                    None,
                )
                is TaskRunState.WAITING
            }
            if waiting_ids:
                task_runs = await self._skip_lifecycle_tasks(
                    task_runs,
                    waiting_ids,
                    plan[0].lifecycle_phase,
                    tenant_id=execution.tenant_id,
                    reason="lifecycle flowable reached a terminal state",
                )
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=execution.state,
                tasks_run=0,
                task_runs=tuple(task_runs),
            )
        by_task_id = {task_run.task_id: task_run for task_run in task_runs}
        ready = _select_ready_tasks(
            plan,
            by_task_id,
            set(decision.runnable_task_ids),
            self._recover_running_types,
            set(),
            max_tasks=max_tasks,
        )
        outputs = {
            task_id: task_run.result or {}
            for task_id, task_run in by_task_id.items()
            if task_run.state is TaskRunState.SUCCESS
        }
        outcomes = await asyncio.gather(
            *(
                self._run_task(
                    flow,
                    execution,
                    by_task_id[node.task.id],
                    node.task,
                    outputs,
                    workspace_parent=_working_directory_ancestor(
                        node,
                        {candidate.task.id: candidate for candidate in plan},
                    ),
                    handler_error=handler_errors.get(node.task.id),
                )
                for node in ready
            )
        )
        refreshed = await self._repository.list_task_runs(
            execution.execution_id,
            tenant_id=execution.tenant_id,
        )
        refreshed = await self._advance_flowables(
            flow,
            execution,
            plan,
            refreshed,
            tenant_id=execution.tenant_id,
            handler_errors=handler_errors,
        )
        return ExecutionProgress(
            execution_id=execution.execution_id,
            state=execution.state,
            tasks_run=sum(outcome.claimed for outcome in outcomes),
            task_runs=tuple(refreshed),
        )

    async def _skip_lifecycle_tasks(
        self,
        task_runs: list[PersistedTaskRun],
        task_ids: set[str],
        phase: LifecyclePhase,
        *,
        tenant_id: str,
        reason: str,
    ) -> list[PersistedTaskRun]:
        for task_run in task_runs:
            if task_run.task_id not in task_ids or task_run.state is not TaskRunState.WAITING:
                continue
            with suppress(TaskStateConflictError):
                await self._repository.skip_task(
                    task_run.task_run_id,
                    {"skipped": True, "reason": reason},
                    tenant_id=tenant_id,
                    evidence={
                        "control": {
                            "lifecycle": {
                                "phase": phase.value,
                                "reason": reason,
                            }
                        }
                    },
                )
        return await self._repository.list_task_runs(
            task_runs[0].execution_id,
            tenant_id=tenant_id,
        )

    async def _advance_flowables(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        plan: tuple[PlannedTask, ...],
        task_runs: list[PersistedTaskRun],
        *,
        tenant_id: str,
        handler_errors: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> list[PersistedTaskRun]:
        """Start and reduce durable flowable parents without dispatching handlers."""

        by_node_id = {node.task.id: node for node in plan}
        by_task_id = {task_run.task_id: task_run for task_run in task_runs}
        changed = True
        while changed:
            changed = False
            for node in plan:
                task_run = by_task_id[node.task.id]
                if not node.flowable or node.dynamic or task_run.state is not TaskRunState.WAITING:
                    continue
                if not _parent_is_running(node, by_task_id):
                    continue
                if not _dependencies_satisfied(node, by_node_id, by_task_id):
                    continue
                expression_context = _flowable_expression_context(
                    flow,
                    execution,
                    node,
                    task_run,
                    plan,
                    by_task_id,
                    handler_error=(handler_errors or {}).get(node.task.id),
                )
                run_if = self._evaluate_task_condition(
                    flow,
                    execution,
                    node.task,
                    expression_context,
                    (handler_errors or {}).get(node.task.id),
                )
                if run_if.error is not None:
                    running = await self._repository.start_task(
                        task_run.task_run_id,
                        tenant_id=tenant_id,
                        dispatch=False,
                    )
                    reason = f"flowable runIf failed: {run_if.error}"
                    by_task_id[node.task.id] = await self._repository.fail_task(
                        running.task_run_id,
                        running.current_attempt,
                        reason,
                        tenant_id=tenant_id,
                        failure_category=FailureCategory.CONFIGURATION,
                        evidence=run_if.evidence,
                    )
                    changed = True
                    continue
                if not run_if.matched:
                    changed = (
                        await self._skip_flowable_subtree(
                            node,
                            plan,
                            by_node_id,
                            by_task_id,
                            tenant_id=tenant_id,
                            evidence=run_if.evidence,
                        )
                        or changed
                    )
                    continue
                running = await self._repository.start_task(
                    task_run.task_run_id,
                    tenant_id=tenant_id,
                    dispatch=False,
                )
                if node.task.run_if is not None or node.task.error_selector is not None:
                    running = await self._repository.record_task_control(
                        running.task_run_id,
                        running.current_attempt,
                        run_if.evidence,
                        tenant_id=tenant_id,
                    )
                by_task_id[node.task.id] = running
                changed = True

            for node in plan:
                task_run = by_task_id[node.task.id]
                if node.mode not in {"IF", "SWITCH"} or task_run.state is not TaskRunState.RUNNING:
                    continue
                branch_evidence = _branch_evidence(task_run.evidence)
                if branch_evidence is None:
                    expression_context = _flowable_expression_context(
                        flow,
                        execution,
                        node,
                        task_run,
                        plan,
                        by_task_id,
                        handler_error=(handler_errors or {}).get(node.task.id),
                    )
                    decision = self._select_branch(
                        flow,
                        execution,
                        node.task,
                        expression_context,
                    )
                    evidence = _merge_task_control(
                        task_run.evidence,
                        "branch",
                        decision.evidence,
                    )
                    if decision.error is not None:
                        reason = f"conditional branch evaluation failed: {decision.error}"
                        by_task_id[node.task.id] = await self._repository.fail_task(
                            task_run.task_run_id,
                            task_run.current_attempt,
                            reason,
                            tenant_id=tenant_id,
                            failure_category=FailureCategory.CONFIGURATION,
                            evidence=evidence,
                        )
                        changed = True
                        continue
                    task_run = await self._repository.record_task_control(
                        task_run.task_run_id,
                        task_run.current_attempt,
                        evidence,
                        tenant_id=tenant_id,
                    )
                    by_task_id[node.task.id] = task_run
                    branch_evidence = decision.evidence
                    changed = True
                selected_branch = branch_evidence.get("selectedBranch")
                if selected_branch is not None and not isinstance(selected_branch, str):
                    selected_branch = str(selected_branch)
                changed = (
                    await self._skip_nonselected_branches(
                        node,
                        plan,
                        by_node_id,
                        by_task_id,
                        selected_branch=selected_branch,
                        tenant_id=tenant_id,
                    )
                    or changed
                )

            for node in reversed(plan):
                task_run = by_task_id[node.task.id]
                if not node.flowable or node.dynamic or task_run.state is not TaskRunState.RUNNING:
                    continue
                children = [by_task_id[child_id] for child_id in node.children]
                failed = [
                    child
                    for child in children
                    if child.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
                ]
                terminal = all(_task_run_is_terminal(child) for child in children)
                mesh_budget_error = _agent_mesh_budget_error(node, children) if terminal else None
                workspace_output: dict[str, object] = {}
                workspace_evidence: dict[str, object] = {}
                should_finalize_workspace = node.task.type == "core.workingDirectory" and (
                    terminal or (failed and node.failure_policy is FlowableFailurePolicy.FAIL_FAST)
                )
                if should_finalize_workspace:
                    try:
                        (
                            workspace_output,
                            workspace_evidence,
                        ) = await self._finalize_working_directory(
                            execution,
                            node,
                            task_run,
                            failed=bool(failed),
                        )
                    except Exception as exc:
                        reason = f"working directory finalization failed: {exc}"
                        by_task_id[node.task.id] = await self._repository.fail_task(
                            task_run.task_run_id,
                            task_run.current_attempt,
                            reason,
                            tenant_id=tenant_id,
                            failure_category=classify_task_failure(exc),
                            evidence=task_run.evidence,
                        )
                        changed = True
                        continue
                if failed and node.failure_policy is FlowableFailurePolicy.FAIL_FAST:
                    failed_ids = [child.task_id for child in failed]
                    reason = f"flowable child failure: {failed_ids}"
                    by_task_id[node.task.id] = await self._repository.fail_task(
                        task_run.task_run_id,
                        task_run.current_attempt,
                        reason,
                        tenant_id=tenant_id,
                        result={
                            **_aggregate_flowable_result(node, children),
                            **workspace_output,
                            "error": reason,
                        },
                        evidence=_merge_completion_evidence(
                            workspace_evidence,
                            task_run.evidence,
                        ),
                    )
                    changed = True
                elif mesh_budget_error is not None:
                    by_task_id[node.task.id] = await self._repository.fail_task(
                        task_run.task_run_id,
                        task_run.current_attempt,
                        mesh_budget_error,
                        tenant_id=tenant_id,
                        failure_category=FailureCategory.NON_RETRYABLE,
                        result={
                            **_aggregate_flowable_result(node, children),
                            "error": mesh_budget_error,
                        },
                        evidence=task_run.evidence,
                    )
                    changed = True
                elif terminal and (
                    not failed or node.failure_policy is FlowableFailurePolicy.CONTINUE_ON_ERROR
                ):
                    by_task_id[node.task.id] = await self._repository.complete_task(
                        task_run.task_run_id,
                        task_run.current_attempt,
                        {
                            **_aggregate_flowable_result(node, children),
                            **workspace_output,
                            **(
                                {"control": task_run.evidence["control"]}
                                if task_run.evidence.get("control")
                                else {}
                            ),
                        },
                        tenant_id=tenant_id,
                        evidence=_merge_completion_evidence(
                            workspace_evidence,
                            task_run.evidence,
                        ),
                    )
                    changed = True
                elif terminal and node.failure_policy is FlowableFailurePolicy.COLLECT_ALL:
                    failed_ids = [child.task_id for child in failed]
                    reason = f"flowable collected child failures: {failed_ids}"
                    by_task_id[node.task.id] = await self._repository.fail_task(
                        task_run.task_run_id,
                        task_run.current_attempt,
                        reason,
                        tenant_id=tenant_id,
                        result={
                            **_aggregate_flowable_result(node, children),
                            **workspace_output,
                            "error": reason,
                        },
                        evidence=_merge_completion_evidence(
                            workspace_evidence,
                            task_run.evidence,
                        ),
                    )
                    changed = True
        return list(by_task_id.values())

    async def _finalize_working_directory(
        self,
        execution: PersistedExecution,
        node: PlannedTask,
        task_run: PersistedTaskRun,
        *,
        failed: bool,
    ) -> tuple[dict[str, object], dict[str, object]]:
        if self._workspace_manager is None:
            raise TaskConfigurationError("core.workingDirectory requires a workspace manager")
        workspace = await self._workspace_manager.prepare(
            tenant_id=execution.tenant_id,
            execution_id=str(execution.execution_id),
            task_run_id=str(task_run.task_run_id),
            attempt_id=str(uuid5(task_run.task_run_id, f"attempt:{task_run.current_attempt}")),
            scope_id=node.task.id,
            input_files={},
            file_references={},
            quota_bytes=node.task.workspace_quota_bytes,
        )
        try:
            if failed:
                artifacts: tuple[TaskArtifactRecord, ...] = ()
                if node.task.retain_diagnostics_on_failure:
                    artifacts = (
                        await self._workspace_manager.retain_failure_diagnostics(
                            workspace,
                            tenant_id=execution.tenant_id,
                            execution_id=str(execution.execution_id),
                            task_run_id=str(task_run.task_run_id),
                            attempt=task_run.current_attempt,
                            details={"flowable": node.task.id, "state": "FAILED"},
                            quota_bytes=node.task.workspace_quota_bytes,
                        ),
                    )
                output_files: Mapping[str, str] = {}
            else:
                collected = await self._workspace_manager.collect(
                    workspace,
                    tenant_id=execution.tenant_id,
                    execution_id=str(execution.execution_id),
                    task_run_id=str(task_run.task_run_id),
                    attempt=task_run.current_attempt,
                    patterns=node.task.output_files,
                    manifest_path=node.task.output_manifest,
                    quota_bytes=node.task.workspace_quota_bytes,
                )
                artifacts = collected.artifacts
                output_files = collected.output_files
            output, evidence = normalize_task_completion(
                TaskCompletion(
                    output={"outputFiles": dict(output_files)},
                    artifacts=artifacts,
                ),
                node.task.contract.resource_limits,
            )
            return output, evidence
        finally:
            self._workspace_manager.cleanup(workspace.path)

    async def _skip_flowable_subtree(
        self,
        node: PlannedTask,
        plan: tuple[PlannedTask, ...],
        by_node_id: Mapping[str, PlannedTask],
        by_task_id: dict[str, PersistedTaskRun],
        *,
        tenant_id: str,
        evidence: dict[str, object],
    ) -> bool:
        changed = False
        for candidate in reversed(plan):
            if candidate.task.id != node.task.id and not _descends_from(
                candidate,
                node,
                by_node_id,
            ):
                continue
            task_run = by_task_id[candidate.task.id]
            if task_run.state is not TaskRunState.WAITING:
                continue
            by_task_id[candidate.task.id] = await self._repository.skip_task(
                task_run.task_run_id,
                {
                    "skipped": True,
                    "reason": f"flowable {node.task.id!r} runIf evaluated false",
                    "controlTask": node.task.id,
                },
                tenant_id=tenant_id,
                evidence=evidence
                if candidate.task.id == node.task.id
                else {
                    "control": {
                        "parentTask": node.task.id,
                        "reason": "parent flowable skipped",
                    }
                },
            )
            changed = True
        return changed

    async def _skip_nonselected_branches(
        self,
        node: PlannedTask,
        plan: tuple[PlannedTask, ...],
        by_node_id: Mapping[str, PlannedTask],
        by_task_id: dict[str, PersistedTaskRun],
        *,
        selected_branch: str | None,
        tenant_id: str,
    ) -> bool:
        selected_path = (
            f"{node.branch_id}/{selected_branch}"
            if node.branch_id is not None and selected_branch is not None
            else selected_branch
        )
        changed = False
        for candidate in reversed(plan):
            if not _descends_from(candidate, node, by_node_id):
                continue
            if (
                selected_path is not None
                and candidate.branch_id is not None
                and (
                    candidate.branch_id == selected_path
                    or candidate.branch_id.startswith(f"{selected_path}/")
                )
            ):
                continue
            task_run = by_task_id[candidate.task.id]
            if task_run.state is not TaskRunState.WAITING:
                continue
            by_task_id[candidate.task.id] = await self._repository.skip_task(
                task_run.task_run_id,
                {
                    "skipped": True,
                    "reason": f"conditional branch {selected_branch!r} selected",
                    "controlTask": node.task.id,
                    "branch": candidate.branch_id,
                    "selectedBranch": selected_branch,
                },
                tenant_id=tenant_id,
                evidence={
                    "control": {
                        "parentTask": node.task.id,
                        "branch": candidate.branch_id,
                        "selectedBranch": selected_branch,
                    }
                },
            )
            changed = True
        return changed

    def _evaluate_run_if(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> _ConditionDecision:
        if task.run_if is None:
            return _ConditionDecision(matched=True, evidence={})
        record: dict[str, object] = {
            "kind": "runIf",
            "expression": task.run_if,
            "conditionInputs": _redacted_condition_inputs(flow, execution, context),
            "policy": task.condition_error_policy.value,
        }
        try:
            matched = self._expressions.evaluate_condition(task.run_if, context)
        except Exception as exc:
            record.update(
                {
                    "result": False,
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                }
            )
            evidence = _merge_task_control({}, "runIf", record)
            if task.condition_error_policy is ConditionErrorPolicy.FALSE:
                return _ConditionDecision(matched=False, evidence=evidence)
            return _ConditionDecision(matched=False, evidence=evidence, error=exc)
        record["result"] = matched
        return _ConditionDecision(
            matched=matched,
            evidence=_merge_task_control({}, "runIf", record),
        )

    def _evaluate_error_selector(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        selector: ErrorSelector | None,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> _ConditionDecision:
        if selector is None:
            return _ConditionDecision(matched=True, evidence={})
        raw_items = (handler_error or {}).get("items", ())
        items = [dict(item) for item in raw_items if isinstance(item, Mapping)]
        matched_items = [
            item
            for item in items
            if (not selector.states or item.get("state") in selector.states)
            and (not selector.categories or item.get("category") in selector.categories)
            and (not selector.task_ids or item.get("taskId") in selector.task_ids)
        ]
        record: dict[str, object] = {
            "kind": "errorSelector",
            "selector": selector.model_dump(mode="json", by_alias=True, exclude_none=True),
            "matchedTaskIds": [str(item.get("taskId")) for item in matched_items],
            "conditionInputs": _redacted_condition_inputs(flow, execution, context),
        }
        matched = bool(matched_items)
        if matched and selector.condition is not None:
            try:
                matched = self._expressions.evaluate_condition(selector.condition, context)
            except Exception as exc:
                record.update(
                    {
                        "result": False,
                        "error": {"type": type(exc).__name__, "message": str(exc)},
                    }
                )
                return _ConditionDecision(
                    matched=False,
                    evidence=_merge_task_control({}, "errorSelector", record),
                    error=exc,
                )
        record["result"] = matched
        return _ConditionDecision(
            matched=matched,
            evidence=_merge_task_control({}, "errorSelector", record),
        )

    def _evaluate_task_condition(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> _ConditionDecision:
        selector = self._evaluate_error_selector(
            flow,
            execution,
            task.error_selector,
            context,
            handler_error,
        )
        if not selector.matched or selector.error is not None:
            return selector
        run_if = self._evaluate_run_if(flow, execution, task, context)
        return _ConditionDecision(
            matched=run_if.matched,
            evidence=_merge_control_evidence(selector.evidence, run_if.evidence),
            error=run_if.error,
        )

    def _select_branch(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> _BranchDecision:
        inputs = _redacted_condition_inputs(flow, execution, context)
        evaluations: list[dict[str, object]] = []
        policy = task.condition_error_policy
        if task.type == "core.if":
            branches = [("then", task.condition or "")]
            branches.extend((f"else-if:{branch.id}", branch.condition) for branch in task.else_if)
            for branch_id, expression in branches:
                try:
                    result = self._expressions.evaluate_condition(expression, context)
                except Exception as exc:
                    evaluations.append(
                        {
                            "branch": branch_id,
                            "expression": expression,
                            "result": False,
                            "error": {
                                "type": type(exc).__name__,
                                "message": str(exc),
                            },
                        }
                    )
                    branch_error_evidence: dict[str, object] = {
                        "kind": "IF",
                        "conditionInputs": inputs,
                        "evaluations": evaluations,
                        "policy": policy.value,
                        "selectedBranch": "else"
                        if policy is ConditionErrorPolicy.FALLBACK
                        else None,
                    }
                    if policy is ConditionErrorPolicy.FAIL:
                        return _BranchDecision(None, branch_error_evidence, error=exc)
                    if policy is ConditionErrorPolicy.FALLBACK:
                        return _BranchDecision("else", branch_error_evidence)
                    continue
                evaluations.append(
                    {
                        "branch": branch_id,
                        "expression": expression,
                        "result": result,
                    }
                )
                if result:
                    return _BranchDecision(
                        branch_id,
                        {
                            "kind": "IF",
                            "conditionInputs": inputs,
                            "evaluations": evaluations,
                            "policy": policy.value,
                            "selectedBranch": branch_id,
                        },
                    )
            selected = "else" if task.else_tasks else None
            return _BranchDecision(
                selected,
                {
                    "kind": "IF",
                    "conditionInputs": inputs,
                    "evaluations": evaluations,
                    "policy": policy.value,
                    "selectedBranch": selected,
                },
            )

        try:
            rendered_selector = self._expressions.render_value(
                task.configuration.handler_view()["value"],
                context,
            )
        except Exception as exc:
            selected = "default" if policy is ConditionErrorPolicy.FALLBACK else None
            evaluations.append(
                {
                    "kind": "selector",
                    "result": False,
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                }
            )
            selector_error_evidence: dict[str, object] = {
                "kind": "SWITCH",
                "conditionInputs": inputs,
                "policy": policy.value,
                "selector": "[ERROR]",
                "evaluations": evaluations,
                "selectedBranch": selected,
            }
            if policy is ConditionErrorPolicy.FAIL:
                return _BranchDecision(None, selector_error_evidence, error=exc)
            if policy is ConditionErrorPolicy.FALLBACK:
                return _BranchDecision("default", selector_error_evidence)
            rendered_selector = None
        selector_key = _switch_case_key(rendered_selector)
        redacted_selector = _redact_condition_value(
            rendered_selector,
            _sensitive_input_values(flow, execution),
        )
        for case in task.cases:
            if case == "default":
                continue
            matched = selector_key == _switch_case_key(case)
            evaluations.append({"kind": "exact", "branch": f"case:{case}", "result": matched})
            if matched:
                selected = f"case:{case}"
                return _BranchDecision(
                    selected,
                    {
                        "kind": "SWITCH",
                        "conditionInputs": inputs,
                        "selector": redacted_selector,
                        "evaluations": evaluations,
                        "policy": policy.value,
                        "selectedBranch": selected,
                    },
                )
        for branch in task.predicate_cases:
            branch_id = f"predicate:{branch.id}"
            try:
                result = self._expressions.evaluate_condition(branch.condition, context)
            except Exception as exc:
                evaluations.append(
                    {
                        "kind": "predicate",
                        "branch": branch_id,
                        "expression": branch.condition,
                        "result": False,
                        "error": {"type": type(exc).__name__, "message": str(exc)},
                    }
                )
                predicate_error_evidence: dict[str, object] = {
                    "kind": "SWITCH",
                    "conditionInputs": inputs,
                    "selector": redacted_selector,
                    "evaluations": evaluations,
                    "policy": policy.value,
                    "selectedBranch": (
                        "default" if policy is ConditionErrorPolicy.FALLBACK else None
                    ),
                }
                if policy is ConditionErrorPolicy.FAIL:
                    return _BranchDecision(None, predicate_error_evidence, error=exc)
                if policy is ConditionErrorPolicy.FALLBACK:
                    return _BranchDecision("default", predicate_error_evidence)
                continue
            evaluations.append(
                {
                    "kind": "predicate",
                    "branch": branch_id,
                    "expression": branch.condition,
                    "result": result,
                }
            )
            if result:
                return _BranchDecision(
                    branch_id,
                    {
                        "kind": "SWITCH",
                        "conditionInputs": inputs,
                        "selector": redacted_selector,
                        "evaluations": evaluations,
                        "policy": policy.value,
                        "selectedBranch": branch_id,
                    },
                )
        selected = "default" if "default" in task.cases else None
        return _BranchDecision(
            selected,
            {
                "kind": "SWITCH",
                "conditionInputs": inputs,
                "selector": redacted_selector,
                "evaluations": evaluations,
                "policy": policy.value,
                "selectedBranch": selected,
            },
        )

    async def run_to_completion(
        self,
        flow: FlowDefinition,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> ExecutionProgress:
        admission_wait_count = 0
        while True:
            progress = await self.run_ready(
                flow,
                execution_id,
                tenant_id=tenant_id,
            )
            if progress.state is not ExecutionState.RUNNING:
                execution = await self._repository.get_execution(
                    execution_id,
                    tenant_id=tenant_id,
                )
                if execution_lifecycle_pending(
                    flow,
                    execution,
                    list(progress.task_runs),
                ):
                    continue
                if progress.state is ExecutionState.SUCCESS:
                    return progress
                raise ExecutionBlockedError(
                    f"execution {execution_id} stopped in state {progress.state.value}"
                )
            if progress.tasks_run:
                admission_wait_count = 0
            if progress.tasks_run == 0:
                if any(task_run.state is TaskRunState.RUNNING for task_run in progress.task_runs):
                    if await self._has_waiting_deferral(progress.task_runs, tenant_id):
                        return progress
                    # A running task without a durable deferral may belong to another
                    # executor.  There is no local work left to wait for: return to
                    # the role loop so it can keep its heartbeat current and retry
                    # from a fresh persisted snapshot on the next cycle.
                    return progress
                retry_at = min(
                    (
                        task_run.retry_at
                        for task_run in progress.task_runs
                        if task_run.state is TaskRunState.RETRY_DELAY
                        and task_run.retry_at is not None
                    ),
                    default=None,
                )
                if retry_at is not None:
                    database_now = await self._repository.database_time()
                    delay_seconds = max((retry_at - database_now).total_seconds(), 0)
                    await asyncio.sleep(min(delay_seconds, 1))
                    continue
                waiting = [
                    task_run.task_id
                    for task_run in progress.task_runs
                    if task_run.state is TaskRunState.WAITING
                ]
                if any(
                    node.task.concurrency and node.task.id in waiting
                    for node in compile_flow_tasks(flow)
                    if not node.flowable
                ):
                    admission_wait_count += 1
                    await asyncio.sleep(
                        bounded_exponential_backoff(
                            self._admission_poll_initial_seconds,
                            self._admission_poll_max_seconds,
                            admission_wait_count,
                        )
                    )
                    continue
                raise ExecutionBlockedError(
                    f"execution {execution_id} has no runnable tasks; waiting={waiting}"
                )

    async def _run_task(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task_run: PersistedTaskRun,
        task: TaskDefinition,
        outputs: Mapping[str, dict[str, Any]],
        workspace_parent: TaskDefinition | None = None,
        iteration: LoopIterationContext | None = None,
        handler_error: Mapping[str, Any] | None = None,
    ) -> _TaskRunOutcome:
        tenant_id = execution.tenant_id
        execution_id = execution.execution_id
        projected = (
            task_run
            if task_run.state is TaskRunState.RUNNING
            else task_run.model_copy(
                update={
                    "state": TaskRunState.RUNNING,
                    "current_attempt": task_run.current_attempt + 1,
                }
            )
        )
        expression_context = _expression_context(
            flow,
            execution,
            projected,
            task,
            outputs,
            iteration=iteration,
            handler_error=handler_error,
        )
        if task.concurrency and task_run.state is not TaskRunState.RUNNING:
            admission = await self._repository.request_admission(
                AdmissionResourceType.TASK,
                task_run.task_run_id,
                resolve_admission_policies(
                    task.concurrency,
                    resource_type=AdmissionResourceType.TASK,
                    tenant_id=tenant_id,
                    namespace=flow.namespace,
                    flow_id=flow.id,
                    render_key=lambda value: self._expressions.render_value(
                        value,
                        expression_context,
                    ),
                ),
                tenant_id=tenant_id,
                priority=task.priority,
            )
            if admission.outcome is AdmissionOutcome.QUEUED:
                await self._repository.reconcile_admission(tenant_id=tenant_id, limit=100)
                return _TaskRunOutcome(claimed=False)
            if admission.outcome in {
                AdmissionOutcome.CANCELLED,
                AdmissionOutcome.FAILED,
                AdmissionOutcome.SKIPPED,
            }:
                return _TaskRunOutcome(
                    claimed=True,
                    failure=(
                        admission.reason
                        if admission.outcome is not AdmissionOutcome.SKIPPED
                        else None
                    ),
                )
        cache_key: TaskCacheKey | None = None
        cache_lookup: TaskCacheLookup | None = None
        condition = (
            _ConditionDecision(matched=True, evidence=task_run.evidence)
            if task_run.state is TaskRunState.RUNNING
            else self._evaluate_task_condition(
                flow,
                execution,
                task,
                expression_context,
                handler_error,
            )
        )
        if not condition.matched and condition.error is None:
            try:
                await self._repository.skip_task(
                    task_run.task_run_id,
                    {"skipped": True},
                    tenant_id=tenant_id,
                    evidence=condition.evidence,
                )
            except TaskStateConflictError:
                return _TaskRunOutcome(claimed=False)
            return _TaskRunOutcome(claimed=True)
        if condition.error is None and self._dispatch_policy_enforcer is not None:
            try:
                policy_decision = await self._dispatch_policy_enforcer(
                    flow,
                    execution,
                    task_run,
                    task,
                )
            except AdmissionPolicyDenied as exc:
                policy_evidence = _merge_task_control(
                    condition.evidence,
                    "policy",
                    policy_decision_metadata(exc.decision),
                )
                try:
                    denied_run = (
                        task_run
                        if task_run.state is TaskRunState.RUNNING
                        else await self._repository.start_task(
                            task_run.task_run_id,
                            tenant_id=tenant_id,
                            dispatch=False,
                        )
                    )
                    await self._repository.fail_task(
                        denied_run.task_run_id,
                        denied_run.current_attempt,
                        str(exc),
                        tenant_id=tenant_id,
                        failure_category=FailureCategory.CONFIGURATION,
                        evidence=policy_evidence,
                    )
                except TaskStateConflictError:
                    return _TaskRunOutcome(claimed=False)
                return _TaskRunOutcome(claimed=True, failure=str(exc))
            condition = _ConditionDecision(
                matched=condition.matched,
                evidence=_merge_task_control(
                    condition.evidence,
                    "policy",
                    policy_decision_metadata(policy_decision),
                ),
            )
        try:
            running = (
                task_run
                if task_run.state is TaskRunState.RUNNING
                else await self._repository.start_task(
                    task_run.task_run_id,
                    tenant_id=tenant_id,
                    dispatch=condition.matched,
                    priority=task.priority,
                    worker_group=task.worker_group,
                )
            )
        except TaskStateConflictError:
            return _TaskRunOutcome(claimed=False)
        if condition.error is not None:
            reason = f"task {task.id!r} runIf failed: {condition.error}"
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
                failure_category=FailureCategory.CONFIGURATION,
                evidence=condition.evidence,
            )
            return _TaskRunOutcome(claimed=True, failure=reason)
        handler = self._handlers.get(task.type)
        if handler is None and task.type not in LOOP_TASK_TYPES:
            reason = f"no in-process handler registered for task type {task.type!r}"
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
                evidence=condition.evidence,
            )
            return _TaskRunOutcome(claimed=True, failure=reason)
        secret_values: tuple[str, ...] = ()
        try:
            resources = await self._resolve_context_resources(
                task,
                execution,
                running,
                declared_files={},
                strict_files=False,
            )
            secret_values = tuple(resources.secrets.values())
            runtime_expression_context = replace(
                expression_context,
                secrets=resources.secrets,
                key_values=resources.key_values,
            )
            rendered_task = _render_task_for_execution(
                self._expressions,
                task,
                runtime_expression_context,
            )
            declared_files = _combine_declared_files(
                (
                    _render_declared_files(
                        self._expressions,
                        _combine_declared_files(
                            workspace_parent.contract.files,
                            workspace_parent.input_files,
                        ),
                        runtime_expression_context,
                    )
                    if workspace_parent is not None
                    else {}
                ),
                _render_declared_files(
                    self._expressions,
                    _combine_declared_files(
                        rendered_task.contract.files,
                        rendered_task.input_files,
                    ),
                    runtime_expression_context,
                ),
            )
            file_resources = await self._resolve_context_resources(
                rendered_task.model_copy(
                    update={"contract": rendered_task.contract.model_copy(update={"files": {}})}
                ),
                execution,
                running,
                declared_files=declared_files,
                resolve_values=False,
            )
            context = TaskExecutionContext(
                tenant_id=tenant_id,
                execution_id=execution_id,
                task_run_id=running.task_run_id,
                attempt=running.current_attempt,
                attempt_id=uuid5(running.task_run_id, f"attempt:{running.current_attempt}"),
                inputs=execution.inputs,
                outputs=outputs,
                task_types={node.task.id: node.task.type for node in compile_flow_tasks(flow)},
                variables=flow.variables,
                namespace=execution.namespace,
                labels=execution.labels,
                trigger=_user_trigger_context(execution),
                iteration=iteration,
                secret_scopes=rendered_task.contract.secret_scopes,
                secrets=resources.secrets,
                files=file_resources.files,
                file_references=file_resources.file_references,
                key_values=resources.key_values,
                workspace_scope_id=(workspace_parent.id if workspace_parent is not None else None),
                workspace_quota_bytes=(
                    min(
                        rendered_task.workspace_quota_bytes,
                        workspace_parent.workspace_quota_bytes,
                    )
                    if workspace_parent is not None
                    else rendered_task.workspace_quota_bytes
                ),
                cancellation=TaskCancellationChannel(
                    self._repository,
                    tenant_id=tenant_id,
                    execution_id=execution_id,
                ),
            )

            if rendered_task.task_cache.enabled and self._task_cache is None:
                raise TaskPlatformError("task cache repository is unavailable")
            if rendered_task.task_cache.enabled and self._task_cache is not None:
                cache_key = derive_task_cache_key(
                    flow,
                    execution,
                    rendered_task,
                    context,
                )
                cache_mode = _execution_cache_mode(execution)
                if cache_mode is TaskCacheMode.BYPASS:
                    reason = "execution requested cache bypass; task handler ran normally"
                    await self._task_cache.record_bypass(
                        cache_key,
                        tenant_id=tenant_id,
                        execution_id=execution_id,
                        task_run_id=running.task_run_id,
                        attempt=running.current_attempt,
                        reason=reason,
                    )
                    cache_lookup = TaskCacheLookup(
                        decision=TaskCacheDecision.BYPASS,
                        reason=reason,
                        key_hash=cache_key.key_hash,
                    )
                else:
                    cache_lookup = await self._task_cache.lookup_or_reserve(
                        cache_key,
                        tenant_id=tenant_id,
                        execution_id=execution_id,
                        task_run_id=running.task_run_id,
                        attempt=running.current_attempt,
                        mode=cache_mode,
                    )
                    if cache_lookup.decision is TaskCacheDecision.HIT:
                        await self._repository.complete_task(
                            running.task_run_id,
                            running.current_attempt,
                            cache_lookup.output or {},
                            tenant_id=tenant_id,
                            evidence=_with_cache_evidence(
                                _merge_completion_evidence(
                                    cache_lookup.evidence or {},
                                    condition.evidence,
                                ),
                                cache_lookup,
                            ),
                        )
                        return _TaskRunOutcome(claimed=True)

            async def invoke() -> TaskHandlerResult:
                if rendered_task.type in LOOP_TASK_TYPES:
                    return await self._run_loop(
                        flow,
                        execution,
                        running,
                        rendered_task,
                        outputs,
                    )
                if handler is None:
                    raise TaskConfigurationError(
                        f"no in-process handler registered for task type {task.type!r}"
                    )
                return await handler(rendered_task, context)

            if task.timeout_seconds is None:
                result = await invoke()
            else:
                async with asyncio.timeout(task.timeout_seconds):
                    result = await invoke()
            if isinstance(result, TaskDeferral):
                if cache_key is not None and cache_lookup is not None:
                    await _abandon_cache_population(
                        self._task_cache,
                        cache_key,
                        cache_lookup,
                        tenant_id=tenant_id,
                        execution_id=execution_id,
                        task_run_id=running.task_run_id,
                        attempt=running.current_attempt,
                        reason="deferred task results cannot populate the cache",
                    )
                await self._repository.defer_task(
                    running.task_run_id,
                    running.current_attempt,
                    result.resume_token,
                    tenant_id=tenant_id,
                    metadata=result.metadata,
                    expires_at=result.expires_at,
                )
                return _TaskRunOutcome(claimed=True)
            output, evidence = normalize_task_completion(
                result,
                rendered_task.contract.resource_limits,
                secret_values=context.secrets.values(),
            )
            await self._repository.complete_task(
                running.task_run_id,
                running.current_attempt,
                output,
                tenant_id=tenant_id,
                evidence=_merge_completion_evidence(
                    (
                        _with_cache_evidence(evidence, cache_lookup)
                        if cache_lookup is not None
                        else evidence
                    ),
                    condition.evidence,
                ),
            )
            if (
                self._task_cache is not None
                and cache_key is not None
                and cache_lookup is not None
                and cache_lookup.owner_token is not None
            ):
                try:
                    await self._task_cache.publish(
                        cache_key.key_hash,
                        cache_lookup.owner_token,
                        output,
                        evidence,
                        tenant_id=tenant_id,
                        execution_id=execution_id,
                        task_run_id=running.task_run_id,
                        attempt=running.current_attempt,
                    )
                except Exception:
                    LOGGER.exception(
                        "task result cache publication failed; execution result remains committed",
                        extra={
                            "tenant_id": tenant_id,
                            "execution_id": str(execution_id),
                            "task_run_id": str(running.task_run_id),
                            "cache_key_hash": cache_key.key_hash,
                        },
                    )
                    try:
                        await _abandon_cache_population(
                            self._task_cache,
                            cache_key,
                            cache_lookup,
                            tenant_id=tenant_id,
                            execution_id=execution_id,
                            task_run_id=running.task_run_id,
                            attempt=running.current_attempt,
                            reason="cache publication failed after task completion",
                        )
                    except Exception:
                        LOGGER.warning(
                            "cache abandonment failed after authoritative task completion; "
                            "preserving the committed task result",
                            extra={
                                "tenant_id": tenant_id,
                                "execution_id": str(execution_id),
                                "task_run_id": str(running.task_run_id),
                                "cache_key_hash": cache_key.key_hash,
                            },
                        )
            return _TaskRunOutcome(claimed=True)
        except TaskExecutionPaused:
            return _TaskRunOutcome(claimed=True)
        except Exception as exc:
            cache_abandonment_failure: Exception | None = None
            if cache_key is not None and cache_lookup is not None:
                try:
                    await _abandon_cache_population(
                        self._task_cache,
                        cache_key,
                        cache_lookup,
                        tenant_id=tenant_id,
                        execution_id=execution_id,
                        task_run_id=running.task_run_id,
                        attempt=running.current_attempt,
                        reason=(
                            f"cache population abandoned after task failure: {type(exc).__name__}"
                        ),
                    )
                except Exception as abandonment_exc:
                    cache_abandonment_failure = abandonment_exc
            category = classify_task_failure(exc)
            safe_message = redact_runner_payload(str(exc), secret_values)
            reason = f"task {task.id!r} failed [{category.value}]: {safe_message}"
            task_evidence = _merge_completion_evidence(
                (
                    exc.evidence
                    if isinstance(exc, TaskExecutionFailure) and exc.evidence is not None
                    else {}
                ),
                condition.evidence,
            )
            redacted_evidence = redact_runner_payload(task_evidence, secret_values)
            task_evidence = cast(dict[str, object], redacted_evidence)
            if cache_abandonment_failure is not None:
                abandonment_message = redact_runner_payload(
                    str(cache_abandonment_failure), secret_values
                )
                reason = (
                    f"{reason}; cache abandonment failed "
                    f"[{type(cache_abandonment_failure).__name__}]: {abandonment_message}"
                )
                task_evidence = _merge_task_control(
                    task_evidence,
                    "cacheAbandonment",
                    {
                        "state": "FAILED",
                        "errorType": type(cache_abandonment_failure).__name__,
                        "error": abandonment_message,
                    },
                )
            if category is FailureCategory.CANCELLED:
                await self._repository.cancel_task(
                    running.task_run_id,
                    running.current_attempt,
                    reason,
                    tenant_id=tenant_id,
                )
                return _TaskRunOutcome(claimed=True, failure=reason)
            retry_eligible = (
                category
                in {
                    FailureCategory.RETRYABLE,
                    FailureCategory.TIMED_OUT,
                    FailureCategory.INFRASTRUCTURE,
                }
                and running.current_attempt < task.retry.max_attempts
            )
            if retry_eligible and task.retry.condition is not None:
                retry_context = _expression_context(
                    flow,
                    execution,
                    running,
                    task,
                    outputs,
                    iteration=iteration,
                    failure_category=category,
                    error=reason,
                )
                retry_record: dict[str, object] = {
                    "kind": "retry",
                    "expression": task.retry.condition,
                    "conditionInputs": _redacted_condition_inputs(
                        flow,
                        execution,
                        retry_context,
                    ),
                    "policy": task.retry.condition_error_policy.value,
                }
                try:
                    retry_eligible = self._expressions.evaluate_condition(
                        task.retry.condition,
                        retry_context,
                    )
                    retry_record["result"] = retry_eligible
                except Exception as retry_exc:
                    retry_eligible = False
                    retry_record.update(
                        {
                            "result": False,
                            "error": {
                                "type": type(retry_exc).__name__,
                                "message": redact_runner_payload(str(retry_exc), secret_values),
                            },
                        }
                    )
                    if task.retry.condition_error_policy is ConditionErrorPolicy.FAIL:
                        category = FailureCategory.CONFIGURATION
                        reason = f"{reason}; retry condition failed: {retry_exc}"
                task_evidence = _merge_task_control(
                    task_evidence,
                    "retry",
                    retry_record,
                )
                running = await self._repository.record_task_control(
                    running.task_run_id,
                    running.current_attempt,
                    task_evidence,
                    tenant_id=tenant_id,
                )
            if retry_eligible:
                database_now = await self._repository.database_time()
                retry_at = database_now + timedelta(
                    seconds=retry_delay_seconds(
                        task.retry,
                        running.task_run_id,
                        running.current_attempt,
                    )
                )
                await self._repository.retry_task(
                    running.task_run_id,
                    running.current_attempt,
                    retry_at=retry_at,
                    reason=reason,
                    tenant_id=tenant_id,
                    failure_category=category,
                )
                return _TaskRunOutcome(claimed=True)
            failure_result: dict[str, object] | None = (
                cast(dict[str, object], redact_runner_payload(exc.result, secret_values))
                if isinstance(exc, (LoopExecutionFailure, TaskExecutionFailure))
                and exc.result is not None
                else None
            )
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
                result=failure_result,
                failure_category=category,
                evidence=task_evidence,
            )
            return _TaskRunOutcome(claimed=True, failure=reason)

    async def _has_waiting_deferral(
        self,
        task_runs: tuple[PersistedTaskRun, ...],
        tenant_id: str,
    ) -> bool:
        for task_run in task_runs:
            if task_run.state is not TaskRunState.RUNNING:
                continue
            deferral = await self._repository.get_task_deferral(
                task_run.task_run_id,
                tenant_id=tenant_id,
            )
            if deferral is not None and deferral.state == "WAITING":
                return True
        return False

    async def _run_loop(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        parent_run: PersistedTaskRun,
        task: TaskDefinition,
        upstream_outputs: Mapping[str, dict[str, Any]],
    ) -> dict[str, Any]:
        spec = parse_loop_spec(task)
        started_at = await self._repository.task_attempt_started_at(
            parent_run.task_run_id,
            parent_run.current_attempt,
            tenant_id=execution.tenant_id,
        )
        results: list[dict[str, Any]] = []
        collected_failure = False

        async def require_capacity(next_count: int) -> None:
            if next_count > spec.max_iterations:
                raise TaskResourceLimitError(
                    f"loop {task.id!r} exceeded maxIterations={spec.max_iterations}"
                )
            if next_count * len(task.tasks) > spec.max_task_runs:
                raise TaskResourceLimitError(
                    f"loop {task.id!r} exceeded maxTaskRuns={spec.max_task_runs}"
                )
            database_now = await self._repository.database_time()
            if (database_now - started_at).total_seconds() > spec.max_duration_seconds:
                raise TaskResourceLimitError(
                    f"loop {task.id!r} exceeded maxDurationSeconds={spec.max_duration_seconds}"
                )

        async def run_item(item: LoopItem) -> tuple[dict[str, Any], bool, bool]:
            iteration = LoopIterationContext(
                index=item.index,
                key=item.key,
                value=item.value,
                parent={
                    "taskId": task.id,
                    "taskRunId": str(parent_run.task_run_id),
                    "attempt": parent_run.current_attempt,
                },
            )
            if spec.continue_if is not None and self._evaluate_loop_condition(
                spec.continue_if,
                flow,
                execution,
                parent_run,
                task,
                upstream_outputs,
                iteration,
            ):
                return (
                    {
                        "index": item.index,
                        "key": item.key,
                        "state": "CONTINUED",
                        "children": {},
                    },
                    False,
                    False,
                )
            aggregate, child_outputs = await self._run_loop_iteration(
                flow,
                execution,
                task,
                iteration,
                upstream_outputs,
            )
            failed = aggregate["state"] == "FAILED"
            should_break = spec.break_if is not None and self._evaluate_loop_condition(
                spec.break_if,
                flow,
                execution,
                parent_run,
                task,
                {**upstream_outputs, **child_outputs},
                iteration,
            )
            if should_break:
                aggregate["control"] = "BREAK"
            return aggregate, failed, should_break

        if task.type == "core.foreach":
            concurrency = task.max_concurrency or 1
            wave: list[LoopItem] = []
            stop = False
            async for item in iter_foreach_items(
                spec,
                tenant_id=execution.tenant_id,
                object_store=self._object_store,
            ):
                await require_capacity(item.index + 1)
                wave.append(item)
                if len(wave) < concurrency:
                    continue
                outcomes = await asyncio.gather(*(run_item(candidate) for candidate in wave))
                for aggregate, failed, should_break in outcomes:
                    results.append(aggregate)
                    collected_failure = collected_failure or failed
                    stop = (
                        stop
                        or should_break
                        or (failed and task.failure_policy is FlowableFailurePolicy.FAIL_FAST)
                    )
                wave = []
                if stop:
                    break
            if wave and not stop:
                outcomes = await asyncio.gather(*(run_item(candidate) for candidate in wave))
                for aggregate, failed, should_break in outcomes:
                    results.append(aggregate)
                    collected_failure = collected_failure or failed
                    stop = (
                        stop
                        or should_break
                        or (failed and task.failure_policy is FlowableFailurePolicy.FAIL_FAST)
                    )
        else:
            previous_outputs: dict[str, dict[str, Any]] = {}
            terminated = False
            for index in range(spec.max_iterations):
                await require_capacity(index + 1)
                iteration = LoopIterationContext(
                    index=index,
                    key=str(index),
                    value=previous_outputs or None,
                    parent={
                        "taskId": task.id,
                        "taskRunId": str(parent_run.task_run_id),
                        "attempt": parent_run.current_attempt,
                    },
                )
                if task.type == "core.while" and not self._evaluate_loop_condition(
                    spec.condition or "",
                    flow,
                    execution,
                    parent_run,
                    task,
                    {**upstream_outputs, **previous_outputs},
                    iteration,
                ):
                    terminated = True
                    break
                aggregate, failed, should_break = await run_item(
                    LoopItem(index=index, key=str(index), value=previous_outputs or None)
                )
                results.append(aggregate)
                collected_failure = collected_failure or failed
                previous_outputs = {
                    child_id: child["output"]
                    for child_id, child in aggregate["children"].items()
                    if child["state"] == TaskRunState.SUCCESS.value
                    and isinstance(child["output"], dict)
                }
                if should_break or (
                    failed and task.failure_policy is FlowableFailurePolicy.FAIL_FAST
                ):
                    terminated = True
                    break
                if task.type == "core.until" and self._evaluate_loop_condition(
                    spec.condition or "",
                    flow,
                    execution,
                    parent_run,
                    task,
                    {**upstream_outputs, **previous_outputs},
                    iteration,
                ):
                    terminated = True
                    break
            if not terminated:
                raise TaskResourceLimitError(
                    f"loop {task.id!r} reached maxIterations={spec.max_iterations} "
                    "before its condition terminated"
                )

        result = await self._finalize_loop_result(execution, parent_run, task, spec, results)
        if collected_failure and task.failure_policy in {
            FlowableFailurePolicy.FAIL_FAST,
            FlowableFailurePolicy.COLLECT_ALL,
        }:
            reason = f"loop {task.id!r} collected failed iterations"
            raise LoopExecutionFailure(reason, {**result, "error": reason})
        return result

    async def _run_loop_iteration(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        loop_task: TaskDefinition,
        iteration: LoopIterationContext,
        upstream_outputs: Mapping[str, dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        iteration_key = f"{loop_task.id}:{iteration.index:08d}"
        task_ids = tuple(task.id for task in loop_task.tasks)
        task_runs = await self._repository.ensure_iteration_task_runs(
            execution.execution_id,
            iteration_key,
            task_ids,
            tenant_id=execution.tenant_id,
        )
        tasks_by_id = {task.id: task for task in loop_task.tasks}
        admission_wait_count = 0

        while True:
            runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
            outputs = {
                task_id: task_run.result or {}
                for task_id, task_run in runs_by_id.items()
                if task_run.state is TaskRunState.SUCCESS
            }
            pending = [
                task for task in loop_task.tasks if not _task_run_is_terminal(runs_by_id[task.id])
            ]
            if not pending:
                break
            now = await self._repository.database_time()
            ready: list[TaskDefinition] = []
            for task in pending:
                task_run = runs_by_id[task.id]
                if task_run.state is TaskRunState.RUNNING:
                    deferral = await self._repository.get_task_deferral(
                        task_run.task_run_id,
                        tenant_id=execution.tenant_id,
                    )
                    if deferral is not None and deferral.state == "WAITING":
                        continue
                elif not _is_ready(task_run, now):
                    continue
                if all(
                    runs_by_id[dependency].state is TaskRunState.SUCCESS
                    for dependency in task.depends_on
                ):
                    ready.append(task)
            if not ready:
                if any(
                    task_run.state in {TaskRunState.RUNNING, TaskRunState.RETRY_DELAY}
                    for task_run in runs_by_id.values()
                ):
                    admission_wait_count += 1
                    await asyncio.sleep(
                        bounded_exponential_backoff(
                            self._admission_poll_initial_seconds,
                            self._admission_poll_max_seconds,
                            admission_wait_count,
                        )
                    )
                    task_runs = await self._repository.ensure_iteration_task_runs(
                        execution.execution_id,
                        iteration_key,
                        task_ids,
                        tenant_id=execution.tenant_id,
                    )
                    continue
                break
            admission_wait_count = 0
            await asyncio.gather(
                *(
                    self._run_task(
                        flow,
                        execution,
                        runs_by_id[task.id],
                        task,
                        {
                            **upstream_outputs,
                            **{
                                task_id: output
                                for task_id, output in outputs.items()
                                if task_id in _template_visible_output_ids(task.id, tasks_by_id)
                            },
                        },
                        iteration=iteration,
                    )
                    for task in ready
                )
            )
            task_runs = await self._repository.ensure_iteration_task_runs(
                execution.execution_id,
                iteration_key,
                task_ids,
                tenant_id=execution.tenant_id,
            )

        runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
        outputs = {
            task_id: task_run.result or {}
            for task_id, task_run in runs_by_id.items()
            if task_run.state is TaskRunState.SUCCESS
        }
        failed = any(
            task_run.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
            for task_run in runs_by_id.values()
        )
        aggregate = {
            "index": iteration.index,
            "key": iteration.key,
            "state": "FAILED" if failed else "SUCCESS",
            "childOrder": list(task_ids),
            "children": {
                task_id: {
                    "state": runs_by_id[task_id].state.value,
                    "output": (
                        runs_by_id[task_id].result
                        if runs_by_id[task_id].state is TaskRunState.SUCCESS
                        else None
                    ),
                    "error": (
                        (runs_by_id[task_id].result or {}).get("error")
                        if runs_by_id[task_id].state
                        in {TaskRunState.FAILED, TaskRunState.CANCELLED}
                        else None
                    ),
                }
                for task_id in task_ids
            },
        }
        return aggregate, outputs

    def _evaluate_loop_condition(
        self,
        expression: str,
        flow: FlowDefinition,
        execution: PersistedExecution,
        parent_run: PersistedTaskRun,
        task: TaskDefinition,
        outputs: Mapping[str, dict[str, Any]],
        iteration: LoopIterationContext,
    ) -> bool:
        return self._expressions.evaluate_condition(
            expression,
            _expression_context(
                flow,
                execution,
                parent_run,
                task,
                outputs,
                iteration=iteration,
            ),
        )

    async def _finalize_loop_result(
        self,
        execution: PersistedExecution,
        parent_run: PersistedTaskRun,
        task: TaskDefinition,
        spec: LoopSpec,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        aggregate = {
            "mode": task.type.removeprefix("core.").upper(),
            "failurePolicy": task.failure_policy.value,
            "iterationCount": len(results),
            "iterations": sorted(results, key=lambda result: int(result["index"])),
        }
        encoded = json.dumps(aggregate, separators=(",", ":"), ensure_ascii=False).encode()
        if len(encoded) <= spec.inline_payload_bytes:
            return aggregate
        if self._object_store is None:
            raise TaskConfigurationError(
                f"loop {task.id!r} produced {len(encoded)} bytes and requires an object store"
            )

        async def chunks() -> Any:
            yield encoded

        metadata = await self._object_store.put(
            execution.tenant_id,
            (
                f"loops/{execution.execution_id}/{parent_run.task_run_id}/"
                f"attempt-{parent_run.current_attempt}.json"
            ),
            chunks(),
            content_type="application/json",
        )
        return {
            "mode": aggregate["mode"],
            "failurePolicy": aggregate["failurePolicy"],
            "iterationCount": len(results),
            "manifestUri": metadata.uri,
            "sizeBytes": metadata.size,
            "checksumSha256": metadata.checksum_sha256,
        }

    async def _resolve_context_resources(
        self,
        task: TaskDefinition,
        execution: PersistedExecution,
        task_run: PersistedTaskRun,
        *,
        declared_files: Mapping[str, str] | None = None,
        resolve_values: bool = True,
        strict_files: bool = True,
    ) -> TaskContextResources:
        contract = task.contract
        selected_files = contract.files if declared_files is None else declared_files
        if self._context_provider is None:
            if resolve_values and contract.secret_scopes:
                raise TaskConfigurationError(
                    f"task {task.id!r} declares secret scopes but no context provider is configured"
                )
            return TaskContextResources(files=dict(selected_files))
        try:
            resources = await self._context_provider.resolve(
                TaskContextRequest(
                    tenantId=execution.tenant_id,
                    namespace=execution.namespace,
                    executionId=str(execution.execution_id),
                    taskRunId=str(task_run.task_run_id),
                    attempt=task_run.current_attempt,
                    taskType=task.type,
                    secretScopes=(contract.secret_scopes if resolve_values else ()),
                    declaredFiles=dict(selected_files),
                    keyValuesRequired=(
                        _contains_kv_expression(task.model_dump(mode="json"))
                        if resolve_values
                        else False
                    ),
                )
            )
        except TaskExecutionFailure:
            raise
        except Exception as exc:
            raise TaskPlatformError(f"task context provider failed: {exc}") from exc
        unexpected_files = (
            sorted(set(resources.files) - set(selected_files)) if strict_files else []
        )
        if unexpected_files:
            raise TaskConfigurationError(
                "context provider returned undeclared files: " + ", ".join(unexpected_files)
            )
        unexpected_references = (
            sorted(set(resources.file_references) - set(selected_files)) if strict_files else []
        )
        if unexpected_references:
            raise TaskConfigurationError(
                "context provider returned undeclared file metadata: "
                + ", ".join(unexpected_references)
            )
        return resources

    async def _finish_execution(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        decision: OrchestrationDecision,
        task_runs: list[PersistedTaskRun],
    ) -> PersistedExecution:
        if decision.terminal_state is ExecutionState.SUCCESS:
            task_outputs = {
                task_run.task_id: task_run.result or {}
                for task_run in task_runs
                if task_run.state is TaskRunState.SUCCESS
            }
            context = ExpressionContext(
                flow={
                    "id": flow.id,
                    "namespace": flow.namespace,
                    "revision": flow.revision,
                },
                execution={
                    "id": str(execution.execution_id),
                    "state": ExecutionState.SUCCESS.value,
                    "startDate": execution.created_at,
                    "tenantId": execution.tenant_id,
                },
                trigger=_user_trigger_context(execution),
                inputs=execution.inputs,
                outputs=task_outputs,
                variables=flow.variables,
                labels=execution.labels,
                namespace={"id": flow.namespace},
            )
            try:
                outputs = render_flow_outputs(flow, self._expressions, context)
            except (TypeError, ValueError) as exc:
                return await self._repository.fail_execution(
                    execution.execution_id,
                    f"flow output contract failed: {exc}",
                    expected_epoch=execution.epoch,
                    tenant_id=execution.tenant_id,
                )
            return await self._repository.complete_execution(
                execution.execution_id,
                expected_epoch=execution.epoch,
                tenant_id=execution.tenant_id,
                outputs=outputs,
            )
        if decision.terminal_state is ExecutionState.FAILED:
            return await self._repository.fail_execution(
                execution.execution_id,
                decision.diagnostic or "execution graph is unsatisfiable",
                expected_epoch=execution.epoch,
                tenant_id=execution.tenant_id,
            )
        raise ValueError("orchestration decision is not terminal")


def _lifecycle_plan(plan: tuple[PlannedTask, ...]) -> tuple[PlannedTask, ...]:
    return tuple(node for node in plan if node.lifecycle_phase is not LifecyclePhase.MAIN)


def _phase_plan(
    plan: tuple[PlannedTask, ...],
    phase: LifecyclePhase,
) -> tuple[PlannedTask, ...]:
    return tuple(node for node in plan if node.lifecycle_phase is phase)


def _main_task_runs(task_runs: list[PersistedTaskRun]) -> list[PersistedTaskRun]:
    return [
        task_run
        for task_run in task_runs
        if task_run.lifecycle_phase.value == LifecyclePhase.MAIN.value
    ]


def _phase_was_completed(
    phases: Mapping[str, Any],
    phase: LifecyclePhase,
) -> bool:
    record = phases.get(phase.value)
    return isinstance(record, Mapping) and record.get("status") == "COMPLETED"


def _phase_is_complete(
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
) -> bool:
    runs = {task_run.task_id: task_run for task_run in task_runs}
    return all(node.task.id in runs and _task_run_is_terminal(runs[node.task.id]) for node in plan)


def _completed_phase_evidence(
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
) -> dict[str, object]:
    runs = {task_run.task_id: task_run for task_run in task_runs}
    failures = [
        {
            "taskId": node.task.id,
            "handlerOwnerId": node.handler_owner_id,
            "state": runs[node.task.id].state.value,
            "category": _failure_category_value(runs[node.task.id]),
            "error": (runs[node.task.id].result or {}).get("error"),
        }
        for node in plan
        if node.task.id in runs
        and runs[node.task.id].state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
    ]
    return {"status": "COMPLETED", "failures": failures}


def _main_error_items(
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
) -> list[dict[str, object]]:
    runs = {task_run.task_id: task_run for task_run in task_runs}
    return [
        {
            "taskId": node.task.id,
            "state": runs[node.task.id].state.value,
            "category": _failure_category_value(runs[node.task.id]),
            "error": (runs[node.task.id].result or {}).get("error"),
        }
        for node in plan
        if node.lifecycle_phase is LifecyclePhase.MAIN
        and node.task.id in runs
        and runs[node.task.id].state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
    ]


def _primary_error_message(errors: list[dict[str, object]]) -> str | None:
    for error in errors:
        message = error.get("error")
        if message:
            return str(message)
    return None


def _failure_category_value(task_run: PersistedTaskRun) -> str | None:
    if task_run.failure_category is not None:
        return task_run.failure_category.value
    if task_run.state is TaskRunState.CANCELLED:
        return FailureCategory.CANCELLED.value
    return None


def _handler_error_contexts(
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    primary_state: ExecutionState,
) -> dict[str, Mapping[str, Any]]:
    main_plan = tuple(node for node in plan if node.lifecycle_phase is LifecyclePhase.MAIN)
    by_id = {node.task.id: node for node in main_plan}
    errors = _main_error_items(plan, task_runs)
    contexts: dict[str, Mapping[str, Any]] = {}
    for node in plan:
        if node.lifecycle_phase not in {LifecyclePhase.ERROR, LifecyclePhase.AFTER_EXECUTION}:
            continue
        owner_id = node.handler_owner_id or "flow"
        owner = by_id.get(owner_id)
        scoped = errors
        if owner is not None:
            scoped = [
                error
                for error in errors
                if error.get("taskId") == owner_id
                or (
                    isinstance(error.get("taskId"), str)
                    and error["taskId"] in by_id
                    and _descends_from(by_id[str(error["taskId"])], owner, by_id)
                )
            ]
        first = next(
            (
                error
                for error in scoped
                if isinstance(error.get("taskId"), str)
                and error["taskId"] in by_id
                and not by_id[str(error["taskId"])].flowable
            ),
            scoped[0] if scoped else {},
        )
        contexts[node.task.id] = {
            "state": primary_state.value,
            "taskId": first.get("taskId"),
            "category": first.get("category"),
            "message": first.get("error"),
            "items": scoped,
            "handlerOwnerId": owner_id,
        }
    return contexts


def _error_handler_is_applicable(
    node: PlannedTask,
    primary_state: ExecutionState,
    context: Mapping[str, Any] | None,
) -> bool:
    items = (context or {}).get("items")
    if not isinstance(items, list) or not items:
        return False
    if primary_state is not ExecutionState.CANCELLED:
        return True
    selector = node.task.error_selector
    if selector is None:
        return False
    return not selector.states or "CANCELLED" in selector.states


def _reduce_lifecycle_phase(
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    *,
    now: datetime,
) -> OrchestrationDecision:
    if not plan:
        return OrchestrationDecision(terminal_state=ExecutionState.SUCCESS)
    by_id = {task_run.task_id: task_run for task_run in task_runs}
    top_level = [node for node in plan if node.parent_id is None]
    if all(
        node.task.id in by_id and _task_run_is_terminal(by_id[node.task.id]) for node in top_level
    ):
        return OrchestrationDecision(terminal_state=ExecutionState.SUCCESS)
    plan_by_id = {node.task.id: node for node in plan}
    runnable = tuple(
        node.task.id
        for node in plan
        if (not node.flowable or node.dynamic)
        and node.task.id in by_id
        and _is_ready(by_id[node.task.id], now)
        and _parent_is_running(node, by_id)
        and _dependencies_satisfied(node, plan_by_id, by_id)
    )
    if runnable:
        return OrchestrationDecision(runnable_task_ids=runnable)
    retry_values = [
        by_id[node.task.id].retry_at
        for node in plan
        if node.task.id in by_id and by_id[node.task.id].state is TaskRunState.RETRY_DELAY
    ]
    retry_at = min((value for value in retry_values if value is not None), default=None)
    return OrchestrationDecision(retry_at=retry_at)


def execution_lifecycle_pending(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_runs: list[PersistedTaskRun],
) -> bool:
    del task_runs
    if not _lifecycle_plan(compile_execution_tasks(flow)):
        return False
    return execution.lifecycle_evidence.get("status") != "COMPLETE"


def reduce_orchestration(
    flow: FlowDefinition,
    task_runs: list[PersistedTaskRun],
    *,
    now: datetime,
) -> OrchestrationDecision:
    """Reduce committed task state to one deterministic orchestration decision."""

    plan = compile_flow_tasks(flow)
    task_runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
    _require_matching_plan(flow, task_runs_by_id)
    failed = [
        node.task.id
        for node in plan
        if node.parent_id is None
        and task_runs_by_id[node.task.id].state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
    ]
    if failed:
        blocked = [
            node.task.id
            for node in plan
            if node.parent_id is None
            and task_runs_by_id[node.task.id].state is TaskRunState.WAITING
            and any(dependency in failed for dependency in node.dependencies)
        ]
        return OrchestrationDecision(
            terminal_state=ExecutionState.FAILED,
            diagnostic=(f"unsatisfiable execution graph; failed={failed}; blocked={blocked}"),
        )
    top_level = [node for node in plan if node.parent_id is None]
    if top_level and all(
        task_runs_by_id[node.task.id].state is TaskRunState.SUCCESS for node in top_level
    ):
        return OrchestrationDecision(terminal_state=ExecutionState.SUCCESS)

    plan_by_id = {node.task.id: node for node in plan}
    runnable = tuple(
        node.task.id
        for node in plan
        if (not node.flowable or node.dynamic)
        and _is_ready(task_runs_by_id[node.task.id], now)
        and _parent_is_running(node, task_runs_by_id)
        and _dependencies_satisfied(node, plan_by_id, task_runs_by_id)
    )
    if runnable:
        return OrchestrationDecision(runnable_task_ids=runnable)

    retry_at = min(
        (
            task_run.retry_at
            for task_run in task_runs
            if task_run.state is TaskRunState.RETRY_DELAY and task_run.retry_at is not None
        ),
        default=None,
    )
    if retry_at is not None or any(
        task_run.state is TaskRunState.RUNNING for task_run in task_runs
    ):
        return OrchestrationDecision(retry_at=retry_at)

    blocked = [
        f"{node.task.id}<-{','.join(node.dependencies) or 'condition'}"
        for node in plan
        if task_runs_by_id[node.task.id].state is not TaskRunState.SUCCESS
    ]
    return OrchestrationDecision(
        terminal_state=ExecutionState.FAILED,
        diagnostic=f"unsatisfiable execution graph; blocked={blocked}",
    )


def _select_ready_tasks(
    plan: tuple[PlannedTask, ...],
    task_runs_by_id: Mapping[str, PersistedTaskRun],
    runnable_ids: set[str],
    recover_running_types: frozenset[str],
    deferred_task_run_ids: set[UUID],
    *,
    max_tasks: int | None,
) -> list[PlannedTask]:
    plan_by_id = {node.task.id: node for node in plan}
    limited_counts: dict[str, int] = {}
    for node in plan:
        task_run = task_runs_by_id[node.task.id]
        if (node.flowable and not node.dynamic) or task_run.state is not TaskRunState.RUNNING:
            continue
        for ancestor in _flowable_ancestors(node, plan_by_id):
            if ancestor.max_concurrency is not None:
                limited_counts[ancestor.task.id] = limited_counts.get(ancestor.task.id, 0) + 1

    selected: list[PlannedTask] = []
    for node in plan:
        if node.flowable and not node.dynamic:
            continue
        task_run = task_runs_by_id[node.task.id]
        recovering = (
            task_run.state is TaskRunState.RUNNING
            and node.task.type in recover_running_types
            and task_run.task_run_id not in deferred_task_run_ids
        )
        if node.task.id not in runnable_ids and not recovering:
            continue
        ancestors = _flowable_ancestors(node, plan_by_id)
        if not recovering and any(
            ancestor.max_concurrency is not None
            and limited_counts.get(ancestor.task.id, 0) >= ancestor.max_concurrency
            for ancestor in ancestors
        ):
            continue
        selected.append(node)
        if not recovering:
            for ancestor in ancestors:
                if ancestor.max_concurrency is not None:
                    limited_counts[ancestor.task.id] = limited_counts.get(ancestor.task.id, 0) + 1
        if max_tasks is not None and len(selected) >= max_tasks:
            break
    return selected


def _flowable_ancestors(
    node: PlannedTask,
    plan_by_id: Mapping[str, PlannedTask],
) -> tuple[PlannedTask, ...]:
    ancestors: list[PlannedTask] = []
    parent_id = node.parent_id
    while parent_id is not None:
        parent = plan_by_id[parent_id]
        ancestors.append(parent)
        parent_id = parent.parent_id
    return tuple(ancestors)


def _working_directory_ancestor(
    node: PlannedTask,
    plan_by_id: Mapping[str, PlannedTask],
) -> TaskDefinition | None:
    return next(
        (
            ancestor.task
            for ancestor in _flowable_ancestors(node, plan_by_id)
            if ancestor.task.type == "core.workingDirectory"
        ),
        None,
    )


def _parent_is_running(
    node: PlannedTask,
    task_runs_by_id: Mapping[str, PersistedTaskRun],
) -> bool:
    return node.parent_id is None or task_runs_by_id[node.parent_id].state is TaskRunState.RUNNING


def _dependencies_satisfied(
    node: PlannedTask,
    plan_by_id: Mapping[str, PlannedTask],
    task_runs_by_id: Mapping[str, PersistedTaskRun],
) -> bool:
    for dependency_id in node.dependencies:
        dependency = task_runs_by_id[dependency_id]
        if dependency.state is TaskRunState.SUCCESS:
            continue
        if node.lifecycle_phase is not LifecyclePhase.MAIN and _task_run_is_terminal(dependency):
            continue
        if (
            dependency.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
            and node.parent_id is not None
            and plan_by_id[dependency_id].parent_id == node.parent_id
            and plan_by_id[node.parent_id].failure_policy is not FlowableFailurePolicy.FAIL_FAST
        ):
            continue
        return False
    return True


def _task_run_is_terminal(task_run: PersistedTaskRun) -> bool:
    return task_run.state in {
        TaskRunState.SUCCESS,
        TaskRunState.FAILED,
        TaskRunState.CANCELLED,
    }


def _aggregate_flowable_result(
    node: PlannedTask,
    children: list[PersistedTaskRun],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "mode": node.mode,
        "failurePolicy": node.failure_policy.value,
        "childOrder": [child.task_id for child in children],
        "children": {
            child.task_id: {
                "state": child.state.value,
                "output": child.result if child.state is TaskRunState.SUCCESS else None,
                "error": (
                    (child.result or {}).get("error")
                    if child.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
                    else None
                ),
            }
            for child in children
        },
    }
    if node.mode == "AGENT_MESH":
        definition = _agent_mesh_definition(node)
        usage = _agent_mesh_usage(node, definition, children)
        result["agentMesh"] = {
            "schemaVersion": "amesh.agent-mesh/v1",
            "topology": definition.topology.value,
            "members": [
                member.model_dump(mode="json", by_alias=True) for member in definition.members
            ],
            "budget": definition.budget.model_dump(mode="json", by_alias=True),
            "usage": usage,
            "routing": [
                child.result["agentRoute"]
                for child in children
                if child.result is not None and "agentRoute" in child.result
            ],
            "handoffs": [
                child.result["agentHandoff"]
                for child in children
                if child.result is not None and "agentHandoff" in child.result
            ],
            "nondeterministic": True,
            "nondeterminismDisclosure": (
                "Topology, routing, policy and budgets are deterministic; model outputs are not."
            ),
        }
    return result


def _agent_mesh_definition(node: PlannedTask) -> AgentMeshDefinition:
    extra = node.task.configuration.handler_view()
    return AgentMeshDefinition.model_validate(
        {
            "topology": extra.get("topology"),
            "members": extra.get("members"),
            "budget": extra.get("budget"),
        }
    )


def _agent_mesh_usage(
    node: PlannedTask,
    definition: AgentMeshDefinition,
    children: list[PersistedTaskRun],
) -> dict[str, object]:
    member_tasks = {member.task for member in definition.members}
    sessions = 0
    total_tokens = 0
    total_cost = Decimal(0)
    tool_calls = 0
    for child in children:
        if child.task_id not in member_tasks:
            continue
        counters: object | None = None
        if child.result is not None:
            session = child.result.get("session")
            if isinstance(session, dict):
                counters = session.get("counters")
        if counters is None:
            failure = child.evidence.get("agentSession")
            if isinstance(failure, dict):
                counters = failure.get("counters")
        if not isinstance(counters, dict):
            continue
        sessions += 1
        total_tokens += _mesh_counter_int(counters, "totalTokens")
        total_cost += Decimal(str(counters.get("costUsd", "0")))
        tool_calls += _mesh_counter_int(counters, "toolCalls")
    return {
        "sessions": sessions,
        "totalTokens": total_tokens,
        "costUsd": str(total_cost),
        "toolCalls": tool_calls,
        "reservedDurationSeconds": sum(
            AgentMeshSessionBudget.model_validate(
                child.configuration.handler_view().get("meshBudget")
            ).max_duration_seconds
            for child in node.task.tasks
            if child.id in member_tasks
        ),
    }


def _mesh_counter_int(counters: Mapping[str, object], key: str) -> int:
    value = counters.get(key, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _agent_mesh_budget_error(
    node: PlannedTask,
    children: list[PersistedTaskRun],
) -> str | None:
    if node.mode != "AGENT_MESH":
        return None
    definition = _agent_mesh_definition(node)
    usage = _agent_mesh_usage(node, definition, children)
    exceeded: list[str] = []
    if _mesh_counter_int(usage, "sessions") > definition.budget.max_sessions:
        exceeded.append("maxSessions")
    if _mesh_counter_int(usage, "totalTokens") > definition.budget.max_total_tokens:
        exceeded.append("maxTotalTokens")
    if Decimal(str(usage["costUsd"])) > definition.budget.max_cost_usd:
        exceeded.append("maxCostUsd")
    if _mesh_counter_int(usage, "toolCalls") > definition.budget.max_tool_calls:
        exceeded.append("maxToolCalls")
    if exceeded:
        return "agent.mesh exceeded parent budget: " + ", ".join(exceeded)
    return None


def _template_visible_output_ids(
    task_id: str,
    tasks_by_id: Mapping[str, TaskDefinition],
) -> frozenset[str]:
    visible: set[str] = set()
    pending = list(tasks_by_id[task_id].depends_on)
    while pending:
        dependency = pending.pop()
        if dependency in visible:
            continue
        visible.add(dependency)
        pending.extend(tasks_by_id[dependency].depends_on)
    return frozenset(visible)


def _expression_context(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    outputs: Mapping[str, dict[str, Any]],
    *,
    iteration: LoopIterationContext | None = None,
    failure_category: FailureCategory | None = None,
    error: str | None = None,
    handler_error: Mapping[str, Any] | None = None,
) -> ExpressionContext:
    return ExpressionContext(
        flow={
            "id": flow.id,
            "namespace": flow.namespace,
            "revision": flow.revision,
        },
        execution={
            "id": str(execution.execution_id),
            "state": execution.state.value,
            "startDate": execution.created_at,
            "tenantId": execution.tenant_id,
        },
        task=task.model_dump(mode="json", by_alias=True),
        taskrun={
            "id": str(task_run.task_run_id),
            "attempt": task_run.current_attempt,
            "state": task_run.state.value,
            "failureCategory": failure_category.value if failure_category is not None else None,
            "error": error,
        },
        trigger=_user_trigger_context(execution),
        inputs=execution.inputs,
        outputs=outputs,
        variables=flow.variables,
        labels=flow.labels,
        namespace={"id": flow.namespace},
        iteration=iteration.as_mapping() if iteration is not None else {},
        error=handler_error or {},
    )


def _flowable_expression_context(
    flow: FlowDefinition,
    execution: PersistedExecution,
    node: PlannedTask,
    task_run: PersistedTaskRun,
    plan: tuple[PlannedTask, ...],
    by_task_id: Mapping[str, PersistedTaskRun],
    *,
    handler_error: Mapping[str, Any] | None = None,
) -> ExpressionContext:
    visible = visible_output_ids(node.task.id, plan)
    outputs = {
        task_id: task_state.result or {}
        for task_id, task_state in by_task_id.items()
        if task_id in visible and task_state.state is TaskRunState.SUCCESS
    }
    return _expression_context(
        flow,
        execution,
        task_run,
        node.task,
        outputs,
        handler_error=handler_error,
    )


def _user_trigger_context(execution: PersistedExecution) -> dict[str, Any]:
    return {key: value for key, value in execution.trigger.items() if not key.startswith("_amesh")}


def _descends_from(
    candidate: PlannedTask,
    ancestor: PlannedTask,
    by_node_id: Mapping[str, PlannedTask],
) -> bool:
    parent_id = candidate.parent_id
    while parent_id is not None:
        if parent_id == ancestor.task.id:
            return True
        parent = by_node_id.get(parent_id)
        parent_id = parent.parent_id if parent is not None else None
    return False


def _branch_evidence(evidence: Mapping[str, Any]) -> dict[str, object] | None:
    control = evidence.get("control")
    if not isinstance(control, Mapping):
        return None
    branch = control.get("branch")
    return dict(branch) if isinstance(branch, Mapping) else None


def _merge_task_control(
    evidence: Mapping[str, Any],
    key: str,
    value: Mapping[str, object],
) -> dict[str, object]:
    merged = deepcopy(dict(evidence))
    existing = merged.get("control")
    control = dict(existing) if isinstance(existing, Mapping) else {}
    control[key] = dict(value)
    merged["control"] = control
    return merged


def _merge_control_evidence(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, object]:
    merged = deepcopy(dict(left))
    for source in (left, right):
        control = source.get("control")
        if not isinstance(control, Mapping):
            continue
        existing = merged.get("control")
        combined = dict(existing) if isinstance(existing, Mapping) else {}
        combined.update(dict(control))
        merged["control"] = combined
    return merged


def _merge_completion_evidence(
    completion: Mapping[str, object],
    condition: Mapping[str, object],
) -> dict[str, object]:
    merged = dict(completion)
    control = condition.get("control")
    if isinstance(control, Mapping):
        merged["control"] = dict(control)
    return merged


def _sensitive_input_values(
    flow: FlowDefinition,
    execution: PersistedExecution,
) -> tuple[Any, ...]:
    return tuple(
        execution.inputs[definition.id]
        for definition in flow.inputs
        if definition.sensitive and definition.id in execution.inputs
    )


def _redact_condition_value(value: Any, sensitive_values: tuple[Any, ...]) -> Any:
    for sensitive in sensitive_values:
        try:
            if value == sensitive:
                return "[REDACTED]"
        except (TypeError, ValueError):
            pass
    if isinstance(value, str):
        redacted = value
        for sensitive in sensitive_values:
            if isinstance(sensitive, str) and sensitive:
                redacted = redacted.replace(sensitive, "[REDACTED]")
        return redacted
    if isinstance(value, list):
        return [_redact_condition_value(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_condition_value(item, sensitive_values) for item in value)
    if isinstance(value, Mapping):
        return {key: _redact_condition_value(item, sensitive_values) for key, item in value.items()}
    return redact_secret_values(value)


def _redacted_condition_inputs(
    flow: FlowDefinition,
    execution: PersistedExecution,
    context: ExpressionContext,
) -> dict[str, object]:
    values = context.public_values()
    redacted = redact_secret_values(
        _redact_condition_value(
            values,
            _sensitive_input_values(flow, execution),
        )
    )
    return dict(json.loads(json.dumps(redacted, default=_canonical_json_default)))


def _switch_case_key(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.lower() in {"true", "false", "null"}:
            return normalized.lower()
        return normalized
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def derive_task_cache_key(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> TaskCacheKey:
    """Derive a stable key without persisting raw security-context material."""

    policy = task.task_cache
    if not policy.enabled or policy.ttl is None:
        raise ValueError("task cache key requires an enabled policy with ttl")
    declared_inputs = {
        definition.id: execution.inputs.get(definition.id, definition.default)
        for definition in flow.inputs
    }
    selectable_context: dict[str, object] = {
        "inputs": declared_inputs,
        "variables": flow.variables,
        "labels": {
            key: value
            for key, value in execution.labels.items()
            if not key.startswith(("amesh.", "system."))
        },
        "trigger": {
            key: value for key, value in execution.trigger.items() if not key.startswith("_amesh")
        },
        "iteration": context.iteration.as_mapping() if context.iteration is not None else {},
    }
    security_payload = {
        "tenant": execution.tenant_id,
        "secretScopes": sorted(context.secret_scopes),
        "secrets": sorted(context.secrets.items()),
        "files": sorted(context.files.items()),
    }
    security_context_hash = hashlib.sha256(_canonical_json(security_payload)).hexdigest()
    code_version = policy.code_version or f"amesh:{__version__}:{task.type}"
    payload = {
        "schema": "amesh.task-cache/v1",
        "tenant": execution.tenant_id,
        "flow": {
            "namespace": flow.namespace,
            "id": flow.id,
            "revision": flow.revision,
        },
        "task": task.model_dump(
            mode="json",
            by_alias=True,
            exclude={"task_cache"},
            exclude_none=True,
        ),
        "policy": policy.model_dump(mode="json", by_alias=True, exclude_none=True),
        "codeVersion": code_version,
        "context": {name: selectable_context[name] for name in policy.key_context},
        "securityContextHash": security_context_hash,
    }
    cache_namespace = policy.namespace or "default"
    prefix_parts = [cache_namespace, flow.namespace]
    if policy.scope.value in {"TASK", "FLOW"}:
        prefix_parts.append(flow.id)
    if policy.scope.value == "TASK":
        prefix_parts.append(task.id)
    key_prefix = "/".join(prefix_parts)
    lease_seconds = max(task.timeout_seconds or 3600, 60)
    return TaskCacheKey(
        key_hash=hashlib.sha256(_canonical_json(payload)).hexdigest(),
        key_prefix=key_prefix,
        cache_namespace=cache_namespace,
        scope=policy.scope.value,
        namespace=flow.namespace,
        flow_id=flow.id,
        flow_revision=flow.revision,
        task_id=task.id,
        task_type=task.type,
        security_context_hash=security_context_hash,
        invalidation_policy=policy.invalidation_policy.value,
        ttl=policy.ttl,
        population_lease=timedelta(seconds=lease_seconds),
    )


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        default=_canonical_json_default,
    ).encode("utf-8")


def _canonical_json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return str(value)


def _contains_kv_expression(value: object) -> bool:
    if isinstance(value, str):
        return "kv(" in value
    if isinstance(value, Mapping):
        return any(_contains_kv_expression(item) for item in value.values())
    if isinstance(value, list | tuple):
        return any(_contains_kv_expression(item) for item in value)
    return False


def _execution_cache_mode(execution: PersistedExecution) -> TaskCacheMode:
    raw = execution.trigger.get("_ameshCacheMode", TaskCacheMode.USE.value)
    try:
        return TaskCacheMode(str(raw))
    except ValueError:
        return TaskCacheMode.USE


def _with_cache_evidence(
    evidence: Mapping[str, object],
    lookup: TaskCacheLookup,
) -> dict[str, object]:
    result = deepcopy(dict(evidence))
    result["cache"] = {
        "decision": lookup.decision.value,
        "reason": lookup.reason,
        "keyHash": lookup.key_hash,
        "sourceExecutionId": (
            str(lookup.source_execution_id) if lookup.source_execution_id is not None else None
        ),
        "sourceTaskRunId": (
            str(lookup.source_task_run_id) if lookup.source_task_run_id is not None else None
        ),
        "sourceAttempt": lookup.source_attempt,
        "expiresAt": lookup.expires_at.isoformat() if lookup.expires_at is not None else None,
    }
    stored_logs = result.get("logs", [])
    logs = list(stored_logs) if isinstance(stored_logs, list) else []
    logs.insert(
        0,
        TaskLogRecord(
            logger="amesh.task.cache",
            message=f"Cache {lookup.decision.value}: {lookup.reason}",
            fields={"keyHash": lookup.key_hash},
            sourceStream=LogSourceStream.SYSTEM,
            occurredAt=datetime.now(UTC),
        ).model_dump(mode="json", by_alias=True),
    )
    result["logs"] = logs
    return result


async def _abandon_cache_population(
    repository: TaskCacheRepository | None,
    key: TaskCacheKey,
    lookup: TaskCacheLookup,
    *,
    tenant_id: str,
    execution_id: UUID,
    task_run_id: UUID,
    attempt: int,
    reason: str,
) -> None:
    if repository is None or lookup.owner_token is None:
        return
    try:
        await repository.abandon(
            key.key_hash,
            lookup.owner_token,
            tenant_id=tenant_id,
            execution_id=execution_id,
            task_run_id=task_run_id,
            attempt=attempt,
            reason=reason,
        )
    except Exception:
        LOGGER.exception(
            "task result cache abandonment failed",
            extra={
                "tenant_id": tenant_id,
                "execution_id": str(execution_id),
                "task_run_id": str(task_run_id),
                "cache_key_hash": key.key_hash,
                "reason": reason,
            },
        )
        raise


def _require_matching_plan(
    flow: FlowDefinition,
    task_runs_by_id: Mapping[str, PersistedTaskRun],
) -> None:
    expected = {node.task.id for node in compile_flow_tasks(flow)}
    persisted = {
        task_id for task_id, task_run in task_runs_by_id.items() if task_run.iteration_key is None
    }
    if expected != persisted:
        raise ExecutionBlockedError(
            f"persisted task plan does not match flow revision: expected={sorted(expected)}, "
            f"persisted={sorted(persisted)}"
        )


def _is_ready(task_run: PersistedTaskRun, now: datetime) -> bool:
    if task_run.state is TaskRunState.WAITING:
        return True
    retry_at = task_run.retry_at
    return task_run.state is TaskRunState.RETRY_DELAY and retry_at is not None and retry_at <= now


def normalize_task_completion(
    result: dict[str, Any] | TaskCompletion,
    limits: TaskResourceLimits,
    *,
    secret_values: Iterable[str] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    completion = result if isinstance(result, TaskCompletion) else TaskCompletion(output=result)
    serialized = completion.model_dump(mode="json", by_alias=True)
    sensitive_keys = {
        key.casefold().replace("-", "_") for key in serialized.pop("sensitiveOutputKeys")
    }
    secrets = tuple(value for value in secret_values if value)
    output, output_redacted = _redact_task_evidence(
        serialized["output"],
        sensitive_keys=sensitive_keys,
        secret_values=secrets,
    )
    logs = serialized["logs"]
    for log in logs:
        if log["redacted"]:
            log["message"] = "[REDACTED]"
            log["fields"] = {}
            continue
        message, message_redacted = _redact_task_evidence(
            log["message"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        fields, fields_redacted = _redact_task_evidence(
            log["fields"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        log["message"] = message
        log["fields"] = fields
        log["redacted"] = message_redacted or fields_redacted
    for metric in serialized["metrics"]:
        labels, _ = _redact_task_evidence(
            metric["labels"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        metric["labels"] = labels
    artifacts = serialized["artifacts"]
    for artifact in artifacts:
        uri, uri_redacted = _redact_task_evidence(
            artifact["uri"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        if uri_redacted:
            raise TaskResourceLimitError("artifact URI contains secret material")
        artifact["uri"] = uri
    assets, assets_redacted = _redact_task_evidence(
        serialized["assets"], sensitive_keys=sensitive_keys, secret_values=secrets
    )
    if assets_redacted:
        raise TaskResourceLimitError("asset event contains secret material")
    exit_metadata, _ = _redact_task_evidence(
        serialized["exit"], sensitive_keys=sensitive_keys, secret_values=secrets
    )
    output_bytes = _json_size(output)
    log_bytes = _json_size(logs)
    artifact_bytes = sum(int(artifact["sizeBytes"]) for artifact in artifacts)
    _require_within_limit("output", output_bytes, limits.max_output_bytes)
    _require_within_limit("log", log_bytes, limits.max_log_bytes)
    _require_within_limit("artifact", artifact_bytes, limits.max_artifact_bytes)
    return output, {
        "logs": logs,
        "metrics": serialized["metrics"],
        "artifacts": artifacts,
        "assets": assets,
        "exit": exit_metadata,
        "outputSensitive": bool(sensitive_keys or output_redacted),
        "sizes": {
            "outputBytes": output_bytes,
            "logBytes": log_bytes,
            "artifactBytes": artifact_bytes,
        },
    }


def _is_sensitive_field_name(value: str) -> bool:
    normalized = "".join(character for character in value.casefold() if character.isalnum())
    if normalized in {
        "apikey",
        "authorization",
        "credential",
        "credentials",
        "password",
        "secret",
        "secrets",
        "token",
    }:
        return True
    return normalized.startswith(
        ("authorization", "credential", "password", "secret")
    ) or normalized.endswith(("apikey", "credential", "password", "secret", "token"))


def _redact_task_evidence(
    value: Any,
    *,
    sensitive_keys: set[str],
    secret_values: tuple[str, ...],
) -> tuple[Any, bool]:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        changed = False
        for key, item in value.items():
            normalized = str(key).casefold().replace("-", "_")
            if normalized in sensitive_keys or _is_sensitive_field_name(normalized):
                redacted[key] = "[REDACTED]"
                changed = True
                continue
            redacted[key], item_changed = _redact_task_evidence(
                item,
                sensitive_keys=sensitive_keys,
                secret_values=secret_values,
            )
            changed = changed or item_changed
        return redacted, changed
    if isinstance(value, list):
        redacted_items: list[Any] = []
        changed = False
        for item in value:
            redacted, item_changed = _redact_task_evidence(
                item,
                sensitive_keys=sensitive_keys,
                secret_values=secret_values,
            )
            redacted_items.append(redacted)
            changed = changed or item_changed
        return redacted_items, changed
    if isinstance(value, str):
        redacted_text = value
        for secret in sorted(set(secret_values), key=len, reverse=True):
            redacted_text = redacted_text.replace(secret, "[REDACTED]")
        return redacted_text, redacted_text != value
    return value, False


def _json_size(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _require_within_limit(kind: str, actual: int, limit: int) -> None:
    if actual > limit:
        raise TaskResourceLimitError(
            f"task {kind} evidence is {actual} bytes; configured limit is {limit} bytes"
        )


def _validate_registered_task_schemas(
    flow: FlowDefinition,
    registry: ResourceSchemaRegistry,
) -> None:
    pending = [*flow.tasks, *flow.errors, *flow.finally_tasks, *flow.after_execution]
    while pending:
        task = pending.pop(0)
        pending[0:0] = [
            *[child for _, children in task.child_task_groups() for child in children],
            *task.errors,
        ]
        issues = registry.validate(ResourceKind.TASK, task.type, task.configuration)
        if issues:
            details = "; ".join(issue.message for issue in issues)
            raise TaskConfigurationError(
                f"task {task.id!r} configuration does not match {task.type!r}: {details}"
            )


def _core_handlers() -> dict[str, TaskHandler]:
    return {
        "core.log": _run_core_log,
        "core.return": _run_core_return,
    }


async def _run_core_log(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> TaskCompletion:
    extra = task.configuration.handler_view()
    message = str(redact_secret_values(extra.get("message", "")))
    LOGGER.info(
        message,
        extra={
            "tenant_id": context.tenant_id,
            "execution_id": str(context.execution_id),
            "task_run_id": str(context.task_run_id),
            "task_id": task.id,
        },
    )
    return TaskCompletion(
        output={"message": message},
        logs=(
            TaskLogRecord(
                logger="amesh.task.core.log",
                message=message,
                fields={"taskId": task.id},
                redacted=message == "[REDACTED]",
            ),
        ),
    )


async def _run_core_return(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> dict[str, Any]:
    del context
    extra = task.configuration.handler_view()
    return {"value": extra.get("value")}


def _render_task_for_execution(
    expressions: ExpressionEngine,
    task: TaskDefinition,
    context: ExpressionContext,
) -> TaskDefinition:
    extra = task.configuration.handler_view()
    deferred_keys = (
        frozenset({"condition", "continueIf", "breakIf"})
        if task.type in LOOP_TASK_TYPES
        else frozenset({"outputMapping", "outputSchema", "artifactMapping", "artifactSchema"})
    )
    deferred = {key: extra[key] for key in deferred_keys if key in extra}
    if task.type not in {"core.subflow", *LOOP_TASK_TYPES} or not deferred:
        return expressions.render_task(task, context)

    payload = task.model_dump(mode="python", by_alias=True)
    for key in deferred:
        payload.pop(key, None)
    rendered = expressions.render_task(TaskDefinition.model_validate(payload), context)
    rendered_payload = rendered.model_dump(mode="python", by_alias=True)
    rendered_payload.update(deferred)
    return TaskDefinition.model_validate(rendered_payload)


def _combine_declared_files(*mappings: Mapping[str, str]) -> dict[str, str]:
    combined: dict[str, str] = {}
    for mapping in mappings:
        for path, reference in mapping.items():
            existing = combined.get(path)
            if existing is not None and existing != reference:
                raise TaskConfigurationError(
                    f"workspace path {path!r} has conflicting input file references"
                )
            combined[path] = reference
    return combined


def _render_declared_files(
    expressions: ExpressionEngine,
    declared_files: Mapping[str, str],
    context: ExpressionContext,
) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for path, reference in declared_files.items():
        value = expressions.render_value(reference, context)
        if not isinstance(value, str) or not value:
            raise TaskConfigurationError(
                f"inputFiles reference for {path!r} must render to a non-empty internal URI"
            )
        rendered[path] = str(value)
    return rendered
