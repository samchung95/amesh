from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import httpx
import yaml

from amesh.cli import EXIT_CONFIRMATION_REQUIRED, EXIT_SUCCESS, main


class UpgradeClient:
    posts: ClassVar[list[tuple[str, dict[str, Any]]]] = []

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> UpgradeClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        del kwargs
        assert path == "/api/v1/upgrades/events/upcast"
        return httpx.Response(
            200,
            request=httpx.Request("GET", path),
            json={
                "eligibleEvents": 3,
                "migratedEvents": 0,
                "remainingEvents": 3,
                "confirmationPhrase": "UPCAST 3",
                "applied": False,
                "evidenceEventId": None,
            },
        )

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        payload = kwargs["json"]
        self.posts.append((path, payload))
        if path.endswith("/events/upcast"):
            body = {
                "eligibleEvents": 3,
                "migratedEvents": 3,
                "remainingEvents": 0,
                "confirmationPhrase": "UPCAST 3",
                "applied": True,
                "evidenceEventId": "01991b1e-cc00-7000-8000-000000000001",
            }
        else:
            body = {
                "kind": payload["kind"],
                "targetVersion": payload["targetVersion"],
                "changed": True,
                "canonical": {
                    "id": "upgrade",
                    "namespace": "tests.upgrade",
                    "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
                },
                "warnings": [],
            }
        return httpx.Response(200, request=httpx.Request("POST", path), json=body)


def test_upgrade_event_upcast_requires_force_and_uses_exact_preview(
    monkeypatch: Any,
) -> None:
    UpgradeClient.posts.clear()
    monkeypatch.setattr(httpx, "Client", UpgradeClient)

    assert (
        main(["--token", "test", "upgrade", "events-upcast", "--reason", "lts migration"])
        == EXIT_CONFIRMATION_REQUIRED
    )
    assert UpgradeClient.posts == []

    assert (
        main(
            [
                "--token",
                "test",
                "upgrade",
                "events-upcast",
                "--reason",
                "lts migration",
                "--batch-size",
                "25",
                "--force",
            ]
        )
        == EXIT_SUCCESS
    )
    assert UpgradeClient.posts == [
        (
            "/api/v1/upgrades/events/upcast",
            {
                "confirmation": "UPCAST 3",
                "reason": "lts migration",
                "batchSize": 25,
            },
        )
    ]


def test_upgrade_configuration_migration_writes_canonical_output(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    UpgradeClient.posts.clear()
    monkeypatch.setattr(httpx, "Client", UpgradeClient)
    source = tmp_path / "flow.yaml"
    target = tmp_path / "canonical.yaml"
    source.write_text(
        "id: upgrade\nnamespace: tests.upgrade\ntasks: []\n",
        encoding="utf-8",
    )

    assert (
        main(
            [
                "--token",
                "test",
                "upgrade",
                "migrate-config",
                "flow",
                str(source),
                "--target-version",
                "0.2.0",
                "--output",
                str(target),
            ]
        )
        == EXIT_SUCCESS
    )
    assert yaml.safe_load(target.read_text(encoding="utf-8"))["id"] == "upgrade"
    assert UpgradeClient.posts[0][0] == "/api/v1/upgrades/configuration/migrate"
