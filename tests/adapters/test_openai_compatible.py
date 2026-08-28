from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
import pytest
from pydantic import SecretStr

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

    asyncio.run(scenario())
