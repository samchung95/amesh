from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .identity import NamespaceId, NaturalId, TenantSlug, new_runtime_id
from .resources import canonical_hash

_MAX_POLICY_IDENTIFIERS = 100


class AgentSessionPolicy(BaseModel):
    """Versioned admission and dependency limits for agent sessions."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    admission_enabled: bool = Field(default=True, alias="admissionEnabled")
    max_concurrency: int = Field(alias="maxConcurrency", ge=1, le=1_000)
    max_total_tokens: int = Field(alias="maxTotalTokens", ge=1, le=10_000_000)
    max_cost_usd: Decimal = Field(alias="maxCostUsd", ge=0)
    max_duration_seconds: int = Field(alias="maxDurationSeconds", ge=1, le=86_400)
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
    max_concurrency: int = Field(alias="maxConcurrency", ge=1)
    retention_seconds: int = Field(alias="retentionSeconds", ge=0)

    @property
    def provenance(self) -> dict[str, object]:
        return {
            "policies": [
                {
                    "policyId": str(revision.policy_id),
                    "revision": revision.revision,
                    "digest": revision.digest,
                    "namespace": revision.namespace,
                    "applicationId": revision.application_id,
                }
                for revision in self.revisions
            ],
            "retentionSeconds": self.retention_seconds,
        }


def evaluate_agent_session_policies(
    revisions: Iterable[AgentSessionPolicyRevision],
    *,
    envelope_max_total_tokens: int,
    envelope_max_cost_usd: Decimal,
    envelope_max_duration_seconds: int,
    envelope_max_concurrency: int,
    requested_timeout_seconds: float | None,
    provider_ids: Iterable[str],
    harness_id: str,
    tool_ids: Iterable[str],
) -> AgentSessionPolicyEvaluation:
    """Validate cumulative session policy constraints before execution creation."""

    applied = tuple(revisions)
    if not applied:
        return AgentSessionPolicyEvaluation(
            revisions=(),
            maxConcurrency=envelope_max_concurrency,
            retentionSeconds=0,
        )
    if any(not revision.spec.admission_enabled for revision in applied):
        raise ValueError("agent session admission is disabled by policy")
    max_tokens = min(revision.spec.max_total_tokens for revision in applied)
    max_cost = min(revision.spec.max_cost_usd for revision in applied)
    max_duration = min(revision.spec.max_duration_seconds for revision in applied)
    max_concurrency = min(
        envelope_max_concurrency,
        *(revision.spec.max_concurrency for revision in applied),
    )
    if envelope_max_total_tokens > max_tokens:
        raise ValueError("agent envelope exceeds the effective session token limit")
    if envelope_max_cost_usd > max_cost:
        raise ValueError("agent envelope exceeds the effective session cost limit")
    if envelope_max_duration_seconds > max_duration:
        raise ValueError("agent envelope exceeds the effective session duration limit")
    if requested_timeout_seconds is not None and requested_timeout_seconds > max_duration:
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
