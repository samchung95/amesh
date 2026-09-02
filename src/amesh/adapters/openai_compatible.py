from __future__ import annotations

import base64
import copy
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx
from pydantic import SecretStr

from amesh.domain.agent_progress import (
    AgentProgressActivity,
    AgentProgressStatus,
    AgentPublicSummaryDetail,
)
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.domain.image_validation import build_image_artifact_ref, inspect_image_bytes
from amesh.networking import HttpTaskPolicy, outbound_http_client, validate_http_destination
from amesh.ports.agent_primitives import (
    ImageArtifactResolver,
    ModelProviderAccess,
    ModelProviderContinuationBinding,
    ModelProviderProgressDelta,
    ModelProviderRequest,
    ModelProviderResponse,
    ModelProviderStreamEvent,
)
from amesh.ports.errors import ProviderDiagnosticError

_MAX_PROVIDER_DIAGNOSTIC_CHARS = 512


@dataclass(frozen=True)
class ProviderErrorDiagnostic:
    """Bounded, allowlisted provider failure details safe for propagation."""

    status: int
    type: str
    code: str | None
    message: str
    body_truncated: bool = False

    def as_dict(self) -> dict[str, object]:
        diagnostic: dict[str, object] = {
            "status": self.status,
            "type": self.type,
            "code": self.code,
            "message": self.message,
        }
        if self.body_truncated:
            diagnostic["bodyTruncated"] = True
        return diagnostic


class OpenAICompatibleProviderError(httpx.HTTPStatusError, ProviderDiagnosticError):
    """HTTP status failure with a sanitized provider diagnostic."""

    def __init__(self, diagnostic: ProviderErrorDiagnostic, *, request: httpx.Request) -> None:
        self.diagnostic = diagnostic
        response = httpx.Response(diagnostic.status, request=request)
        super().__init__(
            f"model provider returned a sanitized error (status {diagnostic.status})",
            request=request,
            response=response,
        )


