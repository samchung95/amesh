from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import new_runtime_id


class AuditExportFormat(StrEnum):
    JSON = "JSON"
    NDJSON = "NDJSON"


class AuditExportDestination(StrEnum):
    FILE = "FILE"
    OBJECT_STORAGE = "OBJECT_STORAGE"


class AuditArtifactKind(StrEnum):
    AUDIT = "AUDIT"
    COMPLIANCE = "COMPLIANCE"


class ComplianceEvidenceCategory(StrEnum):
    ACCESS_REVIEW = "ACCESS_REVIEW"
    CHANGE_EVIDENCE = "CHANGE_EVIDENCE"
    BACKUP_RESTORE = "BACKUP_RESTORE"
    VULNERABILITY = "VULNERABILITY"
    INCIDENT = "INCIDENT"
    PROVENANCE = "PROVENANCE"


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    cursor: int = Field(ge=1)
    event_id: UUID = Field(alias="eventId")
    tenant_id: str = Field(alias="tenantId")
    actor_id: str = Field(alias="actorId")
    delegated_actor_id: str | None = Field(default=None, alias="delegatedActorId")
    action: str
    resource_type: str = Field(alias="resourceType")
    resource_id: str | None = Field(default=None, alias="resourceId")
    outcome: str
    reason: str
    correlation_id: UUID = Field(alias="correlationId")
    trace_id: UUID = Field(alias="traceId")
    source: dict[str, Any]
    evidence: dict[str, Any]
    occurred_at: datetime = Field(alias="occurredAt")
    previous_hash: str | None = Field(default=None, alias="previousHash")
    event_hash: str = Field(alias="eventHash", pattern=r"^[0-9a-f]{64}$")
    retention_until: datetime = Field(alias="retentionUntil")


class AuditEventPage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    items: tuple[AuditEvent, ...]
    next_cursor: int | None = Field(default=None, alias="nextCursor")


class AuditIntegrityReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    valid: bool
    checked_events: int = Field(alias="checkedEvents", ge=0)
    anchor_hash: str | None = Field(default=None, alias="anchorHash")
    head_hash: str | None = Field(default=None, alias="headHash")
    first_broken_event_id: UUID | None = Field(default=None, alias="firstBrokenEventId")
    reason: str | None = None


class AuditRetentionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    retention_days: int = Field(default=365, alias="retentionDays", ge=1, le=36_500)
    updated_by: str = Field(default="system", alias="updatedBy")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="updatedAt")


class AuditRetentionPolicyUpdate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    retention_days: int = Field(alias="retentionDays", ge=1, le=36_500)


class AuditLegalHoldCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    reason: str = Field(min_length=1, max_length=2048)
    starts_at: datetime = Field(alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")

    @model_validator(mode="after")
    def validate_range(self) -> AuditLegalHoldCreate:
        if self.ends_at is not None and self.ends_at <= self.starts_at:
            raise ValueError("endsAt must be after startsAt")
        return self


class AuditLegalHold(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    hold_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str = Field(alias="tenantId")
    name: str
    reason: str
    starts_at: datetime = Field(alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    active: bool = True
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")
    released_by: str | None = Field(default=None, alias="releasedBy")
    released_at: datetime | None = Field(default=None, alias="releasedAt")


class AuditRetentionResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    deleted_events: int = Field(alias="deletedEvents", ge=0)
    anchor_hash: str | None = Field(default=None, alias="anchorHash")
    stopped_by_legal_hold: bool = Field(default=False, alias="stoppedByLegalHold")


class AuditExportReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    export_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str = Field(alias="tenantId")
    artifact_kind: AuditArtifactKind = Field(alias="artifactKind")
    destination: AuditExportDestination
    format: str
    event_count: int = Field(alias="eventCount", ge=0)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
    signature: str
    object_uri: str | None = Field(default=None, alias="objectUri")
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")


class AuditExportRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    format: AuditExportFormat = AuditExportFormat.NDJSON
    limit: int = Field(default=10_000, ge=1, le=10_000)
    action: str | None = Field(default=None, max_length=255)
    resource_type: str | None = Field(default=None, alias="resourceType", max_length=128)
    outcome: str | None = Field(default=None, max_length=64)
    occurred_from: datetime | None = Field(default=None, alias="occurredFrom")
    occurred_to: datetime | None = Field(default=None, alias="occurredTo")

    @model_validator(mode="after")
    def validate_range(self) -> AuditExportRequest:
        if (
            self.occurred_from is not None
            and self.occurred_to is not None
            and self.occurred_to <= self.occurred_from
        ):
            raise ValueError("occurredTo must be after occurredFrom")
        return self


class CompliancePackageRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    occurred_from: datetime | None = Field(default=None, alias="occurredFrom")
    occurred_to: datetime | None = Field(default=None, alias="occurredTo")
    max_audit_events: int = Field(default=10_000, alias="maxAuditEvents", ge=1, le=10_000)

    @model_validator(mode="after")
    def validate_range(self) -> CompliancePackageRequest:
        if (
            self.occurred_from is not None
            and self.occurred_to is not None
            and self.occurred_to <= self.occurred_from
        ):
            raise ValueError("occurredTo must be after occurredFrom")
        return self


class ComplianceEvidenceCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    category: ComplianceEvidenceCategory
    title: str = Field(min_length=1, max_length=255)
    source: str = Field(min_length=1, max_length=512)
    occurred_at: datetime = Field(alias="occurredAt")
    payload: dict[str, Any] = Field(default_factory=dict)


class ComplianceEvidenceRecord(ComplianceEvidenceCreate):
    evidence_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str = Field(alias="tenantId")
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")


class ComplianceSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    access_reviews: tuple[dict[str, Any], ...] = Field(alias="accessReviews")
    change_evidence: tuple[dict[str, Any], ...] = Field(alias="changeEvidence")
    audit_records: tuple[dict[str, Any], ...] = Field(alias="auditRecords")
    backup_restore_evidence: tuple[dict[str, Any], ...] = Field(alias="backupRestoreEvidence")
    vulnerability_results: tuple[dict[str, Any], ...] = Field(alias="vulnerabilityResults")
    incident_records: tuple[dict[str, Any], ...] = Field(alias="incidentRecords")
    provenance: tuple[dict[str, Any], ...]
