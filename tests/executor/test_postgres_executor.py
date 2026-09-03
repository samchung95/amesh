from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from tests.fixtures.task_schemas import registered_test_task_registry

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresMetadataRepository
from amesh.domain import AdmissionOutcome, AdmissionResourceType, ExecutionState
from amesh.dsl import FlowDefinition, TaskDefinition, validate_flow_document
from amesh.executor import InProcessExecutor, TaskExecutionContext, TaskExecutionError
from amesh.ports import (
    ExecutionLaunchSource,
    ExecutionStateConflictError,
    PersistedTaskRun,
    TaskRunState,
    TaskStateConflictError,
)
from amesh.tasks import core_control_handlers, core_data_handlers

ROOT = Path(__file__).resolve().parents[2]


def load_parallel_dag() -> FlowDefinition:
    result = validate_flow_document((ROOT / "examples" / "parallel-dag.yaml").read_bytes())
    assert result.valid
    assert result.canonical is not None
    return FlowDefinition.model_validate(result.canonical)


def test_execution_guard_prevents_overlap_and_releases_with_owner(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        first = PostgresExecutionRepository(engine)
        second = PostgresExecutionRepository(engine)
        execution_id = uuid4()
        try:
            async with first.execution_guard("default", execution_id) as first_acquired:
                assert first_acquired
                async with second.execution_guard("default", execution_id) as overlap_acquired:
                    assert not overlap_acquired
            async with second.execution_guard("default", execution_id) as recovered_acquired:
                assert recovered_acquired
        finally:
            await engine.dispose()

    asyncio.run(scenario())


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


async def execution_transaction_snapshot(
    engine: AsyncEngine,
    execution_id: UUID,
    task_run_id: UUID,
) -> dict[str, object]:
    async with engine.connect() as connection:
        row = (
            (
                await connection.execute(
                    text(
                        """
                        SELECT
                            (SELECT state FROM executions WHERE id = :execution_id)
                                AS execution_state,
                            (SELECT version FROM executions WHERE id = :execution_id)
                                AS execution_version,
                            (SELECT outputs FROM executions WHERE id = :execution_id)
                                AS execution_outputs,
                            (SELECT lifecycle_evidence FROM executions WHERE id = :execution_id)
                                AS execution_evidence,
                            (SELECT state FROM task_runs WHERE id = :task_run_id)
                                AS task_state,
                            (SELECT version FROM task_runs WHERE id = :task_run_id)
                                AS task_version,
                            (SELECT terminal_result FROM task_runs WHERE id = :task_run_id)
                                AS task_result,
                            (SELECT control_evidence FROM task_runs WHERE id = :task_run_id)
                                AS task_evidence,
                            (SELECT count(*) FROM execution_events
                             WHERE execution_id = :execution_id) AS execution_event_count,
                            (SELECT count(*) FROM task_run_events
                             WHERE execution_id = :execution_id) AS task_event_count,
                            (SELECT count(*) FROM messages_outbox
                             WHERE partition_key = :partition_key) AS outbox_count,
                            (SELECT count(*) FROM execution_evidence_events
                             WHERE execution_id = :execution_id) AS evidence_event_count,
                            (SELECT count(*) FROM execution_outputs
                             WHERE execution_id = :execution_id) AS output_evidence_count,
                            (SELECT count(*) FROM check_evaluations
                             WHERE execution_id = :execution_id) AS check_evidence_count,
                            (SELECT count(*) FROM admission_requests
                             WHERE resource_id IN (:execution_id, :task_run_id))
                                AS admission_count,
                            (SELECT count(*) FROM admission_reservations
                             WHERE resource_id IN (:execution_id, :task_run_id))
                                AS reservation_count,
                            (SELECT count(*) FROM admission_requests
                             WHERE resource_id IN (:execution_id, :task_run_id)
                               AND outcome = 'RELEASED') AS released_admission_count,
                            (SELECT count(*) FROM admission_reservations
                             WHERE resource_id IN (:execution_id, :task_run_id)
                               AND released_at IS NOT NULL) AS released_reservation_count
                        """
                    ),
                    {
                        "execution_id": execution_id,
                        "task_run_id": task_run_id,
                        "partition_key": f"execution:{execution_id}",
                    },
                )
            )
            .mappings()
            .one()
        )
    return dict(row)


def test_create_execution_rolls_back_all_rows_when_initial_events_fail(
    migrated_test_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "creation_transaction_rollback",
                "namespace": f"tests.transactions.create.{uuid4().hex}",
                "tasks": [{"id": "only", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        original_insert_initial_events = repository._insert_initial_events
        attempted_execution_id: UUID | None = None

        async def fail_after_initial_events(
            connection: AsyncConnection,
            tenant_id: UUID,
            execution_id: UUID,
            occurred_at: datetime,
            actor_id: str,
            outcome: AdmissionOutcome,
            reason: str,
            trace_context: str,
        ) -> None:
            nonlocal attempted_execution_id
            attempted_execution_id = execution_id
            await original_insert_initial_events(
                connection,
                tenant_id,
                execution_id,
                occurred_at,
                actor_id,
                outcome,
                reason,
                trace_context,
            )
            raise RuntimeError("injected initial-event failure")

        monkeypatch.setattr(repository, "_insert_initial_events", fail_after_initial_events)
        try:
            with pytest.raises(RuntimeError, match="injected initial-event failure"):
                await repository.create_execution(flow, tenant_id="default", inputs={})

            assert attempted_execution_id is not None
            snapshot = await execution_transaction_snapshot(
                engine,
                attempted_execution_id,
                attempted_execution_id,
            )
            assert all(value is None or value == 0 for value in snapshot.values())
        finally:
            await engine.dispose()

    asyncio.run(scenario())


@pytest.mark.parametrize("completion_kind", ("task", "execution"))
def test_completion_failure_rolls_back_primary_and_terminal_side_effects(
    migrated_test_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    completion_kind: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": f"{completion_kind}_completion_transaction_rollback",
                "namespace": f"tests.transactions.{completion_kind}.{uuid4().hex}",
                "tasks": [{"id": "only", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        task = (await repository.list_task_runs(execution.execution_id, tenant_id="default"))[0]
        if completion_kind == "task":
            task = await repository.start_task(task.task_run_id, tenant_id="default")
        before = await execution_transaction_snapshot(
            engine,
            execution.execution_id,
            task.task_run_id,
        )
        original_release_admission = repository._release_admission_tx

        async def fail_after_admission_release(
            connection: AsyncConnection,
            tenant_id: UUID,
            resource_type: AdmissionResourceType,
            resource_id: UUID,
            reason: str,
            *,
            replacement: bool = False,
        ) -> bool:
            await original_release_admission(
                connection,
                tenant_id,
                resource_type,
                resource_id,
                reason,
                replacement=replacement,
            )
            raise RuntimeError("injected post-update failure")

        monkeypatch.setattr(repository, "_release_admission_tx", fail_after_admission_release)
        try:
            with pytest.raises(RuntimeError, match="injected post-update failure"):
                if completion_kind == "task":
                    await repository.complete_task(
                        task.task_run_id,
                        task.current_attempt,
                        {"value": "must roll back"},
                        tenant_id="default",
                        evidence={"transactionTest": True},
                    )
                else:
                    await repository.complete_execution(
                        execution.execution_id,
                        tenant_id="default",
                        expected_epoch=execution.epoch,
                        outputs={"value": "must roll back"},
                    )

            after = await execution_transaction_snapshot(
                engine,
                execution.execution_id,
                task.task_run_id,
            )
            assert after == before
        finally:
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_core_utility_pack_persists_deterministic_outputs(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        flow = FlowDefinition.model_validate(
            {
                "id": "core_utilities",
                "namespace": f"tests.utilities.{uuid4().hex}",
                "tasks": [
                    {
                        "id": "parse",
                        "type": "core.data.json",
                        "operation": "parse",
                        "input": '{"ready":true,"name":"amesh"}',
                    },
                    {
                        "id": "normalize",
                        "type": "core.data.text",
                        "dependsOn": ["parse"],
                        "operation": "upper",
                        "input": "{{ outputs.parse.value.name }}",
                    },
                    {
                        "id": "assert_ready",
                        "type": "core.assert",
                        "dependsOn": ["parse"],
                        "value": "{{ outputs.parse.value.ready }}",
                    },
                    {
                        "id": "debug",
                        "type": "core.debug",
                        "dependsOn": ["normalize", "assert_ready"],
                        "include": ["outputs"],
                    },
                ],
            }
        )
        executor = InProcessExecutor(
            repository,
            handlers={**core_data_handlers(), **core_control_handlers()},
        )
        execution_id = await executor.create_execution(flow, tenant_id="default")
        try:
            completed = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert completed.state is ExecutionState.SUCCESS
            results = {item.task_id: item.result for item in completed.task_runs}
            assert results["parse"] == {
                "format": "json",
                "operation": "parse",
                "value": {"ready": True, "name": "amesh"},
            }
            assert results["normalize"] == {
                "format": "text",
                "operation": "upper",
                "value": "AMESH",
            }
            assert results["assert_ready"] == {"asserted": True}
            assert results["debug"]["secretsRedacted"] is False
            assert results["debug"]["secretScopes"] == []
            assert "parse" in results["debug"]["context"]["outputs"]
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_parallel_dag_resumes_from_persisted_task_state_after_restart(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        source_flow = load_parallel_dag()
        flow = source_flow.model_copy(update={"namespace": f"tests.executor.{uuid4().hex}"})
        first_engine = create_async_engine(migrated_test_database_url)
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

        resumed_engine = create_async_engine(migrated_test_database_url)
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


def test_all_execution_launch_sources_are_persisted(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "launch_sources",
                "namespace": f"tests.launch.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
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
                assert execution.trigger["launch_key"] == source.value
                assert execution.trigger["source"] == source.value
                envelope = execution.trigger["_ameshDeterminism"]
                assert envelope["revision"] == 1
                assert envelope["nodes"][0]["logicalId"] == "done"
                assert envelope["nodes"][0]["order"] == 0
                assert envelope["policyPins"] == []
                assert envelope["dynamicBounds"] == []
                assert envelope["worstCaseTaskRuns"] == 1
                assert envelope["envelopeDigest"]
        finally:
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_optimistic_task_start_allows_only_one_executor_owner(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "executor_ownership",
                "namespace": f"tests.executor.ownership.{uuid4().hex}",
                "tasks": [{"id": "only", "type": "core.return", "value": "ok"}],
            }
        )
        first_engine = create_async_engine(migrated_test_database_url)
        second_engine = create_async_engine(migrated_test_database_url)
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


def test_executor_terminates_unsatisfiable_graph_with_diagnostics(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
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
        engine = create_async_engine(migrated_test_database_url)
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


def test_terminal_execution_event_is_fenced_by_epoch(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = load_parallel_dag().model_copy(update={"namespace": f"tests.fencing.{uuid4().hex}"})
        engine = create_async_engine(migrated_test_database_url)
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


def test_rolled_back_state_event_does_not_escape_through_outbox(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = load_parallel_dag().model_copy(update={"namespace": f"tests.outbox.{uuid4().hex}"})
        engine = create_async_engine(migrated_test_database_url)
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


def test_duplicate_task_result_is_idempotent_and_illegal_transition_is_recorded(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "task_event_contract",
                "namespace": f"tests.task.events.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
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


def test_canonical_resource_metadata_and_uuid7_are_persisted(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "resource_contract",
                "namespace": f"tests.resources.{uuid4().hex}",
                "labels": {"team": "platform"},
                "annotations": {"purpose": "EPIC-002 verification"},
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        execution_id: UUID | None = None
        try:
            persisted_flow = await repository.apply_flow(flow, tenant_id="default")
            assert persisted_flow.resource_id.version == 7
            assert persisted_flow.tenant_id == "default"
            assert persisted_flow.metadata.labels == {
                "team": "platform",
                "amesh.namespace": flow.namespace,
                "amesh.flow.id": flow.id,
                "amesh.flow.revision": "1",
            }
            assert persisted_flow.metadata.annotations == {"purpose": "EPIC-002 verification"}
            assert persisted_flow.metadata.resource_version >= 2
            assert persisted_flow.etag.startswith('"sha256:')

            execution = await repository.create_execution(flow, tenant_id="default", inputs={})
            execution_id = execution.execution_id
            task_runs = await repository.list_task_runs(
                execution_id,
                tenant_id="default",
            )
            assert execution.labels["amesh.execution.id"] == str(execution.execution_id)
            assert task_runs[0].labels["amesh.task.id"] == "done"
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


def test_list_flows_normalizes_transaction_timestamp_skew(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "timestamp_skew",
                "namespace": f"tests.resources.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        engine = create_async_engine(migrated_test_database_url)
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
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
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
        engine = create_async_engine(migrated_test_database_url)
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


def test_executor_populates_the_documented_expression_context(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
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
        engine = create_async_engine(migrated_test_database_url)
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


def test_nested_flowables_are_durable_bounded_and_policy_driven(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:

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
        engine = create_async_engine(migrated_test_database_url)
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
            executor = InProcessExecutor(
                repository,
                handlers=handlers,
                resource_registry=registered_test_task_registry(*handlers),
            )
            dag_execution_id = await executor.create_execution(dag_flow, tenant_id="default")
            execution_ids.append(dag_execution_id)

            first = await executor.run_ready(dag_flow, dag_execution_id, tenant_id="default")
            assert first.tasks_run == 1
            await engine.dispose()

            engine = create_async_engine(migrated_test_database_url)
            repository = PostgresExecutionRepository(engine)
            executor = InProcessExecutor(
                repository,
                handlers=handlers,
                resource_registry=registered_test_task_registry(*handlers),
            )
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
            continue_executor = InProcessExecutor(
                repository,
                handlers=handlers,
                resource_registry=registered_test_task_registry(*handlers),
            )
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
            fail_fast_executor = InProcessExecutor(
                repository,
                handlers=handlers,
                resource_registry=registered_test_task_registry(*handlers),
            )
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
            collect_executor = InProcessExecutor(
                repository,
                handlers=handlers,
                resource_registry=registered_test_task_registry(*handlers),
            )
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
