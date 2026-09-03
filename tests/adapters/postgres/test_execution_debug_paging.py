from __future__ import annotations

import asyncio
import os
import tracemalloc
from time import perf_counter

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.dsl import FlowDefinition

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_urs_nfr_performance_006_pages_and_aggregates_100k_task_runs(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresExecutionRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "large_debug_view",
                    "namespace": "tests.performance",
                    "tasks": [{"id": "seed", "type": "core.return"}],
                }
            )
            execution = await repository.create_execution(flow, tenant_id="default", inputs={})
            async with tenant_transaction(engine, "default") as (connection, tenant_id):
                await connection.execute(
                    text(
                        """
                        INSERT INTO task_runs (
                            id, tenant_id, execution_id, task_path, iteration_key,
                            lifecycle_phase, labels, state, current_attempt, version
                        )
                        SELECT gen_random_uuid(), :tenant_id, :execution_id,
                               'synthetic-' || value::text, NULL, 'MAIN', '{}'::jsonb,
                               'SUCCESS', 0, 1
                        FROM generate_series(1, 99999) AS value
                        """
                    ),
                    {"tenant_id": tenant_id, "execution_id": execution.execution_id},
                )

            tracemalloc.start()
            started = perf_counter()
            summary = await repository.summarize_task_runs(
                execution.execution_id,
                tenant_id="default",
                include_iterations=False,
            )
            page = await repository.list_task_runs(
                execution.execution_id,
                tenant_id="default",
                include_iterations=False,
                limit=100,
                offset=99_900,
            )
            elapsed = perf_counter() - started
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            assert summary.total == 100_000
            assert summary.succeeded == 99_999
            assert len(page) == 100
            assert elapsed < 5
            assert peak < 16 * 1024 * 1024
        finally:
            await engine.dispose()

    asyncio.run(scenario())
