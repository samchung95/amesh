from uuid import uuid4

import pytest

from amesh.domain import (
    ExecutionEvent,
    ExecutionEventType,
    ExecutionSnapshot,
    ExecutionState,
    InvalidTransition,
    reduce_execution,
)


def snapshot() -> ExecutionSnapshot:
    return ExecutionSnapshot(
        execution_id=uuid4(),
        tenant_id="default",
        namespace="examples",
        flow_id="hello",
        flow_revision=1,
    )


def test_happy_path_and_duplicate_idempotency() -> None:
    current = snapshot()
    queued = ExecutionEvent(event_type=ExecutionEventType.QUEUED)
    current = reduce_execution(current, queued)
    assert current.state is ExecutionState.QUEUED
    assert current.version == 1

    duplicate = reduce_execution(current, queued)
    assert duplicate is current
    assert duplicate.version == 1

    current = reduce_execution(
        current,
        ExecutionEvent(event_type=ExecutionEventType.STARTED),
    )
    current = reduce_execution(
        current,
        ExecutionEvent(event_type=ExecutionEventType.SUCCEEDED),
    )
    assert current.state is ExecutionState.SUCCESS
    assert current.terminal


def test_illegal_transition_does_not_mutate_snapshot() -> None:
    current = snapshot()
    with pytest.raises(InvalidTransition):
        reduce_execution(
            current,
            ExecutionEvent(event_type=ExecutionEventType.SUCCEEDED),
        )
    assert current.state is ExecutionState.CREATED
    assert current.version == 0


def test_restart_increments_epoch() -> None:
    current = snapshot()
    for event_type in (
        ExecutionEventType.QUEUED,
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
        ExecutionEventType.RESTART_REQUESTED,
        ExecutionEventType.STARTED,
    ):
        current = reduce_execution(current, ExecutionEvent(event_type=event_type))
    assert current.state is ExecutionState.RUNNING
    assert current.epoch == 2
