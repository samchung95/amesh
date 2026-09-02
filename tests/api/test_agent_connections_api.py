from __future__ import annotations

import asyncio
import socket
import time
from datetime import UTC, datetime
from threading import Thread
from typing import Any
from uuid import uuid4

import httpx
import pytest
import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import SecretStr
from tests.fixtures.api_stubs import DefaultTenantQuotaStub as _TenantQuota

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_primitive_repository,
    get_audit_repository,
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


class _Audit:
    def __init__(self) -> None:
        self.records: list[dict[str, object]] = []
        self.evidence_id = uuid4()

    async def record_connection_test(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        connection_key: str,
        connection_revision: int,
        connection_digest: str,
        status: str,
        observed_digest: str | None,
        checked_tool_count: int,
        diagnostic: str | None,
    ) -> object:
        self.records.append(
            {
                "tenant_id": tenant_id,
                "actor_id": actor_id,
                "connection_key": connection_key,
                "connection_revision": connection_revision,
                "connection_digest": connection_digest,
                "status": status,
                "observed_digest": observed_digest,
                "checked_tool_count": checked_tool_count,
                "diagnostic": diagnostic,
            }
        )
        return self.evidence_id


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


def _connection(tool: McpToolPin | None = None) -> McpConnectionRevision:
    selected = tool or _tool()
    spec = McpConnectionSpec(
        key="catalog",
        namespace="agents.demo",
        endpoint="https://mcp.example.test/mcp",
        credentialRef="mcp-token",
        toolAllowlist=(selected.name,),
        tools=(selected,),
    )
    return McpConnectionRevision(
        connectionId=uuid4(),
        tenantId="default",
        revision=1,
        digest=spec.digest,
        spec=spec,
        createdBy="agent-author",
        createdAt=datetime.now(UTC),
    )


def _overrides(
    repository: _AgentRepository,
    shared_resources: _SharedResources,
    authorization: _Authorization,
    audit: _Audit | None = None,
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
    if audit is not None:
        app.dependency_overrides[get_audit_repository] = lambda: audit
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

            tool_catalog = await client.get(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/catalog/tools",
                headers=headers,
                params={"revision": 1},
            )
            assert tool_catalog.status_code == 200
            assert tool_catalog.json()[0]["schemaDigest"] == tool.schema_digest
            assert "outbound-secret" not in tool_catalog.text

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


@pytest.mark.parametrize(
    ("live_tool", "expected_status"),
    [
        (_tool(), "PASSED"),
        (
            _tool().model_copy(
                update={"input_schema": {"type": "object", "properties": {"other": {}}}}
            ),
            "SCHEMA_DRIFT",
        ),
    ],
)
def test_agent_mcp_connection_test_returns_exact_pin_and_redacted_evidence(
    monkeypatch: pytest.MonkeyPatch,
    live_tool: McpToolPin,
    expected_status: str,
) -> None:
    repository = _AgentRepository()
    connection = _connection()
    repository.saved.append(connection)
    shared_resources = _SharedResources()
    authorization = _Authorization()
    audit = _Audit()

    async def discover(
        endpoint: str,
        credential: str,
        **kwargs: object,
    ) -> McpDiscoveryResult:
        assert endpoint == connection.spec.endpoint
        assert credential == "outbound-secret"
        assert kwargs["timeout_seconds"] == 17
        return McpDiscoveryResult(
            serverName="catalog",
            serverVersion="1.0.0",
            tools=(live_tool,),
            digest="sha256:" + "b" * 64,
        )

    monkeypatch.setenv("AMESH_TEST_MCP_TOKEN", "outbound-secret")
    monkeypatch.setattr("amesh.app.discover_mcp_server", discover)
    _overrides(repository, shared_resources, authorization, audit)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/catalog/test",
                headers={"X-Amesh-Tenant": "default"},
                json={"revision": 1, "timeoutSeconds": 17},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["status"] == expected_status
            assert body["connectionPin"] == {
                "key": "catalog",
                "revision": 1,
                "digest": connection.digest,
            }
            assert body["evidenceId"] == str(audit.evidence_id)
            assert body["observedDigest"] == "sha256:" + "b" * 64
            assert body["checkedToolCount"] == 1
            assert body["redacted"] is True
            assert body["effectBoundary"] == "DISCOVERY_ONLY"
            assert "outbound-secret" not in response.text
            assert "mcp-token" not in response.text

    try:
        asyncio.run(scenario())
        assert len(audit.records) == 1
        assert audit.records[0]["status"] == expected_status
        assert audit.records[0]["connection_key"] == "catalog"
        assert audit.records[0]["connection_revision"] == 1
    finally:
        app.dependency_overrides.clear()


def test_agent_mcp_connection_test_reports_unavailable_without_provider_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _AgentRepository()
    repository.saved.append(_connection())
    shared_resources = _SharedResources()
    audit = _Audit()

    async def unavailable(*args: object, **kwargs: object) -> McpDiscoveryResult:
        del args, kwargs
        raise TimeoutError("provider secret outbound-secret timed out")

    monkeypatch.setenv("AMESH_TEST_MCP_TOKEN", "outbound-secret")
    monkeypatch.setattr("amesh.app.discover_mcp_server", unavailable)
    _overrides(repository, shared_resources, _Authorization(), audit)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/catalog/test",
                headers={"X-Amesh-Tenant": "default"},
                json={"revision": 1},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["status"] == "UNAVAILABLE"
            assert body["observedDigest"] is None
            assert body["checkedToolCount"] == 0
            assert body["diagnostic"]
            assert "outbound-secret" not in response.text

    try:
        asyncio.run(scenario())
        assert audit.records[0]["status"] == "UNAVAILABLE"
        assert audit.records[0]["observed_digest"] is None
    finally:
        app.dependency_overrides.clear()


def test_agent_mcp_connection_test_requires_manage_permission_before_secret_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _AgentRepository()
    repository.saved.append(_connection())
    shared_resources = _SharedResources()
    audit = _Audit()
    called = False

    async def discover(*args: object, **kwargs: object) -> McpDiscoveryResult:
        nonlocal called
        called = True
        del args, kwargs
        raise AssertionError("denied connection test must not discover")

    monkeypatch.setattr("amesh.app.discover_mcp_server", discover)
    _overrides(repository, shared_resources, _Authorization(allow=False), audit)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/catalog/test",
                headers={"X-Amesh-Tenant": "default"},
                json={"revision": 1},
            )
            assert response.status_code == 404

    try:
        asyncio.run(scenario())
        assert not called
        assert shared_resources.requests == []
        assert audit.records == []
    finally:
        app.dependency_overrides.clear()


