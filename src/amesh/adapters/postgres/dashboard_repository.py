from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain.dashboards import (
    DashboardAggregation,
    DashboardDataSource,
    DashboardDefinition,
    DashboardMeasure,
    DashboardQuery,
    DashboardQueryResult,
    DashboardSpec,
    DashboardVisualization,
)
from amesh.ports.dashboard_repository import (
    DashboardQueryTimeout,
    DashboardRepository,
    DashboardVersionConflict,
)
from amesh.ports.errors import NotFoundError

from .repository_support import PostgresRepositoryBase

_LIST_DEFINITIONS = text(
    """
    SELECT * FROM dashboard_definitions
    WHERE tenant_id = :tenant_uuid AND deleted = false
    ORDER BY title, dashboard_id
    """
)

_GET_DEFINITION = text(
    """
    SELECT * FROM dashboard_definitions
    WHERE tenant_id = :tenant_uuid AND dashboard_id = :dashboard_id AND deleted = false
    """
)

_INSERT_DEFINITION = text(
    """
    INSERT INTO dashboard_definitions (
        tenant_id, dashboard_id, title, description, visibility, owner_id,
        viewer_ids, editor_ids, definition, version, source, created_by, updated_by
    ) VALUES (
        :tenant_uuid, :dashboard_id, :title, :description, :visibility, :actor_id,
        CAST(:viewer_ids AS jsonb), CAST(:editor_ids AS jsonb), CAST(:definition AS jsonb),
        1, :source, :actor_id, :actor_id
    )
    RETURNING *
    """
)

_UPDATE_DEFINITION = text(
    """
    UPDATE dashboard_definitions
    SET title = :title,
        description = :description,
        visibility = :visibility,
        viewer_ids = CAST(:viewer_ids AS jsonb),
        editor_ids = CAST(:editor_ids AS jsonb),
        definition = CAST(:definition AS jsonb),
        source = :source,
        version = version + 1,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid
      AND dashboard_id = :dashboard_id
      AND version = :expected_version
      AND deleted = false
    RETURNING *
    """
)

_DELETE_DEFINITION = text(
    """
    UPDATE dashboard_definitions
    SET deleted = true,
        version = version + 1,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE tenant_id = :tenant_uuid
      AND dashboard_id = :dashboard_id
      AND version = :expected_version
      AND deleted = false
    RETURNING version
    """
)

_INSERT_EVENT = text(
    """
    INSERT INTO dashboard_definition_events (
        event_id, tenant_id, dashboard_id, version, event_type, actor_id, payload
    ) VALUES (
        gen_random_uuid(), :tenant_uuid, :dashboard_id, :version,
        :event_type, :actor_id, CAST(:payload AS jsonb)
    )
    """
)

