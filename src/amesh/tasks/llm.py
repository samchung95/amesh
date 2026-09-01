from __future__ import annotations

import json
import os
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, cast
from uuid import UUID, uuid5

import httpx
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    field_validator,
    model_validator,
)

from amesh.adapters.openai_compatible import (
    OpenAICompatibleModelProvider,
    OpenAICompatibleProviderError,
)
from amesh.domain import (
    AgentInvocationKind,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    FailureCategory,
    ModelBudget,
    ModelDataEgress,
    ModelDataHandling,
    ModelOperation,
    ModelProviderSpec,
    ModelToolDefinition,
    PromptRetention,
    canonical_hash,
)
from amesh.domain.agent_primitives import (
    validate_model_provider_options,
    validate_model_request_options,
)
from amesh.domain.agent_progress import (
    AgentProgressFrame,
    AgentPublicSummaryDetail,
    AgentStatusDetail,
)
from amesh.domain.image_inputs import (
    ContentPart,
    ImageContentPart,
    InputModality,
    MultimodalMessage,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskCompletion,
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskHandler,
    TaskMetricRecord,
)
from amesh.model_continuations import ModelContinuationProtector
from amesh.model_providers import (
    DEFAULT_OPENROUTER_MODEL,
    OPENROUTER_MODEL_CAPABILITY_PROFILES,
    CapabilityRequirement,
    ModelProviderCapabilities,
    ModelProviderRegistry,
    ProviderCapability,
    ProviderPin,
    StructuredOutputDialect,
    normalize_cost,
    normalize_usage,
)
from amesh.ports import (
    AgentPrimitiveRepository,
    AgentProgressContext,
    AgentProgressSink,
    ImageArtifactResolver,
    ModelProvider,
    ModelProviderRequest,
    ModelProviderResponse,
    ModelProviderStreamEvent,
)
from amesh.tasks.http import HttpTaskPolicy

DEFAULT_OPENROUTER_CHAT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_EMBEDDING_ENDPOINT = "https://openrouter.ai/api/v1/embeddings"

_TASK_OPERATIONS = {
    "agent.llm": ModelOperation.CHAT,
    "agent.chat": ModelOperation.CHAT,
    "agent.embedding": ModelOperation.EMBEDDING,
    "agent.structured": ModelOperation.STRUCTURED,
    "agent.toolCall": ModelOperation.TOOL_CALL,
}


class _StructuredModelOutputError(ValueError):
    """A provider response that reached AMESH but failed structured normalization."""

    def __init__(
        self,
        message: str,
        *,
        kind: str,
        path: str,
        partial_output: dict[str, Any],
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.path = path
        self.partial_output = partial_output


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    api_key: str
    endpoint: str = DEFAULT_OPENROUTER_CHAT_ENDPOINT
    embedding_endpoint: str = DEFAULT_OPENROUTER_EMBEDDING_ENDPOINT
    default_model: str = DEFAULT_OPENROUTER_MODEL

    @classmethod
    def from_environment(cls) -> OpenAICompatibleConfig:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required for agent.llm")
        return cls(
            api_key=api_key,
            endpoint=os.getenv("OPENROUTER_CHAT_COMPLETIONS_URL", DEFAULT_OPENROUTER_CHAT_ENDPOINT),
            embedding_endpoint=os.getenv(
                "OPENROUTER_EMBEDDINGS_URL",
                DEFAULT_OPENROUTER_EMBEDDING_ENDPOINT,
            ),
            default_model=os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
        )


class _MessageRole(StrEnum):
    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class _ModelMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: _MessageRole
    content: str | tuple[ContentPart, ...]

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: object) -> object:
        if isinstance(value, str):
            if not value:
                raise ValueError("message content cannot be empty")
            if len(value) > 1_000_000:
                raise ValueError("message content exceeds the maximum length")
            return value
        if not isinstance(value, list | tuple):
            raise ValueError("message content must be text or an ordered content-part list")
        return value

    @model_validator(mode="after")
    def validate_multimodal_content(self) -> _ModelMessage:
        if isinstance(self.content, str):
            return self
        # Reuse the platform-wide multimodal contract for role restrictions,
        # image limits, and the discriminated content-part schema.
        validated = MultimodalMessage(role=self.role.value, content=self.content)
        object.__setattr__(self, "content", validated.content)
        return self

    @property
    def has_image_input(self) -> bool:
        return any(isinstance(part, ImageContentPart) for part in self.content)


