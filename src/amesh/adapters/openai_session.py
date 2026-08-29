"""OpenAI-style transport translation for the canonical agent-session API.

The adapter owns only wire compatibility.  Session creation, model selection,
provider credentials, tool authority and harness execution stay behind the
injected canonical session facade.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator, Mapping
from datetime import UTC, datetime
from typing import Any, Literal, Protocol
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

ChatMessageRole = Literal["system", "user", "assistant", "tool"]
FinishReason = Literal["stop", "length", "tool_calls"]
ResponseInputRole = Literal["user", "assistant", "system", "developer"]
ResponseStatus = Literal["completed", "incomplete"]


class OpenAIChatCompletionRequest(BaseModel):
    """Supported OpenAI chat-completion request fields at the HTTP edge."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    model: str = Field(min_length=1, max_length=512)
    messages: tuple[dict[str, Any], ...] = Field(min_length=1, max_length=100)
    stream: bool = False
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(
        default=None,
        validation_alias=AliasChoices("top_p", "topP"),
        ge=0,
        le=1,
    )
    max_tokens: int | None = Field(
        default=None,
        validation_alias=AliasChoices("max_tokens", "maxTokens"),
        ge=1,
        le=1_000_000,
    )
    max_completion_tokens: int | None = Field(
        default=None,
        validation_alias=AliasChoices("max_completion_tokens", "maxCompletionTokens"),
        ge=1,
        le=1_000_000,
    )
    response_format: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("response_format", "responseFormat"),
    )
    user: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
        for message in value:
            if not isinstance(message, Mapping):
                raise ValueError("messages must be objects")
            if message.get("role") not in {"system", "user", "assistant", "tool"}:
                raise ValueError("messages must use a supported OpenAI chat role")
            unsupported = set(message) - {"role", "content"}
            if unsupported:
                raise ValueError(
                    "messages support only role and text content; unsupported fields: "
                    + ", ".join(sorted(str(item) for item in unsupported))
                )
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("messages content must be a non-blank string")
        return value

    @model_validator(mode="after")
    def validate_token_aliases(self) -> OpenAIChatCompletionRequest:
        if (
            self.max_tokens is not None
            and self.max_completion_tokens is not None
            and self.max_tokens != self.max_completion_tokens
        ):
            raise ValueError("maxTokens and maxCompletionTokens must agree when both are supplied")
        return self


class OpenAIResponseInputText(BaseModel):
    """Text-only content item accepted by the Responses compatibility subset."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["input_text"] = "input_text"
    text: str = Field(min_length=1, max_length=1_000_000)


class OpenAIResponseInputMessage(BaseModel):
    """Responses message input normalized into a canonical chat-style message."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["message"] = "message"
    role: ResponseInputRole
    content: str | tuple[OpenAIResponseInputText, ...]

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: Any) -> Any:
        if isinstance(value, str):
            if not value.strip():
                raise ValueError("Responses message content must not be blank")
            return value
        if not isinstance(value, (list, tuple)) or not value:
            raise ValueError(
                "Responses message content must be text or a non-empty input_text list"
            )
        for part in value:
            if not isinstance(part, Mapping) or part.get("type") != "input_text":
                raise ValueError(
                    "Responses message content supports only input_text items in this endpoint"
                )
        return value


class OpenAIResponseTextFormat(BaseModel):
    """Supported Responses text/structured-output format."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    type: Literal["text", "json_object", "json_schema"] = "text"
    name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=512)
    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    strict: bool | None = None

    @model_validator(mode="after")
    def validate_format_fields(self) -> OpenAIResponseTextFormat:
        structured_fields = (self.name, self.description, self.schema_, self.strict)
        if self.type == "json_schema":
            if self.name is None or self.schema_ is None:
                raise ValueError("json_schema text format requires name and schema")
            return self
        if any(value is not None for value in structured_fields):
            raise ValueError(
                "name, description, schema, and strict are supported only for json_schema"
            )
        return self


class OpenAIResponseTextConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    format: OpenAIResponseTextFormat = Field(default_factory=OpenAIResponseTextFormat)


class OpenAIResponseRequest(BaseModel):
    """Supported request fields for the Responses compatibility endpoint."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    model: str = Field(min_length=1, max_length=512)
    input: str | tuple[OpenAIResponseInputMessage, ...]
    instructions: str | None = Field(default=None, min_length=1, max_length=1_000_000)
    stream: bool = False
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(
        default=None,
        validation_alias=AliasChoices("top_p", "topP"),
        ge=0,
        le=1,
    )
    max_output_tokens: int | None = Field(
        default=None,
        validation_alias=AliasChoices("max_output_tokens", "maxOutputTokens"),
        ge=1,
        le=1_000_000,
    )
    text: OpenAIResponseTextConfig | None = None
    user: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("input", mode="before")
    @classmethod
    def validate_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            if not value.strip():
                raise ValueError("Responses input text must not be blank")
            return value
        if not isinstance(value, (list, tuple)) or not value:
            raise ValueError("Responses input must be text or a non-empty message list")
        for item in value:
            if not isinstance(item, Mapping) or item.get("type", "message") != "message":
                raise ValueError("Responses input supports only message items in this endpoint")
        return value


