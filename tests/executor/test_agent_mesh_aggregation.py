from uuid import uuid4

from amesh.domain import TaskRunState
from amesh.dsl import FlowDefinition, compile_flow_tasks
from amesh.executor.service import _agent_mesh_budget_error, _aggregate_flowable_result
from amesh.ports import PersistedTaskRun


def _plan_and_children(*, tokens: tuple[int, int]):
    session_budget = {
        "maxTotalTokens": 5,
        "maxCostUsd": "0.10",
        "maxDurationSeconds": 30,
        "maxToolCalls": 1,
    }
    mesh = {
        "id": "peer-mesh",
        "type": "agent.mesh",
        "topology": "PEER_TO_PEER",
        "maxConcurrency": 2,
        "budget": {
            "maxSessions": 2,
            "maxConcurrency": 2,
            "maxTotalTokens": 10,
            "maxCostUsd": "0.20",
            "maxDurationSeconds": 60,
            "maxToolCalls": 2,
        },
        "members": [
            {
                "memberId": member,
                "task": f"{member}-session",
                "agent": f"{member}-agent",
                "agentRevision": 1,
                "role": "PEER",
            }
            for member in ("first", "second")
        ],
        "tasks": [
            {
                "id": f"{member}-session",
                "type": "agent.session",
                "agent": f"{member}-agent",
                "agentRevision": 1,
                "meshId": "peer-mesh",
                "memberId": member,
                "meshBudget": session_budget,
                "input": {"prompt": member},
            }
            for member in ("first", "second")
        ],
    }
    flow = FlowDefinition.model_validate({"id": "peer-flow", "namespace": "tests", "tasks": [mesh]})
    node = compile_flow_tasks(flow)[0]
    execution_id = uuid4()
    children = [
        PersistedTaskRun(
            task_run_id=uuid4(),
            execution_id=execution_id,
            task_id=f"{member}-session",
            state=TaskRunState.SUCCESS,
            current_attempt=1,
            version=2,
            result={
                "session": {
                    "counters": {
                        "totalTokens": token_count,
                        "costUsd": "0.05",
                        "toolCalls": 1,
                    }
                }
            },
        )
        for member, token_count in zip(("first", "second"), tokens, strict=True)
    ]
    return node, children


def test_mesh_parent_aggregates_usage_and_discloses_model_nondeterminism() -> None:
    node, children = _plan_and_children(tokens=(4, 5))

    result = _aggregate_flowable_result(node, children)

    assert result["agentMesh"]["usage"] == {
        "sessions": 2,
        "totalTokens": 9,
        "costUsd": "0.10",
        "toolCalls": 2,
        "reservedDurationSeconds": 60,
    }
    assert result["agentMesh"]["nondeterministic"] is True
    assert _agent_mesh_budget_error(node, children) is None


def test_mesh_parent_fails_closed_if_persisted_usage_exceeds_its_budget() -> None:
    node, children = _plan_and_children(tokens=(6, 5))

    assert _agent_mesh_budget_error(node, children) == (
        "agent.mesh exceeded parent budget: maxTotalTokens"
    )
