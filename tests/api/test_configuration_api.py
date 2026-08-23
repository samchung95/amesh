from __future__ import annotations

import asyncio
import os
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresFeatureFlagRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_configuration_manager,
    get_feature_flag_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import ConfigurationManager, get_settings, load_configuration
from amesh.domain import (
    ActorContext,
    FeatureFlag,
    FeatureFlagScope,
    PrincipalType,
    TenantDefinition,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_administrator_configuration_reload_diagnostics_and_scoped_flags(tmp_path: Path) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        try:
            await apply_migrations(database.database_url, migration_directory())
            tenant_repository = PostgresTenantRepository(engine)
            tenant_service = TenantService(tenant_repository)
            feature_repository = PostgresFeatureFlagRepository(engine)
            for slug in ("config-alpha", "config-beta"):
                await tenant_repository.create(
                    TenantDefinition(slug=slug, display_name=slug),
                    actor_id="configuration-api-test",
                )
            await feature_repository.upsert(
                FeatureFlag(
                    key="beta-only",
                    scope=FeatureFlagScope.TENANT,
                    tenant_id="config-beta",
                    enabled=True,
                    updated_by="configuration-api-test",
                ),
                actor_id="configuration-api-test",
            )

            secret_directory = tmp_path / "secrets"
            secret_directory.mkdir()
            (secret_directory / "pepper").write_text(
                "configuration-canary-secret",
                encoding="utf-8",
            )
            common_environment = {
                "DATABASE_URL": database.database_url,
                "TENANCY_MODE": "multi",
                "AMESH_SECRETS_DIR": str(secret_directory),
                "AMESH_TOKEN_PEPPER": "secret://pepper",
            }
            candidates = [
                load_configuration(environment={**common_environment, "LOG_LEVEL": "INFO"}),
                load_configuration(environment={**common_environment, "LOG_LEVEL": "DEBUG"}),
            ]
            manager = ConfigurationManager(lambda: candidates.pop(0))
            actor = ActorContext(
                principal_id=uuid4(),
                principal_type=PrincipalType.SYSTEM,
                display="configuration-api-admin",
                bootstrap_admin=True,
            )
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_settings] = lambda: manager.settings
            app.dependency_overrides[get_configuration_manager] = lambda: manager
            app.dependency_overrides[get_tenant_service] = lambda: tenant_service
            app.dependency_overrides[get_feature_flag_repository] = lambda: feature_repository
            app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
                PostgresAuthorizationRepository(engine)
            )
            transport = httpx.ASGITransport(app=app)
            headers = {"X-Amesh-Tenant": "config-alpha"}
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                configuration = await client.get("/api/v1/configuration")
                assert configuration.status_code == 200, configuration.text
                assert "configuration-canary-secret" not in configuration.text
                entries = {entry["name"]: entry for entry in configuration.json()["entries"]}
                assert entries["amesh_token_pepper"]["value"] == "[REDACTED]"
                assert entries["amesh_token_pepper"]["source"].startswith("environment+secret:")

                reloaded = await client.post("/api/v1/configuration/reload")
                assert reloaded.status_code == 200, reloaded.text
                assert reloaded.json()["version"] == 2
                reloaded_entries = {entry["name"]: entry for entry in reloaded.json()["entries"]}
                assert reloaded_entries["log_level"]["value"] == "DEBUG"

                instance = await client.put(
                    "/api/v1/feature-flags/new-engine",
                    headers=headers,
                    json={"scope": "INSTANCE", "enabled": False},
                )
                assert instance.status_code == 200, instance.text
                namespace = await client.put(
                    "/api/v1/feature-flags/new-engine",
                    headers=headers,
                    json={
                        "scope": "NAMESPACE",
                        "namespace": "finance.payments",
                        "enabled": True,
                    },
                )
                assert namespace.status_code == 200, namespace.text
                decision = await client.get(
                    "/api/v1/feature-flags/new-engine/evaluate",
                    headers=headers,
                    params={"namespace": "finance.payments"},
                )
                assert decision.status_code == 200, decision.text
                assert (decision.json()["enabled"], decision.json()["reason"]) == (
                    True,
                    "NAMESPACE_MATCH",
                )

                diagnostics = await client.get(
                    "/api/v1/configuration/diagnostics",
                    headers=headers,
                    params={"namespace": "finance.payments"},
                )
                assert diagnostics.status_code == 200, diagnostics.text
                assert diagnostics.json()["tenantId"] == "config-alpha"
                assert "configuration-canary-secret" not in diagnostics.text
                assert "beta-only" not in diagnostics.text
                assert "new-engine" in diagnostics.text

                reserved = await client.put(
                    "/api/v1/feature-flags/admin-execution-kill-switch",
                    headers=headers,
                    json={"scope": "TENANT", "enabled": True},
                )
                assert reserved.status_code == 409, reserved.text

                draft = {
                    "key": "KILL_SWITCH",
                    "enabled": True,
                    "value": None,
                    "reason": "integration incident exercise",
                    "expectedVersion": None,
                }
                preview = await client.post(
                    "/api/v1/admin/controls/preview",
                    headers=headers,
                    json=draft,
                )
                assert preview.status_code == 200, preview.text
                rejected = await client.put(
                    "/api/v1/admin/controls/KILL_SWITCH",
                    headers=headers,
                    json={
                        "draft": draft,
                        "approval": preview.json()["approval"],
                        "confirmation": "WRONG",
                    },
                )
                assert rejected.status_code == 409, rejected.text
                applied = await client.put(
                    "/api/v1/admin/controls/KILL_SWITCH",
                    headers=headers,
                    json={
                        "draft": draft,
                        "approval": preview.json()["approval"],
                        "confirmation": preview.json()["confirmation"],
                    },
                )
                assert applied.status_code == 200, applied.text
                assert applied.json()["enabled"] is True
                controls = await client.get("/api/v1/admin/controls", headers=headers)
                assert controls.status_code == 200, controls.text
                assert next(
                    item for item in controls.json() if item["key"] == "KILL_SWITCH"
                )["enabled"] is True
                audit = await client.get("/api/v1/admin/audit", headers=headers)
                assert audit.status_code == 200, audit.text
                assert [entry["outcome"] for entry in audit.json()[:2]] == [
                    "SUCCESS",
                    "REJECTED",
                ]
                beta_audit = await client.get(
                    "/api/v1/admin/audit",
                    headers={"X-Amesh-Tenant": "config-beta"},
                )
                assert beta_audit.status_code == 200, beta_audit.text
                assert beta_audit.json() == []
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
