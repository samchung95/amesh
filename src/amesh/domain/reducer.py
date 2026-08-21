from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .execution import (
    ExecutionCommand,
    ExecutionCommandType,
    ExecutionEvent,
    ExecutionEventType,
    ExecutionSnapshot,
    ExecutionState,
    ExecutionTransition,
    InvalidTransition,
    TaskRunCommand,
    TaskRunCommandType,
    TaskRunEvent,
    TaskRunEventType,
    TaskRunSnapshot,
    TaskRunState,
    TaskRunTransition,
    TransitionRejection,
    TransitionRejectionCode,
    UnsupportedEventSchema,
)

_TRANSITIONS: dict[tuple[ExecutionState, ExecutionEventType], ExecutionState] = {
    (ExecutionState.CREATED, ExecutionEventType.CREATED): ExecutionState.CREATED,
    (ExecutionState.CREATED, ExecutionEventType.QUEUED): ExecutionState.QUEUED,
    (ExecutionState.QUEUED, ExecutionEventType.STARTED): ExecutionState.RUNNING,
    (ExecutionState.RUNNING, ExecutionEventType.PAUSED): ExecutionState.PAUSED,
    (ExecutionState.PAUSED, ExecutionEventType.RESUMED): ExecutionState.RUNNING,
    (ExecutionState.RUNNING, ExecutionEventType.CANCEL_REQUESTED): ExecutionState.CANCELLING,
    (ExecutionState.PAUSED, ExecutionEventType.CANCEL_REQUESTED): ExecutionState.CANCELLING,
    (ExecutionState.QUEUED, ExecutionEventType.CANCEL_REQUESTED): ExecutionState.CANCELLING,
    (ExecutionState.CANCELLING, ExecutionEventType.CANCELLED): ExecutionState.CANCELLED,
    (ExecutionState.RUNNING, ExecutionEventType.SUCCEEDED): ExecutionState.SUCCESS,
    (ExecutionState.RUNNING, ExecutionEventType.FAILED): ExecutionState.FAILED,
    (ExecutionState.RUNNING, ExecutionEventType.WARNED): ExecutionState.WARNING,
    (ExecutionState.FAILED, ExecutionEventType.RESTART_REQUESTED): ExecutionState.RESTARTING,
    (ExecutionState.CANCELLED, ExecutionEventType.RESTART_REQUESTED): ExecutionState.RESTARTING,
    (ExecutionState.WARNING, ExecutionEventType.RESTART_REQUESTED): ExecutionState.RESTARTING,
    (ExecutionState.RESTARTING, ExecutionEventType.STARTED): ExecutionState.RUNNING,
}

_COMMAND_EVENTS: dict[ExecutionCommandType, ExecutionEventType] = {
    ExecutionCommandType.CREATE: ExecutionEventType.CREATED,
    ExecutionCommandType.QUEUE: ExecutionEventType.QUEUED,
    ExecutionCommandType.START: ExecutionEventType.STARTED,
    ExecutionCommandType.PAUSE: ExecutionEventType.PAUSED,
    ExecutionCommandType.RESUME: ExecutionEventType.RESUMED,
    ExecutionCommandType.REQUEST_CANCEL: ExecutionEventType.CANCEL_REQUESTED,
    ExecutionCommandType.CONFIRM_CANCEL: ExecutionEventType.CANCELLED,
    ExecutionCommandType.SUCCEED: ExecutionEventType.SUCCEEDED,
    ExecutionCommandType.FAIL: ExecutionEventType.FAILED,
    ExecutionCommandType.WARN: ExecutionEventType.WARNED,
    ExecutionCommandType.REQUEST_RESTART: ExecutionEventType.RESTART_REQUESTED,
}

_TASK_TRANSITIONS: dict[tuple[TaskRunState, TaskRunEventType], TaskRunState] = {
    (TaskRunState.WAITING, TaskRunEventType.CREATED): TaskRunState.WAITING,
    (TaskRunState.WAITING, TaskRunEventType.STARTED): TaskRunState.RUNNING,
    (TaskRunState.RETRY_DELAY, TaskRunEventType.STARTED): TaskRunState.RUNNING,
    (TaskRunState.RUNNING, TaskRunEventType.RETRY_SCHEDULED): TaskRunState.RETRY_DELAY,
    (TaskRunState.RUNNING, TaskRunEventType.DEFERRED): TaskRunState.RUNNING,
    (TaskRunState.RUNNING, TaskRunEventType.SUCCEEDED): TaskRunState.SUCCESS,
    (TaskRunState.RUNNING, TaskRunEventType.FAILED): TaskRunState.FAILED,
    (TaskRunState.WAITING, TaskRunEventType.CANCELLED): TaskRunState.CANCELLED,
    (TaskRunState.RUNNING, TaskRunEventType.CANCELLED): TaskRunState.CANCELLED,
    (TaskRunState.RETRY_DELAY, TaskRunEventType.CANCELLED): TaskRunState.CANCELLED,
    (TaskRunState.SUCCESS, TaskRunEventType.RESTARTED): TaskRunState.WAITING,
    (TaskRunState.FAILED, TaskRunEventType.RESTARTED): TaskRunState.WAITING,
    (TaskRunState.CANCELLED, TaskRunEventType.RESTARTED): TaskRunState.WAITING,
}