class _ModelParameters(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, alias="topP", gt=0, le=1)
    seed: int | None = None
    provider_options: dict[str, Any] = Field(
        default_factory=dict,
        alias="providerOptions",
        max_length=16,
    )
    request_options: dict[str, Any] = Field(
        default_factory=dict,
        alias="requestOptions",
        max_length=16,
    )

    @field_validator("provider_options")
    @classmethod
    def validate_provider_options(cls, value: dict[str, Any]) -> dict[str, Any]:
        return validate_model_provider_options(value)

    @field_validator("request_options")
    @classmethod
    def validate_request_options(cls, value: dict[str, Any]) -> dict[str, Any]:
        return validate_model_request_options(value)

    def provider_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.seed is not None:
            payload["seed"] = self.seed
        if self.provider_options:
            payload["provider"] = dict(self.provider_options)
        payload.update(self.request_options)
        return payload


class _ModelTaskSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    operation: ModelOperation
    provider: ModelProviderSpec
    model: str = Field(min_length=1, max_length=512)
    budget: ModelBudget | None
    max_completion_tokens: int | None = Field(
        default=None,
        alias="maxCompletionTokens",
        ge=1,
    )
    data_handling: ModelDataHandling = Field(alias="dataHandling")
    messages: tuple[_ModelMessage, ...] = ()
    embedding_input: str | tuple[str, ...] | None = Field(default=None, alias="input")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")
    schema_name: str = Field(default="amesh_output", alias="schemaName", min_length=1)
    tools: tuple[ModelToolDefinition, ...] = ()
    tool_choice: str | None = Field(default=None, alias="toolChoice")
    parameters: _ModelParameters = Field(default_factory=_ModelParameters)

    @model_validator(mode="after")
    def validate_operation_contract(self) -> _ModelTaskSpec:
        if self.operation is ModelOperation.EMBEDDING:
            if self.embedding_input is None or self.messages:
                raise ValueError("embedding tasks require input and cannot declare messages")
            if isinstance(self.embedding_input, tuple) and not self.embedding_input:
                raise ValueError("embedding input cannot be empty")
        elif not self.messages:
            raise ValueError(f"{self.operation.value.lower()} tasks require prompt or messages")
        if self.operation is ModelOperation.STRUCTURED and self.output_schema is None:
            raise ValueError("structured tasks require outputSchema")
        if self.operation is ModelOperation.TOOL_CALL and not self.tools:
            raise ValueError("tool-call tasks require at least one tool")
        if self.operation is not ModelOperation.TOOL_CALL and (self.tools or self.tool_choice):
            raise ValueError("tools and toolChoice are valid only for tool-call tasks")
        if self.output_schema is not None:
            try:
                Draft202012Validator.check_schema(self.output_schema)
            except SchemaError as exc:
                raise ValueError(f"invalid structured output schema: {exc.message}") from exc
        return self


