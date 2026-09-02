from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresBackfillRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_backfill_repository,
    get_backfill_service,
    get_repository,
    get_settings,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.backfills import BackfillService
from amesh.config import Settings
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.tenancy import TenantService


async def _cleanup(engine: AsyncEngine, namespace: str) -> None:
    async with engine.begin() as connection:
        backfill_ids = list(
            await connection.scalars(
                text("SELECT id FROM backfills WHERE namespace_name = :namespace"),
                {"namespace": namespace},
            )
        )
        execution_ids = list(
            await connection.scalars(
                text("SELECT id FROM executions WHERE namespace_name = :namespace"),
                {"namespace": namespace},
            )
        )
        await connection.execute(
            text(
                "DELETE FROM messages_outbox WHERE partition_key LIKE 'backfill:%' "
                "AND partition_key = ANY(CAST(:keys AS text[]))"
            ),
            {"keys": [f"backfill:{value}" for value in backfill_ids]},
        )
        await connection.execute(
            text("DELETE FROM backfills WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": backfill_ids},
        )
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = ANY(CAST(:keys AS text[]))"),
            {"keys": [f"execution:{value}" for value in execution_ids]},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_reservations WHERE resource_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[]))) "
                "OR resource_id = ANY(CAST(:ids AS uuid[]))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_requests WHERE resource_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[]))) "
                "OR resource_id = ANY(CAST(:ids AS uuid[]))"
            ),
            {"ids": execution_ids},
        )
        for table in ("task_run_events", "task_runs", "execution_events", "executions"):
            column = "execution_id" if table != "executions" else "id"
            await connection.execute(
                text(f"DELETE FROM {table} WHERE {column} = ANY(CAST(:ids AS uuid[]))"),
                {"ids": execution_ids},
            )


def test_backfill_preview_monitor_and_lifecycle_api(migrated_test_database_url: str) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        executions = PostgresExecutionRepository(engine)
        backfills = PostgresBackfillRepository(engine)
        authorization = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenancy = TenantService(PostgresTenantRepository(engine))
        service = BackfillService(executions, backfills)
        settings = Settings(database_url=migrated_test_database_url, amesh_admin_token="test-token")
        app.dependency_overrides[get_repository] = lambda: executions
        app.dependency_overrides[get_backfill_repository] = lambda: backfills
        app.dependency_overrides[get_backfill_service] = lambda: service
        app.dependency_overrides[get_authorization_service] = lambda: authorization
        app.dependency_overrides[get_tenant_service] = lambda: tenancy
        app.dependency_overrides[get_settings] = lambda: settings
        namespace = f"tests.backfill_api.{uuid4().hex}"
        flow = FlowDefinition(
            id="api_backfill",
            namespace=namespace,
            revision=2,
            tasks=[TaskDefinition(id="return", type="core.return")],
        )
        payload = {
            "namespace": namespace,
            "flowId": flow.id,
            "flowRevision": flow.revision,
            "selection": {"partitions": ["a", "b"]},
            "inputs": {"historical": True},
            "labels": {"source": "api-test"},
            "maxConcurrency": 1,
            "ratePerMinute": 10,
            "priority": 7,
        }
        try:
            await executions.create_execution(flow, tenant_id="default", inputs={})
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                assert (
                    await client.post("/api/v1/backfills/preview", json=payload)
                ).status_code == 401
                headers = {"authorization": "Bearer test-token"}
                replay_override = {
                    **payload,
                    "selection": {"sourceExecutionIds": [str(uuid4())]},
                    "inputs": {"override": "not allowed"},
                }
                rejected = await client.post(
                    "/api/v1/backfills/preview",
                    json=replay_override,
                    headers=headers,
                )
                assert rejected.status_code == 422
                assert "overrides" in rejected.text

                preview = await client.post(
                    "/api/v1/backfills/preview", json=payload, headers=headers
                )
                assert preview.status_code == 200
                assert preview.json()["executionCount"] == 2
                assert preview.json()["estimatedTaskRuns"] == 2

                created = await client.post("/api/v1/backfills", json=payload, headers=headers)
                assert created.status_code == 201
                backfill_id = created.json()["backfillId"]
                assert created.json()["flowRevision"] == 2
                assert created.json()["pending"] == 1

                listed = await client.get("/api/v1/backfills", headers=headers)
                assert listed.status_code == 200
                assert backfill_id in {item["backfillId"] for item in listed.json()}
                fetched = await client.get(f"/api/v1/backfills/{backfill_id}", headers=headers)
                assert fetched.status_code == 200

                paused = await client.post(
                    f"/api/v1/backfills/{backfill_id}/pause",
                    json={"reason": "review impact"},
                    headers=headers,
                )
                assert paused.status_code == 200
                assert paused.json()["state"] == "PAUSED"
                resumed = await client.post(
                    f"/api/v1/backfills/{backfill_id}/resume",
                    json={"reason": "approved"},
                    headers=headers,
                )
                assert resumed.status_code == 200
                assert resumed.json()["state"] == "RUNNING"
                cancelled = await client.post(
                    f"/api/v1/backfills/{backfill_id}/cancel",
                    json={"reason": "operator stop"},
                    headers=headers,
                )
                assert cancelled.status_code == 200
                assert cancelled.json()["state"] == "CANCELLED"
                assert cancelled.json()["cancelled"] == 1
        finally:
            app.dependency_overrides.clear()
            await _cleanup(engine, namespace)
            await engine.dispose()

    asyncio.run(scenario())
