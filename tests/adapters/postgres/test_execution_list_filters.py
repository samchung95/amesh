from __future__ import annotations

import asyncio
import os

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.dsl import FlowDefinition

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _flow(namespace: str, flow_id: str) -> FlowDefinition:
    return FlowDefinition.model_validate(
        {"id": flow_id, "namespace": namespace, "tasks": [{"id": "seed", "type": "core.return"}]}
    )


def test_list_executions_filters_one_flow_in_sql(migrated_test_database_url: str) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresExecutionRepository(engine)
            quiet_flow = _flow("tests.list_filter.a", "quiet")
            busy_flow = _flow("tests.list_filter.a", "busy")
            other_namespace = _flow("tests.list_filter.b", "quiet")
            quiet = await repository.create_execution(quiet_flow, tenant_id="default", inputs={})
            for _ in range(3):
                await repository.create_execution(busy_flow, tenant_id="default", inputs={})
            await repository.create_execution(other_namespace, tenant_id="default", inputs={})

            recent = await repository.list_executions(tenant_id="default", limit=2)
            filtered = await repository.list_executions(
                tenant_id="default",
                limit=2,
                namespace="tests.list_filter.a",
                flow_id="quiet",
            )
            busy = await repository.list_executions(
                tenant_id="default",
                limit=10,
                namespace="tests.list_filter.a",
                flow_id="busy",
            )

            assert quiet.execution_id not in {item.execution_id for item in recent}
            assert [item.execution_id for item in filtered] == [quiet.execution_id]
            assert len(busy) == 3
            assert {(item.namespace, item.flow_id) for item in busy} == {
                ("tests.list_filter.a", "busy")
            }
            with pytest.raises(ValueError, match="together"):
                await repository.list_executions(tenant_id="default", namespace="x")
        finally:
            await engine.dispose()

    asyncio.run(scenario())
