from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any

import pytest
from pydantic import SecretStr

from amesh.model_providers import (
    DEEPSEEK_V4_FLASH_VISION_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    OPENROUTER_MODEL_CAPABILITY_PROFILES,
    CapabilityRequirement,
    CompletionTokenParameter,
    CostBudgetError,
    ModelCapabilityProfile,
    ModelProviderCapabilities,
    ModelProviderRegistry,
    NormalizationState,
    OpaqueContinuation,
    ProviderCapability,
    ProviderNegotiationError,
    ProviderRevisionConflict,
    RetryableProviderError,
    StructuredOutputDialect,
    enforce_cost_budget,
    invoke_with_retry,
    invoke_with_timeout,
    normalize_cost,
    normalize_prompt_cache,
    normalize_usage,
)
from amesh.ports import ModelProviderRequest, ModelProviderResponse


class ScriptedProvider:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.response = response or {"choices": [{"message": {"content": "ok"}}]}
        self.calls = 0
        self.failures = 0
        self.wait = 0.0

    async def invoke(
        self, request: ModelProviderRequest, credential: SecretStr
    ) -> ModelProviderResponse:
        del request, credential
        self.calls += 1
        if self.wait:
            await asyncio.sleep(self.wait)
        if self.failures:
            self.failures -= 1
            raise RetryableProviderError("temporary provider failure")
        return ModelProviderResponse(payload=self.response)


class DeepSeekCompatibleFixtureProvider:
    """Independent fixture for DeepSeek's OpenAI-compatible reasoning response shape."""

    def __init__(self) -> None:
        self.calls = 0
        self.response = {
            "choices": [
                {
                    "message": {
                        "content": "x" * 8192,
                        "reasoning_content": "opaque-reasoning-history",
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "function": {"name": "lookup", "arguments": '{"key":"x"}'},
                            }
                        ],
                    }
                }
            ],
            "usage": {"prompt_tokens": 4, "completion_tokens": 8192, "cost": "0.01"},
            "continuation": "opaque-fixture-value",
        }

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        assert request.payload["messages"]
        assert credential.get_secret_value() == "fixture"
        self.calls += 1
        return ModelProviderResponse(payload=self.response)


ALL_CAPABILITIES = ModelProviderCapabilities(
    structuredOutput=True,
    tool=True,
    streaming=True,
    opaqueContinuation=True,
    cancellation=True,
    usage=True,
    cache=True,
    cost=True,
    retry=True,
    imageInput=True,
    contextWindowTokens=32_000,
    maxOutputTokens=16_000,
)


def test_image_modality_is_negotiated_before_provider_io() -> None:
    provider = ScriptedProvider()
    registry = ModelProviderRegistry()
    registry.register(
        "text-only",
        "1.0.0",
        provider,
        ModelProviderCapabilities(imageInput=False),
    )

    requirement = CapabilityRequirement(inputModalities={"text", "image"})
    assert ProviderCapability.IMAGE_INPUT in requirement.required
    with pytest.raises(ProviderNegotiationError, match="image_input"):
        registry.negotiate("text-only", requirement, revision="1.0.0")
    assert provider.calls == 0


def request() -> ModelProviderRequest:
    return ModelProviderRequest(
        operation="CHAT",
        endpoint="https://provider.example.test/v1/chat",
        model="fixture/model",
        payload={"messages": [{"role": "user", "content": "hello"}]},
        timeoutSeconds=0.05,
    )


def test_registry_pins_revision_and_rejects_incompatible_request_before_io() -> None:
    provider = ScriptedProvider()
    registry = ModelProviderRegistry()
    registration = registry.register("fixture", "1.0.0", provider, ALL_CAPABILITIES)

    pin = registry.negotiate(
        "fixture",
        CapabilityRequirement(required=frozenset({ProviderCapability.STRUCTURED_OUTPUT})),
        revision="1.0.0",
    )
    assert (pin.provider_id, pin.revision, pin.digest) == (
        "fixture",
        "1.0.0",
        registration.digest,
    )
    assert provider.calls == 0

    limited = registry.register(
        "limited",
        "1.0.0",
        provider,
        ModelProviderCapabilities(structuredOutput=False),
    )
    with pytest.raises(ProviderNegotiationError, match="structured_output"):
        registry.negotiate(
            limited.provider_id,
            CapabilityRequirement(required=frozenset({ProviderCapability.STRUCTURED_OUTPUT})),
        )
    assert provider.calls == 0

    with pytest.raises(ProviderRevisionConflict):
        registry.register(
            "fixture",
            "1.0.0",
            ScriptedProvider(),
            ModelProviderCapabilities(structuredOutput=False),
        )


