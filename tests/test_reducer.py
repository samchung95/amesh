import ast
import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

from amesh.domain import (
    ExecutionCommand,
    ExecutionCommandType,
    ExecutionEvent,
    ExecutionEventType,
    ExecutionSnapshot,
    ExecutionState,
    InvalidTransition,
    TaskRunCommand,
    TaskRunCommandType,
    TaskRunEvent,
    TaskRunEventType,
    TaskRunSnapshot,
    TaskRunState,
    TransitionRejectionCode,
    UnsupportedEventSchema,
    decide_execution,
    decide_task_run,
    reduce_execution,
    reduce_task_run,
    replay_execution,
    replay_task_run,
    upcast_execution_event,
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


def test_command_decision_preserves_metadata_and_deduplicates_by_stable_key() -> None:
    current = snapshot()
    command = ExecutionCommand(
        command_type=ExecutionCommandType.QUEUE,
        idempotency_key="queue:examples.hello:1",
        expected_version=0,
        expected_epoch=1,
        actor_id="user:operator",
        reason="manual launch",
    )

    accepted = decide_execution(current, command)

    assert accepted.rejection is None
    assert accepted.snapshot.state is ExecutionState.QUEUED
    assert accepted.events[0].actor_id == "user:operator"
    assert accepted.events[0].reason == "manual launch"
    duplicate_command = command.model_copy(update={"command_id": uuid4()})
    duplicate = decide_execution(accepted.snapshot, duplicate_command)
    assert duplicate.duplicate
    assert duplicate.snapshot is accepted.snapshot
    assert duplicate.events == ()


@pytest.mark.parametrize(
    ("command", "code"),
    [
        (
            ExecutionCommand(
                command_type=ExecutionCommandType.QUEUE,
                idempotency_key="stale-version",
                expected_version=4,
            ),
            TransitionRejectionCode.VERSION_CONFLICT,
        ),
        (
            ExecutionCommand(
                command_type=ExecutionCommandType.QUEUE,
                idempotency_key="stale-epoch",
                expected_epoch=2,
            ),
            TransitionRejectionCode.EPOCH_CONFLICT,
        ),
        (
            ExecutionCommand(
                command_type=ExecutionCommandType.SUCCEED,
                idempotency_key="illegal-transition",
            ),
            TransitionRejectionCode.ILLEGAL_TRANSITION,
        ),
    ],
)
def test_rejected_command_is_deterministic_and_does_not_mutate(
    command: ExecutionCommand,
    code: TransitionRejectionCode,
) -> None:
    current = snapshot()

    first = decide_execution(current, command)
    second = decide_execution(current, command)

    assert first == second
    assert first.snapshot is current
    assert first.events == ()
    assert first.rejection is not None
    assert first.rejection.code is code
    assert first.rejection.actor_id == command.actor_id
    assert first.rejection.correlation_id == command.correlation_id


def test_execution_replay_is_byte_stable_across_one_hundred_runs() -> None:
    initial = snapshot()
    events = [
        ExecutionEvent(event_type=ExecutionEventType.CREATED, idempotency_key="created"),
        ExecutionEvent(event_type=ExecutionEventType.QUEUED, idempotency_key="queued"),
        ExecutionEvent(event_type=ExecutionEventType.STARTED, idempotency_key="started"),
        ExecutionEvent(event_type=ExecutionEventType.SUCCEEDED, idempotency_key="succeeded"),
    ]
    expected = replay_execution(initial, events).model_dump_json()

    assert {replay_execution(initial, events).model_dump_json() for _ in range(100)} == {expected}


def test_historical_execution_event_upcasts_and_unknown_version_fails() -> None:
    event = ExecutionEvent(
        event_type=ExecutionEventType.FAILED,
        payload={"reason": "worker exited"},
    )
    historical = event.model_dump(mode="json")
    historical["schema_version"] = 1
    historical.pop("idempotency_key")
    historical.pop("reason")

    upgraded = upcast_execution_event(historical)

    assert upgraded.schema_version == 2
    assert upgraded.idempotency_key == str(event.event_id)
    assert upgraded.reason == "worker exited"
    with pytest.raises(UnsupportedEventSchema):
        upcast_execution_event({**historical, "schema_version": 99})


def test_task_run_reducer_replays_retry_history_and_deduplicates() -> None:
    initial = TaskRunSnapshot(
        task_run_id=uuid4(),
        execution_id=uuid4(),
        task_id="call-agent",
    )
    events = [
        TaskRunEvent(event_type=TaskRunEventType.CREATED, idempotency_key="created"),
        TaskRunEvent(event_type=TaskRunEventType.STARTED, idempotency_key="attempt:1"),
        TaskRunEvent(event_type=TaskRunEventType.RETRY_SCHEDULED, idempotency_key="retry:1"),
        TaskRunEvent(event_type=TaskRunEventType.STARTED, idempotency_key="attempt:2"),
        TaskRunEvent(event_type=TaskRunEventType.SUCCEEDED, idempotency_key="success:2"),
    ]

    current = replay_task_run(initial, [*events, events[-1]])

    assert current.state is TaskRunState.SUCCESS
    assert current.current_attempt == 2
    assert current.version == 5
    with pytest.raises(InvalidTransition):
        reduce_task_run(current, TaskRunEvent(event_type=TaskRunEventType.STARTED))


def test_task_control_event_is_replayable_and_skip_keeps_attempt_zero() -> None:
    initial = TaskRunSnapshot(
        task_run_id=uuid4(),
        execution_id=uuid4(),
        task_id="conditional-child",
    )
    skipped = replay_task_run(
        initial,
        [
            TaskRunEvent(event_type=TaskRunEventType.CREATED, idempotency_key="created"),
            TaskRunEvent(event_type=TaskRunEventType.SKIPPED, idempotency_key="skipped"),
        ],
    )
    assert skipped.state is TaskRunState.SUCCESS
    assert skipped.current_attempt == 0

    parent = replay_task_run(
        initial.model_copy(update={"task_id": "conditional-parent"}),
        [
            TaskRunEvent(event_type=TaskRunEventType.CREATED, idempotency_key="parent-created"),
            TaskRunEvent(event_type=TaskRunEventType.STARTED, idempotency_key="parent-started"),
            TaskRunEvent(
                event_type=TaskRunEventType.CONTROL_RECORDED,
                idempotency_key="parent-decision",
            ),
            TaskRunEvent(event_type=TaskRunEventType.SUCCEEDED, idempotency_key="parent-success"),
        ],
    )
    assert parent.state is TaskRunState.SUCCESS
    assert parent.current_attempt == 1


def test_task_command_decision_is_typed_and_version_checked() -> None:
    current = TaskRunSnapshot(
        task_run_id=uuid4(),
        execution_id=uuid4(),
        task_id="call-agent",
    )
    accepted = decide_task_run(
        current,
        TaskRunCommand(
            command_type=TaskRunCommandType.CREATE,
            idempotency_key="task-created",
            expected_version=0,
        ),
    )

    assert accepted.events[0].event_type is TaskRunEventType.CREATED
    rejected = decide_task_run(
        accepted.snapshot,
        TaskRunCommand(
            command_type=TaskRunCommandType.START,
            idempotency_key="stale-task-start",
            expected_version=0,
        ),
    )
    assert rejected.rejection is not None
    assert rejected.rejection.code is TransitionRejectionCode.VERSION_CONFLICT
    assert rejected.rejection.aggregate_type == "task_run"


def test_domain_modules_do_not_import_infrastructure_frameworks() -> None:
    forbidden_roots = {
        "aioboto3",
        "fastapi",
        "kubernetes",
        "opentelemetry",
        "prometheus_client",
        "sqlalchemy",
    }
    domain_root = Path(__file__).parents[1] / "src" / "amesh" / "domain"
    imported_roots: set[str] = set()
    imported_modules: set[str] = set()
    for module_path in domain_root.glob("*.py"):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.partition(".")[0] for alias in node.names)
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.partition(".")[0])
                imported_modules.add(node.module)

    assert imported_roots.isdisjoint(forbidden_roots)
    assert "amesh.observability" not in imported_modules


def test_domain_package_import_does_not_load_heavy_runtime_dependencies() -> None:
    repository_root = Path(__file__).parents[1]
    probe = """
import json
import sys

import amesh.domain

forbidden = ("sqlalchemy", "opentelemetry", "prometheus_client", "PIL", "yaml")
loaded = sorted(
    name
    for name in sys.modules
    if any(name == root or name.startswith(root + ".") for root in forbidden)
)
print(json.dumps(loaded))
"""
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == []


def test_execution_contracts_accept_only_explicit_trace_context() -> None:
    command = ExecutionCommand(
        command_type=ExecutionCommandType.QUEUE,
        idempotency_key="explicit-trace-context",
    )
    event = ExecutionEvent(
        event_type=ExecutionEventType.QUEUED,
        trace_context={"TraceParent": "trace-value", "baggage": "not-propagated"},
    )

    assert command.trace_context == {}
    assert event.trace_context == {"traceparent": "trace-value"}
