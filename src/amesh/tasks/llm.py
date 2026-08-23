from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskHandler
from amesh.networking import outbound_http_client
from amesh.tasks.http import HttpTaskPolicy, validate_http_destination

DEFAULT_OPENROUTER_MODEL = "openai/gpt-5.6-luna"


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    api_key: str
    endpoint: str = "https://openrouter.ai/api/v1/chat/completions"
    default_model: str = DEFAULT_OPENROUTER_MODEL

    @classmethod
    def from_environment(cls) -> OpenAICompatibleConfig:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required for agent.llm")
        return cls(
            api_key=api_key,
            endpoint=os.getenv(
                "OPENROUTER_CHAT_COMPLETIONS_URL",
                "https://openrouter.ai/api/v1/chat/completions",
            ),
            default_model=os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
        )


def agent_llm_handler(
    configuration: OpenAICompatibleConfig | None = None,
    client: httpx.AsyncClient | None = None,
    *,
    http_policy: HttpTaskPolicy | None = None,
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        active_configuration = configuration or OpenAICompatibleConfig.from_environment()
        active_policy = http_policy or HttpTaskPolicy()
        validate_http_destination(
            active_configuration.endpoint,
            active_policy,
            resolve_dns=client is None,
        )
        extra = task.model_extra or {}
        messages = extra.get("messages")
        if messages is None:
            prompt = extra.get("prompt")
            if not isinstance(prompt, str) or not prompt:
                raise ValueError(f"task {task.id!r} requires prompt or messages")
            messages = [{"role": "user", "content": prompt}]
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"task {task.id!r} messages must be a non-empty list")
        model = str(extra.get("model", active_configuration.default_model))
        max_tokens = int(extra.get("maxCompletionTokens", 128))

        async def complete(active_client: httpx.AsyncClient) -> dict[str, Any]:
            response = await active_client.post(
                active_configuration.endpoint,
                headers={
                    "Authorization": f"Bearer {active_configuration.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_completion_tokens": max_tokens,
                },
                timeout=task.timeout_seconds or 60,
            )
            response.raise_for_status()
            payload = response.json()
            choices = payload.get("choices") or []
            if not choices:
                raise RuntimeError("model response did not contain choices")
            message = choices[0].get("message") or {}
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("model response did not contain assistant content")
            return {
                "content": content,
                "model": payload.get("model", model),
                "usage": payload.get("usage", {}),
            }

        if client is not None:
            return await complete(client)
        async with outbound_http_client(
            active_configuration.endpoint,
            http_proxy_url=active_policy.http_proxy_url,
            https_proxy_url=active_policy.https_proxy_url,
            no_proxy=active_policy.no_proxy,
            ca_file=active_policy.ca_file,
            client_certificate_file=active_policy.client_certificate_file,
            client_key_file=active_policy.client_key_file,
        ) as active_client:
            return await complete(active_client)

    return run
