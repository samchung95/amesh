from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
from tests.fixtures.api_stubs import NonEmptyTenantQuotaStub as _TenantQuota

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_memory_repository,
    get_authorization_service,
    get_operational_control_repository,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AgentMemoryMetadata,
    AgentMemoryScope,
    AuthorizationDecision,
    AuthorizationRequest,
    OperationalBoundary,
    OperationalControlDecision,
    PermissionAction,
    PrincipalType,
    RunningWorkPolicy,
)


class _Authorization:
    def __init__(self) -> None:
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="agent memory API fixture",
            policy_version=1,
        )


class _Controls:
    async def evaluate(
        self,
        boundary: OperationalBoundary,
        **kwargs: object,
    ) -> OperationalControlDecision:
        del kwargs
        return OperationalControlDecision(
            blocked=False,
            boundary=boundary,
            runningWorkPolicy=RunningWorkPolicy.CONTINUE,
        )


class _Memory:
    def __init__(self, metadata: AgentMemoryMetadata) -> None:
        self.metadata = metadata
        self.deleted: tuple[str, str, UUID, str] | None = None

    async def list_metadata(
        self,
        tenant_id: str,
        namespace: str,
        *,
        agent_key: str | None = None,
        limit: int = 100,
    ) -> tuple[AgentMemoryMetadata, ...]:
        assert (tenant_id, namespace, agent_key, limit) == (
            "default",
            "agents.demo",
            "helper",
            10,
        )
        return (self.metadata,)

    async def delete(
        self,
        tenant_id: str,
        namespace: str,
        entry_id: UUID,
        *,
        actor_id: str,
    ) -> AgentMemoryMetadata:
        self.deleted = (tenant_id, namespace, entry_id, actor_id)
        return self.metadata


def test_agent_memory_api_exposes_metadata_only_and_namespace_scoped_delete() -> None:
    now = datetime.now(UTC)
    metadata = AgentMemoryMetadata(
        entryId=uuid4(),
        tenantId="default",
        namespace="agents.demo",
        agentKey="helper",
        agentRevision=1,
        executionId=uuid4(),
        scope=AgentMemoryScope.PRIVATE,
        sharedScope=None,
        key="answer",
        contentDigest="sha256:" + "1" * 64,
        byteSize=20,
        provenance={"sessionId": "session-1"},
        redacted=True,
        version=1,
        createdAt=now,
        updatedAt=now,
        expiresAt=now + timedelta(hours=1),
    )
    memory = _Memory(metadata)
    authorization = _Authorization()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="operator",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_agent_memory_repository] = lambda: memory
    app.dependency_overrides[get_tenant_service] = _TenantQuota
    app.dependency_overrides[get_operational_control_repository] = _Controls

    async def scenario() -> None:
        headers = {"X-Amesh-Tenant": "default"}
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            listed = await client.get(
                "/api/v1/namespaces/agents.demo/agent/memory",
                headers=headers,
                params={"agentKey": "helper", "limit": 10},
            )
            assert listed.status_code == 200, listed.text
            assert listed.json()[0]["key"] == "answer"
            assert "value" not in listed.json()[0]

            deleted = await client.delete(
                f"/api/v1/namespaces/agents.demo/agent/memory/{metadata.entry_id}",
                headers=headers,
            )
            assert deleted.status_code == 200, deleted.text
            assert memory.deleted is not None
            assert memory.deleted[:3] == (
                "default",
                "agents.demo",
                metadata.entry_id,
            )

    try:
        asyncio.run(scenario())
        assert [request.action for request in authorization.requests] == [
            PermissionAction.VIEW,
            PermissionAction.MANAGE,
        ]
    finally:
        app.dependency_overrides.clear()
