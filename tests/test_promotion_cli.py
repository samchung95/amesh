from __future__ import annotations

from typing import Any, ClassVar

import httpx

from amesh.cli import main


class FakeReleaseClient:
    request: ClassVar[tuple[str, dict[str, Any]] | None] = None

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> FakeReleaseClient:
        return self

    def __exit__(self, *args: object) -> None:
        del args

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).request = (path, kwargs.get("json", {}))
        return httpx.Response(200, request=httpx.Request("POST", path), json={"passed": True})

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).request = (path, kwargs)
        return httpx.Response(200, request=httpx.Request("GET", path), json={"state": "ACTIVE"})


def test_release_preview_cli_uses_provider_neutral_endpoint(monkeypatch: Any) -> None:
    monkeypatch.setattr("amesh.cli.httpx.Client", FakeReleaseClient)

    exit_code = main(
        [
            "--api-url",
            "http://amesh.test",
            "--token",
            "test-token",
            "--tenant",
            "tenant-a",
            "releases",
            "preview",
            "00000000-0000-7000-8000-000000000001",
        ]
    )

    assert exit_code == 0
    assert FakeReleaseClient.request == (
        "/api/v1/releases/policies/00000000-0000-7000-8000-000000000001/preview",
        {},
    )


def test_release_rollback_cli_sends_optimistic_concurrency_fields(monkeypatch: Any) -> None:
    monkeypatch.setattr("amesh.cli.httpx.Client", FakeReleaseClient)

    exit_code = main(
        [
            "--api-url",
            "http://amesh.test",
            "--token",
            "test-token",
            "--tenant",
            "tenant-a",
            "releases",
            "rollback",
            "WORKFLOW",
            "checkout",
            "--to-revision",
            "3",
            "--expected-version",
            "7",
            "--reason",
            "restore known-good",
        ]
    )

    assert exit_code == 0
    assert FakeReleaseClient.request == (
        "/api/v1/releases/workflow/checkout/rollback",
        {"toRevision": 3, "expectedVersion": 7, "reason": "restore known-good"},
    )
