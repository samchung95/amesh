from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from fnmatch import fnmatchcase
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from semantic_version import SimpleSpec, Version  # type: ignore[import-untyped]

from .identity import new_runtime_id


class PluginPolicyScope(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"


class PluginPolicyStage(StrEnum):
    AUTHORING = "AUTHORING"
    VALIDATION = "VALIDATION"
    EXECUTION = "EXECUTION"
    ADMINISTRATION = "ADMINISTRATION"


class PluginPolicyEffect(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class PluginQuarantineState(StrEnum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class PluginPolicySelector(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    package: str = Field(default="*", min_length=1, max_length=255)
    version_range: str = Field(default="*", alias="versionRange", min_length=1, max_length=128)
    vendor: str = Field(default="*", min_length=1, max_length=255)
    plugin_types: tuple[str, ...] = Field(default=(), alias="pluginTypes")
    capabilities: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_selector(self) -> PluginPolicySelector:
        try:
            SimpleSpec(self.version_range)
        except ValueError as exc:
            raise ValueError("versionRange must be a semantic-version range") from exc
        for values, label in (
            (self.plugin_types, "pluginTypes"),
            (self.capabilities, "capabilities"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")
            if any(not value or value.strip() != value for value in values):
                raise ValueError(f"{label} values must be non-empty and trimmed")
        return self

    def matches(self, subject: PluginPolicySubject) -> bool:
        try:
            version_matches = SimpleSpec(self.version_range).match(Version(subject.version))
        except ValueError:
            return False
        return (
            fnmatchcase(subject.package, self.package)
            and version_matches
            and fnmatchcase(subject.vendor, self.vendor)
            and (
                not self.plugin_types
                or bool(set(self.plugin_types).intersection(subject.plugin_types))
            )
            and set(self.capabilities).issubset(subject.capabilities)
        )


class PluginPolicyRuleCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    scope: PluginPolicyScope
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    effect: PluginPolicyEffect
    stages: tuple[PluginPolicyStage, ...] = Field(min_length=1)
    selector: PluginPolicySelector = Field(default_factory=PluginPolicySelector)
    priority: int = Field(default=0, ge=-10_000, le=10_000)
    reason: str = Field(min_length=1, max_length=2048)
    enabled: bool = True

    @model_validator(mode="after")
    def validate_scope(self) -> PluginPolicyRuleCreate:
        if self.scope is PluginPolicyScope.NAMESPACE and self.namespace is None:
            raise ValueError("namespace is required for NAMESPACE scope")
        if self.scope is not PluginPolicyScope.NAMESPACE and self.namespace is not None:
            raise ValueError("namespace is only valid for NAMESPACE scope")
        if len(self.stages) != len(set(self.stages)):
            raise ValueError("stages must be unique")
        return self


class PluginPolicyRule(PluginPolicyRuleCreate):
    rule_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")
    updated_by: str = Field(alias="updatedBy")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="updatedAt")


class PluginPolicySubject(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    package: str
    version: str
    vendor: str
    plugin_types: tuple[str, ...] = Field(default=(), alias="pluginTypes")
    capabilities: tuple[str, ...] = ()
    content_digest: str | None = Field(default=None, alias="contentDigest")


class PluginQuarantineCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    scope: PluginPolicyScope = PluginPolicyScope.INSTANCE
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    package: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=128)
    reason: str = Field(min_length=1, max_length=2048)

    @model_validator(mode="after")
    def validate_quarantine(self) -> PluginQuarantineCreate:
        try:
            Version(self.version)
        except ValueError as exc:
            raise ValueError("version must be an exact semantic version") from exc
        if self.scope is PluginPolicyScope.NAMESPACE and self.namespace is None:
            raise ValueError("namespace is required for NAMESPACE scope")
        if self.scope is not PluginPolicyScope.NAMESPACE and self.namespace is not None:
            raise ValueError("namespace is only valid for NAMESPACE scope")
        return self


class PluginQuarantine(PluginQuarantineCreate):
    quarantine_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    state: PluginQuarantineState = PluginQuarantineState.ACTIVE
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")
    released_by: str | None = Field(default=None, alias="releasedBy")
    released_at: datetime | None = Field(default=None, alias="releasedAt")


class PluginPolicyRuleSource(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: str
    source_id: str = Field(alias="sourceId")
    scope: PluginPolicyScope | None = None
    effect: PluginPolicyEffect
    reason: str


class PluginPolicySubjectDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    subject: PluginPolicySubject
    allowed: bool
    reason_code: str = Field(alias="reasonCode")
    sources: tuple[PluginPolicyRuleSource, ...]


class PluginPolicyDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    decision_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    stage: PluginPolicyStage
    allowed: bool
    flow_id: str | None = Field(default=None, alias="flowId")
    flow_revision: int | None = Field(default=None, alias="flowRevision")
    subjects: tuple[PluginPolicySubjectDecision, ...]
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="decidedAt")


class EffectivePluginPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")
    namespace: str | None = None
    default_effect: PluginPolicyEffect = Field(alias="defaultEffect")
    rules: tuple[PluginPolicyRule, ...]
    quarantines: tuple[PluginQuarantine, ...]


class PluginPolicyImpactPreview(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    package: str
    version: str
    affected_flows: tuple[dict[str, Any], ...] = Field(alias="affectedFlows")
    running_executions: tuple[dict[str, Any], ...] = Field(alias="runningExecutions")


def evaluate_plugin_policy(
    subjects: tuple[PluginPolicySubject, ...],
    rules: tuple[PluginPolicyRule, ...],
    quarantines: tuple[PluginQuarantine, ...],
    *,
    tenant_id: str,
    namespace: str,
    stage: PluginPolicyStage,
    default_allow: bool,
    flow_id: str | None = None,
    flow_revision: int | None = None,
) -> PluginPolicyDecision:
    subject_decisions: list[PluginPolicySubjectDecision] = []
    for subject in subjects:
        quarantine_sources = tuple(
            PluginPolicyRuleSource(
                kind="QUARANTINE",
                sourceId=str(item.quarantine_id),
                scope=item.scope,
                effect=PluginPolicyEffect.DENY,
                reason=item.reason,
            )
            for item in quarantines
            if item.state is PluginQuarantineState.ACTIVE
            and item.package == subject.package
            and item.version == subject.version
        )
        matching = tuple(
            rule
            for rule in rules
            if rule.enabled and stage in rule.stages and rule.selector.matches(subject)
        )
        deny_sources = tuple(
            _rule_source(rule) for rule in matching if rule.effect is PluginPolicyEffect.DENY
        )
        allow_sources = tuple(
            _rule_source(rule) for rule in matching if rule.effect is PluginPolicyEffect.ALLOW
        )
        if quarantine_sources:
            allowed = False
            reason_code = "PLUGIN_QUARANTINED"
            sources = quarantine_sources
        elif deny_sources:
            allowed = False
            reason_code = "EXPLICIT_DENY"
            sources = deny_sources
        elif allow_sources:
            allowed = True
            reason_code = "EXPLICIT_ALLOW"
            sources = allow_sources
        else:
            allowed = subject.package == "amesh.core" or default_allow
            reason_code = "BUILT_IN_CORE" if subject.package == "amesh.core" else "DEFAULT_POLICY"
            sources = (
                PluginPolicyRuleSource(
                    kind="BUILT_IN" if subject.package == "amesh.core" else "DEFAULT",
                    sourceId="amesh.core" if subject.package == "amesh.core" else "secure-default",
                    effect=(PluginPolicyEffect.ALLOW if allowed else PluginPolicyEffect.DENY),
                    reason=(
                        "embedded core plugin"
                        if subject.package == "amesh.core"
                        else "unmatched third-party plugins require an explicit allow rule"
                    ),
                ),
            )
        subject_decisions.append(
            PluginPolicySubjectDecision(
                subject=subject,
                allowed=allowed,
                reasonCode=reason_code,
                sources=sources,
            )
        )
    return PluginPolicyDecision(
        tenantId=tenant_id,
        namespace=namespace,
        stage=stage,
        allowed=all(item.allowed for item in subject_decisions),
        flowId=flow_id,
        flowRevision=flow_revision,
        subjects=tuple(subject_decisions),
    )


def _rule_source(rule: PluginPolicyRule) -> PluginPolicyRuleSource:
    return PluginPolicyRuleSource(
        kind="RULE",
        sourceId=str(rule.rule_id),
        scope=rule.scope,
        effect=rule.effect,
        reason=rule.reason,
    )
