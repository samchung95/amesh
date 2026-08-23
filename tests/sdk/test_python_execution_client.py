from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdks" / "api" / "python"))

from amesh_client.execution import (  # noqa: E402
    AmeshError,
    ExecutionClient,
    HttpResponse,
    RetryPolicy,
    verify_webhook,
)


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]) -> None:
        self.responses = responses
        self.requests: list[dict[str, Any]] = []

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "timeout": timeout_seconds,
            }
        )
        return self.responses.pop(0)


def _detail(state: str = "SUCCESS") -> dict[str, object]:
    return {
        "execution": {
            "execution_id": "0198cafe-0000-7000-8000-000000000001",
            "tenant_id": "default",
            "state": state,
            "epoch": 1,
            "version": 2,
            "namespace": "examples.mvp",
            "flow_id": "hello_world",
            "created_at": "2026-08-23T00:00:00Z",
            "updated_at": "2026-08-23T00:00:01Z",
        },
        "taskRuns": [],
    }


def test_launch_retries_with_one_stable_key_and_typed_result() -> None:
    transport = FakeTransport(
        [
            HttpResponse(503, {"retry-after": "0", "x-request-id": "retry-1"}, b"{}"),
            HttpResponse(200, {}, json.dumps(_detail()).encode()),
        ]
    )
    client = ExecutionClient(
        "https://amesh.test",
        "test-token",
        transport=transport,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
        sleeper=lambda _: None,
    )

    detail = client.launch(
        "examples.mvp", "hello_world", inputs={"name": "SDK"}, idempotency_key="stable-key"
    )

    assert detail.execution.state.value == "SUCCESS"
    assert len(transport.requests) == 2
    assert {request["headers"]["Idempotency-Key"] for request in transport.requests} == {
        "stable-key"
    }
    assert transport.requests[0]["headers"]["Authorization"] == "Bearer test-token"
    assert transport.requests[0]["headers"]["X-Amesh-Tenant"] == "default"
    assert transport.requests[0]["body"] == transport.requests[1]["body"]


def test_normalized_error_and_ndjson_stream() -> None:
    denied = ExecutionClient(
        "https://amesh.test",
        "test-token",
        transport=FakeTransport(
            [HttpResponse(403, {"x-request-id": "request-7"}, b'{"detail":"denied"}')]
        ),
        retry_policy=RetryPolicy(max_attempts=1),
    )
    with pytest.raises(AmeshError) as captured:
        denied.get("0198cafe-0000-7000-8000-000000000001")
    assert captured.value.status == 403
    assert captured.value.request_id == "request-7"
    assert captured.value.retryable is False

    stream = ExecutionClient(
        "https://amesh.test",
        "test-token",
        transport=FakeTransport([HttpResponse(200, {}, b'{"taskId":"one"}\n{"taskId":"two"}\n')]),
    )
    assert [item["taskId"] for item in stream.stream_logs("execution-1")] == ["one", "two"]


def test_webhook_verification_enforces_hmac_and_timestamp_window() -> None:
    secret = "webhook-secret"
    timestamp = 1_800_000_000
    delivery_id = "0198cafe-0000-7000-8000-000000000002"
    body = b'{"event":"execution.completed"}'
    signed = f"{timestamp}.{delivery_id}.".encode() + body
    signature = "v1=" + hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()

    assert verify_webhook(
        secret, timestamp, delivery_id, body, signature, now_seconds=timestamp + 30
    )
    assert not verify_webhook(
        secret, timestamp, delivery_id, body, signature, now_seconds=timestamp + 301
    )
    assert not verify_webhook(
        secret, timestamp, delivery_id, body + b"x", signature, now_seconds=timestamp
    )


@pytest.mark.skipif(not os.getenv("AMESH_SDK_LIVE_ENDPOINT"), reason="live endpoint not configured")
def test_live_execution_conformance() -> None:
    client = ExecutionClient(
        os.environ["AMESH_SDK_LIVE_ENDPOINT"],
        os.environ["AMESH_SDK_LIVE_TOKEN"],
        os.getenv("AMESH_SDK_LIVE_TENANT", "default"),
    )
    launched = client.launch(
        os.getenv("AMESH_SDK_LIVE_NAMESPACE", "examples.getting_started"),
        os.getenv("AMESH_SDK_LIVE_FLOW", "hello_world"),
        inputs={"name": "Python SDK"},
    )
    execution_id = str(launched.execution.execution_id)
    completed = client.wait(execution_id, timeout_seconds=90, poll_seconds=0.25)
    assert completed.execution.state.value == "SUCCESS"
    assert client.get(execution_id).execution.execution_id == launched.execution.execution_id
    assert isinstance(client.logs(execution_id), list)
    assert isinstance(client.artifacts(execution_id), list)
