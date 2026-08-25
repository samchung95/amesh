from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from mcp.server import MCPServer

from amesh.domain import (
    AgentInvocationClaim,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    FailureCategory,
    McpConnectionRevision,
    McpConnectionSpec,
    McpToolImpact,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskExecutionFailure
from amesh.ports import ModelProviderRequest, ModelProviderResponse
from amesh.tasks import agent_llm_handler, agent_mcp_handler, discover_mcp_server


class MemoryAgentRepository:
    def __init__(self, connection: McpConnectionRevision | None = None) -> None:
        self.connection = connection
        self.invocations: dict[tuple[UUID, int, str, str], AgentInvocationRecord] = {}

    async def save_mcp_connection(
        self,
        tenant_id: str,
        spec: McpConnectionSpec,
        *,
        actor_id: str,
    ) -> McpConnectionRevision:
        del tenant_id, spec, actor_id
        raise NotImplementedError

    async def get_mcp_connection(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        *,
        revision: int | None = None,
    ) -> McpConnectionRevision:
        del revision
        if (
            self.connection is None
            or self.connection.tenant_id != tenant_id
            or self.connection.spec.namespace != namespace
            or self.connection.spec.key != key
        ):
            raise LookupError("connection not found")
        return self.connection

    async def list_mcp_connections(
        self,
        tenant_id: str,
        namespace: str,
    ) -> tuple[McpConnectionRevision, ...]:
        if (
            self.connection is None
            or self.connection.tenant_id != tenant_id
            or self.connection.spec.namespace != namespace
        ):
            return ()
        return (self.connection,)

    async def begin_invocation(self, start: AgentInvocationStart) -> AgentInvocationClaim:
        key = (start.task_run_id, start.attempt, start.kind.value, start.operation)
        existing = self.invocations.get(key)
        if existing is not None:
            if existing.request_hash != start.request_hash:
                raise ValueError("different request")
            return AgentInvocationClaim(record=existing, created=False)
        record = AgentInvocationRecord(
            **start.model_dump(mode="python", by_alias=True),
            state=AgentInvocationState.STARTED,
            startedAt=datetime.now(UTC),
        )
        self.invocations[key] = record
        return AgentInvocationClaim(record=record, created=True)

    async def complete_invocation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        state: AgentInvocationState,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> AgentInvocationRecord:
        selected_key, selected = next(
            (item for item in self.invocations.items() if item[1].invocation_id == invocation_id),
            (None, None),
        )
        if selected_key is None or selected is None or selected.tenant_id != tenant_id:
            raise LookupError("invocation not found")
        completed = selected.model_copy(
            update={
                "state": state,
                "result": result,
                "error": error,
                "completed_at": datetime.now(UTC),
            }
        )
        self.invocations[selected_key] = completed
        return completed


class FakeModelProvider:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.requests: list[ModelProviderRequest] = []

    async def invoke(self, request: ModelProviderRequest, credential: Any) -> ModelProviderResponse:
        assert credential.get_secret_value() == "openrouter-key"
        self.requests.append(request)
        return ModelProviderResponse(payload=self.responses.pop(0))


def execution_context(*, outputs: dict[str, dict[str, Any]] | None = None) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        namespace="agents.demo",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs=outputs or {},
        variables={},
        secret_scopes=("openrouter", "sensitive", "mcp-token"),
        secrets={
            "openrouter": "openrouter-key",
            "sensitive": "never-send-canary",
            "mcp-token": "mcp-key",
        },
    )


def provider_policy() -> dict[str, Any]:
    return {
        "provider": {
            "adapter": "openai-compatible",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "embeddingEndpoint": "https://openrouter.ai/api/v1/embeddings",
            "credentialRef": "openrouter",
        },
        "model": "openai/gpt-5.6-luna",
        "budget": {
            "maxTotalTokens": 64,
            "maxCompletionTokens": 32,
            "maxCostUsd": "0.01",
        },
        "dataHandling": {
            "egress": "REDACT_SECRETS",
            "promptRetention": "REDACTED",
        },
        "timeoutSeconds": 10,
        "contract": {"secretScopes": ["openrouter", "sensitive"]},
    }


