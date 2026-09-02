from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .agent_resources import AgentCeilingMode
from .identity import NamespaceId, NaturalId, TenantSlug, new_runtime_id
from .resources import canonical_hash

_MAX_POLICY_IDENTIFIERS = 100


class AgentSessionPolicy(BaseModel):
    """Versioned admission and dependency limits for agent sessions."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    ceiling_mode: AgentCeilingMode = Field(
        default=AgentCeilingMode.BOUNDED,
        alias="ceilingMode",
        exclude_if=lambda value: value is AgentCeilingMode.BOUNDED,
    )
    admission_enabled: bool = Field(default=True, alias="admissionEnabled")
    max_concurrency: int = Field(alias="maxConcurrency", ge=1, le=1_000)
    max_total_tokens: int | None = Field(alias="maxTotalTokens", ge=1, le=10_000_000)
    max_cost_usd: Decimal | None = Field(alias="maxCostUsd", ge=0)
    max_duration_seconds: int | None = Field(alias="maxDurationSeconds", ge=1, le=86_400)
    retention_seconds: int = Field(alias="retentionSeconds", ge=0, le=31_536_000)
    allowed_provider_ids: tuple[NaturalId, ...] = Field(
        default=(),
        alias="allowedProviderIds",
        max_length=_MAX_POLICY_IDENTIFIERS,
    )
    allowed_harness_ids: tuple[NaturalId, ...] = Field(
        default=(),
        alias="allowedHarnessIds",
        max_length=_MAX_POLICY_IDENTIFIERS,
    )
    allowed_tool_ids: tuple[NaturalId, ...] = Field(
        default=(),
        alias="allowedToolIds",
        max_length=_MAX_POLICY_IDENTIFIERS,
    )

    @field_validator(
        "allowed_provider_ids",
        "allowed_harness_ids",
        "allowed_tool_ids",
    )
    @classmethod
    def validate_unique_identifiers(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("session policy dependency identifiers must be unique")
        return value

    @model_validator(mode="after")
    def validate_ceiling_mode(self) -> AgentSessionPolicy:
        if self.ceiling_mode is AgentCeilingMode.BOUNDED and any(
            value is None
            for value in (
                self.max_total_tokens,
                self.max_cost_usd,
                self.max_duration_seconds,
            )
        ):
            raise ValueError("bounded session policy requires finite application ceilings")
        return self

    @property
    def digest(self) -> str:
        return f"sha256:{canonical_hash(self)}"


AgentSessionPolicySpec = AgentSessionPolicy


class AgentSessionPolicyRevision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    policy_id: UUID = Field(default_factory=new_runtime_id, alias="policyId")
    tenant_id: TenantSlug = Field(alias="tenantId")
    namespace: NamespaceId | None = None
    application_id: NaturalId | None = Field(default=None, alias="applicationId")
    revision: int = Field(ge=1)
    spec: AgentSessionPolicy
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    created_by: str = Field(alias="createdBy", min_length=1, max_length=255)
    created_at: datetime = Field(alias="createdAt")

    @model_validator(mode="after")
    def validate_digest(self) -> AgentSessionPolicyRevision:
        if self.digest != self.spec.digest:
            raise ValueError("session policy revision digest does not match its policy")
        if self.application_id is not None and self.namespace is None:
            raise ValueError("application session policies require a namespace")
        return self

    @property
    def policy(self) -> AgentSessionPolicy:
        """Compatibility accessor for callers that name the revision payload policy."""

        return self.spec


class AgentSessionPolicyEvaluation(BaseModel):
    """Validated cumulative policy result used by the launch boundary."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    revisions: tuple[AgentSessionPolicyRevision, ...]
    envelope_ceiling_mode: AgentCeilingMode = Field(alias="envelopeCeilingMode")
    max_total_tokens: int | None = Field(alias="maxTotalTokens", ge=1)
    max_cost_usd: Decimal | None = Field(alias="maxCostUsd", ge=0)
    max_duration_seconds: int | None = Field(alias="maxDurationSeconds", ge=1)
    max_concurrency: int = Field(alias="maxConcurrency", ge=1)
    retention_seconds: int = Field(alias="retentionSeconds", ge=0)

    @property
    def provenance(self) -> dict[str, object]:
        return {
            "envelopeCeilingMode": self.envelope_ceiling_mode.value,
            "policies": [
                {
                    "policyId": str(revision.policy_id),
                    "revision": revision.revision,
                    "digest": revision.digest,
                    "namespace": revision.namespace,
                    "applicationId": revision.application_id,
                    "ceilingMode": revision.spec.ceiling_mode.value,
                }
                for revision in self.revisions
            ],
            "effectiveLimits": {
                "maxTotalTokens": self.max_total_tokens,
                "maxCostUsd": (str(self.max_cost_usd) if self.max_cost_usd is not None else None),
                "maxDurationSeconds": self.max_duration_seconds,
                "maxConcurrency": self.max_concurrency,
            },
            "retentionSeconds": self.retention_seconds,
        }


