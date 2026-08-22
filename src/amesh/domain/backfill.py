from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BackfillState(StrEnum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class BackfillSelectionKind(StrEnum):
    TIME_RANGE = "TIME_RANGE"
    PARTITIONS = "PARTITIONS"
    OCCURRENCES = "OCCURRENCES"
    REPLAY = "REPLAY"


class BackfillItemState(StrEnum):
    PENDING = "PENDING"
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"


class TimeRangeSelection(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    start: datetime
    end: datetime
    interval_seconds: int = Field(alias="intervalSeconds", ge=1, le=31_536_000)

    @model_validator(mode="after")
    def validate_bounds(self) -> TimeRangeSelection:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("backfill time-range bounds must include time zones")
        if self.end <= self.start:
            raise ValueError("backfill time-range end must be after start")
        return self


class BackfillSelection(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    time_range: TimeRangeSelection | None = Field(default=None, alias="timeRange")
    partitions: tuple[str, ...] = ()
    occurrences: tuple[datetime, ...] = ()
    source_execution_ids: tuple[UUID, ...] = Field(default=(), alias="sourceExecutionIds")

    @model_validator(mode="after")
    def validate_one_selector(self) -> BackfillSelection:
        selected = sum(
            (
                self.time_range is not None,
                bool(self.partitions),
                bool(self.occurrences),
                bool(self.source_execution_ids),
            )
        )
        if selected != 1:
            raise ValueError("exactly one backfill selector must be provided")
        if any(not value.strip() for value in self.partitions):
            raise ValueError("backfill partition keys must not be empty")
        if any(value.tzinfo is None for value in self.occurrences):
            raise ValueError("backfill occurrences must include time zones")
        return self

    @property
    def kind(self) -> BackfillSelectionKind:
        if self.time_range is not None:
            return BackfillSelectionKind.TIME_RANGE
        if self.partitions:
            return BackfillSelectionKind.PARTITIONS
        if self.occurrences:
            return BackfillSelectionKind.OCCURRENCES
        return BackfillSelectionKind.REPLAY

    def item_keys(self, *, maximum: int = 10_000) -> tuple[str, ...]:
        if maximum < 1:
            raise ValueError("maximum backfill preview size must be positive")
        if self.time_range is not None:
            range_values: list[str] = []
            current = self.time_range.start.astimezone(UTC)
            end = self.time_range.end.astimezone(UTC)
            step = timedelta(seconds=self.time_range.interval_seconds)
            while current < end:
                range_values.append(f"time:{current.isoformat()}")
                if len(range_values) > maximum:
                    raise ValueError(f"backfill exceeds the {maximum}-item safety limit")
                current += step
            return tuple(range_values)
        if self.partitions:
            values = tuple(f"partition:{value}" for value in dict.fromkeys(self.partitions))
        elif self.occurrences:
            values = tuple(
                f"occurrence:{value}"
                for value in sorted({item.astimezone(UTC).isoformat() for item in self.occurrences})
            )
        else:
            values = tuple(f"replay:{value}" for value in dict.fromkeys(self.source_execution_ids))
        if len(values) > maximum:
            raise ValueError(f"backfill exceeds the {maximum}-item safety limit")
        return values


class BackfillSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    namespace: str = Field(min_length=1, max_length=255)
    flow_id: str = Field(alias="flowId", min_length=1, max_length=255)
    flow_revision: int = Field(alias="flowRevision", ge=1)
    selection: BackfillSelection
    inputs: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    max_concurrency: int = Field(default=1, alias="maxConcurrency", ge=1, le=10_000)
    rate_per_minute: int = Field(default=60, alias="ratePerMinute", ge=1, le=1_000_000)
    priority: int = Field(default=0, ge=-1_000_000, le=1_000_000)

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, value: dict[str, str]) -> dict[str, str]:
        for key, item in value.items():
            if not key or len(key) > 128 or len(item) > 256:
                raise ValueError("label keys must be 1-128 characters and values at most 256")
            if key.startswith(("amesh.", "system.")):
                raise ValueError(f"label {key!r} uses a protected system prefix")
        return value


class BackfillPreview(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    selection_kind: BackfillSelectionKind = Field(alias="selectionKind")
    execution_count: int = Field(alias="executionCount", ge=0)
    estimated_task_runs: int = Field(alias="estimatedTaskRuns", ge=0)
    estimated_cost_units: int = Field(alias="estimatedCostUnits", ge=0)
    idempotency_key_template: str = Field(alias="idempotencyKeyTemplate")
    warnings: tuple[str, ...]


class BackfillItem(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    item_id: UUID = Field(alias="itemId")
    backfill_id: UUID = Field(alias="backfillId")
    occurrence_key: str = Field(alias="occurrenceKey")
    state: BackfillItemState
    scheduled_for: datetime | None = Field(default=None, alias="scheduledFor")
    partition_key: str | None = Field(default=None, alias="partitionKey")
    source_execution_id: UUID | None = Field(default=None, alias="sourceExecutionId")
    execution_id: UUID | None = Field(default=None, alias="executionId")


class BackfillRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    backfill_id: UUID = Field(alias="backfillId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    flow_id: str = Field(alias="flowId")
    flow_revision: int = Field(alias="flowRevision", ge=1)
    state: BackfillState
    selection_kind: BackfillSelectionKind = Field(alias="selectionKind")
    inputs: dict[str, Any]
    labels: dict[str, str]
    max_concurrency: int = Field(alias="maxConcurrency", ge=1)
    rate_per_minute: int = Field(alias="ratePerMinute", ge=1)
    priority: int
    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    running: int = Field(ge=0)
    succeeded: int = Field(ge=0)
    failed: int = Field(ge=0)
    cancelled: int = Field(ge=0)
    duration_seconds: float = Field(alias="durationSeconds", ge=0)
    estimated_cost_units: int = Field(alias="estimatedCostUnits", ge=0)
    actual_cost_units: int = Field(alias="actualCostUnits", ge=0)
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")