class OpenAICompatibleModelProvider:
    """OpenAI-compatible HTTP edge behind the provider-neutral model port."""

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        *,
        http_policy: HttpTaskPolicy | None = None,
        image_resolver: ImageArtifactResolver | None = None,
    ) -> None:
        self._client = client
        self._http_policy = http_policy or HttpTaskPolicy()
        self._image_resolver = image_resolver

    async def invoke(
        self,
        request: ModelProviderRequest,
        access: ModelProviderAccess,
    ) -> ModelProviderResponse:
        credential = _credential_from_access(access)
        endpoint = request.endpoint
        if endpoint is None:
            raise ValueError("OpenAI-compatible model provider requires an endpoint")
        validate_http_destination(
            endpoint,
            self._http_policy,
            resolve_dns=self._client is None,
        )

        async def post(active_client: httpx.AsyncClient) -> ModelProviderResponse:
            payload = await self._prepare_payload(request)
            payload = _apply_openrouter_provider_routing(endpoint, payload)
            response = await active_client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {credential.get_secret_value()}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=request.timeout_seconds,
            )
            if not 200 <= response.status_code < 300:
                _raise_http_error(response, credential.get_secret_value(), self._http_policy)
            if len(response.content) > self._http_policy.maximum_response_bytes:
                raise ValueError("model response exceeds the configured payload limit")
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError("model provider response must be a JSON object")
            _raise_provider_error_envelope(
                payload,
                response,
                secrets=(credential.get_secret_value(),),
            )
            continuation = _extract_continuation(payload)
            return ModelProviderResponse(
                payload=_without_private_reasoning(payload),
                continuation=continuation,
            )

        if self._client is not None:
            return await post(self._client)
        async with outbound_http_client(
            endpoint,
            http_proxy_url=self._http_policy.http_proxy_url,
            https_proxy_url=self._http_policy.https_proxy_url,
            no_proxy=self._http_policy.no_proxy,
            ca_file=self._http_policy.ca_file,
            client_certificate_file=self._http_policy.client_certificate_file,
            client_key_file=self._http_policy.client_key_file,
        ) as active_client:
            return await post(active_client)

    async def stream(
        self,
        request: ModelProviderRequest,
        access: ModelProviderAccess,
    ) -> AsyncIterator[ModelProviderStreamEvent]:
        """Stream safe status/progress events and one assembled terminal response.

        OpenAI-compatible SSE chunks are never forwarded as public state. Private reasoning emits
        status-only lifecycle deltas while its content remains private continuation material.
        Only fields explicitly named ``public_summary`` by the provider can become public text.
        """

        credential = _credential_from_access(access)
        endpoint = request.endpoint
        if endpoint is None:
            raise ValueError("OpenAI-compatible model provider requires an endpoint")
        validate_http_destination(
            endpoint,
            self._http_policy,
            resolve_dns=self._client is None,
        )

        async def consume(
            active_client: httpx.AsyncClient,
        ) -> AsyncIterator[ModelProviderStreamEvent]:
            payload = await self._prepare_payload(request)
            payload = _apply_openrouter_provider_routing(endpoint, payload)
            payload["stream"] = True
            payload.setdefault("stream_options", {"include_usage": True})
            headers = {
                "Authorization": f"Bearer {credential.get_secret_value()}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            }
            async with active_client.stream(
                "POST",
                endpoint,
                headers=headers,
                json=payload,
                timeout=request.timeout_seconds,
            ) as response:
                if not 200 <= response.status_code < 300:
                    await _raise_stream_http_error(
                        response,
                        credential.get_secret_value(),
                        self._http_policy,
                    )
                source_sequence = 1
                yield ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.MODEL,
                        status=AgentProgressStatus.STARTED,
                        activityId=f"model:{request.operation.lower()}",
                        sourceSequence=source_sequence,
                    )
                )
                source_sequence += 1
                assembled: dict[str, object] = {}
                tool_started: set[int] = set()
                active_summary_segment: UUID | None = None
                active_private_reasoning_segment: UUID | None = None
                received = False
                response_bytes = 0
                async for line in response.aiter_lines():
                    response_bytes += len(line.encode("utf-8")) + 1
                    if response_bytes > self._http_policy.maximum_response_bytes:
                        raise ValueError("model response exceeds the configured payload limit")
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if not data:
                        continue
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError("model provider stream contained invalid JSON") from exc
                    if not isinstance(chunk, dict):
                        raise RuntimeError("model provider stream event must be a JSON object")
                    received = True
                    _raise_provider_error_envelope(
                        chunk,
                        response,
                        secrets=(credential.get_secret_value(),),
                    )
                    _merge_stream_chunk(assembled, chunk)
                    accounting_payload = _stream_accounting_payload(chunk)
                    if accounting_payload is not None:
                        yield ModelProviderStreamEvent.accounting_event(accounting_payload)
                    choice = _first_stream_choice(chunk)
                    delta = choice.get("delta") if choice is not None else None
                    if not isinstance(delta, dict):
                        delta = choice.get("message") if choice is not None else None
                    if not isinstance(delta, dict):
                        continue
                    public_summary = _public_summary(delta)
                    if public_summary is not None:
                        if active_private_reasoning_segment is not None:
                            yield ModelProviderStreamEvent.progress_event(
                                ModelProviderProgressDelta(
                                    activity=AgentProgressActivity.THINKING,
                                    status=AgentProgressStatus.COMPLETED,
                                    activityId="model:private-reasoning",
                                    segmentId=active_private_reasoning_segment,
                                    sourceSequence=source_sequence,
                                )
                            )
                            source_sequence += 1
                            active_private_reasoning_segment = None
                        summary_status = AgentProgressStatus.DELTA
                        if active_summary_segment is None:
                            active_summary_segment = uuid4()
                            summary_status = AgentProgressStatus.STARTED
                        yield ModelProviderStreamEvent.progress_event(
                            ModelProviderProgressDelta(
                                activity=AgentProgressActivity.THINKING,
                                status=summary_status,
                                activityId="model:public-summary",
                                segmentId=active_summary_segment,
                                sourceSequence=source_sequence,
                                detail=AgentPublicSummaryDetail(text=public_summary),
                            )
                        )
                        source_sequence += 1
                    if _has_private_reasoning_chunk(delta):
                        if active_summary_segment is not None:
                            yield ModelProviderStreamEvent.progress_event(
                                ModelProviderProgressDelta(
                                    activity=AgentProgressActivity.THINKING,
                                    status=AgentProgressStatus.COMPLETED,
                                    activityId="model:public-summary",
                                    segmentId=active_summary_segment,
                                    sourceSequence=source_sequence,
                                )
                            )
                            source_sequence += 1
                            active_summary_segment = None
                        reasoning_status = AgentProgressStatus.DELTA
                        if active_private_reasoning_segment is None:
                            active_private_reasoning_segment = uuid4()
                            reasoning_status = AgentProgressStatus.STARTED
                        yield ModelProviderStreamEvent.progress_event(
                            ModelProviderProgressDelta(
                                activity=AgentProgressActivity.THINKING,
                                status=reasoning_status,
                                activityId="model:private-reasoning",
                                segmentId=active_private_reasoning_segment,
                                sourceSequence=source_sequence,
                            )
                        )
                        source_sequence += 1
                    raw_tools = delta.get("tool_calls")
                    visible_model_work = (
                        isinstance(delta.get("content"), str) and bool(delta["content"])
                    ) or (isinstance(raw_tools, list) and bool(raw_tools))
                    if visible_model_work and active_summary_segment is not None:
                        yield ModelProviderStreamEvent.progress_event(
                            ModelProviderProgressDelta(
                                activity=AgentProgressActivity.THINKING,
                                status=AgentProgressStatus.COMPLETED,
                                activityId="model:public-summary",
                                segmentId=active_summary_segment,
                                sourceSequence=source_sequence,
                            )
                        )
                        source_sequence += 1
                        active_summary_segment = None
                    if visible_model_work and active_private_reasoning_segment is not None:
                        yield ModelProviderStreamEvent.progress_event(
                            ModelProviderProgressDelta(
                                activity=AgentProgressActivity.THINKING,
                                status=AgentProgressStatus.COMPLETED,
                                activityId="model:private-reasoning",
                                segmentId=active_private_reasoning_segment,
                                sourceSequence=source_sequence,
                            )
                        )
                        source_sequence += 1
                        active_private_reasoning_segment = None
                    if isinstance(raw_tools, list):
                        for index, tool_call in enumerate(raw_tools):
                            if not isinstance(tool_call, dict):
                                continue
                            tool_index = tool_call.get("index", index)
                            if not isinstance(tool_index, int) or tool_index < 0:
                                raise RuntimeError("model tool-call index must be non-negative")
                            if tool_index in tool_started:
                                continue
                            tool_started.add(tool_index)
                            yield ModelProviderStreamEvent.progress_event(
                                ModelProviderProgressDelta(
                                    activity=AgentProgressActivity.TOOL,
                                    status=AgentProgressStatus.STARTED,
                                    activityId=f"provider-tool:{tool_index}",
                                    sourceSequence=source_sequence,
                                )
                            )
                            source_sequence += 1
                if not received:
                    raise RuntimeError("model provider stream contained no data")
                if active_summary_segment is not None:
                    yield ModelProviderStreamEvent.progress_event(
                        ModelProviderProgressDelta(
                            activity=AgentProgressActivity.THINKING,
                            status=AgentProgressStatus.COMPLETED,
                            activityId="model:public-summary",
                            segmentId=active_summary_segment,
                            sourceSequence=source_sequence,
                        )
                    )
                    source_sequence += 1
                if active_private_reasoning_segment is not None:
                    yield ModelProviderStreamEvent.progress_event(
                        ModelProviderProgressDelta(
                            activity=AgentProgressActivity.THINKING,
                            status=AgentProgressStatus.COMPLETED,
                            activityId="model:private-reasoning",
                            segmentId=active_private_reasoning_segment,
                            sourceSequence=source_sequence,
                        )
                    )
                    source_sequence += 1
                yield ModelProviderStreamEvent.progress_event(
                    ModelProviderProgressDelta(
                        activity=AgentProgressActivity.MODEL,
                        status=AgentProgressStatus.COMPLETED,
                        activityId=f"model:{request.operation.lower()}",
                        sourceSequence=source_sequence,
                    )
                )
                continuation = _extract_continuation(assembled)
                response_payload = _without_private_reasoning(assembled)
                yield ModelProviderStreamEvent.response_event(
                    ModelProviderResponse(
                        payload=response_payload,
                        continuation=continuation,
                    )
                )

        if self._client is not None:
            async for event in consume(self._client):
                yield event
            return
        async with outbound_http_client(
            endpoint,
            http_proxy_url=self._http_policy.http_proxy_url,
            https_proxy_url=self._http_policy.https_proxy_url,
            no_proxy=self._http_policy.no_proxy,
            ca_file=self._http_policy.ca_file,
            client_certificate_file=self._http_policy.client_certificate_file,
            client_key_file=self._http_policy.client_key_file,
        ) as active_client:
            async for event in consume(active_client):
                yield event

    async def _prepare_payload(self, request: ModelProviderRequest) -> dict[str, object]:
        payload = _apply_continuation_bindings(request.payload, request.continuation_bindings)
        payload = _apply_continuation(payload, request.continuation)
        return await _resolve_image_parts(
            payload,
            resolver=self._image_resolver,
            tenant_id=request.tenant_id,
        )


