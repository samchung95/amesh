from __future__ import annotations

import asyncio
import os
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresTaskCacheRepository
from amesh.dsl import FlowDefinition
from amesh.executor import (
    InProcessExecutor,
    TaskArtifactRecord,
    TaskCompletion,
    TaskExecutionContext,
    TaskMetricRecord,
)
from amesh.ports import TaskCacheMode

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _flow(namespace: str) -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "cached",
            "namespace": namespace,
            "inputs": [{"id": "value", "type": "STRING"}],
            "tasks": [
                {
                    "id": "result",
                    "type": "test.cached",
                    "taskCache": {
                        "enabled": True,
                        "ttl": "PT1H",
                        "namespace": "acceptance",
                    },
                }
            ],
        }
    )


def test_cache_survives_restart_and_supports_hit_bypass_refresh_and_purge(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        counter = 0

        async def handler(_task: object, _context: TaskExecutionContext) -> TaskCompletion:
            nonlocal counter
            counter += 1
            return TaskCompletion(
                output={"value": counter},
                metrics=(TaskMetricRecord(name="records", value=Decimal(counter)),),
                artifacts=(
                    TaskArtifactRecord(
                        uri=f"s3://amesh-artifacts/cache/result-{counter}.json",
                        sizeBytes=10,
                        mediaType="application/json",
                    ),
                ),
            )

        flow = _flow("tests.cache.restart")

        async def execute(mode: TaskCacheMode = TaskCacheMode.USE) -> tuple[object, object]:
            repository = PostgresExecutionRepository(engine)
            cache = PostgresTaskCacheRepository(engine)
            executor = InProcessExecutor(
                repository,
                handlers={"test.cached": handler},
                task_cache=cache,
            )
            execution = await repository.create_execution(
                flow,
                tenant_id="default",
                inputs={"value": "same"},
                trigger=(
                    {"_ameshCacheMode": mode.value} if mode is not TaskCacheMode.USE else None
                ),
            )
            progress = await executor.run_to_completion(
                flow,
                execution.execution_id,
                tenant_id="default",
            )
            return execution, progress.task_runs[0]

        try:
            _, first = await execute()
            assert first.result == {"value": 1}
            await engine.dispose()
            engine = create_async_engine(migrated_test_database_url)

            _, hit = await execute()
            assert counter == 1
            assert hit.result == {"value": 1}
            assert hit.evidence["cache"]["decision"] == "HIT"
            assert hit.evidence["cache"]["sourceExecutionId"] is not None
            assert len(hit.evidence["metrics"]) == 1
            assert len(hit.evidence["artifacts"]) == 1

            _, bypass = await execute(TaskCacheMode.BYPASS)
            assert counter == 2
            assert bypass.evidence["cache"]["decision"] == "BYPASS"

            _, still_hit = await execute()
            assert counter == 2
            assert still_hit.result == {"value": 1}

            _, refreshed = await execute(TaskCacheMode.REFRESH)
            assert counter == 3
            assert refreshed.evidence["cache"]["decision"] == "REFRESH"
            _, refreshed_hit = await execute()
            assert counter == 3
            assert refreshed_hit.result == {"value": 3}

            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE task_cache_entries "
                        "SET expires_at = clock_timestamp() - interval '1 second'"
                    )
                )
            _, expired = await execute()
            assert counter == 4
            assert expired.evidence["cache"]["decision"] == "MISS_EXPIRED"

            cache = PostgresTaskCacheRepository(engine)
            entries = await cache.list_entries(
                tenant_id="default",
                namespace=flow.namespace,
            )
            assert len(entries) == 1
            assert entries[0].hit_count == 3
            purged = await cache.purge(
                tenant_id="default",
                actor_id="test:operator",
                reason="acceptance purge",
                key_prefix=entries[0].key_prefix,
            )
            assert purged.invalidated_count == 1
            _, after_purge = await execute()
            assert counter == 5
            assert after_purge.evidence["cache"]["decision"] == "MISS_INVALIDATED"

            async with engine.connect() as connection:
                event_types = set(
                    (
                        await connection.execute(text("SELECT event_type FROM task_cache_events"))
                    ).scalars()
                )
                cached_evidence = await connection.scalar(
                    text("SELECT evidence FROM task_cache_entries LIMIT 1")
                )
                audit_action = await connection.scalar(
                    text("SELECT action FROM audit_events WHERE action = 'cache.purge' LIMIT 1")
                )
            assert {
                "MISS",
                "MISS_EXPIRED",
                "HIT",
                "BYPASS",
                "REFRESH",
                "PURGED",
                "FILLED",
            } <= event_types
            assert len(cached_evidence["metrics"]) == 1
            assert len(cached_evidence["artifacts"]) == 1
            assert audit_action == "cache.purge"
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_concurrent_population_computes_a_safe_duplicate_and_keeps_one_entry(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        flow = _flow("tests.cache.concurrent")
        started = 0
        both_started = asyncio.Event()

        async def handler(_task: object, _context: TaskExecutionContext) -> dict[str, int]:
            nonlocal started
            started += 1
            if started == 2:
                both_started.set()
            await asyncio.wait_for(both_started.wait(), timeout=5)
            return {"value": started}

        try:
            repository = PostgresExecutionRepository(engine)
            cache = PostgresTaskCacheRepository(engine)
            executor = InProcessExecutor(
                repository,
                handlers={"test.cached": handler},
                task_cache=cache,
            )
            executions = [
                await repository.create_execution(
                    flow,
                    tenant_id="default",
                    inputs={"value": "same"},
                )
                for _ in range(2)
            ]
            progress = await asyncio.gather(
                *(
                    executor.run_to_completion(
                        flow,
                        execution.execution_id,
                        tenant_id="default",
                    )
                    for execution in executions
                )
            )
            decisions = {item.task_runs[0].evidence["cache"]["decision"] for item in progress}
            assert started == 2
            assert decisions == {"MISS", "MISS_CONCURRENT"}
            entries = await cache.list_entries(tenant_id="default", namespace=flow.namespace)
            assert len(entries) == 1
            assert entries[0].state == "READY"
        finally:
            await engine.dispose()

    asyncio.run(scenario())
