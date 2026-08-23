from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from amesh.domain.authorization import ActorContext, PrincipalType
from amesh.domain.policy import (
    PolicyActorContext,
    PolicyDecision,
    PolicyDocument,
    PolicyEvaluationRequest,
    PolicyFixture,
    PolicyFixtureResult,
    PolicyFlowContext,
    PolicyImageContext,
    PolicyInput,
    PolicyNamespaceContext,
    PolicyNetworkContext,
    PolicyPluginContext,
    PolicyResourceContext,
    PolicyRevision,
    PolicyRunnerContext,
    PolicySecretContext,
    PolicyStage,
    PolicyTenantContext,
    evaluate_policies,
    test_policy_fixture,
)
from amesh.dsl import FlowDefinition, TaskDefinition, compile_execution_tasks
from amesh.workflow import redact_sensitive_inputs


class AdmissionPolicyDenied(ValueError):
    def __init__(self, decision: PolicyDecision) -> None:
        self.decision = decision
        reasons = "; ".join(item.reason for item in decision.matched_rules)
        super().__init__(
            f"admission policy {decision.outcome.value.lower()} at "
            f"{decision.stage.value.lower()}: {reasons or 'operation is not allowed'}"
        )


class AdmissionPolicyRepository(Protocol):
    async def effective_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str,
    ) -> tuple[PolicyRevision, ...]: ...

    async def save_revision(
        self,
        tenant_id: str,
        document: PolicyDocument,
        *,
        actor_id: str,
    ) -> PolicyRevision: ...

    async def get_revision(
        self,
        tenant_id: str,
        policy_key: str,
        *,
        revision: int | None = None,
    ) -> PolicyRevision: ...

    async def record_decision(
        self,
        decision: PolicyDecision,
        *,
        actor_id: str,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision: ...

    async def list_decisions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[PolicyDecision, ...]: ...


class AdmissionPolicyService:
    def __init__(self, repository: AdmissionPolicyRepository) -> None:
        self._repository = repository

    async def evaluate(
        self,
        request: PolicyEvaluationRequest,
        *,
        record: bool = True,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        revisions = await self._repository.effective_revisions(
            request.input.tenant.id,
            namespace=request.input.namespace.id,
        )
        decision = evaluate_policies(revisions, request)
        if record:
            await self._repository.record_decision(
                decision,
                actor_id=request.input.actor.principal_id,
                execution_id=execution_id,
                task_run_id=task_run_id,
            )
        return decision

    async def enforce_flow(
        self,
        flow: FlowDefinition,
        tenant_id: str,
        stage: PolicyStage,
        actor_id: str,
        *,
        actor: ActorContext | None = None,
        inputs: dict[str, object] | None = None,
        requested_runner: str | None = None,
        selected_runners: Sequence[str] = (),
        plugin_resolution: dict[str, object] | None = None,
        task: TaskDefinition | None = None,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
        approvals: tuple[str, ...] = (),
    ) -> PolicyDecision:
        request = PolicyEvaluationRequest(
            stage=stage,
            input=policy_input_from_flow(
                flow,
                tenant_id=tenant_id,
                actor=actor or _system_actor(actor_id),
                inputs=inputs,
                requested_runner=requested_runner,
                selected_runners=selected_runners,
                plugin_resolution=plugin_resolution,
                task=task,
            ),
            approvals=approvals,
        )
        decision = await self.evaluate(
            request,
            execution_id=execution_id,
            task_run_id=task_run_id,
        )
        if not decision.allowed:
            raise AdmissionPolicyDenied(decision)
        return decision

    async def enforce_repository(
        self,
        flow: FlowDefinition,
        tenant_id: str,
        stage: PolicyStage,
        actor_id: str,
        inputs: dict[str, object] | None,
        task: TaskDefinition | None,
        execution_id: UUID | None,
        task_run_id: UUID | None,
    ) -> PolicyDecision:
        return await self.enforce_flow(
            flow,
            tenant_id,
            stage,
            actor_id,
            inputs=inputs,
            task=task,
            execution_id=execution_id,
            task_run_id=task_run_id,
        )

    async def test_fixture(
        self,
        tenant_id: str,
        policy_key: str,
        fixture: PolicyFixture,
        *,
        revision: int | None = None,
    ) -> PolicyFixtureResult:
        policy = await self._repository.get_revision(
            tenant_id,
            policy_key,
            revision=revision,
        )
        return test_policy_fixture(policy, fixture)


def policy_input_from_flow(
    flow: FlowDefinition,
    *,
    tenant_id: str,
    actor: ActorContext,
    inputs: dict[str, object] | None = None,
    requested_runner: str | None = None,
    selected_runners: Sequence[str] = (),
    plugin_resolution: dict[str, object] | None = None,
    task: TaskDefinition | None = None,
) -> PolicyInput:
    planned = compile_execution_tasks(flow)
    tasks = tuple(node.task for node in planned)
    selected_task = task
    packages: tuple[dict[str, object], ...] = ()
    if plugin_resolution is not None:
        raw_packages = plugin_resolution.get("packages", ())
        if isinstance(raw_packages, list):
            packages = tuple(item for item in raw_packages if isinstance(item, dict))
    images = tuple(sorted({item.image for item in tasks if item.image is not None}))
    secret_scopes = tuple(
        sorted({scope for item in tasks for scope in item.contract.secret_scopes})
    )
    network_payloads = [
        item.network_policy.model_dump(mode="json", by_alias=True) for item in tasks
    ]
    effective_requested_runner = requested_runner
    if effective_requested_runner is None and selected_task is not None:
        runner_extension = selected_task.task_runner
        if runner_extension is not None:
            effective_requested_runner = runner_extension.type.value
    network_modes = tuple(
        sorted(
            {
                str(payload.get("access", "INHERIT"))
                for payload in network_payloads
            }
        )
    )
    allowed_egress = tuple(
        sorted(
            {
                str(host)
                for payload in network_payloads
                for host in payload.get("allowedEgress", ())
                if isinstance(host, str)
            }
        )
    )
    return PolicyInput(
        actor=PolicyActorContext(
            principalId=str(actor.principal_id),
            principalType=actor.principal_type.value,
            display=actor.display,
            attributes={
                "bootstrapAdmin": actor.bootstrap_admin,
                "credentialScopes": list(actor.credential_scopes),
            },
        ),
        tenant=PolicyTenantContext(id=tenant_id),
        namespace=PolicyNamespaceContext(id=flow.namespace),
        flow=PolicyFlowContext(
            id=flow.id,
            revision=flow.revision,
            labels=flow.labels,
            definition=flow.model_dump(mode="json", by_alias=True),
        ),
        plugin=PolicyPluginContext(
            packages=packages,
            taskTypes=tuple(sorted({item.type for item in tasks})),
        ),
        runner=PolicyRunnerContext(
            requested=effective_requested_runner,
            selected=tuple(sorted(set(selected_runners))),
        ),
        image=PolicyImageContext(references=images),
        secret=PolicySecretContext(scopes=secret_scopes),
        network=PolicyNetworkContext(
            modes=network_modes,
            allowedEgress=allowed_egress,
        ),
        resource=PolicyResourceContext(
            taskId=selected_task.id if selected_task is not None else None,
            taskType=selected_task.type if selected_task is not None else None,
            inputs=redact_sensitive_inputs(flow, inputs or {}),
            task=(
                selected_task.model_dump(mode="json", by_alias=True)
                if selected_task is not None
                else {}
            ),
            attributes={"taskCount": len(tasks)},
        ),
    )


def policy_decision_metadata(decision: PolicyDecision) -> dict[str, object]:
    """Return redaction-safe, bounded decision evidence for execution metadata."""

    return {
        "id": str(decision.decision_id),
        "engineVersion": decision.engine_version,
        "stage": decision.stage.value,
        "outcome": decision.outcome.value,
        "allowed": decision.allowed,
        "policyPins": [
            item.model_dump(mode="json", by_alias=True) for item in decision.pinned_policies
        ],
        "matchedRules": [
            item.model_dump(mode="json", by_alias=True) for item in decision.matched_rules
        ],
        "warnings": list(decision.warnings),
        "mutations": [item.model_dump(mode="json") for item in decision.mutations],
        "requiredApprovals": list(decision.required_approvals),
        "inputHash": decision.input_hash,
        "evaluationDurationMs": decision.evaluation_duration_ms,
    }


def _system_actor(actor_id: str) -> ActorContext:
    try:
        principal_id = UUID(actor_id)
    except ValueError:
        principal_id = UUID(int=0)
    return ActorContext(
        principal_id=principal_id,
        principal_type=PrincipalType.SYSTEM,
        display=actor_id,
    )
