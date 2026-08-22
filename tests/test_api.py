from fastapi.testclient import TestClient
from starlette.requests import Request

from amesh.app import _build_flow_graph, _problem_response, app, get_read_repository
from amesh.config import Settings
from amesh.dsl import FlowDefinition
from amesh.ports import PersistedIterationSummary

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_http_errors_use_problem_details() -> None:
    response = client.get("/api/v1/not-a-resource")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "urn:amesh:problem:http_404",
        "title": "Not Found",
        "status": 404,
        "detail": "Not Found",
        "code": "HTTP_404",
        "instance": "/api/v1/not-a-resource",
    }


def test_problem_details_preserve_structured_validation_detail() -> None:
    detail = [{"code": "MISSING_FIELD", "path": ["namespace"]}]
    request = Request(
        {
            "type": "http",
            "method": "PUT",
            "scheme": "http",
            "server": ("amesh.test", 80),
            "path": "/api/v1/flows",
            "query_string": b"",
            "headers": [],
        }
    )
    response = _problem_response(
        request,
        status_code=422,
        detail=detail,
    )

    assert response.status_code == 422
    assert response.media_type == "application/problem+json"
    assert detail[0]["code"].encode() in response.body


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


def test_read_repository_uses_primary_unless_replica_is_configured(monkeypatch) -> None:
    primary = object()
    replica = object()
    monkeypatch.setattr(
        "amesh.app.get_settings",
        lambda: Settings(_env_file=None),
    )
    assert get_read_repository(primary) is primary

    monkeypatch.setattr(
        "amesh.app.get_settings",
        lambda: Settings(
            _env_file=None,
            database_read_replica_url="postgresql+asyncpg://replica/amesh",
        ),
    )
    monkeypatch.setattr("amesh.app.get_replica_repository", lambda: replica)
    assert get_read_repository(primary) is replica