_SOURCES: dict[DashboardDataSource, str] = {
    DashboardDataSource.EXECUTIONS: """
        SELECT executions.id::text AS row_id,
               executions.created_at AS occurred_at,
               executions.namespace_name AS namespace,
               executions.flow_key AS flow,
               executions.state,
               NULL::text AS worker_group,
               NULL::text AS level,
               NULL::text AS metric_name,
               NULL::text AS asset_type,
               NULL::text AS provider,
               NULL::text AS outcome,
               NULL::text AS check_type,
               NULL::text AS unit,
               executions.labels,
               '{}'::jsonb AS custom_dimensions,
               NULL::numeric AS numeric_value,
               EXTRACT(EPOCH FROM (COALESCE(executions.terminal_at, executions.updated_at)
                   - executions.created_at)) * 1000 AS duration_ms
        FROM executions
        WHERE executions.tenant_id = :tenant_uuid
    """,
    DashboardDataSource.LOGS: """
        SELECT execution_logs.id::text AS row_id,
               execution_logs.occurred_at,
               executions.namespace_name AS namespace,
               executions.flow_key AS flow,
               executions.state,
               workers.worker_group,
               execution_logs.level,
               NULL::text AS metric_name,
               NULL::text AS asset_type,
               NULL::text AS provider,
               NULL::text AS outcome,
               NULL::text AS check_type,
               NULL::text AS unit,
               executions.labels,
               execution_logs.fields AS custom_dimensions,
               NULL::numeric AS numeric_value,
               NULL::numeric AS duration_ms
        FROM execution_logs
        JOIN executions ON executions.tenant_id = execution_logs.tenant_id
          AND executions.id = execution_logs.execution_id
        LEFT JOIN workers ON workers.tenant_id = execution_logs.tenant_id
          AND workers.id = execution_logs.worker_id
        WHERE execution_logs.tenant_id = :tenant_uuid
    """,
    DashboardDataSource.METRICS: """
        SELECT execution_metrics.id::text AS row_id,
               execution_metrics.occurred_at,
               executions.namespace_name AS namespace,
               executions.flow_key AS flow,
               executions.state,
               NULL::text AS worker_group,
               NULL::text AS level,
               execution_metrics.metric_name,
               NULL::text AS asset_type,
               NULL::text AS provider,
               NULL::text AS outcome,
               NULL::text AS check_type,
               execution_metrics.unit,
               executions.labels || execution_metrics.labels AS labels,
               execution_metrics.labels AS custom_dimensions,
               execution_metrics.metric_value AS numeric_value,
               NULL::numeric AS duration_ms
        FROM execution_metrics
        JOIN executions ON executions.tenant_id = execution_metrics.tenant_id
          AND executions.id = execution_metrics.execution_id
        WHERE execution_metrics.tenant_id = :tenant_uuid
    """,
    DashboardDataSource.SLA: """
        SELECT check_evaluations.evaluation_id::text AS row_id,
               check_evaluations.evaluated_at AS occurred_at,
               check_evaluations.namespace_name AS namespace,
               check_evaluations.flow_key AS flow,
               check_evaluations.outcome AS state,
               NULL::text AS worker_group,
               NULL::text AS level,
               NULL::text AS metric_name,
               NULL::text AS asset_type,
               NULL::text AS provider,
               check_evaluations.outcome,
               check_evaluations.check_type,
               NULL::text AS unit,
               check_evaluations.labels,
               check_evaluations.evidence AS custom_dimensions,
               NULL::numeric AS numeric_value,
               NULL::numeric AS duration_ms
        FROM check_evaluations
        WHERE check_evaluations.tenant_id = :tenant_uuid
    """,
    DashboardDataSource.WORKERS: """
        SELECT workers.id::text AS row_id,
               workers.last_heartbeat_at AS occurred_at,
               NULL::text AS namespace,
               NULL::text AS flow,
               workers.status AS state,
               workers.worker_group,
               NULL::text AS level,
               NULL::text AS metric_name,
               NULL::text AS asset_type,
               NULL::text AS provider,
               NULL::text AS outcome,
               NULL::text AS check_type,
               NULL::text AS unit,
               workers.labels,
               workers.resource_usage AS custom_dimensions,
               workers.capacity::numeric AS numeric_value,
               NULL::numeric AS duration_ms
        FROM workers
        WHERE workers.tenant_id = :tenant_uuid
    """,
    DashboardDataSource.ASSETS: """
        SELECT assets.id::text AS row_id,
               assets.updated_at AS occurred_at,
               assets.namespace_name AS namespace,
               NULL::text AS flow,
               NULL::text AS state,
               NULL::text AS worker_group,
               NULL::text AS level,
               NULL::text AS metric_name,
               assets.asset_type,
               assets.provider,
               NULL::text AS outcome,
               NULL::text AS check_type,
               NULL::text AS unit,
               assets.labels,
               assets.metadata AS custom_dimensions,
               NULL::numeric AS numeric_value,
               NULL::numeric AS duration_ms
        FROM assets
        WHERE assets.tenant_id = :tenant_uuid
    """,
}

_FIXED_DIMENSIONS = {
    "namespace": "namespace",
    "flow": "flow",
    "state": "state",
    "workerGroup": "worker_group",
    "level": "level",
    "metricName": "metric_name",
    "assetType": "asset_type",
    "provider": "provider",
    "outcome": "outcome",
    "checkType": "check_type",
    "unit": "unit",
}


