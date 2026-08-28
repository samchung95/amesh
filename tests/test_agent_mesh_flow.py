from copy import deepcopy

import pytest
from pydantic import ValidationError

from amesh.dsl import FlowDefinition, compile_flow_tasks


def _mesh_task() -> dict[str, object]:
    session_budget = {
        "maxTotalTokens": 500,
        "maxCostUsd": "0.10",
        "maxDurationSeconds": 60,
        "maxToolCalls": 2,
    }
    return {
        "id": "incident-mesh",
        "type": "agent.mesh",
        "topology": "SUPERVISOR",
        "maxConcurrency": 1,
        "budget": {
            "maxSessions": 2,
            "maxConcurrency": 1,
            "maxTotalTokens": 1_000,
            "maxCostUsd": "0.20",
            "maxDurationSeconds": 120,
            "maxToolCalls": 4,
        },
        "members": [
            {
                "memberId": "analyst",
                "task": "analyst-session",
                "agent": "incident-analyst",
                "agentRevision": 2,
                "role": "WORKER",
                "capabilities": ["incident-analysis"],
            },
            {
                "memberId": "supervisor",
                "task": "supervisor-session",
                "agent": "incident-supervisor",
                "agentRevision": 4,
                "role": "SUPERVISOR",
                "capabilities": ["incident-response"],
            },
        ],
        "tasks": [
            {
                "id": "analyst-session",
                "type": "agent.session",
                "agent": "incident-analyst",
                "agentRevision": 2,
                "meshId": "incident-mesh",
                "memberId": "analyst",
                "meshBudget": session_budget,
                "input": {"question": "Assess the incident."},
            },
            {
                "id": "validated-handoff",
                "type": "agent.handoff",
                "dependsOn": ["analyst-session"],
                "source": {
                    "task": "analyst-session",
                    "agent": "incident-analyst",
                    "agentRevision": 2,
                },
                "destination": {
                    "task": "supervisor-session",
                    "agent": "incident-supervisor",
                    "agentRevision": 4,
                },
                "payload": {"finding": "confirmed"},
                "schema": {
                    "type": "object",
                    "required": ["finding"],
                    "properties": {"finding": {"type": "string"}},
                },
                "rationale": "Escalate the validated finding.",
                "requiredCapabilities": ["incident-response"],
                "policy": {
                    "outcome": "ALLOW",
                    "decisionId": "handoff-policy-1",
                    "policyDigest": "sha256:" + "a" * 64,
                },
            },
            {
                "id": "supervisor-session",
                "type": "agent.session",
                "dependsOn": ["validated-handoff"],
                "agent": "incident-supervisor",
                "agentRevision": 4,
                "meshId": "incident-mesh",
                "memberId": "supervisor",
                "meshBudget": session_budget,
                "input": {"finding": "{{ outputs['validated-handoff'].payload.finding }}"},
            },
        ],
    }


def test_agent_mesh_compiles_to_existing_durable_task_plan() -> None:
    flow = FlowDefinition.model_validate(
        {"id": "incident", "namespace": "tests", "tasks": [_mesh_task()]}
    )

    plan = compile_flow_tasks(flow)

    assert [node.task.id for node in plan] == [
        "incident-mesh",
        "analyst-session",
        "validated-handoff",
        "supervisor-session",
    ]
    assert plan[0].mode == "AGENT_MESH"
    assert plan[2].dependencies == ("analyst-session",)
    assert plan[3].dependencies == ("validated-handoff",)


def test_agent_mesh_rejects_overcommitted_reservations() -> None:
    mesh = _mesh_task()
    mesh["budget"] = {**mesh["budget"], "maxTotalTokens": 999}  # type: ignore[arg-type]

    with pytest.raises(ValidationError, match="session reservations exceed"):
        FlowDefinition.model_validate({"id": "incident", "namespace": "tests", "tasks": [mesh]})


def test_agent_mesh_rejects_an_unwired_handoff() -> None:
    mesh = deepcopy(_mesh_task())
    mesh["tasks"][1]["dependsOn"] = []  # type: ignore[index]

    with pytest.raises(ValidationError, match="directly depend on its source"):
        FlowDefinition.model_validate({"id": "incident", "namespace": "tests", "tasks": [mesh]})
