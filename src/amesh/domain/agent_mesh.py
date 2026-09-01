from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .agent_resources import AgentHardLimits
from .identity import NaturalId
from .resources import canonical_hash


class AgentMeshTopology(StrEnum):
    SUPERVISOR = "SUPERVISOR"
    ROUTER = "ROUTER"
    PEER_TO_PEER = "PEER_TO_PEER"
    HIERARCHICAL = "HIERARCHICAL"
    SWARM = "SWARM"


class AgentMeshMemberRole(StrEnum):
    SUPERVISOR = "SUPERVISOR"
    ROUTER = "ROUTER"
    WORKER = "WORKER"
    PEER = "PEER"


class AgentMeshSessionBudget(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_total_tokens: int = Field(alias="maxTotalTokens", ge=1)
    max_cost_usd: Decimal = Field(alias="maxCostUsd", ge=0)
    max_duration_seconds: int = Field(alias="maxDurationSeconds", ge=1, le=86_400)
    max_tool_calls: int = Field(alias="maxToolCalls", ge=0, le=10_000)


class AgentMeshBudget(AgentMeshSessionBudget):
    max_sessions: int = Field(alias="maxSessions", ge=1, le=1_000)
    max_concurrency: int = Field(alias="maxConcurrency", ge=1, le=1_000)


class AgentMeshMember(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    member_id: NaturalId = Field(alias="memberId")
    task: NaturalId
    agent: NaturalId
    agent_revision: int = Field(alias="agentRevision", ge=1)
    role: AgentMeshMemberRole
    capabilities: tuple[NaturalId, ...] = ()
    parent_member_id: NaturalId | None = Field(default=None, alias="parentMemberId")

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("mesh member capabilities must be unique")
        return value


class AgentMeshDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    topology: AgentMeshTopology
    members: tuple[AgentMeshMember, ...] = Field(min_length=1, max_length=1_000)
    budget: AgentMeshBudget

    @model_validator(mode="after")
    def validate_topology(self) -> AgentMeshDefinition:
        member_ids = tuple(member.member_id for member in self.members)
        tasks = tuple(member.task for member in self.members)
        if len(set(member_ids)) != len(member_ids):
            raise ValueError("mesh memberId values must be unique")
        if len(set(tasks)) != len(tasks):
            raise ValueError("mesh members must reference unique session tasks")
        if len(self.members) > self.budget.max_sessions:
            raise ValueError("mesh member count exceeds budget.maxSessions")
        by_id = {member.member_id: member for member in self.members}
        for member in self.members:
            if member.parent_member_id is not None and member.parent_member_id not in by_id:
                raise ValueError(
                    f"mesh member {member.member_id!r} references an unknown parentMemberId"
                )
            seen = {member.member_id}
            current = member
            while current.parent_member_id is not None:
                if current.parent_member_id in seen:
                    raise ValueError("mesh parentMemberId graph must be acyclic")
                seen.add(current.parent_member_id)
                current = by_id[current.parent_member_id]

        roles = tuple(member.role for member in self.members)
        roots = tuple(member for member in self.members if member.parent_member_id is None)
        if self.topology is AgentMeshTopology.SUPERVISOR:
            if roles.count(AgentMeshMemberRole.SUPERVISOR) != 1 or len(self.members) < 2:
                raise ValueError(
                    "SUPERVISOR topology requires one supervisor and at least one worker"
                )
        elif self.topology is AgentMeshTopology.ROUTER:
            if roles.count(AgentMeshMemberRole.ROUTER) != 1 or len(self.members) < 2:
                raise ValueError("ROUTER topology requires one router and at least one candidate")
        elif self.topology is AgentMeshTopology.PEER_TO_PEER:
            if len(self.members) < 2 or set(roles) != {AgentMeshMemberRole.PEER}:
                raise ValueError("PEER_TO_PEER topology requires at least two peer members")
        elif self.topology is AgentMeshTopology.HIERARCHICAL:
            if len(self.members) < 2 or len(roots) != 1:
                raise ValueError("HIERARCHICAL topology requires one root and at least one child")
        elif self.topology is AgentMeshTopology.SWARM and (
            len(self.members) < 2 or set(roles) != {AgentMeshMemberRole.PEER}
        ):
            raise ValueError("SWARM topology requires at least two peer members")
        return self


class AgentRoutePolicySignal(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    outcome: Literal["ALLOW", "DENY"]
    decision_id: str = Field(alias="decisionId", min_length=1, max_length=256)
    policy_digest: str = Field(
        alias="policyDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )


class AgentRouteAvailabilitySignal(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    available: bool
    source: str = Field(min_length=1, max_length=256)
    checked_at: datetime = Field(alias="checkedAt")


class AgentRouteEvaluationSignal(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: NaturalId
    revision: int = Field(ge=1)
    score: Decimal = Field(ge=0, le=1)


class AgentRouteCandidate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    member_id: NaturalId = Field(alias="memberId")
    task: NaturalId
    agent: NaturalId
    agent_revision: int = Field(alias="agentRevision", ge=1)
    capabilities: tuple[NaturalId, ...]
    policy: AgentRoutePolicySignal
    projected_cost_usd: Decimal = Field(alias="projectedCostUsd", ge=0)
    projected_latency_ms: int = Field(alias="projectedLatencyMs", ge=0)
    availability: AgentRouteAvailabilitySignal
    evaluation: AgentRouteEvaluationSignal

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("route candidate capabilities must be unique")
        return value


class AgentRouteRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    required_capabilities: tuple[NaturalId, ...] = Field(
        alias="requiredCapabilities",
        min_length=1,
    )
    candidates: tuple[AgentRouteCandidate, ...] = Field(min_length=1, max_length=1_000)

    @model_validator(mode="after")
    def validate_unique_candidates(self) -> AgentRouteRequest:
        if len(set(self.required_capabilities)) != len(self.required_capabilities):
            raise ValueError("requiredCapabilities must be unique")
        ids = tuple(candidate.member_id for candidate in self.candidates)
        if len(set(ids)) != len(ids):
            raise ValueError("route candidate memberId values must be unique")
        return self


class AgentRouteAssessment(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    member_id: NaturalId = Field(alias="memberId")
    eligible: bool
    reasons: tuple[str, ...]
    evaluation_score: Decimal = Field(alias="evaluationScore")
    projected_cost_usd: Decimal = Field(alias="projectedCostUsd")
    projected_latency_ms: int = Field(alias="projectedLatencyMs")
    policy_outcome: str = Field(alias="policyOutcome")
    available: bool


class AgentRouteDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.agent-route/v1"] = Field(
        default="amesh.agent-route/v1",
        alias="schemaVersion",
    )
    selected_member_id: NaturalId = Field(alias="selectedMemberId")
    selected_task: NaturalId = Field(alias="selectedTask")
    selected_agent: NaturalId = Field(alias="selectedAgent")
    selected_agent_revision: int = Field(alias="selectedAgentRevision")
    ranked_member_ids: tuple[NaturalId, ...] = Field(alias="rankedMemberIds")
    required_capabilities: tuple[NaturalId, ...] = Field(alias="requiredCapabilities")
    assessments: tuple[AgentRouteAssessment, ...]
    factor_order: tuple[str, ...] = Field(alias="factorOrder")
    explanation: str
    decision_digest: str = Field(alias="decisionDigest", pattern=r"^sha256:[0-9a-f]{64}$")


def route_agent(request: AgentRouteRequest) -> AgentRouteDecision:
    required = set(request.required_capabilities)
    assessments: list[AgentRouteAssessment] = []
    eligible: list[AgentRouteCandidate] = []
    for candidate in request.candidates:
        reasons: list[str] = []
        missing = sorted(required - set(candidate.capabilities))
        if missing:
            reasons.append("missing capabilities: " + ", ".join(missing))
        if candidate.policy.outcome != "ALLOW":
            reasons.append("policy denied")
        if not candidate.availability.available:
            reasons.append("unavailable")
        if not reasons:
            eligible.append(candidate)
        assessments.append(
            AgentRouteAssessment(
                memberId=candidate.member_id,
                eligible=not reasons,
                reasons=tuple(reasons) or ("eligible",),
                evaluationScore=candidate.evaluation.score,
                projectedCostUsd=candidate.projected_cost_usd,
                projectedLatencyMs=candidate.projected_latency_ms,
                policyOutcome=candidate.policy.outcome,
                available=candidate.availability.available,
            )
        )
    if not eligible:
        detail = "; ".join(
            f"{assessment.member_id}: {', '.join(assessment.reasons)}" for assessment in assessments
        )
        raise ValueError(f"no eligible agent route candidate ({detail})")
    ranked = sorted(
        eligible,
        key=lambda candidate: (
            -candidate.evaluation.score,
            candidate.projected_cost_usd,
            candidate.projected_latency_ms,
            candidate.member_id,
        ),
    )
    selected = ranked[0]
    factor_order = (
        "required capability coverage",
        "policy allow",
        "availability",
        "evaluation score descending",
        "projected cost ascending",
        "projected latency ascending",
        "stable member id",
    )
    evidence = {
        "request": request.model_dump(mode="json", by_alias=True),
        "assessments": [item.model_dump(mode="json", by_alias=True) for item in assessments],
        "rankedMemberIds": [item.member_id for item in ranked],
        "selectedMemberId": selected.member_id,
        "factorOrder": list(factor_order),
    }
    return AgentRouteDecision(
        selectedMemberId=selected.member_id,
        selectedTask=selected.task,
        selectedAgent=selected.agent,
        selectedAgentRevision=selected.agent_revision,
        rankedMemberIds=tuple(item.member_id for item in ranked),
        requiredCapabilities=request.required_capabilities,
        assessments=tuple(assessments),
        factorOrder=factor_order,
        explanation=(
            f"Selected {selected.member_id!r} after capability, policy and availability gates; "
            "eligible candidates were ranked by evaluation score, projected cost, latency and "
            "stable member id."
        ),
        decisionDigest="sha256:" + canonical_hash(evidence),
    )


class AgentHandoffEndpoint(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    task: NaturalId
    agent: NaturalId
    agent_revision: int = Field(alias="agentRevision", ge=1)


class AgentHandoffRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source: AgentHandoffEndpoint
    destination: AgentHandoffEndpoint
    payload: dict[str, Any]
    schema_: dict[str, Any] = Field(alias="schema")
    rationale: str = Field(min_length=1, max_length=4096)
    context_keys: tuple[str, ...] = Field(default=(), alias="contextKeys", max_length=100)
    redact_keys: tuple[str, ...] = Field(default=(), alias="redactKeys", max_length=100)
    required_capabilities: tuple[NaturalId, ...] = Field(
        default=(),
        alias="requiredCapabilities",
    )
    policy: AgentRoutePolicySignal

    @field_validator("schema_")
    @classmethod
    def validate_schema(cls, value: dict[str, Any]) -> dict[str, Any]:
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise ValueError(f"invalid hand-off schema: {exc.message}") from exc
        return value

    @field_validator("context_keys", "redact_keys", "required_capabilities")
    @classmethod
    def validate_unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("hand-off selection values must be unique")
        return value


class AgentHandoffRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.agent-handoff/v1"] = Field(
        default="amesh.agent-handoff/v1",
        alias="schemaVersion",
    )
    source: AgentHandoffEndpoint
    destination: AgentHandoffEndpoint
    context: dict[str, Any]
    rationale: str
    required_capabilities: tuple[NaturalId, ...] = Field(alias="requiredCapabilities")
    policy: AgentRoutePolicySignal
    schema_digest: str = Field(alias="schemaDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    context_digest: str = Field(alias="contextDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    redacted_keys: tuple[str, ...] = Field(alias="redactedKeys")
    secret_values_redacted: bool = Field(alias="secretValuesRedacted")
    handoff_digest: str = Field(alias="handoffDigest", pattern=r"^sha256:[0-9a-f]{64}$")


def build_agent_handoff(
    request: AgentHandoffRequest,
    *,
    source_session: dict[str, Any],
    destination_capabilities: tuple[str, ...],
    secrets: tuple[str, ...] = (),
) -> AgentHandoffRecord:
    if request.policy.outcome != "ALLOW":
        raise PermissionError("agent hand-off policy denied the transfer")
    if (
        source_session.get("agentKey") != request.source.agent
        or source_session.get("agentRevision") != request.source.agent_revision
    ):
        raise PermissionError("agent hand-off source does not match the completed source session")
    missing_capabilities = sorted(
        set(request.required_capabilities) - set(destination_capabilities)
    )
    if missing_capabilities:
        raise PermissionError(
            "agent hand-off requests undelegated destination capabilities: "
            + ", ".join(missing_capabilities)
        )
    errors = sorted(
        Draft202012Validator(request.schema_).iter_errors(request.payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise ValueError(f"agent hand-off schema failed: {errors[0].message}")
    selected_keys = request.context_keys or tuple(request.payload)
    unknown_keys = sorted(set(selected_keys) - set(request.payload))
    if unknown_keys:
        raise ValueError("agent hand-off contextKeys are unavailable: " + ", ".join(unknown_keys))
    selected = {key: request.payload[key] for key in selected_keys}
    explicitly_redacted = sorted(set(request.redact_keys) & set(selected))
    for key in explicitly_redacted:
        selected[key] = "[REDACTED]"
    safe_context, secret_redacted = _redact_secret_values(selected, secrets)
    schema_digest = "sha256:" + canonical_hash(request.schema_)
    context_digest = "sha256:" + canonical_hash(safe_context)
    evidence = {
        "source": request.source.model_dump(mode="json", by_alias=True),
        "destination": request.destination.model_dump(mode="json", by_alias=True),
        "contextDigest": context_digest,
        "schemaDigest": schema_digest,
        "rationale": request.rationale,
        "requiredCapabilities": list(request.required_capabilities),
        "policy": request.policy.model_dump(mode="json", by_alias=True),
        "redactedKeys": explicitly_redacted,
        "secretValuesRedacted": secret_redacted,
    }
    return AgentHandoffRecord(
        source=request.source,
        destination=request.destination,
        context=safe_context,
        rationale=request.rationale,
        requiredCapabilities=request.required_capabilities,
        policy=request.policy,
        schemaDigest=schema_digest,
        contextDigest=context_digest,
        redactedKeys=tuple(explicitly_redacted),
        secretValuesRedacted=secret_redacted,
        handoffDigest="sha256:" + canonical_hash(evidence),
    )


def effective_agent_limits(
    limits: AgentHardLimits,
    budget: AgentMeshSessionBudget | None,
) -> AgentHardLimits:
    if budget is None:
        return limits
    return limits.model_copy(
        update={
            "max_total_tokens": (
                budget.max_total_tokens
                if limits.max_total_tokens is None
                else min(limits.max_total_tokens, budget.max_total_tokens)
            ),
            "max_cost_usd": (
                budget.max_cost_usd
                if limits.max_cost_usd is None
                else min(limits.max_cost_usd, budget.max_cost_usd)
            ),
            "max_duration_seconds": (
                budget.max_duration_seconds
                if limits.max_duration_seconds is None
                else min(limits.max_duration_seconds, budget.max_duration_seconds)
            ),
            "max_tool_calls": (
                budget.max_tool_calls
                if limits.max_tool_calls is None
                else min(limits.max_tool_calls, budget.max_tool_calls)
            ),
        }
    )


def _redact_secret_values(value: Any, secrets: tuple[str, ...]) -> tuple[Any, bool]:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[REDACTED]")
        return redacted, redacted != value
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        changed = False
        for key, item in value.items():
            output[key], item_changed = _redact_secret_values(item, secrets)
            changed = changed or item_changed
        return output, changed
    if isinstance(value, list):
        output_list: list[Any] = []
        changed = False
        for item in value:
            safe, item_changed = _redact_secret_values(item, secrets)
            output_list.append(safe)
            changed = changed or item_changed
        return output_list, changed
    return value, False
