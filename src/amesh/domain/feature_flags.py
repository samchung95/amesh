from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import NamespaceId, NaturalId, TenantSlug, new_runtime_id


class FeatureFlagScope(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"


class FeatureFlag(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=new_runtime_id)
    key: NaturalId
    scope: FeatureFlagScope
    enabled: bool
    tenant_id: TenantSlug | None = None
    namespace: NamespaceId | None = None
    description: str = Field(default="", max_length=4096)
    version: int = Field(default=1, ge=1)
    updated_by: str = Field(min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_scope(self) -> FeatureFlag:
        if self.scope is FeatureFlagScope.INSTANCE:
            if self.tenant_id is not None or self.namespace is not None:
                raise ValueError("instance feature flag cannot declare tenant or namespace")
        elif self.scope is FeatureFlagScope.TENANT:
            if self.tenant_id is None or self.namespace is not None:
                raise ValueError("tenant feature flag requires only tenant_id")
        elif self.tenant_id is None or self.namespace is None:
            raise ValueError("namespace feature flag requires tenant_id and namespace")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("feature flag timestamps must be timezone-aware")
        return self


class FeatureFlagDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: NaturalId
    enabled: bool
    reason: str
    matched_scope: FeatureFlagScope | None = None
    matched_version: int | None = Field(default=None, ge=1)


def resolve_feature_flag(
    key: str,
    flags: tuple[FeatureFlag, ...],
    *,
    default: bool,
) -> FeatureFlagDecision:
    precedence = {
        FeatureFlagScope.INSTANCE: 1,
        FeatureFlagScope.TENANT: 2,
        FeatureFlagScope.NAMESPACE: 3,
    }
    matching = [flag for flag in flags if flag.key == key]
    if not matching:
        return FeatureFlagDecision(key=key, enabled=default, reason="DEFAULT")
    selected = max(matching, key=lambda flag: precedence[flag.scope])
    return FeatureFlagDecision(
        key=key,
        enabled=selected.enabled,
        reason=f"{selected.scope.value}_MATCH",
        matched_scope=selected.scope,
        matched_version=selected.version,
    )
