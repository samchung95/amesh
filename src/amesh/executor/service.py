from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition
from amesh.dsl.models import TaskDefinition
from amesh.expressions import (
    ExpressionContext,
    ExpressionEngine,
    NativeExpressionEngine,
    redact_secret_values,
)
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionRepository,
    PersistedExecution,
    PersistedTaskRun,
    TaskRunState,
    TaskStateConflictError,
)

LOGGER = logging.getLogger("amesh.task.core.log")


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


TaskHandler = Callable[[TaskDefinition, TaskExecutionContext], Awaitable[dict[str, Any]]]


class ExecutionBlockedError(RuntimeError):
    """Raised when an unfinished execution has no runnable task."""


class TaskExecutionError(RuntimeError):
    """Raised after a task failure has been persisted."""


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


class InProcessExecutor:
    """Runs the MVP top-level DAG while PostgreSQL remains authoritative for progress."""

    def __init__(
        self,
        repository: ExecutionRepository,
        handlers: Mapping[str, TaskHandler] | None = None,
        expressions: ExpressionEngine | None = None,
        recover_running_types: frozenset[str] | None = None,
    ) -> None:
        self._repository = repository
        self._handlers = _core_handlers()
        self._handlers.update(handlers or {})
        self._expressions = expressions or NativeExpressionEngine()
        self._recover_running_types = recover_running_types or frozenset()

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
        execution = await self._repository.create_execution(
            flow,
            tenant_id=tenant_id,
            inputs=inputs or {},
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
        if execution.state is not ExecutionState.RUNNING:
            return ExecutionProgress(
                execution_id=execution_id,
                state=execution.state,
                tasks_run=0,
                task_runs=tuple(task_runs),
            )

        now = datetime.now(UTC)
        decision = reduce_orchestration(flow, task_runs, now=now)
        if decision.terminal_state is not None:
            execution = await self._finish_execution(execution, decision)
            return ExecutionProgress(
                execution_id=execution_id,
                state=execution.state,
                tasks_run=0,
                task_runs=tuple(task_runs),
            )

        task_runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
        runnable_ids = set(decision.runnable_task_ids)
        ready = [
            task
            for task in flow.tasks
            if task.id in runnable_ids
            or (
                task_runs_by_id[task.id].state is TaskRunState.RUNNING
                and task.type in self._recover_running_types
            )
        ]
        if max_tasks is not None:
            ready = ready[:max_tasks]

        outputs = {
            task_id: task_run.result or {}
            for task_id, task_run in task_runs_by_id.items()
            if task_run.state is TaskRunState.SUCCESS
        }
        outcomes = await asyncio.gather(
            *(
                self._run_task(
                    flow,
                    execution,
                    task_runs_by_id[task.id],
                    task,
                    outputs,
                )
                for task in ready
            )
        )

        updated_task_runs = await self._repository.list_task_runs(
            execution_id,
            tenant_id=tenant_id,
        )
        updated_decision = reduce_orchestration(
            flow,
            updated_task_runs,
            now=datetime.now(UTC),
        )
        if updated_decision.terminal_state is not None:
            execution = await self._finish_execution(execution, updated_decision)
        else:
            execution = await self._repository.get_execution(execution_id, tenant_id=tenant_id)
        progress = ExecutionProgress(
            execution_id=execution_id,
            state=execution.state,
            tasks_run=sum(outcome.claimed for outcome in outcomes),
            task_runs=tuple(updated_task_runs),
        )
        failure = next((outcome.failure for outcome in outcomes if outcome.failure), None)
        if failure is not None:
            raise TaskExecutionError(updated_decision.diagnostic or failure)
        return progress

    async def run_to_completion(
        self,
        flow: FlowDefinition,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> ExecutionProgress:
        while True:
            progress = await self.run_ready(
                flow,
                execution_id,
                tenant_id=tenant_id,
            )
            if progress.state is ExecutionState.SUCCESS:
                return progress
            if progress.state is not ExecutionState.RUNNING:
                raise ExecutionBlockedError(
                    f"execution {execution_id} stopped in state {progress.state.value}"
                )
            if progress.tasks_run == 0:
                if any(task_run.state is TaskRunState.RUNNING for task_run in progress.task_runs):
                    await asyncio.sleep(0.05)
                    continue
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
                    delay_seconds = max((retry_at - datetime.now(UTC)).total_seconds(), 0)
                    await asyncio.sleep(min(delay_seconds, 1))
                    continue
                waiting = [
                    task_run.task_id
                    for task_run in progress.task_runs
                    if task_run.state is TaskRunState.WAITING
                ]
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
        expression_context = _expression_context(flow, execution, projected, task, outputs)
        condition_error: Exception | None = None
        try:
            condition_matches = task.run_if is None or self._expressions.evaluate_condition(
                task.run_if,
                expression_context,
            )
        except Exception as exc:
            condition_matches = False
            condition_error = exc
        try:
            running = (
                task_run
                if task_run.state is TaskRunState.RUNNING
                else await self._repository.start_task(
                    task_run.task_run_id,
                    tenant_id=tenant_id,
                    dispatch=condition_matches,
                )
            )
        except TaskStateConflictError:
            return _TaskRunOutcome(claimed=False)
        if not condition_matches and condition_error is None:
            await self._repository.complete_task(
                running.task_run_id,
                running.current_attempt,
                {"skipped": True},
                tenant_id=tenant_id,
            )
            return _TaskRunOutcome(claimed=True)
        handler = self._handlers.get(task.type)
        if handler is None:
            reason = f"no in-process handler registered for task type {task.type!r}"
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
            )
            return _TaskRunOutcome(claimed=True, failure=reason)
        context = TaskExecutionContext(
            tenant_id=tenant_id,
            execution_id=execution_id,
            task_run_id=running.task_run_id,
            attempt=running.current_attempt,
            attempt_id=uuid5(running.task_run_id, f"attempt:{running.current_attempt}"),
            inputs=execution.inputs,
            outputs=outputs,
            variables=flow.variables,
        )
        try:
            if condition_error is not None:
                raise condition_error
            rendered_task = self._expressions.render_task(task, expression_context)
            result = await handler(rendered_task, context)
        except Exception as exc:
            reason = f"task {task.id!r} failed: {exc}"
            if running.current_attempt < task.retry.max_attempts:
                retry_at = datetime.now(UTC) + timedelta(
                    seconds=task.retry.delay_seconds
                    * task.retry.backoff_multiplier ** (running.current_attempt - 1)
                )
                await self._repository.retry_task(
                    running.task_run_id,
                    running.current_attempt,
                    retry_at=retry_at,
                    reason=reason,
                    tenant_id=tenant_id,
                )
                return _TaskRunOutcome(claimed=True)
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
            )
            return _TaskRunOutcome(claimed=True, failure=reason)
        await self._repository.complete_task(
            running.task_run_id,
            running.current_attempt,
            result,
            tenant_id=tenant_id,
        )
        return _TaskRunOutcome(claimed=True)

    async def _finish_execution(
        self,
        execution: PersistedExecution,
        decision: OrchestrationDecision,
    ) -> PersistedExecution:
        if decision.terminal_state is ExecutionState.SUCCESS:
            return await self._repository.complete_execution(
                execution.execution_id,
                expected_epoch=execution.epoch,
                tenant_id=execution.tenant_id,
            )
        if decision.terminal_state is ExecutionState.FAILED:
            return await self._repository.fail_execution(
                execution.execution_id,
                decision.diagnostic or "execution graph is unsatisfiable",
                expected_epoch=execution.epoch,
                tenant_id=execution.tenant_id,
            )
        raise ValueError("orchestration decision is not terminal")


