from fastapi.testclient import TestClient
from starlette.routing import Match

from amesh.app import app

from .test_kestra_flow_import import FIXTURE


def test_declared_compatibility_api_validates_source_and_serves_manifest() -> None:
    client = TestClient(app)

    validation = client.post(
        "/api/v1/main/flows/validate",
        content=FIXTURE.read_bytes(),
        headers={"content-type": "application/yaml"},
    )
    manifest = client.get("/api/v1/compatibility/kestra/manifest")

    assert validation.status_code == 200
    assert validation.json()["valid"] is True
    assert validation.json()["releaseClaimAllowed"] is False
    assert manifest.status_code == 200
    assert manifest.json()["target"]["version"] == "1.3.30"
    assert manifest.json()["releaseClaimAllowed"] is False
    rest = next(item for item in manifest.json()["surfaces"] if item["name"] == "rest")
    assert all(
        {
            "method",
            "path",
            "requestSchema",
            "responseSchema",
            "pagination",
            "statusCodes",
            "errorSchema",
        }
        <= set(operation)
        for operation in rest["operations"]
    )


def test_openapi_declares_the_bounded_execution_facade_schema() -> None:
    document = TestClient(app).get("/openapi.json").json()

    operation = document["paths"]["/api/v1/executions/{namespace}/{flow_id}"]["post"]
    assert operation["tags"] == ["compatibility"]
    assert operation["requestBody"]["required"] is True
    schema = document["components"]["schemas"]["KestraExecutionRequest"]
    assert set(schema["properties"]) == {"inputs", "runner", "idempotencyKey"}


def test_compatibility_execution_route_does_not_intercept_specific_actions() -> None:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/executions/example/interventions",
        "root_path": "",
    }

    first_match = next(
        route
        for route in app.routes
        if route.matches(scope)[0] is Match.FULL  # type: ignore[attr-defined]
    )

    assert first_match.path == "/api/v1/executions/{execution_id}/interventions"  # type: ignore[attr-defined]
