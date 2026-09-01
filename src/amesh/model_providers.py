"""Provider-neutral model capability contracts and negotiation.

The registry is deliberately an in-memory boundary. Durable callers persist the returned
``ProviderPin`` alongside their invocation/session state; adapters remain replaceable and
are never consulted while capability negotiation is happening.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from amesh.domain.image_inputs import InputModality
from amesh.ports.agent_primitives import (
    ModelProvider,
    ModelProviderAccess,
    ModelProviderRequest,
    ModelProviderResponse,
)


class ProviderCapability(StrEnum):
    """Capabilities that a workflow request may require."""

    CONTEXT = "context"
    OUTPUT = "output"
    STRUCTURED_OUTPUT = "structured_output"
    TOOL = "tool"
    STREAMING = "streaming"
    OPAQUE_CONTINUATION = "opaque_continuation"
    TIMEOUT = "timeout"
    CANCELLATION = "cancellation"
    USAGE = "usage"
    CACHE = "cache"
    COST = "cost"
    RETRY = "retry"
    IMAGE_INPUT = "image_input"
    EMBEDDING = "embedding"


class StructuredOutputDialect(StrEnum):
    """Provider request dialect used to obtain an AMESH-validated JSON object."""

    JSON_SCHEMA = "json_schema"
    JSON_OBJECT = "json_object"


class CompletionTokenParameter(StrEnum):
    """Provider wire field used for one semantic completion-token limit."""

    MAX_COMPLETION_TOKENS = "max_completion_tokens"
    MAX_TOKENS = "max_tokens"


class CompletionTokenParameterOverride(BaseModel):
    """Wire-field override for one exact downstream provider route tag."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    provider: str = Field(min_length=1, max_length=128)
    parameter: CompletionTokenParameter


