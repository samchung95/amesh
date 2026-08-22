from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresMetadataRepository
from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, TaskDefinition, validate_flow_document
from amesh.executor import InProcessExecutor, TaskExecutionContext, TaskExecutionError
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionStateConflictError,
    PersistedTaskRun,
    TaskRunState,
    TaskStateConflictError,
)

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
        for table in ("execution_logs", "execution_metrics"):
            await connection.execute(
                text(f"DELETE FROM {table} WHERE execution_id = :execution_id"),
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


def test_parallel_dag_resumes_from_persisted_task_state_after_restart() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        source_flow = load_parallel_dag()
        flow = source_flow.model_copy(update={"namespace": f"tests.executor.{uuid4().hex}"})
        first_engine = create_async_engine(TEST_DATABASE_URL)
        first_repository = PostgresExecutionRepository(first_engine)
        first_executor = InProcessExecutor(first_repository)
        execution_id = await first_executor.create_execution(flow, tenant_id="default")

        first_progress = await first_executor.run_ready(
            flow,
            execution_id,
            tenant_id="default",
            max_tasks=1,
        )
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
            completed = await resumed_executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )

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
                task_events = (
                    (
                        await connection.execute(
                            text(
                                "SELECT task_runs.task_path, task_run_events.event_type "
                                "FROM task_run_events "
                                "JOIN task_runs ON task_runs.id = task_run_events.task_run_id "
                                "WHERE task_run_events.execution_id = :execution_id "
                                "ORDER BY task_runs.task_path, task_run_events.sequence"
                            ),
                            {"execution_id": execution_id},
                        )
                    )
                    .tuples()
                    .all()
                )
                outbox_count = await connection.scalar(
                    text("SELECT count(*) FROM messages_outbox WHERE partition_key = :key"),
                    {"key": f"execution:{execution_id}"},
                )
                outbox_contracts = (
                    (
                        await connection.execute(
                            text(
                                "SELECT subject, envelope ->> 'message_type' "
                                "FROM messages_outbox WHERE partition_key = :key"
                            ),
                            {"key": f"execution:{execution_id}"},
                        )
                    )
                    .tuples()
                    .all()
                )
            assert events == [
                "ExecutionCreated",
                "ExecutionQueued",
                "ExecutionStarted",
                "ExecutionSucceeded",
            ]
            for task_id in ("combine", "extract_a", "extract_b"):
                assert [event for task, event in task_events if task == task_id] == [
                    "TaskRunCreated",
                    "TaskRunStarted",
                    "TaskRunSucceeded",
                ]
            assert outbox_count == len(events) + len(task_events)
            assert outbox_contracts.count(("task-dispatch", "DispatchTaskRun")) == 3
            assert ("execution-events", "ExecutionSucceeded") in outbox_contracts
        finally:
            await cleanup_execution(resumed_engine, execution_id)
            await resumed_engine.dispose()

    asyncio.run(scenario())


def test_all_execution_launch_sources_are_persisted() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "launch_sources",
                "namespace": f"tests.launch.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution_ids: list[UUID] = []
        try:
            for source in ExecutionLaunchSource:
                execution = await repository.create_execution(
                    flow,
                    tenant_id="default",
                    inputs={},
                    trigger={"launch_key": source.value},
                    launch_source=source,
                )
                execution_ids.append(execution.execution_id)
                assert execution.trigger == {
                    "launch_key": source.value,
                    "source": source.value,
                }
        finally:
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_optimistic_task_start_allows_only_one_executor_owner() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "executor_ownership",
                "namespace": f"tests.executor.ownership.{uuid4().hex}",
                "tasks": [{"id": "only", "type": "core.return", "value": "ok"}],
            }
        )
        first_engine = create_async_engine(TEST_DATABASE_URL)
        second_engine = create_async_engine(TEST_DATABASE_URL)
        first_repository = PostgresExecutionRepository(first_engine)
        second_repository = PostgresExecutionRepository(second_engine)
        execution = await first_repository.create_execution(flow, tenant_id="default", inputs={})
        task_run = (
            await first_repository.list_task_runs(execution.execution_id, tenant_id="default")
        )[0]
        try:
            results = await asyncio.gather(
                first_repository.start_task(task_run.task_run_id, tenant_id="default"),
                second_repository.start_task(task_run.task_run_id, tenant_id="default"),
                return_exceptions=True,
            )
            assert sum(isinstance(result, PersistedTaskRun) for result in results) == 1
            assert sum(isinstance(result, TaskStateConflictError) for result in results) == 1
            async with first_engine.connect() as connection:
                started_events = await connection.scalar(
                    text(
                        "SELECT count(*) FROM task_run_events "
                        "WHERE task_run_id = :task_run_id AND event_type = 'TaskRunStarted'"
                    ),
                    {"task_run_id": task_run.task_run_id},
                )
                dispatches = await connection.scalar(
                    text(
                        "SELECT count(*) FROM messages_outbox "
                        "WHERE partition_key = :partition_key AND subject = 'task-dispatch'"
                    ),
                    {"partition_key": f"execution:{execution.execution_id}"},
                )
            assert started_events == 1
            assert dispatches == 1
        finally:
            await cleanup_execution(first_engine, execution.execution_id)
            await first_engine.dispose()
            await second_engine.dispose()

    asyncio.run(scenario())


