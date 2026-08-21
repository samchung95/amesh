from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from .identity import NaturalId, TenantSlug, new_runtime_id
from .resources import ResourceLifecycle, ResourceMetadata

SYSTEM_TENANT_ID = UUID("00000000-0000-7000-8000-000000000002")
SYSTEM_TENANT_SLUG = "amesh-system"


class TenantStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TOMBSTONED = "TOMBSTONED"


def validate_policy_reference(value: str) -> str:
    if not value.strip() or len(value) > 512:
        raise ValueError("tenant policy reference must contain 1 to 512 characters")
    return value


PolicyReference = Annotated[str, AfterValidator(validate_policy_reference)]


class TenantPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    retention_days: int = Field(default=30, ge=1, le=36_500)
    max_concurrent_executions: int = Field(default=100, ge=1, le=1_000_000)
    max_storage_bytes: int = Field(default=10_737_418_240, ge=1)
    encryption_key_ref: PolicyReference | None = None
    identity_provider_refs: tuple[PolicyReference, ...] = ()
    plugin_allowlist: tuple[PolicyReference, ...] = ("*",)
    feature_flags: dict[NaturalId, bool] = Field(default_factory=dict)
    worker_groups: tuple[NaturalId, ...] = ("default",)

    @model_validator(mode="after")
    def require_policy_consumers(self) -> TenantPolicy:
        if not self.plugin_allowlist:
            raise ValueError("tenant plugin allowlist cannot be empty")
        if not self.worker_groups:
            raise ValueError("tenant requires at least one worker group")
        return self

    def allows_plugin(self, task_type: str) -> bool:
        return "*" in self.plugin_allowlist or task_type in self.plugin_allowlist

    def feature_enabled(self, name: str, *, default: bool = True) -> bool:
        return self.feature_flags.get(name, default)


class TenantDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=new_runtime_id)
    slug: TenantSlug
    display_name: str = Field(min_length=1, max_length=255)
    status: TenantStatus = TenantStatus.ACTIVE
    policy: TenantPolicy = Field(default_factory=TenantPolicy)
    storage_prefix: str | None = None
    metadata: ResourceMetadata = Field(default_factory=ResourceMetadata)

    @model_validator(mode="after")
    def normalize_storage_and_lifecycle(self) -> TenantDefinition:
        expected_prefix = f"tenants/{self.slug}/"
        if self.storage_prefix is None:
            object.__setattr__(self, "storage_prefix", expected_prefix)
        elif self.storage_prefix != expected_prefix:
            raise ValueError("tenant storage prefix must be derived from its canonical slug")
        if self.status is TenantStatus.TOMBSTONED:
            if self.metadata.lifecycle is not ResourceLifecycle.TOMBSTONED:
                raise ValueError("tombstoned tenant requires tombstoned resource metadata")
        elif self.metadata.lifecycle is ResourceLifecycle.TOMBSTONED:
            raise ValueError("active or suspended tenant cannot have tombstoned metadata")
        return self


class TenantExport(BaseModel):
    model_config = ConfigDict(frozen=True)

    export_id: UUID = Field(default_factory=new_runtime_id)
    tenant: TenantDefinition
    resource_counts: dict[str, int]
    exported_by: str = Field(min_length=1)
    exported_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_export(self) -> TenantExport:
        if self.exported_at.tzinfo is None:
            raise ValueError("tenant export timestamp must be timezone-aware")
        if any(value < 0 for value in self.resource_counts.values()):
            raise ValueError("tenant export counts cannot be negative")
        return self


def tenant_storage_key(tenant: TenantDefinition, key: str) -> str:
    normalized = key.lstrip("/")
    if not normalized or ".." in normalized.split("/"):
        raise ValueError("tenant object key must be a non-empty relative path")
    assert tenant.storage_prefix is not None
    return f"{tenant.storage_prefix}{normalized}"
