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
    AgentInvocationClaim,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
)
from amesh.domain.model_continuations import ProtectedModelContinuation
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext
from amesh.model_continuations import ModelContinuationProtector
from amesh.model_providers import (
    ModelProviderCapabilities,
    ModelProviderRegistry,
)
from amesh.ports import ModelProviderRequest, ModelProviderResponse
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


def capabilities(*, structured: bool = True) -> ModelProviderCapabilities:
    return ModelProviderCapabilities(
        structuredOutput=structured,
        tool=True,
        usage=True,
        cost=True,
        cancellation=True,
    )


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