def agent_llm_handler(
    configuration: OpenAICompatibleConfig | None = None,
    client: httpx.AsyncClient | None = None,
    *,
    http_policy: HttpTaskPolicy | None = None,
    provider: ModelProvider | None = None,
    repository: AgentPrimitiveRepository | None = None,
    provider_registry: ModelProviderRegistry | None = None,
    continuation_protector: ModelContinuationProtector | None = None,
    image_resolver: ImageArtifactResolver | None = None,
    progress_sink: AgentProgressSink | None = None,
) -> TaskHandler:
    active_provider = provider or OpenAICompatibleModelProvider(
        client,
        http_policy=http_policy,
        image_resolver=image_resolver,
    )
    registry = provider_registry or ModelProviderRegistry()

    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        extra = dict(task.model_extra or {})
        operation = _TASK_OPERATIONS.get(task.type)
        if operation is None:
            raise ValueError(f"unsupported model task type {task.type!r}")
        spec, credential = _parse_task_spec(task, context, operation, configuration)
        continuation_source = _continuation_source(extra)
        progress_context = _parse_progress_context(extra, context, progress_sink)
        provider_pin = _negotiate_provider(
            registry,
            active_provider,
            spec,
            require_continuation=continuation_source is not None,
        )
        continuation, continuation_metadata = await _load_continuation(
            continuation_source,
            context=context,
            repository=repository,
            protector=continuation_protector,
            provider_pin=provider_pin,
        )
        outbound_payload = _provider_payload(spec, provider_pin)
        outbound_payload = _apply_egress_policy(
            outbound_payload,
            spec.data_handling.egress,
            tuple(context.secrets.values()),
        )
        endpoint = (
            spec.provider.embedding_endpoint or spec.provider.endpoint
            if operation is ModelOperation.EMBEDDING
            else spec.provider.endpoint
        )
        request_hash = canonical_hash(
            {
                "adapter": spec.provider.adapter,
                "endpoint": endpoint,
                "operation": operation.value,
                "payload": outbound_payload,
                "continuation": continuation_metadata,
            }
        )
        request_metadata = _request_metadata(
            spec,
            endpoint,
            outbound_payload,
            request_hash,
            tuple(context.secrets.values()),
            task,
            provider_pin,
            continuation_metadata,
        )
        journal_operation = _journal_operation(operation.value, extra, request_metadata)
        claim = None
        if repository is not None:
            claim = await repository.begin_invocation(
                AgentInvocationStart(
                    invocationId=uuid5(context.attempt_id, f"model:{journal_operation}"),
                    tenantId=context.tenant_id,
                    namespace=context.namespace,
                    executionId=context.execution_id,
                    taskRunId=context.task_run_id,
                    attempt=context.attempt,
                    kind=AgentInvocationKind.MODEL,
                    operation=journal_operation,
                    requestHash=request_hash,
                    requestMetadata=request_metadata,
                )
            )
            if not claim.created:
                return _reused_completion(claim.record)
        invocation_id = claim.record.invocation_id if claim is not None else None
        try:
            provider_request = ModelProviderRequest(
                operation=operation.value,
                endpoint=endpoint,
                model=spec.model,
                payload=outbound_payload,
                timeoutSeconds=task.timeout_seconds or 60,
                tenantId=context.tenant_id,
                continuation=continuation,
            )
            stream = getattr(provider_pin.registration.adapter, "stream", None)
            if progress_context is not None and callable(stream):
                response = await _invoke_stream_with_progress(
                    stream,
                    provider_request,
                    SecretStr(credential),
                    progress_context=progress_context,
                    sink=progress_sink,
                    invocation_id=invocation_id,
                    execution_id=context.execution_id,
                    task_run_id=context.task_run_id,
                    journal_operation=journal_operation,
                    secrets=tuple(context.secrets.values()),
                )
            else:
                response = await provider_pin.registration.adapter.invoke(
                    provider_request,
                    SecretStr(credential),
                )
            try:
                output = _normalize_response(spec, response.payload, request_metadata)
            except _StructuredModelOutputError as exc:
                _enforce_budget(spec.budget, exc.partial_output)
                raise
            _enforce_budget(spec.budget, output)
            safe_output = _redact_values(output, tuple(context.secrets.values()))
            protected_continuation = None
            if response.continuation is not None and repository is not None:
                if invocation_id is None or continuation_protector is None:
                    raise RuntimeError(
                        "provider returned continuation state but durable protected storage is unavailable"
                    )
                if not provider_pin.capabilities.opaque_continuation:
                    raise RuntimeError(
                        "provider returned continuation state without declaring opaque_continuation"
                    )
                protected_continuation = continuation_protector.protect(
                    tenant_id=context.tenant_id,
                    invocation_id=invocation_id,
                    provider_id=provider_pin.provider_id,
                    provider_revision=provider_pin.revision,
                    token=response.continuation,
                )
                safe_output["continuation"] = {
                    "invocationId": str(invocation_id),
                    **protected_continuation.public_metadata(),
                }
            if repository is not None and invocation_id is not None:
                await repository.complete_invocation(
                    invocation_id,
                    tenant_id=context.tenant_id,
                    state=AgentInvocationState.SUCCEEDED,
                    result=safe_output,
                    protected_continuation=protected_continuation,
                )
            return _completion(safe_output)
        except Exception as exc:
            secret_values = tuple(context.secrets.values())
            safe_error = str(_redact_values(_safe_error(exc), secret_values))
            if repository is not None and invocation_id is not None:
                await repository.complete_invocation(
                    invocation_id,
                    tenant_id=context.tenant_id,
                    state=AgentInvocationState.FAILED,
                    error=safe_error,
                )
            raise _model_failure(
                exc,
                invocation_id,
                request_hash,
                secrets=secret_values,
            ) from exc

    return run


def _parse_progress_context(
    extra: dict[str, Any],
    context: TaskExecutionContext,
    sink: AgentProgressSink | None,
) -> AgentProgressContext | None:
    raw_context = extra.get("progressContext")
    if raw_context is None:
        return None
    if sink is None:
        raise ValueError("progressContext requires an AgentProgressSink")
    try:
        progress_context = AgentProgressContext.model_validate(raw_context)
    except ValidationError as exc:
        raise ValueError("progressContext is invalid") from exc
    if (
        progress_context.tenant_id != context.tenant_id
        or progress_context.execution_id != context.execution_id
        or progress_context.task_run_id != context.task_run_id
        or progress_context.attempt != context.attempt
    ):
        raise ValueError("progressContext does not match the task execution context")
    return progress_context


