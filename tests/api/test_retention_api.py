from __future__ import annotations

import asyncio
import os

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresRetentionRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_retention_repository,
    get_retention_service,
    get_settings,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings
from amesh.retention import RetentionService
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class EmptyObjectStore:
    async def delete(self, tenant_id: str, uri: str) -> None:
        raise AssertionError(f"unexpected object deletion for {tenant_id}: {uri}")


def test_lifecycle_api_requires_preview_and_exact_destructive_confirmation(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresRetentionRepository(engine)
            service = RetentionService(repository, EmptyObjectStore())  # type: ignore[arg-type]
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            app.dependency_overrides[get_tenant_service] = lambda: TenantService(
                PostgresTenantRepository(engine)
            )
            app.dependency_overrides[get_retention_repository] = lambda: repository
            app.dependency_overrides[get_retention_service] = lambda: service
            app.dependency_overrides[get_settings] = lambda: Settings(
                _env_file=None,
                database_url=migrated_test_database_url,
                amesh_admin_token="test-token",
            )
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://amesh.test"
            ) as client:
                assert (await client.get("/api/v1/lifecycle/policies")).status_code == 401
                headers = {"authorization": "Bearer test-token"}
                created = await client.post(
                    "/api/v1/lifecycle/policies",
                    headers=headers,
                    json={
                        "resourceType": "LOG",
                        "scope": "TENANT",
                        "retentionDays": 30,
                        "batchSize": 50,
                        "scheduleIntervalMinutes": 60,
                        "reason": "retain task logs for thirty days",
                    },
                )
                assert created.status_code == 201, created.text
                policy = created.json()
                assert policy["nextRunAt"] is not None

                update_payload = {
                    "resourceType": "LOG",
                    "scope": "TENANT",
                    "retentionDays": 31,
                    "batchSize": 50,
                    "scheduleIntervalMinutes": 60,
                    "reason": "extend task log retention by one day",
                }
                updated = await client.put(
                    f"/api/v1/lifecycle/policies/{policy['id']}",
                    headers=headers,
                    params={"expectedVersion": policy["version"]},
                    json=update_payload,
                )
                assert updated.status_code == 200, updated.text
                assert updated.json()["version"] == policy["version"] + 1

                stale = await client.put(
                    f"/api/v1/lifecycle/policies/{policy['id']}",
                    headers=headers,
                    params={"expectedVersion": policy["version"]},
                    json=update_payload,
                )
                assert stale.status_code == 409, stale.text

                previewed = await client.post(
                    "/api/v1/lifecycle/previews",
                    headers=headers,
                    json={"policyId": policy["id"], "reason": "manual empty purge preview"},
                )
                assert previewed.status_code == 201, previewed.text
                preview = previewed.json()
                assert preview["estimatedRecords"] == 0
                assert preview["confirmationPhrase"] == "PURGE 0"

                rejected = await client.post(
                    f"/api/v1/lifecycle/jobs/{preview['id']}/execute",
                    headers=headers,
                    json={"confirmation": "PURGE"},
                )
                assert rejected.status_code == 409
                completed = await client.post(
                    f"/api/v1/lifecycle/jobs/{preview['id']}/execute",
                    headers=headers,
                    json={"confirmation": preview["confirmationPhrase"]},
                )
                assert completed.status_code == 200, completed.text
                assert completed.json()["state"] == "SUCCEEDED"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
