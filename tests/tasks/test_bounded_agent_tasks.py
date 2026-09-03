from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from mcp.server import MCPServer

from amesh.domain import (
    AgentInvocationAccounting,
    AgentInvocationClaim,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    FailureCategory,
    McpConnectionRevision,
    McpConnectionSpec,
    McpToolImpact,
)
from amesh.domain.agent_progress import (
    AgentProgressActivity,
    AgentProgressStatus,
    AgentPublicSummaryDetail,
    AgentStatusDetail,
)
from amesh.domain.artifacts import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    build_artifact_reference,
)
from amesh.domain.image_inputs import (
    ImageArtifactRef,
    ImageContentPart,
    ImageDisplayMetadata,
    TextContentPart,
)
from amesh.domain.model_continuations import ProtectedModelContinuation
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskExecutionFailure
from amesh.model_providers import (
    DEEPSEEK_V4_FLASH_VISION_MODEL,
    ModelProviderCapabilities,
    ModelProviderRegistry,
)
from amesh.ports import (
    AgentProgressContext,
    ModelProviderProgressDelta,
    ModelProviderRequest,
    ModelProviderResponse,
    ModelProviderStreamEvent,
)
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
        protected_continuation: ProtectedModelContinuation | None = None,
    ) -> AgentInvocationRecord:
        assert protected_continuation is None
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

    async def record_invocation_accounting(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        accounting: AgentInvocationAccounting,
    ) -> AgentInvocationRecord:
        selected_key, selected = next(
            (item for item in self.invocations.items() if item[1].invocation_id == invocation_id),
            (None, None),
        )
        if selected_key is None or selected is None or selected.tenant_id != tenant_id:
            raise LookupError("invocation not found")
        if selected.accounting is not None and selected.accounting != accounting:
            raise RuntimeError("accounting conflicts")
        recorded = selected.model_copy(update={"accounting": accounting})
        self.invocations[selected_key] = recorded
        return recorded

    async def get_model_continuation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
    ) -> ProtectedModelContinuation | None:
        del invocation_id, tenant_id
        return None


class FakeModelProvider:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.requests: list[ModelProviderRequest] = []

    async def invoke(self, request: ModelProviderRequest, credential: Any) -> ModelProviderResponse:
        assert credential.get_secret_value() == "openrouter-key"
        self.requests.append(request)
        return ModelProviderResponse(payload=self.responses.pop(0))


class StreamingFakeModelProvider:
    def __init__(self, events: tuple[ModelProviderStreamEvent, ...]) -> None:
        self.events = events
        self.invoke_calls = 0

    async def invoke(self, request: ModelProviderRequest, credential: Any) -> ModelProviderResponse:
        del request, credential
        self.invoke_calls += 1
        return ModelProviderResponse(
            payload={
                "choices": [{"message": {"content": "unary fallback"}}],
                "usage": {"total_tokens": 1, "cost": 0.001},
            }
        )

    async def stream(
        self,
        request: ModelProviderRequest,
        credential: Any,
    ) -> AsyncIterator[ModelProviderStreamEvent]:
        del request, credential
        for event in self.events:
            yield event


class FailingStreamingModelProvider(StreamingFakeModelProvider):
    async def stream(
        self,
        request: ModelProviderRequest,
        credential: Any,
    ) -> AsyncIterator[ModelProviderStreamEvent]:
        del request, credential
        for event in self.events:
            yield event
        raise RuntimeError("stream disconnected")


class RecordingProgressSink:
    def __init__(self) -> None:
        self.frames: list[Any] = []
        self.closed: list[AgentProgressContext] = []

    async def append(self, context: AgentProgressContext, frame: Any) -> Any:
        del context
        self.frames.append(frame)
        return None

    async def close_active_segment(
        self, context: AgentProgressContext, *, occurred_at: datetime
    ) -> None:
        del occurred_at
        self.closed.append(context)


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
        task_types={"approve": "core.approval"},
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


