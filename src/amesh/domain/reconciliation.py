from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReconciliationMode(StrEnum):
    DRY_RUN = "DRY_RUN"
    APPLY = "APPLY"


class ReconciliationTargetType(StrEnum):
    TENANT = "TENANT"
    EXECUTION = "EXECUTION"
    TRIGGER = "TRIGGER"
    WORKER = "WORKER"
    TIME_RANGE = "TIME_RANGE"


class ReconciliationInvariant(StrEnum):
    EXPIRED_LEASE = "EXPIRED_LEASE"
    ORPHAN_TASK_RUN = "ORPHAN_TASK_RUN"
    STUCK_EXECUTION = "STUCK_EXECUTION"
    MISSING_DISPATCH = "MISSING_DISPATCH"
    UNPROJECTED_EVENT = "UNPROJECTED_EVENT"
    MISSING_SCHEDULE_PROJECTION = "MISSING_SCHEDULE_PROJECTION"


class ReconciliationDisposition(StrEnum):
    DETECTED = "DETECTED"
    REPAIRED = "REPAIRED"
    QUARANTINED = "QUARANTINED"


class ReconciliationRunState(StrEnum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReconciliationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    mode: ReconciliationMode = ReconciliationMode.DRY_RUN
    execution_id: UUID | None = Field(default=None, alias="executionId")
    trigger_definition_id: UUID | None = Field(default=None, alias="triggerDefinitionId")
    worker_id: UUID | None = Field(default=None, alias="workerId")
    since: datetime | None = None
    until: datetime | None = None
    stale_after_seconds: int = Field(default=300, ge=30, le=86_400, alias="staleAfterSeconds")
    max_findings: int = Field(default=500, ge=1, le=1_000, alias="maxFindings")
    max_repairs: int = Field(default=25, ge=0, le=100, alias="maxRepairs")
    idempotency_key: str = Field(min_length=1, max_length=256, alias="idempotencyKey")
    reason: str = Field(min_length=1, max_length=1_024)

    @model_validator(mode="after")
    def validate_target(self) -> ReconciliationRequest:
        selected = sum(
            value is not None
            for value in (self.execution_id, self.trigger_definition_id, self.worker_id)
        ) + int(self.since is not None or self.until is not None)
        if selected > 1:
            raise ValueError("reconciliation accepts exactly one target dimension")
        if self.since is not None and self.until is not None and self.since >= self.until:
            raise ValueError("reconciliation since must be before until")
        if self.mode is ReconciliationMode.APPLY and self.max_repairs < 1:
            raise ValueError("apply reconciliation requires at least one permitted repair")
        return self

    @property
    def target_type(self) -> ReconciliationTargetType:
        if self.execution_id is not None:
            return ReconciliationTargetType.EXECUTION
        if self.trigger_definition_id is not None:
            return ReconciliationTargetType.TRIGGER
        if self.worker_id is not None:
            return ReconciliationTargetType.WORKER
        if self.since is not None or self.until is not None:
            return ReconciliationTargetType.TIME_RANGE
        return ReconciliationTargetType.TENANT

    @property
    def target_id(self) -> str | None:
        selected = self.execution_id or self.trigger_definition_id or self.worker_id
        return str(selected) if selected is not None else None


class ReconciliationFinding(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    finding_id: UUID = Field(alias="id")
    invariant: ReconciliationInvariant
    resource_type: str = Field(alias="resourceType")
    resource_id: str = Field(alias="resourceId")
    expected_version: int | None = Field(default=None, ge=0, alias="expectedVersion")
    disposition: ReconciliationDisposition
    repair_action: str | None = Field(default=None, alias="repairAction")
    detail: dict[str, Any] = Field(default_factory=dict)
    runbook: str
    observed_at: datetime = Field(alias="observedAt")
    resolved_at: datetime | None = Field(default=None, alias="resolvedAt")


class ReconciliationRun(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    run_id: UUID = Field(alias="id")
    tenant_id: str = Field(alias="tenantId")
    mode: ReconciliationMode
    target_type: ReconciliationTargetType = Field(alias="targetType")
    target_id: str | None = Field(default=None, alias="targetId")
    since: datetime | None = None
    until: datetime | None = None
    state: ReconciliationRunState
    max_repairs: int = Field(ge=0, alias="maxRepairs")
    repairs_applied: int = Field(ge=0, alias="repairsApplied")
    finding_count: int = Field(ge=0, alias="findingCount")
    unresolved_count: int = Field(ge=0, alias="unresolvedCount")
    actor_id: str = Field(alias="actorId")
    reason: str
    idempotency_key: str = Field(alias="idempotencyKey")
    created_at: datetime = Field(alias="createdAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    findings: tuple[ReconciliationFinding, ...] = ()
