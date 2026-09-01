from __future__ import annotations

import asyncio
import base64
import json
from typing import Any
from uuid import uuid4

import pytest

import amesh.adapters.openai_session as openai_session
from amesh.adapters.openai_session import (
    CanonicalSessionRequest,
    CanonicalSessionResult,
    HarnessProvenance,
    OpenAIChatCompletionRequest,
    OpenAICompatibleSessionAdapter,
    OpenAIResponseRequest,
    from_canonical_response_result,
    from_canonical_session_result,
    openai_response_sse_events,
    openai_sse_events,
    to_canonical_response_request,
    to_canonical_session_request,
)


def _image_data_url(media_type: str, content: bytes) -> str:
    return f"data:{media_type};base64,{base64.b64encode(content).decode('ascii')}"


class _Facade:
    def __init__(self) -> None:
        self.calls: list[tuple[CanonicalSessionRequest, dict[str, str | None]]] = []

    async def complete(
        self,
        request: CanonicalSessionRequest,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
        idempotency_key: str | None,
    ) -> CanonicalSessionResult:
        self.calls.append(
            (
                request,
                {
                    "tenant_id": tenant_id,
                    "namespace": namespace,
                    "actor_id": actor_id,
                    "idempotency_key": idempotency_key,
                },
            )
        )
        return CanonicalSessionResult(
            sessionId=uuid4(),
            profile=request.profile,
            content={"answer": "ok"},
            usage={"inputTokens": 2, "outputTokens": 3},
            harness=HarnessProvenance(adapter="fixture", adapterVersion="1"),
        )


def test_request_translation_is_harness_neutral_and_preserves_messages() -> None:
    request = OpenAIChatCompletionRequest(
        model="fixture-model",
        messages=({"role": "user", "content": "hello"},),
        temperature=0.2,
        top_p=0.8,
        max_completion_tokens=32,
        response_format={"type": "json_object"},
    )

    canonical = to_canonical_session_request(request)

    assert canonical.profile == "fixture-model"
    assert canonical.messages == request.messages
    assert canonical.parameters == {
        "temperature": 0.2,
        "topP": 0.8,
        "maxCompletionTokens": 32,
        "responseFormat": {"type": "json_object"},
    }
    assert "harness" not in canonical.model_dump()
    with pytest.raises(ValueError):
        OpenAIChatCompletionRequest.model_validate(
            {
                "model": "fixture-model",
                "messages": [{"role": "user", "content": "hello"}],
                "harness": "pi",
            }
        )


def test_chat_multimodal_translation_preserves_part_order_and_extracts_uploads() -> None:
    first_bytes = b"first-png-bytes"
    second_bytes = b"second-jpeg-bytes"
    first_url = _image_data_url("image/png", first_bytes)
    second_url = _image_data_url("image/jpeg", second_bytes)
    request = OpenAIChatCompletionRequest.model_validate(
        {
            "model": "fixture-model",
            "messages": [
                {"role": "system", "content": "Use the supplied evidence."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "before"},
                        {"type": "image_url", "image_url": {"url": first_url}},
                        {"type": "text", "text": "between"},
                        {"type": "image_url", "image_url": {"url": second_url}},
                    ],
                },
            ],
        }
    )

    canonical = to_canonical_session_request(request)

    assert canonical.messages == (
        {"role": "system", "content": "Use the supplied evidence."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "before"},
                {"type": "inline_image_upload", "uploadId": "inline-image-0000"},
                {"type": "text", "text": "between"},
                {"type": "inline_image_upload", "uploadId": "inline-image-0001"},
            ],
        },
    )
    assert [upload.upload_id for upload in canonical.inline_images] == [
        "inline-image-0000",
        "inline-image-0001",
    ]
    assert [upload.media_type for upload in canonical.inline_images] == [
        "image/png",
        "image/jpeg",
    ]
    assert [upload.content for upload in canonical.inline_images] == [first_bytes, second_bytes]
    serialized_messages = json.dumps(canonical.messages)
    assert "data:" not in serialized_messages
    assert base64.b64encode(first_bytes).decode("ascii") not in serialized_messages
    assert base64.b64encode(second_bytes).decode("ascii") not in serialized_messages


