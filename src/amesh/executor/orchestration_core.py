from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from amesh.domain import ExecutionState, FailureCategory
from amesh.dsl import (
    FlowableFailurePolicy,
    FlowDefinition,
    LifecyclePhase,
    PlannedTask,
    compile_execution_tasks,
    compile_flow_tasks,
)
from amesh.dsl.models import TaskDefinition
from amesh.ports import PersistedExecution, PersistedTaskRun, TaskRunState

from .contracts import ExecutionBlockedError, OrchestrationDecision
from .flowable_core import _descends_from


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