class CanonicalSessionRequest(BaseModel):
    """Harness-neutral request passed to the existing session authority.

    ``profile`` is an authorized AMESH profile alias, not a provider model ID.
    The session authority resolves its immutable provider/model/harness pins.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    profile: str = Field(min_length=1, max_length=512)
    messages: tuple[dict[str, Any], ...] = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)


class HarnessProvenance(BaseModel):
    """Safe adapter provenance; credentials and private state are excluded."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adapter: str = Field(min_length=1, max_length=128)
    adapter_version: str = Field(alias="adapterVersion", min_length=1, max_length=128)


class CanonicalSessionResult(BaseModel):
    """Completed canonical session result supplied by the session service."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: UUID = Field(alias="sessionId")
    profile: str = Field(min_length=1, max_length=512)
    content: str | dict[str, Any]
    finish_reason: FinishReason = Field(default="stop", alias="finishReason")
    usage: dict[str, Any] | None = None
    created: int | None = Field(default=None, ge=0)
    harness: HarnessProvenance | None = None


class OpenAIUsage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    prompt_tokens: int = Field(alias="prompt_tokens", ge=0)
    completion_tokens: int = Field(alias="completion_tokens", ge=0)
    total_tokens: int = Field(alias="total_tokens", ge=0)


class OpenAIChatMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Literal["assistant"] = "assistant"
    content: str


class OpenAIChatChoice(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    index: int = Field(ge=0)
    message: OpenAIChatMessage
    finish_reason: FinishReason = Field(alias="finish_reason")


class OpenAIChatCompletionResponse(BaseModel):
    """OpenAI chat-completion response generated from a canonical result."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(ge=0)
    model: str = Field(min_length=1, max_length=512)
    choices: tuple[OpenAIChatChoice, ...] = Field(min_length=1, max_length=1)
    usage: OpenAIUsage | None = None


