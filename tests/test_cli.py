from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from amesh.cli import main
from amesh.ports import StorageBackend, StorageMigrationCheckpoint
from amesh.storage import StorageValidationReport


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


class FakeStorage:
    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend

    async def validate_inventory(
        self, tenant_id: str, *, verify_content: bool
    ) -> StorageValidationReport:
        assert tenant_id == "tenant-a"
        assert verify_content
        return StorageValidationReport(
            backend=self.backend.value,
            objects=2,
            bytes=10,
            verified=2,
        )

    async def migrate_to(
        self,
        destination: FakeStorage,
        tenant_id: str,
        *,
        checkpoint: StorageMigrationCheckpoint | None,
        write_checkpoint: Any,
    ) -> StorageMigrationCheckpoint:
        assert tenant_id == "tenant-a"
        assert checkpoint is None
        result = StorageMigrationCheckpoint(
            source_backend=self.backend,
            destination_backend=destination.backend,
            last_key="item.bin",
            objects_copied=1,
            bytes_copied=10,
            complete=True,
        )
        await write_checkpoint(result)
        return result


def test_storage_cli_validates_and_persists_migration_checkpoint(
    monkeypatch: Any,
    capsys: Any,
    tmp_path: Path,
) -> None:
    def fake_build(settings: Any) -> FakeStorage:
        return FakeStorage(StorageBackend(settings.object_storage_backend))

    monkeypatch.setattr("amesh.cli.build_object_store", fake_build)
    assert main(["--tenant", "tenant-a", "storage", "validate"]) == 0
    assert '"verified": 2' in capsys.readouterr().out

    destination = tmp_path / "destination.json"
    destination.write_text(
        json.dumps(
            {
                "object_storage_backend": "azure",
                "object_storage_azure_account_url": "https://account.blob.core.windows.net",
                "object_storage_workload_identity": True,
            }
        ),
        encoding="utf-8",
    )
    checkpoint = tmp_path / "migration-checkpoint.json"
    assert (
        main(
            [
                "--tenant",
                "tenant-a",
                "storage",
                "migrate",
                str(destination),
                "--checkpoint",
                str(checkpoint),
            ]
        )
        == 0
    )
    saved = StorageMigrationCheckpoint.model_validate_json(checkpoint.read_text(encoding="utf-8"))
    assert saved.complete and saved.destination_backend is StorageBackend.AZURE
