from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresBackfillRepository, PostgresExecutionRepository
from amesh.backfills import BackfillService
from amesh.domain import (
    BackfillReplaySource,
    BackfillResourcePin,
    BackfillSelection,
    BackfillSpec,
    BackfillState,
    frozen_input_digest,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _flow(namespace: str) -> FlowDefinition:
    return FlowDefinition(
        id="historical_flow",
        namespace=namespace,
        revision=3,
        tasks=[TaskDefinition(id="capture", type="test.capture")],
    )


async def _capture(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> dict[str, object]:
    del task
    return {"trigger": context.trigger, "inputs": context.inputs}


async def _cleanup(engine: AsyncEngine, namespace: str) -> None:
    async with engine.begin() as connection:
        backfill_ids = list(
            await connection.scalars(
                text("SELECT id FROM backfills WHERE namespace_name = :namespace"),
                {"namespace": namespace},
            )
        )
        execution_ids = list(
            await connection.scalars(
                text("SELECT id FROM executions WHERE namespace_name = :namespace"),
                {"namespace": namespace},
            )
        )
        partition_keys = [
            *(f"backfill:{value}" for value in backfill_ids),
            *(f"execution:{value}" for value in execution_ids),
        ]
        await connection.execute(
            text("DELETE FROM durable_work_queue WHERE partition_key = ANY(CAST(:keys AS text[]))"),
            {"keys": partition_keys},
        )
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = ANY(CAST(:keys AS text[]))"),
            {"keys": partition_keys},
        )
        await connection.execute(
            text("DELETE FROM backfills WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": backfill_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_reservations WHERE resource_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[]))) "
                "OR resource_id = ANY(CAST(:ids AS uuid[]))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_requests WHERE resource_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[]))) "
                "OR resource_id = ANY(CAST(:ids AS uuid[]))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM task_run_events WHERE execution_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM task_attempts WHERE task_run_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[])))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM execution_events WHERE execution_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM executions WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )


def test_backfill_preview_lifecycle_rate_and_restart_resume() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        executions = PostgresExecutionRepository(engine)
        backfills = PostgresBackfillRepository(engine)
        service = BackfillService(executions, backfills)
        namespace = f"tests.backfills.{uuid4().hex}"
        flow = _flow(namespace)
        spec = BackfillSpec(
            namespace=namespace,
            flowId=flow.id,
            flowRevision=flow.revision,
            selection=BackfillSelection(partitions=("2026-08-20", "2026-08-21", "2026-08-22")),
            inputs={"mode": "historical"},
            labels={"purpose": "qualification"},
            maxConcurrency=1,
            ratePerMinute=100,
            priority=42,
        )
        try:
            await executions.create_execution(flow, tenant_id="default", inputs={})
            preview = await service.preview(spec, tenant_id="default")
            assert preview.execution_count == 3
            assert preview.estimated_task_runs == 3
            assert "creates no executions" in preview.warnings[0]

            created = await service.create(spec, tenant_id="default", actor_id="test:author")
            assert created.state is BackfillState.RUNNING
            assert (created.total, created.pending, created.running) == (3, 2, 1)
            async with engine.connect() as connection:
                applied_priority = await connection.scalar(
                    text(
                        "SELECT admission_requests.priority "
                        "FROM backfill_items "
                        "JOIN admission_requests "
                        "ON admission_requests.resource_id = backfill_items.execution_id "
                        "WHERE backfill_items.backfill_id = :backfill_id"
                    ),
                    {"backfill_id": created.backfill_id},
                )
            assert applied_priority == 42

            paused = await backfills.transition_backfill(
                created.backfill_id,
                BackfillState.PAUSED,
                tenant_id="default",
                actor_id="test:author",
                reason="operator pause",
            )
            assert paused.state is BackfillState.PAUSED
            assert await service.process_active(tenant_id="default") == 0
            await backfills.transition_backfill(
                created.backfill_id,
                BackfillState.RUNNING,
                tenant_id="default",
                actor_id="test:author",
                reason="operator resume",
            )

            executor = InProcessExecutor(executions, handlers={"test.capture": _capture})
            while True:
                current = await backfills.get_backfill(created.backfill_id, tenant_id="default")
                active = [
                    execution
                    for execution in await executions.list_executions(
                        tenant_id="default", limit=1000
                    )
                    if execution.labels.get("amesh.backfill.id") == str(created.backfill_id)
                    and execution.state.value == "RUNNING"
                ]
                for execution in active:
                    await executor.run_to_completion(
                        flow,
                        execution.execution_id,
                        tenant_id="default",
                    )
                restarted_service = BackfillService(executions, backfills)
                current = await restarted_service.pump(
                    created.backfill_id,
                    tenant_id="default",
                )
                if current.state is BackfillState.COMPLETED:
                    break

            assert (current.pending, current.running, current.succeeded) == (0, 0, 3)
            assert current.actual_cost_units == 3
            assert current.duration_seconds > 0
            async with engine.connect() as connection:
                events = await connection.scalar(
                    text("SELECT count(*) FROM backfill_events WHERE backfill_id = :id"),
                    {"id": created.backfill_id},
                )
                outbox = await connection.scalar(
                    text(
                        "SELECT count(*) FROM messages_outbox WHERE partition_key = :partition_key"
                    ),
                    {"partition_key": f"backfill:{created.backfill_id}"},
                )
            assert int(events or 0) >= 6
            assert outbox == events

            rate_limited = await service.create(
                spec.model_copy(
                    update={
                        "selection": BackfillSelection(partitions=("r1", "r2", "r3")),
                        "max_concurrency": 10,
                        "rate_per_minute": 1,
                    }
                ),
                tenant_id="default",
                actor_id="test:author",
            )
            assert (rate_limited.pending, rate_limited.running) == (2, 1)
            await backfills.transition_backfill(
                rate_limited.backfill_id,
                BackfillState.CANCELLED,
                tenant_id="default",
                actor_id="test:author",
                reason="rate assertion complete",
            )
        finally:
            await _cleanup(engine, namespace)
            await engine.dispose()

    asyncio.run(scenario())


