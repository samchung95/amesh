from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_session_fleet_repository,
    get_authorization_service,
    require_tenant_context,
)
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AgentSessionFleetAggregates,
    AgentSessionFleetItem,
    AgentSessionFleetPage,
    AgentSessionFleetQuery,
    AgentSessionInstanceAggregate,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)


def _page(tenant_id: str = "default") -> AgentSessionFleetPage:
    now = datetime.now(UTC)
    execution_id = uuid4()
    item = AgentSessionFleetItem(
        sessionId=uuid4(),
        tenantId=tenant_id,
        namespace="research",
        agentRef="research/analyst@1",
        ownerId="owner-a",
        executionId=execution_id,
        state="RUNNING",
        executionEpoch=1,
        executionVersion=1,
        createdAt=now,
        updatedAt=now,
    )
    return AgentSessionFleetPage(
        items=(item,),
        aggregates=AgentSessionFleetAggregates(
            matchedExecutions=1,
            active=1,
            terminal=0,
        ),
        readAt=now,
    )


def test_admin_fleet_requires_both_session_administration_permissions() -> None:
    actor = ActorContext(principal_id=uuid4(), principal_type=PrincipalType.USER, display="admin")
    calls: list[AuthorizationRequest] = []

    class Authorization:
        async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
            calls.append(request)
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="allowed",
                policy_version=1,
                matched_role_names=("session-admin",),
            )

    class Fleet:
        async def list_fleet(
            self, tenant_id: str, query: AgentSessionFleetQuery
        ) -> AgentSessionFleetPage:
            assert tenant_id == "default"
            assert query.namespace == "research"
            assert query.agent_ref == "research/analyst@1"
            assert query.owner_id == "owner-a"
            assert query.harness == "pi"
            return _page(tenant_id)

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_agent_session_fleet_repository: Fleet,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                "/api/v1/admin/agent-sessions",
                params={
                    "namespace": "research",
                    "agentRef": "research/analyst@1",
                    "ownerId": "owner-a",
                    "harness": "pi",
                },
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert response.json()["items"][0]["tenantId"] == "default"
        assert response.json()["items"][0]["ownerId"] == "owner-a"

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()

    assert [(call.resource_type, call.action.value) for call in calls] == [
        ("agent_session_administration", "view"),
        ("agent_session", "list"),
    ]


def test_admin_fleet_has_no_legacy_authorization_fallback() -> None:
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )

    class Authorization:
        async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
            decision = AuthorizationDecision(
                allowed=False,
                reason_code="NO_MATCHING_GRANT",
                summary="denied",
                policy_version=1,
                matched_role_names=("session-client",),
            )
            raise AuthorizationDenied(decision)

    class Fleet:
        async def list_fleet(
            self, tenant_id: str, query: AgentSessionFleetQuery
        ) -> AgentSessionFleetPage:
            raise AssertionError("authorization must run before the fleet query")

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_agent_session_fleet_repository: Fleet,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                "/api/v1/admin/agent-sessions",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 403, response.text

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_instance_aggregate_is_metadata_only_and_instance_authorized() -> None:
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="instance-admin"
    )
    calls: list[AuthorizationRequest] = []

    class Authorization:
        async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
            calls.append(request)
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="allowed",
                policy_version=1,
                matched_role_names=("instance-admin",),
            )

    class Fleet:
        async def instance_aggregate(self) -> AgentSessionInstanceAggregate:
            return AgentSessionInstanceAggregate(
                tenants=(), matchedExecutions=0, active=0, terminal=0, readAt=datetime.now(UTC)
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            get_authorization_service: Authorization,
            get_agent_session_fleet_repository: Fleet,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get("/api/v1/admin/agent-sessions/aggregate")
        assert response.status_code == 200, response.text
        assert response.json()["tenants"] == []

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()

    assert [(call.resource_type, call.action.value, call.tenant_id) for call in calls] == [
        ("agent_session_administration", "view", None),
        ("agent_session", "list", None),
    ]
