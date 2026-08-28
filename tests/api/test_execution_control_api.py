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
from amesh.dsl import FlowDefinition
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


def test_execution_intervention_preview_apply_and_history_api() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        authorization_service = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenant_service = TenantService(PostgresTenantRepository(engine))
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_settings] = lambda: Settings(
            database_url=TEST_DATABASE_URL,
            amesh_admin_token="test-token",
        )
        flow = FlowDefinition.model_validate(
            {
                "id": "control_api",
                "namespace": f"tests.control.api.{uuid4().hex}",
                "tasks": [{"id": "one", "type": "core.return", "value": "ok"}],
            }
        )
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        transport = httpx.ASGITransport(app=app)
        headers = {"authorization": "Bearer test-token"}
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                unauthorized = await client.post(
                    f"/api/v1/executions/{execution.execution_id}/interventions/preview",
                    json={"action": "PAUSE"},
                )
                assert unauthorized.status_code == 401

                preview = await client.post(
                    f"/api/v1/executions/{execution.execution_id}/interventions/preview",
                    headers=headers,
                    json={"action": "PAUSE"},
                )
                assert preview.status_code == 200
                prediction = preview.json()
                assert prediction["current_state"] == "RUNNING"
                assert prediction["predicted_state"] == "PAUSED"
                assert prediction["impacted_task_ids"] == ["one"]
                assert prediction["consequences"]

                applied = await client.post(
                    f"/api/v1/executions/{execution.execution_id}/interventions",
                    headers=headers,
                    json={
                        "action": "PAUSE",
                        "expectedVersion": prediction["current_version"],
                        "expectedEpoch": prediction["current_epoch"],
                        "reason": "inspect task inputs",
                    },
                )
                assert applied.status_code == 200
                assert applied.json()["execution"]["state"] == "PAUSED"

                stale = await client.post(
                    f"/api/v1/executions/{execution.execution_id}/interventions",
                    headers=headers,
                    json={
                        "action": "RESUME",
                        "expectedVersion": prediction["current_version"],
                        "expectedEpoch": prediction["current_epoch"],
                        "reason": "stale preview must fail",
                    },
                )
                assert stale.status_code == 409

                history = await client.get(
                    f"/api/v1/executions/{execution.execution_id}/interventions",
                    headers=headers,
                )
                assert history.status_code == 200
                assert history.json()[0]["action"] == "PAUSE"
                assert history.json()[0]["reason"] == "inspect task inputs"
        finally:
            app.dependency_overrides.clear()
            await cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())
