from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from contextlib import suppress
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid5

from amesh.backoff import bounded_exponential_backoff
from amesh.domain import ExecutionState
from amesh.dsl import (
    ErrorSelector,
    FlowDefinition,
    LifecyclePhase,
    PlannedTask,
    ResourceSchemaRegistry,
    compile_flow_tasks,
    default_resource_registry,
)
from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionContext, ExpressionEngine, NativeExpressionEngine
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    ObjectStore,
    PersistedExecution,
    PersistedTaskRun,
    TaskCacheRepository,
    TaskRunState,
    TaskStateConflictError,
)
from amesh.workflow.data_contracts import render_flow_outputs, validate_flow_inputs

if TYPE_CHECKING:
    from amesh.workflow.working_directory import WorkingDirectoryManager

from . import execution_runtime, flowable_execution, lifecycle_execution, loop_execution
from .attempt_execution import AttemptExecutionCallbacks, execute_task_attempt
from .conditions import ConditionEvaluator
from .contracts import BranchDecision as _BranchDecision
from .contracts import ConditionDecision as _ConditionDecision
from .contracts import (
    DispatchPolicyEnforcer,
    ExecutionBlockedError,
    ExecutionProgress,
    OrchestrationDecision,
    TaskArtifactRecord,
    TaskCompletion,
    TaskConfigurationError,
    TaskContextProvider,
    TaskContextRequest,
    TaskContextResources,
    TaskExecutionFailure,
    TaskHandler,
    TaskPlatformError,
)
from .contracts import LoopExecutionFailure as LoopExecutionFailure
from .contracts import TaskExecutionContext as TaskExecutionContext
from .contracts import TaskExecutionError as TaskExecutionError
from .contracts import TaskExecutionPaused as TaskExecutionPaused
from .contracts import TaskResourceLimitError as TaskResourceLimitError
from .contracts import TaskRunOutcome as _TaskRunOutcome
from .contracts import TaskUserCodeError as TaskUserCodeError
from .contracts import classify_task_failure as classify_task_failure
from .contracts import retry_delay_seconds as retry_delay_seconds
from .flowable_core import _agent_mesh_budget_error as _agent_mesh_budget_error
from .flowable_core import _aggregate_flowable_result as _aggregate_flowable_result
from .flowable_core import _user_trigger_context
from .loops import LOOP_TASK_TYPES, LoopIterationContext, LoopSpec
from .orchestration_core import (
    _reduce_lifecycle_phase,
    _select_ready_tasks,
    _working_directory_ancestor,
)
from .orchestration_core import (
    execution_lifecycle_pending as execution_lifecycle_pending,
)
from .orchestration_core import reduce_orchestration as reduce_orchestration
from .task_handlers import _contains_kv_expression, _core_handlers
from .task_handlers import _run_core_log as _run_core_log
from .task_results import _abandon_cache_population as _abandon_cache_population
from .task_results import _validate_registered_task_schemas
from .task_results import derive_task_cache_key as derive_task_cache_key
from .task_results import normalize_task_completion as normalize_task_completion

LOGGER = logging.getLogger("amesh.task.core.log")


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
        return await execution_runtime.run_ready(
            self,
            flow,
            execution_id,
            tenant_id=tenant_id,
            max_tasks=max_tasks,
        )

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
        return await lifecycle_execution.advance_execution_lifecycle(
            flow,
            execution,
            execution_plan,
            task_runs,
            primary_decision=primary_decision,
            max_tasks=max_tasks,
            repository=self._repository,
            finish_execution=self._finish_execution,
            run_lifecycle_phase=self._run_lifecycle_phase,
            skip_lifecycle_tasks=self._skip_lifecycle_tasks,
            claimed_tasks=claimed_tasks,
            primary_failure=primary_failure,
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
        return await flowable_execution.advance_flowables(
            flow,
            execution,
            plan,
            task_runs,
            tenant_id=tenant_id,
            repository=self._repository,
            evaluate_task_condition=self._evaluate_task_condition,
            select_branch=self._select_branch,
            finalize_working_directory=self._finalize_working_directory,
            handler_errors=handler_errors,
        )

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

    def _evaluate_run_if(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> _ConditionDecision:
        return ConditionEvaluator(self._expressions).evaluate_run_if(
            flow,
            execution,
            task,
            context,
        )

    def _evaluate_error_selector(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        selector: ErrorSelector | None,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> _ConditionDecision:
        return ConditionEvaluator(self._expressions).evaluate_error_selector(
            flow,
            execution,
            selector,
            context,
            handler_error,
        )

    def _evaluate_task_condition(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> _ConditionDecision:
        return ConditionEvaluator(self._expressions).evaluate_task_condition(
            flow,
            execution,
            task,
            context,
            handler_error,
        )

    def _select_branch(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> _BranchDecision:
        return ConditionEvaluator(self._expressions).select_branch(
            flow,
            execution,
            task,
            context,
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
        return await execute_task_attempt(
            AttemptExecutionCallbacks(
                repository=self._repository,
                handlers=self._handlers,
                expressions=self._expressions,
                evaluate_task_condition=self._evaluate_task_condition,
                resolve_context_resources=self._resolve_context_resources,
                run_loop=self._run_loop,
                task_cache=self._task_cache,
                dispatch_policy_enforcer=self._dispatch_policy_enforcer,
            ),
            flow,
            execution,
            task_run,
            task,
            outputs,
            workspace_parent,
            iteration,
            handler_error,
        )

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
        return await loop_execution.run_loop(
            flow,
            execution,
            parent_run,
            task,
            upstream_outputs,
            repository=self._repository,
            expressions=self._expressions,
            object_store=self._object_store,
            run_task=self._run_task,
            admission_poll_initial_seconds=self._admission_poll_initial_seconds,
            admission_poll_max_seconds=self._admission_poll_max_seconds,
        )

    async def _run_loop_iteration(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        loop_task: TaskDefinition,
        iteration: LoopIterationContext,
        upstream_outputs: Mapping[str, dict[str, Any]],
    ) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        return await loop_execution.run_loop_iteration(
            flow,
            execution,
            loop_task,
            iteration,
            upstream_outputs,
            repository=self._repository,
            run_task=self._run_task,
            admission_poll_initial_seconds=self._admission_poll_initial_seconds,
            admission_poll_max_seconds=self._admission_poll_max_seconds,
        )

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
        return loop_execution.evaluate_loop_condition(
            self._expressions,
            expression,
            flow,
            execution,
            parent_run,
            task,
            outputs,
            iteration,
        )

    async def _finalize_loop_result(
        self,
        execution: PersistedExecution,
        parent_run: PersistedTaskRun,
        task: TaskDefinition,
        spec: LoopSpec,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return await loop_execution.finalize_loop_result(
            execution,
            parent_run,
            task,
            spec,
            results,
            object_store=self._object_store,
        )

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
