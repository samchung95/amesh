from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from amesh.domain import (
    AgentHandoffRequest,
    AgentHardLimits,
    AgentMeshBudget,
    AgentMeshDefinition,
    AgentMeshSessionBudget,
    AgentRouteRequest,
    build_agent_handoff,
    effective_agent_limits,
    route_agent,
)


def _policy(*, outcome: str = "ALLOW") -> dict[str, object]:
    return {
        "outcome": outcome,
        "decisionId": "policy-decision-1",
        "policyDigest": "sha256:" + "a" * 64,
    }


def _candidate(
    member_id: str,
    *,
    score: str,
    cost: str,
    latency: int,
    outcome: str = "ALLOW",
    available: bool = True,
) -> dict[str, object]:
    return {
        "memberId": member_id,
        "task": f"{member_id}-session",
        "agent": f"{member_id}-agent",
        "agentRevision": 1,
        "capabilities": ["incident-analysis"],
        "policy": _policy(outcome=outcome),
        "projectedCostUsd": cost,
        "projectedLatencyMs": latency,
        "availability": {
            "available": available,
            "source": "worker-heartbeat",
            "checkedAt": datetime(2026, 8, 25, tzinfo=UTC),
        },
        "evaluation": {"key": "incident-quality", "revision": 3, "score": score},
    }


def _hard_limits() -> AgentHardLimits:
    return AgentHardLimits(
        maxTotalTokens=8_000,
        maxCostUsd="2.00",
        maxDurationSeconds=600,
        maxToolCalls=20,
        maxTurns=10,
        maxLoopIterations=0,
        maxRecursionDepth=0,
        maxConcurrency=1,
    )


@pytest.mark.parametrize(
    ("topology", "roles", "parents"),
    [
        ("SUPERVISOR", ("SUPERVISOR", "WORKER"), (None, None)),
        ("ROUTER", ("ROUTER", "WORKER"), (None, None)),
        ("PEER_TO_PEER", ("PEER", "PEER"), (None, None)),
        ("HIERARCHICAL", ("SUPERVISOR", "WORKER"), (None, "first")),
        ("SWARM", ("PEER", "PEER"), (None, None)),
    ],
)
def test_supported_mesh_topologies_are_explicit_and_bounded(
    topology: str,
    roles: tuple[str, str],
    parents: tuple[str | None, str | None],
) -> None:
    definition = AgentMeshDefinition.model_validate(
        {
            "topology": topology,
            "members": [
                {
                    "memberId": member_id,
                    "task": f"{member_id}-session",
                    "agent": f"{member_id}-agent",
                    "agentRevision": 1,
                    "role": role,
                    "parentMemberId": parent,
                }
                for member_id, role, parent in zip(("first", "second"), roles, parents, strict=True)
            ],
            "budget": {
                "maxSessions": 2,
                "maxConcurrency": 2,
                "maxTotalTokens": 2_000,
                "maxCostUsd": "1",
                "maxDurationSeconds": 120,
                "maxToolCalls": 4,
            },
        }
    )

    assert definition.topology.value == topology


def test_mesh_topology_rejects_cycles_and_session_overcommit() -> None:
    budget = AgentMeshBudget(
        maxSessions=1,
        maxConcurrency=1,
        maxTotalTokens=1_000,
        maxCostUsd="1",
        maxDurationSeconds=60,
        maxToolCalls=2,
    )
    with pytest.raises(ValidationError, match="member count exceeds"):
        AgentMeshDefinition.model_validate(
            {
                "topology": "HIERARCHICAL",
                "members": [
                    {
                        "memberId": "lead",
                        "task": "lead-session",
                        "agent": "lead-agent",
                        "agentRevision": 1,
                        "role": "SUPERVISOR",
                        "parentMemberId": "worker",
                    },
                    {
                        "memberId": "worker",
                        "task": "worker-session",
                        "agent": "worker-agent",
                        "agentRevision": 1,
                        "role": "WORKER",
                        "parentMemberId": "lead",
                    },
                ],
                "budget": budget.model_dump(mode="json", by_alias=True),
            }
        )


def test_route_agent_gates_then_ranks_with_a_durable_explanation() -> None:
    request = AgentRouteRequest.model_validate(
        {
            "requiredCapabilities": ["incident-analysis"],
            "candidates": [
                _candidate("low-score", score="0.70", cost="0.01", latency=100),
                _candidate("winner", score="0.90", cost="0.03", latency=400),
                _candidate("denied", score="1", cost="0", latency=1, outcome="DENY"),
                _candidate("offline", score="1", cost="0", latency=1, available=False),
            ],
        }
    )

    decision = route_agent(request)

    assert decision.selected_member_id == "winner"
    assert decision.ranked_member_ids == ("winner", "low-score")
    assert decision.decision_digest.startswith("sha256:")
    assert {item.member_id: item.eligible for item in decision.assessments} == {
        "low-score": True,
        "winner": True,
        "denied": False,
        "offline": False,
    }


def test_handoff_enforces_source_schema_capabilities_policy_and_redaction() -> None:
    request = AgentHandoffRequest.model_validate(
        {
            "source": {"task": "analyst-session", "agent": "analyst", "agentRevision": 2},
            "destination": {
                "task": "supervisor-session",
                "agent": "supervisor",
                "agentRevision": 4,
            },
            "payload": {"finding": "token=secret-value", "internal": "omit"},
            "schema": {
                "type": "object",
                "required": ["finding"],
                "properties": {"finding": {"type": "string"}},
                "additionalProperties": True,
            },
            "rationale": "Escalate the validated incident finding.",
            "contextKeys": ["finding"],
            "requiredCapabilities": ["incident-response"],
            "policy": _policy(),
        }
    )

    handoff = build_agent_handoff(
        request,
        source_session={"agentKey": "analyst", "agentRevision": 2},
        destination_capabilities=("incident-response",),
        secrets=("secret-value",),
    )

    assert handoff.context == {"finding": "token=[REDACTED]"}
    assert handoff.secret_values_redacted is True
    assert handoff.context_digest.startswith("sha256:")
    assert handoff.handoff_digest.startswith("sha256:")

    with pytest.raises(PermissionError, match="source does not match"):
        build_agent_handoff(
            request,
            source_session={"agentKey": "wrong", "agentRevision": 2},
            destination_capabilities=("incident-response",),
        )


def test_mesh_session_budget_tightens_agent_limits() -> None:
    effective = effective_agent_limits(
        _hard_limits(),
        AgentMeshSessionBudget(
            maxTotalTokens=2_000,
            maxCostUsd="0.25",
            maxDurationSeconds=90,
            maxToolCalls=3,
        ),
    )

    assert effective.max_total_tokens == 2_000
    assert effective.max_cost_usd == Decimal("0.25")
    assert effective.max_duration_seconds == 90
    assert effective.max_tool_calls == 3
    assert effective.max_turns == 10
