from __future__ import annotations

import asyncio
from collections.abc import Mapping
from contextlib import suppress
from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.backoff import bounded_exponential_backoff
from amesh.domain import ExecutionState, FailureCategory
from amesh.dsl import (
    FlowDefinition,
    PlannedTask,
    compile_execution_tasks,
    compile_flow_tasks,
    visible_output_ids,
)
from amesh.dsl.models import TaskDefinition
from amesh.ports import (
    ExecutionRepository,
    PersistedExecution,
    PersistedTaskRun,
    TaskRunState,
    TaskStateConflictError,
)

from .contracts import (
    ExecutionBlockedError,
    ExecutionProgress,
    OrchestrationDecision,
    TaskExecutionError,
    TaskRunOutcome,
)
from .loops import LoopIterationContext
from .orchestration_core import (
    _lifecycle_plan,
    _main_task_runs,
    _select_ready_tasks,
    _working_directory_ancestor,
    execution_lifecycle_pending,
    reduce_orchestration,
)


class ExecutionRuntime(Protocol):
    """Narrow runtime surface required by top-level execution orchestration."""

    _repository: ExecutionRepository
    _recover_running_types: frozenset[str]
    _admission_poll_initial_seconds: float
    _admission_poll_max_seconds: float

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
    ) -> ExecutionProgress: ...

    async def _advance_flowables(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        plan: tuple[PlannedTask, ...],
        task_runs: list[PersistedTaskRun],
        *,
        tenant_id: str,
        handler_errors: Mapping[str, Mapping[str, object]] | None = None,
    ) -> list[PersistedTaskRun]: ...

    async def _run_task(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task_run: PersistedTaskRun,
        task: TaskDefinition,
        outputs: Mapping[str, dict[str, object]],
        workspace_parent: TaskDefinition | None = None,
        iteration: LoopIterationContext | None = None,
        handler_error: Mapping[str, object] | None = None,
    ) -> TaskRunOutcome: ...

    async def _finish_execution(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        decision: OrchestrationDecision,
        task_runs: list[PersistedTaskRun],
    ) -> PersistedExecution: ...

    async def _has_waiting_deferral(
        self,
        task_runs: tuple[PersistedTaskRun, ...],
        tenant_id: str,
    ) -> bool: ...

    async def run_ready(
        self,
        flow: FlowDefinition,
        execution_id: UUID,
        *,
        tenant_id: str,
        max_tasks: int | None = None,
    ) -> ExecutionProgress: ...


async def run_ready(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution_id: UUID,
    *,
    tenant_id: str,
    max_tasks: int | None = None,
) -> ExecutionProgress:
    """Advance one execution wave from committed repository state."""

    if max_tasks is not None and max_tasks < 1:
        raise ValueError("max_tasks must be at least 1")
    execution = await runtime._repository.get_execution(execution_id, tenant_id=tenant_id)
    task_runs = await runtime._repository.list_task_runs(execution_id, tenant_id=tenant_id)
    execution_plan = compile_execution_tasks(flow)
    if execution.state is not ExecutionState.RUNNING:
        return await _nonrunning_progress(
            runtime,
            flow,
            execution,
            execution_plan,
            task_runs,
            max_tasks=max_tasks,
        )
    now = await runtime._repository.database_time()
    timed_out = await _timeout_progress(
        runtime,
        flow,
        execution,
        execution_plan,
        task_runs,
        now=now,
        max_tasks=max_tasks,
    )
    if timed_out is not None:
        return timed_out
    task_runs, deferred_ids = await _expire_deferrals(
        runtime,
        execution,
        task_runs,
        now=now,
    )
    plan = compile_flow_tasks(flow)
    task_runs = await runtime._advance_flowables(
        flow,
        execution,
        plan,
        task_runs,
        tenant_id=tenant_id,
    )
    decision = reduce_orchestration(flow, _main_task_runs(task_runs), now=now)
    terminal = await _terminal_progress(
        runtime,
        flow,
        execution,
        execution_plan,
        task_runs,
        decision,
        max_tasks=max_tasks,
    )
    if terminal is not None:
        return terminal
    outcomes = await _run_ready_wave(
        runtime,
        flow,
        execution,
        plan,
        task_runs,
        decision,
        deferred_ids,
        now=now,
        max_tasks=max_tasks,
    )
    return await _refresh_after_wave(
        runtime,
        flow,
        execution,
        execution_plan,
        plan,
        outcomes,
        max_tasks=max_tasks,
    )


