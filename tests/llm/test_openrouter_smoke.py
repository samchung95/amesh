from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext
from amesh.tasks import agent_llm_handler

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
        handler = agent_llm_handler()
        task = TaskDefinition.model_validate(
            {
                "id": "live_llm",
                "type": "agent.chat",
                "prompt": "Reply with a short confirmation that the AMESH LLM test is reachable.",
                "provider": {
                    "endpoint": OPENROUTER_CHAT_COMPLETIONS_URL,
                    "credentialRef": "openrouter",
                },
                "model": model,
                "budget": {
                    "maxTotalTokens": 128,
                    "maxCompletionTokens": 32,
                    "maxCostUsd": "0.10",
                },
                "dataHandling": {
                    "egress": "REDACT_SECRETS",
                    "promptRetention": "HASH_ONLY",
                },
                "contract": {"secretScopes": ["openrouter"]},
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
                namespace="agents.smoke",
                secret_scopes=("openrouter",),
                secrets={"openrouter": api_key},
            ),
        )
        assert result.output["model"]
        assert result.output["content"].strip()
        assert result.output["costUsd"]
        assert result.output["provenance"]["nondeterministic"] is True
        assert "request" not in result.output["provenance"]

    asyncio.run(scenario())