def test_chat_messages_reject_tool_calls_blank_content_and_non_user_images() -> None:
    base = {"model": "fixture-model", "messages": [{"role": "user", "content": "hello"}]}
    with pytest.raises(ValueError, match="unsupported fields"):
        OpenAIChatCompletionRequest.model_validate(
            {
                **base,
                "messages": [{"role": "assistant", "content": "hello", "tool_calls": []}],
            }
        )
    with pytest.raises(ValueError, match="non-blank"):
        OpenAIChatCompletionRequest.model_validate(
            {**base, "messages": [{"role": "user", "content": "  "}]}
        )
    with pytest.raises(ValueError, match="only user messages"):
        OpenAIChatCompletionRequest.model_validate(
            {
                **base,
                "messages": [
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": _image_data_url("image/png", b"image")},
                            }
                        ],
                    }
                ],
            }
        )


def test_adapter_forwards_tenant_and_idempotency_to_the_canonical_facade() -> None:
    async def scenario() -> None:
        facade = _Facade()
        adapter = OpenAICompatibleSessionAdapter(facade)
        response = await adapter.create_chat_completion(
            OpenAIChatCompletionRequest(
                model="fixture-model",
                messages=({"role": "user", "content": "hello"},),
            ),
            tenant_id="tenant-a",
            namespace="default",
            actor_id="actor-a",
            idempotency_key="request-1",
        )
        assert response.object == "chat.completion"
        assert response.choices[0].message.content == '{"answer":"ok"}'
        assert response.usage is not None
        assert response.usage.total_tokens == 5
        assert facade.calls[0][1] == {
            "tenant_id": "tenant-a",
            "namespace": "default",
            "actor_id": "actor-a",
            "idempotency_key": "request-1",
        }

    asyncio.run(scenario())


def test_sse_translation_is_bounded_and_terminates_with_done() -> None:
    response = from_canonical_session_result(
        CanonicalSessionResult(
            sessionId=uuid4(),
            profile="fixture-model",
            content="abcdef",
            finishReason="stop",
            created=123,
        )
    )

    events = list(openai_sse_events(response, chunk_size=2))
    payloads: list[dict[str, Any]] = [
        json.loads(event.removeprefix("data: ").strip()) for event in events[:-1]
    ]

    assert len(events) == 6
    assert payloads[0]["choices"][0]["delta"] == {"role": "assistant"}
    assert [item["choices"][0]["delta"]["content"] for item in payloads[1:4]] == [
        "ab",
        "cd",
        "ef",
    ]
    assert payloads[4]["choices"][0]["finish_reason"] == "stop"
    assert events[-1] == "data: [DONE]\n\n"


def test_concurrent_requests_keep_tenant_and_session_calls_separate() -> None:
    async def scenario() -> None:
        facade = _Facade()
        adapter = OpenAICompatibleSessionAdapter(facade)

        await asyncio.gather(
            *(
                adapter.create_chat_completion(
                    OpenAIChatCompletionRequest(
                        model="fixture-model",
                        messages=({"role": "user", "content": str(index)},),
                    ),
                    tenant_id=f"tenant-{index}",
                    namespace="default",
                    actor_id=f"actor-{index}",
                    idempotency_key=f"request-{index}",
                )
                for index in range(32)
            )
        )

        assert len(facade.calls) == 32
        assert {call[1]["tenant_id"] for call in facade.calls} == {
            f"tenant-{index}" for index in range(32)
        }
        assert len({call[1]["idempotency_key"] for call in facade.calls}) == 32

    asyncio.run(scenario())


