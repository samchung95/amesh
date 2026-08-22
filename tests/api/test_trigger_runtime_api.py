from __future__ import annotations

import asyncio
import os
from pathlib import Path

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_repository,
    get_settings,
    get_task_cache_repository,
    get_tenant_service,
    get_trigger_runtime_repository,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings
from amesh.dsl import FlowDefinition
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_trigger_health_pause_webhook_deduplication_and_replay_api() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        repository = PostgresExecutionRepository(engine)
        trigger_runtime = PostgresTriggerRuntimeRepository(engine)
        flow = FlowDefinition.model_validate(
            {
                "id": "webhook-api",
                "namespace": "tests.trigger-api",
                "inputs": [{"id": "message", "type": "STRING"}],
                "tasks": [
                    {
                        "id": "echo",
                        "type": "core.return",
                        "value": "{{ inputs.message }}",
                    }
                ],
                "triggers": [
                    {
                        "id": "incoming",
                        "type": "core.webhook",
                        "retryDelay": "PT1S",
                    }
                ],
            }
        )
        try:
            await repository.apply_flow(flow, tenant_id="default")
            app.dependency_overrides[get_repository] = lambda: repository
            app.dependency_overrides[get_task_cache_repository] = lambda: (
                PostgresTaskCacheRepository(engine)
            )
            app.dependency_overrides[get_trigger_runtime_repository] = lambda: trigger_runtime
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            app.dependency_overrides[get_tenant_service] = lambda: TenantService(
                PostgresTenantRepository(engine)
            )
            app.dependency_overrides[get_settings] = lambda: Settings(
                _env_file=None,
                database_url=database.database_url,
                amesh_admin_token="test-token",
            )
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                assert (await client.get("/api/v1/triggers")).status_code == 401
                headers = {"authorization": "Bearer test-token"}

                listed = await client.get("/api/v1/triggers", headers=headers)
                assert listed.status_code == 200
                assert listed.json()[0]["last_decision"] == "trigger revision activated"

                paused = await client.post(
                    "/api/v1/triggers/tests.trigger-api/webhook-api/incoming/pause",
                    headers=headers,
                    json={"reason": "API maintenance"},
                )
                assert paused.status_code == 200
                assert paused.json()["paused"] is True

                deferred = await client.post(
                    "/api/v1/webhooks/tests.trigger-api/webhook-api/incoming",
                    headers={**headers, "X-Event-Id": "event-paused"},
                    json={"message": "wait"},
                )
                assert deferred.status_code == 429

                resumed = await client.post(
                    "/api/v1/triggers/tests.trigger-api/webhook-api/incoming/resume",
                    headers=headers,
                    json={"reason": "API maintenance complete"},
                )
                assert resumed.status_code == 200
                assert resumed.json()["paused"] is False

                event_headers = {**headers, "X-Event-Id": "event-accepted"}
                first = await client.post(
                    "/api/v1/webhooks/tests.trigger-api/webhook-api/incoming",
                    headers=event_headers,
                    json={"message": "run"},
                )
                assert first.status_code == 200
                first_execution_id = first.json()["execution"]["execution_id"]
                duplicate = await client.post(
                    "/api/v1/webhooks/tests.trigger-api/webhook-api/incoming",
                    headers=event_headers,
                    json={"message": "run"},
                )
                assert duplicate.status_code == 200
                assert duplicate.json()["execution"]["execution_id"] == first_execution_id

                occurrences = await client.get(
                    "/api/v1/trigger-occurrences?flowId=webhook-api",
                    headers=headers,
                )
                assert occurrences.status_code == 200
                succeeded = next(
                    item for item in occurrences.json() if item["state"] == "SUCCEEDED"
                )
                assert succeeded["evidence"]["reason"] == (
                    "webhook occurrence created an execution"
                )

                replayed = await client.post(
                    f"/api/v1/trigger-occurrences/{succeeded['occurrence_id']}/replay",
                    headers=headers,
                    json={"reason": "API acceptance replay"},
                )
                assert replayed.status_code == 200
                assert replayed.json()["replay_of"] == succeeded["occurrence_id"]
                assert replayed.json()["state"] == "ACCEPTED"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