def _credential_from_access(access: ModelProviderAccess | SecretStr) -> SecretStr:
    if isinstance(access, SecretStr):
        return access
    if access.credential is None:
        raise ValueError("OpenAI-compatible model provider requires a credential access")
    return access.credential


def _raise_provider_error_envelope(
    payload: dict[str, object],
    response: httpx.Response,
    *,
    secrets: tuple[str, ...] = (),
) -> None:
    error = payload.get("error")
    if not isinstance(error, dict):
        return
    raw_code = error.get("code")
    status_code = _status_code(raw_code) or (
        response.status_code if 400 <= response.status_code <= 599 else 502
    )
    diagnostic = _diagnostic_from_error(
        status_code,
        error,
        secrets=secrets,
    )
    raise OpenAICompatibleProviderError(diagnostic, request=response.request)


def _status_code(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) or (isinstance(value, str) and value.isdecimal()):
        status = int(value)
        return status if 400 <= status <= 599 else None
    return None


def _bounded_text(value: object, secrets: tuple[str, ...]) -> str | None:
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return None
    text = " ".join(str(value).split())
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text[:_MAX_PROVIDER_DIAGNOSTIC_CHARS] or None


def _diagnostic_from_error(
    status: int,
    error: dict[str, object],
    *,
    secrets: tuple[str, ...],
    body_truncated: bool = False,
) -> ProviderErrorDiagnostic:
    return ProviderErrorDiagnostic(
        status=status,
        type=_bounded_text(error.get("type"), secrets) or "provider_error",
        code=_bounded_text(error.get("code"), secrets),
        message=_bounded_text(error.get("message"), secrets)
        or "provider returned an error response",
        body_truncated=body_truncated,
    )


