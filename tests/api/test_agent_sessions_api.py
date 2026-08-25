from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_session_repository,
    get_authorization_service,
    get_repository,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AgentSessionRecord,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)


class _Authorization:
    def __init__(self) -> None:
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="agent session fixture",
            policy_version=1,
        )


class _TenantQuota:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug
        return 1


class _Executions:
    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> object:
        assert tenant_id == "default"
        assert execution_id
        return object()


class _Sessions:
    def __init__(self, record: AgentSessionRecord) -> None:
        self.record = record

    async def list_execution_sessions(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> tuple[AgentSessionRecord, ...]:
        assert tenant_id == "default"
        assert execution_id == self.record.execution_id
        return (self.record,)


def test_execution_agent_sessions_are_authorized_and_inspectable() -> None:
    execution_id = uuid4()
    record = AgentSessionRecord(
        tenantId="default",
        namespace="agents.demo",
        executionId=execution_id,
        taskRunId=uuid4(),
        attempt=1,
        capabilityPinId=uuid4(),
        envelopeDigest="sha256:" + "1" * 64,
        createdAt=datetime.now(UTC),
        updatedAt=datetime.now(UTC),
    )
    authorization = _Authorization()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="operator",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_repository] = _Executions
    app.dependency_overrides[get_agent_session_repository] = lambda: _Sessions(record)
    app.dependency_overrides[get_tenant_service] = _TenantQuota

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/executions/{execution_id}/agent-sessions",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert response.json()[0]["envelopeDigest"] == record.envelope_digest
        assert response.json()[0]["state"] == "RUNNING"

    try:
        asyncio.run(scenario())
        assert authorization.requests[0].resource_type == "execution"
    finally:
        app.dependency_overrides.clear()
