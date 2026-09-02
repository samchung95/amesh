from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from amesh.admission_policy import AdmissionPolicyDenied, AdmissionPolicyService
from amesh.domain import ActorContext, PrincipalType
from amesh.domain.policy import (
    PolicyActorContext,
    PolicyCondition,
    PolicyCriticality,
    PolicyDecision,
    PolicyDocument,
    PolicyEvaluationRequest,
    PolicyFixture,
    PolicyFlowContext,
    PolicyInput,
    PolicyNamespaceContext,
    PolicyOperator,
    PolicyOutcome,
    PolicyResourceContext,
    PolicyRevision,
    PolicyRule,
    PolicyRunnerContext,
    PolicyStage,
    PolicyTenantContext,
    evaluate_policies,
)
from amesh.domain.policy import (
    test_policy_fixture as run_policy_fixture,
)
from amesh.dsl import FlowDefinition


def _input(*, runner: str | None = None, inputs: dict[str, object] | None = None) -> PolicyInput:
    return PolicyInput(
        actor=PolicyActorContext(
            principalId=str(uuid4()),
            principalType="USER",
            display="policy-tester",
        ),
        tenant=PolicyTenantContext(id="default"),
        namespace=PolicyNamespaceContext(id="governance"),
        flow=PolicyFlowContext(id="governed", revision=3),
        runner=PolicyRunnerContext(requested=runner),
        resource=PolicyResourceContext(inputs=inputs or {}),
    )


def _revision(
    *rules: PolicyRule,
    criticality: PolicyCriticality = PolicyCriticality.ENFORCING,
    timeout_ms: int = 100,
) -> PolicyRevision:
    document = PolicyDocument(
        policyKey="secure.defaults",
        name="Secure defaults",
        criticality=criticality,
        evaluationTimeoutMs=timeout_ms,
        rules=rules,
    )
    return PolicyRevision(
        policyId=uuid4(),
        tenantId="default",
        revision=4,
        digest=document.digest,
        document=document,
        createdBy="tester",
    )


def test_declarative_rules_explain_deny_warn_and_pin_revisions() -> None:
    revision = _revision(
        PolicyRule(
            id="warn-docker",
            stages=(PolicyStage.LAUNCH,),
            conditions=(
                PolicyCondition(
                    path="runner.requested",
                    operator=PolicyOperator.EQUALS,
                    value="DOCKER",
                ),
            ),
            outcome=PolicyOutcome.WARN,
            reason="Docker launches require review",
        ),
        PolicyRule(
            id="deny-production",
            stages=(PolicyStage.LAUNCH,),
            conditions=(
                PolicyCondition(
                    path="resource.inputs.environment",
                    operator=PolicyOperator.EQUALS,
                    value="production",
                ),
            ),
            outcome=PolicyOutcome.DENY,
            reason="Direct production launches are prohibited",
        ),
    )

    decision = evaluate_policies(
        (revision,),
        PolicyEvaluationRequest(
            stage=PolicyStage.LAUNCH,
            input=_input(runner="DOCKER", inputs={"environment": "production"}),
        ),
    )

    assert decision.allowed is False
    assert decision.outcome is PolicyOutcome.DENY
    assert decision.pinned_policies[0].revision == 4
    assert [item.rule_id for item in decision.matched_rules] == [
        "warn-docker",
        "deny-production",
    ]
    assert decision.matched_rules[1].conditions[0].actual == "production"
    assert decision.warnings == ("Docker launches require review",)


def test_mutate_default_never_overwrites_and_approval_is_explicit() -> None:
    revision = _revision(
        PolicyRule(
            id="region-default",
            stages=(PolicyStage.LAUNCH,),
            outcome=PolicyOutcome.MUTATE_DEFAULT,
            reason="Use the local region unless the caller selected one",
            mutations={"resource.inputs.region": "local"},
        ),
        PolicyRule(
            id="production-approval",
            stages=(PolicyStage.LAUNCH,),
            conditions=(
                PolicyCondition(
                    path="resource.inputs.environment",
                    operator=PolicyOperator.EQUALS,
                    value="production",
                ),
            ),
            outcome=PolicyOutcome.REQUIRE_APPROVAL,
            reason="Production requires a security approval",
        ),
    )
    request = PolicyEvaluationRequest(
        stage=PolicyStage.LAUNCH,
        input=_input(inputs={"environment": "production"}),
    )

    pending = evaluate_policies((revision,), request)
    assert pending.outcome is PolicyOutcome.REQUIRE_APPROVAL
    assert pending.required_approvals == ("secure.defaults/production-approval",)
    assert pending.mutated_input is not None
    assert pending.mutated_input.resource.inputs["region"] == "local"
    assert pending.mutations[0].applied is True
    assert "mutatedInput" not in pending.model_dump(mode="json", by_alias=True)

    approved = evaluate_policies(
        (revision,),
        request.model_copy(update={"approvals": ("secure.defaults/production-approval",)}),
    )
    assert approved.allowed is True
    assert approved.outcome is PolicyOutcome.MUTATE_DEFAULT

    explicit = evaluate_policies(
        (revision,),
        PolicyEvaluationRequest(
            stage=PolicyStage.LAUNCH,
            input=_input(inputs={"region": "user-selected"}),
            approvals=("secure.defaults/production-approval",),
        ),
    )
    assert explicit.mutated_input is not None
    assert explicit.mutated_input.resource.inputs["region"] == "user-selected"
    assert explicit.mutations[0].applied is False