def _diagnostic_from_body(
    status: int,
    body: bytes,
    *,
    maximum_bytes: int,
    secrets: tuple[str, ...],
    truncated: bool = False,
) -> ProviderErrorDiagnostic:
    body_truncated = truncated or len(body) > maximum_bytes
    if body_truncated:
        return ProviderErrorDiagnostic(
            status=status,
            type="provider_error",
            code=None,
            message="provider error response exceeded the configured payload limit",
            body_truncated=True,
        )
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = None
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        return _diagnostic_from_error(
            status,
            payload["error"],
            secrets=secrets,
        )
    return ProviderErrorDiagnostic(
        status=status,
        type="provider_error",
        code=None,
        message="provider returned a non-JSON error response",
    )


def _raise_http_error(
    response: httpx.Response,
    secret: str,
    policy: HttpTaskPolicy,
) -> None:
    diagnostic = _diagnostic_from_body(
        response.status_code,
        response.content,
        maximum_bytes=policy.maximum_response_bytes,
        secrets=(secret,),
    )
    raise OpenAICompatibleProviderError(diagnostic, request=response.request)


async def _read_bounded_error_body(
    response: httpx.Response,
    maximum_bytes: int,
) -> tuple[bytes, bool]:
    chunks: list[bytes] = []
    total = 0
    truncated = False
    async for chunk in response.aiter_bytes():
        remaining = maximum_bytes + 1 - total
        if remaining > 0:
            chunks.append(chunk[:remaining])
            total += min(len(chunk), remaining)
        if len(chunk) > remaining:
            truncated = True
            break
    return b"".join(chunks), truncated


