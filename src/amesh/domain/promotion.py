"""Provider-neutral, evidence-backed release promotion contracts.

The release aggregate deliberately contains no workflow or agent semantics.  A client supplies
the exact target digest and the evidence requirements; AMESH only verifies freshness, identity and
the configured gate result before recording a state transition.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

_DIGEST = r"^sha256:[0-9a-f]{64}$"


class PromotionTargetKind(StrEnum):
    WORKFLOW = "WORKFLOW"
    AGENT = "AGENT"


class PromotionEvidenceKind(StrEnum):
    TEST = "TEST"
    ASSERTION = "ASSERTION"
    DIFFERENTIAL = "DIFFERENTIAL"
    HEALTH = "HEALTH"
    BUDGET = "BUDGET"
    APPROVAL = "APPROVAL"


class ReleaseAction(StrEnum):
    PROMOTE = "PROMOTE"
    ROLLBACK = "ROLLBACK"
    KILL_SWITCH = "KILL_SWITCH"


class ReleaseState(StrEnum):
    ACTIVE = "ACTIVE"
    KILLED = "KILLED"


class PromotionError(RuntimeError):
    """Base error for a rejected release action."""


class PromotionEvidenceError(PromotionError):
    """Raised when evidence is absent, stale, failed or bound to another revision."""


class PromotionConcurrencyError(PromotionError):
    """Raised when a release action uses an old aggregate version."""


class EvidenceRequirement(BaseModel):
    """A policy pin for one immutable evidence artifact."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    kind: PromotionEvidenceKind
    key: str = Field(min_length=1, max_length=512)
    digest: str = Field(pattern=_DIGEST)


