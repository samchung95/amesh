from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4, uuid5

import httpx
import httpx2
import pytest
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, Response
from tests.tasks.test_bounded_agent_tasks import MemoryAgentRepository, execution_context

from amesh.domain import McpConnectionRevision, McpConnectionSpec, McpToolImpact, McpToolPin
from amesh.domain.resources import canonical_hash
from amesh.dsl import TaskDefinition
from amesh.executor import TaskExecutionFailure
from amesh.networking import HttpTaskPolicy
from amesh.tasks import agent_mcp_handler
from amesh.tasks.mcp_grants import execution_grant_context

ENDPOINT = "https://gateway.test/mcp"
TOOL = McpToolPin(
    name="read_binding",
    inputSchema={"type": "object", "properties": {"bindingId": {"type": "string"}}},
    impact=McpToolImpact.READ_ONLY,
)


def connection(*, scoped: bool = True) -> McpConnectionRevision:
    spec = McpConnectionSpec(
        key="gateway",
        namespace="agents.demo",
        endpoint=ENDPOINT,
        credentialRef="mcp-token",
        toolAllowlist=(TOOL.name,),
        tools=(TOOL,),
        **(
            {"executionGrant": {"exchangeEndpoint": "https://gateway.test/exchange"}}
            if scoped
            else {}
        ),
    )
    return McpConnectionRevision(
        connectionId=uuid4(),
        tenantId="default",
        revision=1,
        digest=spec.digest,
        spec=spec,
        createdBy="fixture",
        createdAt=datetime.now(UTC),
    )


def task(binding: str | None = None) -> TaskDefinition:
    return TaskDefinition.model_validate(
        {
            "id": "tool",
            "type": "agent.mcp",
            "connection": "gateway",
            "revision": 1,
            "tool": TOOL.name,
            "arguments": {} if binding is None else {"bindingId": binding},
            "contract": {"secretScopes": ["mcp-token"]},
            "invocationKey": "session:tool:1",
        }
    )


