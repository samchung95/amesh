from __future__ import annotations

import asyncio
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState
from amesh.dsl.models import FlowDefinition, RetryPolicy, TaskDefinition
from amesh.executor import InProcessExecutor, local_process_handler
from amesh.ports import TaskStateConflictError

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
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


def test_local_process_task_retries_then_succeeds(tmp_path: Path) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        marker = tmp_path / "attempted"
        script = (
            "from pathlib import Path; import sys; "
            "p=Path(sys.argv[1]); existed=p.exists(); p.write_text('attempted'); "
            "raise SystemExit(0 if existed else 7)"
        )
        flow = FlowDefinition(
            id="local_retry",
            namespace=f"tests.executor.{uuid4().hex}",
            tasks=[
                TaskDefinition(
                    id="shell",
                    type="core.shell",
                    command=[sys.executable, "-c", script, str(marker)],
                    retry=RetryPolicy(max_attempts=2),
                    timeout_seconds=5,
                )
            ],
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(
            repository,
            handlers={"core.shell": local_process_handler(LocalProcessRunner())},
        )
        execution_id = await executor.create_execution(flow)
        try:
            completed = await executor.run_to_completion(flow, execution_id)
            assert completed.state is ExecutionState.SUCCESS
            assert completed.task_runs[0].current_attempt == 2
            assert completed.task_runs[0].result is not None
            assert completed.task_runs[0].result["exitCode"] == 0
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_retry_fences_late_result_from_superseded_attempt() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition(
            id="stale_result",
            namespace=f"tests.executor.{uuid4().hex}",
            tasks=[TaskDefinition(id="task", type="core.return")],
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution_id = (
            await repository.create_execution(flow, tenant_id="default", inputs={})
        ).execution_id
        try:
            task_run = (await repository.list_task_runs(execution_id))[0]
            first = await repository.start_task(task_run.task_run_id)
            await repository.retry_task(
                first.task_run_id,
                first.current_attempt,
                retry_at=datetime.now(UTC),
                reason="worker disappeared",
            )
            second = await repository.start_task(task_run.task_run_id)
            assert second.current_attempt == 2
            with pytest.raises(TaskStateConflictError):
                await repository.complete_task(
                    first.task_run_id, first.current_attempt, {"late": True}
                )
            await repository.complete_task(second.task_run_id, second.current_attempt, {"ok": True})
            completed = await repository.complete_execution(execution_id, expected_epoch=1)
            assert completed.state is ExecutionState.SUCCESS
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
