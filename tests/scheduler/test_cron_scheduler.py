from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresExecutionRepository,
    PostgresSchedulerRepository,
    PostgresTriggerRuntimeRepository,
)
from amesh.domain import ExecutionState
from amesh.dsl.models import FlowDefinition, TaskDefinition, TriggerDefinition
from amesh.executor import InProcessExecutor
from amesh.ports import PersistedFlow, SchedulerFenceError
from amesh.scheduler import CronScheduler, ScheduleAction
from amesh.worker import schedule_once

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class ScopedPostgresExecutionRepository(PostgresExecutionRepository):
    def __init__(self, engine: AsyncEngine, namespace: str, flow_id: str) -> None:
        super().__init__(engine)
        self._namespace = namespace
        self._flow_id = flow_id

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]:
        flows = await super().list_flows(tenant_id=tenant_id)
        return [
            flow
            for flow in flows
            if flow.namespace == self._namespace and flow.flow_id == self._flow_id
        ]


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "DELETE FROM trigger_occurrence_events WHERE occurrence_id IN "
                "(SELECT occurrence_id FROM trigger_occurrences "
                "WHERE execution_id = :execution_id)"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM trigger_occurrences WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
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


def test_cron_occurrence_is_unique_across_scheduler_restart_and_renders_outputs() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        trigger = TriggerDefinition(
            id="every_minute",
            type="core.cron",
            cron="* * * * *",
            timezone="UTC",
        )
        flow = FlowDefinition(
            id="scheduled_expressions",
            namespace=f"tests.scheduler.{uuid4().hex}",
            variables={"suffix": "world"},
            triggers=[trigger],
            tasks=[
                TaskDefinition.model_validate(
                    {
                        "id": "first",
                        "type": "core.return",
                        "value": "{{ inputs.greeting }}",
                    }
                ),
                TaskDefinition.model_validate(
                    {
                        "id": "second",
                        "type": "core.return",
                        "dependsOn": ["first"],
                        "runIf": "{{ outputs.first.value == 'hello' }}",
                        "value": "{{ outputs.first.value }} {{ vars.suffix }}",
                    }
                ),
                TaskDefinition.model_validate(
                    {
                        "id": "guarded",
                        "type": "core.return",
                        "dependsOn": ["second"],
                        "runIf": "{{ outputs.second.value == 'never' }}",
                        "value": "not-run",
                    }
                ),
                TaskDefinition.model_validate(
                    {
                        "id": "trigger_context",
                        "type": "core.return",
                        "dependsOn": ["second"],
                        "value": {
                            "id": "{{ trigger.id }}",
                            "type": "{{ trigger.type }}",
                            "date": "{{ trigger.date }}",
                            "timezone": "{{ trigger.timezone }}",
                        },
                    }
                ),
            ],
        )
        scheduled_for = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)
        first_engine = create_async_engine(TEST_DATABASE_URL)
        second_engine = create_async_engine(TEST_DATABASE_URL)
        first_repository = PostgresExecutionRepository(first_engine)
        second_repository = PostgresExecutionRepository(second_engine)
        first_scheduler = CronScheduler(first_repository)
        second_scheduler = CronScheduler(second_repository)

        occurrence = first_scheduler.next_occurrence(
            trigger,
            after=scheduled_for - timedelta(minutes=1),
        )
        assert occurrence.scheduled_for == scheduled_for

        first, concurrent_duplicate = await asyncio.gather(
            first_scheduler.fire_occurrence(
                flow,
                trigger_id=trigger.id,
                scheduled_for=scheduled_for,
                tenant_id="default",
                inputs={"greeting": "hello"},
            ),
            second_scheduler.fire_occurrence(
                flow,
                trigger_id=trigger.id,
                scheduled_for=scheduled_for,
                tenant_id="default",
                inputs={"greeting": "hello"},
            ),
        )
        assert concurrent_duplicate.execution_id == first.execution_id
        assert {
            key: value
            for key, value in first.trigger.items()
            if not key.startswith("_amesh")
        } == {
            "source": "scheduled",
            "id": "every_minute",
            "type": "core.cron",
            "date": "2026-08-21T12:00:00+00:00",
            "timezone": "UTC",
        }
        assert first.trigger["_ameshDeterminism"]["revision"] == first.flow_revision

        try:
            completed = await InProcessExecutor(first_repository).run_to_completion(
                flow,
                first.execution_id,
                tenant_id="default",
            )
            assert completed.state is ExecutionState.SUCCESS
            results = {task_run.task_id: task_run.result for task_run in completed.task_runs}
            assert results["first"] == {"value": "hello"}
            assert results["second"] == {"value": "hello world"}
            assert results["guarded"] == {"skipped": True}
            assert results["trigger_context"] == {
                "value": {
                    "id": "every_minute",
                    "type": "core.cron",
                    "date": "2026-08-21T12:00:00+00:00",
                    "timezone": "UTC",
                }
            }

            await second_engine.dispose()
            restarted_engine = create_async_engine(TEST_DATABASE_URL)
            try:
                restarted = await CronScheduler(
                    PostgresExecutionRepository(restarted_engine)
                ).fire_occurrence(
                    flow,
                    trigger_id=trigger.id,
                    scheduled_for=scheduled_for,
                    tenant_id="default",
                    inputs={"greeting": "hello"},
                )
                assert restarted.execution_id == first.execution_id
            finally:
                await restarted_engine.dispose()

            async with first_engine.connect() as connection:
                execution_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM executions "
                        "WHERE namespace_name = :namespace AND flow_key = :flow_key"
                    ),
                    {"namespace": flow.namespace, "flow_key": flow.id},
                )
                dispatch_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM messages_outbox "
                        "WHERE partition_key = :partition_key AND subject = 'task-dispatch'"
                    ),
                    {"partition_key": f"execution:{first.execution_id}"},
                )
            assert execution_count == 1
            assert dispatch_count == 3
        finally:
            await cleanup_execution(first_engine, first.execution_id)
            await first_engine.dispose()
            await second_engine.dispose()

    asyncio.run(scenario())


