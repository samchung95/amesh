from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState
from amesh.dsl.models import FlowDefinition, TaskDefinition, TriggerDefinition
from amesh.executor import InProcessExecutor
from amesh.ports import PersistedFlow
from amesh.scheduler import CronScheduler
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
                inputs={"greeting": "hello"},
            ),
            second_scheduler.fire_occurrence(
                flow,
                trigger_id=trigger.id,
                scheduled_for=scheduled_for,
                inputs={"greeting": "hello"},
            ),
        )
        assert concurrent_duplicate.execution_id == first.execution_id

        try:
            completed = await InProcessExecutor(first_repository).run_to_completion(
                flow,
                first.execution_id,
            )
            assert completed.state is ExecutionState.SUCCESS
            results = {task_run.task_id: task_run.result for task_run in completed.task_runs}
            assert results["first"] == {"value": "hello"}
            assert results["second"] == {"value": "hello world"}
            assert results["guarded"] == {"skipped": True}

            await second_engine.dispose()
            restarted_engine = create_async_engine(TEST_DATABASE_URL)
            try:
                restarted = await CronScheduler(
                    PostgresExecutionRepository(restarted_engine)
                ).fire_occurrence(
                    flow,
                    trigger_id=trigger.id,
                    scheduled_for=scheduled_for,
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
            assert execution_count == 1
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
        await repository.apply_flow(flow, tenant_id="default")
        first_poll = datetime(2026, 8, 21, 12, 0, 5, tzinfo=UTC)
        executions = []

        try:
            assert await schedule_once(repository, now=first_poll) == 1
            assert (
                await schedule_once(
                    repository,
                    now=first_poll.replace(second=55),
                )
                == 1
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
        finally:
            if executions:
                await cleanup_execution(engine, executions[0].execution_id)
            await engine.dispose()

    asyncio.run(scenario())