async def _invoke_stream_with_progress(
    stream: Any,
    request: ModelProviderRequest,
    credential: SecretStr,
    *,
    progress_context: AgentProgressContext,
    sink: AgentProgressSink | None,
    invocation_id: UUID | None,
    execution_id: UUID,
    task_run_id: UUID,
    journal_operation: str,
    secrets: tuple[str, ...],
) -> ModelProviderResponse:
    if sink is None:
        raise ValueError("streaming progress requires an AgentProgressSink")
    model_identity = invocation_id or uuid5(
        execution_id,
        f"model:{task_run_id}:{journal_operation}",
    )
    source_id = f"model:{model_identity}"
    active_segment_id = None
    response: ModelProviderResponse | None = None
    try:
        async for event in stream(request, credential):
            if not isinstance(event, ModelProviderStreamEvent):
                event = ModelProviderStreamEvent.model_validate(event)
            if event.kind == "progress":
                progress = event.progress
                if progress is None:
                    raise ValueError("provider progress event did not contain progress")
                detail = progress.detail
                if isinstance(detail, AgentPublicSummaryDetail):
                    detail = AgentStatusDetail(
                        code="model.processing",
                        label="Model processing",
                    )
                frame = AgentProgressFrame(
                    attemptSessionId=progress_context.attempt_session_id,
                    attempt=progress_context.attempt,
                    activity=progress.activity,
                    status=progress.status,
                    activityId=progress.activity_id,
                    segmentId=progress.segment_id,
                    sourceId=source_id,
                    sourceSequence=progress.source_sequence,
                    occurredAt=datetime.now(UTC),
                    detail=detail,
                )
                await sink.append(progress_context, frame)
                if frame.segment_id is None or frame.status.value in {
                    "COMPLETED",
                    "FAILED",
                    "CANCELLED",
                    "TRUNCATED",
                }:
                    active_segment_id = None
                else:
                    active_segment_id = frame.segment_id
                continue
            if event.response is None:
                raise ValueError("provider response event did not contain a response")
            if response is not None:
                raise ValueError("provider stream emitted multiple terminal responses")
            response = event.response
        if response is None:
            raise RuntimeError("provider stream ended without a terminal response")
        return response
    except BaseException:
        if active_segment_id is not None:
            with suppress(Exception):
                await sink.close_active_segment(progress_context, occurred_at=datetime.now(UTC))
        raise


def _journal_operation(
    operation: str,
    extra: dict[str, Any],
    metadata: dict[str, Any],
) -> str:
    invocation_key = extra.get("invocationKey")
    if invocation_key is None:
        return operation
    if not isinstance(invocation_key, str) or not invocation_key or len(invocation_key) > 255:
        raise ValueError("invocationKey must be a non-empty string of at most 255 characters")
    metadata["invocationKey"] = invocation_key
    return f"{operation[:80]}#{canonical_hash(invocation_key)[:32]}"


def _negotiate_provider(
    registry: ModelProviderRegistry,
    active_provider: ModelProvider,
    spec: _ModelTaskSpec,
    *,
    require_continuation: bool = False,
) -> ProviderPin:
    """Resolve an immutable provider pin before the adapter receives the request."""

    try:
        registry.resolve(spec.provider.adapter)
    except LookupError:
        registration = registry.register(
            spec.provider.adapter,
            "1.0.0",
            active_provider,
            ModelProviderCapabilities(
                structuredOutput=True,
                tool=True,
                streaming=callable(getattr(active_provider, "stream", None)),
                cancellation=True,
                usage=True,
                cache=True,
                cost=True,
                opaqueContinuation=True,
                imageInput=True,
            ),
        )
        for profile in OPENROUTER_MODEL_CAPABILITY_PROFILES:
            registry.register_model_profile(
                registration.provider_id,
                registration.revision,
                profile,
            )
    required = {
        ProviderCapability.CONTEXT,
        ProviderCapability.OUTPUT,
        ProviderCapability.TIMEOUT,
        ProviderCapability.USAGE,
    }
    if spec.operation is ModelOperation.STRUCTURED:
        required.add(ProviderCapability.STRUCTURED_OUTPUT)
    if spec.operation is ModelOperation.TOOL_CALL:
        required.add(ProviderCapability.TOOL)
    if spec.budget is not None:
        required.add(ProviderCapability.COST)
    if require_continuation:
        required.add(ProviderCapability.OPAQUE_CONTINUATION)
    input_modalities = {InputModality.TEXT}
    if any(message.has_image_input for message in spec.messages):
        input_modalities.add(InputModality.IMAGE)
    return registry.negotiate(
        spec.provider.adapter,
        CapabilityRequirement(
            required=frozenset(required),
            outputTokens=spec.max_completion_tokens,
            inputModalities=frozenset(input_modalities),
        ),
        revision=spec.provider.revision,
        model=spec.model,
    )


def _continuation_source(extra: dict[str, Any]) -> UUID | None:
    value = extra.get("continuationFromInvocationId")
    if value is None:
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError("continuationFromInvocationId must be a UUID") from exc


