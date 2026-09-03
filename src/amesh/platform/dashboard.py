from __future__ import annotations

from datetime import UTC, datetime

from amesh.domain.dashboards import (
    DashboardAggregation,
    DashboardDataSource,
    DashboardDefinition,
    DashboardDefinitionSource,
    DashboardFilters,
    DashboardMeasure,
    DashboardQuery,
    DashboardVisibility,
    DashboardVisualization,
    DashboardWidget,
)

_BUILTIN_AT = datetime(2026, 1, 1, tzinfo=UTC)


def _widget(
    widget_id: str,
    title: str,
    source: DashboardDataSource,
    visualization: DashboardVisualization,
    *,
    measure: DashboardMeasure = DashboardMeasure.COUNT,
    aggregation: DashboardAggregation = DashboardAggregation.COUNT,
    group_by: tuple[str, ...] = (),
    limit: int = 100,
) -> DashboardWidget:
    return DashboardWidget(
        widgetId=widget_id,
        title=title,
        query=DashboardQuery(
            source=source,
            visualization=visualization,
            measure=measure,
            aggregation=aggregation,
            groupBy=group_by,
            limit=limit,
        ),
    )


_BUILTINS: dict[str, tuple[str, str, tuple[DashboardWidget, ...]]] = {
    "builtin.instance": (
        "Instance overview",
        "Execution, log and worker posture across the selected tenant.",
        (
            _widget(
                "executions",
                "Executions",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.COUNTER,
            ),
            _widget(
                "states",
                "Execution states",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.STATUS_BREAKDOWN,
            ),
            _widget(
                "activity",
                "Execution activity",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.TIME_SERIES,
                group_by=("state",),
            ),
            _widget(
                "log_levels",
                "Log levels",
                DashboardDataSource.LOGS,
                DashboardVisualization.RANKED_LIST,
                group_by=("level",),
                limit=8,
            ),
        ),
    ),
    "builtin.tenant": (
        "Tenant operations",
        "Flow activity, assets and ranked workload for one tenant.",
        (
            _widget(
                "flow_rank",
                "Top flows",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.RANKED_LIST,
                group_by=("flow",),
                limit=10,
            ),
            _widget(
                "flow_series",
                "Flow activity",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.TIME_SERIES,
                group_by=("flow",),
            ),
            _widget(
                "assets",
                "Asset types",
                DashboardDataSource.ASSETS,
                DashboardVisualization.STATUS_BREAKDOWN,
                group_by=("assetType",),
            ),
        ),
    ),
    "builtin.namespace": (
        "Namespace health",
        "Execution and log posture filtered to a namespace.",
        (
            _widget(
                "namespace_states",
                "States",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.STATUS_BREAKDOWN,
            ),
            _widget(
                "namespace_activity",
                "Activity",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.TIME_SERIES,
                group_by=("state",),
            ),
            _widget(
                "recent_logs",
                "Recent log levels",
                DashboardDataSource.LOGS,
                DashboardVisualization.TABLE,
                group_by=("flow", "level"),
                limit=25,
            ),
        ),
    ),
    "builtin.flow": (
        "Flow performance",
        "Duration, metrics and recent executions for one flow.",
        (
            _widget(
                "durations",
                "Duration distribution",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.DISTRIBUTION,
                measure=DashboardMeasure.DURATION_MS,
                aggregation=DashboardAggregation.P95,
            ),
            _widget(
                "metrics",
                "Metric series",
                DashboardDataSource.METRICS,
                DashboardVisualization.TIME_SERIES,
                measure=DashboardMeasure.VALUE,
                aggregation=DashboardAggregation.AVG,
                group_by=("metricName",),
            ),
            _widget(
                "recent",
                "Recent states",
                DashboardDataSource.EXECUTIONS,
                DashboardVisualization.TABLE,
                group_by=("state",),
                limit=25,
            ),
        ),
    ),
    "builtin.workers": (
        "Worker fleet",
        "Worker status and group distribution.",
        (
            _widget(
                "worker_states",
                "Worker states",
                DashboardDataSource.WORKERS,
                DashboardVisualization.STATUS_BREAKDOWN,
            ),
            _widget(
                "worker_groups",
                "Worker groups",
                DashboardDataSource.WORKERS,
                DashboardVisualization.RANKED_LIST,
                group_by=("workerGroup",),
                limit=20,
            ),
            _widget(
                "worker_table",
                "Workers",
                DashboardDataSource.WORKERS,
                DashboardVisualization.TABLE,
                group_by=("workerGroup", "state"),
                limit=50,
            ),
        ),
    ),
    "builtin.sla": (
        "SLA and checks",
        "Check outcomes, trends and highest-volume check types.",
        (
            _widget(
                "sla_outcomes",
                "Outcomes",
                DashboardDataSource.SLA,
                DashboardVisualization.STATUS_BREAKDOWN,
                group_by=("outcome",),
            ),
            _widget(
                "sla_series",
                "Outcome trend",
                DashboardDataSource.SLA,
                DashboardVisualization.TIME_SERIES,
                group_by=("outcome",),
            ),
            _widget(
                "sla_rank",
                "Check types",
                DashboardDataSource.SLA,
                DashboardVisualization.RANKED_LIST,
                group_by=("checkType",),
                limit=12,
            ),
        ),
    ),
}


def builtin_dashboards(tenant_id: str) -> tuple[DashboardDefinition, ...]:
    return tuple(builtin_dashboard(dashboard_id, tenant_id) for dashboard_id in _BUILTINS)


def builtin_dashboard(dashboard_id: str, tenant_id: str) -> DashboardDefinition:
    try:
        title, description, widgets = _BUILTINS[dashboard_id]
    except KeyError as exc:
        raise LookupError(f"dashboard {dashboard_id!r} does not exist") from exc
    return DashboardDefinition(
        dashboardId=dashboard_id,
        tenantId=tenant_id,
        title=title,
        description=description,
        visibility=DashboardVisibility.TENANT,
        viewerIds=(),
        editorIds=(),
        widgets=widgets,
        source=DashboardDefinitionSource.BUILTIN,
        version=1,
        ownerId="system",
        builtin=True,
        createdAt=_BUILTIN_AT,
        updatedAt=_BUILTIN_AT,
    )


def apply_dashboard_filters(query: DashboardQuery, filters: DashboardFilters) -> DashboardQuery:
    base = query.filters
    merged = DashboardFilters.model_validate(
        {
            "from": filters.from_time or base.from_time,
            "to": filters.to_time or base.to_time,
            "labels": {**base.labels, **filters.labels},
            "namespace": filters.namespace or base.namespace,
            "flowId": filters.flow_id or base.flow_id,
            "states": filters.states or base.states,
            "workerGroups": filters.worker_groups or base.worker_groups,
            "dimensions": {**base.dimensions, **filters.dimensions},
        }
    )
    return query.model_copy(update={"filters": merged})


def can_view_dashboard(definition: DashboardDefinition, principal_id: str) -> bool:
    return (
        definition.builtin
        or definition.visibility is DashboardVisibility.TENANT
        or principal_id == definition.owner_id
        or principal_id in definition.viewer_ids
        or principal_id in definition.editor_ids
    )


def can_edit_dashboard(definition: DashboardDefinition, principal_id: str) -> bool:
    return not definition.builtin and (
        principal_id == definition.owner_id or principal_id in definition.editor_ids
    )
