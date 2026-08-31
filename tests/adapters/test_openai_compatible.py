from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from datetime import UTC, datetime
from io import BytesIO
from typing import Any

import httpx
import pytest
from PIL import Image
from pydantic import SecretStr

from amesh.domain.artifacts import ArtifactProvenance, ArtifactRetention, build_artifact_reference
from amesh.domain.image_inputs import ImageArtifactRef, ImageDisplayMetadata
from amesh.ports import ModelProviderRequest
from amesh.tasks.http import HttpTaskPolicy


def test_openrouter_structured_requests_require_compatible_provider() -> None:
    posted: list[dict[str, Any]] = []

    async def respond(request: httpx.Request) -> httpx.Response:
        posted.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"answer": 1}'}}],
                "usage": {"total_tokens": 1},
            },
        )

    async def scenario() -> None:
        from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client, http_policy=HttpTaskPolicy())
            structured_payload = {
                "model": "fixture/model",
                "messages": [{"role": "user", "content": "Return JSON"}],
                "response_format": {"type": "json_schema"},
                "provider": {"order": ["provider-a"]},
            }
            await adapter.invoke(
                ModelProviderRequest(
                    operation="STRUCTURED",
                    endpoint="https://openrouter.ai/api/v1/chat/completions",
                    model="fixture/model",
                    payload=structured_payload,
                    timeoutSeconds=5,
                ),
                SecretStr("credential"),
            )
            await adapter.invoke(
                ModelProviderRequest(
                    operation="CHAT",
                    endpoint="https://provider.example.test/v1/chat",
                    model="fixture/model",
                    payload={
                        "model": "fixture/model",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "response_format": {"type": "json_schema"},
                    },
                    timeoutSeconds=5,
                ),
                SecretStr("credential"),
            )
            assert structured_payload["provider"] == {"order": ["provider-a"]}

    asyncio.run(scenario())
    assert posted[0]["provider"] == {
        "order": ["provider-a"],
        "require_parameters": True,
    }
    assert "provider" not in posted[1]


@pytest.mark.parametrize("code", [429, 502, 401])
def test_provider_error_envelope_raises_credential_safe_status_error(code: int) -> None:
    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "error": {
                    "message": "upstream diagnostic credential-secret",
                    "code": code,
                }
            },
        )

    async def scenario() -> None:
        from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client, http_policy=HttpTaskPolicy())
            with pytest.raises(httpx.HTTPStatusError) as caught:
                await adapter.invoke(
                    ModelProviderRequest(
                        operation="CHAT",
                        endpoint="https://provider.example.test/v1/chat",
                        model="fixture/model",
                        payload={"messages": [{"role": "user", "content": "Hello"}]},
                        timeoutSeconds=5,
                    ),
                    SecretStr("credential-secret"),
                )
            assert caught.value.response.status_code == code
            assert "credential-secret" not in str(caught.value)
            assert "upstream diagnostic" not in str(caught.value)
            assert caught.value.diagnostic.as_dict() == {
                "status": code,
                "type": "provider_error",
                "code": str(code),
                "message": "upstream diagnostic [REDACTED]",
            }

    asyncio.run(scenario())


