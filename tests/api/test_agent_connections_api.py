from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx
import pytest
from pydantic import SecretStr

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_primitive_repository,
    get_authorization_service,
    get_operational_control_repository,
    get_settings,
    get_shared_resource_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationDenied
from amesh.config import Settings
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    McpConnectionRevision,
    McpConnectionSpec,
    McpDiscoveryResult,
    McpToolImpact,
    McpToolPin,
    OperationalBoundary,
    OperationalControlDecision,
    PrincipalType,
    RunningWorkPolicy,
    SecretBinding,
)


class _Authorization:
    def __init__(self, *, allow: bool = True) -> None:
        self.allow = allow
        self.requests: list[AuthorizationRequest] = []

    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        return AuthorizationDecision(
            allowed=self.allow,
            reason_code="test_allow" if self.allow else "test_deny",
            summary="agent connection API fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


class _TenantQuota:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug == "default"
        return 1


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


class _SharedResources:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, str]] = []

    async def get_secret_binding(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> SecretBinding:
        del actor_id
        self.requests.append((tenant_id, namespace, key))
        now = datetime.now(UTC)
        return SecretBinding(
            namespace=namespace,
            key=key,
            provider="env",
            providerReference="AMESH_TEST_MCP_TOKEN",
            resourceVersion=1,
            originNamespace=namespace,
            createdAt=now,
            updatedAt=now,
        )


class _AgentRepository:
    def __init__(self) -> None:
        self.saved: list[McpConnectionRevision] = []

    async def save_mcp_connection(
        self,
        tenant_id: str,
        spec: McpConnectionSpec,
        *,
        actor_id: str,
    ) -> McpConnectionRevision:
        assert actor_id
        revision = McpConnectionRevision(
            connectionId=uuid4(),
            tenantId=tenant_id,
            revision=len(self.saved) + 1,
            digest=spec.digest,
            spec=spec,
            createdBy=actor_id,
            createdAt=datetime.now(UTC),
        )
        self.saved.append(revision)
        return revision

    async def list_mcp_connections(
        self,
        tenant_id: str,
        namespace: str,
    ) -> tuple[McpConnectionRevision, ...]:
        return tuple(
            item
            for item in self.saved
            if item.tenant_id == tenant_id and item.spec.namespace == namespace
        )

    async def get_mcp_connection(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        *,
        revision: int | None = None,
    ) -> McpConnectionRevision:
        matches = [
            item
            for item in self.saved
            if item.tenant_id == tenant_id
            and item.spec.namespace == namespace
            and item.spec.key == key
            and (revision is None or item.revision == revision)
        ]
        if not matches:
            raise LookupError("connection not found")
        return matches[-1]

    async def begin_invocation(self, start: Any) -> Any:
        del start
        raise NotImplementedError

    async def complete_invocation(self, invocation_id: Any, **kwargs: Any) -> Any:
        del invocation_id, kwargs
        raise NotImplementedError


def _tool() -> McpToolPin:
    return McpToolPin(
        name="lookup",
        description="Look up a record",
        inputSchema={
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
            "additionalProperties": False,
        },
        impact=McpToolImpact.READ_ONLY,
    )


def _overrides(
    repository: _AgentRepository,
    shared_resources: _SharedResources,
    authorization: _Authorization,
) -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="agent-author",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_agent_primitive_repository] = lambda: repository
    app.dependency_overrides[get_shared_resource_repository] = lambda: shared_resources
    app.dependency_overrides[get_tenant_service] = _TenantQuota
    app.dependency_overrides[get_operational_control_repository] = _Controls
    app.dependency_overrides[get_settings] = lambda: Settings(
        amesh_token_pepper=SecretStr("agent-api-test-key"),
        network_egress_allowed_hosts=("mcp.example.test",),
    )


def test_agent_mcp_connection_discovery_versioning_and_tenant_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _AgentRepository()
    shared_resources = _SharedResources()
    authorization = _Authorization()
    tool = _tool()
    unapproved_tool = tool.model_copy(update={"name": "unapproved"})

    async def discover(
        endpoint: str,
        credential: str,
        **kwargs: object,
    ) -> McpDiscoveryResult:
        assert endpoint == "https://mcp.example.test/mcp"
        assert credential == "outbound-secret"
        assert kwargs["timeout_seconds"] == 30
        return McpDiscoveryResult(
            serverName="catalog",
            serverVersion="1.0.0",
            tools=(tool, unapproved_tool),
            digest="sha256:" + "a" * 64,
        )

    monkeypatch.setenv("AMESH_TEST_MCP_TOKEN", "outbound-secret")
    monkeypatch.setattr("amesh.app.discover_mcp_server", discover)
    _overrides(repository, shared_resources, authorization)

    async def scenario() -> None:
        headers = {"X-Amesh-Tenant": "default"}
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            discovery = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/discover",
                headers=headers,
                json={
                    "endpoint": "https://mcp.example.test/mcp",
                    "credentialRef": "mcp-token",
                },
            )
            assert discovery.status_code == 200, discovery.text
            assert discovery.json()["tools"][0]["inputSchema"] == tool.input_schema

            spec = {
                "key": "catalog",
                "namespace": "agents.demo",
                "endpoint": "https://mcp.example.test/mcp",
                "credentialRef": "mcp-token",
                "toolAllowlist": ["lookup"],
                "tools": [tool.model_dump(mode="json", by_alias=True)],
            }
            created = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections",
                headers=headers,
                json=spec,
            )
            assert created.status_code == 201, created.text
            assert "outbound-secret" not in created.text

            listed = await client.get(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections",
                headers=headers,
            )
            assert listed.status_code == 200
            assert [item["spec"]["key"] for item in listed.json()] == ["catalog"]

            loaded = await client.get(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/catalog",
                headers=headers,
                params={"revision": 1},
            )
            assert loaded.status_code == 200
            assert loaded.json()["tenantId"] == "default"

    try:
        asyncio.run(scenario())
        assert shared_resources.requests == [
            ("default", "agents.demo", "mcp-token"),
            ("default", "agents.demo", "mcp-token"),
        ]
        assert {request.resource_type for request in authorization.requests} == {
            "agent_connection",
            "secret_binding",
        }
    finally:
        app.dependency_overrides.clear()


def test_agent_mcp_connection_denial_and_outage_are_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _AgentRepository()
    shared_resources = _SharedResources()
    monkeypatch.setenv("AMESH_TEST_MCP_TOKEN", "outbound-secret")

    async def outage(*args: object, **kwargs: object) -> McpDiscoveryResult:
        del args, kwargs
        raise TimeoutError("provider included outbound-secret in a diagnostic")

    monkeypatch.setattr("amesh.app.discover_mcp_server", outage)

    async def request() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            return await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/discover",
                headers={"X-Amesh-Tenant": "default"},
                json={
                    "endpoint": "https://mcp.example.test/mcp",
                    "credentialRef": "mcp-token",
                },
            )

    try:
        _overrides(repository, shared_resources, _Authorization(allow=False))
        denied = asyncio.run(request())
        assert denied.status_code == 404
        assert shared_resources.requests == []

        app.dependency_overrides[get_authorization_service] = _Authorization
        unavailable = asyncio.run(request())
        assert unavailable.status_code == 502
        assert unavailable.json()["detail"] == "MCP discovery failed"
        assert "outbound-secret" not in unavailable.text
    finally:
        app.dependency_overrides.clear()