def test_registry_pins_exact_openrouter_model_capabilities_and_dialect() -> None:
    provider = ScriptedProvider()
    registry = ModelProviderRegistry()
    registry.register(
        "openai-compatible",
        "1.0.0",
        provider,
        ALL_CAPABILITIES.model_copy(
            update={"context_window_tokens": None, "max_output_tokens": None}
        ),
    )
    for profile in OPENROUTER_MODEL_CAPABILITY_PROFILES:
        registry.register_model_profile("openai-compatible", "1.0.0", profile)

    luna = registry.resolve_model_profile(
        "openai-compatible",
        DEFAULT_OPENROUTER_MODEL,
        revision="1.0.0",
    )
    deepseek = registry.resolve_model_profile(
        "openai-compatible",
        DEEPSEEK_V4_FLASH_VISION_MODEL,
        revision="1.0.0",
    )

    assert luna.structured_output_dialect is StructuredOutputDialect.JSON_SCHEMA
    assert luna.completion_token_parameter is CompletionTokenParameter.MAX_COMPLETION_TOKENS
    assert (
        luna.completion_token_parameter_for({"only": ["azure/eu"]})
        is CompletionTokenParameter.MAX_COMPLETION_TOKENS
    )
    assert (
        luna.completion_token_parameter_for({"only": ["openai"]})
        is CompletionTokenParameter.MAX_TOKENS
    )
    assert luna.capabilities.context_window_tokens == 1_050_000
    assert luna.capabilities.max_output_tokens == 128_000
    assert deepseek.structured_output_dialect is StructuredOutputDialect.JSON_OBJECT
    assert deepseek.completion_token_parameter is CompletionTokenParameter.MAX_TOKENS
    assert deepseek.capabilities.context_window_tokens == 1_048_576
    assert deepseek.capabilities.max_output_tokens == 384_000
    assert deepseek.capabilities.image_input is True
    assert (
        deepseek.digest
        == ModelCapabilityProfile.model_validate(
            deepseek.model_dump(mode="json", by_alias=True)
        ).digest
    )
    assert (
        deepseek.digest
        != deepseek.model_copy(
            update={"structured_output_dialect": StructuredOutputDialect.JSON_SCHEMA}
        ).digest
    )

    pin = registry.negotiate(
        "openai-compatible",
        CapabilityRequirement(
            required=frozenset({ProviderCapability.STRUCTURED_OUTPUT}),
            contextTokens=1_048_576,
            outputTokens=384_000,
            inputModalities={"text", "image"},
        ),
        revision="1.0.0",
        model=DEEPSEEK_V4_FLASH_VISION_MODEL,
    )
    assert pin.model_profile_digest == deepseek.digest
    assert pin.structured_output_dialect is StructuredOutputDialect.JSON_OBJECT
    assert (
        pin.completion_token_parameter_for({"only": ["novita"]})
        is CompletionTokenParameter.MAX_TOKENS
    )

    for requirement in (
        CapabilityRequirement(contextTokens=1_048_577),
        CapabilityRequirement(outputTokens=384_001),
    ):
        with pytest.raises(ProviderNegotiationError):
            registry.negotiate(
                "openai-compatible",
                requirement,
                revision="1.0.0",
                model=DEEPSEEK_V4_FLASH_VISION_MODEL,
            )
    assert provider.calls == 0


def test_usage_and_cost_normalization_fail_closed_for_hard_budgets() -> None:
    usage = normalize_usage({"usage": {"prompt_tokens": 3, "completion_tokens": 5}})
    assert usage.state is NormalizationState.UNPRICED
    assert usage.total_tokens == 8

    billed = normalize_cost({"usage": {"total_tokens": 8, "cost": "0.004"}})
    assert billed.state is NormalizationState.BILLED
    enforce_cost_budget(billed, maximum_usd=Decimal("0.01"))

    unpriced = normalize_cost({"usage": {"total_tokens": 8}})
    assert unpriced.state is NormalizationState.UNPRICED
    with pytest.raises(CostBudgetError, match="billed provider cost"):
        enforce_cost_budget(unpriced, maximum_usd=Decimal("0.01"))

    unavailable = normalize_cost({"choices": []})
    assert unavailable.state is NormalizationState.UNAVAILABLE


