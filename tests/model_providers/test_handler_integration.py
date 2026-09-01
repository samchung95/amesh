from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from amesh.domain import (
    AgentInvocationAccounting,
    AgentInvocationClaim,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    ModelProviderSpec,
)
from amesh.domain.model_continuations import ProtectedModelContinuation
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskExecutionFailure
from amesh.model_continuations import ModelContinuationProtector
from amesh.model_providers import (
    ModelProviderCapabilities,
    ModelProviderRegistry,
)
from amesh.ports import ModelProviderRequest, ModelProviderResponse
from amesh.ports.model_engines import ModelEngineAccess
from amesh.tasks import agent_llm_handler


class CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def invoke(
        self, request: ModelProviderRequest, credential: SecretStr
    ) -> ModelProviderResponse:
        del request, credential
        self.calls += 1
        return ModelProviderResponse(
            payload={
                "model": "fixture/model",
                "choices": [{"message": {"content": "ready"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 3, "cost": "0.001"},
            }
        )


class EngineProvider:
    def __init__(self) -> None:
        self.calls = 0
        self.access: object | None = None
        self.requests: list[ModelProviderRequest] = []

    async def invoke(self, request: ModelProviderRequest, access: object) -> ModelProviderResponse:
        self.calls += 1
        self.access = access
        self.requests.append(request)
        return ModelProviderResponse(
            payload={
                "model": "fixture/model",
                "choices": [{"message": {"content": "ready"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 3, "cost": "0.001"},
            }
        )


class ContinuationProvider:
    def __init__(self) -> None:
        self.calls: list[str | None] = []

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        del credential
        continuation = (
            request.continuation.get_secret_value() if request.continuation is not None else None
        )
        self.calls.append(continuation)
        return ModelProviderResponse(
            payload={
                "model": "fixture/model",
                "choices": [{"message": {"content": "ready"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 3, "cost": "0.001"},
            },
            continuation=(SecretStr("hidden-provider-state") if continuation is None else None),
        )


class IndexedContinuationProvider:
    def __init__(self) -> None:
        self.requests: list[ModelProviderRequest] = []

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        del credential
        self.requests.append(request)
        return ModelProviderResponse(
            payload={
                "model": "fixture/model",
                "choices": [{"message": {"content": "ready"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 3, "cost": "0.001"},
            },
            continuation=SecretStr(
                json.dumps({"kind": "reasoning_content", "value": "hidden-provider-state"})
            ),
        )


class PayloadProvider:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls = 0

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        del request, credential
        self.calls += 1
        return ModelProviderResponse(payload=self.payload)


class TimeoutProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        del request, credential
        self.calls += 1
        raise TimeoutError("fixture provider timed out")


class MemoryInvocationRepository:
    def __init__(self) -> None:
        self.records: dict[UUID, AgentInvocationRecord] = {}
        self.continuations: dict[UUID, ProtectedModelContinuation] = {}

    async def begin_invocation(self, start: AgentInvocationStart) -> AgentInvocationClaim:
        existing = self.records.get(start.invocation_id)
        if existing is not None:
            return AgentInvocationClaim(record=existing, created=False)
        record = AgentInvocationRecord(
            **start.model_dump(mode="python"),
            state=AgentInvocationState.STARTED,
        )
        self.records[start.invocation_id] = record
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
        current = self.records[invocation_id]
        assert current.tenant_id == tenant_id
        completed = current.model_copy(update={"state": state, "result": result, "error": error})
        self.records[invocation_id] = completed
        if protected_continuation is not None:
            self.continuations[invocation_id] = protected_continuation
        return completed

    async def record_invocation_accounting(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
        accounting: AgentInvocationAccounting,
    ) -> AgentInvocationRecord:
        current = self.records[invocation_id]
        assert current.tenant_id == tenant_id
        if current.accounting is not None and current.accounting != accounting:
            raise RuntimeError("accounting conflicts")
        recorded = current.model_copy(update={"accounting": accounting})
        self.records[invocation_id] = recorded
        return recorded

    async def get_model_continuation(
        self,
        invocation_id: UUID,
        *,
        tenant_id: str,
    ) -> ProtectedModelContinuation | None:
        assert self.records[invocation_id].tenant_id == tenant_id
        return self.continuations.get(invocation_id)


def context() -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        namespace="agents.demo",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs={},
        variables={},
        secret_scopes=("fixture",),
        secrets={"fixture": "fixture-key"},
    )


def capabilities(*, structured: bool = True, opaque_continuation: bool = False) -> ModelProviderCapabilities:
    return ModelProviderCapabilities(
        structuredOutput=structured,
        tool=True,
        usage=True,
        cost=True,
        cancellation=True,
        opaqueContinuation=opaque_continuation,
    )


def model_task(*, task_type: str = "agent.chat", output_schema: bool = False) -> TaskDefinition:
    payload: dict[str, Any] = {
        "id": "model",
        "type": task_type,
        "prompt": "Return ready",
        "provider": {
            "adapter": "fixture",
            "endpoint": "https://fixture.example.test/v1/chat",
            "credentialRef": "fixture",
        },
        "model": "fixture/model",
        "budget": {"maxTotalTokens": 64, "maxCompletionTokens": 16, "maxCostUsd": "0.01"},
        "dataHandling": {"egress": "REDACT_SECRETS", "promptRetention": "HASH_ONLY"},
        "contract": {"secretScopes": ["fixture"]},
        "invocationKey": "accounting-test",
    }
    if output_schema:
        payload["outputSchema"] = {"type": "object", "required": ["ready"]}
    return TaskDefinition.model_validate(payload)


def engine_task(*, engine_scope: str = "codex-account") -> TaskDefinition:
    return TaskDefinition.model_validate(
        {
            "id": "engine-model",
            "type": "agent.chat",
            "prompt": "Return ready",
            "provider": {"adapter": "codex", "engineRef": engine_scope},
            "model": "fixture/model",
            "budget": {"maxTotalTokens": 64, "maxCompletionTokens": 16, "maxCostUsd": "0.01"},
            "dataHandling": {"egress": "REDACT_SECRETS", "promptRetention": "HASH_ONLY"},
            "contract": {"engineScopes": [engine_scope]},
        }
    )


def test_model_provider_spec_keeps_direct_shape_and_rejects_mixed_access() -> None:
    direct = model_task().model_extra["provider"]
    assert direct == {
        "adapter": "fixture",
        "endpoint": "https://fixture.example.test/v1/chat",
        "credentialRef": "fixture",
    }
    with pytest.raises(ValueError, match="cannot declare"):
        ModelProviderSpec(
            adapter="codex",
            engineRef="codex-account",
            endpoint="https://fixture.example.test/v1/chat",
        )


def test_engine_handler_uses_registered_adapter_and_typed_engine_access() -> None:
    async def scenario() -> None:
        provider = EngineProvider()
        registry = ModelProviderRegistry()
        registry.register("codex", "1.0.0", provider, capabilities())

        result = await agent_llm_handler(provider_registry=registry)(engine_task(), context())

        assert isinstance(result, TaskCompletion)
        assert provider.calls == 1
        assert isinstance(provider.access, ModelEngineAccess)
        assert provider.access.engine_ref == "codex-account"
        assert provider.requests[0].endpoint is None

    asyncio.run(scenario())


def test_provider_bounded_engine_omits_unsupported_exact_output_limit() -> None:
    async def scenario() -> None:
        provider = EngineProvider()
        registry = ModelProviderRegistry()
        engine_capabilities = capabilities().model_copy(
            update={"output": False, "cost": False}
        )
        registry.register("codex", "1.0.0", provider, engine_capabilities)
        base = {
            "id": "provider-bounded-engine",
            "type": "agent.chat",
            "prompt": "Return ready",
            "provider": {"adapter": "codex", "engineRef": "codex-account"},
            "model": "fixture/model",
            "ceilingMode": "PROVIDER_BOUNDED",
            "dataHandling": {"egress": "REDACT_SECRETS", "promptRetention": "HASH_ONLY"},
            "contract": {"engineScopes": ["codex-account"]},
        }
        handler = agent_llm_handler(provider_registry=registry)

        completed = await handler(TaskDefinition.model_validate(base), context())

        assert isinstance(completed, TaskCompletion)
        assert provider.calls == 1
        assert "max_completion_tokens" not in provider.requests[0].payload

        with pytest.raises(ValueError, match="output"):
            await handler(
                TaskDefinition.model_validate({**base, "maxCompletionTokens": 16}),
                context(),
            )
        assert provider.calls == 1

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("task", "message"),
    (
        (
            engine_task(),
            "contract.engineScopes",
        ),
        (
            TaskDefinition.model_validate(
                {
                    **engine_task().model_dump(mode="json", by_alias=True),
                    "provider": {"adapter": "missing-engine", "engineRef": "codex-account"},
                }
            ),
            "not registered",
        ),
    ),
)
def test_engine_authorization_and_registration_fail_before_adapter_io(
    task: TaskDefinition,
    message: str,
) -> None:
    async def scenario() -> None:
        provider = EngineProvider()
        registry = ModelProviderRegistry()
        active_task = task
        if "not registered" not in message:
            registry.register("codex", "1.0.0", provider, capabilities())
            active_task = TaskDefinition.model_validate(
                {
                    **task.model_dump(mode="json", by_alias=True),
                    "contract": {"engineScopes": []},
                }
            )
        handler = agent_llm_handler(provider_registry=registry)
        with pytest.raises(ValueError, match=message):
            await handler(active_task, context())
        assert provider.calls == 0

    asyncio.run(scenario())


def test_handler_exposes_provider_pin_and_normalized_usage() -> None:
    async def scenario() -> None:
        provider = CountingProvider()
        registry = ModelProviderRegistry()
        registry.register("fixture", "9.1.0", provider, capabilities())
        handler = agent_llm_handler(provider=provider, provider_registry=registry)
        task = TaskDefinition.model_validate(
            {
                "id": "chat",
                "type": "agent.chat",
                "prompt": "Say ready",
                "provider": {
                    "adapter": "fixture",
                    "endpoint": "https://fixture.example.test/v1/chat",
                    "credentialRef": "fixture",
                },
                "model": "fixture/model",
                "budget": {"maxTotalTokens": 64, "maxCompletionTokens": 16, "maxCostUsd": "0.01"},
                "dataHandling": {"egress": "REDACT_SECRETS", "promptRetention": "HASH_ONLY"},
                "contract": {"secretScopes": ["fixture"]},
            }
        )
        result = await handler(task, context())
        assert isinstance(result, TaskCompletion)
        assert provider.calls == 1
        assert result.output["provenance"]["providerRevision"] == "9.1.0"
        assert result.output["provenance"]["capabilities"]["usage"] is True
        assert result.output["usageNormalized"]["totalTokens"] == 5
        assert result.output["costNormalized"] == {"state": "billed", "amountUsd": "0.001"}

    asyncio.run(scenario())


def test_handler_negotiates_before_provider_io() -> None:
    async def scenario() -> None:
        provider = CountingProvider()
        registry = ModelProviderRegistry()
        registry.register("limited", "1.0.0", provider, capabilities(structured=False))
        handler = agent_llm_handler(provider=provider, provider_registry=registry)
        task = TaskDefinition.model_validate(
            {
                "id": "structured",
                "type": "agent.structured",
                "prompt": "Return ready",
                "outputSchema": {"type": "object"},
                "provider": {
                    "adapter": "limited",
                    "endpoint": "https://limited.example.test/v1/chat",
                    "credentialRef": "fixture",
                },
                "model": "limited/model",
                "budget": {"maxTotalTokens": 64, "maxCompletionTokens": 16, "maxCostUsd": "0.01"},
                "dataHandling": {"egress": "REDACT_SECRETS", "promptRetention": "HASH_ONLY"},
                "contract": {"secretScopes": ["fixture"]},
            }
        )
        with pytest.raises(ValueError, match="structured_output"):
            await handler(task, context())
        assert provider.calls == 0

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("task_type", "content", "expected_message"),
    (
        ("agent.structured", "not-json", "not valid JSON"),
        ("agent.chat", "", "did not contain assistant content"),
    ),
)
def test_failed_response_keeps_provider_accounting_before_content_validation(
    task_type: str,
    content: str,
    expected_message: str,
) -> None:
    async def scenario() -> None:
        provider = PayloadProvider(
            {
                "model": "fixture/model",
                "choices": [{"message": {"content": content}}],
                "usage": {
                    "prompt_tokens": 11,
                    "completion_tokens": 7,
                    "total_tokens": 18,
                    "completion_tokens_details": {"reasoning_tokens": 5},
                    "prompt_tokens_details": {"cached_tokens": 3},
                    "cache_write_tokens": 2,
                    "cost": "0.0042",
                },
            }
        )
        repository = MemoryInvocationRepository()
        registry = ModelProviderRegistry()
        registry.register("fixture", "9.1.0", provider, capabilities())
        handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
        )

        with pytest.raises(TaskExecutionFailure, match=expected_message) as raised:
            await handler(
                model_task(
                    task_type=task_type,
                    output_schema=task_type == "agent.structured",
                ),
                context(),
            )

        record = next(iter(repository.records.values()))
        assert record.state is AgentInvocationState.FAILED
        assert record.accounting is not None
        assert record.accounting.model_dump(mode="json", by_alias=True) == {
            "inputTokens": 11,
            "outputTokens": 7,
            "reasoningTokens": 5,
            "totalTokens": 18,
            "cacheReadTokens": 3,
            "cacheWriteTokens": 2,
            "costState": "billed",
            "costAmountUsd": "0.0042",
        }
        assert raised.value.result is not None
        assert raised.value.result["usageNormalized"]["reasoningTokens"] == 5
        assert raised.value.result["costUsd"] == "0.0042"
        assert "not-json" not in str(record.accounting)

    asyncio.run(scenario())


def test_failed_structured_invocation_replays_safe_rejection_and_accounting() -> None:
    async def scenario() -> None:
        provider = PayloadProvider(
            {
                "model": "fixture/model",
                "choices": [
                    {
                        "message": {
                            "content": "not-json",
                            "reasoning_details": [{"data": "hidden-reasoning"}],
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 11,
                    "completion_tokens": 7,
                    "total_tokens": 18,
                    "completion_tokens_details": {"reasoning_tokens": 5},
                    "cost": "0.0042",
                },
            }
        )
        repository = MemoryInvocationRepository()
        registry = ModelProviderRegistry()
        registry.register("fixture", "9.1.0", provider, capabilities())
        handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
        )
        task = model_task(task_type="agent.structured", output_schema=True)
        execution_context = context()

        with pytest.raises(TaskExecutionFailure, match="not valid JSON") as first:
            await handler(task, execution_context)

        stored = next(iter(repository.records.values()))
        assert stored.state is AgentInvocationState.FAILED
        assert stored.result is not None
        assert stored.result == first.value.result
        assert stored.result["modelOutputRejection"] == {
            "kind": "invalid_json",
            "path": "$",
            "message": "structured model output is not valid JSON",
        }
        assert stored.result["usageNormalized"]["totalTokens"] == 18
        assert stored.result["costNormalized"] == {
            "state": "billed",
            "amountUsd": "0.0042",
        }
        assert "usage" not in stored.result
        assert "choices" not in stored.result
        assert "hidden-reasoning" not in str(stored.result)

        restarted_handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
        )
        with pytest.raises(TaskExecutionFailure, match="not valid JSON") as replayed:
            await restarted_handler(task, execution_context)

        assert replayed.value.result == stored.result
        assert replayed.value.evidence["modelOutputRejection"] == stored.result[
            "modelOutputRejection"
        ]
        assert replayed.value.evidence["agentInvocation"]["accounting"]["costAmountUsd"] == "0.0042"
        assert provider.calls == 1

    asyncio.run(scenario())


def test_timed_out_invocation_settles_in_doubt_and_is_not_repeated() -> None:
    async def scenario() -> None:
        provider = TimeoutProvider()
        repository = MemoryInvocationRepository()
        registry = ModelProviderRegistry()
        registry.register("fixture", "9.1.0", provider, capabilities())
        handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
        )
        execution_context = context()
        task = model_task()

        with pytest.raises(TaskExecutionFailure) as timed_out:
            await handler(task, execution_context)
        record = next(iter(repository.records.values()))
        assert timed_out.value.category.value == "TIMED_OUT"
        assert record.state is AgentInvocationState.IN_DOUBT
        assert record.accounting is None

        with pytest.raises(TaskExecutionFailure, match="ambiguous external outcome") as replayed:
            await handler(task, execution_context)
        assert replayed.value.evidence["agentInvocation"]["state"] == "IN_DOUBT"
        assert provider.calls == 1

    asyncio.run(scenario())


def test_handler_resumes_encrypted_continuation_after_process_restart() -> None:
    async def scenario() -> None:
        provider = ContinuationProvider()
        registry = ModelProviderRegistry()
        registry.register(
            "fixture",
            "9.1.0",
            provider,
            capabilities().model_copy(update={"opaque_continuation": True}),
        )
        repository = MemoryInvocationRepository()
        key = Fernet.generate_key().decode("ascii")
        protector = ModelContinuationProtector(
            primary_key_id="current",
            keys={"current": key},
        )
        first_handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
            continuation_protector=protector,
        )
        common = {
            "type": "agent.chat",
            "prompt": "Say ready",
            "provider": {
                "adapter": "fixture",
                "revision": "9.1.0",
                "endpoint": "https://fixture.example.test/v1/chat",
                "credentialRef": "fixture",
            },
            "model": "fixture/model",
            "budget": {
                "maxTotalTokens": 64,
                "maxCompletionTokens": 16,
                "maxCostUsd": "0.01",
            },
            "dataHandling": {"egress": "REDACT_SECRETS", "promptRetention": "HASH_ONLY"},
            "contract": {"secretScopes": ["fixture"]},
        }
        first = await first_handler(
            TaskDefinition.model_validate({"id": "first", "invocationKey": "first", **common}),
            context(),
        )
        continuation = first.output["continuation"]
        source = UUID(continuation["invocationId"])
        assert "hidden-provider-state" not in str(first.output)
        assert b"hidden-provider-state" not in repository.continuations[source].ciphertext

        restarted_handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
            continuation_protector=ModelContinuationProtector(
                primary_key_id="current",
                keys={"current": key},
            ),
        )
        second = await restarted_handler(
            TaskDefinition.model_validate(
                {
                    "id": "second",
                    "invocationKey": "second",
                    "continuationFromInvocationId": str(source),
                    **common,
                }
            ),
            context(),
        )

        assert second.output["content"] == "ready"
        assert provider.calls == [None, "hidden-provider-state"]
        assert "hidden-provider-state" not in str(repository.records)

    asyncio.run(scenario())


def test_openai_compatible_adapter_preserves_reasoning_details_privately() -> None:
    from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

    posted: list[dict[str, Any]] = []

    async def respond(request: httpx.Request) -> httpx.Response:
        posted.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "tool requested",
                            "reasoning_details": [
                                {
                                    "type": "reasoning.encrypted",
                                    "data": "provider-ciphertext",
                                }
                            ],
                        }
                    }
                ]
            },
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client)
            first = await adapter.invoke(
                ModelProviderRequest(
                    operation="CHAT",
                    endpoint="https://provider.example.test/v1/chat",
                    model="fixture/model",
                    payload={"messages": [{"role": "user", "content": "begin"}]},
                    timeoutSeconds=5,
                ),
                SecretStr("credential"),
            )
            assert first.continuation is not None
            assert "provider-ciphertext" not in repr(first)
            await adapter.invoke(
                ModelProviderRequest(
                    operation="CHAT",
                    endpoint="https://provider.example.test/v1/chat",
                    model="fixture/model",
                    payload={
                        "messages": [
                            {"role": "user", "content": "begin"},
                            {"role": "assistant", "content": "tool requested"},
                            {"role": "tool", "content": "done"},
                        ]
                    },
                    timeoutSeconds=5,
                    continuation=first.continuation,
                ),
                SecretStr("credential"),
            )

    asyncio.run(scenario())
    assert posted[1]["messages"][1]["reasoning_details"] == [
        {"type": "reasoning.encrypted", "data": "provider-ciphertext"}
    ]