async def _raise_stream_http_error(
    response: httpx.Response,
    secret: str,
    policy: HttpTaskPolicy,
) -> None:
    body, truncated = await _read_bounded_error_body(
        response,
        policy.maximum_response_bytes,
    )
    diagnostic = _diagnostic_from_body(
        response.status_code,
        body,
        maximum_bytes=policy.maximum_response_bytes,
        secrets=(secret,),
        truncated=truncated,
    )
    raise OpenAICompatibleProviderError(diagnostic, request=response.request)


async def _resolve_image_parts(
    payload: dict[str, object],
    *,
    resolver: ImageArtifactResolver | None,
    tenant_id: str | None,
) -> dict[str, object]:
    """Turn governed image refs into transient provider content immediately before I/O."""

    copied = copy.deepcopy(payload)
    messages = copied.get("messages")
    if not isinstance(messages, list):
        return copied
    for message in messages:
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for index, part in enumerate(content):
            if not isinstance(part, dict) or part.get("type") != "image_ref":
                continue
            if resolver is None or tenant_id is None:
                raise ValueError("image input requires a tenant-scoped image resolver")
            raw_image = part.get("image")
            if not isinstance(raw_image, dict):
                raise ValueError("image_ref content part is malformed")
            image = ImageArtifactRef.model_validate(raw_image)
            content_bytes = await resolver.resolve_image(image, tenant_id=tenant_id)
            if not isinstance(content_bytes, bytes):
                raise ValueError("image resolver must return bytes")
            inspection = inspect_image_bytes(
                content_bytes,
                declared_media_type=image.artifact.media_type,
            )
            build_image_artifact_ref(
                image.artifact,
                inspection,
                filename=image.display.filename,
                alt_text=image.display.alt_text,
            )
            content[index] = {
                "type": "image_url",
                "image_url": {
                    "url": (
                        f"data:{inspection.media_type};base64,"
                        f"{base64.b64encode(content_bytes).decode('ascii')}"
                    )
                },
            }
    return copied


def _first_stream_choice(payload: dict[str, object]) -> dict[str, object] | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return None
    return choices[0]


def _public_summary(delta: dict[str, object]) -> str | None:
    """Read only an explicitly provider-authorized public summary field."""

    value = delta.get("public_summary", delta.get("publicSummary"))
    if not isinstance(value, str) or not value.strip():
        return None
    return value[:4096]


def _has_private_reasoning_chunk(delta: dict[str, object]) -> bool:
    if any(
        isinstance(delta.get(key), str) and bool(delta[key])
        for key in ("reasoning_content", "reasoning")
    ):
        return True
    details = delta.get("reasoning_details")
    return isinstance(details, list) and bool(details)