@pytest.mark.parametrize(
    ("criticality", "expected_outcome", "allowed"),
    [
        (PolicyCriticality.ENFORCING, PolicyOutcome.DENY, False),
        (PolicyCriticality.ADVISORY, PolicyOutcome.WARN, True),
    ],
)
def test_evaluation_timeout_fails_safely_by_criticality(
    criticality: PolicyCriticality,
    expected_outcome: PolicyOutcome,
    allowed: bool,
) -> None:
    revision = _revision(
        PolicyRule(
            id="bounded",
            stages=(PolicyStage.DISPATCH,),
            outcome=PolicyOutcome.ALLOW,
            reason="bounded test rule",
        ),
        criticality=criticality,
        timeout_ms=1,
    )
    values = iter((0.0, 0.01, 0.02, 0.03, 0.04))

    decision = evaluate_policies(
        (revision,),
        PolicyEvaluationRequest(stage=PolicyStage.DISPATCH, input=_input()),
        clock=lambda: next(values),
    )

    assert decision.outcome is expected_outcome
    assert decision.allowed is allowed
    assert decision.matched_rules[0].rule_id == "evaluation-timeout"


def test_policy_fixture_reports_expected_outcome_mismatches() -> None:
    revision = _revision(
        PolicyRule(
            id="deny-docker",
            stages=(PolicyStage.DISPATCH,),
            conditions=(
                PolicyCondition(
                    path="runner.requested",
                    operator=PolicyOperator.EQUALS,
                    value="DOCKER",
                ),
            ),
            outcome=PolicyOutcome.DENY,
            reason="Docker is disabled",
        )
    )
    fixture = PolicyFixture(
        name="docker denied",
        request=PolicyEvaluationRequest(
            stage=PolicyStage.DISPATCH,
            input=_input(runner="DOCKER"),
        ),
        expectedOutcome=PolicyOutcome.ALLOW,
        expectedAllowed=True,
    )

    result = run_policy_fixture(revision, fixture)

    assert result.passed is False
    assert "expected outcome ALLOW, got DENY" in result.failures


class _Repository:
    def __init__(self, revisions: tuple[PolicyRevision, ...]) -> None:
        self.revisions = revisions
        self.decisions: list[tuple[PolicyDecision, UUID | None, UUID | None]] = []

    async def effective_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str,
    ) -> tuple[PolicyRevision, ...]:
        assert tenant_id == "default"
        assert namespace == "governance"
        return self.revisions

    async def save_revision(
        self,
        tenant_id: str,
        document: PolicyDocument,
        *,
        actor_id: str,
    ) -> PolicyRevision:
        del tenant_id, document, actor_id
        return self.revisions[0]

    async def get_revision(
        self,
        tenant_id: str,
        policy_key: str,
        *,
        revision: int | None = None,
    ) -> PolicyRevision:
        del tenant_id, policy_key, revision
        return self.revisions[0]

    async def record_decision(
        self,
        decision: PolicyDecision,
        *,
        actor_id: str,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        del actor_id
        self.decisions.append((decision, execution_id, task_run_id))
        return decision

    async def list_decisions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[PolicyDecision, ...]:
        del tenant_id, limit
        return tuple(item[0] for item in self.decisions)


def test_service_builds_secret_safe_dispatch_context_and_records_metadata_links() -> None:
    revision = _revision(
        PolicyRule(
            id="deny-payment-secret",
            stages=(PolicyStage.DISPATCH,),
            conditions=(
                PolicyCondition(
                    path="secret.scopes",
                    operator=PolicyOperator.CONTAINS,
                    value="payments:read",
                ),
            ),
            outcome=PolicyOutcome.DENY,
            reason="Payment secrets cannot be used by this task",
        )
    )
    repository = _Repository((revision,))
    service = AdmissionPolicyService(repository)
    flow = FlowDefinition.model_validate(
        {
            "id": "governed",
            "namespace": "governance",
            "inputs": [{"id": "credential", "type": "SECRET"}],
            "tasks": [
                {
                    "id": "payment",
                    "type": "core.return",
                    "contract": {"secretScopes": ["payments:read"]},
                }
            ],
        }
    )
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="security-engineer",
    )
    execution_id = uuid4()
    task_run_id = uuid4()

    with pytest.raises(AdmissionPolicyDenied) as denied:
        asyncio.run(
            service.enforce_flow(
                flow,
                "default",
                PolicyStage.DISPATCH,
                str(actor.principal_id),
                actor=actor,
                inputs={"credential": "plaintext-must-not-persist"},
                task=flow.tasks[0],
                execution_id=execution_id,
                task_run_id=task_run_id,
            )
        )

    assert denied.value.decision.mutated_input is not None
    assert denied.value.decision.mutated_input.secret.scopes == ("payments:read",)
    assert denied.value.decision.mutated_input.resource.inputs["credential"] == "[REDACTED]"
    assert "plaintext-must-not-persist" not in denied.value.decision.model_dump_json(by_alias=True)
    assert repository.decisions[0][1:] == (execution_id, task_run_id)
    assert denied.value.decision.decided_at <= datetime.now(UTC)