class Gateway:
    def __init__(self, actor: UUID, sessions: dict[str, UUID], *, fault: str = "") -> None:
        self.actor = str(actor)
        self.sessions = {key: str(value) for key, value in sessions.items()}
        self.fault = fault
        self.exchanges: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self.tokens: dict[str, dict[str, Any]] = {}
        self.app = FastAPI()
        self.app.post("/exchange")(self.exchange)
        self.app.post("/mcp")(self.mcp)

    async def exchange(self, request: Request) -> Response:
        body = await request.json()
        self.exchanges.append(body)
        if (
            request.headers.get("authorization") != "Bearer mcp-key"
            or body["tenantId"] != "default"
            or body["actorId"] != self.actor
            or self.sessions.get(body["grantRef"]) != body["sessionId"]
            or body["audience"] != ENDPOINT
            or body["tool"] != TOOL.name
            or self.fault in {"revoked", "invalid"}
        ):
            return JSONResponse({"error": "denied"}, status_code=403)
        token = f"scoped-token-{uuid4()}"
        self.tokens[token] = body
        return JSONResponse(
            {
                "accessToken": token,
                "tokenType": "Bearer",
                "audience": "https://wrong.test/mcp" if self.fault == "audience" else ENDPOINT,
                "contextDigest": "0" * 64 if self.fault == "context" else canonical_hash(body),
                "expiresAt": (
                    datetime.now(UTC) + timedelta(seconds=-1 if self.fault == "expired" else 60)
                ).isoformat(),
            }
        )

    async def mcp(self, request: Request) -> Response:
        body = await request.json()
        bearer = request.headers.get("authorization", "").removeprefix("Bearer ")
        context = self.tokens.get(bearer)
        if bearer != "mcp-key" and context is None:
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        method = body["method"]
        if method.startswith("notifications/"):
            return Response(status_code=202)
        if method == "initialize":
            result = {
                "protocolVersion": body["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "gateway", "version": "1"},
            }
        elif method == "tools/list":
            result = {"tools": [{"name": TOOL.name, "inputSchema": TOOL.input_schema}]}
        elif method == "tools/call":
            if context is None or self.fault == "expire-at-call":
                return JSONResponse({"error": "grant required"}, status_code=403)
            binding = body["params"].get("arguments", {}).get("bindingId", context["grantRef"])
            if binding != context["grantRef"]:
                return JSONResponse({"error": "wrong binding"}, status_code=403)
            self.calls.append(context)
            result = {
                "content": [],
                "structuredContent": {"session": context["sessionId"], "echo": bearer},
            }
        else:
            return Response(status_code=405)
        return JSONResponse({"jsonrpc": "2.0", "id": body["id"], "result": result})


def install_gateway(monkeypatch: pytest.MonkeyPatch, gateway: Gateway) -> None:
    client = httpx.AsyncClient
    mcp_client = httpx2.AsyncClient
    monkeypatch.setattr(
        "amesh.tasks.mcp_grants.httpx.AsyncClient",
        lambda **kwargs: client(transport=httpx.ASGITransport(app=gateway.app), **kwargs),
    )
    monkeypatch.setattr(
        "amesh.tasks.mcp_client.httpx2.AsyncClient",
        lambda **kwargs: mcp_client(transport=httpx2.ASGITransport(app=gateway.app), **kwargs),
    )


def test_scoped_http_calls_bind_two_sessions_and_reuse_receipts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    actor, first_session, second_session = uuid4(), uuid4(), uuid4()
    gateway = Gateway(actor, {"grant-a": first_session, "grant-b": second_session})
    install_gateway(monkeypatch, gateway)
    repository = MemoryAgentRepository(connection())
    handler = agent_mcp_handler(
        repository=repository,
        http_policy=HttpTaskPolicy(allowed_private_hosts=frozenset({"gateway.test"})),
    )
    first = replace(
        execution_context(),
        trigger={
            "ameshActorId": str(actor),
            "ameshAgentSessionId": str(first_session),
            "ameshToolGrants": {"gateway": "grant-a"},
        },
    )
    second = replace(
        execution_context(),
        trigger={
            "ameshActorId": str(actor),
            "ameshAgentSessionId": str(second_session),
            "ameshToolGrants": {"gateway": "grant-b"},
        },
    )

    async def scenario() -> None:
        result = await handler(task(), first)
        assert result.output["structuredContent"] == {
            "session": str(first_session),
            "echo": "[REDACTED]",
        }
        other = await handler(task(), second)
        assert other.output["structuredContent"]["session"] == str(second_session)
        retry = replace(first, attempt_id=uuid4())
        assert (await handler(task(), retry)).output == result.output
        assert len(gateway.calls) == len(gateway.exchanges) == 2
        follow_up = replace(first, execution_id=uuid4(), task_run_id=uuid4(), attempt_id=uuid4())
        await handler(task(), follow_up)
        assert gateway.calls[-1]["sessionId"] == str(first_session)
        assert gateway.calls[-1]["invocationId"] != gateway.calls[0]["invocationId"]
        assert gateway.calls[-1]["attemptId"] == str(follow_up.attempt_id)
        # Tool arguments cannot select another session's authority or binding.
        forged = replace(first, task_run_id=uuid4(), attempt_id=uuid4())
        with pytest.raises(TaskExecutionFailure):
            await handler(task("grant-b"), forged)
        transferred = replace(
            second,
            task_run_id=uuid4(),
            trigger={
                **second.trigger,
                "ameshToolGrants": {"gateway": "grant-a"},
            },
        )
        with pytest.raises(TaskExecutionFailure):
            await handler(task(), transferred)
        assert len(gateway.calls) == 3
        evidence = json.dumps(
            [record.model_dump(mode="json") for record in repository.invocations.values()]
        )
        assert all(token not in evidence for token in gateway.tokens)
        assert "grant-a" not in evidence and "grant-b" not in evidence

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "fault", ["invalid", "revoked", "expired", "audience", "context", "expire-at-call"]
)
def test_invalid_grants_fail_without_tool_side_effects(
    monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    actor, session = uuid4(), uuid4()
    gateway = Gateway(actor, {"grant-a": session}, fault=fault)
    install_gateway(monkeypatch, gateway)
    handler = agent_mcp_handler(
        repository=MemoryAgentRepository(connection()),
        http_policy=HttpTaskPolicy(allowed_private_hosts=frozenset({"gateway.test"})),
    )
    context = replace(
        execution_context(),
        trigger={
            "ameshActorId": str(actor),
            "ameshAgentSessionId": str(session),
            "ameshToolGrants": {"gateway": "grant-a"},
        },
    )
    with pytest.raises(TaskExecutionFailure):
        asyncio.run(handler(task(), context))
    assert len(gateway.exchanges) == 1
    assert gateway.calls == []


def test_missing_scope_fails_and_attempt_identity_is_separate_from_invocation() -> None:
    revision = connection()
    context = execution_context()
    invocation = uuid5(context.task_run_id, "tool")
    with pytest.raises(PermissionError, match="bound canonical session grant"):
        execution_grant_context(revision, context, tool=TOOL.name, invocation_id=invocation)
    assert (
        execution_grant_context(
            connection(scoped=False), context, tool=TOOL.name, invocation_id=invocation
        )
        is None
    )
    context = replace(
        context,
        trigger={
            "ameshActorId": str(uuid4()),
            "ameshAgentSessionId": str(uuid4()),
            "ameshToolGrants": {"gateway": "grant-a"},
        },
    )
    first = execution_grant_context(revision, context, tool=TOOL.name, invocation_id=invocation)
    retried = execution_grant_context(
        revision,
        replace(context, attempt=2, attempt_id=uuid4()),
        tool=TOOL.name,
        invocation_id=invocation,
    )
    assert first.invocation_id == retried.invocation_id
    assert first.session_id == retried.session_id
    assert first.attempt_id != retried.attempt_id
    assert first.attempt == 1 and retried.attempt == 2


def test_exchange_origin_and_existing_connection_digest_are_preserved() -> None:
    legacy = connection(scoped=False).spec
    assert "executionGrant" not in legacy.model_dump(mode="json", by_alias=True)
    assert legacy.digest == "sha256:" + canonical_hash(
        legacy.model_dump(mode="json", by_alias=True, exclude_none=True)
    )
    with pytest.raises(ValueError, match="share the connection endpoint origin"):
        McpConnectionSpec.model_validate(
            {
                **legacy.model_dump(mode="json", by_alias=True),
                "executionGrant": {"exchangeEndpoint": "https://other.test/exchange"},
            }
        )