async def _nonrunning_progress(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution: PersistedExecution,
    execution_plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    *,
    max_tasks: int | None,
) -> ExecutionProgress:
    if execution_lifecycle_pending(flow, execution, task_runs):
        return await runtime._advance_execution_lifecycle(
            flow,
            execution,
            execution_plan,
            task_runs,
            primary_decision=None,
            max_tasks=max_tasks,
        )
    return ExecutionProgress(
        execution_id=execution.execution_id,
        state=execution.state,
        tasks_run=0,
        task_runs=tuple(task_runs),
    )


async def _timeout_progress(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution: PersistedExecution,
    execution_plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    *,
    now: datetime,
    max_tasks: int | None,
) -> ExecutionProgress | None:
    if execution.timeout_at is None or now < execution.timeout_at:
        return None
    timed_out = await runtime._repository.timeout_execution(
        execution.execution_id,
        tenant_id=execution.tenant_id,
        expected_epoch=execution.epoch,
    )
    timed_out_runs = await runtime._repository.list_task_runs(
        execution.execution_id,
        tenant_id=execution.tenant_id,
    )
    if execution_lifecycle_pending(flow, timed_out, timed_out_runs):
        return await runtime._advance_execution_lifecycle(
            flow,
            timed_out,
            execution_plan,
            timed_out_runs,
            primary_decision=None,
            max_tasks=max_tasks,
        )
    return ExecutionProgress(
        execution_id=execution.execution_id,
        state=timed_out.state,
        tasks_run=0,
        task_runs=tuple(timed_out_runs),
    )


async def _expire_deferrals(
    runtime: ExecutionRuntime,
    execution: PersistedExecution,
    task_runs: list[PersistedTaskRun],
    *,
    now: datetime,
) -> tuple[list[PersistedTaskRun], set[UUID]]:
    deferred_ids: set[UUID] = set()
    expired = False
    for task_run in task_runs:
        if task_run.state is not TaskRunState.RUNNING:
            continue
        deferral = await runtime._repository.get_task_deferral(
            task_run.task_run_id,
            tenant_id=execution.tenant_id,
        )
        if deferral is None:
            continue
        is_expired = deferral.state == "EXPIRED" or (
            deferral.state == "WAITING"
            and deferral.expires_at is not None
            and now >= deferral.expires_at
        )
        if is_expired:
            with suppress(TaskStateConflictError):
                await runtime._repository.fail_task(
                    task_run.task_run_id,
                    deferral.attempt,
                    "asynchronous task deferral expired",
                    tenant_id=execution.tenant_id,
                    failure_category=FailureCategory.TIMED_OUT,
                )
            expired = True
        elif deferral.state == "WAITING":
            deferred_ids.add(task_run.task_run_id)
    if expired:
        task_runs = await runtime._repository.list_task_runs(
            execution.execution_id,
            tenant_id=execution.tenant_id,
        )
    return task_runs, deferred_ids


async def _terminal_progress(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution: PersistedExecution,
    execution_plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    decision: OrchestrationDecision,
    *,
    max_tasks: int | None,
) -> ExecutionProgress | None:
    if decision.terminal_state is None:
        return None
    if _lifecycle_plan(execution_plan):
        return await runtime._advance_execution_lifecycle(
            flow,
            execution,
            execution_plan,
            task_runs,
            primary_decision=decision,
            max_tasks=max_tasks,
        )
    finished = await runtime._finish_execution(flow, execution, decision, task_runs)
    return ExecutionProgress(
        execution_id=execution.execution_id,
        state=finished.state,
        tasks_run=0,
        task_runs=tuple(task_runs),
    )


