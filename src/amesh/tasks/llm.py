from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskHandler

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
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        active_configuration = configuration or OpenAICompatibleConfig.from_environment()
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
        async with httpx.AsyncClient() as active_client:
            return await complete(active_client)

    return run
