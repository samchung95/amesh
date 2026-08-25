from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    ExecutionState,
    FlowLifecycle,
    PrincipalType,
    TaskRunState,
)
from amesh.mcp_server import create_amesh_mcp_application, create_amesh_mcp_server


class _Credentials:
    def __init__(self, actor: ActorContext) -> None:
        self.actor = actor
        self.requests: list[tuple[str | None, str]] = []

    async def authenticate_bearer(
        self,
        authorization: str | None,
        *,
        audience: str = "amesh-api",
    ) -> ActorContext:
        self.requests.append((authorization, audience))
        if authorization != "Bearer mcp-token":
            from amesh.credentials import InvalidCredential

            raise InvalidCredential("invalid")
        return self.actor


class _Authorization:
    def __init__(self) -> None:
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="MCP read fixture",
            policy_version=1,
        )


class _Executions:
    def __init__(self) -> None:
        self.execution_id = uuid4()
        self.reads: list[tuple[str, str]] = []

    async def list_flows(self, *, tenant_id: str) -> list[SimpleNamespace]:
        self.reads.append(("list_flows", tenant_id))
        return [
            SimpleNamespace(
                flow_id="summarize",
                namespace="agents.demo",
                revision=3,
                lifecycle=FlowLifecycle.ACTIVE,
                semantic_hash="abc123",
                etag='"flow-etag"',
            ),
            SimpleNamespace(
                flow_id="hidden",
                namespace="other.namespace",
                revision=1,
                lifecycle=FlowLifecycle.ACTIVE,
                semantic_hash="def456",
                etag='"hidden-etag"',
            ),
        ]

    async def get_execution(self, execution_id: object, *, tenant_id: str) -> SimpleNamespace:
        self.reads.append(("get_execution", tenant_id))
        if execution_id != self.execution_id:
            raise LookupError("missing")
        now = datetime.now(UTC)
        return SimpleNamespace(
            execution_id=self.execution_id,
            namespace="agents.demo",
            flow_id="summarize",
            flow_revision=3,
            state=ExecutionState.RUNNING,
            created_at=now,
            updated_at=now,
        )

    async def list_task_runs(
        self, execution_id: object, *, tenant_id: str
    ) -> list[SimpleNamespace]:
        self.reads.append(("list_task_runs", tenant_id))
        assert execution_id == self.execution_id
        return [
            SimpleNamespace(
                task_run_id=uuid4(),
                task_id="model",
                state=TaskRunState.RUNNING,
                current_attempt=1,
            )
        ]


def test_amesh_mcp_requires_workload_token_and_exposes_read_only_authorized_tools() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.SERVICE_ACCOUNT,
        display="mcp-reader",
        credential_id=uuid4(),
        credential_scopes=("flow:list", "execution:view"),
        credential_audience="amesh-mcp",
    )
    credentials = _Credentials(actor)
    authorization = _Authorization()
    executions = _Executions()
    server = create_amesh_mcp_server(
        credentials,  # type: ignore[arg-type]
        executions,  # type: ignore[arg-type]
        authorization,  # type: ignore[arg-type]
        base_url="http://amesh.test",
    )
    application = create_amesh_mcp_application(server, base_url="http://amesh.test")

    async def scenario() -> None:
        async with application.router.lifespan_context(application):
            transport = httpx2.ASGITransport(app=application)
            async with httpx2.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as anonymous:
                response = await anonymous.post(
                    "/mcp",
                    headers={"Content-Type": "application/json"},
                    json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                )
                assert response.status_code == 401

            async with httpx2.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
                headers={"Authorization": "Bearer mcp-token"},
            ) as authenticated:
                mcp_transport = streamable_http_client(
                    "http://amesh.test/mcp",
                    http_client=authenticated,
                )
                async with Client(mcp_transport, raise_exceptions=True) as client:
                    catalog = await client.list_tools()
                    assert [tool.name for tool in catalog.tools] == [
                        "list_workflows",
                        "inspect_execution",
                    ]
                    assert all(
                        tool.annotations is not None
                        and tool.annotations.read_only_hint is True
                        and tool.annotations.destructive_hint is False
                        for tool in catalog.tools
                    )

                    workflows = await client.call_tool(
                        "list_workflows",
                        {"tenant": "default", "namespace": "agents.demo"},
                    )
                    assert workflows.structured_content is not None
                    assert [item["id"] for item in workflows.structured_content["workflows"]] == [
                        "summarize"
                    ]

                    inspected = await client.call_tool(
                        "inspect_execution",
                        {
                            "tenant": "default",
                            "execution_id": str(executions.execution_id),
                        },
                    )
                    assert inspected.structured_content is not None
                    assert inspected.structured_content["state"] == "RUNNING"
                    assert "inputs" not in inspected.structured_content
                    assert "outputs" not in inspected.structured_content

    asyncio.run(scenario())
    assert credentials.requests
    assert set(credentials.requests) == {("Bearer mcp-token", "amesh-mcp")}
    assert [(request.resource_type, request.audience) for request in authorization.requests] == [
        ("flow", "amesh-mcp"),
        ("execution", "amesh-mcp"),
    ]
    assert executions.reads == [
        ("list_flows", "default"),
        ("get_execution", "default"),
        ("list_task_runs", "default"),
    ]