def test_executor_terminates_unsatisfiable_graph_with_diagnostics() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "unsatisfiable_graph",
                "namespace": f"tests.executor.deadlock.{uuid4().hex}",
                "tasks": [
                    {"id": "upstream", "type": "core.return", "value": "ok"},
                    {
                        "id": "blocked",
                        "type": "core.return",
                        "dependsOn": ["upstream"],
                        "value": "never",
                    },
                ],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        try:
            upstream = next(
                task_run
                for task_run in await repository.list_task_runs(
                    execution.execution_id,
                    tenant_id="default",
                )
                if task_run.task_id == "upstream"
            )
            running = await repository.start_task(upstream.task_run_id, tenant_id="default")
            await repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                "worker vanished after recording failure",
                tenant_id="default",
            )

            progress = await executor.run_ready(
                flow,
                execution.execution_id,
                tenant_id="default",
            )
            assert progress.state is ExecutionState.FAILED
            async with engine.connect() as connection:
                reason = await connection.scalar(
                    text(
                        "SELECT reason FROM execution_events "
                        "WHERE execution_id = :execution_id "
                        "AND event_type = 'ExecutionFailed'"
                    ),
                    {"execution_id": execution.execution_id},
                )
            assert reason == (
                "unsatisfiable execution graph; failed=['upstream']; blocked=['blocked']"
            )
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

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
                outbox_count_before = await connection.scalar(
                    text("SELECT count(*) FROM messages_outbox WHERE partition_key = :key"),
                    {"key": f"execution:{execution_id}"},
                )

            with pytest.raises(ExecutionStateConflictError, match="fenced at epoch 1"):
                await repository.complete_execution(
                    execution_id,
                    tenant_id="default",
                    expected_epoch=2,
                )

            unchanged = await repository.get_execution(execution_id, tenant_id="default")
            assert unchanged.state is ExecutionState.RUNNING
            async with engine.connect() as connection:
                event_count_after_stale_write = await connection.scalar(
                    text(
                        "SELECT count(*) FROM execution_events WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution_id},
                )
                rejection = (
                    (
                        await connection.execute(
                            text(
                                "SELECT code, current_state, current_epoch "
                                "FROM transition_rejections "
                                "WHERE aggregate_type = 'execution' "
                                "AND aggregate_id = :execution_id"
                            ),
                            {"execution_id": execution_id},
                        )
                    )
                    .mappings()
                    .one()
                )
                outbox_count_after_stale_write = await connection.scalar(
                    text("SELECT count(*) FROM messages_outbox WHERE partition_key = :key"),
                    {"key": f"execution:{execution_id}"},
                )
            assert event_count_after_stale_write == event_count_before
            assert outbox_count_after_stale_write == outbox_count_before
            assert rejection == {
                "code": "EPOCH_CONFLICT",
                "current_state": "RUNNING",
                "current_epoch": 1,
            }

            completed = await repository.complete_execution(
                execution_id,
                tenant_id="default",
                expected_epoch=1,
            )
            repeated = await repository.complete_execution(
                execution_id,
                tenant_id="default",
                expected_epoch=1,
            )
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


def test_rolled_back_state_event_does_not_escape_through_outbox() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = load_parallel_dag().model_copy(update={"namespace": f"tests.outbox.{uuid4().hex}"})
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        execution_id = execution.execution_id
        rolled_back_event_id = uuid4()

        try:
            with pytest.raises(RuntimeError, match="force transaction rollback"):
                async with engine.begin() as connection:
                    tenant_id = await connection.scalar(
                        text("SELECT id FROM tenants WHERE slug = 'default'")
                    )
                    await connection.execute(
                        text(
                            "UPDATE executions SET version = version + 1 WHERE id = :execution_id"
                        ),
                        {"execution_id": execution_id},
                    )
                    await connection.execute(
                        text(
                            "INSERT INTO execution_events ("
                            "tenant_id, execution_id, sequence, event_id, event_type, "
                            "schema_version, idempotency_key, correlation_id, actor_id, "
                            "occurred_at, payload) VALUES ("
                            ":tenant_id, :execution_id, 4, :event_id, 'ExecutionPaused', "
                            "2, :idempotency_key, :correlation_id, 'test', now(), '{}'::jsonb)"
                        ),
                        {
                            "tenant_id": tenant_id,
                            "execution_id": execution_id,
                            "event_id": rolled_back_event_id,
                            "idempotency_key": str(rolled_back_event_id),
                            "correlation_id": uuid4(),
                        },
                    )
                    raise RuntimeError("force transaction rollback")

            persisted = await repository.get_execution(execution_id, tenant_id="default")
            assert persisted.version == execution.version
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text("SELECT count(*) FROM execution_events WHERE event_id = :event_id"),
                        {"event_id": rolled_back_event_id},
                    )
                    == 0
                )
                assert (
                    await connection.scalar(
                        text("SELECT count(*) FROM messages_outbox WHERE message_id = :event_id"),
                        {"event_id": rolled_back_event_id},
                    )
                    == 0
                )
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_duplicate_task_result_is_idempotent_and_illegal_transition_is_recorded() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "task_event_contract",
                "namespace": f"tests.task.events.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        execution_id = execution.execution_id

        try:
            task = (await repository.list_task_runs(execution_id, tenant_id="default"))[0]
            running = await repository.start_task(task.task_run_id, tenant_id="default")
            completed = await repository.complete_task(
                task.task_run_id,
                running.current_attempt,
                {"value": "ok"},
                tenant_id="default",
            )
            repeated = await repository.complete_task(
                task.task_run_id,
                running.current_attempt,
                {"value": "ok"},
                tenant_id="default",
            )
            assert repeated == completed

            with pytest.raises(TaskStateConflictError, match="is not running"):
                await repository.retry_task(
                    task.task_run_id,
                    running.current_attempt,
                    tenant_id="default",
                    retry_at=datetime.now(UTC),
                    reason="must not retry success",
                )

            persisted = (await repository.list_task_runs(execution_id, tenant_id="default"))[0]
            assert persisted.state is TaskRunState.SUCCESS
            async with engine.connect() as connection:
                task_event_count = await connection.scalar(
                    text("SELECT count(*) FROM task_run_events WHERE task_run_id = :task_run_id"),
                    {"task_run_id": task.task_run_id},
                )
                rejection = (
                    (
                        await connection.execute(
                            text(
                                "SELECT code, current_state FROM transition_rejections "
                                "WHERE aggregate_type = 'task_run' "
                                "AND aggregate_id = :task_run_id"
                            ),
                            {"task_run_id": task.task_run_id},
                        )
                    )
                    .mappings()
                    .one()
                )
            assert task_event_count == 3
            assert dict(rejection) == {
                "code": "ILLEGAL_TRANSITION",
                "current_state": "SUCCESS",
            }
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
            task_runs = await repository.list_task_runs(
                execution_id,
                tenant_id="default",
            )
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


