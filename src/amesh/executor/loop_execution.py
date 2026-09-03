from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from amesh.backoff import bounded_exponential_backoff
from amesh.dsl import FlowableFailurePolicy, FlowDefinition
from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionEngine
from amesh.ports import (
    ObjectStore,
    PersistedExecution,
    PersistedTaskDeferral,
    PersistedTaskRun,
    TaskRunState,
)

from .contracts import (
    LoopExecutionFailure,
    TaskConfigurationError,
    TaskResourceLimitError,
    TaskRunOutcome,
)
from .flowable_core import _expression_context, _template_visible_output_ids
from .loops import LoopItem, LoopIterationContext, LoopSpec, iter_foreach_items, parse_loop_spec
from .orchestration_core import _is_ready, _task_run_is_terminal


class LoopExecutionRepository(Protocol):
    async def task_attempt_started_at(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
    ) -> datetime: ...

    async def database_time(self) -> datetime: ...

    async def ensure_iteration_task_runs(
        self,
        execution_id: UUID,
        iteration_key: str,
        task_ids: tuple[str, ...],
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]: ...

    async def get_task_deferral(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedTaskDeferral | None: ...


class RunTask(Protocol):
    async def __call__(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task_run: PersistedTaskRun,
        task: TaskDefinition,
        outputs: Mapping[str, dict[str, Any]],
        workspace_parent: TaskDefinition | None = None,
        iteration: LoopIterationContext | None = None,
        handler_error: Mapping[str, Any] | None = None,
    ) -> TaskRunOutcome: ...


@dataclass(frozen=True)
class _LoopDependencies:
    repository: LoopExecutionRepository
    expressions: ExpressionEngine
    object_store: ObjectStore | None
    run_task: RunTask
    admission_poll_initial_seconds: float
    admission_poll_max_seconds: float


@dataclass(frozen=True)
class _LoopContext:
    flow: FlowDefinition
    execution: PersistedExecution
    parent_run: PersistedTaskRun
    task: TaskDefinition
    spec: LoopSpec
    upstream_outputs: Mapping[str, dict[str, Any]]
    started_at: datetime
    dependencies: _LoopDependencies


async def _require_capacity(context: _LoopContext, next_count: int) -> None:
    spec = context.spec
    task = context.task
    if next_count > spec.max_iterations:
        raise TaskResourceLimitError(
            f"loop {task.id!r} exceeded maxIterations={spec.max_iterations}"
        )
    if next_count * len(task.tasks) > spec.max_task_runs:
        raise TaskResourceLimitError(f"loop {task.id!r} exceeded maxTaskRuns={spec.max_task_runs}")
    database_now = await context.dependencies.repository.database_time()
    if (database_now - context.started_at).total_seconds() > spec.max_duration_seconds:
        raise TaskResourceLimitError(
            f"loop {task.id!r} exceeded maxDurationSeconds={spec.max_duration_seconds}"
        )


def evaluate_loop_condition(
    expressions: ExpressionEngine,
    expression: str,
    flow: FlowDefinition,
    execution: PersistedExecution,
    parent_run: PersistedTaskRun,
    task: TaskDefinition,
    outputs: Mapping[str, dict[str, Any]],
    iteration: LoopIterationContext,
) -> bool:
    return expressions.evaluate_condition(
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


async def _run_item(
    context: _LoopContext,
    item: LoopItem,
) -> tuple[dict[str, Any], bool, bool]:
    iteration = LoopIterationContext(
        index=item.index,
        key=item.key,
        value=item.value,
        parent={
            "taskId": context.task.id,
            "taskRunId": str(context.parent_run.task_run_id),
            "attempt": context.parent_run.current_attempt,
        },
    )
    if context.spec.continue_if is not None and evaluate_loop_condition(
        context.dependencies.expressions,
        context.spec.continue_if,
        context.flow,
        context.execution,
        context.parent_run,
        context.task,
        context.upstream_outputs,
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
    aggregate, child_outputs = await run_loop_iteration(
        context.flow,
        context.execution,
        context.task,
        iteration,
        context.upstream_outputs,
        repository=context.dependencies.repository,
        run_task=context.dependencies.run_task,
        admission_poll_initial_seconds=context.dependencies.admission_poll_initial_seconds,
        admission_poll_max_seconds=context.dependencies.admission_poll_max_seconds,
    )
    failed = aggregate["state"] == "FAILED"
    should_break = context.spec.break_if is not None and evaluate_loop_condition(
        context.dependencies.expressions,
        context.spec.break_if,
        context.flow,
        context.execution,
        context.parent_run,
        context.task,
        {**context.upstream_outputs, **child_outputs},
        iteration,
    )
    if should_break:
        aggregate["control"] = "BREAK"
    return aggregate, failed, should_break


def _collect_outcomes(
    context: _LoopContext,
    results: list[dict[str, Any]],
    outcomes: list[tuple[dict[str, Any], bool, bool]],
    collected_failure: bool,
) -> tuple[bool, bool]:
    stop = False
    for aggregate, failed, should_break in outcomes:
        results.append(aggregate)
        collected_failure = collected_failure or failed
        stop = (
            stop
            or should_break
            or (failed and context.task.failure_policy is FlowableFailurePolicy.FAIL_FAST)
        )
    return collected_failure, stop


async def _run_foreach(
    context: _LoopContext,
) -> tuple[list[dict[str, Any]], bool]:
    results: list[dict[str, Any]] = []
    collected_failure = False
    concurrency = context.task.max_concurrency or 1
    wave: list[LoopItem] = []
    stop = False
    async for item in iter_foreach_items(
        context.spec,
        tenant_id=context.execution.tenant_id,
        object_store=context.dependencies.object_store,
    ):
        await _require_capacity(context, item.index + 1)
        wave.append(item)
        if len(wave) < concurrency:
            continue
        outcomes = await asyncio.gather(*(_run_item(context, candidate) for candidate in wave))
        collected_failure, stop = _collect_outcomes(
            context,
            results,
            outcomes,
            collected_failure,
        )
        wave = []
        if stop:
            break
    if wave and not stop:
        outcomes = await asyncio.gather(*(_run_item(context, candidate) for candidate in wave))
        collected_failure, _ = _collect_outcomes(
            context,
            results,
            outcomes,
            collected_failure,
        )
    return results, collected_failure


def _iteration_context(
    task: TaskDefinition,
    parent_run: PersistedTaskRun,
    index: int,
    previous_outputs: Mapping[str, dict[str, Any]],
) -> LoopIterationContext:
    return LoopIterationContext(
        index=index,
        key=str(index),
        value=previous_outputs or None,
        parent={
            "taskId": task.id,
            "taskRunId": str(parent_run.task_run_id),
            "attempt": parent_run.current_attempt,
        },
    )


def _successful_child_outputs(aggregate: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        child_id: child["output"]
        for child_id, child in aggregate["children"].items()
        if child["state"] == TaskRunState.SUCCESS.value and isinstance(child["output"], dict)
    }


async def _run_conditional_loop(
    context: _LoopContext,
) -> tuple[list[dict[str, Any]], bool]:
    results: list[dict[str, Any]] = []
    collected_failure = False
    previous_outputs: dict[str, dict[str, Any]] = {}
    terminated = False
    for index in range(context.spec.max_iterations):
        await _require_capacity(context, index + 1)
        iteration = _iteration_context(context.task, context.parent_run, index, previous_outputs)
        visible_outputs = {**context.upstream_outputs, **previous_outputs}
        if context.task.type == "core.while" and not evaluate_loop_condition(
            context.dependencies.expressions,
            context.spec.condition or "",
            context.flow,
            context.execution,
            context.parent_run,
            context.task,
            visible_outputs,
            iteration,
        ):
            terminated = True
            break
        aggregate, failed, should_break = await _run_item(
            context,
            LoopItem(index=index, key=str(index), value=previous_outputs or None),
        )
        results.append(aggregate)
        collected_failure = collected_failure or failed
        previous_outputs = _successful_child_outputs(aggregate)
        if should_break or (
            failed and context.task.failure_policy is FlowableFailurePolicy.FAIL_FAST
        ):
            terminated = True
            break
        if context.task.type == "core.until" and evaluate_loop_condition(
            context.dependencies.expressions,
            context.spec.condition or "",
            context.flow,
            context.execution,
            context.parent_run,
            context.task,
            {**context.upstream_outputs, **previous_outputs},
            iteration,
        ):
            terminated = True
            break
    if not terminated:
        raise TaskResourceLimitError(
            f"loop {context.task.id!r} reached maxIterations={context.spec.max_iterations} "
            "before its condition terminated"
        )
    return results, collected_failure


async def run_loop(
    flow: FlowDefinition,
    execution: PersistedExecution,
    parent_run: PersistedTaskRun,
    task: TaskDefinition,
    upstream_outputs: Mapping[str, dict[str, Any]],
    *,
    repository: LoopExecutionRepository,
    expressions: ExpressionEngine,
    object_store: ObjectStore | None,
    run_task: RunTask,
    admission_poll_initial_seconds: float,
    admission_poll_max_seconds: float,
) -> dict[str, Any]:
    spec = parse_loop_spec(task)
    started_at = await repository.task_attempt_started_at(
        parent_run.task_run_id,
        parent_run.current_attempt,
        tenant_id=execution.tenant_id,
    )
    context = _LoopContext(
        flow=flow,
        execution=execution,
        parent_run=parent_run,
        task=task,
        spec=spec,
        upstream_outputs=upstream_outputs,
        started_at=started_at,
        dependencies=_LoopDependencies(
            repository=repository,
            expressions=expressions,
            object_store=object_store,
            run_task=run_task,
            admission_poll_initial_seconds=admission_poll_initial_seconds,
            admission_poll_max_seconds=admission_poll_max_seconds,
        ),
    )
    if task.type == "core.foreach":
        results, collected_failure = await _run_foreach(context)
    else:
        results, collected_failure = await _run_conditional_loop(context)
    result = await finalize_loop_result(
        execution,
        parent_run,
        task,
        spec,
        results,
        object_store=object_store,
    )
    if collected_failure and task.failure_policy in {
        FlowableFailurePolicy.FAIL_FAST,
        FlowableFailurePolicy.COLLECT_ALL,
    }:
        reason = f"loop {task.id!r} collected failed iterations"
        raise LoopExecutionFailure(reason, {**result, "error": reason})
    return result


def _iteration_outputs(
    runs_by_id: Mapping[str, PersistedTaskRun],
) -> dict[str, dict[str, Any]]:
    return {
        task_id: task_run.result or {}
        for task_id, task_run in runs_by_id.items()
        if task_run.state is TaskRunState.SUCCESS
    }


async def _ready_iteration_tasks(
    execution: PersistedExecution,
    pending: list[TaskDefinition],
    runs_by_id: Mapping[str, PersistedTaskRun],
    now: datetime,
    repository: LoopExecutionRepository,
) -> list[TaskDefinition]:
    ready: list[TaskDefinition] = []
    for task in pending:
        task_run = runs_by_id[task.id]
        if task_run.state is TaskRunState.RUNNING:
            deferral = await repository.get_task_deferral(
                task_run.task_run_id,
                tenant_id=execution.tenant_id,
            )
            if deferral is not None and deferral.state == "WAITING":
                continue
        elif not _is_ready(task_run, now):
            continue
        if all(
            runs_by_id[dependency].state is TaskRunState.SUCCESS for dependency in task.depends_on
        ):
            ready.append(task)
    return ready


def _iteration_aggregate(
    iteration: LoopIterationContext,
    task_ids: tuple[str, ...],
    runs_by_id: Mapping[str, PersistedTaskRun],
) -> dict[str, Any]:
    failed = any(
        task_run.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
        for task_run in runs_by_id.values()
    )
    return {
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
                    if runs_by_id[task_id].state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
                    else None
                ),
            }
            for task_id in task_ids
        },
    }


