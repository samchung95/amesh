from __future__ import annotations

import asyncio
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import create_async_engine

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


def test_failed_synchronous_run_returns_the_failed_execution(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        await repository.apply_flow(
            FlowDefinition.model_validate(
                {
                    "id": "nightly_inventory_sync",
                    "namespace": "tests.launch",
                    "tasks": [
                        {"id": "load", "type": "core.fail", "message": "export exited 2"},
                        {
                            "id": "publish",
                            "type": "core.return",
                            "value": "never",
                            "dependsOn": ["load"],
                        },
                    ],
                }
            ),
            tenant_id="default",
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
            PostgresAuthorizationRepository(engine)
        )
        app.dependency_overrides[get_tenant_service] = lambda: TenantService(
            PostgresTenantRepository(engine)
        )
        app.dependency_overrides[get_settings] = lambda: Settings(
            _env_file=None,
            database_url=migrated_test_database_url,
            amesh_admin_token="test-token",
        )
        try:
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
                base_url="http://amesh.test",
            ) as client:
                launched = await client.post(
                    "/api/v1/executions/tests.launch/nightly_inventory_sync",
                    headers={"authorization": "Bearer test-token"},
                    json={},
                )
            assert launched.status_code == 200, launched.text
            execution = launched.json()["execution"]
            assert execution["state"] == "FAILED"
            stored = await repository.get_execution(
                UUID(execution["execution_id"]), tenant_id="default"
            )
            assert stored.state.value == "FAILED"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