class OpenAIResponseInputTokensDetails(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    cached_tokens: int = Field(default=0, ge=0)


class OpenAIResponseOutputTokensDetails(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    reasoning_tokens: int = Field(default=0, ge=0)


class OpenAIResponseUsage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    input_tokens: int = Field(ge=0)
    input_tokens_details: OpenAIResponseInputTokensDetails = Field(
        default_factory=OpenAIResponseInputTokensDetails
    )
    output_tokens: int = Field(ge=0)
    output_tokens_details: OpenAIResponseOutputTokensDetails = Field(
        default_factory=OpenAIResponseOutputTokensDetails
    )
    total_tokens: int = Field(ge=0)


class OpenAIResponseOutputText(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["output_text"] = "output_text"
    text: str
    annotations: tuple[dict[str, Any], ...] = ()


class OpenAIResponseOutputMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    type: Literal["message"] = "message"
    status: ResponseStatus
    role: Literal["assistant"] = "assistant"
    content: tuple[OpenAIResponseOutputText, ...] = Field(min_length=1, max_length=1)


class OpenAIResponseIncompleteDetails(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    reason: Literal["max_output_tokens"]


class OpenAIResponse(BaseModel):
    """Completed or token-limited OpenAI-compatible Responses object."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    object: Literal["response"] = "response"
    created_at: int = Field(ge=0)
    status: ResponseStatus
    completed_at: int | None = Field(default=None, ge=0)
    error: dict[str, Any] | None = None
    incomplete_details: OpenAIResponseIncompleteDetails | None = None
    instructions: str | None = None
    model: str = Field(min_length=1, max_length=512)
    output: tuple[OpenAIResponseOutputMessage, ...] = Field(min_length=1, max_length=1)
    output_text: str
    usage: OpenAIResponseUsage | None = None


class CanonicalSessionFacade(Protocol):
    """Existing session authority used by the OpenAI edge adapter."""

    async def complete(
        self,
        request: CanonicalSessionRequest,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
        idempotency_key: str | None,
    ) -> CanonicalSessionResult: ...


def to_canonical_session_request(
    request: OpenAIChatCompletionRequest,
) -> CanonicalSessionRequest:
    """Translate the supported OpenAI request into neutral session input."""

    parameters: dict[str, Any] = {}
    if request.temperature is not None:
        parameters["temperature"] = request.temperature
    if request.top_p is not None:
        parameters["topP"] = request.top_p
    token_limit = request.max_completion_tokens or request.max_tokens
    if token_limit is not None:
        parameters["maxCompletionTokens"] = token_limit
    if request.response_format is not None:
        parameters["responseFormat"] = copy.deepcopy(request.response_format)
    if request.user is not None:
        parameters["user"] = request.user
    return CanonicalSessionRequest(
        profile=request.model,
        messages=tuple(copy.deepcopy(message) for message in request.messages),
        parameters=parameters,
    )


def to_canonical_response_request(request: OpenAIResponseRequest) -> CanonicalSessionRequest:
    """Translate the supported Responses request into neutral session input."""

    messages: list[dict[str, Any]] = []
    if request.instructions is not None:
        messages.append({"role": "developer", "content": request.instructions})
    if isinstance(request.input, str):
        messages.append({"role": "user", "content": request.input})
    else:
        messages.extend(
            {
                "role": message.role,
                "content": _response_input_content(message.content),
            }
            for message in request.input
        )

    parameters: dict[str, Any] = {}
    if request.temperature is not None:
        parameters["temperature"] = request.temperature
    if request.top_p is not None:
        parameters["topP"] = request.top_p
    if request.max_output_tokens is not None:
        parameters["maxCompletionTokens"] = request.max_output_tokens
    response_format = _response_format_parameter(request.text)
    if response_format is not None:
        parameters["responseFormat"] = response_format
    if request.user is not None:
        parameters["user"] = request.user

    return CanonicalSessionRequest(
        profile=request.model,
        messages=tuple(messages),
        parameters=parameters,
    )


def from_canonical_session_result(
    result: CanonicalSessionResult,
) -> OpenAIChatCompletionResponse:
    """Translate one canonical result into one OpenAI-compatible response."""

    content = _content_to_text(result.content)
    return OpenAIChatCompletionResponse(
        id=f"chatcmpl-{result.session_id}",
        created=result.created
        if result.created is not None
        else int(datetime.now(UTC).timestamp()),
        model=result.profile,
        choices=(
            OpenAIChatChoice(
                index=0,
                message=OpenAIChatMessage(content=content),
                finish_reason=result.finish_reason,
            ),
        ),
        usage=_usage_from_mapping(result.usage),
    )


def from_canonical_response_result(result: CanonicalSessionResult) -> OpenAIResponse:
    """Translate one canonical result into a Responses-compatible object."""

    created_at = (
        result.created if result.created is not None else int(datetime.now(UTC).timestamp())
    )
    content = _content_to_text(result.content)
    status: ResponseStatus = "incomplete" if result.finish_reason == "length" else "completed"
    incomplete_details = (
        OpenAIResponseIncompleteDetails(reason="max_output_tokens")
        if status == "incomplete"
        else None
    )
    return OpenAIResponse(
        id=f"resp_{result.session_id}",
        created_at=created_at,
        status=status,
        completed_at=created_at if status == "completed" else None,
        incomplete_details=incomplete_details,
        model=result.profile,
        output=(
            OpenAIResponseOutputMessage(
                id=f"msg_{result.session_id}",
                status=status,
                content=(OpenAIResponseOutputText(text=content),),
            ),
        ),
        output_text=content,
        usage=_response_usage_from_mapping(result.usage),
    )


def openai_sse_events(
    response: OpenAIChatCompletionResponse,
    *,
    chunk_size: int = 1024,
) -> Iterator[str]:
    """Yield bounded OpenAI-style SSE chunks for a completed response."""

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    choice = response.choices[0]

    def encode_event(payload: dict[str, Any]) -> str:
        return "data: " + json.dumps(payload, separators=(",", ":")) + "\n\n"

    yield encode_event(
        {
            "id": response.id,
            "object": "chat.completion.chunk",
            "created": response.created,
            "model": response.model,
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        }
    )
    content = choice.message.content
    for offset in range(0, len(content), chunk_size):
        yield encode_event(
            {
                "id": response.id,
                "object": "chat.completion.chunk",
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": content[offset : offset + chunk_size]},
                        "finish_reason": None,
                    }
                ],
            }
        )
    final: dict[str, Any] = {
        "id": response.id,
        "object": "chat.completion.chunk",
        "created": response.created,
        "model": response.model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": choice.finish_reason}],
    }
    if response.usage is not None:
        final["usage"] = response.usage.model_dump(mode="json", by_alias=True)
    yield encode_event(final)
    yield "data: [DONE]\n\n"


def openai_response_sse_events(
    response: OpenAIResponse,
    *,
    chunk_size: int = 1024,
) -> Iterator[str]:
    """Yield Responses SSE events for an already completed canonical result."""

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")

    sequence_number = 0

    def encode_event(event_type: str, payload: dict[str, Any]) -> str:
        nonlocal sequence_number
        body = {"type": event_type, "sequence_number": sequence_number, **payload}
        sequence_number += 1
        return (
            f"event: {event_type}\n"
            f"data: {json.dumps(body, ensure_ascii=False, separators=(',', ':'))}\n\n"
        )

    final_response = response.model_dump(mode="json")
    in_progress_response = copy.deepcopy(final_response)
    in_progress_response.update(
        {
            "status": "in_progress",
            "completed_at": None,
            "incomplete_details": None,
            "output": [],
            "output_text": "",
            "usage": None,
        }
    )
    yield encode_event("response.created", {"response": in_progress_response})
    yield encode_event("response.in_progress", {"response": in_progress_response})

    item = response.output[0]
    final_item = item.model_dump(mode="json")
    in_progress_item = {
        "id": item.id,
        "type": "message",
        "status": "in_progress",
        "role": "assistant",
        "content": [],
    }
    yield encode_event(
        "response.output_item.added",
        {"output_index": 0, "item": in_progress_item},
    )

    part = item.content[0]
    final_part = part.model_dump(mode="json")
    empty_part = {"type": "output_text", "text": "", "annotations": []}
    part_location = {
        "item_id": item.id,
        "output_index": 0,
        "content_index": 0,
    }
    yield encode_event(
        "response.content_part.added",
        {**part_location, "part": empty_part},
    )
    for offset in range(0, len(part.text), chunk_size):
        yield encode_event(
            "response.output_text.delta",
            {**part_location, "delta": part.text[offset : offset + chunk_size]},
        )
    yield encode_event(
        "response.output_text.done",
        {**part_location, "text": part.text},
    )
    yield encode_event(
        "response.content_part.done",
        {**part_location, "part": final_part},
    )
    yield encode_event(
        "response.output_item.done",
        {"output_index": 0, "item": final_item},
    )
    terminal_event = (
        "response.completed" if response.status == "completed" else "response.incomplete"
    )
    yield encode_event(terminal_event, {"response": final_response})


class OpenAICompatibleSessionAdapter:
    """OpenAI wire adapter over an injected canonical session service."""

    def __init__(self, facade: CanonicalSessionFacade) -> None:
        self._facade = facade

    async def create_chat_completion(
        self,
        request: OpenAIChatCompletionRequest,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
        idempotency_key: str | None = None,
    ) -> OpenAIChatCompletionResponse:
        result = await self._facade.complete(
            to_canonical_session_request(request),
            tenant_id=tenant_id,
            namespace=namespace,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        return from_canonical_session_result(result)

    async def create_response(
        self,
        request: OpenAIResponseRequest,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
        idempotency_key: str | None = None,
    ) -> OpenAIResponse:
        result = await self._facade.complete(
            to_canonical_response_request(request),
            tenant_id=tenant_id,
            namespace=namespace,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        return from_canonical_response_result(result)


def _content_to_text(value: str | dict[str, Any]) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _response_input_content(value: str | tuple[OpenAIResponseInputText, ...]) -> str:
    if isinstance(value, str):
        return value
    return "".join(part.text for part in value)


def _response_format_parameter(
    text: OpenAIResponseTextConfig | None,
) -> dict[str, Any] | None:
    if text is None or text.format.type == "text":
        return None
    if text.format.type == "json_object":
        return {"type": "json_object"}

    schema: dict[str, Any] = {
        "name": text.format.name,
        "schema": copy.deepcopy(text.format.schema_),
    }
    if text.format.description is not None:
        schema["description"] = text.format.description
    if text.format.strict is not None:
        schema["strict"] = text.format.strict
    return {"type": "json_schema", "json_schema": schema}


def _response_usage_from_mapping(
    value: Mapping[str, Any] | None,
) -> OpenAIResponseUsage | None:
    usage = _usage_from_mapping(value)
    if usage is None:
        return None
    return OpenAIResponseUsage(
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
    )


def _usage_from_mapping(value: Mapping[str, Any] | None) -> OpenAIUsage | None:
    if value is None:
        return None
    prompt = value.get("prompt_tokens", value.get("inputTokens", 0))
    completion = value.get("completion_tokens", value.get("outputTokens", 0))
    total = value.get("total_tokens", value.get("totalTokens"))
    if any(isinstance(item, bool) or not isinstance(item, int) for item in (prompt, completion)):
        raise ValueError("canonical session usage must contain integer token counts")
    if total is None:
        total = prompt + completion
    elif isinstance(total, bool) or not isinstance(total, int):
        raise ValueError("canonical session usage must contain integer token counts")
    return OpenAIUsage(
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=total,
    )
