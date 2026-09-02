from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import httpx
from tests.fixtures.api_stubs import TenantQuotaStub

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_dashboard_repository,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    DashboardQuery,
    DashboardQueryResult,
    PermissionAction,
    PrincipalType,
)


class DashboardAuthorizationStub:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        allowed = (request.resource_type, request.action) in {
            ("dashboard", PermissionAction.VIEW),
            ("execution", PermissionAction.VIEW),
        }
        return AuthorizationDecision(
            allowed=allowed,
            reason_code="allowed" if allowed else "denied",
            summary="dashboard API permission test",
            policy_version=1,
            matched_role_names=("viewer",),
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AssertionError("test invoked require for an intentionally denied source")
        return decision


class DashboardRepositoryStub:
    async def list_definitions(self, *, tenant_id: str) -> tuple[()]:
        del tenant_id
        return ()

    async def execute_query(
        self,
        query: DashboardQuery,
        *,
        tenant_id: str,
    ) -> DashboardQueryResult:
        del query, tenant_id
        return DashboardQueryResult(
            columns=("value",),
            rows=({"value": 3},),
            freshAt=datetime(2026, 8, 23, tzinfo=UTC),
            partial=False,
            sampled=False,
            redacted=False,
            scannedRows=3,
            limit=100,
        )


def test_dashboard_render_redacts_denied_widget_sources_without_hiding_definitions() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="dashboard-viewer",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = DashboardAuthorizationStub
    app.dependency_overrides[get_dashboard_repository] = DashboardRepositoryStub
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            listed = await client.get(
                "/api/v1/dashboards",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert listed.status_code == 200
            assert len(listed.json()) == 6

            allowed = await client.post(
                "/api/v1/dashboards/builtin.instance/render",
                headers={"X-Amesh-Tenant": "default"},
                json={},
            )
            assert allowed.status_code == 200
            assert all(not item["result"]["redacted"] for item in allowed.json()["widgets"])

            redacted = await client.post(
                "/api/v1/dashboards/builtin.sla/render",
                headers={"X-Amesh-Tenant": "default"},
                json={},
            )
            assert redacted.status_code == 200
            assert all(item["result"]["redacted"] for item in redacted.json()["widgets"])
            assert all(item["result"]["rows"] == [] for item in redacted.json()["widgets"])

            direct_denied = await client.post(
                "/api/v1/dashboard-queries",
                headers={"X-Amesh-Tenant": "default"},
                json={"source": "SLA", "visualization": "COUNTER"},
            )
            assert direct_denied.status_code == 403

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
