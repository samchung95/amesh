from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SearchDocumentType(StrEnum):
    FLOW = "FLOW"
    EXECUTION = "EXECUTION"
    LOG = "LOG"
    ASSET = "ASSET"
    AUDIT = "AUDIT"


class SearchSortField(StrEnum):
    RELEVANCE = "RELEVANCE"
    TITLE = "TITLE"
    OCCURRED_AT = "OCCURRED_AT"
    UPDATED_AT = "UPDATED_AT"
    TYPE = "TYPE"
    STATE = "STATE"


class SearchSortDirection(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


class SearchRangeField(StrEnum):
    OCCURRED_AT = "OCCURRED_AT"
    UPDATED_AT = "UPDATED_AT"
    SOURCE_VERSION = "SOURCE_VERSION"


class SearchProjectionCondition(StrEnum):
    READY = "READY"
    REBUILDING = "REBUILDING"
    DEGRADED = "DEGRADED"


class SearchRange(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    field: SearchRangeField
    gte: datetime | int | None = None
    lte: datetime | int | None = None

    @model_validator(mode="after")
    def validate_values(self) -> SearchRange:
        values = (self.gte, self.lte)
        if values == (None, None):
            raise ValueError("search range requires gte or lte")
        expected = int if self.field is SearchRangeField.SOURCE_VERSION else datetime
        if any(value is not None and not isinstance(value, expected) for value in values):
            raise ValueError(f"{self.field.value} search range has an invalid value type")
        if self.gte is not None and self.lte is not None:
            if self.field is SearchRangeField.SOURCE_VERSION:
                invalid_order = cast(int, self.gte) > cast(int, self.lte)
            else:
                invalid_order = cast(datetime, self.gte) > cast(datetime, self.lte)
            if invalid_order:
                raise ValueError("search range gte cannot be greater than lte")
        return self


class SearchRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    query: str = Field(default="", max_length=500)
    types: tuple[SearchDocumentType, ...] = Field(default=(), max_length=5)
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    states: tuple[str, ...] = Field(default=(), max_length=20)
    labels: dict[str, str] = Field(default_factory=dict, max_length=20)
    fields: dict[str, str] = Field(default_factory=dict, max_length=20)
    from_time: datetime | None = Field(default=None, alias="from")
    to_time: datetime | None = Field(default=None, alias="to")
    ranges: tuple[SearchRange, ...] = Field(default=(), max_length=3)
    sort: SearchSortField = SearchSortField.RELEVANCE
    direction: SearchSortDirection = SearchSortDirection.DESC
    limit: int = Field(default=50, ge=1, le=200)
    cursor: str | None = Field(default=None, max_length=2048)

    @field_validator("types", "states")
    @classmethod
    def unique_tuple(cls, value: tuple[Any, ...]) -> tuple[Any, ...]:
        if len(value) != len(set(value)):
            raise ValueError("search filter values must be unique")
        return value

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, value: dict[str, str]) -> dict[str, str]:
        allowed = {
            "flowId",
            "executionId",
            "taskRunId",
            "level",
            "logger",
            "provider",
            "assetType",
            "resourceType",
            "action",
            "outcome",
            "actorId",
        }
        invalid = sorted(set(value) - allowed)
        if invalid:
            raise ValueError(f"unsupported search fields: {', '.join(invalid)}")
        return value

    @model_validator(mode="after")
    def validate_window_and_ranges(self) -> SearchRequest:
        if self.from_time is not None and self.to_time is not None:
            if self.to_time < self.from_time:
                raise ValueError("search 'to' cannot be earlier than 'from'")
            if (self.to_time - self.from_time).days > 366:
                raise ValueError("search time range cannot exceed 366 days")
        range_fields = [item.field for item in self.ranges]
        if len(range_fields) != len(set(range_fields)):
            raise ValueError("search range fields must be unique")
        return self

    def fingerprint(self, *, authorized_types: tuple[SearchDocumentType, ...]) -> str:
        payload = self.model_dump(
            mode="json",
            by_alias=True,
            exclude={"cursor", "limit"},
        )
        payload["types"] = [item.value for item in authorized_types]
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:24]


class SearchDocument(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    document_type: SearchDocumentType = Field(alias="documentType")
    document_id: str = Field(alias="documentId")
    namespace: str | None = None
    title: str
    summary: str
    state: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    fields: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(alias="occurredAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_version: int = Field(alias="sourceVersion", ge=0)
    relevance: float = Field(ge=0)


class SearchResponse(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    items: tuple[SearchDocument, ...]
    next_cursor: str | None = Field(alias="nextCursor")
    denied_types: tuple[SearchDocumentType, ...] = Field(alias="deniedTypes")
    projection_version: int = Field(alias="projectionVersion", ge=1)
    projection_condition: SearchProjectionCondition = Field(alias="projectionCondition")


class SearchProjectionStatus(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    projection_version: int = Field(alias="projectionVersion", ge=1)
    condition: SearchProjectionCondition
    documents_indexed: int = Field(alias="documentsIndexed", ge=0)
    source_documents: int = Field(alias="sourceDocuments", ge=0)
    progress: float = Field(ge=0, le=1)
    last_projected_at: datetime | None = Field(alias="lastProjectedAt")
    latest_source_at: datetime | None = Field(alias="latestSourceAt")
    lag_seconds: float | None = Field(alias="lagSeconds", ge=0)
    rebuild_started_at: datetime | None = Field(alias="rebuildStartedAt")
    rebuild_completed_at: datetime | None = Field(alias="rebuildCompletedAt")
    failures: int = Field(ge=0)
    last_error: str | None = Field(alias="lastError")


class SearchRebuildAccepted(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    accepted: bool = True
    projection_version: int = Field(alias="projectionVersion", ge=1)
    condition: SearchProjectionCondition = SearchProjectionCondition.REBUILDING


class SearchRebuildRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    reason: str = Field(min_length=1, max_length=500)
