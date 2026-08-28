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
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_repository,
    get_authorization_service,
    get_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.domain import ActorContext, PrincipalType
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def _cleanup(engine: AsyncEngine, tenant_ids: list[UUID], actor_id: str) -> None:
    if not tenant_ids:
        return
    parameters = {"tenant_ids": tenant_ids}
    async with engine.begin() as connection:
        for table in (
            "task_attempts",
            "task_runs",
            "execution_events",
            "executions",
        ):
            await connection.execute(
                text(f"DELETE FROM {table} WHERE tenant_id = ANY(CAST(:tenant_ids AS uuid[]))"),
                parameters,
            )
        await connection.execute(
            text(
                "UPDATE flows SET active_revision = NULL "
                "WHERE tenant_id = ANY(CAST(:tenant_ids AS uuid[]))"
            ),
            parameters,
        )
        for table in ("flow_revisions", "flows", "namespaces", "tenant_exports"):
            await connection.execute(
                text(f"DELETE FROM {table} WHERE tenant_id = ANY(CAST(:tenant_ids AS uuid[]))"),
                parameters,
            )
        await connection.execute(
            text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
            {"actor_id": actor_id},
        )
        await connection.execute(
            text("DELETE FROM tenants WHERE id = ANY(CAST(:tenant_ids AS uuid[]))"),
            parameters,
        )


def test_multi_tenant_api_lifecycle_and_resource_isolation() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        execution_repository = PostgresExecutionRepository(engine)
        tenant_repository = PostgresTenantRepository(engine)
        tenant_service = TenantService(tenant_repository)
        authorization_repository = PostgresAuthorizationRepository(engine)
        authorization_service = AuthorizationService(authorization_repository)
        suffix = uuid4().hex[:10]
        first_slug = f"api-a-{suffix}"
        second_slug = f"api-b-{suffix}"
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.SYSTEM,
            display="tenant-api-test-admin",
            bootstrap_admin=True,
        )
        actor_id = str(actor.principal_id)
        settings = Settings(
            database_url=TEST_DATABASE_URL,
            tenancy_mode="multi",
        )
        tenant_ids: list[UUID] = []
        app.dependency_overrides[authenticate_actor] = lambda: actor
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_repository] = lambda: execution_repository
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_authorization_repository] = lambda: authorization_repository
        app.dependency_overrides[get_authorization_service] = lambda: authorization_service
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                for slug, display, worker_group in (
                    (first_slug, "API tenant A", "regulated"),
                    (second_slug, "API tenant B", "general"),
                ):
                    response = await client.post(
                        "/api/v1/admin/tenants",
                        json={
                            "slug": slug,
                            "displayName": display,
                            "policy": {
                                "retention_days": 14,
                                "max_concurrent_executions": 3,
                                "max_storage_bytes": 4096,
                                "encryption_key_ref": f"kms://{slug}",
                                "identity_provider_refs": [f"oidc-{slug}"],
                                "plugin_allowlist": ["core.return"],
                                "feature_flags": {"executions": True},
                                "worker_groups": [worker_group],
                            },
                        },
                    )
                    assert response.status_code == 201, response.text
                    tenant_ids.append(UUID(response.json()["id"]))

                missing_context = await client.get("/api/v1/flows")
                assert missing_context.status_code == 400
                assert missing_context.json()["detail"] == "X-Amesh-Tenant header required"

                flow_yaml = (
                    "id: shared-flow\n"
                    "namespace: tests.tenancy\n"
                    "tasks:\n"
                    "  - id: done\n"
                    "    type: core.return\n"
                    "    value: ok\n"
                )
                first_apply = await client.put(
                    "/api/v1/flows",
                    content=flow_yaml,
                    headers={"X-Amesh-Tenant": first_slug},
                )
                assert first_apply.status_code == 200, first_apply.text
                assert first_apply.json()["tenant_id"] == first_slug
                empty_second = await client.get(
                    "/api/v1/flows",
                    headers={"X-Amesh-Tenant": second_slug},
                )
                assert empty_second.status_code == 200
                assert empty_second.json() == []

                second_apply = await client.put(
                    "/api/v1/flows",
                    content=flow_yaml,
                    headers={"X-Amesh-Tenant": second_slug},
                )
                assert second_apply.status_code == 200, second_apply.text
                assert second_apply.json()["tenant_id"] == second_slug
                for slug in (first_slug, second_slug):
                    listed = await client.get(
                        "/api/v1/flows",
                        headers={"X-Amesh-Tenant": slug},
                    )
                    assert listed.status_code == 200
                    assert [item["tenant_id"] for item in listed.json()] == [slug]

                missing_flow_errors = []
                for slug in (first_slug, second_slug):
                    missing = await client.post(
                        "/api/v1/executions",
                        headers={"X-Amesh-Tenant": slug},
                        json={
                            "namespace": "tests.tenancy",
                            "flowId": "not-present",
                        },
                    )
                    assert missing.status_code == 404
                    missing_flow_errors.append(missing.json())
                assert missing_flow_errors[0] == missing_flow_errors[1]

                suspended = await client.post(f"/api/v1/admin/tenants/{first_slug}/suspend")
                assert suspended.status_code == 200
                assert suspended.json()["status"] == "SUSPENDED"
                unavailable = await client.get(
                    "/api/v1/flows",
                    headers={"X-Amesh-Tenant": first_slug},
                )
                assert unavailable.status_code == 404
                assert unavailable.json()["detail"] == "tenant unavailable"
                assert (
                    await client.post(f"/api/v1/admin/tenants/{first_slug}/restore")
                ).status_code == 200

                exported = await client.post(f"/api/v1/admin/tenants/{first_slug}/exports")
                assert exported.status_code == 201
                assert exported.json()["tenant"]["slug"] == first_slug
                deleted = await client.delete(f"/api/v1/admin/tenants/{first_slug}")
                assert deleted.status_code == 200
                assert deleted.json()["status"] == "TOMBSTONED"
                restored = await client.post(f"/api/v1/admin/tenants/{first_slug}/restore")
                assert restored.status_code == 200
                assert restored.json()["status"] == "ACTIVE"

                listed_tenants = await client.get("/api/v1/admin/tenants")
                assert listed_tenants.status_code == 200
                listed_slugs = {item["slug"] for item in listed_tenants.json()}
                assert {first_slug, second_slug} <= listed_slugs
                assert "amesh-system" not in listed_slugs

                metrics = await client.get("/metrics")
                assert metrics.status_code == 200
                assert first_slug not in metrics.text
                assert second_slug not in metrics.text

            async with engine.connect() as connection:
                audit_rows = (
                    (
                        await connection.execute(
                            text(
                                "SELECT tenant_id, evidence FROM audit_events "
                                "WHERE actor_id = :actor_id AND action LIKE 'tenant.%'"
                            ),
                            {"actor_id": actor_id},
                        )
                    )
                    .mappings()
                    .all()
                )
            assert audit_rows
            assert all(UUID(str(row["tenant_id"])) in tenant_ids for row in audit_rows)
            assert all(row["evidence"]["superAdmin"] is True for row in audit_rows)
        finally:
            app.dependency_overrides.clear()
            await _cleanup(engine, tenant_ids, actor_id)
            await engine.dispose()

    asyncio.run(scenario())