def test_actual_http_error_preserves_only_sanitized_provider_diagnostic() -> None:
    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "type": "invalid_request_error",
                    "code": "unsupported_field",
                    "message": "bad request credential-secret",
                    "param": "messages",
                }
            },
        )

    async def scenario() -> None:
        from amesh.adapters.openai_compatible import (
            OpenAICompatibleModelProvider,
            OpenAICompatibleProviderError,
        )

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client, http_policy=HttpTaskPolicy())
            with pytest.raises(OpenAICompatibleProviderError) as caught:
                await adapter.invoke(
                    ModelProviderRequest(
                        operation="CHAT",
                        endpoint="https://provider.example.test/v1/chat",
                        model="fixture/model",
                        payload={"messages": [{"role": "user", "content": "private prompt"}]},
                        timeoutSeconds=5,
                    ),
                    SecretStr("credential-secret"),
                )
            assert caught.value.response.status_code == 400
            assert caught.value.diagnostic.as_dict() == {
                "status": 400,
                "type": "invalid_request_error",
                "code": "unsupported_field",
                "message": "bad request [REDACTED]",
            }
            assert "private prompt" not in repr(caught.value.diagnostic)
            assert "credential-secret" not in repr(caught.value.diagnostic)

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("body", "truncated"),
    [
        (b"not-json", False),
        (b"x" * 128, True),
    ],
)
def test_plain_malformed_and_oversized_http_errors_have_bounded_fallback(
    body: bytes, truncated: bool
) -> None:
    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, content=body)

    async def scenario() -> None:
        from amesh.adapters.openai_compatible import (
            OpenAICompatibleModelProvider,
            OpenAICompatibleProviderError,
        )

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(
                client,
                http_policy=HttpTaskPolicy(maximum_response_bytes=64),
            )
            with pytest.raises(OpenAICompatibleProviderError) as caught:
                await adapter.invoke(
                    ModelProviderRequest(
                        operation="CHAT",
                        endpoint="https://provider.example.test/v1/chat",
                        model="fixture/model",
                        payload={"messages": [{"role": "user", "content": "Hello"}]},
                        timeoutSeconds=5,
                    ),
                    SecretStr("credential"),
                )
            diagnostic = caught.value.diagnostic
            assert diagnostic.status == 400
            assert diagnostic.type == "provider_error"
            assert diagnostic.code is None
            assert diagnostic.message == (
                "provider error response exceeded the configured payload limit"
                if truncated
                else "provider returned a non-JSON error response"
            )
            assert diagnostic.body_truncated is truncated

    asyncio.run(scenario())


def test_stream_http_error_uses_the_same_sanitized_diagnostic() -> None:
    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={
                "error": {
                    "type": "invalid_request_error",
                    "code": "bad_input",
                    "message": "invalid",
                }
            },
        )

    async def scenario() -> None:
        from amesh.adapters.openai_compatible import (
            OpenAICompatibleModelProvider,
            OpenAICompatibleProviderError,
        )

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client, http_policy=HttpTaskPolicy())
            with pytest.raises(OpenAICompatibleProviderError) as caught:
                async for _event in adapter.stream(
                    ModelProviderRequest(
                        operation="CHAT",
                        endpoint="https://provider.example.test/v1/chat",
                        model="fixture/model",
                        payload={"messages": [{"role": "user", "content": "Hello"}]},
                        timeoutSeconds=5,
                    ),
                    SecretStr("credential"),
                ):
                    pass
            assert caught.value.diagnostic.as_dict() == {
                "status": 422,
                "type": "invalid_request_error",
                "code": "bad_input",
                "message": "invalid",
            }

    asyncio.run(scenario())


class _ImageResolver:
    def __init__(self, content: bytes) -> None:
        self.content = content
        self.tenant_ids: list[str] = []

    async def resolve_image(self, image: ImageArtifactRef, *, tenant_id: str) -> bytes:
        self.tenant_ids.append(tenant_id)
        assert image.artifact.tenant_id == tenant_id
        return self.content


def _image_ref(content: bytes) -> ImageArtifactRef:
    digest = hashlib.sha256(content).hexdigest()
    artifact = {
        "reference": build_artifact_reference("input.png", 1, digest),
        "contentAddress": f"sha256:{digest}",
        "tenantId": "tenant-a",
        "namespace": "workspace",
        "path": "input.png",
        "version": 1,
        "mediaType": "image/png",
        "sizeBytes": len(content),
        "checksumSha256": digest,
        "provenance": ArtifactProvenance(
            source="namespace-file",
            originNamespace="workspace",
            createdBy="test",
            createdAt=datetime(2026, 8, 31, tzinfo=UTC),
        ),
        "retention": ArtifactRetention(),
    }
    return ImageArtifactRef(
        artifact=artifact,
        display=ImageDisplayMetadata(widthPixels=2, heightPixels=2),
    )