def _merge_stream_chunk(assembled: dict[str, object], chunk: dict[str, object]) -> None:
    """Assemble OpenAI chat SSE deltas without retaining private reasoning fields."""

    for key in ("id", "object", "created", "model", "system_fingerprint"):
        if key in chunk:
            assembled[key] = chunk[key]
    choices = chunk.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        if "usage" in chunk:
            assembled["usage"] = chunk["usage"]
        return
    choice = choices[0]
    existing_choices = assembled.setdefault(
        "choices",
        [{"index": 0, "message": {"role": "assistant", "content": ""}}],
    )
    if not isinstance(existing_choices, list) or not existing_choices:
        return
    target = existing_choices[0]
    if not isinstance(target, dict):
        return
    if "finish_reason" in choice:
        target["finish_reason"] = choice["finish_reason"]
    delta = choice.get("delta")
    if not isinstance(delta, dict):
        delta = choice.get("message")
    if not isinstance(delta, dict):
        return
    message = target.setdefault("message", {"role": "assistant", "content": ""})
    if not isinstance(message, dict):
        return
    if isinstance(delta.get("role"), str):
        message["role"] = delta["role"]
    if isinstance(delta.get("content"), str):
        message["content"] = str(message.get("content") or "") + delta["content"]
    _merge_private_reasoning(message, delta)
    _merge_tool_calls(message, delta.get("tool_calls"))
    if "usage" in chunk:
        assembled["usage"] = chunk["usage"]


def _stream_accounting_payload(chunk: dict[str, object]) -> dict[str, Any] | None:
    usage = chunk.get("usage")
    if not isinstance(usage, dict):
        return None
    payload: dict[str, Any] = {"usage": copy.deepcopy(usage)}
    for key in ("cost", "costUsd", "cache_discount", "cacheDiscount"):
        if key in chunk:
            payload[key] = copy.deepcopy(chunk[key])
    return payload


def _merge_private_reasoning(message: dict[str, object], delta: dict[str, object]) -> None:
    """Retain provider continuation material only long enough to protect it at the boundary."""

    for key in ("reasoning_content", "reasoning"):
        value = delta.get(key)
        if isinstance(value, str):
            message[key] = str(message.get(key) or "") + value
    details = delta.get("reasoning_details")
    if isinstance(details, list):
        prior = message.setdefault("reasoning_details", [])
        if isinstance(prior, list):
            prior.extend(copy.deepcopy(details))


def _merge_tool_calls(message: dict[str, object], raw_calls: object) -> None:
    if not isinstance(raw_calls, list):
        return
    calls = message.setdefault("tool_calls", [])
    if not isinstance(calls, list):
        return
    for index, raw_call in enumerate(raw_calls):
        if not isinstance(raw_call, dict):
            continue
        call_index = raw_call.get("index", index)
        if not isinstance(call_index, int) or call_index < 0:
            raise RuntimeError("model tool-call index must be non-negative")
        while len(calls) <= call_index:
            calls.append({"index": len(calls), "function": {"arguments": ""}})
        call = calls[call_index]
        if not isinstance(call, dict):
            continue
        for key in ("id", "type", "index"):
            if key in raw_call:
                call[key] = raw_call[key]
        function = raw_call.get("function")
        if not isinstance(function, dict):
            continue
        target_function = call.setdefault("function", {})
        if not isinstance(target_function, dict):
            continue
        for key in ("name",):
            if isinstance(function.get(key), str):
                target_function[key] = function[key]
        if isinstance(function.get("arguments"), str):
            target_function["arguments"] = (
                str(target_function.get("arguments") or "") + function["arguments"]
            )


