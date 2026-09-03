from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuota

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresHumanTaskRepository
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_human_task_repository,
    get_human_task_service,
    get_repository,
    get_tenant_service,
)
from amesh.domain import ActorContext, AuthorizationDecision, AuthorizationRequest, PrincipalType
from amesh.dsl import FlowDefinition
from amesh.executor import InProcessExecutor
from amesh.human_tasks import HumanTaskService, approval_task_handler

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class _AllowApps:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="apps API fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        return await self.decide(request)


def test_apps_and_human_task_api_expose_versioned_forms_and_decisions(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        executions = PostgresExecutionRepository(engine)
        human_tasks = PostgresHumanTaskRepository(engine)
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="approval-participant",
        )
        pepper = "apps-api-test-pepper"
        service = HumanTaskService(human_tasks, executions, token_pepper=pepper)
        flow = FlowDefinition.model_validate(
            {
                "id": "api_review",
                "namespace": "tests.apps.api",
                "inputs": [
                    {
                        "id": "request",
                        "type": "string",
                        "required": True,
                        "displayName": "Request",
                        "description": "What should be reviewed?",
                    }
                ],
                "tasks": [
                    {
                        "id": "review",
                        "type": "core.approval",
                        "title": "API approval",
                        "assigneeIds": [str(actor.principal_id)],
                    }
                ],
            }
        )
        try:
            await executions.apply_flow(flow, tenant_id="default", actor_id="test-author")
            executor = InProcessExecutor(
                executions,
                handlers={
                    "core.approval": approval_task_handler(
                        human_tasks,
                        executions,
                        token_pepper=pepper,
                    )
                },
            )
            execution_id = await executor.create_execution(
                flow,
                tenant_id="default",
                inputs={"request": "Review this"},
            )
            await executor.run_to_completion(flow, execution_id, tenant_id="default")

            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_authorization_service] = _AllowApps
            app.dependency_overrides[get_tenant_service] = _TenantQuota
            app.dependency_overrides[get_repository] = lambda: executions
            app.dependency_overrides[get_human_task_repository] = lambda: human_tasks
            app.dependency_overrides[get_human_task_service] = lambda: service
            headers = {"X-Amesh-Tenant": "default"}
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                created = await client.put(
                    "/api/v1/apps/tests.apps.api/review-request",
                    headers=headers,
                    json={
                        "title": "Review request",
                        "description": "Submit a request for review.",
                        "flowId": flow.id,
                    },
                )
                assert created.status_code == 200, created.text
                assert created.json()["form"]["fields"][0]["label"] == "Request"
                assert created.json()["flowRevision"] == 1

                listed = await client.get("/api/v1/apps", headers=headers)
                assert listed.status_code == 200
                assert [item["appId"] for item in listed.json()] == ["review-request"]
                deep_link = await client.get(
                    "/api/v1/apps/tests.apps.api/review-request",
                    headers=headers,
                )
                assert deep_link.status_code == 200
                assert deep_link.json()["embedEnabled"] is True

                stale = await client.put(
                    "/api/v1/apps/tests.apps.api/review-request",
                    headers=headers,
                    json={
                        "title": "Stale update",
                        "flowId": flow.id,
                        "expectedVersion": 99,
                    },
                )
                assert stale.status_code == 412

                inbox = await client.get("/api/v1/human-tasks", headers=headers)
                assert inbox.status_code == 200, inbox.text
                task_id = inbox.json()[0]["humanTaskId"]
                approved = await client.post(
                    f"/api/v1/human-tasks/{task_id}/actions",
                    headers=headers,
                    json={
                        "action": "APPROVE",
                        "idempotencyKey": "api-approval-001",
                        "reason": "Looks good",
                        "formValues": {"reviewed": True},
                    },
                )
                assert approved.status_code == 200, approved.text
                assert approved.json()["state"] == "APPROVED"
                assert approved.json()["formValues"] == {"reviewed": True}

                notifications = await client.get(
                    "/api/v1/human-task-notifications",
                    headers=headers,
                )
                assert notifications.status_code == 200
                assert {item["kind"] for item in notifications.json()} == {
                    "ASSIGNED",
                    "DECIDED",
                }
                assert "executionId" not in notifications.text
                assert "reviewed" not in notifications.text
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
