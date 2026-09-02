from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import httpx
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuota

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_primitive_repository,
    get_agent_resource_repository,
    get_authorization_service,
    get_self_hosted_plugin_registry,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AgentResourceKind,
    AgentResourceRevision,
    AuthorizationDecision,
    AuthorizationRequest,
    McpConnectionRevision,
    McpConnectionSpec,
    McpToolImpact,
    McpToolPin,
    PrincipalType,
    PromptSpec,
    agent_resource_digest,
)
from amesh.plugin_sdk.registry import PluginRegistryPackage


class _Authorization:
    def __init__(self, *, denied: set[str] | None = None) -> None:
        self.denied = denied or set()
        self.requests: list[AuthorizationRequest] = []

    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        allowed = request.resource_type not in self.denied
        return AuthorizationDecision(
            allowed=allowed,
            reason_code="test_allow" if allowed else "test_deny",
            summary="capability catalog API fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            from amesh.authorization import AuthorizationDenied

            raise AuthorizationDenied(decision)
        return decision


class _ResourceRepository:
    def __init__(self, resources: tuple[AgentResourceRevision, ...]) -> None:
        self.resources = resources
        self.calls: list[tuple[str, str]] = []

    async def list_resources(
        self,
        tenant_id: str,
        namespace: str,
        *,
        kind: AgentResourceKind | None = None,
    ) -> tuple[AgentResourceRevision, ...]:
        self.calls.append((tenant_id, namespace))
        return tuple(
            item
            for item in self.resources
            if item.tenant_id == tenant_id
            and item.namespace == namespace
            and (kind is None or item.kind is kind)
        )


class _PrimitiveRepository:
    def __init__(self, connections: tuple[McpConnectionRevision, ...]) -> None:
        self.connections = connections
        self.calls: list[tuple[str, str]] = []

    async def list_mcp_connections(
        self,
        tenant_id: str,
        namespace: str,
    ) -> tuple[McpConnectionRevision, ...]:
        self.calls.append((tenant_id, namespace))
        return tuple(
            item
            for item in self.connections
            if item.tenant_id == tenant_id and item.spec.namespace == namespace
        )


class _PluginRegistry:
    def __init__(self, packages: tuple[PluginRegistryPackage, ...]) -> None:
        self.packages = packages

    def snapshot(self) -> SimpleNamespace:
        return SimpleNamespace(packages=self.packages)


def _prompt() -> AgentResourceRevision:
    spec = PromptSpec(
        key="research-prompt",
        namespace="agents.demo",
        title="Research prompt",
        content="PRIVATE PROMPT CONTENT",
        variables={"topic": "requested topic"},
    )
    return AgentResourceRevision(
        tenantId="default",
        namespace=spec.namespace,
        kind=spec.kind,
        key=spec.key,
        revision=2,
        digest=agent_resource_digest(spec),
        spec=spec,
        createdBy="catalog-test",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _connection() -> McpConnectionRevision:
    tool = McpToolPin(
        name="search",
        description="Search records",
        inputSchema={"type": "object", "additionalProperties": False},
        outputSchema={"type": "array"},
        impact=McpToolImpact.READ_ONLY,
    )
    spec = McpConnectionSpec(
        key="catalog",
        namespace="agents.demo",
        endpoint="https://mcp.example.test/mcp",
        credentialRef="mcp-token",
        toolAllowlist=(tool.name,),
        tools=(tool,),
    )
    return McpConnectionRevision(
        connectionId=uuid4(),
        tenantId="default",
        revision=3,
        digest=spec.digest,
        spec=spec,
        createdBy="catalog-test",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _plugin() -> PluginRegistryPackage:
    return PluginRegistryPackage(
        name="research.plugin",
        version="1.0.0",
        bundle="PRIVATE PLUGIN BUNDLE",
        contentDigest="sha256:" + "a" * 64,
    )


def _overrides(
    resources: _ResourceRepository,
    connections: _PrimitiveRepository,
    registry: _PluginRegistry,
    authorization: _Authorization,
) -> None:
    app.dependency_overrides[authenticate_actor] = lambda: ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="catalog-user",
    )
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_agent_resource_repository] = lambda: resources
    app.dependency_overrides[get_agent_primitive_repository] = lambda: connections
    app.dependency_overrides[get_self_hosted_plugin_registry] = lambda: registry
    app.dependency_overrides[get_tenant_service] = _TenantQuota


def test_capability_catalog_aggregates_authorized_sources_and_exact_pins() -> None:
    resources = _ResourceRepository((_prompt(),))
    connections = _PrimitiveRepository((_connection(),))
    registry = _PluginRegistry((_plugin(),))
    authorization = _Authorization()
    _overrides(resources, connections, registry, authorization)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                "/api/v1/namespaces/agents.demo/agent/capabilities/catalog",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["namespace"] == "agents.demo"
            assert {item["kind"] for item in body["items"]} == {
                "prompt",
                "mcp-connection",
                "mcp-tool",
                "plugin",
            }
            tool = next(item for item in body["items"] if item["kind"] == "mcp-tool")
            reference = tool["attachment"]["reference"]
            assert reference["connectionKey"] == "catalog"
            assert reference["connectionRevision"] == 3
            assert reference["connectionDigest"] == connections.connections[0].digest
            assert (
                reference["schemaDigest"] == connections.connections[0].spec.tools[0].schema_digest
            )
            assert "PRIVATE PROMPT CONTENT" not in response.text
            assert "PRIVATE PLUGIN BUNDLE" not in response.text
            assert "mcp-token" not in response.text

    try:
        asyncio.run(scenario())
        assert resources.calls == [("default", "agents.demo")]
        assert connections.calls == [("default", "agents.demo")]
        assert {request.resource_type for request in authorization.requests} == {
            "agent",
            "agent_connection",
            "plugin",
        }
    finally:
        app.dependency_overrides.clear()


def test_capability_catalog_search_kind_status_limit_are_server_side_filters() -> None:
    resources = _ResourceRepository((_prompt(),))
    connections = _PrimitiveRepository((_connection(),))
    registry = _PluginRegistry((_plugin(),))
    authorization = _Authorization()
    _overrides(resources, connections, registry, authorization)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                "/api/v1/namespaces/agents.demo/agent/capabilities/catalog",
                headers={"X-Amesh-Tenant": "default"},
                params={"q": "search", "kind": "mcp-tool", "status": "available", "limit": 1},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["returned"] == 1
            assert body["total"] == 1
            assert body["truncated"] is False
            assert len(body["items"]) == 1
            assert body["items"][0]["kind"] == "mcp-tool"
            assert body["items"][0]["key"] == "search"

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_capability_catalog_denied_source_is_explicit_and_not_projected() -> None:
    resources = _ResourceRepository((_prompt(),))
    connections = _PrimitiveRepository((_connection(),))
    registry = _PluginRegistry((_plugin(),))
    authorization = _Authorization(denied={"plugin"})
    _overrides(resources, connections, registry, authorization)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                "/api/v1/namespaces/agents.demo/agent/capabilities/catalog",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert all(item["kind"] != "plugin" for item in body["items"])
            access = {item["source"]: item for item in body["sourceAccess"]}
            assert access["plugins"]["status"] == "denied"
            assert access["agents"]["status"] == "allowed"
            assert access["connections"]["status"] == "allowed"
            assert "research.plugin" not in response.text

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
