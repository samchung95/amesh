from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresReconciliationRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_reconciliation_service,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.reconciliation import ReconciliationService
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_tenant_administrator_can_run_and_inspect_reconciliation(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            app.dependency_overrides[get_tenant_service] = lambda: TenantService(
                PostgresTenantRepository(engine)
            )
            app.dependency_overrides[get_reconciliation_service] = lambda: ReconciliationService(
                PostgresReconciliationRepository(engine)
            )
            app.dependency_overrides[get_settings] = lambda: Settings(
                _env_file=None,
                database_url=migrated_test_database_url,
                amesh_admin_token="test-token",
            )
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                payload = {
                    "mode": "DRY_RUN",
                    "idempotencyKey": f"api-{uuid4()}",
                    "reason": "operator inspection",
                }
                unauthorized = await client.post("/api/v1/reconciliations", json=payload)
                assert unauthorized.status_code == 401

                headers = {"authorization": "Bearer test-token"}
                created = await client.post(
                    "/api/v1/reconciliations",
                    headers=headers,
                    json=payload,
                )
                assert created.status_code == 201
                run_id = created.json()["id"]
                assert created.json()["state"] == "COMPLETED"

                listed = await client.get("/api/v1/reconciliations", headers=headers)
                assert listed.status_code == 200
                assert listed.json()[0]["id"] == run_id

                fetched = await client.get(
                    f"/api/v1/reconciliations/{run_id}",
                    headers=headers,
                )
                assert fetched.status_code == 200
                assert fetched.json() == created.json()

                missing = await client.get(
                    f"/api/v1/reconciliations/{uuid4()}",
                    headers=headers,
                )
                assert missing.status_code == 404
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
