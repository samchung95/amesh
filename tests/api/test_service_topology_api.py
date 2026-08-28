from __future__ import annotations

import asyncio
import os
from pathlib import Path

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresServiceRegistryRepository,
)
from amesh.app import app, get_authorization_service, get_service_registry_repository
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.domain import ServiceRegistration, ServiceRole, new_runtime_id
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_instance_administrator_can_inspect_and_drain_service_topology() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            repository = PostgresServiceRegistryRepository(engine)
            registered = await repository.register(
                ServiceRegistration(
                    id=new_runtime_id(),
                    role=ServiceRole.EXECUTOR,
                    instanceName="executor-api-test",
                    version="0.2.0",
                    failureZone="zone-a",
                )
            )
            registered = await repository.heartbeat(
                registered.instance_id,
                registered.generation,
            )
            app.dependency_overrides[get_service_registry_repository] = lambda: repository
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
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
                assert (await client.get("/api/v1/operations/topology")).status_code == 401
                headers = {"authorization": "Bearer test-token"}
                topology = await client.get("/api/v1/operations/topology", headers=headers)
                assert topology.status_code == 200
                assert topology.json()["instances"][0]["instanceName"] == "executor-api-test"

                drained = await client.post(
                    f"/api/v1/operations/services/{registered.instance_id}/drain",
                    headers=headers,
                    json={
                        "expectedVersion": registered.resource_version,
                        "reason": "rolling deployment",
                    },
                )
                assert drained.status_code == 200
                assert drained.json()["state"] == "DRAINING"

                stale = await client.post(
                    f"/api/v1/operations/services/{registered.instance_id}/drain",
                    headers=headers,
                    json={
                        "expectedVersion": registered.resource_version,
                        "reason": "stale deployment action",
                    },
                )
                assert stale.status_code == 409
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
