from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from amesh.domain import ExecutionState, FailureCategory
from amesh.dsl import FlowDefinition, compile_flow_tasks
from amesh.executor.contracts import BranchDecision, ConditionDecision
from amesh.executor.flowable_execution import advance_flowables
from amesh.ports import PersistedExecution, PersistedTaskRun, TaskRunState


class _FlowableRepository:
    def __init__(self, task_runs: list[PersistedTaskRun]) -> None:
        self.runs = {task_run.task_run_id: task_run for task_run in task_runs}
        self.calls: list[tuple[str, str]] = []

    def _store(self, task_run: PersistedTaskRun, operation: str) -> PersistedTaskRun:
        self.runs[task_run.task_run_id] = task_run
        self.calls.append((operation, task_run.task_id))
        return task_run

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
        priority: int = 0,
        worker_group: str | None = None,
    ) -> PersistedTaskRun:
        del tenant_id, priority, worker_group
        assert dispatch is False
        current = self.runs[task_run_id]
        return self._store(
            current.model_copy(
                update={
                    "state": TaskRunState.RUNNING,
                    "current_attempt": current.current_attempt + 1,
                }
            ),
            "start",
        )

    async def record_task_control(
        self,
        task_run_id: UUID,
        attempt: int,
        evidence: dict[str, object],
        *,
        tenant_id: str,
    ) -> PersistedTaskRun:
        del tenant_id
        current = self.runs[task_run_id]
        assert current.current_attempt == attempt
        return self._store(current.model_copy(update={"evidence": evidence}), "record")

    async def skip_task(
        self,
        task_run_id: UUID,
        result: dict[str, Any],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        del tenant_id
        current = self.runs[task_run_id]
        return self._store(
            current.model_copy(
                update={
                    "state": TaskRunState.SUCCESS,
                    "result": result,
                    "evidence": evidence or {},
                }
            ),
            "skip",
        )

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, Any],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        del tenant_id, worker_id, fencing_token
        current = self.runs[task_run_id]
        assert current.current_attempt == attempt
        return self._store(
            current.model_copy(
                update={
                    "state": TaskRunState.SUCCESS,
                    "result": result,
                    "evidence": evidence or {},
                }
            ),
            "complete",
        )

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        result: dict[str, object] | None = None,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        del tenant_id, worker_id, fencing_token
        current = self.runs[task_run_id]
        assert current.current_attempt == attempt
        return self._store(
            current.model_copy(
                update={
                    "state": TaskRunState.FAILED,
                    "result": result or {"error": reason},
                    "failure_category": failure_category,
                    "evidence": evidence or {},
                }
            ),
            "fail",
        )


def _execution() -> PersistedExecution:
    now = datetime.now(UTC)
    return PersistedExecution(
        execution_id=uuid4(),
        tenant_id="tenant-a",
        state=ExecutionState.RUNNING,
        epoch=1,
        version=0,
        namespace="tests.flowables",
        flow_id="coordinator",
        created_at=now,
        updated_at=now,
    )


def _task_runs(execution_id: UUID, task_ids: list[str]) -> list[PersistedTaskRun]:
    return [
        PersistedTaskRun(
            task_run_id=uuid4(),
            execution_id=execution_id,
            task_id=task_id,
            state=TaskRunState.WAITING,
            current_attempt=0,
            version=0,
        )
        for task_id in task_ids
    ]


