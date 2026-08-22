from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
    PostgresWorkerRepository,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_repository,
    get_authorization_service,
    get_repository,
    get_tenant_service,
    get_worker_repository,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.domain import (
    ActorContext,
    AuthorizationScopeType,
    ExecutionEvent,
    ExecutionEventType,
    ExecutionSnapshot,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
    TenantDefinition,
)
from amesh.tenancy import TenantService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_every_protected_rest_surface_enforces_tenant_and_permission_policy() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        policy_repository = PostgresAuthorizationRepository(engine)
        execution_repository = PostgresExecutionRepository(engine)
        worker_repository = PostgresWorkerRepository(engine)
        tenant_repository = PostgresTenantRepository(engine)
        tenant_service = TenantService(tenant_repository)
        suffix = uuid4().hex[:12]
        cross_tenant_slug = f"authorization-cross-{suffix}"
        audit_actor = f"test:api-authorization:{suffix}"
        principal = PrincipalDefinition(
            principal_type=PrincipalType.USER,
            handle=f"api-viewer-{suffix}",
            display_name="API viewer",
        )
        binding = RoleBinding(
            principal_id=principal.id,
            principal_type=principal.principal_type,
            role_name="viewer",
            scope_type=AuthorizationScopeType.TENANT,
            tenant_id="default",
        )
        actor = ActorContext(
            principal_id=principal.id,
            principal_type=principal.principal_type,
            display=principal.handle,
        )
        await policy_repository.create_principal(principal, actor_id=audit_actor)
        await policy_repository.create_binding(binding, actor_id=audit_actor)
        cross_tenant_definition = await tenant_repository.create(
            TenantDefinition(
                slug=cross_tenant_slug,
                display_name="Authorization cross-tenant probe",
            ),
            actor_id=audit_actor,
        )
        service = AuthorizationService(policy_repository)
        app.dependency_overrides[authenticate_actor] = lambda: actor
        app.dependency_overrides[get_authorization_repository] = lambda: policy_repository
        app.dependency_overrides[get_authorization_service] = lambda: service
        app.dependency_overrides[get_repository] = lambda: execution_repository
        app.dependency_overrides[get_worker_repository] = lambda: worker_repository
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        missing_id = uuid4()
        snapshot = ExecutionSnapshot(
            execution_id=missing_id,
            tenant_id="default",
            namespace="tests.authorization",
            flow_id="missing",
            flow_revision=1,
        )
        event = ExecutionEvent(event_type=ExecutionEventType.QUEUED)
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                assert (await client.get("/health")).status_code == 200
                assert (await client.get("/ready")).status_code == 200
                assert (await client.get("/metrics")).status_code == 200
                validation = await client.post(
                    "/api/v1/flows/validate",
                    content="id: demo\nnamespace: tests\ntasks:\n  - id: one\n    type: core.return\n",
                )
                assert validation.status_code == 200

                assert (await client.get("/api/v1/flows")).status_code == 200
                assert (await client.get("/api/v1/workers")).status_code == 200
                cross_tenant_response = await client.get(
                    "/api/v1/flows",
                    headers={"X-Amesh-Tenant": cross_tenant_slug},
                )
                assert cross_tenant_response.status_code == 404
                assert cross_tenant_response.json()["detail"] == "tenant unavailable"
                missing_tenant = await client.get(
                    "/api/v1/flows",
                    headers={"X-Amesh-Tenant": f"missing-{suffix}"},
                )
                assert missing_tenant.status_code == 404
                assert missing_tenant.json() == cross_tenant_response.json()

                denied_requests = [
                    client.put(
                        "/api/v1/flows",
                        content=(
                            "id: denied\nnamespace: tests.authorization\n"
                            "tasks:\n  - id: one\n    type: core.return\n"
                        ),
                    ),
                    client.post(
                        "/api/v1/executions",
                        json={
                            "namespace": "tests.authorization",
                            "flowId": "missing",
                        },
                    ),
                    client.post(
                        "/api/v1/webhooks/tests.authorization/missing/incoming",
                        json={},
                    ),
                    client.post(
                        "/api/v1/executions/reduce",
                        json={
                            "snapshot": snapshot.model_dump(mode="json"),
                            "events": [event.model_dump(mode="json")],
                        },
                    ),
                    client.get("/api/v1/admin/principals"),
                    client.get("/api/v1/admin/tenants"),
                    client.get("/api/v1/admin/tenants/default"),
                    client.post(
                        "/api/v1/admin/tenants",
                        json={"slug": "denied-tenant", "displayName": "Denied tenant"},
                    ),
                    client.put(
                        "/api/v1/admin/tenants/default/policy",
                        json={},
                    ),
                    client.post("/api/v1/admin/tenants/default/suspend"),
                    client.delete("/api/v1/admin/tenants/default"),
                    client.post("/api/v1/admin/tenants/default/restore"),
                    client.post("/api/v1/admin/tenants/default/exports"),
                    client.get(f"/api/v1/admin/principals/{uuid4()}/credentials"),
                    client.post(
                        "/api/v1/admin/principals",
                        json={
                            "principal_type": "USER",
                            "handle": f"denied-{suffix}",
                            "display_name": "Denied user",
                        },
                    ),
                    client.put(f"/api/v1/admin/groups/{uuid4()}/members/{uuid4()}"),
                    client.delete(f"/api/v1/admin/groups/{uuid4()}/members/{uuid4()}"),
                    client.get("/api/v1/admin/roles"),
                    client.put(
                        f"/api/v1/admin/roles/denied-{suffix}",
                        json={
                            "name": f"denied-{suffix}",
                            "display_name": "Denied role",
                        },
                    ),
                    client.get("/api/v1/admin/bindings"),
                    client.post(
                        "/api/v1/admin/bindings",
                        json={
                            "principal_id": str(principal.id),
                            "principal_type": "USER",
                            "role_name": "viewer",
                            "scope_type": "TENANT",
                            "tenant_id": "default",
                        },
                    ),
                    client.delete(f"/api/v1/admin/bindings/{uuid4()}"),
                    client.put(
                        "/api/v1/admin/tenants/default/namespaces/tests/authorization-boundary"
                    ),
                    client.post(
                        f"/api/v1/admin/principals/{uuid4()}/credentials",
                        json={
                            "name": "denied",
                            "scopes": ["flow:view"],
                            "expiresAt": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
                        },
                    ),
                    client.post(
                        f"/api/v1/admin/credentials/{uuid4()}/rotate",
                        json={"overlapSeconds": 60},
                    ),
                    client.delete(f"/api/v1/admin/credentials/{uuid4()}"),
                    client.delete(f"/api/v1/admin/principals/{uuid4()}/credentials"),
                    client.put(
                        f"/api/v1/admin/principals/{uuid4()}/local-password",
                        json={"newPassword": "denied password material"},
                    ),
                    client.delete(f"/api/v1/admin/principals/{uuid4()}/sessions"),
                    client.post(
                        "/api/v1/credentials/exchange",
                        json={
                            "scopes": ["worker:view"],
                            "audience": "amesh-worker",
                            "expiresInSeconds": 300,
                        },
                    ),
                    client.post(
                        "/api/v1/authorization/explain",
                        json={
                            "principalId": str(principal.id),
                            "principalType": principal.principal_type.value,
                            "tenantId": "default",
                            "resourceType": "flow",
                            "action": "view",
                        },
                    ),
                    client.post(
                        f"/api/v1/workers/{uuid4()}/drain",
                        params={"expectedVersion": 1},
                    ),
                    client.get("/api/v1/operations/topology"),
                    client.post(
                        f"/api/v1/operations/services/{uuid4()}/drain",
                        json={"expectedVersion": 1, "reason": "denied"},
                    ),
                ]
                responses = await asyncio.gather(*denied_requests)
                assert all(response.status_code == 403 for response in responses)
                assert all(response.json()["detail"] == "not authorized" for response in responses)

                assert (await client.get("/api/v1/executions")).status_code == 200
                assert (await client.get(f"/api/v1/executions/{missing_id}")).status_code == 404
                assert (
                    await client.get(f"/api/v1/executions/{missing_id}/logs")
                ).status_code == 404
        finally:
            app.dependency_overrides.clear()
            async with engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM auth_principals WHERE id = :principal_id"),
                    {"principal_id": principal.id},
                )
                await connection.execute(
                    text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
                    {"actor_id": audit_actor},
                )
                await connection.execute(
                    text("DELETE FROM tenants WHERE id = :tenant_id"),
                    {"tenant_id": cross_tenant_definition.id},
                )
            await engine.dispose()

    asyncio.run(scenario())