def _definition_from_row(row: RowMapping, tenant_id: str) -> DashboardDefinition:
    payload = dict(row["definition"])
    payload.update(
        {
            "dashboardId": str(row["dashboard_id"]),
            "tenantId": tenant_id,
            "version": int(row["version"]),
            "ownerId": str(row["owner_id"]),
            "builtin": False,
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
    )
    return DashboardDefinition.model_validate(payload)


def _dimension_value(row: RowMapping, dimension: str) -> str | None:
    if column := _FIXED_DIMENSIONS.get(dimension):
        value = row.get(column)
    elif dimension.startswith("label."):
        value = (row.get("labels") or {}).get(dimension.removeprefix("label."))
    else:
        value = (row.get("custom_dimensions") or {}).get(dimension.removeprefix("dimension."))
    return None if value is None else str(value)


def _default_breakdown(query: DashboardQuery) -> tuple[str, ...]:
    if query.group_by:
        return query.group_by
    return {
        DashboardDataSource.EXECUTIONS: ("state",),
        DashboardDataSource.LOGS: ("level",),
        DashboardDataSource.METRICS: ("metricName",),
        DashboardDataSource.SLA: ("outcome",),
        DashboardDataSource.WORKERS: ("state",),
        DashboardDataSource.ASSETS: ("assetType",),
    }[query.source]


def _bucket_start(value: datetime, window: timedelta) -> datetime:
    seconds = window.total_seconds()
    bucket_seconds = 300 if seconds <= 21_600 else 3600 if seconds <= 172_800 else 86_400
    if seconds > 2_592_000:
        bucket_seconds = 604_800
    timestamp = int(value.timestamp())
    return datetime.fromtimestamp(timestamp - (timestamp % bucket_seconds), tz=UTC)


def _distribution_bucket(value: float) -> str:
    boundaries = (0.0, 1.0, 10.0, 100.0, 1_000.0, 10_000.0, 100_000.0)
    for lower, upper in pairwise(boundaries):
        if lower <= value < upper:
            return f"{lower:g}-{upper:g}"
    if value < 0:
        return "<0"
    return "100000+"


def _aggregate(values: Sequence[float], aggregation: DashboardAggregation) -> float:
    if not values:
        return 0.0
    if aggregation is DashboardAggregation.COUNT:
        return float(len(values))
    if aggregation is DashboardAggregation.SUM:
        return float(sum(values))
    if aggregation is DashboardAggregation.AVG:
        return float(sum(values) / len(values))
    if aggregation is DashboardAggregation.MIN:
        return float(min(values))
    if aggregation is DashboardAggregation.MAX:
        return float(max(values))
    ordered = sorted(values)
    percentile = 0.5 if aggregation is DashboardAggregation.P50 else 0.95
    return float(ordered[max(0, math.ceil(percentile * len(ordered)) - 1)])


class PostgresDashboardRepository(PostgresRepositoryBase, DashboardRepository):
    """Tenant-isolated saved dashboards and bounded analytics over rebuildable projections."""

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def list_definitions(self, *, tenant_id: str) -> Sequence[DashboardDefinition]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(_LIST_DEFINITIONS, {"tenant_uuid": tenant_uuid})
            ).mappings()
            return tuple(_definition_from_row(row, tenant_id) for row in rows)

    async def get_definition(
        self,
        dashboard_id: str,
        *,
        tenant_id: str,
    ) -> DashboardDefinition:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_DEFINITION,
                        {"tenant_uuid": tenant_uuid, "dashboard_id": dashboard_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                message = f"dashboard {dashboard_id!r} does not exist"
                raise NotFoundError("dashboard", dashboard_id, message=message)
            return _definition_from_row(row, tenant_id)

    async def upsert_definition(
        self,
        dashboard_id: str,
        spec: DashboardSpec,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None,
    ) -> DashboardDefinition:
        if spec.source.value == "BUILTIN":
            raise ValueError("custom dashboards cannot claim BUILTIN source")
        definition = json.dumps(spec.model_dump(mode="json", by_alias=True), separators=(",", ":"))
        values: dict[str, Any] = {
            "dashboard_id": dashboard_id,
            "title": spec.title,
            "description": spec.description,
            "visibility": spec.visibility.value,
            "viewer_ids": self._services.codec.dumps(spec.viewer_ids),
            "editor_ids": self._services.codec.dumps(spec.editor_ids),
            "definition": definition,
            "source": spec.source.value,
            "actor_id": actor_id,
        }
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            values["tenant_uuid"] = tenant_uuid
            try:
                if expected_version is None:
                    saved_row = (
                        (await connection.execute(_INSERT_DEFINITION, values)).mappings().one()
                    )
                    event_type = "DashboardCreated"
                else:
                    updated_row = (
                        (
                            await connection.execute(
                                _UPDATE_DEFINITION,
                                {**values, "expected_version": expected_version},
                            )
                        )
                        .mappings()
                        .one_or_none()
                    )
                    if updated_row is None:
                        raise DashboardVersionConflict("dashboard version is stale or unavailable")
                    saved_row = updated_row
                    event_type = "DashboardUpdated"
            except IntegrityError as exc:
                raise DashboardVersionConflict("dashboard already exists") from exc
            await connection.execute(
                _INSERT_EVENT,
                {
                    "tenant_uuid": tenant_uuid,
                    "dashboard_id": dashboard_id,
                    "version": int(saved_row["version"]),
                    "event_type": event_type,
                    "actor_id": actor_id,
                    "payload": definition,
                },
            )
            return _definition_from_row(saved_row, tenant_id)

    async def delete_definition(
        self,
        dashboard_id: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int,
    ) -> None:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            version = await connection.scalar(
                _DELETE_DEFINITION,
                {
                    "tenant_uuid": tenant_uuid,
                    "dashboard_id": dashboard_id,
                    "expected_version": expected_version,
                    "actor_id": actor_id,
                },
            )
            if version is None:
                raise DashboardVersionConflict("dashboard version is stale or unavailable")
            await connection.execute(
                _INSERT_EVENT,
                {
                    "tenant_uuid": tenant_uuid,
                    "dashboard_id": dashboard_id,
                    "version": int(version),
                    "event_type": "DashboardDeleted",
                    "actor_id": actor_id,
                    "payload": "{}",
                },
            )

    async def execute_query(
        self,
        query: DashboardQuery,
        *,
        tenant_id: str,
    ) -> DashboardQueryResult:
        now = self._services.clock.now()
        to_time = query.filters.to_time or now
        from_time = query.filters.from_time or (to_time - timedelta(hours=24))
        if to_time - from_time > timedelta(days=90):
            raise ValueError("dashboard query time range cannot exceed 90 days")
        scan_limit = min(20_000, max(1_000, query.limit * 100))
        predicates = ["occurred_at >= :from_time", "occurred_at < :to_time"]
        parameters: dict[str, Any] = {
            "from_time": from_time,
            "to_time": to_time,
            "scan_limit": scan_limit + 1,
            "sample_threshold": int(query.sample_rate * 1_000_000),
        }
        if query.filters.namespace:
            predicates.append("namespace = :namespace")
            parameters["namespace"] = query.filters.namespace
        if query.filters.flow_id:
            predicates.append("flow = :flow")
            parameters["flow"] = query.filters.flow_id
        if query.filters.states:
            predicates.append("state = ANY(CAST(:states AS text[]))")
            parameters["states"] = list(query.filters.states)
        if query.filters.worker_groups:
            predicates.append("worker_group = ANY(CAST(:worker_groups AS text[]))")
            parameters["worker_groups"] = list(query.filters.worker_groups)
        if query.filters.labels:
            predicates.append("labels @> CAST(:labels AS jsonb)")
            parameters["labels"] = self._services.codec.dumps(query.filters.labels)
        if query.filters.dimensions:
            predicates.append("custom_dimensions @> CAST(:dimensions AS jsonb)")
            parameters["dimensions"] = self._services.codec.dumps(query.filters.dimensions)
        if query.sample_rate < 1:
            predicates.append("mod(abs(hashtextextended(row_id, 0)), 1000000) < :sample_threshold")
        statement = text(
            "WITH source_rows AS ("
            + _SOURCES[query.source]
            + ") SELECT * FROM source_rows WHERE "
            + " AND ".join(predicates)
            + " ORDER BY occurred_at DESC, row_id LIMIT :scan_limit"
        )
        try:
            async with self._services.transactions.tenant(tenant_id) as (
                connection,
                tenant_uuid,
            ):
                parameters["tenant_uuid"] = tenant_uuid
                await connection.execute(
                    text("SELECT set_config('statement_timeout', :timeout, true)"),
                    {"timeout": f"{query.timeout_ms}ms"},
                )
                fetched = (await connection.execute(statement, parameters)).mappings().all()
        except DBAPIError as exc:
            if "statement timeout" in str(exc).lower() or "querycanceled" in str(exc).lower():
                raise DashboardQueryTimeout(
                    f"dashboard query exceeded {query.timeout_ms} ms"
                ) from exc
            raise
        partial = len(fetched) > scan_limit
        rows = fetched[:scan_limit]
        result_rows, columns, aggregation_partial = self._render_rows(
            query,
            rows,
            from_time=from_time,
            to_time=to_time,
        )
        fresh_at = max((row["occurred_at"] for row in rows), default=now)
        return DashboardQueryResult(
            columns=columns,
            rows=tuple(result_rows),
            freshAt=fresh_at,
            partial=partial or aggregation_partial,
            sampled=query.sample_rate < 1,
            redacted=False,
            scannedRows=len(rows),
            limit=query.limit,
        )

    @staticmethod
    def _render_rows(
        query: DashboardQuery,
        rows: Sequence[RowMapping],
        *,
        from_time: datetime,
        to_time: datetime,
    ) -> tuple[list[dict[str, Any]], tuple[str, ...], bool]:
        if query.visualization is DashboardVisualization.TABLE:
            dimensions = query.group_by or _default_breakdown(query)
            rendered = [
                {
                    "occurredAt": row["occurred_at"].isoformat(),
                    **{dimension: _dimension_value(row, dimension) for dimension in dimensions},
                    "value": float(
                        row["duration_ms"]
                        if query.measure is DashboardMeasure.DURATION_MS
                        else row["numeric_value"]
                        if query.measure is DashboardMeasure.VALUE
                        else 1
                    ),
                }
                for row in rows[: query.limit]
            ]
            columns = ("occurredAt", *dimensions, "value")
            return rendered, columns, len(rows) > query.limit

        dimensions = (
            _default_breakdown(query)
            if query.visualization
            in {DashboardVisualization.STATUS_BREAKDOWN, DashboardVisualization.RANKED_LIST}
            else query.group_by
        )
        grouped: dict[tuple[str | None, ...], list[float]] = defaultdict(list)
        dimension_names = list(dimensions)
        for row in rows:
            dimension_values = [_dimension_value(row, dimension) for dimension in dimensions]
            if query.visualization is DashboardVisualization.TIME_SERIES:
                dimension_values.insert(
                    0,
                    _bucket_start(row["occurred_at"], to_time - from_time).isoformat(),
                )
            raw_value = (
                float(row["duration_ms"] or 0)
                if query.measure is DashboardMeasure.DURATION_MS
                else float(row["numeric_value"] or 0)
                if query.measure is DashboardMeasure.VALUE
                else 1.0
            )
            if query.visualization is DashboardVisualization.DISTRIBUTION:
                dimension_values.append(_distribution_bucket(raw_value))
            grouped[tuple(dimension_values)].append(raw_value)
        if query.visualization is DashboardVisualization.TIME_SERIES:
            dimension_names.insert(0, "bucketStart")
        if query.visualization is DashboardVisualization.DISTRIBUTION:
            dimension_names.append("range")
        rendered = []
        for key, measure_values in grouped.items():
            aggregate = _aggregate(measure_values, query.aggregation)
            if query.sample_rate < 1 and query.aggregation in {
                DashboardAggregation.COUNT,
                DashboardAggregation.SUM,
            }:
                aggregate /= query.sample_rate
            rendered.append(
                {
                    **dict(zip(dimension_names, key, strict=True)),
                    "value": round(aggregate, 6),
                }
            )
        if query.visualization is DashboardVisualization.RANKED_LIST:
            rendered.sort(key=lambda item: float(item["value"]), reverse=True)
        elif query.visualization is DashboardVisualization.TIME_SERIES:
            rendered.sort(key=lambda item: tuple(str(item[name]) for name in dimension_names))
        else:
            rendered.sort(key=lambda item: tuple(str(item[name]) for name in dimension_names))
        partial = len(rendered) > query.limit
        if query.visualization is DashboardVisualization.COUNTER and not rendered:
            rendered = [{"value": 0.0}]
        return rendered[: query.limit], (*dimension_names, "value"), partial