def test_prompt_cache_normalization_distinguishes_reported_zero_from_unavailable() -> None:
    unavailable = normalize_prompt_cache({"usage": {"prompt_tokens": 10}})
    assert unavailable.state.value == "unavailable"
    assert unavailable.read_tokens is None

    reported = normalize_prompt_cache(
        {
            "usage": {
                "prompt_tokens": 100,
                "prompt_tokens_details": {
                    "cached_tokens": 75,
                    "cache_write_tokens": 10,
                },
            },
            "cache_discount": "0.0025",
        }
    )
    assert reported.state.value == "reported"
    assert reported.read_tokens == 75
    assert reported.write_tokens == 10
    assert reported.hit_ratio == Decimal("0.75")
    assert reported.cost_effect_usd == Decimal("0.0025")

    explicit_miss = normalize_prompt_cache(
        {
            "usage": {
                "prompt_tokens": 100,
                "prompt_tokens_details": {"cached_tokens": 0},
            }
        }
    )
    assert explicit_miss.state.value == "reported"
    assert explicit_miss.read_tokens == 0
    assert explicit_miss.hit_ratio == 0


def test_prompt_cache_normalization_preserves_signed_write_cost_effect() -> None:
    cache = normalize_usage(
        {
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 5,
                "prompt_tokens_details": {"cache_write_tokens": 20},
                "cache_discount": "-0.001",
            }
        }
    ).prompt_cache

    assert cache.state.value == "reported"
    assert cache.write_tokens == 20
    assert cache.cost_effect_usd == Decimal("-0.001")


def test_opaque_continuation_round_trips_without_public_payload_or_repr_leak() -> None:
    continuation = OpaqueContinuation.create("fixture", "1.0.0", "hidden-provider-state")
    assert continuation.token_for_provider("fixture", "1.0.0") == "hidden-provider-state"
    assert continuation.public_metadata() == {"providerId": "fixture", "revision": "1.0.0"}
    assert "hidden-provider-state" not in repr(continuation)
    assert "hidden-provider-state" not in str(continuation.public_metadata())
    with pytest.raises(ValueError, match="different provider revision"):
        continuation.token_for_provider("other", "1.0.0")


def test_timeout_retry_and_cancellation_are_adapter_neutral() -> None:
    async def scenario() -> None:
        provider = ScriptedProvider()
        registry = ModelProviderRegistry()
        registry.register("fixture", "1.0.0", provider, ALL_CAPABILITIES)
        pin = registry.negotiate(
            "fixture",
            CapabilityRequirement(required=frozenset({ProviderCapability.RETRY})),
            revision="1.0.0",
        )
        provider.failures = 1
        response = await invoke_with_retry(pin, request(), SecretStr("test"), max_attempts=2)
        assert response.payload["choices"]
        assert provider.calls == 2

        provider.wait = 0.2
        with pytest.raises(TimeoutError, match="timed out"):
            await invoke_with_timeout(pin, request(), SecretStr("test"))

        task = asyncio.create_task(invoke_with_timeout(pin, request(), SecretStr("test")))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("provider_id", "provider"),
    [
        (
            "openai-compatible",
            ScriptedProvider(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "x" * 8192,
                                "tool_calls": [
                                    {
                                        "id": "call-1",
                                        "function": {
                                            "name": "lookup",
                                            "arguments": '{"key":"x"}',
                                        },
                                    }
                                ],
                            }
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 4,
                        "completion_tokens": 8192,
                        "cost": "0.01",
                    },
                    "continuation": "opaque-fixture-value",
                }
            ),
        ),
        ("deepseek-fixture", DeepSeekCompatibleFixtureProvider()),
    ],
)
def test_two_independent_provider_registrations_pass_neutral_conformance(
    provider_id: str,
    provider: ScriptedProvider | DeepSeekCompatibleFixtureProvider,
) -> None:
    """The same contract applies to OpenAI-compatible and DeepSeek-shaped fixtures."""
    registry = ModelProviderRegistry()
    registry.register(provider_id, "1.0.0", provider, ALL_CAPABILITIES)
    pin = registry.negotiate(
        provider_id,
        CapabilityRequirement(
            required=frozenset(
                {
                    ProviderCapability.CONTEXT,
                    ProviderCapability.OUTPUT,
                    ProviderCapability.STRUCTURED_OUTPUT,
                    ProviderCapability.TOOL,
                    ProviderCapability.OPAQUE_CONTINUATION,
                    ProviderCapability.USAGE,
                    ProviderCapability.COST,
                }
            ),
            contextTokens=128,
            outputTokens=8192,
        ),
    )
    assert pin.revision == "1.0.0"
    response = asyncio.run(invoke_with_timeout(pin, request(), SecretStr("fixture")))
    assert response.payload["choices"]
    assert provider.calls == 1
    assert normalize_usage(provider.response).total_tokens == 8196
    assert normalize_cost(provider.response).state is NormalizationState.BILLED
    assert provider.response["choices"][0]["message"]["tool_calls"]
    continuation = OpaqueContinuation.create(
        pin.provider_id, pin.revision, provider.response["continuation"]
    )
    assert continuation.token_for_provider(pin.provider_id, pin.revision) == "opaque-fixture-value"
