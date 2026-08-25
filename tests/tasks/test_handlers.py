from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx
from mcp.server import MCPServer

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext
from amesh.tasks import (
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