def test_openai_compatible_resolves_governed_images_only_at_provider_boundary() -> None:
    image_stream = BytesIO()
    Image.new("RGB", (2, 2), color=(1, 2, 3)).save(image_stream, format="PNG")
    content = image_stream.getvalue()
    resolver = _ImageResolver(content)
    posted: list[dict[str, object]] = []

    async def respond(request: httpx.Request) -> httpx.Response:
        posted.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "ok"}}], "usage": {"total_tokens": 1}},
        )

    async def scenario() -> None:
        from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client, image_resolver=resolver)
            await adapter.invoke(
                ModelProviderRequest(
                    operation="CHAT",
                    endpoint="https://provider.example.test/v1/chat",
                    model="fixture/model",
                    tenantId="tenant-a",
                    payload={
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "describe"},
                                    {
                                        "type": "image_ref",
                                        "image": _image_ref(content).model_dump(mode="json"),
                                    },
                                ],
                            }
                        ]
                    },
                    timeoutSeconds=5,
                ),
                SecretStr("credential"),
            )

    asyncio.run(scenario())
    assert resolver.tenant_ids == ["tenant-a"]
    image_part = posted[0]["messages"][0]["content"][1]
    assert image_part["type"] == "image_url"
    encoded = image_part["image_url"]["url"].split(",", 1)[1]
    assert base64.b64decode(encoded) == content


def test_openai_compatible_stream_emits_ordered_safe_progress_and_assembled_response() -> None:
    chunks = [
        {"id": "stream-1", "model": "fixture/model", "choices": [{"delta": {"role": "assistant"}}]},
        {"choices": [{"delta": {"public_summary": "checking the input"}}]},
        {
            "choices": [
                {
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call-1",
                                "type": "function",
                                "function": {"name": "lookup", "arguments": '{"q":'},
                            }
                        ]
                    }
                }
            ]
        },
        {"choices": [{"delta": {"public_summary": "checking the result"}}]},
        {"choices": [{"delta": {"reasoning_content": "private thought"}}]},
        {
            "choices": [
                {
                    "delta": {
                        "content": "done",
                        "tool_calls": [{"index": 0, "function": {"arguments": '"value"}'}}],
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 2,
                "total_tokens": 12,
                "cost": 0.01,
                "prompt_tokens_details": {"cached_tokens": 8},
            },
        },
    ]

    async def respond(request: httpx.Request) -> httpx.Response:
        posted = json.loads(request.content)
        assert posted["stream"] is True
        assert posted["stream_options"] == {"include_usage": True}
        body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=body + "data: [DONE]\n\n",
        )

    async def scenario() -> list[object]:
        from amesh.adapters.openai_compatible import OpenAICompatibleModelProvider

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            adapter = OpenAICompatibleModelProvider(client)
            return [
                event
                async for event in adapter.stream(
                    ModelProviderRequest(
                        operation="CHAT",
                        endpoint="https://provider.example.test/v1/chat",
                        model="fixture/model",
                        payload={"messages": [{"role": "user", "content": "hello"}]},
                        timeoutSeconds=5,
                    ),
                    SecretStr("credential"),
                )
            ]

    events = asyncio.run(scenario())
    assert [event.kind for event in events] == [
        "progress",
        "progress",
        "progress",
        "progress",
        "progress",
        "progress",
        "progress",
        "response",
    ]
    progress = [event.progress for event in events if event.progress is not None]
    assert [event.source_sequence for event in progress] == list(range(1, 8))
    assert [event.activity.value for event in progress] == [
        "MODEL",
        "THINKING",
        "THINKING",
        "TOOL",
        "THINKING",
        "THINKING",
        "MODEL",
    ]
    assert progress[1].segment_id == progress[2].segment_id
    assert progress[4].segment_id == progress[5].segment_id
    assert progress[1].segment_id != progress[4].segment_id
    assert progress[1].detail is not None
    assert "private thought" not in json.dumps(events[-1].response.payload)
    assert events[-1].response.continuation is not None
    assert events[-1].response.payload["choices"][0]["message"]["content"] == "done"
    assert (
        events[-1].response.payload["choices"][0]["message"]["tool_calls"][0]["function"][
            "arguments"
        ]
        == '{"q":"value"}'
    )
    assert events[-1].response.payload["usage"] == {
        "prompt_tokens": 10,
        "completion_tokens": 2,
        "total_tokens": 12,
        "cost": 0.01,
        "prompt_tokens_details": {"cached_tokens": 8},
    }
