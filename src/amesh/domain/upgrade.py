from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import new_runtime_id


class UpgradeCheckStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"


class UpgradePhase(StrEnum):
    PRE_UPGRADE = "PRE_UPGRADE"
    POST_UPGRADE = "POST_UPGRADE"


class UpgradeCapacityThresholds(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    maximum_database_bytes: int = Field(alias="maximumDatabaseBytes", gt=0)
    maximum_queued_work: int = Field(alias="maximumQueuedWork", gt=0)
    maximum_active_executions: int = Field(alias="maximumActiveExecutions", gt=0)


class UpgradeRelease(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    lts: bool
    support_starts_on: date = Field(alias="supportStartsOn")
    support_ends_on: date = Field(alias="supportEndsOn")
    schema_migration: str = Field(alias="schemaMigration", pattern=r"^[0-9]{4}_.+\.sql$")
    minimum_components: dict[str, str] = Field(alias="minimumComponents")

    @model_validator(mode="after")
    def validate_support_window(self) -> UpgradeRelease:
        if self.support_ends_on < self.support_starts_on:
            raise ValueError("release support end must not precede its start")
        return self


class UpgradePath(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    from_version: str = Field(alias="fromVersion")
    to_version: str = Field(alias="toVersion")
    rolling_compatible: bool = Field(alias="rollingCompatible")
    message_schema_versions: tuple[int, ...] = Field(alias="messageSchemaVersions", min_length=1)
    rollback_window_hours: int = Field(alias="rollbackWindowHours", ge=0)
    restoration_guidance: str = Field(alias="restorationGuidance", min_length=1)


class UpgradePolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.upgrade-policy/v1"] = Field(alias="schemaVersion")
    current_version: str = Field(alias="currentVersion")
    capacity_thresholds: UpgradeCapacityThresholds = Field(alias="capacityThresholds")
    releases: tuple[UpgradeRelease, ...]
    paths: tuple[UpgradePath, ...]

    @model_validator(mode="after")
    def validate_release_graph(self) -> UpgradePolicy:
        versions = [release.version for release in self.releases]
        if len(versions) != len(set(versions)):
            raise ValueError("upgrade releases must have unique versions")
        if self.current_version not in versions:
            raise ValueError("currentVersion must identify a declared release")
        edges = [(path.from_version, path.to_version) for path in self.paths]
        if len(edges) != len(set(edges)):
            raise ValueError("upgrade paths must be unique")
        unknown = {
            version
            for edge in edges
            for version in edge
            if version not in versions
        }
        if unknown:
            raise ValueError(f"upgrade paths reference unknown releases: {sorted(unknown)}")
        return self

    def release(self, version: str) -> UpgradeRelease:
        try:
            return next(item for item in self.releases if item.version == version)
        except StopIteration as exc:
            raise ValueError(f"release {version!r} is not supported") from exc

    def path(self, from_version: str, to_version: str) -> UpgradePath:
        try:
            return next(
                item
                for item in self.paths
                if item.from_version == from_version and item.to_version == to_version
            )
        except StopIteration as exc:
            raise ValueError(
                f"upgrade path {from_version} -> {to_version} is not supported"
            ) from exc


class UpgradeCheck(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str
    category: str
    status: UpgradeCheckStatus
    detail: str
    remediation: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


class RollingUpgradeStep(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    order: int = Field(ge=1)
    role: str
    action: str
    verification: str


class UpgradeReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    report_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    phase: UpgradePhase
    from_version: str = Field(alias="fromVersion")
    to_version: str = Field(alias="toVersion")
    observed_at: datetime = Field(alias="observedAt")
    safe_to_proceed: bool = Field(alias="safeToProceed")
    rolling_compatible: bool = Field(alias="rollingCompatible")
    checks: tuple[UpgradeCheck, ...]
    warnings: tuple[str, ...] = ()
    rolling_plan: tuple[RollingUpgradeStep, ...] = Field(default=(), alias="rollingPlan")
    restoration_guidance: str = Field(alias="restorationGuidance")
    report_fingerprint: str = Field(alias="reportFingerprint")


class UpgradeDatabaseInventory(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    applied_migrations: tuple[str, ...] = Field(alias="appliedMigrations")
    migration_checksums: dict[str, str] = Field(alias="migrationChecksums")
    database_bytes: int = Field(alias="databaseBytes", ge=0)
    queued_work: int = Field(alias="queuedWork", ge=0)
    active_executions: int = Field(alias="activeExecutions", ge=0)
    legacy_execution_events: int = Field(alias="legacyExecutionEvents", ge=0)
    unsupported_execution_events: int = Field(alias="unsupportedExecutionEvents", ge=0)


class PersistedEventMigration(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    eligible_events: int = Field(alias="eligibleEvents", ge=0)
    migrated_events: int = Field(alias="migratedEvents", ge=0)
    remaining_events: int = Field(alias="remainingEvents", ge=0)
    confirmation_phrase: str = Field(alias="confirmationPhrase")
    applied: bool
    evidence_event_id: UUID | None = Field(default=None, alias="evidenceEventId")


class ConfigurationMigrationKind(StrEnum):
    FLOW = "flow"
    PLUGIN = "plugin"


class ConfigurationMigration(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: ConfigurationMigrationKind
    target_version: str = Field(alias="targetVersion")
    changed: bool
    canonical: dict[str, Any]
    warnings: tuple[str, ...] = ()


class UpgradeReportRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    from_version: str = Field(alias="fromVersion")
    to_version: str = Field(alias="toVersion")


class PersistedEventMigrationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    confirmation: str
    reason: str = Field(min_length=1, max_length=1_024)
    batch_size: int = Field(default=1_000, alias="batchSize", ge=1, le=10_000)


class ConfigurationMigrationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: ConfigurationMigrationKind
    target_version: str = Field(alias="targetVersion")
    document: dict[str, Any]
