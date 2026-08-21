from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext
from amesh.tasks import OpenAICompatibleConfig, agent_llm_handler

OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_TEST_MODEL = "openai/gpt-5.6-luna"


def configured_models() -> tuple[str, ...]:
    configured = os.getenv("OPENROUTER_TEST_MODELS", DEFAULT_TEST_MODEL)
    return tuple(model.strip() for model in configured.split(",") if model.strip())


@pytest.mark.parametrize("model", configured_models())
def test_openrouter_chat_completion_contract(model: str) -> None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key is None:
        pytest.skip("OPENROUTER_API_KEY is required for live LLM tests")

    async def scenario() -> None:
        handler = agent_llm_handler(
            OpenAICompatibleConfig(
                api_key=api_key,
                endpoint=OPENROUTER_CHAT_COMPLETIONS_URL,
                default_model=model,
            )
        )
        task = TaskDefinition.model_validate(
            {
                "id": "live_llm",
                "type": "agent.llm",
                "prompt": "Reply with a short confirmation that the AMESH LLM test is reachable.",
                "maxCompletionTokens": 32,
            }
        )
        result = await handler(
            task,
            TaskExecutionContext(
                tenant_id="default",
                execution_id=uuid4(),
                task_run_id=uuid4(),
                attempt=1,
                attempt_id=uuid4(),
                inputs={},
                outputs={},
                variables={},
            ),
        )
        assert result["model"]
        assert result["content"].strip()

    asyncio.run(scenario())