def test_list_flows_normalizes_transaction_timestamp_skew() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition.model_validate(
            {
                "id": "timestamp_skew",
                "namespace": f"tests.resources.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        persisted_flow = await repository.apply_flow(flow, tenant_id="default")
        try:
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE flows "
                        "SET updated_at = created_at - interval '1 millisecond' "
                        "WHERE id = :flow_id"
                    ),
                    {"flow_id": persisted_flow.resource_id},
                )

            listed_flow = next(
                candidate
                for candidate in await repository.list_flows(tenant_id="default")
                if candidate.resource_id == persisted_flow.resource_id
            )

            assert listed_flow.metadata.updated_at == listed_flow.metadata.created_at
        finally:
            async with engine.begin() as connection:
                await connection.execute(
                    text("UPDATE flows SET updated_at = created_at WHERE id = :flow_id"),
                    {"flow_id": persisted_flow.resource_id},
                )
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
        execution_id = await executor.create_execution(flow, tenant_id="default")
        metadata = PostgresMetadataRepository(engine)

        try:
            with caplog.at_level("INFO", logger="amesh.task.core.log"):
                completed = await executor.run_to_completion(
                    flow,
                    execution_id,
                    tenant_id="default",
                )
            assert completed.state is ExecutionState.SUCCESS
            record = next(
                record for record in caplog.records if record.name == "amesh.task.core.log"
            )
            assert record.message == "durable message"
            assert record.tenant_id == "default"
            assert record.execution_id == str(execution_id)
            assert record.task_id == "announce"
            logs = await metadata.list_logs(execution_id, tenant_id="default")
            outputs = await metadata.list_outputs(execution_id, tenant_id="default")
            evidence = await metadata.list_evidence_events(execution_id, tenant_id="default")
            assert [(item.logger, item.message, item.attempt) for item in logs] == [
                ("amesh.task.core.log", "durable message", 1)
            ]
            assert logs[0].ingested_at is not None
            assert outputs[0].value == {"message": "durable message"}
            assert {item.kind.value for item in evidence} >= {"STATE", "LOG", "OUTPUT"}
            assert [item.cursor for item in evidence] == sorted(item.cursor for item in evidence)
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_executor_populates_the_documented_expression_context() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        namespace = f"tests.expressions.{uuid4().hex}"
        flow = FlowDefinition.model_validate(
            {
                "id": "expression_context",
                "namespace": namespace,
                "revision": 4,
                "labels": {"team": "platform"},
                "variables": {"region": "apac"},
                "tasks": [
                    {"id": "seed", "type": "core.return", "value": "loaded"},
                    {
                        "id": "context",
                        "type": "core.return",
                        "dependsOn": ["seed"],
                        "value": {
                            "flow": "{{ flow.id }}:{{ flow.revision }}",
                            "execution": "{{ execution.id }}",
                            "state": "{{ execution.state }}",
                            "tenant": "{{ execution.tenantId }}",
                            "task": "{{ task.id }}",
                            "taskrun": "{{ taskrun.id }}:{{ taskrun.attempt }}:{{ taskrun.state }}",
                            "trigger": "{{ trigger }}",
                            "input": "{{ inputs.name }}",
                            "output": "{{ outputs.seed.value }}",
                            "variable": "{{ vars.region }}",
                            "label": "{{ labels.team }}",
                            "namespace": "{{ namespace.id }}",
                        },
                    },
                ],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository)
        execution_id = await executor.create_execution(
            flow,
            tenant_id="default",
            inputs={"name": "Ada"},
        )

        try:
            completed = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            task_run = next(item for item in completed.task_runs if item.task_id == "context")
            assert task_run.result is not None
            value = task_run.result["value"]
            assert value == {
                "flow": "expression_context:4",
                "execution": str(execution_id),
                "state": "RUNNING",
                "tenant": "default",
                "task": "context",
                "taskrun": f"{task_run.task_run_id}:1:RUNNING",
                "trigger": {"source": "manual"},
                "input": "Ada",
                "output": "loaded",
                "variable": "apac",
                "label": "platform",
                "namespace": namespace,
            }
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_nested_flowables_are_durable_bounded_and_policy_driven() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

        observed_outputs: dict[str, tuple[str, ...]] = {}
        call_order: list[str] = []

        async def capture(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            task_id = task.id
            call_order.append(task_id)
            observed_outputs[task_id] = tuple(sorted(context.outputs))
            return {"task": task_id}

        async def fail(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del context
            task_id = task.id
            call_order.append(task_id)
            raise ValueError("expected child failure")

        handlers = {"tests.capture": capture, "tests.fail": fail}
        execution_ids: list[UUID] = []
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        try:
            dag_flow = FlowDefinition.model_validate(
                {
                    "id": "bounded_dag",
                    "namespace": f"tests.flowables.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "graph",
                            "type": "core.dag",
                            "maxConcurrency": 1,
                            "tasks": [
                                {"id": "left", "type": "tests.capture"},
                                {"id": "right", "type": "tests.capture"},
                                {
                                    "id": "join",
                                    "type": "tests.capture",
                                    "dependsOn": ["left", "right"],
                                },
                            ],
                        }
                    ],
                }
            )
            executor = InProcessExecutor(repository, handlers=handlers)
            dag_execution_id = await executor.create_execution(dag_flow, tenant_id="default")
            execution_ids.append(dag_execution_id)

            first = await executor.run_ready(dag_flow, dag_execution_id, tenant_id="default")
            assert first.tasks_run == 1
            await engine.dispose()

            engine = create_async_engine(TEST_DATABASE_URL)
            repository = PostgresExecutionRepository(engine)
            executor = InProcessExecutor(repository, handlers=handlers)
            second = await executor.run_ready(dag_flow, dag_execution_id, tenant_id="default")
            assert second.tasks_run == 1
            completed = await executor.run_ready(
                dag_flow,
                dag_execution_id,
                tenant_id="default",
            )
            assert completed.state is ExecutionState.SUCCESS
            assert completed.tasks_run == 1
            assert observed_outputs["left"] == ()
            assert observed_outputs["right"] == ()
            assert observed_outputs["join"] == ("left", "right")
            graph_run = next(item for item in completed.task_runs if item.task_id == "graph")
            assert graph_run.result is not None
            assert graph_run.result["childOrder"] == ["left", "right", "join"]

            continue_flow = FlowDefinition.model_validate(
                {
                    "id": "continue_sequence",
                    "namespace": f"tests.flowables.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "sequence",
                            "type": "core.sequential",
                            "failurePolicy": "CONTINUE_ON_ERROR",
                            "tasks": [
                                {"id": "expected_failure", "type": "tests.fail"},
                                {"id": "continued", "type": "tests.capture"},
                            ],
                        }
                    ],
                }
            )
            continue_executor = InProcessExecutor(repository, handlers=handlers)
            continue_execution_id = await continue_executor.create_execution(
                continue_flow,
                tenant_id="default",
            )
            execution_ids.append(continue_execution_id)
            continued = await continue_executor.run_to_completion(
                continue_flow,
                continue_execution_id,
                tenant_id="default",
            )
            assert continued.state is ExecutionState.SUCCESS
            assert call_order.index("expected_failure") < call_order.index("continued")
            sequence_run = next(item for item in continued.task_runs if item.task_id == "sequence")
            assert sequence_run.result is not None
            assert sequence_run.result["children"]["expected_failure"]["state"] == "FAILED"

            fail_fast_flow = FlowDefinition.model_validate(
                {
                    "id": "fail_fast_sequence",
                    "namespace": f"tests.flowables.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "sequence_fail_fast",
                            "type": "core.sequential",
                            "tasks": [
                                {"id": "stop_here", "type": "tests.fail"},
                                {"id": "never_run", "type": "tests.capture"},
                            ],
                        }
                    ],
                }
            )
            fail_fast_executor = InProcessExecutor(repository, handlers=handlers)
            fail_fast_execution_id = await fail_fast_executor.create_execution(
                fail_fast_flow,
                tenant_id="default",
            )
            execution_ids.append(fail_fast_execution_id)
            with pytest.raises(TaskExecutionError):
                await fail_fast_executor.run_ready(
                    fail_fast_flow,
                    fail_fast_execution_id,
                    tenant_id="default",
                )
            fail_fast_runs = await repository.list_task_runs(
                fail_fast_execution_id,
                tenant_id="default",
            )
            assert (
                next(item for item in fail_fast_runs if item.task_id == "never_run").state
                is TaskRunState.WAITING
            )

            collect_flow = FlowDefinition.model_validate(
                {
                    "id": "collect_parallel",
                    "namespace": f"tests.flowables.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "collection",
                            "type": "core.parallel",
                            "failurePolicy": "COLLECT_ALL",
                            "tasks": [
                                {"id": "collected_failure", "type": "tests.fail"},
                                {"id": "collected_success", "type": "tests.capture"},
                            ],
                        }
                    ],
                }
            )
            collect_executor = InProcessExecutor(repository, handlers=handlers)
            collect_execution_id = await collect_executor.create_execution(
                collect_flow,
                tenant_id="default",
            )
            execution_ids.append(collect_execution_id)
            with pytest.raises(TaskExecutionError):
                await collect_executor.run_ready(
                    collect_flow,
                    collect_execution_id,
                    tenant_id="default",
                )
            collect_runs = await repository.list_task_runs(
                collect_execution_id,
                tenant_id="default",
            )
            assert (
                next(item for item in collect_runs if item.task_id == "collected_success").state
                is TaskRunState.SUCCESS
            )
            collection_run = next(item for item in collect_runs if item.task_id == "collection")
            assert collection_run.state is TaskRunState.FAILED
            assert collection_run.result is not None
            assert collection_run.result["children"]["collected_failure"]["state"] == "FAILED"
            assert collection_run.result["children"]["collected_success"]["state"] == "SUCCESS"
        finally:
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