async def _load_continuation(
    source: UUID | None,
    *,
    context: TaskExecutionContext,
    repository: AgentPrimitiveRepository | None,
    protector: ModelContinuationProtector | None,
    provider_pin: ProviderPin,
) -> tuple[SecretStr | None, dict[str, str] | None]:
    if source is None:
        return None, None
    if repository is None or protector is None:
        raise RuntimeError("protected model continuation storage is unavailable")
    protected = await repository.get_model_continuation(source, tenant_id=context.tenant_id)
    if protected is None:
        raise LookupError(f"model invocation {source} has no continuation state")
    token = protector.reveal(
        protected,
        tenant_id=context.tenant_id,
        invocation_id=source,
        provider_id=provider_pin.provider_id,
        provider_revision=provider_pin.revision,
    )
    return token, {"sourceInvocationId": str(source), **protected.public_metadata()}


def _parse_task_spec(
    task: TaskDefinition,
    context: TaskExecutionContext,
    operation: ModelOperation,
    configuration: OpenAICompatibleConfig | None,
) -> tuple[_ModelTaskSpec, str]:
    extra = dict(task.model_extra or {})
    raw_provider = extra.get("provider")
    if raw_provider is None:
        if task.type != "agent.llm":
            raise ValueError(f"task {task.id!r} requires provider")
        active = configuration or OpenAICompatibleConfig.from_environment()
        provider = ModelProviderSpec(
            endpoint=active.endpoint,
            embeddingEndpoint=active.embedding_endpoint,
            credentialRef="openrouter",
        )
        credential = active.api_key
        budget = None
        data_handling = ModelDataHandling(
            egress=ModelDataEgress.REDACT_SECRETS,
            promptRetention=PromptRetention.REDACTED,
        )
        model = str(extra.get("model", active.default_model))
    else:
        provider = ModelProviderSpec.model_validate(raw_provider)
        if provider.credential_ref not in task.contract.secret_scopes:
            raise ValueError(
                f"task {task.id!r} provider credentialRef must be declared in contract.secretScopes"
            )
        credential = context.secrets.get(provider.credential_ref, "")
        if not credential:
            raise ValueError(
                f"task {task.id!r} credential {provider.credential_ref!r} is unavailable"
            )
        budget = ModelBudget.model_validate(extra.get("budget"))
        data_handling = ModelDataHandling.model_validate(extra.get("dataHandling"))
        model_value = extra.get("model")
        if not isinstance(model_value, str) or not model_value:
            raise ValueError(f"task {task.id!r} requires model")
        model = model_value
    messages = _messages(extra, task.id) if operation is not ModelOperation.EMBEDDING else ()
    embedding_input = _embedding_input(extra.get("input"), task.id)
    if operation is not ModelOperation.EMBEDDING:
        embedding_input = None
    try:
        spec = _ModelTaskSpec(
            operation=operation,
            provider=provider,
            model=model,
            budget=budget,
            maxCompletionTokens=(
                budget.max_completion_tokens
                if budget is not None
                else extra.get("maxCompletionTokens", 128)
            ),
            dataHandling=data_handling,
            messages=messages,
            input=embedding_input,
            outputSchema=extra.get("outputSchema"),
            schemaName=extra.get("schemaName", "amesh_output"),
            tools=extra.get("tools", ()),
            toolChoice=extra.get("toolChoice"),
            parameters=extra.get("parameters", {}),
        )
    except ValidationError as exc:
        raise ValueError(f"task {task.id!r} model configuration is invalid: {exc}") from exc
    if (
        spec.budget is not None
        and spec.max_completion_tokens is None
        and operation
        in {
            ModelOperation.CHAT,
            ModelOperation.STRUCTURED,
            ModelOperation.TOOL_CALL,
        }
    ):
        raise ValueError(f"task {task.id!r} budget requires maxCompletionTokens")
    return spec, credential


def _messages(extra: dict[str, Any], task_id: str) -> tuple[_ModelMessage, ...]:
    raw_messages = extra.get("messages")
    if raw_messages is None:
        prompt = extra.get("prompt")
        if not isinstance(prompt, str) or not prompt:
            return ()
        raw_messages = ({"role": "user", "content": prompt},)
    if not isinstance(raw_messages, list | tuple) or not raw_messages:
        raise ValueError(f"task {task_id!r} messages must be a non-empty list")
    try:
        return tuple(_ModelMessage.model_validate(message) for message in raw_messages)
    except ValidationError as exc:
        raise ValueError(f"task {task_id!r} messages are invalid: {exc}") from exc


