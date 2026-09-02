from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

import amesh.executor.service as executor_service
from amesh.domain import AdmissionBehavior, AdmissionScope, ConcurrencyLimit, ExecutionState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import ExecutionProgress, InProcessExecutor
from amesh.ports import PersistedTaskRun, TaskRunState


def test_admission_polling_uses_capped_exponential_backoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execution_id = uuid4()
    task_run = PersistedTaskRun(
        task_run_id=uuid4(),
        execution_id=execution_id,
        task_id="limited",
        state=TaskRunState.WAITING,
        current_attempt=0,
        version=1,
    )
    flow = FlowDefinition(
        id="admission_backoff",
        namespace="tests.executor",
        tasks=[
            TaskDefinition(
                id="limited",
                type="core.return",
                concurrency=[
                    ConcurrencyLimit(
                        id="one-at-a-time",
                        scope=AdmissionScope.FLOW,
                        limit=1,
                        behavior=AdmissionBehavior.QUEUE,
                    )
                ],
            )
        ],
    )
    delays: list[float] = []

    class Repository:
        async def get_execution(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            return SimpleNamespace()

    class Executor(InProcessExecutor):
        def __init__(self) -> None:
            super().__init__(
                Repository(),  # type: ignore[arg-type]
                admission_poll_initial_seconds=0.01,
                admission_poll_max_seconds=0.025,
            )
            self.calls = 0

        async def run_ready(self, *args: object, **kwargs: object) -> ExecutionProgress:
            del args, kwargs
            self.calls += 1
            if self.calls <= 3:
                return ExecutionProgress(
                    execution_id=execution_id,
                    state=ExecutionState.RUNNING,
                    tasks_run=0,
                    task_runs=(task_run,),
                )
            return ExecutionProgress(
                execution_id=execution_id,
                state=ExecutionState.SUCCESS,
                tasks_run=1,
                task_runs=(task_run.model_copy(update={"state": TaskRunState.SUCCESS}),),
            )

    async def record_delay(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(executor_service.asyncio, "sleep", record_delay)
    monkeypatch.setattr(executor_service, "execution_lifecycle_pending", lambda *args: False)

    result = asyncio.run(Executor().run_to_completion(flow, execution_id, tenant_id="default"))

    assert result.state is ExecutionState.SUCCESS
    assert delays == [0.01, 0.02, 0.025]