def _apply_openrouter_provider_routing(
    endpoint: str, payload: dict[str, object]
) -> dict[str, object]:
    """Require an OpenRouter provider that supports structured-output parameters."""

    if urlsplit(endpoint).hostname != "openrouter.ai" or "response_format" not in payload:
        return payload
    provider = payload.get("provider")
    if provider is not None and not isinstance(provider, dict):
        raise ValueError("OpenRouter provider options must be an object")
    routed = copy.deepcopy(payload)
    provider_options = dict(provider) if provider is not None else {}
    provider_options["require_parameters"] = True
    routed["provider"] = provider_options
    return routed


def _apply_continuation(
    payload: dict[str, object], continuation: SecretStr | None
) -> dict[str, object]:
    if continuation is None:
        return payload
    try:
        envelope = json.loads(continuation.get_secret_value())
    except json.JSONDecodeError as exc:
        raise ValueError("provider continuation is not a valid adapter envelope") from exc
    if not isinstance(envelope, dict) or envelope.get("kind") not in {
        "reasoning_details",
        "reasoning",
        "reasoning_content",
    }:
        raise ValueError("provider continuation has an unsupported adapter envelope")
    copied = copy.deepcopy(payload)
    messages = copied.get("messages")
    if not isinstance(messages, list):
        raise ValueError("reasoning continuation requires chat messages")
    assistant = next(
        (
            message
            for message in reversed(messages)
            if isinstance(message, dict) and message.get("role") == "assistant"
        ),
        None,
    )
    if assistant is None:
        raise ValueError("reasoning continuation requires a prior assistant message")
    assistant[str(envelope["kind"])] = envelope.get("value")
    return copied


def _apply_continuation_bindings(
    payload: dict[str, object],
    bindings: tuple[ModelProviderContinuationBinding, ...],
) -> dict[str, object]:
    if not bindings:
        return payload
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise ValueError("indexed reasoning continuation requires chat messages")
    copied = copy.deepcopy(payload)
    copied_messages = copied.get("messages")
    if not isinstance(copied_messages, list):
        raise ValueError("indexed reasoning continuation requires chat messages")
    seen_indexes: set[int] = set()
    for binding in bindings:
        message_index = binding.message_index
        if message_index in seen_indexes:
            raise ValueError("indexed reasoning continuations must target unique messages")
        seen_indexes.add(message_index)
        if message_index >= len(copied_messages):
            raise ValueError("indexed reasoning continuation message index is out of range")
        message = copied_messages[message_index]
        if not isinstance(message, dict) or message.get("role") != "assistant":
            raise ValueError("indexed reasoning continuation requires assistant messages")
        kind, value = _decode_continuation_envelope(binding.token)
        message[kind] = value
    return copied


def _decode_continuation_envelope(token: SecretStr) -> tuple[str, object]:
    try:
        envelope = json.loads(token.get_secret_value())
    except json.JSONDecodeError as exc:
        raise ValueError("provider continuation is not a valid adapter envelope") from exc
    if not isinstance(envelope, dict) or envelope.get("kind") not in {
        "reasoning_details",
        "reasoning",
        "reasoning_content",
    }:
        raise ValueError("provider continuation has an unsupported adapter envelope")
    return str(envelope["kind"]), envelope.get("value")


def _extract_continuation(payload: dict[str, object]) -> SecretStr | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return None
    message = choices[0].get("message")
    if not isinstance(message, dict):
        return None
    for key in ("reasoning_details", "reasoning_content", "reasoning"):
        value = message.get(key)
        if (key == "reasoning_details" and isinstance(value, list) and value) or (
            key != "reasoning_details" and isinstance(value, str) and value
        ):
            return SecretStr(
                json.dumps(
                    {"kind": key, "value": value},
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
    return None


def _without_private_reasoning(payload: dict[str, object]) -> dict[str, object]:
    sanitized = copy.deepcopy(payload)
    choices = sanitized.get("choices")
    if not isinstance(choices, list):
        return sanitized
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message")
        if not isinstance(message, dict):
            continue
        for key in ("reasoning_details", "reasoning_content", "reasoning"):
            message.pop(key, None)
    return sanitized
