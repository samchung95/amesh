from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx

from amesh.app import app, authenticate_actor, get_authorization_service, get_tenant_service
from amesh.config import Settings, get_settings
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PermissionAction,
    PrincipalType,
)


class CapabilityServiceStub:
    def __init__(self, allowed: set[tuple[str, PermissionAction]]) -> None:
        self.allowed = allowed

    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        granted = (request.resource_type, request.action) in self.allowed
        return AuthorizationDecision(
            allowed=granted,
            reason_code="allowed" if granted else "denied",
            summary="test capability decision",
            policy_version=1,
        )


class TenantQuotaStub:
    async def consume_api_request(self, tenant_slug: str) -> int:
        del tenant_slug
        return 1


def test_ui_session_returns_server_authoritative_capabilities_and_privacy_policy() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="ui-viewer",
    )
    service = CapabilityServiceStub(
        {
            ("flow", PermissionAction.VIEW),
            ("execution", PermissionAction.VIEW),
            ("release", PermissionAction.VIEW),
        }
    )
    settings = Settings(product_telemetry_enabled=False)
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: service
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            response = await client.get(
                "/api/v1/ui/session?namespace=team.data",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200
        payload = response.json()
        assert payload["principalId"] == str(actor.principal_id)
        assert payload["display"] == "ui-viewer"
        assert payload["tenantId"] == "default"
        assert payload["namespace"] == "team.data"
        assert payload["telemetryEnabled"] is False
        assert payload["capabilities"] == {
            "administration.manage": False,
            "agents.execute": False,
            "agents.manage": False,
            "agents.view": False,
            "announcements.view": False,
            "apps.execute": False,
            "apps.manage": False,
            "apps.view": False,
            "assets.manage": False,
            "assets.view": False,
            "checks.manage": False,
            "checks.view": False,
            "executions.execute": False,
            "executions.manage": False,
            "executions.view": True,
            "dashboards.manage": False,
            "dashboards.view": False,
            "flows.create": False,
            "flows.update": False,
            "flows.view": True,
            "flowTests.execute": False,
            "flowTests.manage": False,
            "flowTests.view": False,
            "humanTasks.update": False,
            "humanTasks.view": False,
            "namespaces.view": False,
            "namespaceResources.read": False,
            "namespaceResources.write": False,
            "plugins.view": False,
            "operationalControls.manage": False,
            "releases.manage": False,
            "releases.view": True,
            "search.manage": False,
            "search.view": False,
            "secretBindings.write": False,
            "triggers.manage": False,
            "triggers.view": False,
        }

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_ui_session_conceals_tenant_when_no_capability_is_granted() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="unbound-user",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: CapabilityServiceStub(set())
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            response = await client.get(
                "/api/v1/ui/session",
                headers={"X-Amesh-Tenant": "private-tenant"},
            )
        assert response.status_code == 404
        assert response.json()["detail"] == "tenant unavailable"

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
