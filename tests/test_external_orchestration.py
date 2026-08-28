from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from amesh.app import _problem_response, app, observe_http
from amesh.external_orchestration import error_category, external_orchestration_profile

sys.path.insert(0, str(Path(__file__).parents[1] / "sdks" / "api" / "python"))

from amesh_client.execution import ExecutionClient, HttpResponse

client = TestClient(app)


class _Transport:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        self.requests.append({"method": method, "url": url, "headers": headers, "body": body})
        return HttpResponse(
            200,
            {},
            json.dumps(
                {
                    "execution": {
                        "execution_id": "0198cafe-0000-7000-8000-000000000001",
                        "tenant_id": "default",
                        "state": "SUCCESS",
                        "epoch": 1,
                        "version": 1,
                        "namespace": "examples.mvp",
                        "flow_id": "hello_world",
                        "created_at": "2026-08-23T00:00:00Z",
                        "updated_at": "2026-08-23T00:00:01Z",
                    },
                    "taskRuns": [],
                }
            ).encode(),
        )


def test_profile_publishes_only_client_neutral_versioned_operations() -> None:
    response = client.get("/api/v1/orchestration/profile")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schemaVersion"] == "amesh.external-orchestration/v1"
    assert {operation["name"] for operation in payload["operations"]} == {
        "validate",
        "apply",
        "read_exact_revision",
        "launch",
        "inspect",
        "preview_control",
        "apply_control",
        "events",
        "webhook_subscription",
    }
    assert all("vibestonks" not in str(operation).lower() for operation in payload["operations"])
    assert "X-Correlation-ID" in payload["requestHeaders"]
    assert "Idempotency-Key" in payload["requestHeaders"]


def test_every_profile_operation_matches_the_published_openapi_contract() -> None:
    profile = external_orchestration_profile()
    openapi_paths = app.openapi()["paths"]

    for operation in profile.operations:
        openapi_path = operation.path.split("?", maxsplit=1)[0]
        assert openapi_path in openapi_paths, operation.name
        assert operation.method.lower() in openapi_paths[openapi_path], operation.name


def test_profile_is_stable_and_categorizes_retry_conflict_and_ambiguous_errors() -> None:
    assert external_orchestration_profile() == external_orchestration_profile()
    assert error_category(503) == "retryable"
    assert error_category(409) == "conflict"
    assert error_category(425, "AMBIGUOUS_EXTERNAL_OUTCOME") == "ambiguous"
    assert error_category(422) == "terminal"


def test_http_boundary_echoes_or_generates_safe_correlation_id() -> None:
    provided = client.get(
        "/api/v1/orchestration/profile",
        headers={"X-Correlation-ID": "client-attempt-17"},
    )
    assert provided.status_code == 200
    assert provided.headers["X-Correlation-ID"] == "client-attempt-17"

    generated = client.get("/api/v1/orchestration/profile")
    assert generated.headers["X-Correlation-ID"]
    assert generated.headers["X-Correlation-ID"] != provided.headers["X-Correlation-ID"]


def test_http_boundary_rejects_header_injection_correlation_id() -> None:
    response = client.get(
        "/api/v1/orchestration/profile",
        headers={"X-Correlation-ID": " bad-value"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CORRELATION_ID"
    assert response.headers["X-Amesh-Error-Category"] == "terminal"


def test_http_boundary_preserves_ambiguous_problem_category() -> None:
    probe = FastAPI()
    probe.middleware("http")(observe_http)

    @probe.get("/ambiguous")
    async def ambiguous(request: Request) -> object:
        return _problem_response(
            request,
            status_code=409,
            detail="external outcome must be inspected before retry",
            code="AMBIGUOUS_EXTERNAL_OUTCOME",
        )

    response = TestClient(probe).get(
        "/ambiguous",
        headers={"X-Correlation-ID": "client-attempt-ambiguous"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "AMBIGUOUS_EXTERNAL_OUTCOME"
    assert response.headers["X-Amesh-Error-Category"] == "ambiguous"
    assert response.headers["X-Correlation-ID"] == "client-attempt-ambiguous"


def test_python_sdk_launch_carries_stable_correlation_and_idempotency_headers() -> None:
    transport = _Transport()
    client_sdk = ExecutionClient("https://amesh.test", "token", transport=transport)

    client_sdk.launch(
        "examples.mvp",
        "hello_world",
        idempotency_key="launch-17",
        correlation_id="client-attempt-17",
    )

    assert transport.requests[0]["headers"]["Idempotency-Key"] == "launch-17"
    assert transport.requests[0]["headers"]["X-Correlation-ID"] == "client-attempt-17"