def test_coordinator_persists_branch_once_and_reduces_in_child_order() -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "coordinator",
                "namespace": "tests.flowables",
                "tasks": [
                    {
                        "id": "choose",
                        "type": "core.if",
                        "condition": "{{ true }}",
                        "then": [{"id": "selected", "type": "core.return", "value": 1}],
                        "else": [{"id": "rejected", "type": "core.return", "value": 2}],
                    }
                ],
            }
        )
        execution = _execution()
        plan = compile_flow_tasks(flow)
        initial = _task_runs(execution.execution_id, [node.task.id for node in plan])
        original_ids = {task_run.task_id: task_run.task_run_id for task_run in initial}
        repository = _FlowableRepository(initial)
        branch_calls = 0

        def evaluate_condition(*args: object) -> ConditionDecision:
            del args
            return ConditionDecision(matched=True, evidence={})

        def select_branch(*args: object) -> BranchDecision:
            nonlocal branch_calls
            del args
            branch_calls += 1
            return BranchDecision(
                selected_branch="then",
                evidence={"kind": "IF", "selectedBranch": "then"},
            )

        async def finalize_workspace(*args: object, **kwargs: object) -> tuple[dict, dict]:
            del args, kwargs
            raise AssertionError("non-workspace flowable must not finalize a workspace")

        task_runs = await advance_flowables(
            flow,
            execution,
            plan,
            initial,
            tenant_id=execution.tenant_id,
            repository=repository,
            evaluate_task_condition=evaluate_condition,
            select_branch=select_branch,
            finalize_working_directory=finalize_workspace,
        )
        assert repository.calls == [
            ("start", "choose"),
            ("record", "choose"),
            ("skip", "rejected"),
        ]
        assert branch_calls == 1
        assert [task_run.task_run_id for task_run in task_runs] == [
            original_ids[node.task.id] for node in plan
        ]

        repository.calls.clear()
        task_runs = await advance_flowables(
            flow,
            execution,
            plan,
            task_runs,
            tenant_id=execution.tenant_id,
            repository=repository,
            evaluate_task_condition=evaluate_condition,
            select_branch=select_branch,
            finalize_working_directory=finalize_workspace,
        )
        assert repository.calls == []
        assert branch_calls == 1

        selected = next(task_run for task_run in task_runs if task_run.task_id == "selected")
        succeeded = selected.model_copy(
            update={"state": TaskRunState.SUCCESS, "current_attempt": 1, "result": {"value": 1}}
        )
        task_runs = [
            succeeded if task_run.task_id == "selected" else task_run for task_run in task_runs
        ]
        repository.runs[succeeded.task_run_id] = succeeded
        completed = await advance_flowables(
            flow,
            execution,
            plan,
            task_runs,
            tenant_id=execution.tenant_id,
            repository=repository,
            evaluate_task_condition=evaluate_condition,
            select_branch=select_branch,
            finalize_working_directory=finalize_workspace,
        )
        assert repository.calls == [("complete", "choose")]
        parent = next(task_run for task_run in completed if task_run.task_id == "choose")
        assert parent.task_run_id == original_ids["choose"]
        assert parent.result is not None
        assert parent.result["childOrder"] == ["selected", "rejected"]
        assert parent.result["control"] == {"branch": {"kind": "IF", "selectedBranch": "then"}}

    asyncio.run(scenario())


def test_coordinator_finalizes_workspace_before_parent_completion() -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "workspace-coordinator",
                "namespace": "tests.flowables",
                "tasks": [
                    {
                        "id": "workspace",
                        "type": "core.workingDirectory",
                        "outputFiles": ["result.txt"],
                        "tasks": [{"id": "child", "type": "core.return", "value": 1}],
                    }
                ],
            }
        )
        execution = _execution()
        plan = compile_flow_tasks(flow)
        task_runs = _task_runs(execution.execution_id, [node.task.id for node in plan])
        task_runs = [
            task_run.model_copy(
                update={
                    "state": TaskRunState.RUNNING,
                    "current_attempt": 1,
                }
            )
            if task_run.task_id == "workspace"
            else task_run.model_copy(
                update={
                    "state": TaskRunState.SUCCESS,
                    "current_attempt": 1,
                    "result": {"value": 1},
                }
            )
            for task_run in task_runs
        ]
        repository = _FlowableRepository(task_runs)
        calls: list[tuple[str, bool]] = []

        def unexpected_decision(*args: object) -> Any:
            del args
            raise AssertionError("running workspace must not evaluate control conditions")

        async def finalize_workspace(
            persisted_execution: PersistedExecution,
            node: Any,
            task_run: PersistedTaskRun,
            *,
            failed: bool,
        ) -> tuple[dict[str, object], dict[str, object]]:
            assert persisted_execution is execution
            assert node.task.id == "workspace"
            assert task_run.task_id == "workspace"
            calls.append(("finalize", failed))
            return {"outputFiles": {"result.txt": "s3://bucket/result"}}, {
                "artifacts": [{"uri": "s3://bucket/result"}]
            }

        completed = await advance_flowables(
            flow,
            execution,
            plan,
            task_runs,
            tenant_id=execution.tenant_id,
            repository=repository,
            evaluate_task_condition=unexpected_decision,
            select_branch=unexpected_decision,
            finalize_working_directory=finalize_workspace,
        )
        assert calls == [("finalize", False)]
        assert repository.calls == [("complete", "workspace")]
        parent = next(task_run for task_run in completed if task_run.task_id == "workspace")
        assert parent.result is not None
        assert parent.result["outputFiles"] == {"result.txt": "s3://bucket/result"}
        assert parent.evidence == {"artifacts": [{"uri": "s3://bucket/result"}]}

    asyncio.run(scenario())
