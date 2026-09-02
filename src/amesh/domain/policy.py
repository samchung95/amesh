from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from datetime import UTC, datetime
from enum import StrEnum
from fnmatch import fnmatchcase
from time import perf_counter
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .identity import new_runtime_id

POLICY_ENGINE_VERSION = "amesh.policy/v1"
_MISSING = object()
_MUTABLE_ROOTS = frozenset({"flow", "runner", "image", "network", "resource"})
_SENSITIVE_PATH_PARTS = frozenset(
    {"password", "secret", "token", "credential", "api_key", "apikey"}
)


class PolicyStage(StrEnum):
    VALIDATE = "VALIDATE"
    SAVE = "SAVE"
    PROMOTE = "PROMOTE"
    LAUNCH = "LAUNCH"
    DISPATCH = "DISPATCH"


class PolicyOutcome(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    WARN = "WARN"
    MUTATE_DEFAULT = "MUTATE_DEFAULT"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class PolicyCriticality(StrEnum):
    ADVISORY = "ADVISORY"
    ENFORCING = "ENFORCING"


class PolicyScope(StrEnum):
    INSTANCE = "INSTANCE"
    TENANT = "TENANT"
    NAMESPACE = "NAMESPACE"


class PolicyOperator(StrEnum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    IN = "IN"
    CONTAINS = "CONTAINS"
    EXISTS = "EXISTS"
    MATCHES = "MATCHES"
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"


class PolicyCondition(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    path: str = Field(pattern=r"^[a-z][A-Za-z0-9_.-]*$", max_length=512)
    operator: PolicyOperator
    value: object = None

    @model_validator(mode="after")
    def reject_sensitive_value_paths(self) -> PolicyCondition:
        if _is_sensitive_value_path(self.path):
            raise ValueError(
                "policy conditions cannot inspect secret values; match secret.scopes instead"
            )
        return self


class PolicyRule(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    rule_id: str = Field(alias="id", pattern=r"^[a-z][a-z0-9_.-]*$", max_length=128)
    stages: tuple[PolicyStage, ...] = Field(min_length=1, max_length=5)
    conditions: tuple[PolicyCondition, ...] = Field(default=(), max_length=20)
    outcome: PolicyOutcome
    reason: str = Field(min_length=1, max_length=2048)
    mutations: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_rule(self) -> PolicyRule:
        if len(self.stages) != len(set(self.stages)):
            raise ValueError("policy rule stages must be unique")
        if self.outcome is not PolicyOutcome.MUTATE_DEFAULT and self.mutations:
            raise ValueError("mutations are only valid for MUTATE_DEFAULT rules")
        if self.outcome is PolicyOutcome.MUTATE_DEFAULT and not self.mutations:
            raise ValueError("MUTATE_DEFAULT rules require at least one mutation")
        for path in self.mutations:
            root = path.split(".", 1)[0]
            if root not in _MUTABLE_ROOTS or "." not in path:
                raise ValueError(
                    "mutation paths must target flow, runner, image, network or resource fields"
                )
            if _is_sensitive_value_path(path):
                raise ValueError("policy mutations cannot set secret or credential values")
        return self


class PolicyDocument(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.policy/v1"] = Field(
        default="amesh.policy/v1",
        alias="schemaVersion",
    )
    policy_key: str = Field(
        alias="policyKey",
        pattern=r"^[a-z][a-z0-9_.-]*$",
        max_length=128,
    )
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4096)
    scope: PolicyScope = PolicyScope.TENANT
    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    criticality: PolicyCriticality = PolicyCriticality.ENFORCING
    evaluation_timeout_ms: int = Field(
        default=100,
        alias="evaluationTimeoutMs",
        ge=1,
        le=5_000,
    )
    enabled: bool = True
    rules: tuple[PolicyRule, ...] = Field(default=(), max_length=100)

    @model_validator(mode="after")
    def validate_scope(self) -> PolicyDocument:
        if self.scope is PolicyScope.NAMESPACE and self.namespace is None:
            raise ValueError("namespace is required for NAMESPACE policy scope")
        if self.scope is not PolicyScope.NAMESPACE and self.namespace is not None:
            raise ValueError("namespace is only valid for NAMESPACE policy scope")
        rule_ids = [rule.rule_id for rule in self.rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("policy rule ids must be unique")
        return self

    @property
    def digest(self) -> str:
        payload = self.model_dump(mode="json", by_alias=True)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


class PolicyRevision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    policy_id: UUID = Field(default_factory=new_runtime_id, alias="policyId")
    tenant_id: str | None = Field(default=None, alias="tenantId")
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    document: PolicyDocument
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="createdAt")


class PolicyActorContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    principal_id: str = Field(alias="principalId")
    principal_type: str = Field(alias="principalType")
    display: str
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicyTenantContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicyNamespaceContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicyFlowContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    revision: int = Field(ge=1)
    labels: dict[str, str] = Field(default_factory=dict)
    definition: dict[str, object] = Field(default_factory=dict)


class PolicyPluginContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    packages: tuple[dict[str, object], ...] = ()
    task_types: tuple[str, ...] = Field(default=(), alias="taskTypes")


class PolicyRunnerContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    requested: str | None = None
    selected: tuple[str, ...] = ()
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicyImageContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    references: tuple[str, ...] = ()
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicySecretContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    scopes: tuple[str, ...] = ()


class PolicyNetworkContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    modes: tuple[str, ...] = ()
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicyResourceContext(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_id: str | None = Field(default=None, alias="taskId")
    task_type: str | None = Field(default=None, alias="taskType")
    inputs: dict[str, object] = Field(default_factory=dict)
    task: dict[str, object] = Field(default_factory=dict)
    attributes: dict[str, object] = Field(default_factory=dict)


class PolicyInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    actor: PolicyActorContext
    tenant: PolicyTenantContext
    namespace: PolicyNamespaceContext
    flow: PolicyFlowContext
    plugin: PolicyPluginContext = Field(default_factory=PolicyPluginContext)
    runner: PolicyRunnerContext = Field(default_factory=PolicyRunnerContext)
    image: PolicyImageContext = Field(default_factory=PolicyImageContext)
    secret: PolicySecretContext = Field(default_factory=PolicySecretContext)
    network: PolicyNetworkContext = Field(default_factory=PolicyNetworkContext)
    resource: PolicyResourceContext = Field(default_factory=PolicyResourceContext)


class PolicyEvaluationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    stage: PolicyStage
    input: PolicyInput
    approvals: tuple[str, ...] = ()


class PolicyPin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    policy_id: UUID = Field(alias="policyId")
    policy_key: str = Field(alias="policyKey")
    revision: int = Field(ge=1)
    digest: str


class PolicyConditionEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    operator: PolicyOperator
    expected: object = None
    actual: object = None
    matched: bool


class PolicyRuleEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    policy_id: UUID = Field(alias="policyId")
    policy_key: str = Field(alias="policyKey")
    policy_revision: int = Field(alias="policyRevision", ge=1)
    rule_id: str = Field(alias="ruleId")
    outcome: PolicyOutcome
    reason: str
    approval_key: str | None = Field(default=None, alias="approvalKey")
    conditions: tuple[PolicyConditionEvidence, ...] = ()


class PolicyMutation(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    value: object = None
    applied: bool


class PolicyDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    decision_id: UUID = Field(default_factory=new_runtime_id, alias="id")
    engine_version: str = Field(default=POLICY_ENGINE_VERSION, alias="engineVersion")
    stage: PolicyStage
    outcome: PolicyOutcome
    allowed: bool
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    actor_id: str = Field(alias="actorId")
    flow_id: str = Field(alias="flowId")
    flow_revision: int = Field(alias="flowRevision", ge=1)
    pinned_policies: tuple[PolicyPin, ...] = Field(alias="pinnedPolicies")
    matched_rules: tuple[PolicyRuleEvidence, ...] = Field(alias="matchedRules")
    warnings: tuple[str, ...] = ()
    mutations: tuple[PolicyMutation, ...] = ()
    required_approvals: tuple[str, ...] = Field(default=(), alias="requiredApprovals")
    input_hash: str = Field(alias="inputHash")
    evaluation_duration_ms: float = Field(alias="evaluationDurationMs", ge=0)
    evaluation_limit_ms: int = Field(alias="evaluationLimitMs", ge=1)
    mutated_input: PolicyInput | None = Field(default=None, alias="mutatedInput", exclude=True)
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="decidedAt")


class PolicyFixture(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    request: PolicyEvaluationRequest
    expected_outcome: PolicyOutcome = Field(alias="expectedOutcome")
    expected_allowed: bool = Field(alias="expectedAllowed")


class PolicyFixtureResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str
    passed: bool
    decision: PolicyDecision
    failures: tuple[str, ...] = ()


def evaluate_policies(
    revisions: tuple[PolicyRevision, ...],
    request: PolicyEvaluationRequest,
    *,
    clock: Callable[[], float] = perf_counter,
) -> PolicyDecision:
    started = clock()
    current = request.input.model_dump(mode="python", by_alias=True)
    matched_rules: list[PolicyRuleEvidence] = []
    warnings: list[str] = []
    mutations: list[PolicyMutation] = []
    required_approvals: list[str] = []
    pins: list[PolicyPin] = []
    denied = False
    timeout_limit = min(
        (revision.document.evaluation_timeout_ms for revision in revisions),
        default=100,
    )

    for revision in revisions:
        document = revision.document
        if not document.enabled:
            continue
        pins.append(
            PolicyPin(
                policyId=revision.policy_id,
                policyKey=document.policy_key,
                revision=revision.revision,
                digest=revision.digest,
            )
        )
        deadline = clock() + document.evaluation_timeout_ms / 1_000
        try:
            for rule in document.rules:
                _require_before_deadline(clock, deadline)
                if request.stage not in rule.stages:
                    continue
                evidence = tuple(
                    _condition_evidence(condition, current) for condition in rule.conditions
                )
                _require_before_deadline(clock, deadline)
                if not all(item.matched for item in evidence):
                    continue
                approval_key = (
                    f"{document.policy_key}/{rule.rule_id}"
                    if rule.outcome is PolicyOutcome.REQUIRE_APPROVAL
                    else None
                )
                matched_rules.append(
                    PolicyRuleEvidence(
                        policyId=revision.policy_id,
                        policyKey=document.policy_key,
                        policyRevision=revision.revision,
                        ruleId=rule.rule_id,
                        outcome=rule.outcome,
                        reason=rule.reason,
                        approvalKey=approval_key,
                        conditions=evidence,
                    )
                )
                if rule.outcome is PolicyOutcome.DENY:
                    denied = True
                elif rule.outcome is PolicyOutcome.WARN:
                    warnings.append(rule.reason)
                elif rule.outcome is PolicyOutcome.REQUIRE_APPROVAL:
                    assert approval_key is not None
                    if approval_key not in request.approvals:
                        required_approvals.append(approval_key)
                elif rule.outcome is PolicyOutcome.MUTATE_DEFAULT:
                    for path, value in rule.mutations.items():
                        applied = _set_default(current, path, deepcopy(value))
                        mutations.append(PolicyMutation(path=path, value=value, applied=applied))
        except TimeoutError:
            reason = (
                f"policy {document.policy_key}@{revision.revision} exceeded "
                f"{document.evaluation_timeout_ms} ms"
            )
            outcome = (
                PolicyOutcome.DENY
                if document.criticality is PolicyCriticality.ENFORCING
                else PolicyOutcome.WARN
            )
            matched_rules.append(
                PolicyRuleEvidence(
                    policyId=revision.policy_id,
                    policyKey=document.policy_key,
                    policyRevision=revision.revision,
                    ruleId="evaluation-timeout",
                    outcome=outcome,
                    reason=reason,
                )
            )
            if outcome is PolicyOutcome.DENY:
                denied = True
            else:
                warnings.append(reason)

    allowed = not denied and not required_approvals
    outcome = _decision_outcome(
        denied=denied,
        required_approvals=required_approvals,
        warnings=warnings,
        mutations=mutations,
    )
    duration_ms = max((clock() - started) * 1_000, 0)
    return PolicyDecision(
        stage=request.stage,
        outcome=outcome,
        allowed=allowed,
        tenantId=request.input.tenant.id,
        namespace=request.input.namespace.id,
        actorId=request.input.actor.principal_id,
        flowId=request.input.flow.id,
        flowRevision=request.input.flow.revision,
        pinnedPolicies=tuple(pins),
        matchedRules=tuple(matched_rules),
        warnings=tuple(warnings),
        mutations=tuple(mutations),
        requiredApprovals=tuple(dict.fromkeys(required_approvals)),
        inputHash=_input_hash(request),
        evaluationDurationMs=duration_ms,
        evaluationLimitMs=timeout_limit,
        mutatedInput=PolicyInput.model_validate(current),
    )


def test_policy_fixture(
    revision: PolicyRevision,
    fixture: PolicyFixture,
) -> PolicyFixtureResult:
    decision = evaluate_policies((revision,), fixture.request)
    failures: list[str] = []
    if decision.outcome is not fixture.expected_outcome:
        failures.append(
            f"expected outcome {fixture.expected_outcome.value}, got {decision.outcome.value}"
        )
    if decision.allowed is not fixture.expected_allowed:
        failures.append(f"expected allowed={fixture.expected_allowed}, got {decision.allowed}")
    return PolicyFixtureResult(
        name=fixture.name,
        passed=not failures,
        decision=decision,
        failures=tuple(failures),
    )


def _condition_evidence(
    condition: PolicyCondition,
    context: Mapping[str, object],
) -> PolicyConditionEvidence:
    actual = _path_value(context, condition.path)
    matched = _matches(actual, condition.operator, condition.value)
    return PolicyConditionEvidence(
        path=condition.path,
        operator=condition.operator,
        expected=condition.value,
        actual=None if actual is _MISSING else actual,
        matched=matched,
    )


def _path_value(context: Mapping[str, object], path: str) -> object:
    current: object = context
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _matches(actual: object, operator: PolicyOperator, expected: object) -> bool:
    if operator is PolicyOperator.EXISTS:
        exists = actual is not _MISSING
        return exists if expected is not False else not exists
    if actual is _MISSING:
        return False
    if operator is PolicyOperator.EQUALS:
        return actual == expected
    if operator is PolicyOperator.NOT_EQUALS:
        return actual != expected
    if operator is PolicyOperator.IN:
        return isinstance(expected, (list, tuple, set, frozenset)) and actual in expected
    if operator is PolicyOperator.CONTAINS:
        return isinstance(actual, (str, list, tuple, set, frozenset, dict)) and expected in actual
    if operator is PolicyOperator.MATCHES:
        return (
            isinstance(actual, str) and isinstance(expected, str) and fnmatchcase(actual, expected)
        )
    if operator in {
        PolicyOperator.LESS_THAN,
        PolicyOperator.LESS_THAN_OR_EQUAL,
        PolicyOperator.GREATER_THAN,
        PolicyOperator.GREATER_THAN_OR_EQUAL,
    }:
        if not isinstance(actual, (int, float)) or isinstance(actual, bool):
            return False
        if not isinstance(expected, (int, float)) or isinstance(expected, bool):
            return False
        return {
            PolicyOperator.LESS_THAN: actual < expected,
            PolicyOperator.LESS_THAN_OR_EQUAL: actual <= expected,
            PolicyOperator.GREATER_THAN: actual > expected,
            PolicyOperator.GREATER_THAN_OR_EQUAL: actual >= expected,
        }[operator]
    return False


def _set_default(context: dict[str, object], path: str, value: object) -> bool:
    parts = path.split(".")
    current = context
    for part in parts[:-1]:
        existing = current.get(part)
        if existing is None:
            nested: dict[str, object] = {}
            current[part] = nested
            current = nested
        elif isinstance(existing, dict):
            current = existing
        else:
            return False
    leaf = parts[-1]
    if leaf in current and current[leaf] is not None:
        return False
    current[leaf] = value
    return True


def _decision_outcome(
    *,
    denied: bool,
    required_approvals: list[str],
    warnings: list[str],
    mutations: list[PolicyMutation],
) -> PolicyOutcome:
    if denied:
        return PolicyOutcome.DENY
    if required_approvals:
        return PolicyOutcome.REQUIRE_APPROVAL
    if warnings:
        return PolicyOutcome.WARN
    if mutations:
        return PolicyOutcome.MUTATE_DEFAULT
    return PolicyOutcome.ALLOW


def _input_hash(request: PolicyEvaluationRequest) -> str:
    encoded = json.dumps(
        request.model_dump(mode="json", by_alias=True),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _require_before_deadline(clock: Callable[[], float], deadline: float) -> None:
    if clock() > deadline:
        raise TimeoutError("policy evaluation deadline exceeded")


def _is_sensitive_value_path(path: str) -> bool:
    if path == "secret.scopes":
        return False
    return any(part.lower() in _SENSITIVE_PATH_PARTS for part in path.split("."))
