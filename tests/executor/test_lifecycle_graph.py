from amesh.app import _build_flow_graph
from amesh.dsl import FlowDefinition


def test_flow_graph_identifies_lifecycle_phase_and_handler_owner() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "lifecycle_graph",
            "namespace": "tests",
            "tasks": [
                {
                    "id": "group",
                    "type": "core.sequential",
                    "tasks": [{"id": "work", "type": "core.return"}],
                    "errors": [{"id": "recover", "type": "core.return"}],
                }
            ],
            "finally": [{"id": "cleanup", "type": "core.return"}],
            "afterExecution": [{"id": "publish", "type": "core.return"}],
        }
    )

    graph = _build_flow_graph(flow)
    nodes = {node.task_id: node for node in graph.nodes}

    assert nodes["work"].lifecycle_phase == "MAIN"
    assert nodes["recover"].lifecycle_phase == "ERROR"
    assert nodes["recover"].handler_owner_id == "group"
    assert nodes["cleanup"].lifecycle_phase == "FINALLY"
    assert nodes["publish"].lifecycle_phase == "AFTER_EXECUTION"
    assert any(
        edge.source == "group" and edge.target == "recover" and edge.kind == "handles"
        for edge in graph.edges
    )
