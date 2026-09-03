from __future__ import annotations

import asyncio
from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from amesh.domain import ExecutionState, FailureCategory, TaskRunLifecyclePhase
from amesh.dsl import FlowDefinition, LifecyclePhase, PlannedTask, compile_execution_tasks
from amesh.executor.contracts import ExecutionProgress, OrchestrationDecision
from amesh.executor.lifecycle_execution import advance_execution_lifecycle
from amesh.ports import PersistedExecution, PersistedTaskRun, TaskRunState


class _LifecycleRepository:
    def __init__(self, execution: PersistedExecution) -> None:
        self.current = execution
        self.records: list[tuple[str, int]] = []

    async def record_execution_lifecycle(
        self,
        execution_id: UUID,
        evidence: dict[str, object],
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        assert execution_id == self.current.execution_id
        assert tenant_id == self.current.tenant_id
        self.records.append((str(evidence["status"]), expected_epoch))
        self.current = self.current.model_copy(
            update={
                "lifecycle_evidence": deepcopy(evidence),
                "version": self.current.version + 1,
            }
        )
        return self.current


def _execution() -> PersistedExecution:
    now = datetime.now(UTC)
    return PersistedExecution(
        execution_id=uuid4(),
        tenant_id="tenant-a",
        state=ExecutionState.RUNNING,
        epoch=7,
        version=0,
        namespace="tests.lifecycle",
        flow_id="coordinator",
        created_at=now,
        updated_at=now,
    )


def _task_runs(
    execution_id: UUID,
    plan: tuple[PlannedTask, ...],
) -> list[PersistedTaskRun]:
    runs: list[PersistedTaskRun] = []
    for node in plan:
        state = TaskRunState.WAITING
        result = None
        failure_category = None
        if node.lifecycle_phase is LifecyclePhase.MAIN:
            state = TaskRunState.FAILED
            result = {"error": "primary failure"}
            failure_category = FailureCategory.USER_CODE
        runs.append(
            PersistedTaskRun(
                task_run_id=uuid4(),
                execution_id=execution_id,
                task_id=node.task.id,
                state=state,
                current_attempt=1 if state is TaskRunState.FAILED else 0,
                version=0,
                result=result,
                failure_category=failure_category,
                lifecycle_phase=TaskRunLifecyclePhase(node.lifecycle_phase.value),
            )
        )
    return runs


def test_coordinator_preserves_lifecycle_checkpoint_pacing_and_epoch() -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "coordinator",
                "namespace": "tests.lifecycle",
                "tasks": [{"id": "main", "type": "core.return"}],
                "errors": [{"id": "on_error", "type": "core.return"}],
                "finally": [{"id": "cleanup", "type": "core.return"}],
                "afterExecution": [{"id": "audit", "type": "core.return"}],
            }
        )
        plan = compile_execution_tasks(flow)
        repository = _LifecycleRepository(_execution())
        task_runs = _task_runs(repository.current.execution_id, plan)
        phase_calls: list[tuple[LifecyclePhase, int | None]] = []
        finish_decisions: list[OrchestrationDecision] = []

        async def run_phase(
            flow: FlowDefinition,
            execution: PersistedExecution,
            plan: tuple[PlannedTask, ...],
            task_runs: list[PersistedTaskRun],
            *,
            handler_errors: Mapping[str, Mapping[str, Any]],
            max_tasks: int | None,
        ) -> ExecutionProgress:
            del flow, handler_errors
            phase = plan[0].lifecycle_phase
            phase_calls.append((phase, max_tasks))
            phase_ids = {node.task.id for node in plan}
            updated = [
                run.model_copy(
                    update={
                        "state": TaskRunState.SUCCESS,
                        "current_attempt": 1,
                        "result": {"phase": phase.value},
                    }
                )
                if run.task_id in phase_ids
                else run
                for run in task_runs
            ]
            return ExecutionProgress(
                execution_id=execution.execution_id,
                state=execution.state,
                tasks_run=len(phase_ids),
                task_runs=tuple(updated),
            )

        async def finish_execution(
            flow: FlowDefinition,
            execution: PersistedExecution,
            decision: OrchestrationDecision,
            task_runs: list[PersistedTaskRun],
        ) -> PersistedExecution:
            del flow, task_runs
            finish_decisions.append(decision)
            repository.current = execution.model_copy(update={"state": decision.terminal_state})
            return repository.current

        async def skip_tasks(
            task_runs: list[PersistedTaskRun],
            task_ids: set[str],
            phase: LifecyclePhase,
            *,
            tenant_id: str,
            reason: str,
        ) -> list[PersistedTaskRun]:
            del task_runs, task_ids, phase, tenant_id, reason
            raise AssertionError("the matching failure handler must not be skipped")

        progress = await advance_execution_lifecycle(
            flow,
            repository.current,
            plan,
            task_runs,
            primary_decision=OrchestrationDecision(
                terminal_state=ExecutionState.FAILED,
                diagnostic="durable primary diagnostic",
            ),
            max_tasks=3,
            repository=repository,
            finish_execution=finish_execution,
            run_lifecycle_phase=run_phase,
            skip_lifecycle_tasks=skip_tasks,
            claimed_tasks=2,
            primary_failure="transient handler text",
        )
        assert progress.state is ExecutionState.RUNNING
        assert progress.tasks_run == 3
        assert repository.records == [("ERROR", 7), ("FINALLY", 7)]

        for expected_status in ("AFTER_EXECUTION", "FINISHED", "COMPLETE"):
            progress = await advance_execution_lifecycle(
                flow,
                repository.current,
                plan,
                list(progress.task_runs),
                primary_decision=None,
                max_tasks=3,
                repository=repository,
                finish_execution=finish_execution,
                run_lifecycle_phase=run_phase,
                skip_lifecycle_tasks=skip_tasks,
            )
            if expected_status != "FINISHED":
                assert repository.current.lifecycle_evidence["status"] == expected_status

        assert progress.state is ExecutionState.FAILED
        assert phase_calls == [
            (LifecyclePhase.ERROR, 3),
            (LifecyclePhase.FINALLY, 3),
            (LifecyclePhase.AFTER_EXECUTION, 3),
        ]
        assert repository.records == [
            ("ERROR", 7),
            ("FINALLY", 7),
            ("AFTER_EXECUTION", 7),
            ("COMPLETE", 7),
        ]
        assert len(finish_decisions) == 1
        assert finish_decisions[0].terminal_state is ExecutionState.FAILED
        assert finish_decisions[0].diagnostic == "durable primary diagnostic"

    asyncio.run(scenario())
