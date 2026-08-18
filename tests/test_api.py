from fastapi.testclient import TestClient

from amesh.app import app

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
