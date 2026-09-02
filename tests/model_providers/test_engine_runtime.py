from __future__ import annotations

from pathlib import Path

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
