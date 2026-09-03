from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresHumanTaskRepository
from amesh.adapters.postgres.human_task_repository import WorkflowAppVersionConflict
from amesh.domain import ExecutionState
from amesh.domain.human_tasks import (
    AppForm,
    FormField,
    FormSection,
    HumanTaskActionKind,
    HumanTaskActionRequest,
    HumanTaskState,
    WorkflowAppSpec,
    form_from_flow,
)
from amesh.dsl import FlowDefinition
from amesh.executor import InProcessExecutor
from amesh.human_tasks import HumanTaskService, approval_task_handler
from amesh.ports import TaskRunState

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_versioned_apps_and_durable_human_approval_resume_exactly_once(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            human_tasks = PostgresHumanTaskRepository(engine)
            participant_id = uuid4()
            outsider_id = uuid4()
            flow = FlowDefinition.model_validate(
                {
                    "id": "expense_review",
                    "namespace": "tests.apps",
                    "inputs": [
                        {
                            "id": "amount",
                            "type": "number",
                            "required": True,
                            "displayName": "Expense amount",
                            "description": "Amount requested for reimbursement.",
                            "validation": {"minimum": 0},
                        }
                    ],
                    "tasks": [
                        {
                            "id": "manager_review",
                            "type": "core.approval",
                            "title": "Review expense",
                            "description": "Confirm the submitted amount.",
                            "assigneeIds": [str(participant_id)],
                            "escalationAssigneeIds": [str(participant_id)],
                            "deadlineAt": datetime.now(UTC) - timedelta(seconds=1),
                            "form": {
                                "fields": [
                                    {
                                        "id": "costCenter",
                                        "type": "text",
                                        "label": "Cost center",
                                        "required": True,
                                    }
                                ],
                                "layout": [{"title": "Decision", "fields": ["costCenter"]}],
                            },
                        }
                    ],
                }
            )
            persisted = await executions.apply_flow(
                flow,
                tenant_id="default",
                actor_id="test-author",
            )
            generated_form = form_from_flow(flow)
            assert generated_form.fields[0].label == "Expense amount"
            app_spec = WorkflowAppSpec(
                title="Expense request",
                description="Submit an expense for manager review.",
                flowId=flow.id,
                flowRevision=persisted.revision,
                form=generated_form,
            )
            created_app = await human_tasks.upsert_app(
                flow.namespace,
                "expense-request",
                app_spec,
                tenant_id="default",
                actor_id="test-author",
                expected_version=None,
            )
            assert created_app.revision == created_app.resource_version == 1
            updated_app = await human_tasks.upsert_app(
                flow.namespace,
                "expense-request",
                app_spec.model_copy(update={"title": "Expense approval"}),
                tenant_id="default",
                actor_id="test-author",
                expected_version=1,
            )
            assert updated_app.revision == updated_app.resource_version == 2
            assert (
                await human_tasks.get_app(
                    flow.namespace,
                    "expense-request",
                    tenant_id="default",
                    revision=1,
                )
            ).title == "Expense request"
            with pytest.raises(WorkflowAppVersionConflict):
                await human_tasks.upsert_app(
                    flow.namespace,
                    "expense-request",
                    app_spec,
                    tenant_id="default",
                    actor_id="test-author",
                    expected_version=1,
                )

            token_pepper = "test-human-task-token-pepper"
            executor = InProcessExecutor(
                executions,
                handlers={
                    "core.approval": approval_task_handler(
                        human_tasks,
                        executions,
                        token_pepper=token_pepper,
                    )
                },
            )
            execution_id = await executor.create_execution(
                flow,
                tenant_id="default",
                inputs={"amount": 42.5},
            )
            deferred = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert deferred.state is ExecutionState.RUNNING
            assert deferred.task_runs[0].state is TaskRunState.RUNNING
            assert await human_tasks.list_tasks(outsider_id, tenant_id="default") == ()
            assigned = await human_tasks.list_tasks(participant_id, tenant_id="default")
            assert len(assigned) == 1
            assert assigned[0].state is HumanTaskState.OPEN

            service = HumanTaskService(
                human_tasks,
                executions,
                token_pepper=token_pepper,
            )
            await service.reconcile(tenant_id="default")
            escalated = await human_tasks.get_task(
                assigned[0].human_task_id,
                participant_id,
                tenant_id="default",
            )
            assert escalated.state is HumanTaskState.ESCALATED
            assert escalated.actions[0].action.value == "ESCALATE"

            decision = HumanTaskActionRequest(
                action=HumanTaskActionKind.APPROVE,
                idempotencyKey="approval-request-001",
                reason="Budget owner confirmed",
                formValues={"costCenter": "PLATFORM"},
            )
            decided = await service.apply_action(
                escalated.human_task_id,
                decision,
                tenant_id="default",
                actor_id=participant_id,
            )
            duplicate = await service.apply_action(
                escalated.human_task_id,
                decision,
                tenant_id="default",
                actor_id=participant_id,
            )
            assert decided.state is HumanTaskState.APPROVED
            assert duplicate == decided
            assert decided.form_values == {"costCenter": "PLATFORM"}
            task_run = (await executions.list_task_runs(execution_id, tenant_id="default"))[0]
            assert task_run.state is TaskRunState.SUCCESS
            assert task_run.result is not None
            assert task_run.result["decision"] == "APPROVED"
            assert task_run.evidence is not None
            assert task_run.evidence["humanTask"]["formValues"] == {"costCenter": "PLATFORM"}
            finished = await InProcessExecutor(executions).run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert finished.state is ExecutionState.SUCCESS

            notifications = await human_tasks.list_notifications(
                participant_id,
                tenant_id="default",
            )
            assert {notification.kind for notification in notifications} == {
                "ASSIGNED",
                "ESCALATED",
                "DECIDED",
            }
            payload = [item.model_dump(mode="json", by_alias=True) for item in notifications]
            assert "executionId" not in repr(payload)
            assert "costCenter" not in repr(payload)
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_explicit_app_form_shape_is_validated() -> None:
    with pytest.raises(ValueError, match="unknown fields"):
        AppForm(
            fields=(FormField(id="known", type="text", label="Known"),),
            layout=(FormSection(title="Main", fields=("missing",)),),
        )
