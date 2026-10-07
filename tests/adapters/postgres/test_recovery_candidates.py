from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.dsl import FlowDefinition

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_recovery_candidates_dispatch_fresh_execution_but_grace_running_work(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
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

    asyncio.run(scenario())


def test_recovery_candidates_include_terminal_execution_only_with_pending_lifecycle_work(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresExecutionRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "recovery_lifecycle",
                    "namespace": "tests.recovery",
                    "tasks": [{"id": "work", "type": "core.return", "value": "ok"}],
                }
            )
            finishing = await repository.create_execution(flow, tenant_id="default", inputs={})
            finished = await repository.create_execution(flow, tenant_id="default", inputs={})
            async with tenant_transaction(engine, "default") as (connection, _tenant_id):
                await connection.execute(
                    text(
                        "UPDATE executions SET state = 'SUCCESS' "
                        "WHERE id IN (:finishing, :finished)"
                    ),
                    {"finishing": finishing.execution_id, "finished": finished.execution_id},
                )
                await connection.execute(
                    text(
                        "UPDATE task_runs SET lifecycle_phase = 'FINALLY', state = 'WAITING' "
                        "WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": finishing.execution_id},
                )
                await connection.execute(
                    text(
                        "UPDATE task_runs SET state = 'SUCCESS' WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": finished.execution_id},
                )

            candidates = await repository.list_recovery_candidates(
                tenant_id="default",
                updated_before=datetime.now(UTC) - timedelta(hours=1),
            )

            assert [item.execution_id for item in candidates] == [finishing.execution_id]
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_paused_execution_is_a_recovery_candidate_only_when_its_flow_has_lifecycle_tasks(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresExecutionRepository(engine)
            plain = FlowDefinition.model_validate(
                {
                    "id": "paused_plain",
                    "namespace": "tests.recovery",
                    "tasks": [{"id": "work", "type": "core.return", "value": "ok"}],
                }
            )
            with_finally = FlowDefinition.model_validate(
                {
                    "id": "paused_finally",
                    "namespace": "tests.recovery",
                    "tasks": [{"id": "work", "type": "core.return", "value": "ok"}],
                    "finally": [{"id": "cleanup", "type": "core.return", "value": "done"}],
                }
            )
            waiting = await repository.create_execution(plain, tenant_id="default", inputs={})
            finishing = await repository.create_execution(
                with_finally, tenant_id="default", inputs={}
            )
            async with tenant_transaction(engine, "default") as (connection, _tenant_id):
                await connection.execute(
                    text(
                        "UPDATE executions SET state = 'PAUSED' WHERE id IN (:waiting, :finishing)"
                    ),
                    {"waiting": waiting.execution_id, "finishing": finishing.execution_id},
                )

            candidates = await repository.list_recovery_candidates(
                tenant_id="default",
                updated_before=datetime.now(UTC) - timedelta(hours=1),
            )

            # A paused execution without lifecycle work is never recovered, so returning it
            # would only burn every cycle and crowd running work out of the batch.
            assert [item.execution_id for item in candidates] == [finishing.execution_id]
        finally:
            await engine.dispose()

    asyncio.run(scenario())
