from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

import httpx

from amesh.cli import EXIT_ERROR, EXIT_SUCCESS, main

SESSION_ID = "018f47f4-a289-7c7e-9f0b-61dcf6e7d900"
EXECUTION_ID = "018f47f4-a289-7c7e-9f0b-61dcf6e7d901"
TASK_RUN_ID = "018f47f4-a289-7c7e-9f0b-61dcf6e7d902"


def _response(
    method: str,
    path: str,
    payload: object,
    *,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    return httpx.Response(
        status_code,
        request=httpx.Request(method, f"http://amesh.test{path}"),
        json=payload,
        headers=headers,
    )


class SessionClient:
    calls: ClassVar[list[tuple[str, str, dict[str, Any]]]] = []

    def __init__(self, **kwargs: Any) -> None:
        assert kwargs == {
            "base_url": "http://amesh.test",
            "headers": {
                "authorization": "Bearer test-token",
                "x-amesh-tenant": "tenant-a",
            },
            "timeout": 120,
        }

    def __enter__(self) -> SessionClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).calls.append(("POST", path, kwargs))
        return _response(
            "POST",
            path,
            {
                "sessionId": SESSION_ID,
                "executionId": EXECUTION_ID,
                "taskRunId": TASK_RUN_ID,
                "attempt": 1,
                "executionState": "RUNNING",
                "session": None,
            },
            status_code=202 if kwargs.get("headers", {}).get("Prefer") else 200,
            headers={
                "Location": f"/api/v1/agent-sessions/{SESSION_ID}",
                **(
                    {"Preference-Applied": "respond-async"}
                    if kwargs.get("headers", {}).get("Prefer")
                    else {}
                ),
            },
        )

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).calls.append(("GET", path, kwargs))
        if path == f"/api/v1/agent-sessions/{SESSION_ID}":
            return _response(
                "GET",
                path,
                {
                    "session": {
                        "sessionId": SESSION_ID,
                        "executionId": EXECUTION_ID,
                        "version": 4,
                    },
                    "events": [],
                    "nextEventIndex": None,
                },
            )
        if path.endswith("/result"):
            return _response(
                "GET",
                path,
                {"sessionId": SESSION_ID, "state": "SUCCEEDED", "result": {"ok": True}},
            )
        if path.endswith("/events"):
            return _response(
                "GET",
                path,
                {"session": {"sessionId": SESSION_ID}, "events": []},
            )
        if path == "/api/v1/agent-sessions":
            return _response("GET", path, [])
        raise AssertionError(f"unexpected GET {path}")


def _base_arguments() -> list[str]:
    return [
        "--api-url",
        "http://amesh.test",
        "--token",
        "test-token",
        "--tenant",
        "tenant-a",
    ]


