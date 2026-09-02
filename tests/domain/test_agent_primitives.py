from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from amesh.domain import (
    AgentInvocationAccounting,
    AgentInvocationCostState,
    McpConnectionSpec,
    McpToolImpact,
    McpToolPin,
    ModelBudget,
    ModelProviderSpec,
)


def test_invocation_accounting_is_bounded_numeric_and_cost_explicit() -> None:
    accounting = AgentInvocationAccounting(
        inputTokens=120,
        outputTokens=80,
        reasoningTokens=50,
        totalTokens=200,
        cacheReadTokens=40,
        cacheWriteTokens=10,
        costState=AgentInvocationCostState.BILLED,
        costAmountUsd=Decimal("0.00125"),
    )

    assert accounting.model_dump(mode="json", by_alias=True) == {
        "inputTokens": 120,
        "outputTokens": 80,
        "reasoningTokens": 50,
        "totalTokens": 200,
        "cacheReadTokens": 40,
        "cacheWriteTokens": 10,
        "costState": "billed",
        "costAmountUsd": "0.00125",
    }

    with pytest.raises(ValidationError, match="costAmountUsd"):
        AgentInvocationAccounting(costState="billed")
    with pytest.raises(ValidationError, match="only billed"):
        AgentInvocationAccounting(costState="unpriced", costAmountUsd="0.01")
    with pytest.raises(ValidationError):
        AgentInvocationAccounting(inputTokens=2**63, costState="unavailable")
    with pytest.raises(ValidationError, match="Extra inputs"):
        AgentInvocationAccounting(
            costState="unavailable",
            reasoningContent="private chain of thought",
        )


def test_model_provider_and_budget_reject_implicit_or_unbounded_configuration() -> None:
    with pytest.raises(ValidationError, match="cannot contain credentials"):
        ModelProviderSpec(
            endpoint="https://user:secret@example.test/chat",
            credentialRef="openrouter",
        )

    with pytest.raises(ValidationError, match="cannot exceed"):
        ModelBudget(
            maxTotalTokens=10,
            maxCompletionTokens=11,
            maxCostUsd=Decimal("0.01"),
        )


def test_mcp_connection_requires_exact_valid_schema_pins() -> None:
    tool = McpToolPin(
        name="lookup",
        inputSchema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
        impact=McpToolImpact.READ_ONLY,
    )
    connection = McpConnectionSpec(
        key="catalog",
        namespace="agents.demo",
        endpoint="https://mcp.example.test/mcp",
        credentialRef="mcp-token",
        toolAllowlist=("lookup",),
        tools=(tool,),
    )

    assert connection.digest.startswith("sha256:")
    assert connection.pinned_tool("lookup").schema_digest.startswith("sha256:")
    assert connection.model_validate(connection.model_dump()).digest == connection.digest

    with pytest.raises(ValidationError, match="exactly match"):
        McpConnectionSpec(
            key="catalog",
            namespace="agents.demo",
            endpoint="https://mcp.example.test/mcp",
            credentialRef="mcp-token",
            toolAllowlist=("other",),
            tools=(tool,),
        )

    with pytest.raises(ValidationError, match="invalid MCP tool schema"):
        McpToolPin(name="broken", inputSchema={"type": "not-a-json-schema-type"})
