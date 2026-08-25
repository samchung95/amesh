from __future__ import annotations

import json
from typing import Any, ClassVar

import httpx

from amesh.cli import main


class _Client:
    request: ClassVar[tuple[str, dict[str, Any]] | None] = None

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> _Client:
        return self

    def __exit__(self, *args: object) -> None:
        del args

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).request = (path, kwargs["params"])
        return httpx.Response(
            200,
            request=httpx.Request("GET", path),
            json={
                "schemaVersion": "1.0",
                "executionId": "execution-1",
                "bundleDigest": "sha256:" + "a" * 64,
                "section": "trace",
                "items": [],
                "nextCursor": None,
                "limit": 2,
                "total": 0,
            },
        )


def test_evidence_cli_retrieves_and_verifies_page(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setattr(httpx, "Client", _Client)

    exit_code = main(
        [
            "--token",
            "test-token",
            "--tenant",
            "default",
            "--output",
            "json",
            "evidence",
            "execution-1",
            "--limit",
            "2",
            "--verify",
        ]
    )

    assert exit_code == 0
    assert _Client.request == (
        "/api/v1/executions/execution-1/evidence-bundle",
        {"section": "trace", "limit": 2},
    )
    assert json.loads(capsys.readouterr().out)["verified"] is True
