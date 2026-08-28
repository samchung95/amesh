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


async def _cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :key"),
            {"key": f"execution:{execution_id}"},
        )
        await connection.execute(
            text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
            {"execution_id": execution_id},
        )
        for table in ("execution_logs", "execution_metrics"):
            await connection.execute(
                text(f"DELETE FROM {table} WHERE execution_id = :execution_id"),
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


def test_authenticated_task_resume_api_enforces_contract_limits() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        authorization = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenancy = TenantService(PostgresTenantRepository(engine))
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization
        app.dependency_overrides[get_tenant_service] = lambda: tenancy
        app.dependency_overrides[get_settings] = lambda: Settings(
            database_url=TEST_DATABASE_URL,
            amesh_admin_token="test-token",
        )
        flow = FlowDefinition.model_validate(
            {
                "id": "resume_api",
                "namespace": f"tests.resume.api.{uuid4().hex}",
                "tasks": [
                    {
                        "id": "callback",
                        "type": "test.defer",
                        "contract": {"resourceLimits": {"maxOutputBytes": 32}},
                    }
                ],
            }
        )
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        task_run = (await repository.list_task_runs(execution.execution_id, tenant_id="default"))[0]
        running = await repository.start_task(task_run.task_run_id, tenant_id="default")
        token = "api-resume-token-with-at-least-sixteen-characters"
        await repository.defer_task(
            running.task_run_id,
            running.current_attempt,
            token,
            tenant_id="default",
            metadata={},
        )
        path = f"/api/v1/executions/{execution.execution_id}/task-runs/{running.task_run_id}/resume"
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport, base_url="http://amesh.test"
            ) as client:
                unauthorized = await client.post(
                    path,
                    json={"resumeToken": token, "completion": {"output": {"ok": True}}},
                )
                assert unauthorized.status_code == 401

                oversized = await client.post(
                    path,
                    headers={"authorization": "Bearer test-token"},
                    json={
                        "resumeToken": token,
                        "completion": {"output": {"value": "x" * 64}},
                    },
                )
                assert oversized.status_code == 409
                assert "configured limit" in oversized.json()["detail"]

                resumed = await client.post(
                    path,
                    headers={"authorization": "Bearer test-token"},
                    json={
                        "resumeToken": token,
                        "completion": {
                            "output": {"ok": True},
                            "logs": [{"level": "INFO", "message": "resumed"}],
                            "exit": {"status": "SUCCESS", "code": 0},
                        },
                    },
                )
                assert resumed.status_code == 200
                payload = resumed.json()
                assert payload["state"] == "SUCCESS"
                assert payload["result"] == {"ok": True}
                assert payload["evidence"]["logs"][0]["message"] == "resumed"
        finally:
            app.dependency_overrides.clear()
            await _cleanup_execution(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())