class EvidenceArtifact(BaseModel):
    """Evidence captured for a specific target configuration and immutable forever."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    evidence_id: UUID = Field(default_factory=uuid4, alias="evidenceId")
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    kind: PromotionEvidenceKind
    key: str = Field(min_length=1, max_length=512)
    digest: str = Field(pattern=_DIGEST)
    configuration_digest: str = Field(alias="configurationDigest", pattern=_DIGEST)
    passed: bool
    captured_at: datetime = Field(alias="capturedAt")
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    details: Mapping[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_expiry(self) -> EvidenceArtifact:
        if self.expires_at is not None and self.expires_at <= self.captured_at:
            raise ValueError("evidence expiry must be later than capture time")
        return self

    def is_fresh(self, now: datetime) -> bool:
        moment = now if now.tzinfo is not None else now.replace(tzinfo=UTC)
        captured = (
            self.captured_at
            if self.captured_at.tzinfo is not None
            else self.captured_at.replace(tzinfo=UTC)
        )
        expires = (
            None
            if self.expires_at is None
            else self.expires_at
            if self.expires_at.tzinfo is not None
            else self.expires_at.replace(tzinfo=UTC)
        )
        return expires is None or (moment < expires and moment >= captured)


class HealthRequirement(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=512)
    minimum: Decimal | None = None
    maximum: Decimal | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> HealthRequirement:
        if self.minimum is None and self.maximum is None:
            raise ValueError("health requirement must define a minimum or maximum")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("health minimum cannot exceed maximum")
        return self


class BudgetRequirement(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=512)
    maximum: Decimal = Field(gt=0)


class ApprovalRequirement(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=512)
    minimum_approvals: int = Field(default=1, alias="minimumApprovals", ge=1, le=100)


class PromotionPolicy(BaseModel):
    """Immutable tenant policy; thresholds and cutover choices remain client supplied."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    policy_id: UUID = Field(default_factory=uuid4, alias="policyId")
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    target_kind: PromotionTargetKind = Field(alias="targetKind")
    target_key: str = Field(alias="targetKey", min_length=1, max_length=512)
    target_revision: int = Field(alias="targetRevision", ge=1)
    configuration_digest: str = Field(alias="configurationDigest", pattern=_DIGEST)
    required_evidence: tuple[EvidenceRequirement, ...] = Field(
        default=(), alias="requiredEvidence", max_length=1000
    )
    health_requirements: tuple[HealthRequirement, ...] = Field(
        default=(), alias="healthRequirements", max_length=100
    )
    budget_requirements: tuple[BudgetRequirement, ...] = Field(
        default=(), alias="budgetRequirements", max_length=100
    )
    approval_requirements: tuple[ApprovalRequirement, ...] = Field(
        default=(), alias="approvalRequirements", max_length=100
    )
    max_evidence_age_seconds: int = Field(
        default=86_400, alias="maxEvidenceAgeSeconds", ge=1, le=31_536_000
    )
    created_by: str = Field(alias="createdBy", min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")

    @model_validator(mode="after")
    def validate_unique_requirements(self) -> PromotionPolicy:
        pins = [(item.kind, item.key) for item in self.required_evidence]
        if len(pins) != len(set(pins)):
            raise ValueError("required evidence keys must be unique within a policy")
        health = [item.key for item in self.health_requirements]
        if len(health) != len(set(health)):
            raise ValueError("health requirement keys must be unique")
        budgets = [item.key for item in self.budget_requirements]
        if len(budgets) != len(set(budgets)):
            raise ValueError("budget requirement keys must be unique")
        approvals = [item.key for item in self.approval_requirements]
        if len(approvals) != len(set(approvals)):
            raise ValueError("approval requirement keys must be unique")
        return self

    @property
    def digest(self) -> str:
        payload = self.model_dump(
            mode="json", by_alias=True, exclude={"policyId", "createdAt", "createdBy"}
        )
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


class PromotionGate(BaseModel):
    """The immutable result of evaluating a policy against evidence."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    gate_id: UUID = Field(default_factory=uuid4, alias="gateId")
    tenant_id: str = Field(alias="tenantId")
    policy_id: UUID = Field(alias="policyId")
    policy_digest: str = Field(alias="policyDigest", pattern=_DIGEST)
    target_kind: PromotionTargetKind = Field(alias="targetKind")
    target_key: str = Field(alias="targetKey")
    target_revision: int = Field(alias="targetRevision", ge=1)
    configuration_digest: str = Field(alias="configurationDigest", pattern=_DIGEST)
    evidence_digests: tuple[str, ...] = Field(alias="evidenceDigests")
    passed: bool
    failures: tuple[str, ...] = ()
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="evaluatedAt")

    @property
    def digest(self) -> str:
        encoded = json.dumps(
            self.model_dump(mode="json", by_alias=True), sort_keys=True, separators=(",", ":")
        ).encode()
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


class ReleaseTarget(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    tenant_id: str = Field(alias="tenantId")
    target_kind: PromotionTargetKind = Field(alias="targetKind")
    target_key: str = Field(alias="targetKey")
    active_revision: int | None = Field(default=None, alias="activeRevision")
    active_configuration_digest: str | None = Field(default=None, alias="activeConfigurationDigest")
    state: ReleaseState = ReleaseState.KILLED
    version: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="updatedAt")


class ReleaseHistoryEntry(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    event_id: UUID = Field(default_factory=uuid4, alias="eventId")
    tenant_id: str = Field(alias="tenantId")
    target_kind: PromotionTargetKind = Field(alias="targetKind")
    target_key: str = Field(alias="targetKey")
    action: ReleaseAction
    from_revision: int | None = Field(default=None, alias="fromRevision")
    to_revision: int | None = Field(default=None, alias="toRevision")
    to_configuration_digest: str | None = Field(default=None, alias="toConfigurationDigest")
    gate_digest: str | None = Field(default=None, alias="gateDigest")
    actor_id: str = Field(alias="actorId")
    reason: str = Field(min_length=1, max_length=2048)
    version: int = Field(ge=1)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="occurredAt")


def evaluate_promotion_gate(
    policy: PromotionPolicy,
    evidence: tuple[EvidenceArtifact, ...] | list[EvidenceArtifact],
    *,
    now: datetime | None = None,
    approvals: Mapping[str, int] | None = None,
) -> PromotionGate:
    """Evaluate exact tenant/configuration-bound evidence without side effects."""

    evaluated_at = now or datetime.now(UTC)
    failures: list[str] = []
    by_pin = {(item.kind, item.key): item for item in evidence}
    evidence_digests: list[str] = []
    for evidence_requirement in policy.required_evidence:
        artifact = by_pin.get((evidence_requirement.kind, evidence_requirement.key))
        if artifact is None:
            failures.append(f"missing {evidence_requirement.kind.value}:{evidence_requirement.key}")
            continue
        evidence_digests.append(artifact.digest)
        if artifact.tenant_id != policy.tenant_id:
            failures.append(f"tenant mismatch for {evidence_requirement.key}")
        if artifact.configuration_digest != policy.configuration_digest:
            failures.append(f"configuration digest mismatch for {evidence_requirement.key}")
        if artifact.digest != evidence_requirement.digest:
            failures.append(f"evidence digest mismatch for {evidence_requirement.key}")
        if not artifact.passed:
            failures.append(f"evidence failed for {evidence_requirement.key}")
        captured = (
            artifact.captured_at
            if artifact.captured_at.tzinfo is not None
            else artifact.captured_at.replace(tzinfo=UTC)
        )
        if evaluated_at - captured > timedelta(seconds=policy.max_evidence_age_seconds):
            failures.append(f"stale evidence for {evidence_requirement.key}")
        if not artifact.is_fresh(evaluated_at):
            failures.append(f"expired evidence for {evidence_requirement.key}")
    values = {
        item.key: item
        for item in evidence
        if item.configuration_digest == policy.configuration_digest
    }
    for health_requirement in policy.health_requirements:
        health_artifact = values.get(health_requirement.key)
        if health_artifact is None or not health_artifact.passed:
            failures.append(f"health requirement failed for {health_requirement.key}")
    for budget_requirement in policy.budget_requirements:
        budget_artifact = values.get(budget_requirement.key)
        actual = budget_artifact.details.get("value") if budget_artifact else None
        if (
            not isinstance(actual, (int, float, Decimal))
            or Decimal(str(actual)) > budget_requirement.maximum
        ):
            failures.append(f"budget exceeded for {budget_requirement.key}")
    supplied = approvals or {}
    for approval_requirement in policy.approval_requirements:
        if supplied.get(approval_requirement.key, 0) < approval_requirement.minimum_approvals:
            failures.append(f"approval requirement failed for {approval_requirement.key}")
    return PromotionGate(
        tenantId=policy.tenant_id,
        policyId=policy.policy_id,
        policyDigest=policy.digest,
        targetKind=policy.target_kind,
        targetKey=policy.target_key,
        targetRevision=policy.target_revision,
        configurationDigest=policy.configuration_digest,
        evidenceDigests=tuple(evidence_digests),
        passed=not failures,
        failures=tuple(dict.fromkeys(failures)),
        evaluatedAt=evaluated_at,
    )


__all__ = [
    "ApprovalRequirement",
    "BudgetRequirement",
    "EvidenceArtifact",
    "EvidenceRequirement",
    "HealthRequirement",
    "PromotionConcurrencyError",
    "PromotionError",
    "PromotionEvidenceError",
    "PromotionEvidenceKind",
    "PromotionGate",
    "PromotionPolicy",
    "PromotionTargetKind",
    "ReleaseAction",
    "ReleaseHistoryEntry",
    "ReleaseState",
    "ReleaseTarget",
    "evaluate_promotion_gate",
]