def test_agent_llm_accepts_the_explicit_provider_contract() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "model": "openai/gpt-5.6-luna",
                    "choices": [{"message": {"content": "ready"}}],
                    "usage": {"total_tokens": 4, "cost": 0.001},
                }
            ]
        )
        policy = provider_policy()
        task = TaskDefinition.model_validate(
            {
                "id": "explicit-llm",
                "type": "agent.llm",
                "prompt": "Reply ready.",
                **policy,
            }
        )

        result = await agent_llm_handler(provider=provider)(task, execution_context())

        assert result.output["content"] == "ready"
        assert len(provider.requests) == 1

    asyncio.run(scenario())


def image_input() -> ImageArtifactRef:
    checksum = "a" * 64
    artifact = ArtifactRef(
        reference=build_artifact_reference("images/chart.png", 2, checksum),
        contentAddress=f"sha256:{checksum}",
        tenantId="default",
        namespace="agents.demo",
        path="images/chart.png",
        version=2,
        mediaType="image/png",
        sizeBytes=1024,
        checksumSha256=checksum,
        provenance=ArtifactProvenance(
            source="namespace-file",
            originNamespace="agents.demo",
            createdBy="test",
            createdAt=datetime(2026, 8, 31, tzinfo=UTC),
        ),
        retention=ArtifactRetention(),
    )
    return ImageArtifactRef(
        artifact=artifact,
        display=ImageDisplayMetadata(
            filename="chart.png",
            altText="Quarterly chart",
            widthPixels=640,
            heightPixels=480,
        ),
    )


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


def test_streaming_model_progress_is_forwarded_in_provider_order() -> None:
    async def scenario() -> None:
        context = execution_context()
        service_session_id = uuid4()
        attempt_session_id = uuid4()
        first_segment = uuid4()
        second_segment = uuid4()
        provider = StreamingFakeModelProvider(
            (
                ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.THINKING,
                        status=AgentProgressStatus.STARTED,
                        activityId="thinking-1",
                        segmentId=first_segment,
                        sourceSequence=1,
                        detail=AgentPublicSummaryDetail(
                            text="Contact alice@example.test and never-send-canary"
                        ),
                    )
                ),
                ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.TOOL,
                        status=AgentProgressStatus.STARTED,
                        activityId="tool-1",
                        sourceSequence=2,
                    )
                ),
                ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.THINKING,
                        status=AgentProgressStatus.STARTED,
                        activityId="thinking-2",
                        segmentId=second_segment,
                        sourceSequence=3,
                    )
                ),
                ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.THINKING,
                        status=AgentProgressStatus.COMPLETED,
                        activityId="thinking-2",
                        segmentId=second_segment,
                        sourceSequence=4,
                    )
                ),
                ModelProviderStreamEvent.response_event(
                    ModelProviderResponse(
                        payload={
                            "choices": [{"message": {"content": "streamed answer"}}],
                            "usage": {"total_tokens": 2, "cost": 0.001},
                        }
                    )
                ),
            )
        )
        sink = RecordingProgressSink()
        handler = agent_llm_handler(provider=provider, progress_sink=sink)
        task = TaskDefinition.model_validate(
            {
                "id": "streamed",
                "type": "agent.chat",
                "prompt": "Answer",
                "progressContext": AgentProgressContext(
                    tenantId=context.tenant_id,
                    serviceSessionId=service_session_id,
                    executionId=context.execution_id,
                    taskRunId=context.task_run_id,
                    attemptSessionId=attempt_session_id,
                    attempt=context.attempt,
                ).model_dump(mode="json", by_alias=True),
                **provider_policy(),
            }
        )

        result = await handler(task, context)
        assert result.output["content"] == "streamed answer"
        assert [frame.activity for frame in sink.frames] == [
            AgentProgressActivity.THINKING,
            AgentProgressActivity.TOOL,
            AgentProgressActivity.THINKING,
            AgentProgressActivity.THINKING,
        ]
        assert [frame.activity_id for frame in sink.frames] == [
            "thinking-1",
            "tool-1",
            "thinking-2",
            "thinking-2",
        ]
        assert sink.frames[0].source_id == sink.frames[1].source_id
        assert sink.frames[0].attempt_session_id == attempt_session_id
        assert sink.frames[0].attempt_session_id != context.attempt_id
        assert sink.frames[0].detail == AgentStatusDetail(
            code="model.processing",
            label="Model processing",
        )
        assert "alice@example.test" not in sink.frames[0].model_dump_json()
        assert "never-send-canary" not in sink.frames[0].model_dump_json()
        assert sink.frames[2].segment_id == second_segment
        assert provider.invoke_calls == 0

    asyncio.run(scenario())