def _embedding_input(value: object, task_id: str) -> str | tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, str) and value:
        return value
    if isinstance(value, list) and value and all(isinstance(item, str) and item for item in value):
        return tuple(value)
    raise ValueError(f"task {task_id!r} embedding input must be a string or non-empty string list")


def _provider_payload(spec: _ModelTaskSpec, provider_pin: ProviderPin) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": spec.model}
    if spec.operation is ModelOperation.EMBEDDING:
        payload["input"] = spec.embedding_input
        if spec.parameters.provider_options:
            payload["provider"] = dict(spec.parameters.provider_options)
        payload.update(spec.parameters.request_options)
        return payload
    messages = [message.model_dump(mode="json", by_alias=True) for message in spec.messages]
    payload["messages"] = messages
    payload.update(spec.parameters.provider_payload())
    if spec.max_completion_tokens is not None:
        completion_parameter = provider_pin.completion_token_parameter_for(
            spec.parameters.provider_options
        )
        payload[completion_parameter.value] = spec.max_completion_tokens
    if spec.operation is ModelOperation.STRUCTURED:
        dialect = provider_pin.structured_output_dialect
        if dialect is StructuredOutputDialect.JSON_SCHEMA:
            payload["response_format"] = {
                "type": dialect.value,
                "json_schema": {
                    "name": spec.schema_name,
                    "strict": True,
                    "schema": spec.output_schema,
                },
            }
        elif dialect is StructuredOutputDialect.JSON_OBJECT:
            payload["response_format"] = {"type": dialect.value}
            messages.insert(0, _json_object_schema_instruction(spec))
        else:
            raise RuntimeError("negotiated provider does not declare a structured-output dialect")
    if spec.operation is ModelOperation.TOOL_CALL:
        payload["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in spec.tools
        ]
        payload["tool_choice"] = spec.tool_choice or "auto"
    return payload


def _json_object_schema_instruction(spec: _ModelTaskSpec) -> dict[str, str]:
    schema = json.dumps(spec.output_schema, sort_keys=True, separators=(",", ":"))
    name = json.dumps(spec.schema_name, ensure_ascii=False)
    return {
        "role": "system",
        "content": (
            "Return exactly one JSON object and no surrounding prose or Markdown. "
            "The object must validate against the following Draft 2020-12 JSON Schema "
            f"named {name}: {schema}"
        ),
    }


def _apply_egress_policy(
    value: dict[str, Any],
    policy: ModelDataEgress,
    secrets: tuple[str, ...],
) -> dict[str, Any]:
    present = tuple(secret for secret in secrets if secret and _contains_value(value, secret))
    if present and policy is ModelDataEgress.DENY_SECRETS:
        raise ValueError("model request contains secret material denied by dataHandling.egress")
    if policy is ModelDataEgress.REDACT_SECRETS:
        return cast(dict[str, Any], _redact_values(value, secrets))
    return value


def _request_metadata(
    spec: _ModelTaskSpec,
    endpoint: str,
    payload: dict[str, Any],
    request_hash: str,
    secrets: tuple[str, ...],
    task: TaskDefinition,
    provider_pin: ProviderPin,
    continuation: dict[str, str] | None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "adapter": spec.provider.adapter,
        "endpoint": endpoint,
        "model": spec.model,
        "operation": spec.operation.value,
        "requestHash": request_hash,
        "budget": (
            spec.budget.model_dump(mode="json", by_alias=True)
            if spec.budget is not None
            else {"legacyUnboundedCost": True}
        ),
        "timeoutSeconds": task.timeout_seconds or 60,
        "retry": task.retry.model_dump(mode="json", by_alias=True),
        "dataHandling": spec.data_handling.model_dump(mode="json", by_alias=True),
        "nondeterministic": True,
        "providerId": provider_pin.provider_id,
        "providerRevision": provider_pin.revision,
        "providerDigest": provider_pin.digest,
        "capabilities": provider_pin.capabilities.model_dump(mode="json", by_alias=True),
    }
    if provider_pin.model_profile is not None:
        metadata["modelProfile"] = {
            "model": provider_pin.model_profile.model,
            "digest": provider_pin.model_profile.digest,
            "structuredOutputDialect": (
                provider_pin.structured_output_dialect.value
                if provider_pin.structured_output_dialect is not None
                else None
            ),
        }
    if spec.data_handling.prompt_retention is PromptRetention.REDACTED:
        metadata["request"] = _redact_values(payload, secrets)
    if continuation is not None:
        metadata["continuation"] = continuation
    return metadata


