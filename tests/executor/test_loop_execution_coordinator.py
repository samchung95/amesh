from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4, uuid5

from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition
from amesh.dsl.models import TaskDefinition
from amesh.executor.contracts import TaskRunOutcome
from amesh.executor.loop_execution import run_loop
from amesh.executor.loops import LoopIterationContext
from amesh.expressions import NativeExpressionEngine
from amesh.ports import PersistedExecution, PersistedTaskDeferral, PersistedTaskRun, TaskRunState


class _LoopRepository:
    def __init__(self, execution: PersistedExecution, started_at: datetime) -> None:
        self.execution = execution
        self.started_at = started_at
        self.runs: dict[str, PersistedTaskRun] = {}
        self.ensure_keys: list[str] = []

    async def task_attempt_started_at(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
    ) -> datetime:
        del task_run_id
        assert attempt == 3
        assert tenant_id == self.execution.tenant_id
        return self.started_at

    async def database_time(self) -> datetime:
        return self.started_at

    async def ensure_iteration_task_runs(
        self,
        execution_id: UUID,
        iteration_key: str,
        task_ids: tuple[str, ...],
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]:
        assert execution_id == self.execution.execution_id
        assert tenant_id == self.execution.tenant_id
        assert task_ids == ("capture",)
        self.ensure_keys.append(iteration_key)
        if iteration_key not in self.runs:
            self.runs[iteration_key] = PersistedTaskRun(
                task_run_id=uuid5(execution_id, f"{iteration_key}:capture"),
                execution_id=execution_id,
                task_id="capture",
                iteration_key=iteration_key,
                state=TaskRunState.WAITING,
                current_attempt=0,
                version=0,
            )
        return [self.runs[iteration_key]]

    async def get_task_deferral(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedTaskDeferral | None:
        del task_run_id, tenant_id
        return None


def test_foreach_coordinator_preserves_iteration_keys_identity_attempts_and_order() -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "loop-coordinator",
                "namespace": "tests.loops",
                "tasks": [
                    {
                        "id": "loop",
                        "type": "core.foreach",
                        "items": ["slow", "fast"],
                        "maxConcurrency": 2,
                        "maxIterations": 2,
                        "maxTaskRuns": 2,
                        "tasks": [{"id": "capture", "type": "core.return"}],
                    }
                ],
            }
        )
        execution_id = uuid4()
        now = datetime.now(UTC)
        execution = PersistedExecution(
            execution_id=execution_id,
            tenant_id="tenant-a",
            state=ExecutionState.RUNNING,
            epoch=5,
            version=0,
            namespace=flow.namespace,
            flow_id=flow.id,
            created_at=now,
            updated_at=now,
        )
        parent_run = PersistedTaskRun(
            task_run_id=uuid4(),
            execution_id=execution_id,
            task_id="loop",
            state=TaskRunState.RUNNING,
            current_attempt=3,
            version=4,
        )
        repository = _LoopRepository(execution, now)
        observed: list[tuple[str, UUID, int, int]] = []

        async def run_task(
            flow: FlowDefinition,
            execution: PersistedExecution,
            task_run: PersistedTaskRun,
            task: TaskDefinition,
            outputs: Mapping[str, dict[str, Any]],
            workspace_parent: TaskDefinition | None = None,
            iteration: LoopIterationContext | None = None,
            handler_error: Mapping[str, Any] | None = None,
        ) -> TaskRunOutcome:
            del flow, execution, task, outputs, workspace_parent, handler_error
            assert iteration is not None
            assert task_run.iteration_key is not None
            observed.append(
                (
                    task_run.iteration_key,
                    task_run.task_run_id,
                    task_run.current_attempt,
                    int(iteration.parent["attempt"]),
                )
            )
            if iteration.index == 0:
                await asyncio.sleep(0.01)
            repository.runs[task_run.iteration_key] = task_run.model_copy(
                update={
                    "state": TaskRunState.SUCCESS,
                    "current_attempt": task_run.current_attempt + 1,
                    "result": {"index": iteration.index, "value": iteration.value},
                }
            )
            return TaskRunOutcome(claimed=True)

        result = await run_loop(
            flow,
            execution,
            parent_run,
            flow.tasks[0],
            {},
            repository=repository,
            expressions=NativeExpressionEngine(),
            object_store=None,
            run_task=run_task,
            admission_poll_initial_seconds=0.001,
            admission_poll_max_seconds=0.01,
        )

        keys = ["loop:00000000", "loop:00000001"]
        assert sorted(set(repository.ensure_keys)) == keys
        assert sorted(observed) == [
            (key, uuid5(execution_id, f"{key}:capture"), 0, 3) for key in keys
        ]
        assert [iteration["index"] for iteration in result["iterations"]] == [0, 1]
        assert [
            iteration["children"]["capture"]["output"] for iteration in result["iterations"]
        ] == [
            {"index": 0, "value": "slow"},
            {"index": 1, "value": "fast"},
        ]
        assert result["failurePolicy"] == "FAIL_FAST"

    asyncio.run(scenario())
