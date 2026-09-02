"""Runtime composition for isolated subscription-backed model engines."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from amesh.adapters.codex_app_server import (
    CODEX_APP_SERVER_ADAPTER_ID,
    CODEX_APP_SERVER_REVISION,
    CodexAppServerConfig,
    CodexAppServerModelProvider,
)
from amesh.adapters.copilot_cli import (
    COPILOT_CLI_ADAPTER_ID,
    COPILOT_CLI_ADAPTER_REVISION,
    CopilotCliConfig,
    CopilotCliModelProvider,
)
from amesh.config import Settings
from amesh.model_providers import (
    ModelCapabilityProfile,
    ModelProviderCapabilities,
    ModelProviderRegistry,
    StructuredOutputDialect,
    declared_model_capabilities,
)
from amesh.ports import ImageArtifactResolver
from amesh.tasks.llm import OpenAICompatibleConfig

MODEL_ENGINE_DEFAULT_MODEL = "gpt-5.6-luna"
_MODEL_ENGINE_CONTEXT_WINDOW_TOKENS = 1_050_000
_MODEL_ENGINE_MAX_OUTPUT_TOKENS = 128_000


def configured_model_engine_registry(
    settings: Settings,
    *,
    image_resolver: ImageArtifactResolver | None = None,
) -> ModelProviderRegistry:
    """Register the configured process engines with truthful shared capabilities."""

    state_root = Path(settings.model_engine_state_root)
    registry = ModelProviderRegistry()
    capabilities = _process_engine_capabilities()
    codex = registry.register(
        CODEX_APP_SERVER_ADAPTER_ID,
        CODEX_APP_SERVER_REVISION,
        CodexAppServerModelProvider(
            CodexAppServerConfig(
                command=settings.model_engine_codex_command,
                state_root=state_root,
                frame_limit_bytes=settings.model_engine_max_frame_bytes,
                timeout_seconds=settings.model_engine_timeout_seconds,
                cancel_grace_seconds=settings.model_engine_cancel_grace_seconds,
                environment=settings.model_engine_environment,
            ),
            image_resolver=image_resolver,
        ),
        capabilities,
    )
    copilot = registry.register(
        COPILOT_CLI_ADAPTER_ID,
        COPILOT_CLI_ADAPTER_REVISION,
        CopilotCliModelProvider(
            CopilotCliConfig(
                command=settings.model_engine_copilot_command,
                state_root=state_root,
                frame_limit_bytes=settings.model_engine_max_frame_bytes,
                timeout_seconds=settings.model_engine_timeout_seconds,
                cancel_grace_seconds=settings.model_engine_cancel_grace_seconds,
                environment=settings.model_engine_environment,
            ),
            image_resolver=image_resolver,
        ),
        capabilities,
    )
    profile = _process_engine_model_profile(capabilities)
    registry.register_model_profile(codex.provider_id, codex.revision, profile)
    registry.register_model_profile(copilot.provider_id, copilot.revision, profile)
    return registry


def configured_openai_compatible(
    settings: Settings,
) -> OpenAICompatibleConfig | None:
    """Build the direct OpenRouter fallback from typed process settings."""

    if settings.openrouter_api_key is None:
        return None
    return OpenAICompatibleConfig(
        api_key=settings.openrouter_api_key.get_secret_value(),
        endpoint=settings.openrouter_chat_completions_url,
        embedding_endpoint=settings.openrouter_embeddings_url,
        default_model=settings.openrouter_model,
    )


def configured_model_capability_resolver(
    registry: ModelProviderRegistry,
) -> Callable[[str, str], ModelProviderCapabilities]:
    """Resolve exact engine profiles before falling back to the direct-provider catalog."""

    engine_adapters = {CODEX_APP_SERVER_ADAPTER_ID, COPILOT_CLI_ADAPTER_ID}

    def resolve(model: str, adapter: str) -> ModelProviderCapabilities:
        if adapter in engine_adapters:
            return registry.resolve_model_profile(adapter, model).capabilities
        return declared_model_capabilities(model)

    return resolve


def _process_engine_capabilities() -> ModelProviderCapabilities:
    return ModelProviderCapabilities(
        output=False,
        structuredOutput=True,
        streaming=True,
        cancellation=True,
        usage=True,
        imageInput=True,
    )


def _process_engine_model_profile(
    capabilities: ModelProviderCapabilities,
) -> ModelCapabilityProfile:
    return ModelCapabilityProfile(
        model=MODEL_ENGINE_DEFAULT_MODEL,
        capabilities=capabilities.model_copy(
            update={
                "context_window_tokens": _MODEL_ENGINE_CONTEXT_WINDOW_TOKENS,
                "max_output_tokens": _MODEL_ENGINE_MAX_OUTPUT_TOKENS,
            }
        ),
        structuredOutputDialect=StructuredOutputDialect.JSON_SCHEMA,
    )


__all__ = [
    "MODEL_ENGINE_DEFAULT_MODEL",
    "configured_model_capability_resolver",
    "configured_model_engine_registry",
    "configured_openai_compatible",
]