async def run_loop_iteration(
    flow: FlowDefinition,
    execution: PersistedExecution,
    loop_task: TaskDefinition,
    iteration: LoopIterationContext,
    upstream_outputs: Mapping[str, dict[str, Any]],
    *,
    repository: LoopExecutionRepository,
    run_task: RunTask,
    admission_poll_initial_seconds: float,
    admission_poll_max_seconds: float,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    iteration_key = f"{loop_task.id}:{iteration.index:08d}"
    task_ids = tuple(task.id for task in loop_task.tasks)
    task_runs = await repository.ensure_iteration_task_runs(
        execution.execution_id,
        iteration_key,
        task_ids,
        tenant_id=execution.tenant_id,
    )
    tasks_by_id = {task.id: task for task in loop_task.tasks}
    admission_wait_count = 0
    while True:
        runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
        outputs = _iteration_outputs(runs_by_id)
        pending = [
            task for task in loop_task.tasks if not _task_run_is_terminal(runs_by_id[task.id])
        ]
        if not pending:
            break
        ready = await _ready_iteration_tasks(
            execution,
            pending,
            runs_by_id,
            await repository.database_time(),
            repository,
        )
        if not ready:
            if any(
                task_run.state in {TaskRunState.RUNNING, TaskRunState.RETRY_DELAY}
                for task_run in runs_by_id.values()
            ):
                admission_wait_count += 1
                await asyncio.sleep(
                    bounded_exponential_backoff(
                        admission_poll_initial_seconds,
                        admission_poll_max_seconds,
                        admission_wait_count,
                    )
                )
                task_runs = await repository.ensure_iteration_task_runs(
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
                run_task(
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
        task_runs = await repository.ensure_iteration_task_runs(
            execution.execution_id,
            iteration_key,
            task_ids,
            tenant_id=execution.tenant_id,
        )
    runs_by_id = {task_run.task_id: task_run for task_run in task_runs}
    return _iteration_aggregate(iteration, task_ids, runs_by_id), _iteration_outputs(runs_by_id)


async def finalize_loop_result(
    execution: PersistedExecution,
    parent_run: PersistedTaskRun,
    task: TaskDefinition,
    spec: LoopSpec,
    results: list[dict[str, Any]],
    *,
    object_store: ObjectStore | None,
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
    if object_store is None:
        raise TaskConfigurationError(
            f"loop {task.id!r} produced {len(encoded)} bytes and requires an object store"
        )

    async def chunks() -> Any:
        yield encoded

    metadata = await object_store.put(
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
