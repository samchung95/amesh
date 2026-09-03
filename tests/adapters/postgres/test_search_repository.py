from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from decimal import Decimal
from time import perf_counter

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.adapters.postgres.metadata_repository import PostgresMetadataRepository
from amesh.adapters.postgres.search_repository import PostgresSearchRepository
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import new_runtime_id
from amesh.domain.search import (
    SearchDocumentType,
    SearchProjectionCondition,
    SearchRange,
    SearchRangeField,
    SearchRequest,
    SearchSortDirection,
    SearchSortField,
)
from amesh.dsl import FlowDefinition
from amesh.ports.metadata_repository import (
    AssetMetadata,
    ExecutionLogEntry,
    ExecutionMetric,
    LogLevel,
    MetricKind,
)
from amesh.ports.search_repository import SearchCursorError

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_search_projection_filters_paginates_isolates_and_rebuilds(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            metadata = PostgresMetadataRepository(engine)
            search = PostgresSearchRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "searchable_flow",
                    "namespace": "platform.search",
                    "description": "Needle reconciliation workflow",
                    "labels": {"team": "platform"},
                    "tasks": [{"id": "return", "type": "core.return"}],
                }
            )
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                labels={"team": "platform"},
            )
            now = datetime.now(UTC)
            task_run_id = new_runtime_id()
            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                await connection.execute(
                    text(
                        """
                        INSERT INTO task_runs (
                            id, tenant_id, execution_id, task_path, state, current_attempt,
                            version, created_at, updated_at, labels
                        ) VALUES (
                            :id, :tenant_uuid, :execution_id, 'return', 'RUNNING', 1,
                            1, :now, :now, '{"team":"platform"}'::jsonb
                        )
                        """
                    ),
                    {
                        "id": task_run_id,
                        "tenant_uuid": tenant_uuid,
                        "execution_id": execution.execution_id,
                        "now": now,
                    },
                )
            visible_log = ExecutionLogEntry(
                log_id=new_runtime_id(),
                execution_id=execution.execution_id,
                level=LogLevel.ERROR,
                logger="search.test",
                message="diagnostic needle appeared",
                fields={"secret": "not-indexed"},
                occurred_at=now,
            )
            await metadata.append_log(visible_log, tenant_id="default")
            await metadata.append_log(
                visible_log.model_copy(
                    update={
                        "log_id": new_runtime_id(),
                        "message": "super-secret-redacted-value",
                        "redacted": True,
                    }
                ),
                tenant_id="default",
            )
            metric = ExecutionMetric(
                metric_id=new_runtime_id(),
                execution_id=execution.execution_id,
                task_run_id=task_run_id,
                metric_name="search.queue.lag",
                metric_kind=MetricKind.GAUGE,
                metric_value=Decimal("12.5"),
                unit="seconds",
                labels={"team": "platform"},
                occurred_at=now,
            )
            await metadata.append_metric(metric, tenant_id="default")
            await metadata.upsert_asset(
                AssetMetadata(
                    asset_id=new_runtime_id(),
                    provider="catalog",
                    external_key="datasets/search",
                    asset_type="dataset",
                    display_name="Search telemetry",
                    labels={"team": "platform"},
                ),
                tenant_id="default",
                actor_id="test:search",
            )

            assert await search.project_once(tenant_id="default", limit=1_000) > 0
            assert await search.project_once(tenant_id="default", limit=1_000) == 0
            status = await search.status(tenant_id="default")
            assert status.condition is SearchProjectionCondition.READY
            assert status.documents_indexed == status.source_documents
            assert status.progress == 1.0
            assert status.lag_seconds is not None
            assert status.schema_version == 2
            assert status.checkpoints_verified is True
            assert status.active_checksum is not None
            async with engine.connect() as connection:
                components = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM search_projection_components "
                            "WHERE schema_version = 2"
                        )
                    )
                    or 0
                )
                materialized_view = await connection.scalar(
                    text("SELECT to_regclass('search_projection_daily_rollup_v2')::text")
                )
            assert components == 5
            assert materialized_view == "search_projection_daily_rollup_v2"

            task_result = await search.search(
                SearchRequest(
                    types=(SearchDocumentType.TASK_RUN,),
                    fields={"taskRunId": str(task_run_id)},
                ),
                tenant_id="default",
                authorized_types=(SearchDocumentType.TASK_RUN,),
            )
            assert [item.document_id for item in task_result.items] == [str(task_run_id)]
            metric_result = await search.search(
                SearchRequest(
                    query="queue lag",
                    types=(SearchDocumentType.METRIC,),
                    fields={"metricName": "search.queue.lag"},
                ),
                tenant_id="default",
                authorized_types=(SearchDocumentType.METRIC,),
            )
            assert [item.document_id for item in metric_result.items] == [str(metric.metric_id)]

            await search.record_failure(
                tenant_id="default",
                error="simulated optional projection outage",
            )
            degraded = await search.status(tenant_id="default")
            assert degraded.condition is SearchProjectionCondition.DEGRADED
            assert degraded.failures == 1
            execution_during_outage = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
            )
            assert execution_during_outage.flow_id == "searchable_flow"
            assert await search.project_once(tenant_id="default", limit=1_000) > 0
            assert (
                await search.status(tenant_id="default")
            ).condition is SearchProjectionCondition.READY

            log_result = await search.search(
                SearchRequest(
                    query="diagnostic needle",
                    types=(SearchDocumentType.LOG,),
                    fields={"level": "ERROR", "logger": "search.test"},
                    from_time=now,
                    to_time=now,
                ),
                tenant_id="default",
                authorized_types=(SearchDocumentType.LOG,),
            )
            assert [item.document_id for item in log_result.items] == [str(visible_log.log_id)]
            assert log_result.items[0].summary == "diagnostic needle appeared"

            redacted_result = await search.search(
                SearchRequest(query="super-secret-redacted-value"),
                tenant_id="default",
                authorized_types=tuple(SearchDocumentType),
            )
            assert redacted_result.items == ()

            structured = await search.search(
                SearchRequest(
                    types=(SearchDocumentType.EXECUTION,),
                    namespace="platform.search",
                    states=("RUNNING",),
                    labels={"team": "platform"},
                    fields={"executionId": str(execution.execution_id)},
                    ranges=(SearchRange(field=SearchRangeField.SOURCE_VERSION, gte=0, lte=10),),
                ),
                tenant_id="default",
                authorized_types=(SearchDocumentType.EXECUTION,),
            )
            assert len(structured.items) == 1

            first_page = await search.search(
                SearchRequest(
                    sort=SearchSortField.TITLE,
                    direction=SearchSortDirection.ASC,
                    limit=1,
                ),
                tenant_id="default",
                authorized_types=tuple(SearchDocumentType),
            )
            assert first_page.next_cursor is not None
            second_page = await search.search(
                SearchRequest(
                    sort=SearchSortField.TITLE,
                    direction=SearchSortDirection.ASC,
                    limit=1,
                    cursor=first_page.next_cursor,
                ),
                tenant_id="default",
                authorized_types=tuple(SearchDocumentType),
            )
            assert first_page.items[0].document_id != second_page.items[0].document_id
            with pytest.raises(SearchCursorError):
                await search.search(
                    SearchRequest(query="different", cursor=first_page.next_cursor),
                    tenant_id="default",
                    authorized_types=tuple(SearchDocumentType),
                )

            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        INSERT INTO tenants (id, slug, display_name, storage_prefix)
                        VALUES (:id, 'search-other', 'Search other', 'tenants/search-other/')
                        """
                    ),
                    {"id": new_runtime_id()},
                )
            await executions.create_execution(flow, tenant_id="search-other", inputs={})
            await search.project_once(tenant_id="search-other", limit=1_000)
            default_ids = {
                item.document_id
                for item in (
                    await search.search(
                        SearchRequest(),
                        tenant_id="default",
                        authorized_types=tuple(SearchDocumentType),
                    )
                ).items
            }
            other_ids = {
                item.document_id
                for item in (
                    await search.search(
                        SearchRequest(),
                        tenant_id="search-other",
                        authorized_types=tuple(SearchDocumentType),
                    )
                ).items
            }
            assert default_ids.isdisjoint(other_ids)

            rebuilding = await search.request_rebuild(
                tenant_id="default",
                actor_id="test:operator",
                reason="prove scoped blue-green rebuild",
                document_types=(SearchDocumentType.LOG, SearchDocumentType.METRIC),
                from_time=now,
            )
            assert rebuilding.condition is SearchProjectionCondition.REBUILDING
            assert 0 < rebuilding.documents_indexed < rebuilding.source_documents
            assert rebuilding.building_version == rebuilding.projection_version + 1
            still_searchable = await search.search(
                SearchRequest(query="diagnostic needle", types=(SearchDocumentType.LOG,)),
                tenant_id="default",
                authorized_types=(SearchDocumentType.LOG,),
            )
            assert len(still_searchable.items) == 1
            concurrent_execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                labels={"team": "concurrent-rebuild"},
            )
            assert await search.project_once(tenant_id="default", limit=1_000) > 0
            resumed_search = PostgresSearchRepository(engine)
            assert await resumed_search.project_once(tenant_id="default", limit=1_000) == 0
            rebuilt = await search.status(tenant_id="default")
            assert rebuilt.condition is SearchProjectionCondition.READY
            assert rebuilt.documents_indexed == rebuilt.source_documents
            verification = await search.verify(tenant_id="default")
            assert verification.verified is True
            assert all(item.verified for item in verification.items)
            concurrent_result = await search.search(
                SearchRequest(
                    query=str(concurrent_execution.execution_id),
                    types=(SearchDocumentType.EXECUTION,),
                ),
                tenant_id="default",
                authorized_types=(SearchDocumentType.EXECUTION,),
            )
            assert [item.document_id for item in concurrent_result.items] == [
                str(concurrent_execution.execution_id)
            ]

            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                event_types = set(
                    (
                        await connection.execute(
                            text(
                                "SELECT event_type FROM search_projection_events "
                                "WHERE tenant_id = :tenant_uuid"
                            ),
                            {"tenant_uuid": tenant_uuid},
                        )
                    ).scalars()
                )
                outbox_count = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM messages_outbox "
                            "WHERE tenant_id = :tenant_uuid "
                            "AND subject = 'search-projection-events'"
                        ),
                        {"tenant_uuid": tenant_uuid},
                    )
                    or 0
                )
            assert event_types == {
                "SearchProjectionFailed",
                "SearchProjectionRebuildRequested",
                "SearchProjectionRebuildCompleted",
            }
            assert outbox_count == 3

            disabled = await search.set_enabled(
                tenant_id="default",
                actor_id="test:operator",
                enabled=False,
                reason="exercise bounded authoritative fallback",
            )
            assert disabled.condition is SearchProjectionCondition.DISABLED
            assert await search.project_once(tenant_id="default", limit=1_000) == 0
            fallback = await search.search(
                SearchRequest(
                    query="Needle reconciliation",
                    types=(SearchDocumentType.FLOW, SearchDocumentType.LOG),
                ),
                tenant_id="default",
                authorized_types=(SearchDocumentType.FLOW, SearchDocumentType.LOG),
            )
            assert fallback.authoritative_fallback is True
            assert [item.document_type for item in fallback.items] == [SearchDocumentType.FLOW]
            assert fallback.denied_types == (SearchDocumentType.LOG,)
            await search.set_enabled(
                tenant_id="default",
                actor_id="test:operator",
                enabled=True,
                reason="resume projected reads",
            )

            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                await connection.execute(
                    text(
                        "DELETE FROM execution_logs WHERE tenant_id = :tenant_uuid AND id = :log_id"
                    ),
                    {"tenant_uuid": tenant_uuid, "log_id": visible_log.log_id},
                )
            assert await search.project_once(tenant_id="default", limit=1_000) > 0
            assert await search.project_once(tenant_id="default", limit=1_000) == 0
            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                archived = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM search_projection_archives "
                            "WHERE tenant_id = :tenant_uuid AND document_id = :document_id "
                            "AND source_policy = 'authoritative-source-retention'"
                        ),
                        {"tenant_uuid": tenant_uuid, "document_id": str(visible_log.log_id)},
                    )
                    or 0
                )
                checkpoints = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM search_projection_checkpoints "
                            "WHERE tenant_id = :tenant_uuid AND verified "
                            "AND projection_version = ("
                            "SELECT projection_version FROM search_projection_state "
                            "WHERE tenant_id = :tenant_uuid)"
                        ),
                        {"tenant_uuid": tenant_uuid},
                    )
                    or 0
                )
                rollups = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM search_projection_daily_rollups "
                            "WHERE tenant_id = :tenant_uuid"
                        ),
                        {"tenant_uuid": tenant_uuid},
                    )
                    or 0
                )
            assert archived == 1
            assert checkpoints == len(SearchDocumentType)
            assert rollups > 0

            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                await connection.execute(
                    text(
                        """
                        INSERT INTO search_documents_v2 (
                            tenant_id, projection_version, document_type, document_id,
                            namespace, title, content,
                            state, labels, fields, occurred_at, source_updated_at,
                            source_version
                        )
                        SELECT :tenant_uuid, state.projection_version, 'FLOW',
                               'benchmark-' || item::text,
                               'benchmark', 'benchmark flow ' || item::text,
                               CASE WHEN item % 10 = 0 THEN 'indexed needle' ELSE 'ordinary' END,
                               CASE WHEN item % 2 = 0 THEN 'ACTIVE' ELSE 'DISABLED' END,
                               '{"suite":"search"}'::jsonb,
                               jsonb_build_object('flowId', 'benchmark-' || item::text),
                               clock_timestamp() - (item * interval '1 second'),
                               clock_timestamp() - (item * interval '1 second'),
                               item
                        FROM generate_series(1, 50000) AS item
                        CROSS JOIN search_projection_state AS state
                        WHERE state.tenant_id = :tenant_uuid
                        """
                    ),
                    {"tenant_uuid": tenant_uuid},
                )
            benchmark_request = SearchRequest(
                query="indexed needle",
                types=(SearchDocumentType.FLOW,),
                namespace="benchmark",
                states=("ACTIVE",),
                labels={"suite": "search"},
                sort=SearchSortField.RELEVANCE,
                limit=50,
            )
            await search.search(
                benchmark_request,
                tenant_id="default",
                authorized_types=(SearchDocumentType.FLOW,),
            )
            latencies = []
            for _ in range(20):
                started = perf_counter()
                result = await search.search(
                    benchmark_request,
                    tenant_id="default",
                    authorized_types=(SearchDocumentType.FLOW,),
                )
                latencies.append(perf_counter() - started)
                assert len(result.items) == 50
            assert sorted(latencies)[18] < 0.5
        finally:
            await engine.dispose()

    asyncio.run(scenario())
