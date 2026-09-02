from __future__ import annotations

import asyncio
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState, FailureCategory
from amesh.dsl import FlowDefinition
from amesh.dsl.models import RetryPolicy, TaskDefinition
from amesh.executor import ExecutionProgress, InProcessExecutor, preview_execution_intervention
from amesh.executor.service import (
    TaskExecutionError,
    TaskExecutionFailure,
    classify_task_failure,
    retry_delay_seconds,
)
from amesh.ports import (
    ExecutionInterventionAction,
    ExecutionStateConflictError,
    PersistedTaskRun,
    TaskRunState,
    TaskStateConflictError,
)


def test_recovery_returns_when_a_non_deferrable_task_is_already_running(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stale recovery pass must not spin while another owner holds a task run."""

    execution_id = uuid4()
    task_run = PersistedTaskRun(
        task_run_id=uuid4(),
        execution_id=execution_id,
        task_id="already-running",
        state=TaskRunState.RUNNING,
        current_attempt=1,
        version=1,
    )
    progress = ExecutionProgress(
        execution_id=execution_id,
        state=ExecutionState.RUNNING,
        tasks_run=0,
        task_runs=(task_run,),
    )
    executor = InProcessExecutor(object())  # run_ready is replaced below
    calls = 0

    async def run_ready(*args: object, **kwargs: object) -> ExecutionProgress:
        nonlocal calls
        del args, kwargs
        calls += 1
        return progress

    async def no_waiting_deferral(*args: object, **kwargs: object) -> bool:
        del args, kwargs
        return False

    monkeypatch.setattr(executor, "run_ready", run_ready)
    monkeypatch.setattr(executor, "_has_waiting_deferral", no_waiting_deferral)

    result = asyncio.run(
        asyncio.wait_for(
            executor.run_to_completion(
                FlowDefinition(
                    id="recovery-running-task",
                    namespace="tests.recovery",
                    tasks=[TaskDefinition(id="already-running", type="core.return")],
                ),
                execution_id,
                tenant_id="default",
            ),
            timeout=0.2,
        )
    )

    assert result is progress
    assert calls == 1


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
            {"partition_key": f"execution:{execution_id}"},
        )
        await connection.execute(
            text(
                "DELETE FROM transition_rejections WHERE "
                "(aggregate_type = 'execution' AND aggregate_id = :execution_id) OR "
                "(aggregate_type = 'task_run' AND aggregate_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id))"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text(
                "DELETE FROM task_attempts WHERE task_run_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM executions WHERE id = :execution_id"),
            {"execution_id": execution_id},
        )


def two_task_flow(name: str, *, timeout_seconds: float | None = None) -> FlowDefinition:
    return FlowDefinition(
        id=name,
        namespace=f"tests.control.{uuid4().hex}",
        timeoutSeconds=timeout_seconds,
        tasks=[
            TaskDefinition(id="first", type="core.return", value="first"),
            TaskDefinition(
                id="second",
                type="core.return",
                dependsOn=["first"],
                value="second",
            ),
        ],
    )


def test_retry_policy_is_bounded_and_failures_are_classified() -> None:
    policy = RetryPolicy(
        maxAttempts=5,
        delaySeconds=10,
        backoffMultiplier=3,
        maxIntervalSeconds=15,
        jitterRatio=0.25,
    )
    task_run_id = uuid4()

    first = retry_delay_seconds(policy, task_run_id, 3)
    second = retry_delay_seconds(policy, task_run_id, 3)

    assert first == second
    assert 0 <= first <= 15
    assert classify_task_failure(ValueError("bad task")) is FailureCategory.NON_RETRYABLE
    assert classify_task_failure(OSError("worker lost")) is FailureCategory.INFRASTRUCTURE
    assert classify_task_failure(TimeoutError()) is FailureCategory.TIMED_OUT
    cancelled = TaskExecutionFailure("cancelled", FailureCategory.CANCELLED)
    assert classify_task_failure(cancelled) is FailureCategory.CANCELLED


def test_pause_resume_preserves_completed_work_and_history(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = two_task_flow("pause_resume")
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        try:
            first_progress = await executor.run_ready(
                flow,
                execution.execution_id,
                tenant_id="default",
                max_tasks=1,
            )
            current = await repository.get_execution(
                execution.execution_id,
                tenant_id="default",
            )
            preview = preview_execution_intervention(
                flow,
                current,
                list(first_progress.task_runs),
                ExecutionInterventionAction.PAUSE,
                now=await repository.database_time(),
            )
            assert preview.impacted_task_ids == ("second",)
            assert preview.preserved_task_ids == ("first",)

            paused = await repository.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.PAUSE,
                tenant_id="default",
                expected_version=preview.current_version,
                expected_epoch=preview.current_epoch,
                actor_id="test:operator",
                reason="inspect downstream input",
            )
            assert paused.state is ExecutionState.PAUSED
            while_paused = await executor.run_ready(
                flow,
                execution.execution_id,
                tenant_id="default",
            )
            assert while_paused.tasks_run == 0
            assert (
                next(task for task in while_paused.task_runs if task.task_id == "first").state
                is TaskRunState.SUCCESS
            )

            resumed = await repository.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.RESUME,
                tenant_id="default",
                expected_version=paused.version,
                expected_epoch=paused.epoch,
                actor_id="test:operator",
                reason="inspection complete",
            )
            completed = await executor.run_to_completion(
                flow,
                execution.execution_id,
                tenant_id="default",
            )
            assert resumed.state is ExecutionState.RUNNING
            assert completed.state is ExecutionState.SUCCESS
            task_runs = {task.task_id: task for task in completed.task_runs}
            assert task_runs["first"].current_attempt == 1
            assert task_runs["second"].current_attempt == 1
            history = await repository.list_execution_interventions(
                execution.execution_id,
                tenant_id="default",
            )
            assert [record.action for record in history] == [
                ExecutionInterventionAction.PAUSE,
                ExecutionInterventionAction.RESUME,
            ]
            assert [record.reason for record in history] == [
                "inspect downstream input",
                "inspection complete",
            ]
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_cancel_escalation_invalidates_stale_attempt_results(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = two_task_flow("cancel_escalation")
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        task_runs = await repository.list_task_runs(execution.execution_id, tenant_id="default")
        running = await repository.start_task(
            task_runs[0].task_run_id,
            tenant_id="default",
            dispatch=False,
        )
        try:
            cancelling = await repository.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.REQUEST_CANCEL,
                tenant_id="default",
                expected_version=execution.version,
                expected_epoch=execution.epoch,
                actor_id="test:operator",
                reason="operator requested cancellation",
                grace_period=timedelta(seconds=0.2),
            )
            assert cancelling.state is ExecutionState.CANCELLING
            with pytest.raises(
                ExecutionStateConflictError,
                match="not available before the grace deadline",
            ):
                await repository.apply_execution_intervention(
                    execution.execution_id,
                    ExecutionInterventionAction.FORCE_CANCEL,
                    tenant_id="default",
                    expected_version=cancelling.version,
                    expected_epoch=cancelling.epoch,
                    actor_id="test:operator",
                    reason="deadline has not elapsed",
                )
            await asyncio.sleep(0.25)
            cancelled = await repository.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.FORCE_CANCEL,
                tenant_id="default",
                expected_version=cancelling.version,
                expected_epoch=cancelling.epoch,
                actor_id="test:operator",
                reason="grace deadline elapsed",
            )
            assert cancelled.state is ExecutionState.CANCELLED
            with pytest.raises(TaskStateConflictError, match="is not running"):
                await repository.complete_task(
                    running.task_run_id,
                    running.current_attempt,
                    {"value": "stale"},
                    tenant_id="default",
                )
            async with engine.connect() as connection:
                cancellation_requested = await connection.scalar(
                    text(
                        "SELECT cancellation_requested_at IS NOT NULL FROM task_attempts "
                        "WHERE task_run_id = :task_run_id AND attempt = :attempt"
                    ),
                    {"task_run_id": running.task_run_id, "attempt": running.current_attempt},
                )
                attempt_state = await connection.scalar(
                    text(
                        "SELECT state FROM task_attempts "
                        "WHERE task_run_id = :task_run_id AND attempt = :attempt"
                    ),
                    {"task_run_id": running.task_run_id, "attempt": running.current_attempt},
                )
            assert cancellation_requested is True
            assert attempt_state == "CANCELLED"
            history = await repository.list_execution_interventions(
                execution.execution_id,
                tenant_id="default",
            )
            assert [record.action for record in history] == [
                ExecutionInterventionAction.REQUEST_CANCEL,
                ExecutionInterventionAction.FORCE_CANCEL,
            ]
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_restart_from_checkpoint_preserves_upstream_and_advances_epoch(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = two_task_flow("restart_checkpoint")
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        try:
            await executor.run_ready(
                flow,
                execution.execution_id,
                tenant_id="default",
                max_tasks=1,
            )
            task_runs = await repository.list_task_runs(
                execution.execution_id,
                tenant_id="default",
            )
            second = next(task for task in task_runs if task.task_id == "second")
            running = await repository.start_task(
                second.task_run_id,
                tenant_id="default",
                dispatch=False,
            )
            await repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                "controlled failure",
                tenant_id="default",
            )
            failed = await repository.fail_execution(
                execution.execution_id,
                "controlled failure",
                tenant_id="default",
                expected_epoch=execution.epoch,
            )
            failed_tasks = await repository.list_task_runs(
                execution.execution_id,
                tenant_id="default",
            )
            preview = preview_execution_intervention(
                flow,
                failed,
                failed_tasks,
                ExecutionInterventionAction.RESTART,
                checkpoint_task_id="second",
                now=await repository.database_time(),
            )
            assert preview.impacted_task_ids == ("second",)
            assert preview.preserved_task_ids == ("first",)
            restarted = await repository.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.RESTART,
                tenant_id="default",
                expected_version=preview.current_version,
                expected_epoch=preview.current_epoch,
                actor_id="test:operator",
                reason="retry from failed checkpoint",
                reset_task_ids=preview.impacted_task_ids,
                checkpoint_task_id="second",
            )
            assert restarted.state is ExecutionState.RUNNING
            assert restarted.epoch == execution.epoch + 1
            with pytest.raises(TaskStateConflictError, match="is not running"):
                await repository.complete_task(
                    running.task_run_id,
                    running.current_attempt,
                    {"value": "stale"},
                    tenant_id="default",
                )
            completed = await executor.run_to_completion(
                flow,
                execution.execution_id,
                tenant_id="default",
            )
            assert completed.state is ExecutionState.SUCCESS
            completed_tasks = {task.task_id: task for task in completed.task_runs}
            assert completed_tasks["first"].current_attempt == 1
            assert completed_tasks["second"].current_attempt == 2
            history = await repository.list_execution_interventions(
                execution.execution_id,
                tenant_id="default",
            )
            assert [record.event_type for record in history] == [
                "ExecutionRestartRequested",
                "ExecutionStarted",
            ]
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_execution_and_task_deadlines_persist_timeout_category(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        async def sleep_handler(
            task: TaskDefinition,
            context: object,
        ) -> dict[str, object]:
            del task, context
            await asyncio.sleep(0.75)
            return {"value": "late"}

        flow = FlowDefinition(
            id="execution_timeout",
            namespace=f"tests.control.{uuid4().hex}",
            timeoutSeconds=0.5,
            tasks=[TaskDefinition(id="slow", type="test.sleep")],
        )
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository, handlers={"test.sleep": sleep_handler})
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        try:
            with pytest.raises(TaskExecutionError, match="execution deadline exceeded"):
                await executor.run_ready(
                    flow,
                    execution.execution_id,
                    tenant_id="default",
                )
            persisted = await repository.get_execution(
                execution.execution_id,
                tenant_id="default",
            )
            task_run = (
                await repository.list_task_runs(
                    execution.execution_id,
                    tenant_id="default",
                )
            )[0]
            assert persisted.state is ExecutionState.FAILED
            assert task_run.state is TaskRunState.FAILED
            assert task_run.failure_category is FailureCategory.TIMED_OUT
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_task_timeout_retries_only_to_configured_attempt_limit(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        async def sleep_handler(
            task: TaskDefinition,
            context: object,
        ) -> dict[str, object]:
            del task, context
            await asyncio.sleep(0.1)
            return {"value": "late"}

        flow = FlowDefinition.model_validate(
            {
                "id": "task_timeout",
                "namespace": f"tests.control.{uuid4().hex}",
                "tasks": [
                    {
                        "id": "slow",
                        "type": "test.sleep",
                        "timeoutSeconds": 0.01,
                        "retry": {
                            "maxAttempts": 2,
                            "delaySeconds": 0,
                            "maxIntervalSeconds": 1,
                            "jitterRatio": 0.5,
                        },
                    }
                ],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository, handlers={"test.sleep": sleep_handler})
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        try:
            with pytest.raises(TaskExecutionError, match="unsatisfiable execution graph"):
                await executor.run_to_completion(
                    flow,
                    execution.execution_id,
                    tenant_id="default",
                )
            task_run = (
                await repository.list_task_runs(
                    execution.execution_id,
                    tenant_id="default",
                )
            )[0]
            assert task_run.state is TaskRunState.FAILED
            assert task_run.current_attempt == 2
            assert task_run.failure_category is FailureCategory.TIMED_OUT
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())