def reduce_orchestration(
    flow: FlowDefinition,
    task_runs: list[PersistedTaskRun],
    *,
    now: datetime,
) -> OrchestrationDecision:
    """Reduce committed task state to one deterministic orchestration decision."""

    task_runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
    _require_matching_plan(flow, task_runs_by_id)
    failed = [
        task.id
        for task in flow.tasks
        if task_runs_by_id[task.id].state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
    ]
    if failed:
        blocked = [
            task.id
            for task in flow.tasks
            if task_runs_by_id[task.id].state is TaskRunState.WAITING
            and any(dependency in failed for dependency in task.depends_on)
        ]
        return OrchestrationDecision(
            terminal_state=ExecutionState.FAILED,
            diagnostic=(f"unsatisfiable execution graph; failed={failed}; blocked={blocked}"),
        )
    if task_runs and all(task_run.state is TaskRunState.SUCCESS for task_run in task_runs):
        return OrchestrationDecision(terminal_state=ExecutionState.SUCCESS)

    runnable = tuple(
        task.id
        for task in flow.tasks
        if _is_ready(task_runs_by_id[task.id], now)
        and all(
            task_runs_by_id[dependency].state is TaskRunState.SUCCESS
            for dependency in task.depends_on
        )
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
        f"{task.id}<-{','.join(task.depends_on) or 'condition'}"
        for task in flow.tasks
        if task_runs_by_id[task.id].state is not TaskRunState.SUCCESS
    ]
    return OrchestrationDecision(
        terminal_state=ExecutionState.FAILED,
        diagnostic=f"unsatisfiable execution graph; blocked={blocked}",
    )


def _expression_context(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    outputs: Mapping[str, dict[str, Any]],
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
        task=task.model_dump(mode="python", by_alias=True),
        taskrun={
            "id": str(task_run.task_run_id),
            "attempt": task_run.current_attempt,
            "state": task_run.state.value,
        },
        trigger=execution.trigger,
        inputs=execution.inputs,
        outputs=outputs,
        variables=flow.variables,
        labels=flow.labels,
        namespace={"id": flow.namespace},
    )


def _require_matching_plan(
    flow: FlowDefinition,
    task_runs_by_id: Mapping[str, PersistedTaskRun],
) -> None:
    expected = {task.id for task in flow.tasks}
    persisted = set(task_runs_by_id)
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


def _core_handlers() -> dict[str, TaskHandler]:
    return {
        "core.log": _run_core_log,
        "core.return": _run_core_return,
    }


async def _run_core_log(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> dict[str, Any]:
    extra = task.model_extra or {}
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
    return {"message": message}


async def _run_core_return(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> dict[str, Any]:
    del context
    extra = task.model_extra or {}
    return {"value": extra.get("value")}