def evaluate_agent_session_policies(
    revisions: Iterable[AgentSessionPolicyRevision],
    *,
    envelope_ceiling_mode: AgentCeilingMode = AgentCeilingMode.BOUNDED,
    envelope_max_total_tokens: int | None,
    envelope_max_cost_usd: Decimal | None,
    envelope_max_duration_seconds: int | None,
    envelope_max_concurrency: int,
    requested_timeout_seconds: float | None,
    provider_ids: Iterable[str],
    harness_id: str,
    tool_ids: Iterable[str],
) -> AgentSessionPolicyEvaluation:
    """Validate cumulative session policy constraints before execution creation."""

    applied = tuple(revisions)
    if envelope_ceiling_mode is AgentCeilingMode.BOUNDED and any(
        value is None
        for value in (
            envelope_max_total_tokens,
            envelope_max_cost_usd,
            envelope_max_duration_seconds,
        )
    ):
        raise ValueError("bounded agent envelope requires finite application ceilings")
    if not applied:
        if (
            requested_timeout_seconds is not None
            and envelope_max_duration_seconds is not None
            and requested_timeout_seconds > envelope_max_duration_seconds
        ):
            raise ValueError(
                "requested session timeout exceeds the effective session duration limit"
            )
        return AgentSessionPolicyEvaluation(
            revisions=(),
            envelopeCeilingMode=envelope_ceiling_mode,
            maxTotalTokens=envelope_max_total_tokens,
            maxCostUsd=envelope_max_cost_usd,
            maxDurationSeconds=envelope_max_duration_seconds,
            maxConcurrency=envelope_max_concurrency,
            retentionSeconds=0,
        )
    if any(not revision.spec.admission_enabled for revision in applied):
        raise ValueError("agent session admission is disabled by policy")
    token_ceilings = tuple(
        value
        for value in (
            envelope_max_total_tokens,
            *(revision.spec.max_total_tokens for revision in applied),
        )
        if value is not None
    )
    cost_ceilings = tuple(
        value
        for value in (
            envelope_max_cost_usd,
            *(revision.spec.max_cost_usd for revision in applied),
        )
        if value is not None
    )
    duration_ceilings = tuple(
        value
        for value in (
            envelope_max_duration_seconds,
            *(revision.spec.max_duration_seconds for revision in applied),
        )
        if value is not None
    )
    max_tokens = min(token_ceilings, default=None)
    max_cost = min(cost_ceilings, default=None)
    max_duration = min(duration_ceilings, default=None)
    max_concurrency = min(
        envelope_max_concurrency,
        *(revision.spec.max_concurrency for revision in applied),
    )
    if envelope_ceiling_mode is AgentCeilingMode.BOUNDED:
        if envelope_max_total_tokens != max_tokens:
            raise ValueError("agent envelope exceeds the effective session token limit")
        if envelope_max_cost_usd != max_cost:
            raise ValueError("agent envelope exceeds the effective session cost limit")
        if envelope_max_duration_seconds != max_duration:
            raise ValueError("agent envelope exceeds the effective session duration limit")
    if (
        requested_timeout_seconds is not None
        and max_duration is not None
        and requested_timeout_seconds > max_duration
    ):
        raise ValueError("requested session timeout exceeds the effective session duration limit")

    provider_values = tuple(provider_ids)
    tool_values = tuple(tool_ids)
    for revision in applied:
        policy = revision.spec
        if policy.allowed_provider_ids and not all(
            _dependency_matches_allowlist(value, policy.allowed_provider_ids)
            for value in provider_values
        ):
            raise ValueError("agent session provider dependency is outside the policy allowlist")
        if policy.allowed_harness_ids and harness_id not in policy.allowed_harness_ids:
            raise ValueError("agent session harness dependency is outside the policy allowlist")
        if policy.allowed_tool_ids and not all(
            _dependency_matches_allowlist(value, policy.allowed_tool_ids) for value in tool_values
        ):
            raise ValueError("agent session tool dependency is outside the policy allowlist")
    return AgentSessionPolicyEvaluation(
        revisions=applied,
        envelopeCeilingMode=envelope_ceiling_mode,
        maxTotalTokens=max_tokens,
        maxCostUsd=max_cost,
        maxDurationSeconds=max_duration,
        maxConcurrency=max_concurrency,
        retentionSeconds=min(revision.spec.retention_seconds for revision in applied),
    )


def _dependency_matches_allowlist(value: str, allowed: Iterable[str]) -> bool:
    """Match canonical pinned IDs and their stable human-readable identifiers."""

    candidates = {value}
    if ":" in value:
        candidates.add(value.split(":", 1)[0])
        candidates.add(value.rsplit(":", 1)[-1])
    return bool(candidates.intersection(allowed))
