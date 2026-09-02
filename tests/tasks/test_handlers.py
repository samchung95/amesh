from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx
import pytest
from mcp.server import MCPServer

import amesh.tasks.mcp_client as mcp_client_tasks
from amesh.domain import FailureCategory
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskExecutionFailure
from amesh.tasks import (
    HttpTaskPolicy,
    OpenAICompatibleConfig,
    agent_llm_handler,
    agent_mcp_handler,
    core_http_handler,
)


def context() -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs={},
        variables={},
    )


def test_core_http_returns_normalized_json_response() -> None:
    async def respond(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.headers["x-test"] == "amesh"
        assert request.content == b'{"message":"hello"}'
        return httpx.Response(
            201,
            headers={"content-type": "application/json"},
            json={"accepted": True},
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            handler = core_http_handler(client)
            task = TaskDefinition.model_validate(
                {
                    "id": "http",
                    "type": "core.http",
                    "url": "https://example.test/hook",
                    "method": "POST",
                    "headers": {"x-test": "amesh"},
                    "body": {"message": "hello"},
                }
            )
            result = await handler(task, context())
        assert result["statusCode"] == 201
        assert result["json"] == {"accepted": True}

    asyncio.run(scenario())


def test_agent_llm_uses_openrouter_luna_contract() -> None:
    async def respond(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
        payload = request.read().decode()
        assert '"model":"openai/gpt-5.6-luna"' in payload
        return httpx.Response(
            200,
            json={
                "model": "openai/gpt-5.6-luna",
                "choices": [{"message": {"role": "assistant", "content": "ready"}}],
                "usage": {"total_tokens": 4},
            },
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            handler = agent_llm_handler(
                OpenAICompatibleConfig(api_key="test-key"),
                client,
            )
            task = TaskDefinition.model_validate(
                {
                    "id": "llm",
                    "type": "agent.llm",
                    "prompt": "Reply ready",
                    "maxCompletionTokens": 16,
                }
            )
            result = await handler(task, context())
            assert result.output["content"] == "ready"
            assert result.output["model"] == "openai/gpt-5.6-luna"
            assert result.output["usage"] == {"total_tokens": 4}
            assert result.output["provenance"]["nondeterministic"] is True

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("code", "category"),
    [
        (429, FailureCategory.RETRYABLE),
        (502, FailureCategory.RETRYABLE),
        (401, FailureCategory.NON_RETRYABLE),
    ],
)
def test_agent_llm_classifies_provider_error_envelope_by_effective_status(
    code: int, category: FailureCategory
) -> None:
    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "error": {
                    "message": "upstream diagnostic credential-secret",
                    "code": code,
                }
            },
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            handler = agent_llm_handler(
                OpenAICompatibleConfig(api_key="credential-secret"),
                client,
            )
            task = TaskDefinition.model_validate(
                {
                    "id": "llm-error-envelope",
                    "type": "agent.llm",
                    "prompt": "Reply ready",
                    "maxCompletionTokens": 16,
                }
            )
            with pytest.raises(TaskExecutionFailure) as caught:
                await handler(task, context())
            assert caught.value.category is category
            assert "credential-secret" not in str(caught.value)
            assert "upstream diagnostic [REDACTED]" in str(caught.value)
            assert caught.value.evidence is not None
            assert caught.value.evidence["providerError"] == {
                "status": code,
                "type": "provider_error",
                "code": str(code),
                "message": "upstream diagnostic [REDACTED]",
            }

    asyncio.run(scenario())


def test_agent_llm_preserves_sanitized_actual_http_error_evidence() -> None:
    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "type": "invalid_request_error",
                    "code": "unsupported_field",
                    "message": "bad request credential-secret",
                }
            },
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            handler = agent_llm_handler(
                OpenAICompatibleConfig(api_key="credential-secret"),
                client,
            )
            task = TaskDefinition.model_validate(
                {
                    "id": "llm-http-error",
                    "type": "agent.llm",
                    "prompt": "private prompt",
                    "maxCompletionTokens": 16,
                }
            )
            with pytest.raises(TaskExecutionFailure) as caught:
                await handler(task, context())
            assert caught.value.category is FailureCategory.NON_RETRYABLE
            assert caught.value.evidence is not None
            assert caught.value.evidence["providerError"] == {
                "status": 400,
                "type": "invalid_request_error",
                "code": "unsupported_field",
                "message": "bad request [REDACTED]",
            }
            serialized = str(caught.value.evidence)
            assert "credential-secret" not in serialized
            assert "private prompt" not in serialized

    asyncio.run(scenario())