_TASK_COMMAND_EVENTS: dict[TaskRunCommandType, TaskRunEventType] = {
    TaskRunCommandType.CREATE: TaskRunEventType.CREATED,
    TaskRunCommandType.START: TaskRunEventType.STARTED,
    TaskRunCommandType.SCHEDULE_RETRY: TaskRunEventType.RETRY_SCHEDULED,
    TaskRunCommandType.SUCCEED: TaskRunEventType.SUCCEEDED,
    TaskRunCommandType.FAIL: TaskRunEventType.FAILED,
    TaskRunCommandType.CANCEL: TaskRunEventType.CANCELLED,
    TaskRunCommandType.RESTART: TaskRunEventType.RESTARTED,
}


def reduce_execution(snapshot: ExecutionSnapshot, event: ExecutionEvent) -> ExecutionSnapshot:
    """Apply one immutable event.

    Duplicate event IDs are idempotent. All other illegal transitions raise without mutating the input.
    The function has no I/O and is safe to replay.
    """

    if (
        event.event_id in snapshot.applied_event_ids
        or event.deduplication_key in snapshot.applied_idempotency_keys
    ):
        return snapshot

    key = (snapshot.state, event.event_type)
    next_state = _TRANSITIONS.get(key)
    if next_state is None:
        raise InvalidTransition(
            f"{event.event_type.value} is not legal from {snapshot.state.value}"
        )

    next_epoch = snapshot.epoch
    if event.event_type is ExecutionEventType.RESTART_REQUESTED:
        next_epoch += 1

    return snapshot.model_copy(
        update={
            "state": next_state,
            "version": snapshot.version + 1,
            "epoch": next_epoch,
            "applied_event_ids": (*snapshot.applied_event_ids, event.event_id),
            "applied_idempotency_keys": (
                *snapshot.applied_idempotency_keys,
                event.deduplication_key,
            ),
            "last_event_at": event.occurred_at,
        }
    )


def reduce_task_run(snapshot: TaskRunSnapshot, event: TaskRunEvent) -> TaskRunSnapshot:
    """Apply one immutable task-run event without I/O."""

    if (
        event.event_id in snapshot.applied_event_ids
        or event.deduplication_key in snapshot.applied_idempotency_keys
    ):
        return snapshot
    next_state = _TASK_TRANSITIONS.get((snapshot.state, event.event_type))
    if next_state is None:
        raise InvalidTransition(
            f"{event.event_type.value} is not legal from {snapshot.state.value}"
        )
    attempt = snapshot.current_attempt
    if event.event_type is TaskRunEventType.STARTED:
        attempt += 1
    return snapshot.model_copy(
        update={
            "state": next_state,
            "current_attempt": attempt,
            "version": snapshot.version + 1,
            "applied_event_ids": (*snapshot.applied_event_ids, event.event_id),
            "applied_idempotency_keys": (
                *snapshot.applied_idempotency_keys,
                event.deduplication_key,
            ),
            "last_event_at": event.occurred_at,
        }
    )


def decide_execution(snapshot: ExecutionSnapshot, command: ExecutionCommand) -> ExecutionTransition:
    """Turn a typed command into one accepted event or deterministic rejection evidence."""

    if command.idempotency_key in snapshot.applied_idempotency_keys:
        return ExecutionTransition(snapshot=snapshot, duplicate=True)
    if command.expected_version is not None and command.expected_version != snapshot.version:
        return _reject(snapshot, command, TransitionRejectionCode.VERSION_CONFLICT)
    if command.expected_epoch is not None and command.expected_epoch != snapshot.epoch:
        return _reject(snapshot, command, TransitionRejectionCode.EPOCH_CONFLICT)
    event = ExecutionEvent(
        event_id=command.command_id,
        event_type=_COMMAND_EVENTS[command.command_type],
        idempotency_key=command.idempotency_key,
        occurred_at=command.submitted_at,
        correlation_id=command.correlation_id,
        causation_id=command.causation_id,
        actor_id=command.actor_id,
        reason=command.reason,
        payload=command.payload,
    )
    try:
        updated = reduce_execution(snapshot, event)
    except InvalidTransition:
        return _reject(snapshot, command, TransitionRejectionCode.ILLEGAL_TRANSITION)
    return ExecutionTransition(snapshot=updated, events=(event,))


