from __future__ import annotations

import copy
import json
from urllib.parse import urlsplit

import httpx
from pydantic import SecretStr

from amesh.networking import outbound_http_client
from amesh.ports.agent_primitives import (
    ModelProviderRequest,
    ModelProviderResponse,
)
from amesh.tasks.http import HttpTaskPolicy, validate_http_destination


class OpenAICompatibleModelProvider:
    """OpenAI-compatible HTTP edge behind the provider-neutral model port."""

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        *,
        http_policy: HttpTaskPolicy | None = None,
    ) -> None:
        self._client = client
        self._http_policy = http_policy or HttpTaskPolicy()

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        validate_http_destination(
            request.endpoint,
            self._http_policy,
            resolve_dns=self._client is None,
        )

        async def post(active_client: httpx.AsyncClient) -> ModelProviderResponse:
            payload = _apply_continuation(request.payload, request.continuation)
            payload = _apply_openrouter_provider_routing(request.endpoint, payload)
            response = await active_client.post(
                request.endpoint,
                headers={
                    "Authorization": f"Bearer {credential.get_secret_value()}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=request.timeout_seconds,
            )
            response.raise_for_status()
            if len(response.content) > self._http_policy.maximum_response_bytes:
                raise ValueError("model response exceeds the configured payload limit")
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError("model provider response must be a JSON object")
            _raise_provider_error_envelope(payload, response)
            continuation = _extract_continuation(payload)
            return ModelProviderResponse(
                payload=_without_private_reasoning(payload),
                continuation=continuation,
            )

        if self._client is not None:
            return await post(self._client)
        async with outbound_http_client(
            request.endpoint,
            http_proxy_url=self._http_policy.http_proxy_url,
            https_proxy_url=self._http_policy.https_proxy_url,
            no_proxy=self._http_policy.no_proxy,
            ca_file=self._http_policy.ca_file,
            client_certificate_file=self._http_policy.client_certificate_file,
            client_key_file=self._http_policy.client_key_file,
        ) as active_client:
            return await post(active_client)


def _raise_provider_error_envelope(
    payload: dict[str, object], response: httpx.Response
) -> None:
    error = payload.get("error")
    if not isinstance(error, dict):
        return
    raw_code = error.get("code")
    if isinstance(raw_code, bool):
        return
    if isinstance(raw_code, int):
        status_code = raw_code
    elif isinstance(raw_code, str) and raw_code.isdecimal():
        status_code = int(raw_code)
    else:
        return
    if not 400 <= status_code <= 599:
        return
    error_response = httpx.Response(status_code, request=response.request)
    raise httpx.HTTPStatusError(
        f"model provider returned an error envelope (status {status_code})",
        request=response.request,
        response=error_response,
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