def test_model_primitives_validate_outputs_enforce_policy_and_reuse_success() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "model": "openai/gpt-5.6-luna",
                    "choices": [{"message": {"content": "safe answer"}}],
                    "usage": {"total_tokens": 12, "cost": 0.001},
                },
                {
                    "model": "openai/gpt-5.6-luna",
                    "data": [{"embedding": [0.1, 0.2]}],
                    "usage": {"total_tokens": 4, "cost": 0.0001},
                },
                {
                    "model": "openai/gpt-5.6-luna",
                    "choices": [{"message": {"content": '{"answer": 42}'}}],
                    "usage": {"total_tokens": 8, "cost": 0.0004},
                },
                {
                    "model": "openai/gpt-5.6-luna",
                    "choices": [
                        {
                            "message": {
                                "tool_calls": [
                                    {
                                        "id": "call-1",
                                        "function": {
                                            "name": "lookup",
                                            "arguments": '{"query":"amesh"}',
                                        },
                                    }
                                ]
                            }
                        }
                    ],
                    "usage": {"total_tokens": 9, "cost": 0.0005},
                },
            ]
        )
        repository = MemoryAgentRepository()
        handler = agent_llm_handler(provider=provider, repository=repository)

        chat_context = execution_context()
        chat = TaskDefinition.model_validate(
            {
                "id": "chat",
                "type": "agent.chat",
                "prompt": "Keep never-send-canary private",
                **provider_policy(),
            }
        )
        first = await handler(chat, chat_context)
        second = await handler(chat, chat_context)
        assert first.output == second.output
        assert first.output["content"] == "safe answer"
        assert first.output["provenance"]["nondeterministic"] is True
        assert "never-send-canary" not in repr(first)
        assert provider.requests[0].payload["messages"][0]["content"] == ("Keep [REDACTED] private")
        assert len(provider.requests) == 1
        chat_key = next(iter(repository.invocations))
        repository.invocations[chat_key] = repository.invocations[chat_key].model_copy(
            update={
                "state": AgentInvocationState.STARTED,
                "result": None,
                "completed_at": None,
            }
        )
        with pytest.raises(TaskExecutionFailure, match="ambiguous external outcome") as restart:
            await handler(chat, chat_context)
        assert restart.value.evidence["agentInvocation"]["ambiguousExternalOutcome"] is True
        assert len(provider.requests) == 1

        embedding = TaskDefinition.model_validate(
            {
                "id": "embedding",
                "type": "agent.embedding",
                "input": "vectorize this",
                **provider_policy(),
            }
        )
        embedded = await handler(embedding, execution_context())
        assert embedded.output["embeddings"] == [[0.1, 0.2]]

        structured = TaskDefinition.model_validate(
            {
                "id": "structured",
                "type": "agent.structured",
                "prompt": "Return an answer",
                "outputSchema": {
                    "type": "object",
                    "properties": {"answer": {"type": "integer"}},
                    "required": ["answer"],
                    "additionalProperties": False,
                },
                **provider_policy(),
            }
        )
        result = await handler(structured, execution_context())
        assert result.output["structuredOutput"] == {"answer": 42}

        tool_call = TaskDefinition.model_validate(
            {
                "id": "tool-call",
                "type": "agent.toolCall",
                "prompt": "Choose a lookup",
                "tools": [
                    {
                        "name": "lookup",
                        "description": "Look up one record",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
                            "additionalProperties": False,
                        },
                    }
                ],
                **provider_policy(),
            }
        )
        proposed = await handler(tool_call, execution_context())
        assert proposed.output["toolCalls"] == [
            {"id": "call-1", "name": "lookup", "arguments": {"query": "amesh"}}
        ]

    asyncio.run(scenario())


def test_structured_model_output_and_budget_fail_deterministically() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": '{"answer":"wrong"}'}}],
                    "usage": {"total_tokens": 8, "cost": 0.0004},
                },
                {
                    "choices": [{"message": {"content": "too expensive"}}],
                    "usage": {"total_tokens": 12, "cost": 1.0},
                },
            ]
        )
        repository = MemoryAgentRepository()
        handler = agent_llm_handler(provider=provider, repository=repository)
        schema_task = TaskDefinition.model_validate(
            {
                "id": "invalid-structured",
                "type": "agent.structured",
                "prompt": "Return an integer",
                "outputSchema": {
                    "type": "object",
                    "properties": {"answer": {"type": "integer"}},
                    "required": ["answer"],
                },
                **provider_policy(),
            }
        )
        with pytest.raises(TaskExecutionFailure, match="failed schema") as invalid:
            await handler(schema_task, execution_context())
        assert invalid.value.category is FailureCategory.NON_RETRYABLE

        budget_task = TaskDefinition.model_validate(
            {"id": "budget", "type": "agent.chat", "prompt": "Answer", **provider_policy()}
        )
        with pytest.raises(TaskExecutionFailure, match="maxCostUsd") as over_budget:
            await handler(budget_task, execution_context())
        assert over_budget.value.category is FailureCategory.NON_RETRYABLE
        assert all(
            record.state is AgentInvocationState.FAILED
            for record in repository.invocations.values()
        )

    asyncio.run(scenario())


def test_model_failure_redacts_runtime_credentials_from_error_evidence() -> None:
    class LeakyProvider:
        async def invoke(
            self,
            request: ModelProviderRequest,
            credential: Any,
        ) -> ModelProviderResponse:
            del request
            raise RuntimeError(f"provider diagnostic contained {credential.get_secret_value()}")

    async def scenario() -> None:
        repository = MemoryAgentRepository()
        handler = agent_llm_handler(provider=LeakyProvider(), repository=repository)
        task = TaskDefinition.model_validate(
            {
                "id": "redacted-error",
                "type": "agent.chat",
                "prompt": "Answer",
                **provider_policy(),
            }
        )
        with pytest.raises(TaskExecutionFailure) as failed:
            await handler(task, execution_context())
        assert "openrouter-key" not in repr(failed.value)
        record = next(iter(repository.invocations.values()))
        assert record.error is not None
        assert "openrouter-key" not in record.error
        assert "[REDACTED]" in record.error

    asyncio.run(scenario())


