from __future__ import annotations

from .execution import (
    ExecutionEvent,
    ExecutionEventType,
    ExecutionSnapshot,
    ExecutionState,
    InvalidTransition,
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


def reduce_execution(snapshot: ExecutionSnapshot, event: ExecutionEvent) -> ExecutionSnapshot:
    """Apply one immutable event.

    Duplicate event IDs are idempotent. All other illegal transitions raise without mutating the input.
    The function has no I/O and is safe to replay.
    """

    if event.event_id in snapshot.applied_event_ids:
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
            "last_event_at": event.occurred_at,
        }
    )