def test_progress_context_requires_sink_and_streaming_falls_back_to_unary() -> None:
    async def scenario() -> None:
        context = execution_context()
        provider = StreamingFakeModelProvider(())
        task = TaskDefinition.model_validate(
            {
                "id": "fallback",
                "type": "agent.chat",
                "prompt": "Answer",
                **provider_policy(),
            }
        )
        result = await agent_llm_handler(provider=provider)(task, context)
        assert result.output["content"] == "unary fallback"
        assert provider.invoke_calls == 1

        task_with_context = task.model_copy(
            update={
                "progressContext": AgentProgressContext(
                    tenantId=context.tenant_id,
                    serviceSessionId=uuid4(),
                    executionId=context.execution_id,
                    taskRunId=context.task_run_id,
                    attemptSessionId=context.attempt_id,
                    attempt=context.attempt,
                ).model_dump(mode="json", by_alias=True)
            }
        )
        with pytest.raises(ValueError, match="requires an AgentProgressSink"):
            await agent_llm_handler(provider=provider)(task_with_context, context)

    asyncio.run(scenario())


def test_streaming_failure_closes_active_progress_segment() -> None:
    async def scenario() -> None:
        context = execution_context()
        segment_id = uuid4()
        provider = FailingStreamingModelProvider(
            (
                ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.THINKING,
                        status=AgentProgressStatus.STARTED,
                        activityId="thinking",
                        segmentId=segment_id,
                        sourceSequence=1,
                    )
                ),
                ModelProviderStreamEvent.accounting_event(
                    {
                        "usage": {
                            "prompt_tokens": 7,
                            "completion_tokens": 3,
                            "total_tokens": 10,
                            "cost": "0.002",
                        }
                    }
                ),
            )
        )
        sink = RecordingProgressSink()
        repository = MemoryAgentRepository()
        handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            progress_sink=sink,
        )
        task = TaskDefinition.model_validate(
            {
                "id": "stream-failure",
                "type": "agent.chat",
                "prompt": "Answer",
                "progressContext": AgentProgressContext(
                    tenantId=context.tenant_id,
                    serviceSessionId=uuid4(),
                    executionId=context.execution_id,
                    taskRunId=context.task_run_id,
                    attemptSessionId=context.attempt_id,
                    attempt=context.attempt,
                ).model_dump(mode="json", by_alias=True),
                **provider_policy(),
            }
        )
        with pytest.raises(TaskExecutionFailure, match="stream disconnected"):
            await handler(task, context)
        assert len(sink.frames) == 1
        assert len(sink.closed) == 1
        record = next(iter(repository.invocations.values()))
        assert record.state is AgentInvocationState.FAILED
        assert record.accounting is not None
        assert record.accounting.total_tokens == 10
        assert record.accounting.cost_amount_usd == Decimal("0.002")
        assert record.result is not None
        assert record.result["usageNormalized"]["totalTokens"] == 10

    asyncio.run(scenario())


def test_streaming_cancellation_persists_accounting_as_in_doubt() -> None:
    async def scenario() -> None:
        accounting_emitted = asyncio.Event()

        class CancellationStreamingModelProvider(StreamingFakeModelProvider):
            async def stream(
                self,
                request: ModelProviderRequest,
                credential: Any,
            ) -> AsyncIterator[ModelProviderStreamEvent]:
                del request, credential
                yield ModelProviderStreamEvent.accounting_event(
                    {
                        "usage": {
                            "prompt_tokens": 7,
                            "completion_tokens": 3,
                            "total_tokens": 10,
                            "cost": "0.002",
                        }
                    }
                )
                accounting_emitted.set()
                await asyncio.Future()

        context = execution_context()
        repository = MemoryAgentRepository()
        handler = agent_llm_handler(
            provider=CancellationStreamingModelProvider(()),
            repository=repository,
            progress_sink=RecordingProgressSink(),
        )
        task = TaskDefinition.model_validate(
            {
                "id": "stream-cancelled",
                "type": "agent.chat",
                "prompt": "Answer",
                "progressContext": AgentProgressContext(
                    tenantId=context.tenant_id,
                    serviceSessionId=uuid4(),
                    executionId=context.execution_id,
                    taskRunId=context.task_run_id,
                    attemptSessionId=context.attempt_id,
                    attempt=context.attempt,
                ).model_dump(mode="json", by_alias=True),
                **provider_policy(),
            }
        )
        running = asyncio.create_task(handler(task, context))
        await accounting_emitted.wait()
        running.cancel()
        with pytest.raises(asyncio.CancelledError):
            await running

        record = next(iter(repository.invocations.values()))
        assert record.state is AgentInvocationState.IN_DOUBT
        assert record.accounting is not None
        assert record.accounting.total_tokens == 10
        assert record.accounting.cost_amount_usd == Decimal("0.002")
        assert record.result is not None
        assert record.result["usageNormalized"]["totalTokens"] == 10
        assert record.result["costNormalized"] == {
            "state": "billed",
            "amountUsd": "0.002",
        }

    asyncio.run(scenario())