def _normalize_response(
    spec: _ModelTaskSpec,
    payload: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    usage = payload.get("usage") or {}
    if not isinstance(usage, dict):
        raise RuntimeError("model response usage must be an object")
    result: dict[str, Any] = {
        "operation": spec.operation.value,
        "model": str(payload.get("model", spec.model)),
        "usage": usage,
        "usageNormalized": normalize_usage(payload).model_dump(mode="json", by_alias=True),
        "costNormalized": normalize_cost(payload).model_dump(mode="json", by_alias=True),
        "provenance": provenance,
    }
    if spec.operation is ModelOperation.EMBEDDING:
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise RuntimeError("embedding response did not contain data")
        embeddings: list[list[float]] = []
        for item in data:
            vector = item.get("embedding") if isinstance(item, dict) else None
            if (
                not isinstance(vector, list)
                or not vector
                or not all(
                    isinstance(number, int | float) and not isinstance(number, bool)
                    for number in vector
                )
            ):
                raise RuntimeError("embedding response contained an invalid vector")
            embeddings.append([float(number) for number in vector])
        result["embeddings"] = embeddings
        return result
    message = _first_message(payload)
    if spec.operation is ModelOperation.TOOL_CALL:
        result["toolCalls"] = _tool_calls(message, spec.tools)
        return result
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("model response did not contain assistant content")
    if spec.operation is ModelOperation.CHAT:
        result["content"] = content
        return result
    try:
        structured = json.loads(content)
    except json.JSONDecodeError as exc:
        raise _StructuredModelOutputError(
            "structured model output is not valid JSON",
            kind="invalid_json",
            path="$",
            partial_output=result,
        ) from exc
    errors = sorted(
        Draft202012Validator(spec.output_schema or {}).iter_errors(structured),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        path = ".".join(str(part) for part in error.absolute_path) or "$"
        raise _StructuredModelOutputError(
            f"structured model output failed schema at {path}: {error.message}",
            kind="schema",
            path=path,
            partial_output=result,
        )
    result["structuredOutput"] = structured
    result["schemaDigest"] = "sha256:" + canonical_hash(spec.output_schema)
    return result


def _first_message(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise RuntimeError("model response did not contain choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("model response did not contain an assistant message")
    return message


def _tool_calls(
    message: dict[str, Any],
    definitions: tuple[ModelToolDefinition, ...],
) -> list[dict[str, Any]]:
    raw_calls = message.get("tool_calls")
    if not isinstance(raw_calls, list) or not raw_calls:
        raise RuntimeError("model response did not contain tool calls")
    by_name = {tool.name: tool for tool in definitions}
    normalized: list[dict[str, Any]] = []
    for index, raw_call in enumerate(raw_calls):
        function = raw_call.get("function") if isinstance(raw_call, dict) else None
        name = function.get("name") if isinstance(function, dict) else None
        raw_arguments = function.get("arguments") if isinstance(function, dict) else None
        if not isinstance(name, str) or name not in by_name:
            raise ValueError(f"model proposed unknown tool {name!r}")
        try:
            arguments = (
                json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
            )
        except json.JSONDecodeError as exc:
            raise ValueError(f"model tool {name!r} arguments are not valid JSON") from exc
        if not isinstance(arguments, dict):
            raise ValueError(f"model tool {name!r} arguments must be an object")
        try:
            Draft202012Validator(by_name[name].input_schema).validate(arguments)
        except JsonSchemaValidationError as exc:
            raise ValueError(f"model tool {name!r} arguments failed schema: {exc.message}") from exc
        normalized.append(
            {
                "id": str(raw_call.get("id", f"call-{index + 1}")),
                "name": name,
                "arguments": arguments,
            }
        )
    return normalized


def _enforce_budget(budget: ModelBudget | None, output: dict[str, Any]) -> None:
    if budget is None:
        return
    normalized_usage = output.get("usageNormalized")
    total_tokens = (
        normalized_usage.get("totalTokens") if isinstance(normalized_usage, dict) else None
    )
    if not isinstance(total_tokens, int) or isinstance(total_tokens, bool):
        raise RuntimeError("model provider did not report total_tokens required by the budget")
    if total_tokens > budget.max_total_tokens:
        raise ValueError(
            f"model response exceeded maxTotalTokens={budget.max_total_tokens}: {total_tokens}"
        )
    normalized_cost = output.get("costNormalized")
    raw_cost = normalized_cost.get("amountUsd") if isinstance(normalized_cost, dict) else None
    try:
        cost = Decimal(str(raw_cost))
    except (InvalidOperation, ValueError) as exc:
        raise RuntimeError("model provider did not report cost required by the budget") from exc
    if cost > budget.max_cost_usd:
        raise ValueError(f"model response exceeded maxCostUsd={budget.max_cost_usd}: {cost}")
    output["costUsd"] = str(cost)


def _completion(output: dict[str, Any]) -> TaskCompletion:
    usage = output.get("usage", {})
    metrics: list[TaskMetricRecord] = []
    if isinstance(usage.get("total_tokens"), int):
        metrics.append(
            TaskMetricRecord(
                name="agent.model.tokens",
                value=Decimal(usage["total_tokens"]),
                unit="tokens",
            )
        )
    if "costUsd" in output:
        metrics.append(
            TaskMetricRecord(
                name="agent.model.cost",
                value=Decimal(str(output["costUsd"])),
                unit="USD",
            )
        )
    return TaskCompletion(output=output, metrics=tuple(metrics))


def _reused_completion(record: AgentInvocationRecord) -> TaskCompletion:
    if record.state is AgentInvocationState.SUCCEEDED and record.result is not None:
        return _completion(record.result)
    evidence: dict[str, object] = {
        "agentInvocation": {
            "invocationId": str(record.invocation_id),
            "state": record.state.value,
            "requestHash": record.request_hash,
            "ambiguousExternalOutcome": record.state is AgentInvocationState.STARTED,
        }
    }
    if record.state is AgentInvocationState.STARTED:
        raise TaskExecutionFailure(
            "model invocation has an ambiguous external outcome and was not repeated",
            FailureCategory.INFRASTRUCTURE,
            evidence=evidence,
        )
    raise TaskExecutionFailure(
        record.error or "model invocation previously failed",
        FailureCategory.NON_RETRYABLE,
        evidence=evidence,
    )


def _model_failure(
    exc: Exception,
    invocation_id: object,
    request_hash: str,
    *,
    secrets: tuple[str, ...] = (),
) -> TaskExecutionFailure:
    provider_error = _provider_error_evidence(exc, secrets)
    if isinstance(exc, TaskExecutionFailure):
        category = exc.category
        result = exc.result
    elif isinstance(exc, httpx.TimeoutException | TimeoutError):
        category = FailureCategory.TIMED_OUT
        result = None
    elif isinstance(exc, httpx.HTTPStatusError):
        category = (
            FailureCategory.RETRYABLE
            if exc.response.status_code == 429 or exc.response.status_code >= 500
            else FailureCategory.NON_RETRYABLE
        )
        result = None
    elif isinstance(exc, httpx.TransportError | OSError):
        category = FailureCategory.INFRASTRUCTURE
        result = None
    elif isinstance(exc, (TypeError, ValueError, ValidationError)):
        category = FailureCategory.NON_RETRYABLE
        result = _structured_rejection_result(exc)
    else:
        category = FailureCategory.RETRYABLE
        result = None
    evidence: dict[str, object] = {
        "agentInvocation": {
            "invocationId": str(invocation_id) if invocation_id is not None else None,
            "state": AgentInvocationState.FAILED.value,
            "requestHash": request_hash,
            "nondeterministic": True,
        }
    }
    if provider_error is not None:
        evidence["providerError"] = provider_error
    if isinstance(exc, _StructuredModelOutputError):
        evidence["modelOutputRejection"] = {
            "kind": exc.kind,
            "path": exc.path,
            "message": str(_redact_values(str(exc), secrets))[:2000],
        }
    return TaskExecutionFailure(
        str(_redact_values(_safe_error(exc), secrets)),
        category,
        result=result,
        evidence=evidence,
    )


def _safe_error(exc: Exception) -> str:
    if isinstance(exc, OpenAICompatibleProviderError):
        return (
            f"{type(exc).__name__}: "
            f"{json.dumps(exc.diagnostic.as_dict(), sort_keys=True, separators=(',', ':'))}"
        )
    return f"{type(exc).__name__}: {str(exc)[:2000]}"


def _provider_error_evidence(
    exc: Exception,
    secrets: tuple[str, ...],
) -> dict[str, object] | None:
    if not isinstance(exc, OpenAICompatibleProviderError):
        return None
    return cast(
        dict[str, object],
        _redact_values(exc.diagnostic.as_dict(), secrets),
    )


def _structured_rejection_result(exc: Exception) -> dict[str, object] | None:
    if not isinstance(exc, _StructuredModelOutputError):
        return None
    return {
        key: value
        for key, value in exc.partial_output.items()
        if key
        in {
            "model",
            "usage",
            "usageNormalized",
            "costNormalized",
            "costUsd",
        }
    }


def _contains_value(value: object, secret: str) -> bool:
    if isinstance(value, str):
        return secret in value
    if isinstance(value, dict):
        return any(_contains_value(item, secret) for item in value.values())
    if isinstance(value, list | tuple):
        return any(_contains_value(item, secret) for item in value)
    return False


def _redact_values(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[REDACTED]")
        return redacted
    if isinstance(value, dict):
        return {str(key): _redact_values(item, secrets) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_redact_values(item, secrets) for item in value]
    return value
