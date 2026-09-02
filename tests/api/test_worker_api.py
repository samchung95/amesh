from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresTenantRepository,
    PostgresWorkerRepository,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_repository,
    get_authorization_service,
    get_tenant_service,
    get_worker_repository,
)
from amesh.authorization import AuthorizationService
from amesh.domain import ActorContext, PrincipalType
from amesh.ports import WorkerRegistration
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_worker_inventory_and_fenced_drain_api() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        workers = PostgresWorkerRepository(engine)
        authorization_repository = PostgresAuthorizationRepository(engine)
        authorization_service = AuthorizationService(authorization_repository)
        tenant_service = TenantService(PostgresTenantRepository(engine))
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.SYSTEM,
            display="worker-api-test",
            bootstrap_admin=True,
        )
        group = f"api-worker-{uuid4().hex}"
        worker = await workers.register_worker(
            WorkerRegistration(
                worker_id=uuid4(),
                worker_group=group,
                instance_name="one",
                version="1.0.0",
                capabilities=("core.return",),
                runner_types=("local",),
                capacity=2,
            ),
            tenant_id="default",
            actor_id="worker-api-test",
        )
        app.dependency_overrides[authenticate_actor] = lambda: actor
        app.dependency_overrides[get_authorization_repository] = lambda: authorization_repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        app.dependency_overrides[get_worker_repository] = lambda: workers
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                capabilities_response = await client.get("/api/v1/runners/capabilities")
                assert capabilities_response.status_code == 200
                capabilities = {item["runner"]: item for item in capabilities_response.json()}
                assert set(capabilities) == {"local", "kubernetes"}
                assert capabilities["local"]["requiresCommand"] is True
                assert capabilities["kubernetes"]["requiresImage"] is True
                assert capabilities["local"]["cancellationEscalation"] == [
                    "terminate",
                    "wait-grace",
                    "kill",
                ]

                inventory_response = await client.get("/api/v1/workers")
                assert inventory_response.status_code == 200
                listed = {item["worker_id"]: item for item in inventory_response.json()}
                assert listed[str(worker.worker_id)]["capacity"] == 2

                drain_response = await client.post(
                    f"/api/v1/workers/{worker.worker_id}/drain",
                    params={"expectedVersion": worker.resource_version},
                )
                assert drain_response.status_code == 200
                assert drain_response.json()["status"] == "DRAINING"

                stale_response = await client.post(
                    f"/api/v1/workers/{worker.worker_id}/drain",
                    params={"expectedVersion": worker.resource_version},
                )
                assert stale_response.status_code == 409
        finally:
            app.dependency_overrides.clear()
            async with engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM workers WHERE id = :worker_id"),
                    {"worker_id": worker.worker_id},
                )
            await engine.dispose()

    asyncio.run(scenario())