def test_session_create_accepts_inline_json_and_reports_location(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    SessionClient.calls.clear()
    monkeypatch.setattr(httpx, "Client", SessionClient)

    exit_code = main(
        [
            *_base_arguments(),
            "session",
            "create",
            "agents.demo",
            "researcher",
            "--agent-revision",
            "3",
            "--input-json",
            '{"question":"Why now?"}',
            "--idempotency-key",
            "request-42",
            "--prefer-async",
        ]
    )

    assert exit_code == EXIT_SUCCESS
    assert SessionClient.calls == [
        (
            "POST",
            "/api/v1/agent-sessions",
            {
                "json": {
                    "namespace": "agents.demo",
                    "agent": "researcher",
                    "agentRevision": 3,
                    "input": {"question": "Why now?"},
                    "invalidOutputPolicy": "FAIL",
                    "maxRepairAttempts": 0,
                    "dataHandling": "DENY_SECRETS",
                    "memoryReadKeys": [],
                    "runner": "local",
                },
                "headers": {
                    "Idempotency-Key": "request-42",
                    "Prefer": "respond-async",
                },
            },
        )
    ]
    output = json.loads(capsys.readouterr().out)
    assert output["sessionId"] == SESSION_ID
    assert output["location"] == f"/api/v1/agent-sessions/{SESSION_ID}"
    assert output["preferenceApplied"] == "respond-async"


def test_session_create_accepts_json_input_file(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    SessionClient.calls.clear()
    monkeypatch.setattr(httpx, "Client", SessionClient)
    input_path = tmp_path / "input.json"
    input_path.write_text('{"topic":"durability 🧪"}', encoding="utf-8")

    assert (
        main(
            [
                *_base_arguments(),
                "session",
                "create",
                "agents.demo",
                "researcher",
                "--agent-revision",
                "3",
                "--input-file",
                str(input_path),
                "--memory-read-key",
                "customer-context",
                "--timeout-seconds",
                "90",
            ]
        )
        == EXIT_SUCCESS
    )

    request = SessionClient.calls[0][2]
    assert request["json"]["input"] == {"topic": "durability 🧪"}
    assert request["json"]["memoryReadKeys"] == ["customer-context"]
    assert request["json"]["timeoutSeconds"] == 90.0
    assert "headers" not in request


def test_session_create_rejects_non_object_json_before_request(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    SessionClient.calls.clear()
    monkeypatch.setattr(httpx, "Client", SessionClient)

    assert (
        main(
            [
                *_base_arguments(),
                "session",
                "create",
                "agents.demo",
                "researcher",
                "--agent-revision",
                "3",
                "--input-json",
                "[]",
            ]
        )
        == EXIT_ERROR
    )

    assert SessionClient.calls == []
    assert "must be a JSON object" in capsys.readouterr().err


def test_session_read_commands_use_bounded_canonical_routes(monkeypatch: Any) -> None:
    SessionClient.calls.clear()
    monkeypatch.setattr(httpx, "Client", SessionClient)

    assert main([*_base_arguments(), "session", "list", "--limit", "25"]) == EXIT_SUCCESS
    assert (
        main(
            [
                *_base_arguments(),
                "session",
                "get",
                SESSION_ID,
                "--after-event-index",
                "10",
                "--limit",
                "5",
            ]
        )
        == EXIT_SUCCESS
    )
    assert (
        main(
            [
                *_base_arguments(),
                "session",
                "events",
                SESSION_ID,
                "--after-event-index",
                "15",
                "--limit",
                "10",
            ]
        )
        == EXIT_SUCCESS
    )
    assert main([*_base_arguments(), "session", "result", SESSION_ID]) == EXIT_SUCCESS

    assert SessionClient.calls == [
        ("GET", "/api/v1/agent-sessions", {"params": {"limit": 25}}),
        (
            "GET",
            f"/api/v1/agent-sessions/{SESSION_ID}",
            {"params": {"afterEventIndex": 10, "limit": 5}},
        ),
        (
            "GET",
            f"/api/v1/agent-sessions/{SESSION_ID}/events",
            {"params": {"afterEventIndex": 15, "limit": 10}},
        ),
        ("GET", f"/api/v1/agent-sessions/{SESSION_ID}/result", {}),
    ]


def test_session_control_supports_optional_optimistic_fences(monkeypatch: Any) -> None:
    SessionClient.calls.clear()
    monkeypatch.setattr(httpx, "Client", SessionClient)

    assert (
        main(
            [
                *_base_arguments(),
                "session",
                "cancel",
                SESSION_ID,
                "--expected-version",
                "8",
                "--expected-epoch",
                "4",
                "--reason",
                "operator cancellation",
            ]
        )
        == EXIT_SUCCESS
    )
    assert (
        main(
            [
                *_base_arguments(),
                "session",
                "pause",
                SESSION_ID,
                "--reason",
                "hold for operator review",
            ]
        )
        == EXIT_SUCCESS
    )

    assert SessionClient.calls == [
        (
            "POST",
            f"/api/v1/agent-sessions/{SESSION_ID}/cancel",
            {
                "json": {
                    "expectedVersion": 8,
                    "expectedEpoch": 4,
                    "reason": "operator cancellation",
                    "graceSeconds": 30,
                }
            },
        ),
        (
            "POST",
            f"/api/v1/agent-sessions/{SESSION_ID}/pause",
            {
                "json": {
                    "reason": "hold for operator review",
                    "graceSeconds": 30,
                }
            },
        ),
    ]