def test_structured_model_output_and_budget_fail_deterministically() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": "{not-json"}}],
                    "usage": {"total_tokens": 8, "cost": 0.0004},
                },
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
        with pytest.raises(TaskExecutionFailure, match="not valid JSON") as malformed:
            await handler(schema_task, execution_context())
        assert malformed.value.category is FailureCategory.NON_RETRYABLE

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


def test_deepseek_structured_output_uses_json_object_instruction_and_local_validation() -> None:
    async def scenario() -> None:
        schema = {
            "type": "object",
            "properties": {"answer": {"type": "integer"}},
            "required": ["answer"],
            "additionalProperties": False,
        }
        provider = FakeModelProvider(
            [
                {
                    "model": DEEPSEEK_V4_FLASH_VISION_MODEL,
                    "choices": [{"message": {"content": '{"answer":7}'}}],
                    "usage": {"total_tokens": 8, "cost": 0.0004},
                },
                {
                    "model": DEEPSEEK_V4_FLASH_VISION_MODEL,
                    "choices": [{"message": {"content": '{"answer":"wrong"}'}}],
                    "usage": {"total_tokens": 8, "cost": 0.0004},
                },
            ]
        )
        handler = agent_llm_handler(provider=provider)
        policy = provider_policy()
        policy["model"] = DEEPSEEK_V4_FLASH_VISION_MODEL
        task = TaskDefinition.model_validate(
            {
                "id": "deepseek-structured",
                "type": "agent.structured",
                "prompt": "Return an integer answer.",
                "outputSchema": schema,
                "schemaName": "integer_answer",
                **policy,
            }
        )

        result = await handler(task, execution_context())

        assert result.output["structuredOutput"] == {"answer": 7}
        request = provider.requests[0]
        assert request.payload["response_format"] == {"type": "json_object"}
        assert request.payload["max_tokens"] == 32
        assert "max_completion_tokens" not in request.payload
        assert request.payload["messages"][0]["role"] == "system"
        instruction = request.payload["messages"][0]["content"]
        assert 'Draft 2020-12 JSON Schema named "integer_answer"' in instruction
        assert '"additionalProperties":false' in instruction
        assert request.payload["messages"][1] == {
            "role": "user",
            "content": "Return an integer answer.",
        }
        assert result.output["provenance"]["modelProfile"]["structuredOutputDialect"] == (
            "json_object"
        )

        with pytest.raises(TaskExecutionFailure, match="failed schema"):
            await handler(task, execution_context())
        assert provider.requests[1].payload["response_format"] == {"type": "json_object"}

    asyncio.run(scenario())


def test_deepseek_output_limit_is_rejected_before_provider_io() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider([])
        handler = agent_llm_handler(provider=provider)
        policy = provider_policy()
        policy["budget"] = {
            "maxTotalTokens": 384_001,
            "maxCompletionTokens": 384_001,
            "maxCostUsd": "1.00",
        }
        task = TaskDefinition.model_validate(
            {
                "id": "deepseek-output-limit",
                "type": "agent.chat",
                "prompt": "Answer briefly.",
                **policy,
                "model": DEEPSEEK_V4_FLASH_VISION_MODEL,
            }
        )

        with pytest.raises(ValueError, match="output_tokens<=384000"):
            await handler(task, execution_context())
        assert provider.requests == []

    asyncio.run(scenario())


