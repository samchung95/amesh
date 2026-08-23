from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LifecycleResourceType(StrEnum):
    EXECUTION = "EXECUTION"
    LOG = "LOG"
    METRIC = "METRIC"
    ARTIFACT = "ARTIFACT"
    CACHE = "CACHE"


class LifecycleScope(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"
    LABEL = "LABEL"


class LifecycleTrigger(StrEnum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"


class LifecycleJobState(StrEnum):
    PREVIEWED = "PREVIEWED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING_EXTERNAL = "WAITING_EXTERNAL"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class LifecyclePolicyDraft(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    resource_type: LifecycleResourceType = Field(alias="resourceType")
    scope: LifecycleScope
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    label_selector: dict[str, str] = Field(default_factory=dict, alias="labelSelector")
    retention_days: int = Field(alias="retentionDays", ge=1, le=36_500)
    batch_size: int = Field(default=100, alias="batchSize", ge=1, le=1_000)
    schedule_interval_minutes: int | None = Field(
        default=None,
        alias="scheduleIntervalMinutes",
        ge=5,
        le=525_600,
    )
    enabled: bool = True
    reason: str = Field(min_length=3, max_length=2_048)

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if self.scope is LifecycleScope.NAMESPACE and self.namespace is None:
            raise ValueError("namespace scope requires namespace")
        if self.scope is not LifecycleScope.NAMESPACE and self.namespace is not None:
            raise ValueError("namespace is only valid for namespace scope")
        if self.scope is LifecycleScope.LABEL and not self.label_selector:
            raise ValueError("label scope requires labelSelector")
        if self.scope is not LifecycleScope.LABEL and self.label_selector:
            raise ValueError("labelSelector is only valid for label scope")
        return self


class LifecyclePolicy(LifecyclePolicyDraft):
    policy_id: UUID = Field(alias="id")
    tenant_id: str | None = Field(alias="tenantId")
    next_run_at: datetime | None = Field(default=None, alias="nextRunAt")
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_by: str = Field(alias="updatedBy")
    updated_at: datetime = Field(alias="updatedAt")
    version: int = Field(ge=1)


class LifecycleLegalHoldDraft(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    reason: str = Field(min_length=3, max_length=2_048)
    resource_type: LifecycleResourceType | None = Field(default=None, alias="resourceType")
    resource_id: str | None = Field(default=None, alias="resourceId", max_length=255)
    namespace: str | None = Field(default=None, max_length=255)
    label_selector: dict[str, str] = Field(default_factory=dict, alias="labelSelector")
    data_from: datetime | None = Field(default=None, alias="dataFrom")
    data_to: datetime | None = Field(default=None, alias="dataTo")

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.data_from is not None and self.data_to is not None and self.data_to <= self.data_from:
            raise ValueError("dataTo must be after dataFrom")
        return self


class LifecycleLegalHold(LifecycleLegalHoldDraft):
    hold_id: UUID = Field(alias="id")
    tenant_id: str = Field(alias="tenantId")
    active: bool
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    released_by: str | None = Field(default=None, alias="releasedBy")
    released_at: datetime | None = Field(default=None, alias="releasedAt")


class LifecyclePreviewRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    policy_id: UUID = Field(alias="policyId")
    reason: str = Field(min_length=3, max_length=2_048)


class LifecycleExecuteRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    confirmation: str = Field(min_length=1, max_length=128)


class LifecycleJob(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    job_id: UUID = Field(alias="id")
    tenant_id: str = Field(alias="tenantId")
    policy_id: UUID = Field(alias="policyId")
    trigger: LifecycleTrigger
    state: LifecycleJobState
    cutoff: datetime
    policy_snapshot: dict[str, Any] = Field(alias="policySnapshot")
    estimated_records: int = Field(alias="estimatedRecords", ge=0)
    estimated_bytes: int = Field(alias="estimatedBytes", ge=0)
    protected_records: int = Field(alias="protectedRecords", ge=0)
    active_records: int = Field(alias="activeRecords", ge=0)
    processed_records: int = Field(alias="processedRecords", ge=0)
    processed_bytes: int = Field(alias="processedBytes", ge=0)
    batch_size: int = Field(alias="batchSize", ge=1, le=1_000)
    cursor: str | None = None
    retry_count: int = Field(alias="retryCount", ge=0)
    last_error: str | None = Field(default=None, alias="lastError")
    evidence: dict[str, Any]
    reason: str
    actor_id: str = Field(alias="actorId")
    preview_expires_at: datetime = Field(alias="previewExpiresAt")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    confirmation_phrase: str = Field(alias="confirmationPhrase")


class LifecycleObjectDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    job_id: UUID
    ordinal: int
    tenant_id: str
    uri: str
    size_bytes: int = Field(ge=0)


class LifecycleBatch(BaseModel):
    model_config = ConfigDict(frozen=True)

    job: LifecycleJob
    objects: tuple[LifecycleObjectDecision, ...] = ()


class LifecycleScheduleResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    jobs_created: int = Field(alias="jobsCreated", ge=0)
    batches_processed: int = Field(alias="batchesProcessed", ge=0)
    records_processed: int = Field(alias="recordsProcessed", ge=0)
    checked_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="checkedAt",
    )
