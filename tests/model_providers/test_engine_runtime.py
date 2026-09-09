from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from amesh.adapters.codex_app_server import CODEX_APP_SERVER_ADAPTER_ID
from amesh.adapters.copilot_cli import COPILOT_CLI_ADAPTER_ID
from amesh.config import Settings
from amesh.model_engine_runtime import (
    MODEL_ENGINE_DEFAULT_MODEL,
    configured_model_capability_resolver,
    configured_model_engine_registry,
    configured_openai_compatible,
)
from amesh.model_providers import ProviderCapability


def test_process_engines_reject_cache_boundaries_before_launch(tmp_path, monkeypatch):
    from amesh.ports import ModelEngineAccess, ModelProviderRequest

    async def unexpected_launch(*args, **kwargs):
        raise AssertionError("unsupported cache controls must fail before engine launch")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", unexpected_launch)
    registry = configured_model_engine_registry(
        Settings(_env_file=None, model_engine_state_root=str(tmp_path))
    )
    request = ModelProviderRequest(
        operation="CHAT",
        model=MODEL_ENGINE_DEFAULT_MODEL,
        payload={
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "context",
                            "prompt_cache_breakpoint": {"mode": "explicit"},
                        }
                    ],
                }
            ]
        },
        timeoutSeconds=30,
        tenantId="tenant-a",
        namespace="test",
    )
    for registration in registry.registrations():
        with pytest.raises(ValueError, match="does not support explicit prompt-cache controls"):
            asyncio.run(registration.adapter.invoke(request, ModelEngineAccess(engineRef="test")))


def test_custom_registered_model_profile_is_used_for_provider_bounded_context():
    from amesh.model_providers import (
        ModelCapabilityProfile,
        ModelProviderCapabilities,
        ModelProviderRegistry,
    )

    registry = ModelProviderRegistry()
    capabilities = ModelProviderCapabilities(contextWindowTokens=32000, maxOutputTokens=4000)
    registry.register("custom-compatible", "1.0.0", object(), capabilities)
    registry.register_model_profile(
        "custom-compatible",
        "1.0.0",
        ModelCapabilityProfile(model="custom-model", capabilities=capabilities),
    )
    result = configured_model_capability_resolver(registry)("custom-model", "custom-compatible")
    assert result.context_window_tokens == 32000
    assert result.max_output_tokens == 4000


def test_custom_context_limits_respect_adapter_ceiling_and_require_exact_model():
    from amesh.model_providers import (
        ModelCapabilityProfile,
        ModelProviderCapabilities,
        ModelProviderRegistry,
    )

    registry = ModelProviderRegistry()
    registry.register(
        "custom-compatible", "1.0.0", object(), ModelProviderCapabilities(contextWindowTokens=8000)
    )
    registry.register_model_profile(
        "custom-compatible",
        "1.0.0",
        ModelCapabilityProfile(
            model="custom-model", capabilities=ModelProviderCapabilities(contextWindowTokens=32000)
        ),
    )
    resolve = configured_model_capability_resolver(registry)
    assert resolve("custom-model", "custom-compatible").context_window_tokens == 8000
    with pytest.raises(LookupError):
        resolve("openai/gpt-5.6-luna", "custom-compatible")


def test_configured_registry_exposes_only_proven_process_engine_capabilities(
    tmp_path: Path,
) -> None:
    settings = Settings(_env_file=None, model_engine_state_root=str(tmp_path))

    registry = configured_model_engine_registry(settings)

    assert {registration.provider_id for registration in registry.registrations()} == {
        CODEX_APP_SERVER_ADAPTER_ID,
        COPILOT_CLI_ADAPTER_ID,
    }
    for registration in registry.registrations():
        capabilities = registration.capabilities
        for supported in (
            ProviderCapability.CONTEXT,
            ProviderCapability.STRUCTURED_OUTPUT,
            ProviderCapability.STREAMING,
            ProviderCapability.TIMEOUT,
            ProviderCapability.CANCELLATION,
            ProviderCapability.USAGE,
            ProviderCapability.IMAGE_INPUT,
        ):
            assert capabilities.supports(supported)
        for unsupported in (
            ProviderCapability.OUTPUT,
            ProviderCapability.TOOL,
            ProviderCapability.OPAQUE_CONTINUATION,
            ProviderCapability.CACHE,
            ProviderCapability.COST,
            ProviderCapability.RETRY,
            ProviderCapability.EMBEDDING,
        ):
            assert not capabilities.supports(unsupported)

        profile = registry.resolve_model_profile(
            registration.provider_id,
            MODEL_ENGINE_DEFAULT_MODEL,
        )
        assert profile.capabilities.context_window_tokens == 1_050_000
        assert profile.capabilities.max_output_tokens == 128_000
        assert profile.capabilities.output is False

    resolver = configured_model_capability_resolver(registry)
    for adapter in (CODEX_APP_SERVER_ADAPTER_ID, COPILOT_CLI_ADAPTER_ID):
        resolved = resolver(MODEL_ENGINE_DEFAULT_MODEL, adapter)
        assert resolved.context_window_tokens == 1_050_000
        assert resolved.max_output_tokens == 128_000


def test_settings_configure_process_environments_and_direct_openrouter_secret(
    tmp_path: Path,
) -> None:
    settings = Settings(
        _env_file=None,
        model_engine_state_root=str(tmp_path),
        model_engine_environment={"LANG": "C.UTF-8", "TZ": "UTC"},
        openrouter_api_key="settings-secret",
        openrouter_chat_completions_url="https://router.example.test/chat",
        openrouter_embeddings_url="https://router.example.test/embeddings",
        openrouter_model="openai/test-model",
    )

    registry = configured_model_engine_registry(settings)
    for registration in registry.registrations():
        assert registration.adapter._config.environment == {  # type: ignore[attr-defined]
            "LANG": "C.UTF-8",
            "TZ": "UTC",
        }

    direct = configured_openai_compatible(settings)
    assert direct is not None
    assert direct.api_key == "settings-secret"
    assert direct.endpoint == "https://router.example.test/chat"
    assert direct.embedding_endpoint == "https://router.example.test/embeddings"
    assert direct.default_model == "openai/test-model"