def test_provider_options_are_forwarded_as_a_top_level_provider_object() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": '{"answer":1}'}}],
                    "usage": {"total_tokens": 1, "cost": 0.0001},
                }
            ]
        )
        handler = agent_llm_handler(provider=provider)
        task = TaskDefinition.model_validate(
            {
                "id": "provider-options",
                "type": "agent.structured",
                "prompt": "Return an answer",
                "outputSchema": {
                    "type": "object",
                    "properties": {"answer": {"type": "integer"}},
                    "required": ["answer"],
                },
                "parameters": {"providerOptions": {"only": ["azure/eu"]}},
                **provider_policy(),
            }
        )

        await handler(task, execution_context())

        assert provider.requests[0].payload["provider"] == {"only": ["azure/eu"]}
        assert provider.requests[0].payload["model"] == "openai/gpt-5.6-luna"
        assert provider.requests[0].payload["messages"] == [
            {"role": "user", "content": "Return an answer"}
        ]
        assert "outputSchema" not in provider.requests[0].payload

    asyncio.run(scenario())


def test_bounded_model_nodes_preserve_ordered_image_parts_and_negotiate_modality() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": "image understood"}}],
                    "usage": {"total_tokens": 2, "cost": 0.0001},
                }
            ]
        )
        registry = ModelProviderRegistry()
        registry.register(
            "openai-compatible",
            "1.0.0",
            provider,
            ModelProviderCapabilities(
                structuredOutput=True,
                tool=True,
                usage=True,
                cost=True,
                imageInput=True,
            ),
        )
        handler = agent_llm_handler(provider=provider, provider_registry=registry)
        image = image_input()
        task = TaskDefinition.model_validate(
            {
                "id": "multimodal-chat",
                "type": "agent.chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            TextContentPart(text="Compare this chart"),
                            ImageContentPart(image=image),
                            TextContentPart(text=" with the target."),
                        ],
                    }
                ],
                **provider_policy(),
            }
        )

        await handler(task, execution_context())

        assert provider.requests[0].payload["messages"] == [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Compare this chart"},
                    {
                        "type": "image_ref",
                        "image": image.model_dump(mode="json", by_alias=True),
                    },
                    {"type": "text", "text": " with the target."},
                ],
            }
        ]
        assert provider.requests[0].tenant_id == "default"

    asyncio.run(scenario())


def test_bounded_model_nodes_reject_image_input_before_provider_io() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider([])
        registry = ModelProviderRegistry()
        registry.register(
            "text-only",
            "1.0.0",
            provider,
            ModelProviderCapabilities(usage=True, cost=True, imageInput=False),
        )
        handler = agent_llm_handler(provider=provider, provider_registry=registry)
        image = image_input()
        task = TaskDefinition.model_validate(
            {
                "id": "unsupported-image-chat",
                "type": "agent.chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            TextContentPart(text="Describe"),
                            ImageContentPart(image=image),
                        ],
                    }
                ],
                **provider_policy(),
                "provider": {
                    **provider_policy()["provider"],
                    "adapter": "text-only",
                },
            }
        )

        with pytest.raises(ValueError, match="image_input"):
            await handler(task, execution_context())
        assert provider.requests == []

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("provider_tag", "expected_parameter", "excluded_parameter"),
    [
        ("azure/eu", "max_completion_tokens", "max_tokens"),
        ("openai", "max_tokens", "max_completion_tokens"),
    ],
)
def test_luna_pinned_provider_selects_its_completion_token_parameter(
    provider_tag: str,
    expected_parameter: str,
    excluded_parameter: str,
) -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": '{"answer":1}'}}],
                    "usage": {"total_tokens": 1, "cost": 0.0001},
                }
            ]
        )
        handler = agent_llm_handler(provider=provider)
        task = TaskDefinition.model_validate(
            {
                "id": "provider-completion-parameter",
                "type": "agent.structured",
                "prompt": "Return an answer",
                "outputSchema": {
                    "type": "object",
                    "properties": {"answer": {"type": "integer"}},
                    "required": ["answer"],
                },
                "parameters": {"providerOptions": {"only": [provider_tag]}},
                **provider_policy(),
            }
        )

        await handler(task, execution_context())

        request = provider.requests[0]
        assert request.payload["provider"] == {"only": [provider_tag]}
        assert request.payload[expected_parameter] == 32
        assert excluded_parameter not in request.payload

    asyncio.run(scenario())