def test_agent_mcp_connection_live_local_discovery_save_and_test_has_no_tool_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    mcp_server = MCPServer("live-catalog", version="1.0.0")

    @mcp_server.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    def lookup(key: str) -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"value": key}

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = int(listener.getsockname()[1])
    origin = f"http://127.0.0.1:{port}"
    mcp_app = mcp_server.streamable_http_app(
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[f"127.0.0.1:{port}"],
            allowed_origins=[origin],
        ),
        host="127.0.0.1",
    )
    local_server = uvicorn.Server(uvicorn.Config(mcp_app, log_level="critical", lifespan="on"))
    server_thread = Thread(
        target=local_server.run,
        kwargs={"sockets": [listener]},
        daemon=True,
    )
    server_thread.start()
    for _ in range(100):
        if local_server.started:
            break
        time.sleep(0.01)
    assert local_server.started

    repository = _AgentRepository()
    shared_resources = _SharedResources()
    audit = _Audit()
    monkeypatch.setenv("AMESH_TEST_MCP_TOKEN", "outbound-secret")
    _overrides(repository, shared_resources, _Authorization(), audit)
    app.dependency_overrides[get_settings] = lambda: Settings(
        amesh_token_pepper=SecretStr("agent-api-test-key"),
        network_egress_allowed_hosts=("127.0.0.1",),
        core_http_allowed_private_hosts=("127.0.0.1",),
    )

    async def scenario() -> None:
        headers = {"X-Amesh-Tenant": "default"}
        endpoint = f"{origin}/mcp"
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            discovered = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/discover",
                headers=headers,
                json={
                    "endpoint": endpoint,
                    "credentialRef": "mcp-token",
                    "timeoutSeconds": 5,
                },
            )
            assert discovered.status_code == 200, discovered.text
            discovery = discovered.json()
            assert [tool["name"] for tool in discovery["tools"]] == ["lookup"]

            created = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections",
                headers=headers,
                json={
                    "key": "live-catalog",
                    "namespace": "agents.demo",
                    "endpoint": endpoint,
                    "credentialRef": "mcp-token",
                    "toolAllowlist": ["lookup"],
                    "tools": discovery["tools"],
                },
            )
            assert created.status_code == 201, created.text
            revision = created.json()["revision"]

            tested = await client.post(
                "/api/v1/namespaces/agents.demo/agent/mcp-connections/live-catalog/test",
                headers=headers,
                json={"revision": revision, "timeoutSeconds": 5},
            )
            assert tested.status_code == 200, tested.text
            assert tested.json()["status"] == "PASSED"
            assert tested.json()["effectBoundary"] == "DISCOVERY_ONLY"

    try:
        asyncio.run(scenario())
        assert calls == 0
        assert audit.records[0]["status"] == "PASSED"
    finally:
        app.dependency_overrides.clear()
        local_server.should_exit = True
        server_thread.join(timeout=5)
        listener.close()
        assert not server_thread.is_alive()
