from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresExecutionRepository,
    PostgresPluginPolicyRepository,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_plugin_catalog_manager,
    get_plugin_policy_repository,
    get_plugin_policy_service,
    get_tenant_service,
)
from amesh.config import Settings
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)
from amesh.dsl import FlowDefinition
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.plugin_sdk import PluginResolver
from amesh.plugins import PluginPolicyService, build_plugin_catalog

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_plugin_policy_api_explains_rules_and_previews_emergency_disable() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        catalog = build_plugin_catalog(Settings())
        policies = PostgresPluginPolicyRepository(engine)
        service = PluginPolicyService(policies, catalog, default_allow=False)
        executions = PostgresExecutionRepository(
            engine,
            plugin_resolution_provider=lambda flow: (
                PluginResolver(catalog.snapshot).resolve_flow(flow).revision_payload()
            ),
        )
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="plugin-policy-admin",
            bootstrap_admin=True,
        )
        flow_document = """
id: policy_api_flow
namespace: governance.api
tasks:
  - id: done
    type: core.return
    value: ok
"""
        flow = FlowDefinition.model_validate(
            {
                "id": "policy_api_flow",
                "namespace": "governance.api",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        core_version = next(
            record.manifest.version
            for record in catalog.snapshot.packages
            if record.manifest is not None and record.manifest.name == "amesh.core"
        )
        try:
            await apply_migrations(database.database_url, migration_directory())
            await executions.apply_flow(flow, tenant_id="default")
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_authorization_service] = _AllowAuthorization
            app.dependency_overrides[get_tenant_service] = _TenantQuota
            app.dependency_overrides[get_plugin_catalog_manager] = lambda: catalog
            app.dependency_overrides[get_plugin_policy_repository] = lambda: policies
            app.dependency_overrides[get_plugin_policy_service] = lambda: service
            transport = httpx.ASGITransport(app=app)
            headers = {"X-Amesh-Tenant": "default"}
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                created = await client.post(
                    "/api/v1/plugin-policy/rules",
                    headers=headers,
                    json={
                        "scope": "NAMESPACE",
                        "namespace": flow.namespace,
                        "effect": "DENY",
                        "stages": ["VALIDATION"],
                        "selector": {"package": "amesh.core"},
                        "reason": "API acceptance deny",
                    },
                )
                assert created.status_code == 201, created.text

                fetched = await client.get(
                    f"/api/v1/plugin-policy/rules/{created.json()['id']}",
                    headers=headers,
                )
                assert fetched.status_code == 200, fetched.text
                assert fetched.json()["reason"] == "API acceptance deny"

                effective = await client.get(
                    "/api/v1/plugin-policy/effective",
                    headers=headers,
                    params={"namespace": flow.namespace},
                )
                assert effective.status_code == 200, effective.text
                assert effective.json()["rules"][0]["id"] == created.json()["id"]

                evaluated = await client.post(
                    "/api/v1/plugin-policy/evaluate",
                    headers={**headers, "Content-Type": "application/yaml"},
                    params={"stage": "VALIDATION"},
                    content=flow_document,
                )
                assert evaluated.status_code == 200, evaluated.text
                assert evaluated.json()["allowed"] is False
                assert (
                    evaluated.json()["subjects"][0]["sources"][0]["sourceId"]
                    == created.json()["id"]
                )

                request = {
                    "scope": "INSTANCE",
                    "package": "amesh.core",
                    "version": core_version,
                    "reason": "API emergency disable",
                }
                preview = await client.post(
                    "/api/v1/plugin-policy/quarantines/preview",
                    headers=headers,
                    json=request,
                )
                assert preview.status_code == 200, preview.text
                assert preview.json()["affectedFlows"][0]["flow_key"] == flow.id

                quarantine = await client.post(
                    "/api/v1/plugin-policy/quarantines",
                    headers=headers,
                    json=request,
                )
                assert quarantine.status_code == 201, quarantine.text
                assert quarantine.json()["state"] == "ACTIVE"

                decisions = await client.get(
                    "/api/v1/plugin-policy/decisions",
                    headers=headers,
                )
                assert decisions.status_code == 200, decisions.text
                assert decisions.json()[0]["stage"] == "VALIDATION"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


class _AllowAuthorization:
    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary=f"allowed {request.resource_type}",
            policy_version=1,
        )


class _TenantQuota:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug == "default"
        return 1