def test_worker_poll_fires_applied_cron_flow_once_per_minute() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition(
            id="worker_cron_poll",
            namespace=f"tests.scheduler.worker.{uuid4().hex}",
            triggers=[
                TriggerDefinition(
                    id="every_minute",
                    type="core.cron",
                    cron="* * * * *",
                    timezone="UTC",
                )
            ],
            tasks=[TaskDefinition(id="done", type="core.return", value="done")],
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = ScopedPostgresExecutionRepository(engine, flow.namespace, flow.id)
        scheduler_repository = PostgresSchedulerRepository(engine)
        trigger_runtime = PostgresTriggerRuntimeRepository(engine)
        scheduler_id = uuid4()
        await repository.apply_flow(flow, tenant_id="default")
        first_poll = datetime(2026, 8, 21, 12, 0, 5, tzinfo=UTC)
        executions = []

        try:
            assert (
                await schedule_once(
                    repository,
                    scheduler_repository,
                    tenant_ids=("default",),
                    scheduler_id=scheduler_id,
                    now=first_poll,
                    trigger_runtime=trigger_runtime,
                )
                == 1
            )
            assert (
                await schedule_once(
                    repository,
                    scheduler_repository,
                    tenant_ids=("default",),
                    scheduler_id=scheduler_id,
                    now=first_poll.replace(second=55),
                    trigger_runtime=trigger_runtime,
                )
                == 0
            )
            executions = [
                execution
                for execution in await repository.list_executions(
                    tenant_id="default",
                    limit=1000,
                )
                if execution.namespace == flow.namespace and execution.flow_id == flow.id
            ]
            assert len(executions) == 1
            assert executions[0].state is ExecutionState.RUNNING
            occurrences = await trigger_runtime.list_occurrences(
                tenant_id="default",
                namespace=flow.namespace,
            )
            assert len(occurrences) == 1
            assert occurrences[0].state.value == "SUCCEEDED"
            assert occurrences[0].execution_id == executions[0].execution_id
        finally:
            if executions:
                await cleanup_execution(engine, executions[0].execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_persisted_flow_keeps_its_revision_hash_when_trigger_defaults_expand() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        namespace = f"tests.scheduler.upgrade.{uuid4().hex}"
        flow = FlowDefinition(
            id="persisted_trigger_defaults",
            namespace=namespace,
            triggers=[
                TriggerDefinition(
                    id="every_minute",
                    type="core.cron",
                    cron="* * * * *",
                    timezone="UTC",
                )
            ],
            tasks=[TaskDefinition(id="done", type="core.return", value="done")],
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        execution_id: UUID | None = None
        try:
            applied = await repository.apply_flow(flow, tenant_id="default")
            async with engine.begin() as connection:
                result = await connection.execute(
                    text(
                        "SELECT canonical_definition FROM flow_revisions "
                        "WHERE revision = 1 AND flow_id = CAST(:flow_id AS uuid)"
                    ),
                    {"flow_id": applied.resource_id},
                )
                canonical = dict(result.scalar_one())
                canonical["triggers"] = [
                    {
                        key: value
                        for key, value in trigger.items()
                        if key
                        not in {
                            "maxPending",
                            "maxAttempts",
                            "retryDelay",
                            "states",
                            "inputs",
                            "maxDepth",
                        }
                    }
                    for trigger in canonical["triggers"]
                ]
                encoded = json.dumps(
                    canonical,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                await connection.execute(
                    text(
                        "UPDATE flow_revisions SET canonical_definition = CAST(:definition AS jsonb), "
                        "semantic_hash = :semantic_hash WHERE flow_id = CAST(:flow_id AS uuid) "
                        "AND revision = 1"
                    ),
                    {
                        "definition": encoded,
                        "semantic_hash": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                        "flow_id": applied.resource_id,
                    },
                )

            persisted = await repository.get_flow(namespace, flow.id, tenant_id="default")
            execution = await repository.create_execution(
                persisted,
                tenant_id="default",
                inputs={},
                idempotency_key=f"upgrade:{namespace}",
            )
            execution_id = execution.execution_id
            assert execution.flow_id == flow.id
        finally:
            if execution_id is not None:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_postgres_scheduler_claim_is_single_owner_and_stale_completion_is_fenced() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        flow = FlowDefinition(
            id="scheduler_fence",
            namespace=f"tests.scheduler.fence.{uuid4().hex}",
            triggers=[
                TriggerDefinition(
                    id="every_minute",
                    type="core.cron",
                    cron="* * * * *",
                    timezone="UTC",
                    misfire_grace_seconds=0,
                )
            ],
            tasks=[TaskDefinition(id="done", type="core.return", value="done")],
        )
        first_engine = create_async_engine(TEST_DATABASE_URL)
        second_engine = create_async_engine(TEST_DATABASE_URL)
        first_executions = PostgresExecutionRepository(first_engine)
        second_executions = PostgresExecutionRepository(second_engine)
        first_states = PostgresSchedulerRepository(first_engine)
        second_states = PostgresSchedulerRepository(second_engine)
        first_owner = uuid4()
        second_owner = uuid4()
        due_at = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)
        execution_ids: list[UUID] = []

        try:
            await first_executions.apply_flow(flow, tenant_id="default")
            first_result, second_result = await asyncio.gather(
                CronScheduler(
                    first_executions,
                    first_states,
                    owner_id=first_owner,
                ).evaluate_due_occurrences(flow, at=due_at, tenant_id="default"),
                CronScheduler(
                    second_executions,
                    second_states,
                    owner_id=second_owner,
                ).evaluate_due_occurrences(flow, at=due_at, tenant_id="default"),
            )
            evaluations = [first_result[0], second_result[0]]
            assert sorted(item.action for item in evaluations) == [
                ScheduleAction.FIRED,
                ScheduleAction.NOT_DUE,
            ]
            execution_ids = [
                execution.execution_id for item in evaluations for execution in item.executions
            ]
            assert len(execution_ids) == 1

            stale = await first_states.claim_schedule(
                tenant_id="default",
                namespace=flow.namespace,
                flow_id=flow.id,
                flow_revision=flow.revision,
                trigger_id="every_minute",
                initial_next_fire_at=due_at,
                due_before=due_at + timedelta(minutes=1),
                owner_id=first_owner,
                lease_duration=timedelta(milliseconds=10),
            )
            assert stale.claimed
            await asyncio.sleep(0.05)
            current = await second_states.claim_schedule(
                tenant_id="default",
                namespace=flow.namespace,
                flow_id=flow.id,
                flow_revision=flow.revision,
                trigger_id="every_minute",
                initial_next_fire_at=due_at,
                due_before=due_at + timedelta(minutes=1),
                owner_id=second_owner,
                lease_duration=timedelta(seconds=30),
            )
            assert current.claimed
            assert current.fencing_token > stale.fencing_token
            with pytest.raises(SchedulerFenceError):
                await first_states.complete_schedule(
                    tenant_id="default",
                    trigger_definition_id=stale.trigger_definition_id,
                    owner_id=first_owner,
                    fencing_token=stale.fencing_token,
                    evaluated_at=due_at + timedelta(minutes=1),
                    next_fire_at=due_at + timedelta(minutes=2),
                    last_occurrence_at=due_at + timedelta(minutes=1),
                    decision="stale owner must not commit",
                    missed_count=0,
                )
        finally:
            for execution_id in execution_ids:
                await cleanup_execution(first_engine, execution_id)
            async with first_engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM scheduler_states WHERE namespace_name = :namespace"),
                    {"namespace": flow.namespace},
                )
            await first_engine.dispose()
            await second_engine.dispose()

    asyncio.run(scenario())
