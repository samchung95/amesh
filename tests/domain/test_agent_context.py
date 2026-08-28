from __future__ import annotations

import pytest

from amesh.domain import AgentContextPolicy, project_agent_context


def test_projection_preserves_pinned_prefix_and_newest_complete_turn() -> None:
    messages = (
        {"role": "system", "content": "Pinned instructions"},
        {"role": "user", "content": "Pinned input"},
        {"role": "assistant", "content": '{"action":"tool","turn":1}'},
        {"role": "user", "content": '{"tool":"lookup","result":"old"}'},
        {"role": "assistant", "content": '{"action":"tool","turn":2}'},
        {"role": "user", "content": '{"tool":"lookup","result":"new"}'},
    )

    projection = project_agent_context(
        messages,
        AgentContextPolicy(maxMessages=5, maxBytes=10_000, maxEstimatedTokens=10_000),
        turn=3,
    )

    assert projection.messages[0:2] == messages[0:2]
    assert projection.messages[-2:] == messages[-2:]
    assert len(projection.messages) == 5
    assert projection.receipt.compacted is True
    assert projection.receipt.retained_source_indexes == (0, 1, 4, 5)
    assert projection.receipt.omitted_source_indexes == (2, 3)
    assert projection.receipt.complete_turns_preserved is True
    assert projection.receipt.transcript_digest != projection.receipt.context_digest
    assert projection.receipt.receipt_digest.startswith("sha256:")


def test_projection_is_stable_and_does_not_mutate_the_transcript() -> None:
    messages = (
        {"role": "system", "content": "Pinned"},
        {"role": "user", "content": "Input"},
        {"role": "assistant", "content": "Action"},
        {"role": "user", "content": "Result"},
    )
    policy = AgentContextPolicy(maxMessages=4, maxBytes=10_000, maxEstimatedTokens=10_000)

    first = project_agent_context(messages, policy, turn=2)
    second = project_agent_context(messages, policy, turn=2)

    assert first == second
    assert first.messages == messages
    assert first.receipt.compacted is False


def test_projection_fails_closed_when_pinned_context_cannot_fit() -> None:
    messages = (
        {"role": "system", "content": "x" * 500},
        {"role": "user", "content": "input"},
    )

    with pytest.raises(ValueError, match="pinned instructions"):
        project_agent_context(
            messages,
            AgentContextPolicy(maxMessages=3, maxBytes=256, maxEstimatedTokens=10_000),
            turn=1,
        )