async def _run_ready_wave(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution: PersistedExecution,
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    decision: OrchestrationDecision,
    deferred_ids: set[UUID],
    *,
    now: datetime,
    max_tasks: int | None,
) -> tuple[TaskRunOutcome, ...]:
    by_id = {task_run.task_id: task_run for task_run in task_runs}
    ready = _select_ready_tasks(
        plan,
        by_id,
        set(decision.runnable_task_ids),
        runtime._recover_running_types,
        deferred_ids,
        max_tasks=max_tasks,
    )
    outputs = {
        task_id: task_run.result or {}
        for task_id, task_run in by_id.items()
        if task_run.state is TaskRunState.SUCCESS
    }
    plan_by_id = {node.task.id: node for node in plan}
    coroutines = tuple(
        runtime._run_task(
            flow,
            execution,
            by_id[node.task.id],
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
            return tuple(await asyncio.gather(*coroutines))
        remaining = max((execution.timeout_at - now).total_seconds(), 0)
        async with asyncio.timeout(remaining):
            return tuple(await asyncio.gather(*coroutines))
    except TimeoutError as exc:
        await runtime._repository.timeout_execution(
            execution.execution_id,
            tenant_id=execution.tenant_id,
            expected_epoch=execution.epoch,
        )
        raise TaskExecutionError("execution deadline exceeded") from exc


async def _refresh_after_wave(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution: PersistedExecution,
    execution_plan: tuple[PlannedTask, ...],
    plan: tuple[PlannedTask, ...],
    outcomes: tuple[TaskRunOutcome, ...],
    *,
    max_tasks: int | None,
) -> ExecutionProgress:
    task_runs = await runtime._repository.list_task_runs(
        execution.execution_id,
        tenant_id=execution.tenant_id,
    )
    task_runs = await runtime._advance_flowables(
        flow,
        execution,
        plan,
        task_runs,
        tenant_id=execution.tenant_id,
    )
    decision = reduce_orchestration(
        flow,
        _main_task_runs(task_runs),
        now=await runtime._repository.database_time(),
    )
    claimed = sum(outcome.claimed for outcome in outcomes)
    failure = next((outcome.failure for outcome in outcomes if outcome.failure), None)
    if decision.terminal_state is not None and _lifecycle_plan(execution_plan):
        return await runtime._advance_execution_lifecycle(
            flow,
            execution,
            execution_plan,
            task_runs,
            primary_decision=decision,
            max_tasks=max_tasks,
            claimed_tasks=claimed,
            primary_failure=failure,
        )
    if decision.terminal_state is not None:
        execution = await runtime._finish_execution(flow, execution, decision, task_runs)
    else:
        execution = await runtime._repository.get_execution(
            execution.execution_id,
            tenant_id=execution.tenant_id,
        )
    progress = ExecutionProgress(
        execution_id=execution.execution_id,
        state=execution.state,
        tasks_run=claimed,
        task_runs=tuple(task_runs),
    )
    if failure is not None and decision.terminal_state is not None:
        raise TaskExecutionError(decision.diagnostic or failure)
    return progress


async def run_to_completion(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution_id: UUID,
    *,
    tenant_id: str,
) -> ExecutionProgress:
    """Run committed waves until terminal, deferred or externally owned work remains."""

    admission_wait_count = 0
    while True:
        progress = await runtime.run_ready(flow, execution_id, tenant_id=tenant_id)
        terminal = await _require_success_or_continue(
            runtime,
            flow,
            execution_id,
            tenant_id,
            progress,
        )
        if terminal is not None:
            if terminal:
                continue
            return progress
        if progress.tasks_run:
            admission_wait_count = 0
            continue
        wait_action = await _idle_wait_action(runtime, flow, progress, tenant_id=tenant_id)
        if wait_action == "RETURN":
            return progress
        if wait_action == "RETRY":
            continue
        if wait_action == "ADMISSION":
            admission_wait_count += 1
            await asyncio.sleep(
                bounded_exponential_backoff(
                    runtime._admission_poll_initial_seconds,
                    runtime._admission_poll_max_seconds,
                    admission_wait_count,
                )
            )
            continue
        waiting = [
            task_run.task_id
            for task_run in progress.task_runs
            if task_run.state is TaskRunState.WAITING
        ]
        raise ExecutionBlockedError(
            f"execution {execution_id} has no runnable tasks; waiting={waiting}"
        )


async def _require_success_or_continue(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    execution_id: UUID,
    tenant_id: str,
    progress: ExecutionProgress,
) -> bool | None:
    if progress.state is ExecutionState.RUNNING:
        return None
    execution = await runtime._repository.get_execution(execution_id, tenant_id=tenant_id)
    if execution_lifecycle_pending(flow, execution, list(progress.task_runs)):
        return True
    if progress.state is ExecutionState.SUCCESS:
        return False
    raise ExecutionBlockedError(f"execution {execution_id} stopped in state {progress.state.value}")


async def _idle_wait_action(
    runtime: ExecutionRuntime,
    flow: FlowDefinition,
    progress: ExecutionProgress,
    *,
    tenant_id: str,
) -> str:
    if any(task_run.state is TaskRunState.RUNNING for task_run in progress.task_runs):
        await runtime._has_waiting_deferral(progress.task_runs, tenant_id)
        return "RETURN"
    retry_at = min(
        (
            task_run.retry_at
            for task_run in progress.task_runs
            if task_run.state is TaskRunState.RETRY_DELAY and task_run.retry_at is not None
        ),
        default=None,
    )
    if retry_at is not None:
        database_now = await runtime._repository.database_time()
        delay_seconds = max((retry_at - database_now).total_seconds(), 0)
        await asyncio.sleep(min(delay_seconds, 1))
        return "RETRY"
    waiting = {
        task_run.task_id
        for task_run in progress.task_runs
        if task_run.state is TaskRunState.WAITING
    }
    if any(
        node.task.concurrency and node.task.id in waiting
        for node in compile_flow_tasks(flow)
        if not node.flowable
    ):
        return "ADMISSION"
    return "BLOCKED"
