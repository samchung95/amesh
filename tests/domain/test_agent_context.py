from __future__ import annotations

import pytest

from amesh.domain import (
    AgentContextPolicy,
    AgentContextReceipt,
    canonical_json,
    project_agent_context,
)


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


def test_legacy_v1_receipts_remain_readable() -> None:
    messages = (
        {"role": "system", "content": "Pinned"},
        {"role": "user", "content": "Input"},
        {"role": "assistant", "content": "Action"},
        {"role": "user", "content": "Result"},
    )

    legacy = project_agent_context(
        messages,
        AgentContextPolicy(maxMessages=4, maxBytes=10_000, maxEstimatedTokens=10_000),
        turn=2,
        version="v1",
    ).receipt

    restored = AgentContextReceipt.model_validate(legacy.model_dump(mode="json", by_alias=True))

    assert restored == legacy
    assert restored.schema_version == "amesh.agent-context/v1"
    assert restored.algorithm == "amesh.recent-complete-turns/v1"


def test_v2_compaction_marker_and_pinned_prefix_are_stable_as_transcript_grows() -> None:
    first_transcript = (
        {"role": "system", "content": "Pinned instructions"},
        {"role": "user", "content": "Pinned input"},
        {"role": "assistant", "content": '{"action":"tool","turn":1}'},
        {"role": "user", "content": '{"tool":"lookup","result":"old"}'},
        {"role": "assistant", "content": '{"action":"tool","turn":2}'},
        {"role": "user", "content": '{"tool":"lookup","result":"new"}'},
    )
    grown_transcript = (
        *first_transcript,
        {"role": "assistant", "content": '{"action":"tool","turn":3}'},
        {"role": "user", "content": '{"tool":"lookup","result":"latest"}'},
    )
    policy = AgentContextPolicy(maxMessages=5, maxBytes=10_000, maxEstimatedTokens=10_000)

    first = project_agent_context(first_transcript, policy, turn=3)
    grown = project_agent_context(grown_transcript, policy, turn=4)
    legacy_first = project_agent_context(first_transcript, policy, turn=3, version="v1")
    legacy_grown = project_agent_context(grown_transcript, policy, turn=4, version="v1")

    first_prefix_bytes = canonical_json(first.messages[:2])
    grown_prefix_bytes = canonical_json(grown.messages[:2])
    first_marker = first.messages[2]
    grown_marker = grown.messages[2]

    assert first_prefix_bytes == grown_prefix_bytes
    assert canonical_json(legacy_first.messages[2]) != canonical_json(legacy_grown.messages[2])
    assert canonical_json(first_marker) == canonical_json(grown_marker)
    assert first_marker["role"] == "system"
    assert "transcript" not in first_marker["content"].lower()
    assert first.receipt.transcript_digest not in first_marker["content"]
    assert str(first.receipt.transcript_message_count) not in first_marker["content"]
    assert first.receipt.schema_version == "amesh.agent-context/v2"
    assert first.receipt.algorithm == "amesh.recent-complete-turns/v2"
    assert first.receipt.context_message_count <= policy.max_messages
    assert first.receipt.context_bytes <= policy.max_bytes
    assert first.receipt.context_estimated_tokens <= policy.max_estimated_tokens
    assert first.receipt.complete_turns_preserved is True
    assert first.receipt.retained_source_indexes == (0, 1, 4, 5)
    assert first.receipt.omitted_source_indexes == (2, 3)
    assert grown.receipt.omitted_source_indexes == (2, 3, 4, 5)


def test_v2_projection_is_deterministic_for_a_frozen_transcript() -> None:
    messages = (
        {"role": "system", "content": "Pinned"},
        {"role": "user", "content": "Input"},
        {"role": "assistant", "content": "Action"},
        {"role": "user", "content": "Result"},
        {"role": "assistant", "content": "Next action"},
        {"role": "user", "content": "Next result"},
    )
    policy = AgentContextPolicy(maxMessages=5, maxBytes=10_000, maxEstimatedTokens=10_000)

    first = project_agent_context(messages, policy, turn=3)
    second = project_agent_context(messages, policy, turn=3)

    assert first == second
    assert first.receipt.retained_source_indexes == (0, 1, 4, 5)
    assert first.receipt.omitted_source_indexes == (2, 3)


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
