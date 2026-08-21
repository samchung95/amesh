from __future__ import annotations

from typing import Any

import httpx

from amesh.cli import main


class FakeClient:
    last_json: dict[str, Any] | None = None
    last_params: dict[str, Any] | None = None

    def __init__(self, **kwargs: Any) -> None:
        assert kwargs["base_url"] == "http://amesh.test"
        assert kwargs["headers"] == {
            "authorization": "Bearer test-token",
            "x-amesh-tenant": "tenant-a",
        }

    def __enter__(self) -> FakeClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        assert path == "/api/v1/executions"
        FakeClient.last_json = kwargs["json"]
        return httpx.Response(
            200,
            request=httpx.Request("POST", f"http://amesh.test{path}"),
            json={"execution": {"state": "SUCCESS"}, "taskRuns": []},
        )

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        assert path == "/api/v1/executions"
        FakeClient.last_params = kwargs["params"]
        return httpx.Response(
            200,
            request=httpx.Request("GET", f"http://amesh.test{path}"),
            json=[],
        )


def test_run_command_calls_execution_api(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setattr(httpx, "Client", FakeClient)

    exit_code = main(
        [
            "--api-url",
            "http://amesh.test",
            "--token",
            "test-token",
            "--tenant",
            "tenant-a",
            "run",
            "examples.mvp",
            "agent_shell_http",
            "--runner",
            "kubernetes",
            "--input",
            "topic=durability",
        ]
    )

    assert exit_code == 0
    assert FakeClient.last_json == {
        "namespace": "examples.mvp",
        "flowId": "agent_shell_http",
        "inputs": {"topic": "durability"},
        "runner": "kubernetes",
        "idempotencyKey": None,
    }
    assert '"state": "SUCCESS"' in capsys.readouterr().out


def test_executions_command_lists_executions(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setattr(httpx, "Client", FakeClient)

    exit_code = main(
        [
            "--api-url",
            "http://amesh.test",
            "--token",
            "test-token",
            "--tenant",
            "tenant-a",
            "executions",
            "--limit",
            "25",
        ]
    )

    assert exit_code == 0
    assert FakeClient.last_params == {"limit": 25}
    assert capsys.readouterr().out.strip() == "[]"
