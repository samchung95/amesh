from __future__ import annotations

import asyncio
import os
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
)
from amesh.app import app, get_authorization_service, get_repository, get_tenant_service
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
            {"partition_key": f"execution:{execution_id}"},
        )
        await connection.execute(
            text(
                "DELETE FROM transition_rejections WHERE "
                "(aggregate_type = 'execution' AND aggregate_id = :execution_id) OR "
                "(aggregate_type = 'task_run' AND aggregate_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id))"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text(
                "DELETE FROM task_attempts WHERE task_run_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM executions WHERE id = :execution_id"),
            {"execution_id": execution_id},
        )


def test_authenticated_flow_execution_and_webhook_api() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        authorization_service = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenant_service = TenantService(PostgresTenantRepository(engine))
        settings = Settings(
            database_url=TEST_DATABASE_URL,
            amesh_admin_token="test-token",
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_settings] = lambda: settings
        namespace = f"tests.api.{uuid4().hex}"
        flow_id = "api_flow"
        flow_yaml = f"""
id: {flow_id}
namespace: {namespace}
triggers:
  - id: incoming
    type: core.webhook
  - id: every_hour
    type: core.cron
    cron: "0 * * * *"
    timezone: UTC
tasks:
  - id: echo
    type: core.return
    value:
      message: "{{{{ inputs.message }}}}"
      trigger: "{{{{ trigger }}}}"
"""
        headers = {
            "authorization": "Bearer test-token",
            "content-type": "application/yaml",
        }
        execution_ids: list[UUID] = []
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                unauthorized = await client.get("/api/v1/flows")
                assert unauthorized.status_code == 401

                applied = await client.put(
                    "/api/v1/flows",
                    content=flow_yaml,
                    headers=headers,
                )
                assert applied.status_code == 200
                assert applied.json()["namespace"] == namespace
                assert applied.headers["etag"] == applied.json()["etag"]

                stale_update = await client.put(
                    "/api/v1/flows",
                    content=flow_yaml,
                    headers={**headers, "If-Match": '"sha256:stale"'},
                )
                assert stale_update.status_code == 412

                conditional_update = await client.put(
                    "/api/v1/flows",
                    content=flow_yaml,
                    headers={**headers, "If-Match": applied.headers["etag"]},
                )
                assert conditional_update.status_code == 200
                assert conditional_update.headers["etag"] != applied.headers["etag"]

                listed_flows = await client.get(
                    "/api/v1/flows",
                    headers={"authorization": "Bearer test-token"},
                )
                assert any(
                    item["namespace"] == namespace and item["flow_id"] == flow_id
                    for item in listed_flows.json()
                )
                flow_graph = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/graph",
                    headers={"authorization": "Bearer test-token"},
                )
                assert flow_graph.status_code == 200
                assert [node["taskId"] for node in flow_graph.json()["nodes"]] == ["echo"]
                assert flow_graph.json()["nodes"][0]["state"] is None

                preview = await client.get(
                    f"/api/v1/flows/{namespace}/{flow_id}/schedules/every_hour/preview",
                    headers={"authorization": "Bearer test-token"},
                    params={"after": "2026-08-21T12:05:00Z", "count": 2},
                )
                assert preview.status_code == 200
                assert preview.json() == {
                    "trigger_id": "every_hour",
                    "eligible": True,
                    "explanation": "next 2 occurrence(s) are eligible",
                    "occurrences": [
                        {
                            "trigger_id": "every_hour",
                            "scheduled_for": "2026-08-21T13:00:00Z",
                        },
                        {
                            "trigger_id": "every_hour",
                            "scheduled_for": "2026-08-21T14:00:00Z",
                        },
                    ],
                }

                created = await client.post(
                    "/api/v1/executions",
                    headers={"authorization": "Bearer test-token"},
                    json={
                        "namespace": namespace,
                        "flowId": flow_id,
                        "inputs": {"message": "manual"},
                        "runner": "local",
                    },
                )
                assert created.status_code == 200
                created_payload = created.json()
                execution_id = UUID(created_payload["execution"]["execution_id"])
                execution_ids.append(execution_id)
                assert created_payload["execution"]["state"] == "SUCCESS"
                assert created_payload["execution"]["trigger"] == {"source": "api"}
                assert created_payload["taskRuns"][0]["result"] == {
                    "value": {"message": "manual", "trigger": {"source": "api"}},
                }

                admission = await client.get(
                    f"/api/v1/executions/{execution_id}/admission",
                    headers={"authorization": "Bearer test-token"},
                )
                assert admission.status_code == 200
                assert admission.json()["outcome"] == "RELEASED"
                diagnostics = await client.get(
                    "/api/v1/admissions/diagnostics",
                    headers={"authorization": "Bearer test-token"},
                )
                assert diagnostics.status_code == 200
                assert "active_reservations" in diagnostics.json()
                reconciled = await client.post(
                    "/api/v1/admissions/reconcile",
                    headers={"authorization": "Bearer test-token"},
                )
                assert reconciled.status_code == 200
                assert reconciled.json()["promoted"] >= 0

                fetched = await client.get(
                    f"/api/v1/executions/{execution_id}",
                    headers={"authorization": "Bearer test-token"},
                )
                assert fetched.status_code == 200
                execution_graph = await client.get(
                    f"/api/v1/executions/{execution_id}/graph",
                    headers={"authorization": "Bearer test-token"},
                )
                assert execution_graph.status_code == 200
                assert execution_graph.json()["nodes"][0]["state"] == "SUCCESS"
                logs = await client.get(
                    f"/api/v1/executions/{execution_id}/logs",
                    headers={"authorization": "Bearer test-token"},
                )
                assert logs.json()[0]["output"] == {
                    "value": {"message": "manual", "trigger": {"source": "api"}},
                }

                webhook = await client.post(
                    f"/api/v1/webhooks/{namespace}/{flow_id}/incoming",
                    headers={"authorization": "Bearer test-token"},
                    json={"message": "webhook"},
                )
                assert webhook.status_code == 200
                webhook_payload = webhook.json()
                execution_ids.append(UUID(webhook_payload["execution"]["execution_id"]))
                assert webhook_payload["taskRuns"][0]["result"] == {
                    "value": {
                        "message": "webhook",
                        "trigger": {
                            "source": "event",
                            "id": "incoming",
                            "type": "core.webhook",
                            "body": {"message": "webhook"},
                        },
                    },
                }

                executions = await client.get(
                    "/api/v1/executions",
                    headers={"authorization": "Bearer test-token"},
                )
                assert executions.status_code == 200
                returned_ids = {UUID(item["execution_id"]) for item in executions.json()}
                assert set(execution_ids) <= returned_ids
                async with engine.connect() as connection:
                    assert (
                        int(
                            await connection.scalar(
                                text(
                                    "SELECT coalesce(sum(amount), 0) "
                                    "FROM tenant_quota_usage "
                                    "WHERE quota_type = 'API_REQUESTS' "
                                    "AND tenant_id = "
                                    "(SELECT id FROM tenants WHERE slug = 'default')"
                                )
                            )
                            or 0
                        )
                        >= 1
                    )
        finally:
            app.dependency_overrides.clear()
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
