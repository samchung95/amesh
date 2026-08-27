from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.dsl import FlowDefinition
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_recovery_candidates_dispatch_fresh_execution_but_grace_running_work() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            repository = PostgresExecutionRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "recovery_candidate",
                    "namespace": "tests.recovery",
                    "tasks": [{"id": "work", "type": "core.return", "value": "ok"}],
                }
            )
            execution = await repository.create_execution(flow, tenant_id="default", inputs={})
            stale_before = datetime.now(UTC) - timedelta(hours=1)

            fresh = await repository.list_recovery_candidates(
                tenant_id="default",
                updated_before=stale_before,
            )
            assert [item.execution_id for item in fresh] == [execution.execution_id]

            async with tenant_transaction(engine, "default") as (connection, _tenant_id):
                await connection.execute(
                    text(
                        "UPDATE task_runs SET state = 'RUNNING', updated_at = clock_timestamp() "
                        "WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )
                await connection.execute(
                    text(
                        "UPDATE executions SET updated_at = clock_timestamp() - interval '2 hours' "
                        "WHERE id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )

            protected = await repository.list_recovery_candidates(
                tenant_id="default",
                updated_before=stale_before,
            )
            assert not protected

            async with tenant_transaction(engine, "default") as (connection, _tenant_id):
                await connection.execute(
                    text(
                        "UPDATE task_runs SET updated_at = clock_timestamp() - interval '2 hours' "
                        "WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )

            abandoned = await repository.list_recovery_candidates(
                tenant_id="default",
                updated_before=stale_before,
            )
            assert [item.execution_id for item in abandoned] == [execution.execution_id]
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