def test_replay_preserves_source_lineage_inputs_and_idempotency() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        executions = PostgresExecutionRepository(engine)
        backfills = PostgresBackfillRepository(engine)
        service = BackfillService(executions, backfills)
        namespace = f"tests.replay.{uuid4().hex}"
        flow = _flow(namespace)
        try:
            source = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={"source": "kept", "override": "old"},
                labels={"sourceLabel": "kept"},
            )
            determinism = source.trigger["_ameshDeterminism"]
            spec = BackfillSpec(
                namespace=namespace,
                flowId=flow.id,
                flowRevision=flow.revision,
                selection=BackfillSelection(sourceExecutionIds=(source.execution_id,)),
                idempotencyKey="replay-source-lineage-1",
                replaySources=(
                    BackfillReplaySource(
                        sourceExecutionId=source.execution_id,
                        frozenInputDigest=frozen_input_digest(source.inputs),
                        resourcePins=(
                            BackfillResourcePin(
                                key="flow",
                                revision=source.flow_revision,
                                digest=determinism["semanticHash"],
                            ),
                            BackfillResourcePin(
                                key="plugin-set",
                                revision=source.flow_revision,
                                digest=determinism["pluginSetHash"],
                            ),
                            BackfillResourcePin(
                                key="determinism-envelope",
                                revision=source.flow_revision,
                                digest=determinism["envelopeDigest"],
                            ),
                        ),
                    ),
                ),
                labels={"replay": "yes"},
                maxConcurrency=1,
                ratePerMinute=10,
            )
            replay = await service.create(spec, tenant_id="default", actor_id="test:author")
            replayed = next(
                execution
                for execution in await executions.list_executions(tenant_id="default", limit=1000)
                if execution.labels.get("amesh.backfill.id") == str(replay.backfill_id)
            )
            assert replayed.inputs == {"source": "kept", "override": "old"}
            assert replayed.labels["sourceLabel"] == "kept"
            assert replayed.trigger["source"] == "replay"
            assert replayed.trigger["sourceExecutionId"] == str(source.execution_id)

            restarted_service = BackfillService(executions, backfills)
            await restarted_service.pump(replay.backfill_id, tenant_id="default")
            generated = [
                execution
                for execution in await executions.list_executions(tenant_id="default", limit=1000)
                if execution.labels.get("amesh.backfill.id") == str(replay.backfill_id)
            ]
            assert [item.execution_id for item in generated] == [replayed.execution_id]
            async with engine.connect() as connection:
                lineage = await connection.scalar(
                    text(
                        "SELECT source_execution_id FROM backfill_items "
                        "WHERE backfill_id = :backfill_id"
                    ),
                    {"backfill_id": replay.backfill_id},
                )
            assert lineage == source.execution_id

            duplicate = await service.create(spec, tenant_id="default", actor_id="test:author")
            assert duplicate.backfill_id == replay.backfill_id
            assert (
                len(
                    [
                        execution
                        for execution in await executions.list_executions(
                            tenant_id="default", limit=1000
                        )
                        if execution.labels.get("amesh.backfill.id") == str(replay.backfill_id)
                    ]
                )
                == 1
            )

            intentional = await service.create(
                spec.model_copy(update={"idempotency_key": "replay-source-lineage-2"}),
                tenant_id="default",
                actor_id="test:author",
            )
            assert intentional.backfill_id != replay.backfill_id

            cancelled = await backfills.transition_backfill(
                replay.backfill_id,
                BackfillState.CANCELLED,
                tenant_id="default",
                actor_id="test:author",
                reason="stop replay",
            )
            assert cancelled.state is BackfillState.CANCELLED
        finally:
            await _cleanup(engine, namespace)
            await engine.dispose()

    asyncio.run(scenario())
