from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAdmissionPolicyRepository,
    PostgresExecutionRepository,
)
from amesh.admission_policy import AdmissionPolicyService
from amesh.domain import ExecutionState, PluginPolicyStage, PolicyDecision, PolicyOperator
from amesh.domain.policy import (
    PolicyActorContext,
    PolicyCondition,
    PolicyDocument,
    PolicyEvaluationRequest,
    PolicyFlowContext,
    PolicyInput,
    PolicyNamespaceContext,
    PolicyOutcome,
    PolicyRule,
    PolicyStage,
    PolicyTenantContext,
    evaluate_policies,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskExecutionError
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.ports import PersistedExecution, PersistedTaskRun

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_policy_revisions_decisions_and_audit_are_tenant_scoped() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        repository = PostgresAdmissionPolicyRepository(engine)
        try:
            await apply_migrations(database.database_url, migration_directory())
            first_document = PolicyDocument(
                policyKey="security.baseline",
                name="Security baseline",
                rules=(
                    PolicyRule(
                        id="warn-save",
                        stages=(PolicyStage.SAVE,),
                        outcome=PolicyOutcome.WARN,
                        reason="save policy evidence",
                    ),
                ),
            )
            first = await repository.save_revision(
                "default",
                first_document,
                actor_id="security-engineer",
            )
            second = await repository.save_revision(
                "default",
                first_document.model_copy(update={"description": "revision two"}),
                actor_id="security-engineer",
            )
            assert (first.revision, second.revision) == (1, 2)
            assert first.policy_id == second.policy_id

            effective = await repository.effective_revisions(
                "default",
                namespace="governance",
            )
            assert [(item.document.policy_key, item.revision) for item in effective] == [
                ("security.baseline", 2)
            ]
            historical = await repository.get_revision(
                "default",
                "security.baseline",
                revision=1,
            )
            assert historical.digest == first.digest

            request = PolicyEvaluationRequest(
                stage=PolicyStage.SAVE,
                input=PolicyInput(
                    actor=PolicyActorContext(
                        principalId=str(uuid4()),
                        principalType="USER",
                        display="security-engineer",
                    ),
                    tenant=PolicyTenantContext(id="default"),
                    namespace=PolicyNamespaceContext(id="governance"),
                    flow=PolicyFlowContext(id="governed", revision=1),
                ),
            )
            decision = evaluate_policies(effective, request)
            await repository.record_decision(
                decision,
                actor_id=request.input.actor.principal_id,
            )
            assert (await repository.list_decisions("default"))[0].decision_id == (
                decision.decision_id
            )

            async with engine.connect() as connection:
                count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM audit_events "
                        "WHERE resource_type = 'admission_policy'"
                    )
                )
            assert count == 3
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_launch_and_dispatch_decisions_are_pinned_in_execution_metadata() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        policies = PostgresAdmissionPolicyRepository(engine)
        service = AdmissionPolicyService(policies)
        plugin_policy_flows: list[FlowDefinition] = []

        async def plugin_policy(
            candidate: FlowDefinition,
            tenant_id: str,
            stage: PluginPolicyStage,
            actor_id: str,
        ) -> None:
            assert tenant_id == "default"
            if stage is PluginPolicyStage.AUTHORING:
                assert actor_id == "system:flow-manager"
                plugin_policy_flows.append(candidate)

        executions = PostgresExecutionRepository(
            engine,
            plugin_policy_enforcer=plugin_policy,
            admission_policy_enforcer=service.enforce_repository,
        )
        flow = FlowDefinition.model_validate(
            {
                "id": "dispatch_policy",
                "namespace": "governance",
                "tasks": [{"id": "done", "type": "core.return", "value": "blocked"}],
            }
        )
        try:
            await apply_migrations(database.database_url, migration_directory())
            await policies.save_revision(
                "default",
                PolicyDocument(
                    policyKey="security.dispatch",
                    name="Dispatch policy",
                    rules=(
                        PolicyRule(
                            id="default-label",
                            stages=(PolicyStage.SAVE,),
                            outcome=PolicyOutcome.MUTATE_DEFAULT,
                            reason="Mark governed flow revisions",
                            mutations={
                                "flow.definition.labels.policy-default": "applied"
                            },
                        ),
                        PolicyRule(
                            id="deny-return",
                            stages=(PolicyStage.DISPATCH,),
                            conditions=(
                                PolicyCondition(
                                    path="resource.taskType",
                                    operator=PolicyOperator.EQUALS,
                                    value="core.return",
                                ),
                            ),
                            outcome=PolicyOutcome.DENY,
                            reason="return tasks are disabled by fixture policy",
                        ),
                    ),
                ),
                actor_id="security-engineer",
            )
            await executions.apply_flow(flow, tenant_id="default")
            assert plugin_policy_flows[0].labels["policy-default"] == "applied"

            async def dispatch_policy(
                dispatch_flow: FlowDefinition,
                execution: PersistedExecution,
                task_run: PersistedTaskRun,
                task: TaskDefinition,
            ) -> PolicyDecision:
                return await executions.enforce_admission_policy(
                    dispatch_flow,
                    tenant_id=execution.tenant_id,
                    stage=PolicyStage.DISPATCH,
                    actor_id=execution.created_by,
                    inputs=dict(execution.inputs),
                    task=task,
                    execution_id=execution.execution_id,
                    task_run_id=task_run.task_run_id,
                )

            executor = InProcessExecutor(
                executions,
                dispatch_policy_enforcer=dispatch_policy,
            )
            execution_id = await executor.create_execution(flow, tenant_id="default")
            launched = await executions.get_execution(execution_id, tenant_id="default")
            assert launched.trigger["_ameshPolicyDecision"]["stage"] == "LAUNCH"
            determinism = launched.trigger["_ameshDeterminism"]
            assert determinism["revision"] == launched.flow_revision
            assert determinism["policyPins"] == [
                {
                    "category": "ADMISSION",
                    "key": pin["policyKey"],
                    "revision": pin["revision"],
                    "digest": pin["digest"],
                }
                for pin in launched.trigger["_ameshPolicyDecision"]["policyPins"]
            ]

            with pytest.raises(TaskExecutionError, match="unsatisfiable execution graph"):
                await executor.run_to_completion(
                    flow,
                    execution_id,
                    tenant_id="default",
                )
            completed = await executions.get_execution(
                execution_id,
                tenant_id="default",
            )
            assert completed.state is ExecutionState.FAILED
            task_run = (
                await executions.list_task_runs(execution_id, tenant_id="default")
            )[0]
            assert task_run.evidence["control"]["policy"]["outcome"] == "DENY"
            decisions = await policies.list_decisions("default", limit=10)
            assert {item.stage for item in decisions} >= {
                PolicyStage.SAVE,
                PolicyStage.LAUNCH,
                PolicyStage.DISPATCH,
            }
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
