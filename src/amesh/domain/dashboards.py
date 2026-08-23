from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_DIMENSION = re.compile(
    r"^(?:namespace|flow|state|workerGroup|level|metricName|assetType|provider|"
    r"outcome|checkType|unit|label\.[A-Za-z0-9_.-]{1,64}|"
    r"dimension\.[A-Za-z0-9_.-]{1,64})$"
)


class DashboardDataSource(StrEnum):
    EXECUTIONS = "EXECUTIONS"
    LOGS = "LOGS"
    METRICS = "METRICS"
    SLA = "SLA"
    WORKERS = "WORKERS"
    ASSETS = "ASSETS"


class DashboardVisualization(StrEnum):
    TIME_SERIES = "TIME_SERIES"
    TABLE = "TABLE"
    COUNTER = "COUNTER"
    DISTRIBUTION = "DISTRIBUTION"
    STATUS_BREAKDOWN = "STATUS_BREAKDOWN"
    RANKED_LIST = "RANKED_LIST"


class DashboardAggregation(StrEnum):
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    P50 = "P50"
    P95 = "P95"


class DashboardMeasure(StrEnum):
    COUNT = "COUNT"
    DURATION_MS = "DURATION_MS"
    VALUE = "VALUE"


class DashboardVisibility(StrEnum):
    PRIVATE = "PRIVATE"
    TENANT = "TENANT"


class DashboardDefinitionSource(StrEnum):
    BUILTIN = "BUILTIN"
    API = "API"
    GITOPS = "GITOPS"


class DashboardFilters(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    from_time: datetime | None = Field(default=None, alias="from")
    to_time: datetime | None = Field(default=None, alias="to")
    labels: dict[str, str] = Field(default_factory=dict, max_length=20)
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    flow_id: str | None = Field(default=None, alias="flowId", min_length=1, max_length=255)
    states: tuple[str, ...] = Field(default=(), max_length=20)
    worker_groups: tuple[str, ...] = Field(default=(), alias="workerGroups", max_length=20)
    dimensions: dict[str, str] = Field(default_factory=dict, max_length=20)

    @model_validator(mode="after")
    def validate_window(self) -> DashboardFilters:
        if self.from_time is not None and self.to_time is not None:
            if self.to_time <= self.from_time:
                raise ValueError("dashboard query 'to' must be later than 'from'")
            if (self.to_time - self.from_time).days > 90:
                raise ValueError("dashboard query time range cannot exceed 90 days")
        return self


class DashboardQuery(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source: DashboardDataSource
    visualization: DashboardVisualization
    measure: DashboardMeasure = DashboardMeasure.COUNT
    aggregation: DashboardAggregation = DashboardAggregation.COUNT
    group_by: tuple[str, ...] = Field(default=(), alias="groupBy", max_length=3)
    filters: DashboardFilters = Field(default_factory=DashboardFilters)
    limit: int = Field(default=100, ge=1, le=500)
    timeout_ms: int = Field(default=1500, alias="timeoutMs", ge=100, le=5000)
    sample_rate: float = Field(default=1.0, alias="sampleRate", ge=0.01, le=1.0)

    @field_validator("group_by")
    @classmethod
    def validate_dimensions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("dashboard groupBy dimensions must be unique")
        invalid = [item for item in value if _DIMENSION.fullmatch(item) is None]
        if invalid:
            raise ValueError(f"unsupported dashboard dimensions: {', '.join(invalid)}")
        return value

    @model_validator(mode="after")
    def validate_measure(self) -> DashboardQuery:
        allowed = {
            DashboardDataSource.EXECUTIONS: {
                DashboardMeasure.COUNT,
                DashboardMeasure.DURATION_MS,
            },
            DashboardDataSource.LOGS: {DashboardMeasure.COUNT},
            DashboardDataSource.METRICS: {
                DashboardMeasure.COUNT,
                DashboardMeasure.VALUE,
            },
            DashboardDataSource.SLA: {DashboardMeasure.COUNT},
            DashboardDataSource.WORKERS: {DashboardMeasure.COUNT},
            DashboardDataSource.ASSETS: {DashboardMeasure.COUNT},
        }[self.source]
        if self.measure not in allowed:
            raise ValueError(f"measure {self.measure} is unavailable for {self.source}")
        if (
            self.measure is DashboardMeasure.COUNT
            and self.aggregation is not DashboardAggregation.COUNT
        ):
            raise ValueError("COUNT measures require COUNT aggregation")
        return self


class DashboardWidget(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    widget_id: str = Field(alias="widgetId", pattern=r"^[a-z][a-z0-9_.-]{0,63}$")
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    query: DashboardQuery


class DashboardSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    visibility: DashboardVisibility = DashboardVisibility.PRIVATE
    viewer_ids: tuple[str, ...] = Field(default=(), alias="viewerIds", max_length=100)
    editor_ids: tuple[str, ...] = Field(default=(), alias="editorIds", max_length=100)
    widgets: tuple[DashboardWidget, ...] = Field(min_length=1, max_length=24)
    source: DashboardDefinitionSource = DashboardDefinitionSource.API

    @model_validator(mode="after")
    def validate_widgets(self) -> DashboardSpec:
        ids = [widget.widget_id for widget in self.widgets]
        if len(ids) != len(set(ids)):
            raise ValueError("dashboard widget IDs must be unique")
        return self


class DashboardDefinition(DashboardSpec):
    dashboard_id: str = Field(alias="dashboardId", pattern=r"^[a-z][a-z0-9_.-]{0,127}$")
    tenant_id: str = Field(alias="tenantId")
    version: int = Field(ge=1)
    owner_id: str = Field(alias="ownerId")
    builtin: bool = False
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class DashboardQueryResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]
    fresh_at: datetime = Field(alias="freshAt")
    partial: bool
    sampled: bool
    redacted: bool = False
    scanned_rows: int = Field(alias="scannedRows", ge=0)
    limit: int = Field(ge=1)


class DashboardWidgetResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    widget_id: str = Field(alias="widgetId")
    result: DashboardQueryResult


class DashboardRender(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    dashboard: DashboardDefinition
    widgets: tuple[DashboardWidgetResult, ...]
    rendered_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="renderedAt")
