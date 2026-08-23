from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres.dashboard_repository import PostgresDashboardRepository
from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.dashboards import builtin_dashboards
from amesh.domain.dashboards import (
    DashboardDataSource,
    DashboardDefinitionSource,
    DashboardFilters,
    DashboardQuery,
    DashboardSpec,
    DashboardVisibility,
    DashboardVisualization,
    DashboardWidget,
)
from amesh.dsl import FlowDefinition
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.ports.dashboard_repository import DashboardVersionConflict

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_dashboard_definitions_and_bounded_typed_queries_are_durable() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            executions = PostgresExecutionRepository(engine)
            dashboards = PostgresDashboardRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "dashboard_flow",
                    "namespace": "analytics.team",
                    "labels": {"team": "platform"},
                    "tasks": [{"id": "return", "type": "core.return"}],
                }
            )
            await executions.create_execution(flow, tenant_id="default", inputs={})
            widget = DashboardWidget(
                widgetId="states",
                title="States",
                query=DashboardQuery(
                    source=DashboardDataSource.EXECUTIONS,
                    visualization=DashboardVisualization.STATUS_BREAKDOWN,
                    filters=DashboardFilters(namespace="analytics.team"),
                ),
            )
            spec = DashboardSpec(
                title="Platform executions",
                visibility=DashboardVisibility.PRIVATE,
                viewerIds=("viewer-1",),
                editorIds=("editor-1",),
                widgets=(widget,),
                source=DashboardDefinitionSource.GITOPS,
            )
            created = await dashboards.upsert_definition(
                "platform.executions",
                spec,
                tenant_id="default",
                actor_id="owner-1",
                expected_version=None,
            )
            assert created.version == 1
            assert created.source is DashboardDefinitionSource.GITOPS
            assert (
                await dashboards.get_definition("platform.executions", tenant_id="default")
            ).viewer_ids == ("viewer-1",)

            result = await dashboards.execute_query(widget.query, tenant_id="default")
            assert result.scanned_rows == 1
            assert result.rows == ({"state": "RUNNING", "value": 1.0},)
            assert result.partial is False
            assert result.sampled is False
            exercised_sources = set()
            for definition in builtin_dashboards("default"):
                for builtin_widget in definition.widgets:
                    await dashboards.execute_query(builtin_widget.query, tenant_id="default")
                    exercised_sources.add(builtin_widget.query.source)
            assert exercised_sources == set(DashboardDataSource)

            updated = await dashboards.upsert_definition(
                "platform.executions",
                spec.model_copy(update={"title": "Platform workload"}),
                tenant_id="default",
                actor_id="owner-1",
                expected_version=1,
            )
            assert updated.version == 2
            with pytest.raises(DashboardVersionConflict):
                await dashboards.upsert_definition(
                    "platform.executions",
                    spec,
                    tenant_id="default",
                    actor_id="owner-1",
                    expected_version=1,
                )

            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                event_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM dashboard_definition_events "
                        "WHERE tenant_id = :tenant_uuid AND dashboard_id = :dashboard_id"
                    ),
                    {"tenant_uuid": tenant_uuid, "dashboard_id": "platform.executions"},
                )
                outbox_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM messages_outbox "
                        "WHERE tenant_id = :tenant_uuid "
                        "AND subject = 'dashboard-definition-events'"
                    ),
                    {"tenant_uuid": tenant_uuid},
                )
            assert event_count == 2
            assert outbox_count == 2

            await dashboards.delete_definition(
                "platform.executions",
                tenant_id="default",
                actor_id="owner-1",
                expected_version=2,
            )
            with pytest.raises(LookupError):
                await dashboards.get_definition("platform.executions", tenant_id="default")
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