def test_governed_mcp_call_pins_schema_and_deduplicates_attempt() -> None:
    calls = 0
    server = MCPServer("catalog", version="1.0.0")

    @server.tool()
    def add(left: int, right: int) -> dict[str, int]:
        nonlocal calls
        calls += 1
        return {"sum": left + right}

    async def scenario() -> None:
        discovery = await discover_mcp_server(
            "in-process://catalog",
            "mcp-key",
            target_resolver=lambda _endpoint: server,
        )
        pin = discovery.tools[0].model_copy(update={"impact": McpToolImpact.READ_ONLY})
        spec = McpConnectionSpec(
            key="catalog",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("add",),
            tools=(pin,),
        )
        connection = McpConnectionRevision(
            connectionId=uuid4(),
            tenantId="default",
            revision=1,
            digest=spec.digest,
            spec=spec,
            createdBy="author",
            createdAt=datetime.now(UTC),
        )
        repository = MemoryAgentRepository(connection)
        handler = agent_mcp_handler(
            lambda _endpoint: server,
            repository=repository,
        )
        task = TaskDefinition.model_validate(
            {
                "id": "mcp",
                "type": "agent.mcp",
                "connection": "catalog",
                "revision": 1,
                "tool": "add",
                "arguments": {"left": 2, "right": 3},
                "dataHandling": "DENY_SECRETS",
                "contract": {"secretScopes": ["mcp-token"]},
            }
        )
        context = execution_context()
        first = await handler(task, context)
        second = await handler(task, context)
        assert first.output["structuredContent"] == {"sum": 5}
        assert second.output == first.output
        assert calls == 1

    asyncio.run(scenario())


def test_governed_mcp_schema_drift_fails_before_tool_execution() -> None:
    calls = 0
    server = MCPServer("drift")

    @server.tool()
    def lookup(key: str) -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"value": key}

    async def scenario() -> None:
        discovery = await discover_mcp_server(
            "in-process://drift",
            "mcp-key",
            target_resolver=lambda _endpoint: server,
        )
        stale_pin = discovery.tools[0].model_copy(
            update={
                "input_schema": {
                    "type": "object",
                    "properties": {"record": {"type": "string"}},
                    "required": ["record"],
                },
                "impact": McpToolImpact.READ_ONLY,
            }
        )
        spec = McpConnectionSpec(
            key="drift",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("lookup",),
            tools=(stale_pin,),
        )
        repository = MemoryAgentRepository(
            McpConnectionRevision(
                connectionId=uuid4(),
                tenantId="default",
                revision=1,
                digest=spec.digest,
                spec=spec,
                createdBy="author",
                createdAt=datetime.now(UTC),
            )
        )
        handler = agent_mcp_handler(lambda _endpoint: server, repository=repository)
        task = TaskDefinition.model_validate(
            {
                "id": "drift",
                "type": "agent.mcp",
                "connection": "drift",
                "tool": "lookup",
                "arguments": {"record": "one"},
                "contract": {"secretScopes": ["mcp-token"]},
            }
        )
        with pytest.raises(TaskExecutionFailure, match="schema drifted") as drift:
            await handler(task, execution_context())
        assert drift.value.category is FailureCategory.INFRASTRUCTURE
        assert calls == 0

    asyncio.run(scenario())


def test_high_impact_mcp_tool_requires_direct_human_approval() -> None:
    server = MCPServer("danger")

    @server.tool()
    def destroy(name: str) -> dict[str, str]:
        return {"destroyed": name}

    async def scenario() -> None:
        discovery = await discover_mcp_server(
            "in-process://danger",
            "mcp-key",
            target_resolver=lambda _endpoint: server,
        )
        pin = discovery.tools[0].model_copy(update={"impact": McpToolImpact.HIGH_IMPACT})
        spec = McpConnectionSpec(
            key="danger",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("destroy",),
            tools=(pin,),
        )
        repository = MemoryAgentRepository(
            McpConnectionRevision(
                connectionId=uuid4(),
                tenantId="default",
                revision=1,
                digest=spec.digest,
                spec=spec,
                createdBy="author",
                createdAt=datetime.now(UTC),
            )
        )
        handler = agent_mcp_handler(lambda _endpoint: server, repository=repository)
        task = TaskDefinition.model_validate(
            {
                "id": "danger",
                "type": "agent.mcp",
                "dependsOn": ["approve"],
                "connection": "danger",
                "tool": "destroy",
                "arguments": {"name": "record"},
                "dataHandling": "DENY_SECRETS",
                "allowWrite": True,
                "approvalTask": "approve",
                "contract": {"secretScopes": ["mcp-token"]},
            }
        )
        with pytest.raises(PermissionError, match="APPROVED"):
            await handler(task, execution_context())
        approved = await handler(
            task,
            execution_context(outputs={"approve": {"decision": "APPROVED"}}),
        )
        assert approved.output["structuredContent"] == {"destroyed": "record"}

    asyncio.run(scenario())
