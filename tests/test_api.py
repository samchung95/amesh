from fastapi.testclient import TestClient

from amesh.app import _build_flow_graph, app
from amesh.dsl import FlowDefinition
from amesh.ports import PersistedIterationSummary

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validate_endpoint() -> None:
    response = client.post(
        "/api/v1/flows/validate",
        content=b"id: x\nnamespace: tests\ntasks:\n  - id: a\n    type: core.return\n",
        headers={"content-type": "application/yaml"},
    )
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_loop_graph_uses_aggregated_template_nodes() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "loop_graph",
            "namespace": "tests",
            "tasks": [
                {
                    "id": "each",
                    "type": "core.foreach",
                    "items": [1, 2, 3],
                    "tasks": [{"id": "capture", "type": "core.return"}],
                }
            ],
        }
    )
    graph = _build_flow_graph(
        flow,
        iteration_summaries=[
            PersistedIterationSummary(
                loop_id="each",
                task_id="capture",
                iteration_count=3,
                waiting=0,
                running=0,
                succeeded=3,
                failed=0,
                cancelled=0,
            )
        ],
    )

    assert [node.task_id for node in graph.nodes] == [
        "each",
        "each--template--capture",
    ]
    assert graph.nodes[1].label == "capture"
    assert graph.nodes[1].iteration_count == 3
    assert graph.nodes[1].state == "SUCCESS"