def test_request_options_are_forwarded_as_bounded_top_level_extensions() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": '{"answer":1}'}}],
                    "usage": {"total_tokens": 1, "cost": 0.0001},
                }
            ]
        )
        handler = agent_llm_handler(provider=provider)
        task = TaskDefinition.model_validate(
            {
                "id": "request-options",
                "type": "agent.structured",
                "prompt": "Return an answer",
                "outputSchema": {
                    "type": "object",
                    "properties": {"answer": {"type": "integer"}},
                    "required": ["answer"],
                },
                "parameters": {"requestOptions": {"plugins": [{"id": "response-healing"}]}},
                **provider_policy(),
            }
        )

        await handler(task, execution_context())

        assert provider.requests[0].payload["plugins"] == [{"id": "response-healing"}]
        assert provider.requests[0].payload["response_format"]["type"] == "json_schema"
        assert provider.requests[0].payload["max_completion_tokens"] == 32
        assert "max_tokens" not in provider.requests[0].payload

    asyncio.run(scenario())


def test_provider_options_reject_non_objects_and_oversized_objects() -> None:
    async def scenario() -> None:
        handler = agent_llm_handler(provider=FakeModelProvider([]))
        base = {
            "id": "invalid-provider-options",
            "type": "agent.chat",
            "prompt": "Answer",
            **provider_policy(),
        }
        for value in ([], "azure/eu", {f"option-{index}": True for index in range(17)}):
            with pytest.raises(ValueError, match="providerOptions"):
                await handler(
                    TaskDefinition.model_validate(
                        {**base, "parameters": {"providerOptions": value}}
                    ),
                    execution_context(),
                )

    asyncio.run(scenario())


