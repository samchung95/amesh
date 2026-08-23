from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

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


class FakeFlowTestClient:
    request: ClassVar[tuple[str, dict[str, Any], dict[str, Any]] | None] = None

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> FakeFlowTestClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).request = (path, kwargs["params"], kwargs["json"])
        return httpx.Response(
            200,
            request=httpx.Request("POST", path),
            json={
                "outcome": "FAILED",
                "cases": [{"testId": "branch-a"}],
                "coverage": {"percentage": 75.0},
            },
        )


def test_flow_test_command_is_machine_readable_and_ci_fails(monkeypatch: Any) -> None:
    monkeypatch.setattr(httpx, "Client", FakeFlowTestClient)

    exit_code = main(
        [
            "--token",
            "test-token",
            "--output",
            "json",
            "flow",
            "test",
            "examples",
            "approval",
            "--revision",
            "3",
            "--test-id",
            "branch-a",
            "--fail-fast",
        ]
    )

    assert exit_code == 1
    assert FakeFlowTestClient.request == (
        "/api/v1/flows/examples/approval/tests/runs",
        {"revision": 3},
        {"testIds": ["branch-a"], "failFast": True},
    )


class FakeSimulationClient:
    request: ClassVar[tuple[str, dict[str, Any]] | None] = None

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> FakeSimulationClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).request = (path, kwargs["json"])
        return httpx.Response(
            200,
            request=httpx.Request("POST", path),
            json={"planId": "plan-1", "sideEffectsSuppressed": True},
        )


def test_flow_simulation_command_sends_declared_context_and_models(monkeypatch: Any) -> None:
    monkeypatch.setattr(httpx, "Client", FakeSimulationClient)

    exit_code = main(
        [
            "--token",
            "test-token",
            "flow",
            "simulate",
            "examples",
            "forecast",
            "--revision",
            "4",
            "--input",
            "customer=acme",
            "--trigger",
            "kind=primary",
            "--fixture",
            'lookup={source: MOCK, output: {status: approved}}',
            "--estimate-model",
            'vendor.lookup={durationSeconds: 0.5, apiCalls: 1}',
        ]
    )

    assert exit_code == 0
    assert FakeSimulationClient.request == (
        "/api/v1/flows/examples/forecast/revisions/4/simulate",
        {
            "inputs": {"customer": "acme"},
            "variables": {},
            "triggerContext": {"kind": "primary"},
            "fixtures": {"lookup": {"source": "MOCK", "output": {"status": "approved"}}},
            "estimateModels": {
                "vendor.lookup": {"durationSeconds": 0.5, "apiCalls": 1}
            },
            "defaultRunner": "kubernetes",
            "signEvidence": True,
        },
    )


class FakeNamespaceClient:
    calls: ClassVar[list[tuple[str, str, dict[str, Any]]]] = []

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> FakeNamespaceClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        self.calls.append(("PUT", path, kwargs))
        return httpx.Response(200, request=httpx.Request("PUT", path), json={"version": 1})

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        self.calls.append(("GET", path, kwargs))
        return httpx.Response(200, request=httpx.Request("GET", path), content=b"rules")


def test_namespace_file_cli_uploads_and_downloads(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    FakeNamespaceClient.calls.clear()
    monkeypatch.setattr(httpx, "Client", FakeNamespaceClient)
    source = tmp_path / "rules.txt"
    source.write_bytes(b"rules")
    destination = tmp_path / "downloaded.txt"

    assert (
        main(
            [
                "namespace",
                "files",
                "upload",
                "team/data",
                "config/rules.txt",
                str(source),
                "--content-type",
                "text/plain",
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "namespace",
                "files",
                "download",
                "team/data",
                "config/rules.txt",
                str(destination),
                "--version",
                "1",
            ]
        )
        == 0
    )

    assert destination.read_bytes() == b"rules"
    assert FakeNamespaceClient.calls[0] == (
        "PUT",
        "/api/v1/namespaces/team%2Fdata/files/config/rules.txt",
        {
            "params": None,
            "content": b"rules",
            "headers": {"content-type": "text/plain"},
        },
    )
    assert FakeNamespaceClient.calls[1] == (
        "GET",
        "/api/v1/namespaces/team%2Fdata/files/config/rules.txt",
        {"params": {"version": 1}},
    )


class FakeLifecycleClient:
    posts: ClassVar[list[tuple[str, dict[str, Any]]]] = []

    def __init__(self, **kwargs: Any) -> None:
        del kwargs

    def __enter__(self) -> FakeLifecycleClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        del kwargs
        assert path == "/api/v1/lifecycle/jobs/job-608"
        return httpx.Response(
            200,
            request=httpx.Request("GET", path),
            json={
                "id": "job-608",
                "policySnapshot": {"scope": "TENANT", "resourceType": "LOG"},
                "estimatedRecords": 12,
                "estimatedBytes": 4096,
                "protectedRecords": 2,
                "activeRecords": 1,
                "confirmationPhrase": "PURGE 12",
            },
        )

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        type(self).posts.append((path, kwargs["json"]))
        return httpx.Response(200, request=httpx.Request("POST", path), json={"state": "READY"})


def test_lifecycle_cli_previews_destructive_impact_before_force(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    FakeLifecycleClient.posts.clear()
    monkeypatch.setattr(httpx, "Client", FakeLifecycleClient)

    assert main(["lifecycle", "execute", "job-608"]) == 3
    preview = capsys.readouterr().out
    assert '"affectedRecords": 12' in preview
    assert '"requiredFlag": "--force"' in preview
    assert main(["lifecycle", "execute", "job-608", "--force"]) == 0
    assert FakeLifecycleClient.posts == [
        (
            "/api/v1/lifecycle/jobs/job-608/execute",
            {"confirmation": "PURGE 12"},
        )
    ]


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
