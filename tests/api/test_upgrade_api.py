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
    PostgresUpgradeRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_settings,
    get_upgrade_repository,
    get_upgrade_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings
from amesh.domain import AuthorizationDecision, AuthorizationRequest
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.plugin_sdk import PluginCatalogManager
from amesh.storage import StorageValidationReport
from amesh.upgrade import UpgradeService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
PRE_ADMIN_BOUNDARY = "0074_agent_session_policy_ceiling_mode.sql"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class EmptyObjectStore:
    async def validate_inventory(
        self,
        tenant_id: str,
        *,
        verify_content: bool = True,
    ) -> StorageValidationReport:
        del tenant_id, verify_content
        return StorageValidationReport(backend="test", objects=0, bytes=0, verified=0)


class AllowInstanceManageAuthorization:
    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        assert request.resource_type == "instance"
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="upgrade API regression fixture",
            policy_version=1,
        )


def test_upgrade_preflight_before_admin_grants_returns_operator_code() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            applied = await apply_migrations(
                database.database_url,
                MIGRATIONS,
                target_version=PRE_ADMIN_BOUNDARY,
            )
            assert applied[-1] == PRE_ADMIN_BOUNDARY
            repository = PostgresUpgradeRepository(engine)
            service = UpgradeService(
                repository,
                PostgresServiceRegistryRepository(engine),
                PluginCatalogManager(),
                EmptyObjectStore(),  # type: ignore[arg-type]
            )
            app.dependency_overrides[get_authorization_service] = AllowInstanceManageAuthorization
            app.dependency_overrides[get_upgrade_repository] = lambda: repository
            app.dependency_overrides[get_upgrade_service] = lambda: service
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
                response = await client.post(
                    "/api/v1/upgrades/preflight",
                    headers={"authorization": "Bearer test-token"},
                    json={"fromVersion": "0.1.0", "toVersion": "0.2.0"},
                )

            assert response.status_code == 409
            problem = response.json()
            assert problem["code"] == "HTTP_409"
            assert "UPGRADE_SCHEMA_MIGRATION_REQUIRED" in problem["detail"]
            assert "0075_restricted_repository_roles.sql" in problem["detail"]
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_upgrade_api_reports_policy_gates_and_explicit_migrations(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresUpgradeRepository(engine)
            current_head = (await repository.inventory()).applied_migrations[-1]
            service = UpgradeService(
                repository,
                PostgresServiceRegistryRepository(engine),
                PluginCatalogManager(),
                EmptyObjectStore(),  # type: ignore[arg-type]
            )
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            app.dependency_overrides[get_upgrade_repository] = lambda: repository
            app.dependency_overrides[get_upgrade_service] = lambda: service
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
                assert (await client.get("/api/v1/upgrades/policy")).status_code == 401
                headers = {"authorization": "Bearer test-token"}

                policy_response = await client.get(
                    "/api/v1/upgrades/policy",
                    headers=headers,
                )
                assert policy_response.status_code == 200, policy_response.text
                policy = policy_response.json()
                assert policy["currentVersion"] == "0.2.0"
                assert [release["version"] for release in policy["releases"]] == [
                    "0.1.0",
                    "0.2.0",
                ]

                versions = {"fromVersion": "0.1.0", "toVersion": "0.2.0"}
                preflight = await client.post(
                    "/api/v1/upgrades/preflight",
                    headers=headers,
                    json=versions,
                )
                assert preflight.status_code == 200, preflight.text
                preflight_report = preflight.json()
                assert preflight_report["safeToProceed"] is False
                assert len(preflight_report["rollingPlan"]) == 6
                schema_check = next(
                    check
                    for check in preflight_report["checks"]
                    if check["name"] == "schema-and-checksums"
                )
                assert schema_check["status"] == "BLOCKED"
                assert schema_check["evidence"]["latestMigration"] == current_head

                postflight = await client.post(
                    "/api/v1/upgrades/postflight",
                    headers=headers,
                    json=versions,
                )
                assert postflight.status_code == 200, postflight.text
                postflight_report = postflight.json()
                assert postflight_report["safeToProceed"] is False
                postflight_schema = next(
                    check
                    for check in postflight_report["checks"]
                    if check["name"] == "schema-and-checksums"
                )
                assert postflight_schema["status"] == "BLOCKED"
                assert postflight_schema["evidence"]["latestMigration"] == current_head

                preview_response = await client.get(
                    "/api/v1/upgrades/events/upcast",
                    headers=headers,
                )
                assert preview_response.status_code == 200
                preview = preview_response.json()
                assert preview["confirmationPhrase"] == "UPCAST 0"
                rejected = await client.post(
                    "/api/v1/upgrades/events/upcast",
                    headers=headers,
                    json={"confirmation": "UPCAST", "reason": "invalid confirmation"},
                )
                assert rejected.status_code == 409
                applied = await client.post(
                    "/api/v1/upgrades/events/upcast",
                    headers=headers,
                    json={
                        "confirmation": preview["confirmationPhrase"],
                        "reason": "verify explicit upgrade migration",
                    },
                )
                assert applied.status_code == 200, applied.text
                assert applied.json()["applied"] is True

                migrated = await client.post(
                    "/api/v1/upgrades/configuration/migrate",
                    headers=headers,
                    json={
                        "kind": "flow",
                        "targetVersion": "0.2.0",
                        "document": {
                            "id": "upgrade",
                            "namespace": "tests.upgrade",
                            "tasks": [{"id": "return", "type": "core.return", "value": "ok"}],
                        },
                    },
                )
                assert migrated.status_code == 200, migrated.text
                assert migrated.json()["canonical"]["id"] == "upgrade"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