class ModelProviderCapabilities(BaseModel):
    """Versioned, provider-neutral capability declaration."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: str = Field(default="v1", alias="contractVersion", pattern=r"^v[0-9]+$")
    context: bool = True
    output: bool = True
    structured_output: bool = Field(default=False, alias="structuredOutput")
    tool: bool = False
    streaming: bool = False
    opaque_continuation: bool = Field(default=False, alias="opaqueContinuation")
    timeout: bool = True
    cancellation: bool = False
    usage: bool = False
    cache: bool = False
    cost: bool = False
    retry: bool = False
    image_input: bool = Field(default=False, alias="imageInput")
    embedding: bool = False
    context_window_tokens: int | None = Field(default=None, alias="contextWindowTokens", ge=1)
    max_output_tokens: int | None = Field(default=None, alias="maxOutputTokens", ge=1)

    def supports(self, capability: ProviderCapability) -> bool:
        return bool(getattr(self, capability.value))


class ModelCapabilityProfile(BaseModel):
    """Immutable capabilities for one exact model behind a provider adapter revision."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: str = Field(default="v1", alias="contractVersion", pattern=r"^v[0-9]+$")
    model: str = Field(min_length=1, max_length=512)
    capabilities: ModelProviderCapabilities
    structured_output_dialect: StructuredOutputDialect | None = Field(
        default=None,
        alias="structuredOutputDialect",
    )
    completion_token_parameter: CompletionTokenParameter = Field(
        default=CompletionTokenParameter.MAX_COMPLETION_TOKENS,
        alias="completionTokenParameter",
    )
    completion_token_parameter_overrides: tuple[CompletionTokenParameterOverride, ...] = Field(
        default=(),
        alias="completionTokenParameterOverrides",
        max_length=32,
    )

    @model_validator(mode="after")
    def validate_structured_output_dialect(self) -> ModelCapabilityProfile:
        supports_structured_output = self.capabilities.structured_output
        if supports_structured_output != (self.structured_output_dialect is not None):
            raise ValueError(
                "structuredOutputDialect must be declared exactly when structuredOutput is supported"
            )
        providers = tuple(
            override.provider for override in self.completion_token_parameter_overrides
        )
        if len(providers) != len(set(providers)):
            raise ValueError("completionTokenParameterOverrides providers must be unique")
        return self

    def completion_token_parameter_for(
        self,
        provider_options: dict[str, Any],
    ) -> CompletionTokenParameter:
        overrides = {
            override.provider: override.parameter
            for override in self.completion_token_parameter_overrides
        }
        for selector in ("only", "order"):
            providers = provider_options.get(selector)
            if not isinstance(providers, list | tuple):
                continue
            for provider in providers:
                if isinstance(provider, str) and provider in overrides:
                    return overrides[provider]
        return self.completion_token_parameter

    @property
    def digest(self) -> str:
        canonical = json.dumps(
            self.model_dump(mode="json", by_alias=True),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return "sha256:" + hashlib.sha256(canonical).hexdigest()


class CapabilityRequirement(BaseModel):
    """A request that can be checked without touching a provider."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    required: frozenset[ProviderCapability] = frozenset()
    context_tokens: int | None = Field(default=None, alias="contextTokens", ge=1)
    output_tokens: int | None = Field(default=None, alias="outputTokens", ge=1)
    hard_cost_usd: Decimal | None = Field(default=None, alias="hardCostUsd", ge=0)
    require_priced_cost: bool = Field(default=False, alias="requirePricedCost")
    input_modalities: frozenset[InputModality] = Field(
        default=frozenset({InputModality.TEXT}),
        alias="inputModalities",
    )

    @model_validator(mode="before")
    @classmethod
    def infer_required_capabilities(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        required = set(data.get("required", ()))
        if data.get("context_tokens", data.get("contextTokens")) is not None:
            required.add(ProviderCapability.CONTEXT)
        if data.get("output_tokens", data.get("outputTokens")) is not None:
            required.add(ProviderCapability.OUTPUT)
        if data.get("hard_cost_usd", data.get("hardCostUsd")) is not None or data.get(
            "require_priced_cost", data.get("requirePricedCost", False)
        ):
            required.add(ProviderCapability.COST)
        modalities = frozenset(
            data.pop("input_modalities", data.get("inputModalities", {InputModality.TEXT}))
        )
        if InputModality.IMAGE in modalities or InputModality.IMAGE.value in modalities:
            required.add(ProviderCapability.IMAGE_INPUT)
        data["inputModalities"] = modalities
        data["required"] = frozenset(required)
        return data


class ProviderNegotiationError(ValueError):
    """Raised before adapter I/O when a provider cannot satisfy a request."""

    def __init__(self, provider_id: str, revision: str, missing: tuple[str, ...]) -> None:
        self.provider_id = provider_id
        self.revision = revision
        self.missing = missing
        detail = ", ".join(missing)
        super().__init__(
            f"provider {provider_id!r} revision {revision!r} lacks capabilities: {detail}"
        )


class ProviderRevisionConflict(ValueError):
    """Raised when an immutable provider revision is registered twice differently."""


class ModelProfileConflict(ValueError):
    """Raised when an exact model profile is registered twice differently."""


@dataclass(frozen=True)
class ModelProviderRegistration:
    """An adapter and its immutable capability declaration."""

    provider_id: str
    revision: str
    adapter: ModelProvider
    capabilities: ModelProviderCapabilities

    def __post_init__(self) -> None:
        if not self.provider_id or not self.revision:
            raise ValueError("provider_id and revision are required")

    @property
    def digest(self) -> str:
        canonical = json.dumps(
            {
                "providerId": self.provider_id,
                "revision": self.revision,
                "capabilities": self.capabilities.model_dump(mode="json", by_alias=True),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return "sha256:" + hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class ProviderPin:
    """The exact provider revision selected for one durable operation."""

    provider_id: str
    revision: str
    digest: str
    registration: ModelProviderRegistration
    model_profile: ModelCapabilityProfile | None = None
    effective_capabilities: ModelProviderCapabilities | None = None

    @property
    def capabilities(self) -> ModelProviderCapabilities:
        return self.effective_capabilities or self.registration.capabilities

    @property
    def model_profile_digest(self) -> str | None:
        return self.model_profile.digest if self.model_profile is not None else None

    @property
    def structured_output_dialect(self) -> StructuredOutputDialect | None:
        if not self.capabilities.structured_output:
            return None
        if self.model_profile is not None:
            return self.model_profile.structured_output_dialect
        return StructuredOutputDialect.JSON_SCHEMA

    def completion_token_parameter_for(
        self,
        provider_options: dict[str, Any],
    ) -> CompletionTokenParameter:
        if self.model_profile is not None:
            return self.model_profile.completion_token_parameter_for(provider_options)
        return CompletionTokenParameter.MAX_COMPLETION_TOKENS


def _minimum_declared_limit(first: int | None, second: int | None) -> int | None:
    declared = tuple(value for value in (first, second) if value is not None)
    return min(declared) if declared else None


def _intersect_capabilities(
    adapter: ModelProviderCapabilities,
    model: ModelProviderCapabilities,
) -> ModelProviderCapabilities:
    supported = {
        capability.value: adapter.supports(capability) and model.supports(capability)
        for capability in ProviderCapability
    }
    return ModelProviderCapabilities(
        contractVersion=model.contract_version,
        **supported,
        contextWindowTokens=_minimum_declared_limit(
            adapter.context_window_tokens,
            model.context_window_tokens,
        ),
        maxOutputTokens=_minimum_declared_limit(
            adapter.max_output_tokens,
            model.max_output_tokens,
        ),
    )


class ModelProviderRegistry:
    """Registry for immutable, revisioned provider registrations."""

    def __init__(self) -> None:
        self._registrations: dict[tuple[str, str], ModelProviderRegistration] = {}
        self._model_profiles: dict[tuple[str, str, str], ModelCapabilityProfile] = {}

    def register(
        self,
        provider_id: str,
        revision: str,
        adapter: ModelProvider,
        capabilities: ModelProviderCapabilities,
    ) -> ModelProviderRegistration:
        registration = ModelProviderRegistration(provider_id, revision, adapter, capabilities)
        key = (provider_id, revision)
        existing = self._registrations.get(key)
        if existing is not None:
            if (
                existing.digest != registration.digest
                or existing.adapter is not adapter
                or type(existing.adapter) is not type(adapter)
            ):
                raise ProviderRevisionConflict(
                    f"provider revision {provider_id!r}/{revision!r} is already registered"
                )
            return existing
        self._registrations[key] = registration
        return registration

    def register_model_profile(
        self,
        provider_id: str,
        revision: str,
        profile: ModelCapabilityProfile,
    ) -> ModelCapabilityProfile:
        if (provider_id, revision) not in self._registrations:
            raise LookupError(
                f"provider revision {provider_id!r}/{revision!r} must be registered first"
            )
        key = (provider_id, revision, profile.model)
        existing = self._model_profiles.get(key)
        if existing is not None:
            if existing.digest != profile.digest:
                raise ModelProfileConflict(
                    f"model profile {provider_id!r}/{revision!r}/{profile.model!r} "
                    "is already registered"
                )
            return existing
        self._model_profiles[key] = profile
        return profile

    def resolve(self, provider_id: str, revision: str | None = None) -> ModelProviderRegistration:
        if revision is not None:
            try:
                return self._registrations[(provider_id, revision)]
            except KeyError as exc:
                raise LookupError(
                    f"provider revision {provider_id!r}/{revision!r} is not registered"
                ) from exc
        candidates = [
            item
            for (candidate_id, _), item in self._registrations.items()
            if candidate_id == provider_id
        ]
        if not candidates:
            raise LookupError(f"provider {provider_id!r} is not registered")
        return max(candidates, key=lambda item: item.revision)

    def resolve_model_profile(
        self,
        provider_id: str,
        model: str,
        *,
        revision: str | None = None,
    ) -> ModelCapabilityProfile:
        registration = self.resolve(provider_id, revision)
        try:
            return self._model_profiles[(provider_id, registration.revision, model)]
        except KeyError as exc:
            raise LookupError(
                f"model profile {provider_id!r}/{registration.revision!r}/{model!r} "
                "is not registered"
            ) from exc

    def negotiate(
        self,
        provider_id: str,
        requirement: CapabilityRequirement,
        *,
        revision: str | None = None,
        model: str | None = None,
    ) -> ProviderPin:
        registration = self.resolve(provider_id, revision)
        model_profile = (
            self._model_profiles.get((provider_id, registration.revision, model))
            if model is not None
            else None
        )
        capabilities = (
            _intersect_capabilities(registration.capabilities, model_profile.capabilities)
            if model_profile is not None
            else registration.capabilities
        )
        missing = [
            capability.value
            for capability in requirement.required
            if not capabilities.supports(capability)
        ]
        if (
            requirement.context_tokens is not None
            and capabilities.context_window_tokens is not None
            and requirement.context_tokens > capabilities.context_window_tokens
        ):
            missing.append(f"context_tokens<={capabilities.context_window_tokens}")
        if (
            requirement.output_tokens is not None
            and capabilities.max_output_tokens is not None
            and requirement.output_tokens > capabilities.max_output_tokens
        ):
            missing.append(f"output_tokens<={capabilities.max_output_tokens}")
        if missing:
            raise ProviderNegotiationError(
                registration.provider_id, registration.revision, tuple(sorted(set(missing)))
            )
        return ProviderPin(
            provider_id=registration.provider_id,
            revision=registration.revision,
            digest=registration.digest,
            registration=registration,
            model_profile=model_profile,
            effective_capabilities=capabilities,
        )

    def registrations(self) -> tuple[ModelProviderRegistration, ...]:
        return tuple(self._registrations.values())


def declared_model_capabilities(model: str) -> ModelProviderCapabilities:
    """Return the pinned physical limits for a model in the built-in capability catalog."""

    profile = next(
        (
            candidate
            for candidate in OPENROUTER_MODEL_CAPABILITY_PROFILES
            if candidate.model == model
        ),
        None,
    )
    if profile is None:
        raise LookupError(f"model {model!r} has no declared physical capability profile")
    return profile.capabilities


class NormalizationState(StrEnum):
    BILLED = "billed"
    UNPRICED = "unpriced"
    UNAVAILABLE = "unavailable"


class PromptCacheState(StrEnum):
    REPORTED = "reported"
    UNAVAILABLE = "unavailable"


class NormalizedPromptCache(BaseModel):
    """Provider prompt-cache usage; unrelated to task cache or invocation replay."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    state: PromptCacheState = PromptCacheState.UNAVAILABLE
    read_tokens: int | None = Field(default=None, alias="readTokens", ge=0)
    write_tokens: int | None = Field(default=None, alias="writeTokens", ge=0)
    hit_ratio: Decimal | None = Field(default=None, alias="hitRatio", ge=0, le=1)
    cost_effect_usd: Decimal | None = Field(default=None, alias="costEffectUsd")

    @model_validator(mode="after")
    def validate_state(self) -> NormalizedPromptCache:
        values = (self.read_tokens, self.write_tokens, self.hit_ratio, self.cost_effect_usd)
        if self.state is PromptCacheState.UNAVAILABLE and any(item is not None for item in values):
            raise ValueError("unavailable prompt-cache evidence cannot include values")
        if self.state is PromptCacheState.REPORTED and all(item is None for item in values):
            raise ValueError("reported prompt-cache evidence requires a value")
        return self


class NormalizedUsage(BaseModel):
    """Provider usage with explicit absence semantics."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    state: NormalizationState
    input_tokens: int | None = Field(default=None, alias="inputTokens", ge=0)
    output_tokens: int | None = Field(default=None, alias="outputTokens", ge=0)
    reasoning_tokens: int | None = Field(default=None, alias="reasoningTokens", ge=0)
    total_tokens: int | None = Field(default=None, alias="totalTokens", ge=0)
    prompt_cache: NormalizedPromptCache = Field(
        default_factory=NormalizedPromptCache,
        alias="promptCache",
    )


class NormalizedCost(BaseModel):
    """Cost normalized to billed, unpriced or unavailable."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    state: NormalizationState
    amount_usd: Decimal | None = Field(default=None, alias="amountUsd", ge=0)

    @model_validator(mode="after")
    def validate_state(self) -> NormalizedCost:
        if self.state is NormalizationState.BILLED and self.amount_usd is None:
            raise ValueError("billed cost requires amountUsd")
        if self.state is not NormalizationState.BILLED and self.amount_usd is not None:
            raise ValueError("only billed cost may include amountUsd")
        return self


class CostBudgetError(ValueError):
    """Raised when a hard budget cannot be proven safe."""


def normalize_usage(payload: dict[str, Any]) -> NormalizedUsage:
    raw = payload.get("usage")
    if not isinstance(raw, dict):
        return NormalizedUsage(state=NormalizationState.UNAVAILABLE)
    input_tokens = _first_int(raw, "input_tokens", "prompt_tokens", "inputTokens", "promptTokens")
    output_tokens = _first_int(
        raw, "output_tokens", "completion_tokens", "outputTokens", "completionTokens"
    )
    completion_details = raw.get(
        "completion_tokens_details",
        raw.get("completionTokensDetails"),
    )
    detail_values = completion_details if isinstance(completion_details, dict) else {}
    reasoning_tokens = _first_int(
        detail_values,
        "reasoning_tokens",
        "reasoningTokens",
    )
    if reasoning_tokens is None:
        reasoning_tokens = _first_int(raw, "reasoning_tokens", "reasoningTokens")
    total_tokens = _first_int(raw, "total_tokens", "totalTokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    if input_tokens is None and output_tokens is None and total_tokens is None:
        return NormalizedUsage(state=NormalizationState.UNAVAILABLE)
    return NormalizedUsage(
        state=NormalizationState.UNPRICED,
        inputTokens=input_tokens,
        outputTokens=output_tokens,
        reasoningTokens=reasoning_tokens,
        totalTokens=total_tokens,
        promptCache=normalize_prompt_cache(payload),
    )


def normalize_prompt_cache(payload: dict[str, Any]) -> NormalizedPromptCache:
    raw = payload.get("usage")
    if not isinstance(raw, dict):
        return NormalizedPromptCache()
    details = raw.get("prompt_tokens_details", raw.get("promptTokensDetails"))
    detail_values = details if isinstance(details, dict) else {}
    read_tokens = _first_int(
        detail_values,
        "cached_tokens",
        "cache_read_tokens",
        "cachedTokens",
        "cacheReadTokens",
    )
    if read_tokens is None:
        read_tokens = _first_int(
            raw,
            "cache_read_input_tokens",
            "cached_tokens",
            "cacheReadInputTokens",
            "cachedTokens",
        )
    write_tokens = _first_int(
        detail_values,
        "cache_write_tokens",
        "cacheWriteTokens",
    )
    if write_tokens is None:
        write_tokens = _first_int(
            raw,
            "cache_creation_input_tokens",
            "cache_write_tokens",
            "cacheCreationInputTokens",
            "cacheWriteTokens",
        )
    cost_effect = _first_decimal(
        payload.get("cache_discount"),
        payload.get("cacheDiscount"),
        raw.get("cache_discount"),
        raw.get("cacheDiscount"),
    )
    if read_tokens is None and write_tokens is None and cost_effect is None:
        return NormalizedPromptCache()
    input_tokens = _first_int(
        raw,
        "input_tokens",
        "prompt_tokens",
        "inputTokens",
        "promptTokens",
    )
    hit_ratio = (
        Decimal(read_tokens) / Decimal(input_tokens)
        if read_tokens is not None and input_tokens is not None and input_tokens > 0
        else None
    )
    return NormalizedPromptCache(
        state=PromptCacheState.REPORTED,
        readTokens=read_tokens,
        writeTokens=write_tokens,
        hitRatio=hit_ratio,
        costEffectUsd=cost_effect,
    )


def normalize_cost(payload: dict[str, Any]) -> NormalizedCost:
    raw_usage = payload.get("usage")
    candidates: tuple[Any, ...] = (
        payload.get("costUsd"),
        payload.get("cost"),
        raw_usage.get("cost") if isinstance(raw_usage, dict) else None,
        raw_usage.get("costUsd") if isinstance(raw_usage, dict) else None,
    )
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            amount = Decimal(str(candidate))
        except (InvalidOperation, ValueError):
            continue
        if amount.is_finite() and amount >= 0:
            return NormalizedCost(state=NormalizationState.BILLED, amountUsd=amount)
    usage = normalize_usage(payload)
    state = (
        NormalizationState.UNPRICED
        if usage.state is not NormalizationState.UNAVAILABLE
        else NormalizationState.UNAVAILABLE
    )
    return NormalizedCost(state=state)


def enforce_cost_budget(
    cost: NormalizedCost, maximum_usd: Decimal, *, require_priced: bool = True
) -> None:
    """Fail closed when a hard budget cannot be evaluated."""

    if cost.state is not NormalizationState.BILLED or cost.amount_usd is None:
        if require_priced:
            raise CostBudgetError("hard cost budget requires billed provider cost")
        return
    if cost.amount_usd > maximum_usd:
        raise CostBudgetError(f"provider cost {cost.amount_usd} exceeds hard budget {maximum_usd}")


@dataclass(frozen=True)
class OpaqueContinuation:
    """Provider continuation data that is never included in public evidence."""

    provider_id: str
    revision: str
    _token: SecretStr

    @classmethod
    def create(cls, provider_id: str, revision: str, token: str) -> OpaqueContinuation:
        if not token:
            raise ValueError("continuation token cannot be empty")
        return cls(provider_id, revision, SecretStr(token))

    def token_for_provider(self, provider_id: str, revision: str) -> str:
        if (provider_id, revision) != (self.provider_id, self.revision):
            raise ValueError("continuation is pinned to a different provider revision")
        return self._token.get_secret_value()

    def public_metadata(self) -> dict[str, str]:
        return {"providerId": self.provider_id, "revision": self.revision}

    def __repr__(self) -> str:
        return f"OpaqueContinuation(provider_id={self.provider_id!r}, revision={self.revision!r})"


class ProviderCallTimeout(TimeoutError):
    """The provider did not complete within the negotiated timeout."""


class RetryableProviderError(RuntimeError):
    """An adapter may raise this when the external failure is safe to retry."""


class ProviderCallAmbiguous(RuntimeError):
    """The adapter outcome is unknown and must not be repeated automatically."""


async def invoke_with_timeout(
    pin: ProviderPin,
    request: ModelProviderRequest,
    access: ModelProviderAccess,
) -> ModelProviderResponse:
    """Invoke a pinned adapter while preserving cancellation and timeout semantics."""

    if not pin.capabilities.timeout:
        raise ProviderNegotiationError(
            pin.provider_id, pin.revision, (ProviderCapability.TIMEOUT.value,)
        )
    try:
        async with asyncio.timeout(request.timeout_seconds):
            return await pin.registration.adapter.invoke(request, access)
    except TimeoutError as exc:
        raise ProviderCallTimeout("provider call timed out") from exc


async def invoke_with_retry(
    pin: ProviderPin,
    request: ModelProviderRequest,
    access: ModelProviderAccess,
    *,
    max_attempts: int = 1,
) -> ModelProviderResponse:
    """Retry only explicitly retryable failures for a pinned provider revision."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")
    if max_attempts > 1 and not pin.capabilities.retry:
        raise ProviderNegotiationError(
            pin.provider_id, pin.revision, (ProviderCapability.RETRY.value,)
        )
    for attempt in range(max_attempts):
        try:
            return await invoke_with_timeout(pin, request, access)
        except RetryableProviderError:
            if attempt + 1 == max_attempts:
                raise
    raise AssertionError("retry loop did not return or raise")


def _first_int(raw: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and value >= 0:
            return value
    return None


def _first_decimal(*values: Any) -> Decimal | None:
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError):
            continue
        if number.is_finite():
            return number
    return None


DEFAULT_OPENROUTER_MODEL: Final[str] = "openai/gpt-5.6-luna"
DEEPSEEK_V4_FLASH_VISION_MODEL: Final[str] = "deepseek/deepseek-v4-flash-vision-exp"

OPENROUTER_MODEL_CAPABILITY_PROFILES: Final[tuple[ModelCapabilityProfile, ...]] = (
    ModelCapabilityProfile(
        model=DEFAULT_OPENROUTER_MODEL,
        capabilities=ModelProviderCapabilities(
            structuredOutput=True,
            tool=True,
            streaming=True,
            opaqueContinuation=True,
            cancellation=True,
            usage=True,
            cache=True,
            cost=True,
            embedding=True,
            imageInput=True,
            contextWindowTokens=1_050_000,
            maxOutputTokens=128_000,
        ),
        structuredOutputDialect=StructuredOutputDialect.JSON_SCHEMA,
        completionTokenParameter=CompletionTokenParameter.MAX_COMPLETION_TOKENS,
        completionTokenParameterOverrides=(
            CompletionTokenParameterOverride(
                provider="amazon-bedrock/us-east-1",
                parameter=CompletionTokenParameter.MAX_TOKENS,
            ),
            CompletionTokenParameterOverride(
                provider="openai",
                parameter=CompletionTokenParameter.MAX_TOKENS,
            ),
            CompletionTokenParameterOverride(
                provider="openai/fast",
                parameter=CompletionTokenParameter.MAX_TOKENS,
            ),
            CompletionTokenParameterOverride(
                provider="openai/flex",
                parameter=CompletionTokenParameter.MAX_TOKENS,
            ),
        ),
    ),
    ModelCapabilityProfile(
        model=DEEPSEEK_V4_FLASH_VISION_MODEL,
        capabilities=ModelProviderCapabilities(
            structuredOutput=True,
            tool=True,
            streaming=True,
            opaqueContinuation=True,
            cancellation=True,
            usage=True,
            cache=True,
            cost=True,
            embedding=True,
            imageInput=True,
            contextWindowTokens=1_048_576,
            maxOutputTokens=384_000,
        ),
        structuredOutputDialect=StructuredOutputDialect.JSON_OBJECT,
        completionTokenParameter=CompletionTokenParameter.MAX_TOKENS,
    ),
)


__all__ = [
    "DEEPSEEK_V4_FLASH_VISION_MODEL",
    "DEFAULT_OPENROUTER_MODEL",
    "OPENROUTER_MODEL_CAPABILITY_PROFILES",
    "CapabilityRequirement",
    "CompletionTokenParameter",
    "CompletionTokenParameterOverride",
    "CostBudgetError",
    "ModelCapabilityProfile",
    "ModelProfileConflict",
    "ModelProviderCapabilities",
    "ModelProviderRegistration",
    "ModelProviderRegistry",
    "NormalizationState",
    "NormalizedCost",
    "NormalizedPromptCache",
    "NormalizedUsage",
    "OpaqueContinuation",
    "PromptCacheState",
    "ProviderCallAmbiguous",
    "ProviderCallTimeout",
    "ProviderCapability",
    "ProviderNegotiationError",
    "ProviderPin",
    "ProviderRevisionConflict",
    "RetryableProviderError",
    "StructuredOutputDialect",
    "declared_model_capabilities",
    "enforce_cost_budget",
    "invoke_with_retry",
    "invoke_with_timeout",
    "normalize_cost",
    "normalize_prompt_cache",
    "normalize_usage",
]