def test_agent_mcp_calls_official_in_process_server() -> None:
    server = MCPServer("amesh-test")

    @server.tool()
    def add(left: int, right: int) -> dict[str, int]:
        return {"sum": left + right}

    async def scenario() -> None:
        handler = agent_mcp_handler(lambda endpoint: server)
        task = TaskDefinition.model_validate(
            {
                "id": "mcp",
                "type": "agent.mcp",
                "endpoint": "in-process://test",
                "tool": "add",
                "arguments": {"left": 2, "right": 3},
            }
        )
        result = await handler(task, context())
        assert result["structuredContent"] == {"sum": 5}

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("timeout_configuration", "expected_timeout"),
    [
        ({}, 30),
        ({"timeoutMode": "DISABLED"}, None),
        ({"timeoutSeconds": 7}, 7),
    ],
)
def test_agent_mcp_propagates_effective_task_timeout(
    timeout_configuration: dict[str, object],
    expected_timeout: float | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = MCPServer("amesh-timeout-test")

    @server.tool()
    def echo(value: str) -> dict[str, str]:
        return {"value": value}

    real_client = mcp_client_tasks.Client
    observed: list[float | None] = []

    def recording_client(*args: object, **kwargs: object):
        timeout = kwargs.get("read_timeout_seconds")
        assert timeout is None or isinstance(timeout, (int, float))
        observed.append(timeout)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(mcp_client_tasks, "Client", recording_client)

    async def scenario() -> None:
        handler = agent_mcp_handler(lambda _endpoint: server)
        task = TaskDefinition.model_validate(
            {
                "id": "mcp-timeout",
                "type": "agent.mcp",
                "endpoint": "in-process://test",
                "tool": "echo",
                "arguments": {"value": "ready"},
                **timeout_configuration,
            }
        )
        result = await handler(task, context())
        assert result["structuredContent"] == {"value": "ready"}

    asyncio.run(scenario())

    assert observed == [expected_timeout]


def test_disabled_mcp_http_transport_omits_httpx_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    class AsyncContext:
        def __init__(self, value: object) -> None:
            self.value = value

        async def __aenter__(self) -> object:
            return self.value

        async def __aexit__(self, *_args: object) -> None:
            return None

    def unexpected_timeout(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("httpx.Timeout must not be built for disabled timeouts")

    def http_client(**kwargs: object) -> AsyncContext:
        observed["httpxTimeout"] = kwargs["timeout"]
        return AsyncContext(object())

    def mcp_client(*_args: object, **kwargs: object) -> AsyncContext:
        observed["mcpReadTimeout"] = kwargs["read_timeout_seconds"]
        return AsyncContext(object())

    monkeypatch.setattr(
        mcp_client_tasks, "validate_http_destination", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(mcp_client_tasks.httpx2, "Timeout", unexpected_timeout)
    monkeypatch.setattr(mcp_client_tasks.httpx2, "AsyncClient", http_client)
    monkeypatch.setattr(
        mcp_client_tasks, "streamable_http_client", lambda *_args, **_kwargs: object()
    )
    monkeypatch.setattr(mcp_client_tasks, "Client", mcp_client)

    async def scenario() -> None:
        async with mcp_client_tasks._client(
            "https://mcp.example.test",
            "credential",
            timeout_seconds=None,
            target_resolver=None,
            http_policy=None,
        ):
            pass

    asyncio.run(scenario())

    assert observed == {"httpxTimeout": None, "mcpReadTimeout": None}


def test_legacy_mcp_validates_network_destination_before_resolver() -> None:
    resolver_calls = 0

    def resolver(_endpoint: str) -> MCPServer:
        nonlocal resolver_calls
        resolver_calls += 1
        return MCPServer("unexpected")

    async def scenario() -> None:
        handler = agent_mcp_handler(
            resolver,
            http_policy=HttpTaskPolicy(allowed_hosts=("allowed.example",)),
        )
        task = TaskDefinition.model_validate(
            {
                "id": "mcp",
                "type": "agent.mcp",
                "endpoint": "https://blocked.example/mcp",
                "tool": "add",
            }
        )
        with pytest.raises(ValueError, match="egress allowlist"):
            await handler(task, context())

    asyncio.run(scenario())
    assert resolver_calls == 0