def test_responses_text_and_structured_output_translate_to_canonical_request() -> None:
    request = OpenAIResponseRequest.model_validate(
        {
            "model": "authorized-profile",
            "instructions": "Return a governed decision.",
            "input": "Assess the evidence.",
            "temperature": 0.1,
            "top_p": 0.9,
            "max_output_tokens": 128,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "decision",
                    "description": "A bounded decision.",
                    "schema": {
                        "type": "object",
                        "properties": {"decision": {"type": "string"}},
                        "required": ["decision"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            },
        }
    )

    canonical = to_canonical_response_request(request)

    assert canonical.profile == "authorized-profile"
    assert canonical.messages == (
        {"role": "developer", "content": "Return a governed decision."},
        {"role": "user", "content": "Assess the evidence."},
    )
    assert canonical.parameters == {
        "temperature": 0.1,
        "topP": 0.9,
        "maxCompletionTokens": 128,
        "responseFormat": {
            "type": "json_schema",
            "json_schema": {
                "name": "decision",
                "description": "A bounded decision.",
                "schema": {
                    "type": "object",
                    "properties": {"decision": {"type": "string"}},
                    "required": ["decision"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    }
    assert "harness" not in canonical.model_dump()


def test_responses_message_input_normalizes_supported_text_parts() -> None:
    request = OpenAIResponseRequest.model_validate(
        {
            "model": "authorized-profile",
            "input": [
                {"role": "system", "content": "System context."},
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "first "},
                        {"type": "input_text", "text": "second"},
                    ],
                },
            ],
            "text": {"format": {"type": "json_object"}},
        }
    )

    canonical = to_canonical_response_request(request)

    assert canonical.messages == (
        {"role": "system", "content": "System context."},
        {"role": "user", "content": "first second"},
    )
    assert canonical.parameters == {"responseFormat": {"type": "json_object"}}


def test_responses_multimodal_translation_preserves_order_and_extracts_upload() -> None:
    image_bytes = b"webp-image-bytes"
    data_url = _image_data_url("image/webp", image_bytes)
    request = OpenAIResponseRequest.model_validate(
        {
            "model": "authorized-profile",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "inspect "},
                        {"type": "input_image", "image_url": data_url},
                        {"type": "input_text", "text": " then answer"},
                    ],
                }
            ],
        }
    )

    canonical = to_canonical_response_request(request)

    assert canonical.messages == (
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "inspect "},
                {"type": "inline_image_upload", "uploadId": "inline-image-0000"},
                {"type": "text", "text": " then answer"},
            ],
        },
    )
    assert len(canonical.inline_images) == 1
    assert canonical.inline_images[0].media_type == "image/webp"
    assert canonical.inline_images[0].content == image_bytes
    serialized_messages = json.dumps(canonical.messages)
    assert data_url not in serialized_messages
    assert base64.b64encode(image_bytes).decode("ascii") not in serialized_messages


@pytest.mark.parametrize(
    "request_payload",
    [
        {
            "model": "fixture-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": "https://example.test/image.png"},
                        }
                    ],
                }
            ],
        },
        {
            "model": "fixture-model",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": "https://example.test/image.png",
                        }
                    ],
                }
            ],
        },
    ],
)
def test_openai_image_inputs_reject_remote_urls(request_payload: dict[str, Any]) -> None:
    request_type = (
        OpenAIChatCompletionRequest if "messages" in request_payload else OpenAIResponseRequest
    )
    with pytest.raises(ValueError, match="remote URLs are forbidden"):
        request_type.model_validate(request_payload)


@pytest.mark.parametrize(
    ("data_url", "expected_error"),
    [
        ("data:image/png;base64,not*base64", "valid base64"),
        (_image_data_url("image/svg+xml", b"svg"), "media type is not supported"),
        ("data:image/png,AAAA", "must use the data:<media>;base64,<data> form"),
        ("data:image/png;base64,", "data URL is malformed"),
    ],
)
def test_chat_image_inputs_reject_malformed_or_unsupported_data_urls(
    data_url: str,
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        OpenAIChatCompletionRequest.model_validate(
            {
                "model": "fixture-model",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "image_url", "image_url": {"url": data_url}}],
                    }
                ],
            }
        )


def test_responses_image_input_rejects_file_ids() -> None:
    with pytest.raises(ValueError, match="only type and image_url"):
        OpenAIResponseRequest.model_validate(
            {
                "model": "fixture-model",
                "input": [
                    {
                        "role": "user",
                        "content": [{"type": "input_image", "file_id": "file-123"}],
                    }
                ],
            }
        )


def test_openai_image_input_rejects_oversized_decoded_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(openai_session, "MAX_IMAGE_BYTES", 3)
    with pytest.raises(ValueError, match="decoded image exceeds the 3-byte limit"):
        OpenAIResponseRequest.model_validate(
            {
                "model": "fixture-model",
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": _image_data_url("image/png", b"four"),
                            }
                        ],
                    }
                ],
            }
        )