def decide_task_run(snapshot: TaskRunSnapshot, command: TaskRunCommand) -> TaskRunTransition:
    """Turn a typed task-run command into one accepted event or rejection evidence."""

    if command.idempotency_key in snapshot.applied_idempotency_keys:
        return TaskRunTransition(snapshot=snapshot, duplicate=True)
    if command.expected_version is not None and command.expected_version != snapshot.version:
        return _reject_task(snapshot, command, TransitionRejectionCode.VERSION_CONFLICT)
    event = TaskRunEvent(
        event_id=command.command_id,
        event_type=_TASK_COMMAND_EVENTS[command.command_type],
        idempotency_key=command.idempotency_key,
        occurred_at=command.submitted_at,
        correlation_id=command.correlation_id,
        causation_id=command.causation_id,
        actor_id=command.actor_id,
        reason=command.reason,
        payload=command.payload,
    )
    try:
        updated = reduce_task_run(snapshot, event)
    except InvalidTransition:
        return _reject_task(snapshot, command, TransitionRejectionCode.ILLEGAL_TRANSITION)
    return TaskRunTransition(snapshot=updated, events=(event,))


def replay_execution(
    initial: ExecutionSnapshot,
    events: Iterable[ExecutionEvent | Mapping[str, Any]],
) -> ExecutionSnapshot:
    current = initial
    for event in events:
        current = reduce_execution(
            current,
            event if isinstance(event, ExecutionEvent) else upcast_execution_event(event),
        )
    return current


def replay_task_run(
    initial: TaskRunSnapshot,
    events: Iterable[TaskRunEvent],
) -> TaskRunSnapshot:
    current = initial
    for event in events:
        current = reduce_task_run(current, event)
    return current


def upcast_execution_event(raw: Mapping[str, Any]) -> ExecutionEvent:
    """Upgrade supported historical execution-event mappings to schema v2."""

    version = raw.get("schema_version", 1)
    if version == 2:
        return ExecutionEvent.model_validate(raw)
    if version != 1:
        raise UnsupportedEventSchema(f"unsupported execution event schema version {version}")
    upgraded = dict(raw)
    payload = upgraded.get("payload")
    upgraded["schema_version"] = 2
    upgraded["idempotency_key"] = upgraded.get("idempotency_key") or str(upgraded["event_id"])
    if upgraded.get("reason") is None and isinstance(payload, dict):
        upgraded["reason"] = payload.get("reason")
    return ExecutionEvent.model_validate(upgraded)


def _reject(
    snapshot: ExecutionSnapshot,
    command: ExecutionCommand,
    code: TransitionRejectionCode,
) -> ExecutionTransition:
    reason = {
        TransitionRejectionCode.VERSION_CONFLICT: (
            f"expected version {command.expected_version}; current version is {snapshot.version}"
        ),
        TransitionRejectionCode.EPOCH_CONFLICT: (
            f"expected epoch {command.expected_epoch}; current epoch is {snapshot.epoch}"
        ),
        TransitionRejectionCode.ILLEGAL_TRANSITION: (
            f"{command.command_type.value} is not legal from {snapshot.state.value}"
        ),
    }[code]
    return ExecutionTransition(
        snapshot=snapshot,
        rejection=TransitionRejection(
            rejection_id=command.command_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            aggregate_type="execution",
            aggregate_id=snapshot.execution_id,
            code=code,
            current_state=snapshot.state,
            current_version=snapshot.version,
            current_epoch=snapshot.epoch,
            actor_id=command.actor_id,
            reason=reason,
            correlation_id=command.correlation_id,
            causation_id=command.causation_id,
            occurred_at=command.submitted_at,
        ),
    )


def _reject_task(
    snapshot: TaskRunSnapshot,
    command: TaskRunCommand,
    code: TransitionRejectionCode,
) -> TaskRunTransition:
    reason = {
        TransitionRejectionCode.VERSION_CONFLICT: (
            f"expected version {command.expected_version}; current version is {snapshot.version}"
        ),
        TransitionRejectionCode.ILLEGAL_TRANSITION: (
            f"{command.command_type.value} is not legal from {snapshot.state.value}"
        ),
        TransitionRejectionCode.EPOCH_CONFLICT: "task runs do not use execution epochs",
    }[code]
    return TaskRunTransition(
        snapshot=snapshot,
        rejection=TransitionRejection(
            rejection_id=command.command_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            aggregate_type="task_run",
            aggregate_id=snapshot.task_run_id,
            code=code,
            current_state=snapshot.state,
            current_version=snapshot.version,
            actor_id=command.actor_id,
            reason=reason,
            correlation_id=command.correlation_id,
            causation_id=command.causation_id,
            occurred_at=command.submitted_at,
        ),
    )