def test_bootstrap_administrator_can_manage_and_explain_authorization() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresAuthorizationRepository(engine)
        service = AuthorizationService(repository)
        suffix = uuid4().hex[:12]
        namespace = f"tests.authorization.{suffix}"
        role_name = f"api-reader-{suffix}"
        settings = Settings(
            database_url=TEST_DATABASE_URL,
            app_env="development",
            auth_mode="development",
            amesh_admin_token="test-token",
        )
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_authorization_repository] = lambda: repository
        app.dependency_overrides[get_authorization_service] = lambda: service
        headers = {"authorization": "Bearer test-token"}
        created_ids: list[UUID] = []
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                user_response = await client.post(
                    "/api/v1/admin/principals",
                    headers=headers,
                    json={
                        "principal_type": "USER",
                        "handle": f"managed-user-{suffix}",
                        "display_name": "Managed user",
                    },
                )
                group_response = await client.post(
                    "/api/v1/admin/principals",
                    headers=headers,
                    json={
                        "principal_type": "GROUP",
                        "handle": f"managed-group-{suffix}",
                        "display_name": "Managed group",
                    },
                )
                assert user_response.status_code == 201
                assert group_response.status_code == 201
                user_id = UUID(user_response.json()["id"])
                group_id = UUID(group_response.json()["id"])
                created_ids.extend([user_id, group_id])

                membership = await client.put(
                    f"/api/v1/admin/groups/{group_id}/members/{user_id}",
                    headers=headers,
                )
                assert membership.status_code == 204

                role_response = await client.put(
                    f"/api/v1/admin/roles/{role_name}",
                    headers=headers,
                    json={
                        "name": role_name,
                        "display_name": "API reader",
                        "permissions": [{"resource_type": "flow", "action": "view"}],
                    },
                )
                assert role_response.status_code == 200

                binding_response = await client.post(
                    "/api/v1/admin/bindings",
                    headers=headers,
                    json={
                        "principal_id": str(group_id),
                        "principal_type": "GROUP",
                        "role_name": role_name,
                        "scope_type": "TENANT",
                        "tenant_id": "default",
                    },
                )
                assert binding_response.status_code == 201
                binding_id = UUID(binding_response.json()["id"])

                boundary = await client.put(
                    f"/api/v1/admin/tenants/default/namespaces/{namespace}/authorization-boundary",
                    headers=headers,
                )
                assert boundary.status_code == 200

                explanation = await client.post(
                    "/api/v1/authorization/explain",
                    headers=headers,
                    json={
                        "principalId": str(user_id),
                        "principalType": "USER",
                        "tenantId": "default",
                        "resourceType": "flow",
                        "action": "view",
                    },
                )
                assert explanation.status_code == 200
                assert explanation.json()["allowed"] is True
                assert explanation.json()["matched_role_names"] == [role_name]

                membership_removed = await client.delete(
                    f"/api/v1/admin/groups/{group_id}/members/{user_id}",
                    headers=headers,
                )
                assert membership_removed.status_code == 204
                revoked_explanation = await client.post(
                    "/api/v1/authorization/explain",
                    headers=headers,
                    json={
                        "principalId": str(user_id),
                        "principalType": "USER",
                        "tenantId": "default",
                        "resourceType": "flow",
                        "action": "view",
                    },
                )
                assert revoked_explanation.status_code == 200
                assert revoked_explanation.json()["allowed"] is False

                principals = await client.get("/api/v1/admin/principals", headers=headers)
                roles = await client.get("/api/v1/admin/roles", headers=headers)
                bindings = await client.get("/api/v1/admin/bindings", headers=headers)
                assert {item["id"] for item in principals.json()} >= {
                    str(user_id),
                    str(group_id),
                }
                assert role_name in {item["name"] for item in roles.json()}
                assert str(binding_id) in {item["id"] for item in bindings.json()}

                deleted = await client.delete(
                    f"/api/v1/admin/bindings/{binding_id}",
                    headers={**headers, "X-Amesh-Tenant": "default"},
                )
                assert deleted.status_code == 204

                final_admin = await client.post(
                    "/api/v1/admin/bindings",
                    headers=headers,
                    json={
                        "principal_id": str(user_id),
                        "principal_type": "USER",
                        "role_name": "instance-admin",
                        "scope_type": "INSTANCE",
                    },
                )
                assert final_admin.status_code == 201
                protected_delete = await client.delete(
                    f"/api/v1/admin/bindings/{final_admin.json()['id']}",
                    headers=headers,
                )
                assert protected_delete.status_code == 409
                assert "final enabled instance administrator" in protected_delete.text
        finally:
            app.dependency_overrides.clear()
            async with engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM auth_principals WHERE id = ANY(CAST(:ids AS uuid[]))"),
                    {"ids": created_ids},
                )
                await connection.execute(
                    text("DELETE FROM auth_roles WHERE name = :role_name"),
                    {"role_name": role_name},
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM auth_namespace_boundaries
                        WHERE tenant_id = (SELECT id FROM tenants WHERE slug = 'default')
                          AND namespace_name = :namespace
                        """
                    ),
                    {"namespace": namespace},
                )
                await connection.execute(
                    text(
                        "DELETE FROM audit_events "
                        "WHERE actor_id = '00000000-0000-7000-8000-000000000001'"
                    )
                )
            await engine.dispose()

    asyncio.run(scenario())