def test_handler_loads_multiple_indexed_continuations_after_protector_restart() -> None:
    async def scenario() -> None:
        provider = IndexedContinuationProvider()
        registry = ModelProviderRegistry()
        registry.register(
            "fixture",
            "1.0.0",
            provider,
            capabilities(opaque_continuation=True),
        )
        key = Fernet.generate_key().decode()
        protector = ModelContinuationProtector(
            primary_key_id="current",
            keys={"current": key},
        )
        handler = agent_llm_handler(
            provider=provider,
            repository=(repository := MemoryInvocationRepository()),
            provider_registry=registry,
            continuation_protector=protector,
        )
        first = await handler(model_task(), context())
        second = await handler(model_task(), context())
        first_source = first.output["continuation"]["invocationId"]
        second_source = second.output["continuation"]["invocationId"]

        restarted_handler = agent_llm_handler(
            provider=provider,
            repository=repository,
            provider_registry=registry,
            continuation_protector=ModelContinuationProtector(
                primary_key_id="current",
                keys={"current": key},
            ),
        )
        third_task = model_task()
        third_task = TaskDefinition.model_validate(
            {
                **third_task.model_dump(mode="json", by_alias=True),
                "continuationSources": [
                    {"messageIndex": 1, "invocationId": first_source},
                    {"messageIndex": 3, "invocationId": second_source},
                ],
            }
        )
        third = await restarted_handler(third_task, context())

        request = provider.requests[2]
        assert request.continuation is None
        assert [binding.message_index for binding in request.continuation_bindings] == [1, 3]
        assert all(
            binding.token.get_secret_value() == json.dumps(
                {"kind": "reasoning_content", "value": "hidden-provider-state"}
            )
            for binding in request.continuation_bindings
        )
        assert third.output["provenance"]["continuation"]["sources"] == [
            {
                "messageIndex": 1,
                "sourceInvocationId": first_source,
                "providerId": "fixture",
                "providerRevision": "1.0.0",
                "tokenDigest": repository.continuations[UUID(first_source)].token_digest,
            },
            {
                "messageIndex": 3,
                "sourceInvocationId": second_source,
                "providerId": "fixture",
                "providerRevision": "1.0.0",
                "tokenDigest": repository.continuations[UUID(second_source)].token_digest,
            },
        ]
        assert "hidden-provider-state" not in repr(request)

    asyncio.run(scenario())
