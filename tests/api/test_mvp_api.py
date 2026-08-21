from __future__ import annotations

import asyncio
import os
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.app import app, get_repository
from amesh.config import Settings, get_settings

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
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
        settings = Settings(
            database_url=TEST_DATABASE_URL,
            amesh_admin_token="test-token",
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_settings] = lambda: settings
        namespace = f"tests.api.{uuid4().hex}"
        flow_id = "api_flow"
        flow_yaml = f"""
id: {flow_id}
namespace: {namespace}
triggers:
  - id: incoming
    type: core.webhook
tasks:
  - id: echo
    type: core.return
    value: "{{{{ inputs.message }}}}"
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

                listed_flows = await client.get(
                    "/api/v1/flows",
                    headers={"authorization": "Bearer test-token"},
                )
                assert any(
                    item["namespace"] == namespace and item["flow_id"] == flow_id
                    for item in listed_flows.json()
                )

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
                assert created_payload["taskRuns"][0]["result"] == {"value": "manual"}

                fetched = await client.get(
                    f"/api/v1/executions/{execution_id}",
                    headers={"authorization": "Bearer test-token"},
                )
                assert fetched.status_code == 200
                logs = await client.get(
                    f"/api/v1/executions/{execution_id}/logs",
                    headers={"authorization": "Bearer test-token"},
                )
                assert logs.json()[0]["output"] == {"value": "manual"}

                webhook = await client.post(
                    f"/api/v1/webhooks/{namespace}/{flow_id}/incoming",
                    headers={"authorization": "Bearer test-token"},
                    json={"message": "webhook"},
                )
                assert webhook.status_code == 200
                webhook_payload = webhook.json()
                execution_ids.append(UUID(webhook_payload["execution"]["execution_id"]))
                assert webhook_payload["taskRuns"][0]["result"] == {"value": "webhook"}

                executions = await client.get(
                    "/api/v1/executions",
                    headers={"authorization": "Bearer test-token"},
                )
                assert executions.status_code == 200
                returned_ids = {UUID(item["execution_id"]) for item in executions.json()}
                assert set(execution_ids) <= returned_ids
        finally:
            app.dependency_overrides.clear()
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