def test_request_options_cannot_override_amesh_owned_request_fields() -> None:
    async def scenario() -> None:
        handler = agent_llm_handler(provider=FakeModelProvider([]))
        base = {
            "id": "reserved-request-option",
            "type": "agent.chat",
            "prompt": "Answer",
            **provider_policy(),
        }
        with pytest.raises(ValueError, match="AMESH-owned"):
            await handler(
                TaskDefinition.model_validate(
                    {**base, "parameters": {"requestOptions": {"messages": []}}}
                ),
                execution_context(),
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


def test_session_invocation_keys_allow_multiple_model_turns_and_reuse_each_turn() -> None:
    async def scenario() -> None:
        provider = FakeModelProvider(
            [
                {
                    "choices": [{"message": {"content": '{"answer":1}'}}],
                    "usage": {"total_tokens": 4, "cost": 0.0001},
                },
                {
                    "choices": [{"message": {"content": '{"answer":2}'}}],
                    "usage": {"total_tokens": 5, "cost": 0.0002},
                },
            ]
        )
        repository = MemoryAgentRepository()
        handler = agent_llm_handler(provider=provider, repository=repository)
        context = execution_context()
        base = {
            "id": "session-turn",
            "type": "agent.structured",
            "prompt": "Return an answer",
            "outputSchema": {"type": "object", "properties": {"answer": {"type": "integer"}}},
            **provider_policy(),
        }
        first_task = TaskDefinition.model_validate({**base, "invocationKey": "session:one:turn:1"})
        second_task = TaskDefinition.model_validate({**base, "invocationKey": "session:one:turn:2"})

        first = await handler(first_task, context)
        second = await handler(second_task, context)
        repeated = await handler(first_task, context)

        assert (
            first.output["structuredOutput"] == repeated.output["structuredOutput"] == {"answer": 1}
        )
        assert second.output["structuredOutput"] == {"answer": 2}
        assert len(provider.requests) == 2
        assert len(repository.invocations) == 2

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


def test_governed_mcp_application_error_is_returned_to_agent() -> None:
    server = MCPServer("catalog-errors")

    @server.tool()
    def lookup(key: str) -> dict[str, str]:
        raise RuntimeError(f"record {key!r} is unavailable")

    async def scenario() -> None:
        discovery = await discover_mcp_server(
            "in-process://catalog-errors",
            "mcp-key",
            target_resolver=lambda _endpoint: server,
        )
        pin = discovery.tools[0].model_copy(update={"impact": McpToolImpact.READ_ONLY})
        spec = McpConnectionSpec(
            key="catalog-errors",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("lookup",),
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
        handler = agent_mcp_handler(
            lambda _endpoint: server,
            repository=repository,
        )
        task = TaskDefinition.model_validate(
            {
                "id": "mcp-error",
                "type": "agent.mcp",
                "connection": "catalog-errors",
                "revision": 1,
                "tool": "lookup",
                "arguments": {"key": "MSFT"},
                "dataHandling": "DENY_SECRETS",
                "contract": {"secretScopes": ["mcp-token"]},
            }
        )

        result = await handler(task, execution_context())

        assert isinstance(result, TaskCompletion)
        assert result.output["isError"] is True
        assert result.output["content"][0]["text"] == (
            "Error executing tool lookup: record 'MSFT' is unavailable"
        )
        invocation = next(iter(repository.invocations.values()))
        assert invocation.state is AgentInvocationState.FAILED

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


def test_governed_mcp_model_argument_schema_error_is_recoverable_only_when_marked() -> None:
    calls = 0
    server = MCPServer("model-arguments")

    @server.tool()
    def lookup(key: str) -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"value": key}

    async def scenario() -> None:
        discovery = await discover_mcp_server(
            "in-process://model-arguments",
            "mcp-key",
            target_resolver=lambda _endpoint: server,
        )
        pin = discovery.tools[0].model_copy(update={"impact": McpToolImpact.READ_ONLY})
        spec = McpConnectionSpec(
            key="model-arguments",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("lookup",),
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
        handler = agent_mcp_handler(
            lambda _endpoint: server,
            repository=repository,
        )
        base = {
            "id": "mcp-model-arguments",
            "type": "agent.mcp",
            "connection": "model-arguments",
            "revision": 1,
            "tool": "lookup",
            "arguments": {},
            "contract": {"secretScopes": ["mcp-token"]},
        }

        with pytest.raises(TaskExecutionFailure, match="arguments failed schema"):
            await handler(TaskDefinition.model_validate(base), execution_context())
        assert calls == 0

        recovered = await handler(
            TaskDefinition.model_validate({**base, "_ameshModelProposed": True}),
            execution_context(),
        )
        assert isinstance(recovered, TaskCompletion)
        assert recovered.output["isError"] is True
        assert "arguments failed schema" in recovered.output["content"][0]["text"]
        assert calls == 0
        assert repository.invocations == {}

    asyncio.run(scenario())


def test_governed_mcp_invocation_identity_is_stable_across_attempts() -> None:
    calls = 0
    server = MCPServer("stable")

    @server.tool()
    def add(left: int, right: int) -> dict[str, int]:
        nonlocal calls
        calls += 1
        return {"sum": left + right}

    async def scenario() -> None:
        discovery = await discover_mcp_server(
            "in-process://stable",
            "mcp-key",
            target_resolver=lambda _endpoint: server,
        )
        pin = discovery.tools[0].model_copy(update={"impact": McpToolImpact.READ_ONLY})
        spec = McpConnectionSpec(
            key="stable",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("add",),
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
                "id": "mcp",
                "type": "agent.mcp",
                "connection": "stable",
                "revision": 1,
                "tool": "add",
                "arguments": {"left": 2, "right": 3},
                "contract": {"secretScopes": ["mcp-token"]},
            }
        )
        first_context = execution_context()
        second_context = replace(
            first_context,
            attempt_id=uuid4(),
        )
        first = await handler(task, first_context)
        second = await handler(task, second_context)
        assert first.output == second.output
        assert calls == 1

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
        fake_approved_context = execution_context(
            outputs={"approve": {"decision": "APPROVED"}},
        )
        with pytest.raises(PermissionError, match="APPROVED"):
            await handler(task, fake_approved_context)
        approved_context = execution_context()
        approved_context = replace(
            approved_context,
            outputs={
                "approve": {
                    "taskType": "core.approval",
                    "executionId": str(approved_context.execution_id),
                    "decision": "APPROVED",
                }
            },
        )
        approved = await handler(task, approved_context)
        assert approved.output["structuredContent"] == {"destroyed": "record"}

    asyncio.run(scenario())
