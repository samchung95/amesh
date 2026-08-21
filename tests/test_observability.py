from __future__ import annotations

import json
import logging

from fastapi.testclient import TestClient

from amesh.app import app
from amesh.observability import JsonFormatter


def test_metrics_endpoint_exposes_amesh_and_http_metrics() -> None:
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "amesh_build_info" in response.text
    assert 'amesh_http_requests_total{method="GET",route="/health",status="200"}' in response.text


def test_json_formatter_emits_structured_context() -> None:
    record = logging.LogRecord("amesh.test", logging.INFO, __file__, 1, "ready", (), None)
    record.execution_id = "execution-1"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "ready"
    assert payload["execution_id"] == "execution-1"
