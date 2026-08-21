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
from amesh.ports import ExecutionRepository, PersistedExecution, PersistedTaskRun, TaskRunState

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
    ) -> UUID:
        if flow.disabled:
            raise ValueError(f"flow {flow.namespace}.{flow.id} is disabled")
        execution = await self._repository.create_execution(
            flow,
            tenant_id=tenant_id,
            inputs=inputs or {},
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

        task_runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
        _require_matching_plan(flow, task_runs_by_id)
        now = datetime.now(UTC)
        ready = [
            task
            for task in flow.tasks
            if (
                _is_ready(task_runs_by_id[task.id], now)
                or (
                    task_runs_by_id[task.id].state is TaskRunState.RUNNING
                    and task.type in self._recover_running_types
                )
            )
            and all(
                task_runs_by_id[dependency].state is TaskRunState.SUCCESS
                for dependency in task.depends_on
            )
        ]
        if max_tasks is not None:
            ready = ready[:max_tasks]

        outputs = {
            task_id: task_run.result or {}
            for task_id, task_run in task_runs_by_id.items()
            if task_run.state is TaskRunState.SUCCESS
        }
        await asyncio.gather(
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
        if updated_task_runs and all(
            task_run.state is TaskRunState.SUCCESS for task_run in updated_task_runs
        ):
            execution = await self._repository.complete_execution(
                execution_id,
                expected_epoch=execution.epoch,
                tenant_id=tenant_id,
            )
        else:
            execution = await self._repository.get_execution(
                execution_id,
                tenant_id=tenant_id,
            )
        return ExecutionProgress(
            execution_id=execution_id,
            state=execution.state,
            tasks_run=len(ready),
            task_runs=tuple(updated_task_runs),
        )

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
    ) -> None:
        tenant_id = execution.tenant_id
        execution_id = execution.execution_id
        running = (
            task_run
            if task_run.state is TaskRunState.RUNNING
            else await self._repository.start_task(
                task_run.task_run_id,
                tenant_id=tenant_id,
            )
        )
        handler = self._handlers.get(task.type)
        if handler is None:
            reason = f"no in-process handler registered for task type {task.type!r}"
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
            )
            await self._repository.fail_execution(
                execution_id,
                reason,
                expected_epoch=execution.epoch,
                tenant_id=tenant_id,
            )
            raise TaskExecutionError(reason)
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
            expression_context = ExpressionContext(
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
                    "id": str(running.task_run_id),
                    "attempt": running.current_attempt,
                    "state": running.state.value,
                },
                trigger=execution.trigger,
                inputs=execution.inputs,
                outputs=outputs,
                variables=flow.variables,
                labels=flow.labels,
                namespace={"id": flow.namespace},
            )
            if task.run_if is not None and not self._expressions.evaluate_condition(
                task.run_if,
                expression_context,
            ):
                result = {"skipped": True}
            else:
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
                return
            await self._repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
            )
            await self._repository.fail_execution(
                execution_id,
                reason,
                expected_epoch=execution.epoch,
                tenant_id=tenant_id,
            )
            raise TaskExecutionError(reason) from exc
        await self._repository.complete_task(
            running.task_run_id,
            running.current_attempt,
            result,
            tenant_id=tenant_id,
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