@pytest.mark.parametrize(
    ("input_value", "expected_error"),
    [
        ([], "Responses input must be text or a non-empty message list"),
        (
            [{"type": "function_call_output", "call_id": "call-1", "output": "ok"}],
            "Responses input supports only message items in this endpoint",
        ),
        (
            [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": _image_data_url("image/png", b"image"),
                        }
                    ],
                }
            ],
            "only user messages may contain input_image items",
        ),
    ],
)
def test_responses_validation_names_unsupported_input_subset(
    input_value: object,
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        OpenAIResponseRequest.model_validate({"model": "authorized-profile", "input": input_value})


def test_responses_json_schema_validation_names_required_fields() -> None:
    with pytest.raises(ValueError, match="json_schema text format requires name and schema"):
        OpenAIResponseRequest.model_validate(
            {
                "model": "authorized-profile",
                "input": "hello",
                "text": {"format": {"type": "json_schema", "name": "answer"}},
            }
        )


def test_responses_result_maps_json_usage_and_incomplete_status() -> None:
    session_id = uuid4()
    response = from_canonical_response_result(
        CanonicalSessionResult(
            sessionId=session_id,
            profile="authorized-profile",
            content={"decision": "hold", "explanation": "波動"},
            finishReason="length",
            usage={"inputTokens": 11, "outputTokens": 7, "totalTokens": 18},
            created=456,
        )
    )

    assert response.id == f"resp_{session_id}"
    assert response.object == "response"
    assert response.status == "incomplete"
    assert response.completed_at is None
    assert response.incomplete_details is not None
    assert response.incomplete_details.reason == "max_output_tokens"
    assert response.output[0].id == f"msg_{session_id}"
    assert response.output[0].status == "incomplete"
    assert response.output_text == '{"decision":"hold","explanation":"波動"}'
    assert response.output[0].content[0].text == response.output_text
    assert response.usage is not None
    assert response.usage.model_dump(mode="json") == {
        "input_tokens": 11,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens": 7,
        "output_tokens_details": {"reasoning_tokens": 0},
        "total_tokens": 18,
    }


def test_responses_adapter_forwards_authority_context_to_facade() -> None:
    async def scenario() -> None:
        facade = _Facade()
        adapter = OpenAICompatibleSessionAdapter(facade)

        response = await adapter.create_response(
            OpenAIResponseRequest(model="authorized-profile", input="hello"),
            tenant_id="tenant-response",
            namespace="research",
            actor_id="actor-response",
            idempotency_key="response-1",
        )

        assert response.status == "completed"
        assert response.output_text == '{"answer":"ok"}'
        assert facade.calls[0][0].messages == ({"role": "user", "content": "hello"},)
        assert facade.calls[0][1] == {
            "tenant_id": "tenant-response",
            "namespace": "research",
            "actor_id": "actor-response",
            "idempotency_key": "response-1",
        }

    asyncio.run(scenario())


def test_responses_sse_is_bounded_ordered_and_terminal() -> None:
    response = from_canonical_response_result(
        CanonicalSessionResult(
            sessionId=uuid4(),
            profile="authorized-profile",
            content="abcdef",
            created=789,
        )
    )

    events = list(openai_response_sse_events(response, chunk_size=2))
    event_types = [event.splitlines()[0].removeprefix("event: ") for event in events]
    payloads = [json.loads(event.splitlines()[1].removeprefix("data: ")) for event in events]

    assert event_types == [
        "response.created",
        "response.in_progress",
        "response.output_item.added",
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.done",
        "response.content_part.done",
        "response.output_item.done",
        "response.completed",
    ]
    assert [payload["sequence_number"] for payload in payloads] == list(range(len(events)))
    assert [payload["delta"] for payload in payloads[4:7]] == ["ab", "cd", "ef"]
    assert payloads[0]["response"]["status"] == "in_progress"
    assert payloads[0]["response"]["output"] == []
    assert payloads[-1]["response"]["status"] == "completed"
    assert payloads[-1]["response"]["output_text"] == "abcdef"
    assert all("[DONE]" not in event for event in events)


def test_responses_sse_uses_incomplete_terminal_event() -> None:
    response = from_canonical_response_result(
        CanonicalSessionResult(
            sessionId=uuid4(),
            profile="authorized-profile",
            content="bounded",
            finishReason="length",
        )
    )

    events = list(openai_response_sse_events(response))

    assert events[-1].startswith("event: response.incomplete\n")
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        list(openai_response_sse_events(response, chunk_size=0))
