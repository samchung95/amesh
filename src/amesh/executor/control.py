from __future__ import annotations

from datetime import datetime

from amesh.domain import ExecutionState, TaskRunState
from amesh.dsl import FlowDefinition
from amesh.ports import (
    ExecutionInterventionAction,
    ExecutionInterventionPreview,
    PersistedExecution,
    PersistedTaskRun,
)


def preview_execution_intervention(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_runs: list[PersistedTaskRun],
    action: ExecutionInterventionAction,
    *,
    checkpoint_task_id: str | None = None,
    now: datetime,
) -> ExecutionInterventionPreview:
    """Validate an operator action and return its state/task consequences."""

    by_id = {task_run.task_id: task_run for task_run in task_runs}
    task_ids = tuple(task.id for task in flow.tasks)
    if set(by_id) != set(task_ids):
        raise ValueError("persisted task runs do not match the active execution revision")

    if action is ExecutionInterventionAction.PAUSE:
        _require_state(execution, action, {ExecutionState.RUNNING})
        return _preview(
            execution,
            action,
            ExecutionState.PAUSED,
            impacted=_nonterminal(task_ids, by_id),
            preserved=tuple(
                task_id for task_id in task_ids if by_id[task_id].state is TaskRunState.SUCCESS
            ),
            consequences=(
                "No new task runs will be admitted while paused.",
                "Completed work and live in-flight attempts are preserved.",
            ),
        )
    if action is ExecutionInterventionAction.RESUME:
        _require_state(execution, action, {ExecutionState.PAUSED})
        return _preview(
            execution,
            action,
            ExecutionState.RUNNING,
            consequences=("Dependency-ready work may be admitted again.",),
        )
    if action is ExecutionInterventionAction.REQUEST_CANCEL:
        _require_state(
            execution,
            action,
            {ExecutionState.RUNNING, ExecutionState.PAUSED, ExecutionState.QUEUED},
        )
        return _preview(
            execution,
            action,
            ExecutionState.CANCELLING,
            impacted=_nonterminal(task_ids, by_id),
            consequences=(
                "Waiting and delayed-retry tasks will be cancelled immediately.",
                "Running attempts receive a graceful cancellation request before escalation.",
            ),
        )
    if action in {
        ExecutionInterventionAction.CONFIRM_CANCEL,
        ExecutionInterventionAction.FORCE_CANCEL,
    }:
        _require_state(execution, action, {ExecutionState.CANCELLING})
        force_available_at = execution.cancel_deadline_at
        if (
            action is ExecutionInterventionAction.FORCE_CANCEL
            and force_available_at is not None
            and now < force_available_at
        ):
            timing = f"Force termination becomes available at {force_available_at.isoformat()}."
        else:
            timing = "The cancellation can be finalized now."
        return _preview(
            execution,
            action,
            ExecutionState.CANCELLED,
            impacted=_nonterminal(task_ids, by_id),
            invalidates=True,
            destructive=True,
            force_available_at=force_available_at,
            consequences=(
                timing,
                "Active task leases and fencing tokens will be invalidated.",
                "Completed task results remain immutable history.",
            ),
        )
    if action is ExecutionInterventionAction.RESTART:
        _require_state(
            execution,
            action,
            {ExecutionState.FAILED, ExecutionState.CANCELLED, ExecutionState.WARNING},
        )
        impacted = _restart_scope(flow, checkpoint_task_id)
        invalid_terminal = tuple(
            task_id
            for task_id, task_run in by_id.items()
            if task_run.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
            and task_id not in impacted
        )
        if invalid_terminal:
            raise ValueError(
                "restart checkpoint excludes failed or cancelled tasks: "
                + ", ".join(invalid_terminal)
            )
        preserved = tuple(
            task_id
            for task_id in task_ids
            if task_id not in impacted and by_id[task_id].state is TaskRunState.SUCCESS
        )
        return _preview(
            execution,
            action,
            ExecutionState.RUNNING,
            checkpoint_task_id=checkpoint_task_id,
            impacted=impacted,
            preserved=preserved,
            invalidates=True,
            destructive=True,
            consequences=(
                "The execution epoch will advance and old worker results will be rejected.",
                "Impacted task runs return to WAITING while prior attempts remain history.",
                "Successful tasks outside the restart scope keep their committed outputs.",
            ),
        )
    raise ValueError(f"unsupported execution intervention {action.value}")


def _preview(
    execution: PersistedExecution,
    action: ExecutionInterventionAction,
    predicted_state: ExecutionState,
    *,
    checkpoint_task_id: str | None = None,
    impacted: tuple[str, ...] = (),
    preserved: tuple[str, ...] = (),
    invalidates: bool = False,
    destructive: bool = False,
    force_available_at: datetime | None = None,
    consequences: tuple[str, ...] = (),
) -> ExecutionInterventionPreview:
    return ExecutionInterventionPreview(
        execution_id=execution.execution_id,
        action=action,
        current_state=execution.state,
        predicted_state=predicted_state,
        current_version=execution.version,
        current_epoch=execution.epoch,
        checkpoint_task_id=checkpoint_task_id,
        impacted_task_ids=impacted,
        preserved_task_ids=preserved,
        invalidates_active_claims=invalidates,
        destructive=destructive,
        force_available_at=force_available_at,
        consequences=consequences,
    )


def _require_state(
    execution: PersistedExecution,
    action: ExecutionInterventionAction,
    allowed: set[ExecutionState],
) -> None:
    if execution.state not in allowed:
        expected = ", ".join(sorted(state.value for state in allowed))
        raise ValueError(
            f"{action.value} is not available from {execution.state.value}; expected {expected}"
        )


def _nonterminal(
    task_ids: tuple[str, ...],
    by_id: dict[str, PersistedTaskRun],
) -> tuple[str, ...]:
    return tuple(
        task_id
        for task_id in task_ids
        if by_id[task_id].state
        not in {TaskRunState.SUCCESS, TaskRunState.FAILED, TaskRunState.CANCELLED}
    )


def _restart_scope(flow: FlowDefinition, checkpoint_task_id: str | None) -> tuple[str, ...]:
    task_ids = tuple(task.id for task in flow.tasks)
    if checkpoint_task_id is None:
        return task_ids
    if checkpoint_task_id not in task_ids:
        raise ValueError(f"restart checkpoint task {checkpoint_task_id!r} does not exist")
    impacted = {checkpoint_task_id}
    changed = True
    while changed:
        changed = False
        for task in flow.tasks:
            if task.id not in impacted and any(parent in impacted for parent in task.depends_on):
                impacted.add(task.id)
                changed = True
    return tuple(task_id for task_id in task_ids if task_id in impacted)
