from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, validate_flow_document
from amesh.executor import InProcessExecutor
from amesh.ports import ExecutionStateConflictError, TaskRunState

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def load_parallel_dag() -> FlowDefinition:
    result = validate_flow_document((ROOT / "examples" / "parallel-dag.yaml").read_bytes())
    assert result.valid
    assert result.canonical is not None
    return FlowDefinition.model_validate(result.canonical)


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


def test_parallel_dag_resumes_from_persisted_task_state_after_restart() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        source_flow = load_parallel_dag()
        flow = source_flow.model_copy(update={"namespace": f"tests.executor.{uuid4().hex}"})
        first_engine = create_async_engine(TEST_DATABASE_URL)
        first_repository = PostgresExecutionRepository(first_engine)
        first_executor = InProcessExecutor(first_repository)
        execution_id = await first_executor.create_execution(flow)

        first_progress = await first_executor.run_ready(flow, execution_id, max_tasks=1)
        assert first_progress.state is ExecutionState.RUNNING
        assert first_progress.tasks_run == 1
        assert (
            sum(task_run.state is TaskRunState.SUCCESS for task_run in first_progress.task_runs)
            == 1
        )
        await first_engine.dispose()

        resumed_engine = create_async_engine(TEST_DATABASE_URL)
        try:
            resumed_repository = PostgresExecutionRepository(resumed_engine)
            resumed_executor = InProcessExecutor(resumed_repository)
            completed = await resumed_executor.run_to_completion(flow, execution_id)

            assert completed.state is ExecutionState.SUCCESS
            assert {task_run.task_id for task_run in completed.task_runs} == {
                "extract_a",
                "extract_b",
                "combine",
            }
            assert all(task_run.state is TaskRunState.SUCCESS for task_run in completed.task_runs)
            assert all(task_run.current_attempt == 1 for task_run in completed.task_runs)
            results = {task_run.task_id: task_run.result for task_run in completed.task_runs}
            assert results["extract_a"] == {"value": "A"}
            assert results["extract_b"] == {"value": "B"}

            async with resumed_engine.connect() as connection:
                events = (
                    (
                        await connection.execute(
                            text(
                                "SELECT event_type FROM execution_events "
                                "WHERE execution_id = :execution_id ORDER BY sequence"
                            ),
                            {"execution_id": execution_id},
                        )
                    )
                    .scalars()
                    .all()
                )
            assert events == [
                "ExecutionCreated",
                "ExecutionQueued",
                "ExecutionStarted",
                "ExecutionSucceeded",
            ]
        finally:
            await cleanup_execution(resumed_engine, execution_id)
            await resumed_engine.dispose()

    asyncio.run(scenario())


def test_terminal_execution_event_is_fenced_by_epoch() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = load_parallel_dag().model_copy(update={"namespace": f"tests.fencing.{uuid4().hex}"})
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution = await repository.create_execution(
            flow,
            tenant_id="default",
            inputs={},
        )
        execution_id = execution.execution_id

        try:
            async with engine.connect() as connection:
                event_count_before = await connection.scalar(
                    text(
                        "SELECT count(*) FROM execution_events WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution_id},
                )

            with pytest.raises(ExecutionStateConflictError, match="fenced at epoch 1"):
                await repository.complete_execution(execution_id, expected_epoch=2)

            unchanged = await repository.get_execution(execution_id)
            assert unchanged.state is ExecutionState.RUNNING
            async with engine.connect() as connection:
                event_count_after_stale_write = await connection.scalar(
                    text(
                        "SELECT count(*) FROM execution_events WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution_id},
                )
            assert event_count_after_stale_write == event_count_before

            completed = await repository.complete_execution(execution_id, expected_epoch=1)
            repeated = await repository.complete_execution(execution_id, expected_epoch=1)
            assert completed.state is ExecutionState.SUCCESS
            assert repeated == completed

            async with engine.connect() as connection:
                terminal_event_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM execution_events "
                        "WHERE execution_id = :execution_id "
                        "AND event_type = 'ExecutionSucceeded'"
                    ),
                    {"execution_id": execution_id},
                )
            assert terminal_event_count == 1
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_canonical_resource_metadata_and_uuid7_are_persisted() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "resource_contract",
                "namespace": f"tests.resources.{uuid4().hex}",
                "labels": {"team": "platform"},
                "annotations": {"purpose": "EPIC-002 verification"},
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution_id: UUID | None = None
        try:
            persisted_flow = await repository.apply_flow(flow, tenant_id="default")
            assert persisted_flow.resource_id.version == 7
            assert persisted_flow.tenant_id == "default"
            assert persisted_flow.metadata.labels == {"team": "platform"}
            assert persisted_flow.metadata.annotations == {"purpose": "EPIC-002 verification"}
            assert persisted_flow.metadata.resource_version >= 2
            assert persisted_flow.etag.startswith('"sha256:')

            execution = await repository.create_execution(flow, tenant_id="default", inputs={})
            execution_id = execution.execution_id
            task_runs = await repository.list_task_runs(execution_id)
            assert execution_id.version == 7
            assert all(task.task_run_id.version == 7 for task in task_runs)

            async with engine.connect() as connection:
                row = (
                    (
                        await connection.execute(
                            text(
                                "SELECT namespaces.id AS namespace_id, flows.id AS flow_id, "
                                "flow_revisions.id AS revision_id "
                                "FROM flows "
                                "JOIN namespaces ON namespaces.id = flows.namespace_id "
                                "JOIN flow_revisions ON flow_revisions.flow_id = flows.id "
                                "WHERE namespaces.name = :namespace AND flows.flow_key = :flow_key "
                                "ORDER BY flow_revisions.revision DESC LIMIT 1"
                            ),
                            {"namespace": flow.namespace, "flow_key": flow.id},
                        )
                    )
                    .mappings()
                    .one()
                )
                event_ids = (
                    (
                        await connection.execute(
                            text(
                                "SELECT event_id FROM execution_events "
                                "WHERE execution_id = :execution_id"
                            ),
                            {"execution_id": execution_id},
                        )
                    )
                    .scalars()
                    .all()
                )
            assert UUID(str(row["namespace_id"])).version == 7
            assert UUID(str(row["flow_id"])).version == 7
            assert UUID(str(row["revision_id"])).version == 7
            assert all(UUID(str(event_id)).version == 7 for event_id in event_ids)
        finally:
            if execution_id is not None:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_core_log_emits_execution_context(
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "core_log",
                "namespace": f"tests.core.log.{uuid4().hex}",
                "tasks": [
                    {
                        "id": "announce",
                        "type": "core.log",
                        "message": "durable message",
                    }
                ],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository)
        execution_id = await executor.create_execution(flow)

        try:
            with caplog.at_level("INFO", logger="amesh.task.core.log"):
                completed = await executor.run_to_completion(flow, execution_id)
            assert completed.state is ExecutionState.SUCCESS
            record = next(
                record for record in caplog.records if record.name == "amesh.task.core.log"
            )
            assert record.message == "durable message"
            assert record.execution_id == str(execution_id)
            assert record.task_id == "announce"
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
