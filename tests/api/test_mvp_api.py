from __future__ import annotations

import asyncio
import json
import os
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresDashboardRepository,
    PostgresExecutionRepository,
    PostgresMetadataRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_dashboard_repository,
    get_metadata_repository,
    get_repository,
    get_tenant_service,
    get_trigger_runtime_repository,
)
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
            text(
                "DELETE FROM trigger_occurrence_events WHERE occurrence_id IN "
                "(SELECT occurrence_id FROM trigger_occurrences "
                "WHERE execution_id = :execution_id)"
            ),
            {"execution_id": execution_id},
        )
        await connection.execute(
            text("DELETE FROM trigger_occurrences WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
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


async def cleanup_dashboard(engine: AsyncEngine, dashboard_id: str) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
            {"partition_key": f"dashboard:{dashboard_id}"},
        )
        await connection.execute(
            text("DELETE FROM dashboard_definition_events WHERE dashboard_id = :dashboard_id"),
            {"dashboard_id": dashboard_id},
        )
        await connection.execute(
            text("DELETE FROM dashboard_definitions WHERE dashboard_id = :dashboard_id"),
            {"dashboard_id": dashboard_id},
        )


def test_authenticated_flow_execution_and_webhook_api() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        metadata = PostgresMetadataRepository(engine)
        dashboards = PostgresDashboardRepository(engine)
        authorization_service = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenant_service = TenantService(PostgresTenantRepository(engine))
        settings = Settings(
            database_url=TEST_DATABASE_URL,
            amesh_admin_token="test-token",
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_metadata_repository] = lambda: metadata
        app.dependency_overrides[get_dashboard_repository] = lambda: dashboards
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_trigger_runtime_repository] = lambda: (
            PostgresTriggerRuntimeRepository(engine)
        )
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
        dashboard_id = f"api.{uuid4().hex}"
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
                selected_flows = await client.get(
                    "/api/v1/flows",
                    headers={"authorization": "Bearer test-token"},
                    params={
                        "filter": f"namespace={namespace}",
                        "sort": "-revision",
                        "fields": "namespace,flow_id,revision",
                        "limit": 1,
                    },
                )
                assert selected_flows.status_code == 200
                assert selected_flows.headers["x-total-count"] == "1"
                assert selected_flows.json() == [
                    {
                        "namespace": namespace,
                        "flow_id": flow_id,
                        "revision": conditional_update.json()["revision"],
                    }
                ]
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
                bounded_detail = await client.get(
                    f"/api/v1/executions/{execution_id}",
                    headers={"authorization": "Bearer test-token"},
                    params={"taskOffset": 0, "taskLimit": 1},
                )
                assert bounded_detail.status_code == 200
                assert len(bounded_detail.json()["taskRuns"]) == 1
                assert bounded_detail.json()["taskRunOffset"] == 0
                assert bounded_detail.json()["taskRunSummary"] == {
                    "total": 1,
                    "waiting": 0,
                    "running": 0,
                    "retry_delay": 0,
                    "succeeded": 1,
                    "failed": 0,
                    "cancelled": 0,
                }

                async_key = f"api-async-{uuid4().hex}"
                accepted = await client.post(
                    "/api/v1/executions",
                    headers={
                        "authorization": "Bearer test-token",
                        "Prefer": "respond-async",
                        "Idempotency-Key": async_key,
                    },
                    json={
                        "namespace": namespace,
                        "flowId": flow_id,
                        "inputs": {"message": "async"},
                        "runner": "local",
                    },
                )
                assert accepted.status_code == 202
                assert accepted.headers["preference-applied"] == "respond-async"
                accepted_payload = accepted.json()
                accepted_execution_id = UUID(accepted_payload["execution"]["execution_id"])
                execution_ids.append(accepted_execution_id)
                assert accepted.headers["location"] == (
                    f"/api/v1/executions/{accepted_execution_id}"
                )
                assert accepted_payload["execution"]["state"] == "RUNNING"

                completed_async = await client.get(
                    f"/api/v1/executions/{accepted_execution_id}",
                    headers={"authorization": "Bearer test-token"},
                )
                assert completed_async.status_code == 200
                assert completed_async.json()["execution"]["state"] == "SUCCESS"

                replayed = await client.post(
                    "/api/v1/executions",
                    headers={
                        "authorization": "Bearer test-token",
                        "Prefer": "respond-async",
                        "Idempotency-Key": async_key,
                    },
                    json={
                        "namespace": namespace,
                        "flowId": flow_id,
                        "inputs": {"message": "async"},
                        "runner": "local",
                    },
                )
                assert replayed.status_code == 200
                assert replayed.json()["execution"]["execution_id"] == str(accepted_execution_id)

                conflicting_key = await client.post(
                    "/api/v1/executions",
                    headers={
                        "authorization": "Bearer test-token",
                        "Idempotency-Key": "header-key",
                    },
                    json={
                        "namespace": namespace,
                        "flowId": flow_id,
                        "idempotencyKey": "body-key",
                    },
                )
                assert conflicting_key.status_code == 400

                bulk = await client.post(
                    "/api/v1/executions/bulk",
                    headers={
                        "authorization": "Bearer test-token",
                        "Prefer": "respond-async",
                    },
                    json={
                        "items": [
                            {
                                "namespace": namespace,
                                "flowId": flow_id,
                                "inputs": {"message": "bulk"},
                                "idempotencyKey": f"bulk-{uuid4().hex}",
                            },
                            {"namespace": namespace, "flowId": "missing-flow"},
                        ]
                    },
                )
                assert bulk.status_code == 207
                bulk_payload = bulk.json()
                assert [item["status"] for item in bulk_payload] == [202, 404]
                bulk_execution_id = UUID(bulk_payload[0]["execution"]["execution"]["execution_id"])
                execution_ids.append(bulk_execution_id)
                assert bulk_payload[1]["error"]["detail"].endswith("does not exist")

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
                evidence_page = await client.get(
                    f"/api/v1/executions/{execution_id}/evidence",
                    headers={"authorization": "Bearer test-token"},
                    params={"limit": 2},
                )
                assert evidence_page.status_code == 200
                assert len(evidence_page.json()["items"]) == 2
                assert evidence_page.json()["nextCursor"]
                next_evidence_page = await client.get(
                    f"/api/v1/executions/{execution_id}/evidence",
                    headers={"authorization": "Bearer test-token"},
                    params={"cursor": evidence_page.json()["nextCursor"]},
                )
                assert next_evidence_page.status_code == 200
                evidence_items = evidence_page.json()["items"] + next_evidence_page.json()["items"]
                assert {item["kind"] for item in evidence_items} >= {"STATE", "OUTPUT"}
                state_evidence = [item for item in evidence_items if item["kind"] == "STATE"]
                assert state_evidence
                assert all("actorId" in item["payload"] for item in state_evidence)
                assert all("causationId" in item["payload"] for item in state_evidence)
                assert [item["cursor"] for item in evidence_items] == sorted(
                    item["cursor"] for item in evidence_items
                )
                streamed_evidence = await client.get(
                    f"/api/v1/executions/{execution_id}/evidence/stream",
                    headers={"authorization": "Bearer test-token"},
                    params={"cursor": evidence_page.json()["nextCursor"]},
                )
                assert streamed_evidence.status_code == 200
                assert streamed_evidence.headers["content-type"].startswith("application/x-ndjson")
                streamed_evidence_items = [
                    json.loads(line) for line in streamed_evidence.text.splitlines()
                ]
                assert [item["cursor"] for item in streamed_evidence_items] == [
                    item["cursor"] for item in next_evidence_page.json()["items"]
                ]
                assert all(item["nextCursor"] for item in streamed_evidence_items)
                logs = await client.get(
                    f"/api/v1/executions/{execution_id}/logs",
                    headers={"authorization": "Bearer test-token"},
                )
                assert logs.json()[0]["output"] == {
                    "value": {"message": "manual", "trigger": {"source": "api"}},
                }
                streamed_logs = await client.get(
                    f"/api/v1/executions/{execution_id}/logs/stream",
                    headers={"authorization": "Bearer test-token"},
                )
                assert streamed_logs.status_code == 200
                assert streamed_logs.headers["content-type"].startswith("application/x-ndjson")
                streamed_entries = [json.loads(line) for line in streamed_logs.text.splitlines()]
                assert streamed_entries == logs.json()

                webhook = await client.post(
                    f"/api/v1/webhooks/{namespace}/{flow_id}/incoming",
                    headers={"authorization": "Bearer test-token"},
                    json={"message": "webhook"},
                )
                assert webhook.status_code == 200
                webhook_payload = webhook.json()
                execution_ids.append(UUID(webhook_payload["execution"]["execution_id"]))
                webhook_value = webhook_payload["taskRuns"][0]["result"]["value"]
                assert webhook_value["message"] == "webhook"
                assert webhook_value["trigger"]["source"] == "event"
                assert webhook_value["trigger"]["id"] == "incoming"
                assert webhook_value["trigger"]["type"] == "core.webhook"
                assert webhook_value["trigger"]["body"] == {"message": "webhook"}
                UUID(webhook_value["trigger"]["occurrenceId"])
                assert webhook_value["trigger"]["occurrenceKey"].startswith(
                    f"webhook:{namespace}:{flow_id}:1:incoming:sha256:"
                )

                executions = await client.get(
                    "/api/v1/executions",
                    headers={"authorization": "Bearer test-token"},
                )
                assert executions.status_code == 200
                returned_ids = {UUID(item["execution_id"]) for item in executions.json()}
                assert set(execution_ids) <= returned_ids

                listed_dashboards = await client.get(
                    "/api/v1/dashboards",
                    headers={"authorization": "Bearer test-token"},
                )
                assert listed_dashboards.status_code == 200
                assert {
                    "builtin.instance",
                    "builtin.tenant",
                    "builtin.namespace",
                    "builtin.flow",
                    "builtin.workers",
                    "builtin.sla",
                } <= {item["dashboardId"] for item in listed_dashboards.json()}
                created_dashboard = await client.put(
                    f"/api/v1/dashboards/{dashboard_id}",
                    headers={
                        "authorization": "Bearer test-token",
                        "content-type": "application/json",
                    },
                    json={
                        "title": "API execution states",
                        "visibility": "TENANT",
                        "viewerIds": [],
                        "editorIds": [],
                        "source": "API",
                        "widgets": [
                            {
                                "widgetId": "states",
                                "title": "States",
                                "query": {
                                    "source": "EXECUTIONS",
                                    "visualization": "STATUS_BREAKDOWN",
                                    "filters": {"namespace": namespace},
                                },
                            }
                        ],
                    },
                )
                assert created_dashboard.status_code == 200
                assert created_dashboard.json()["version"] == 1
                rendered_dashboard = await client.post(
                    f"/api/v1/dashboards/{dashboard_id}/render",
                    headers={
                        "authorization": "Bearer test-token",
                        "content-type": "application/json",
                    },
                    json={"namespace": namespace},
                )
                assert rendered_dashboard.status_code == 200
                rendered_widget = rendered_dashboard.json()["widgets"][0]["result"]
                assert rendered_widget["redacted"] is False
                assert rendered_widget["scannedRows"] >= 1
                assert rendered_widget["freshAt"]
                invalid_query = await client.post(
                    "/api/v1/dashboard-queries",
                    headers={
                        "authorization": "Bearer test-token",
                        "content-type": "application/json",
                    },
                    json={
                        "source": "EXECUTIONS",
                        "visualization": "COUNTER",
                        "groupBy": ["sql.drop_table"],
                    },
                )
                assert invalid_query.status_code == 422
                exported_dashboard = await client.get(
                    f"/api/v1/dashboards/{dashboard_id}/export?format=yaml",
                    headers={"authorization": "Bearer test-token"},
                )
                assert exported_dashboard.status_code == 200
                assert exported_dashboard.headers["content-type"].startswith("application/yaml")
                assert f"dashboardId: {dashboard_id}" in exported_dashboard.text
                deleted_dashboard = await client.delete(
                    f"/api/v1/dashboards/{dashboard_id}?expectedVersion=1",
                    headers={"authorization": "Bearer test-token"},
                )
                assert deleted_dashboard.status_code == 204
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
            await cleanup_dashboard(engine, dashboard_id)
            await engine.dispose()

    asyncio.run(scenario())
