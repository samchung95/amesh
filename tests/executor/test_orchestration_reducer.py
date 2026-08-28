from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from amesh.domain import ExecutionState, TaskRunState
from amesh.dsl import FlowDefinition
from amesh.executor import reduce_orchestration
from amesh.ports import PersistedTaskRun


def _task_run(task_id: str, state: TaskRunState) -> PersistedTaskRun:
    return PersistedTaskRun(
        task_run_id=uuid4(),
        execution_id=uuid4(),
        task_id=task_id,
        state=state,
        current_attempt=0,
        version=1,
    )


def test_orchestration_reducer_is_deterministic_for_parallel_and_blocked_branches() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "reducer",
            "namespace": "tests.reducer",
            "tasks": [
                {"id": "left", "type": "core.return"},
                {"id": "right", "type": "core.return"},
                {
                    "id": "join",
                    "type": "core.return",
                    "dependsOn": ["left", "right"],
                },
            ],
        }
    )
    now = datetime(2026, 8, 22, tzinfo=UTC)
    initial = [
        _task_run("left", TaskRunState.WAITING),
        _task_run("right", TaskRunState.WAITING),
        _task_run("join", TaskRunState.WAITING),
    ]

    decisions = [reduce_orchestration(flow, initial, now=now) for _ in range(100)]
    assert {decision.model_dump_json() for decision in decisions} == {
        decisions[0].model_dump_json()
    }
    assert decisions[0].runnable_task_ids == ("left", "right")

    failed = [
        initial[0].model_copy(update={"state": TaskRunState.FAILED}),
        initial[1],
        initial[2],
    ]
    terminal = reduce_orchestration(flow, failed, now=now)
    assert terminal.terminal_state is ExecutionState.FAILED
    assert terminal.diagnostic == (
        "unsatisfiable execution graph; failed=['left']; blocked=['join']"
    )
