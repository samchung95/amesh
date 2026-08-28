from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from amesh.executor import TaskFileReference
from amesh.ports import ObjectMetadata, StorageBackend
from amesh.workflow.working_directory import (
    WorkingDirectoryError,
    WorkingDirectoryManager,
    WorkingDirectoryQuotaError,
)


class MemoryObjectStore:
    def __init__(self, objects: dict[str, bytes] | None = None) -> None:
        self.objects = dict(objects or {})
        self.deleted: list[str] = []
        self.fail_suffix: str | None = None

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        if self.fail_suffix is not None and key.endswith(self.fail_suffix):
            raise RuntimeError("injected upload failure")
        content = b"".join([chunk async for chunk in chunks])
        uri = f"s3://memory/{key}"
        self.objects[uri] = content
        return _metadata(tenant_id, uri, content, content_type=content_type)

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        del tenant_id

        async def chunks() -> AsyncIterator[bytes]:
            content = self.objects[uri]
            for start in range(0, len(content), 17):
                yield content[start : start + 17]

        return chunks()

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return _metadata(tenant_id, uri, self.objects[uri])

    async def delete(self, tenant_id: str, uri: str) -> None:
        del tenant_id
        self.deleted.append(uri)
        self.objects.pop(uri, None)


def _metadata(
    tenant_id: str,
    uri: str,
    content: bytes,
    *,
    content_type: str | None = None,
) -> ObjectMetadata:
    return ObjectMetadata(
        uri=uri,
        tenant_id=tenant_id,
        size=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        content_type=content_type,
        key=uri.removeprefix("s3://memory/"),
        backend=StorageBackend.S3,
    )


def test_workspace_streams_verified_inputs_collects_path_glob_and_manifest(tmp_path: Path) -> None:
    async def scenario() -> None:
        source_uri = "s3://memory/source/input.txt"
        source = b"source-bytes" * 20_000
        store = MemoryObjectStore({source_uri: source})
        manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
        reference = TaskFileReference(
            uri=source_uri,
            sizeBytes=len(source),
            checksumSha256=hashlib.sha256(source).hexdigest(),
        )
        first = await manager.prepare(
            tenant_id="default",
            execution_id="execution-1",
            task_run_id="task-1",
            attempt_id="attempt-1",
            scope_id=None,
            input_files={"input/data.txt": source_uri},
            file_references={"input/data.txt": reference},
            quota_bytes=2_000_000,
        )
        second = await manager.prepare(
            tenant_id="default",
            execution_id="execution-1",
            task_run_id="task-1",
            attempt_id="attempt-2",
            scope_id=None,
            input_files={},
            file_references={},
            quota_bytes=2_000_000,
        )
        assert first.path != second.path
        assert (first.path / "input" / "data.txt").read_bytes() == source

        (first.path / "result.txt").write_text("result", encoding="utf-8")
        (first.path / "nested").mkdir()
        (first.path / "nested" / "data.json").write_text("{}", encoding="utf-8")
        (first.path / "outputs.json").write_text(
            json.dumps(["nested/data.json"]),
            encoding="utf-8",
        )
        collected = await manager.collect(
            first,
            tenant_id="default",
            execution_id="execution-1",
            task_run_id="task-1",
            attempt=1,
            patterns=("*.txt",),
            manifest_path="outputs.json",
            quota_bytes=2_000_000,
        )

        assert set(collected.output_files) == {"result.txt", "nested/data.json"}
        assert all(source_uri in artifact.lineage for artifact in collected.artifacts)
        assert store.objects[collected.output_files["result.txt"]] == b"result"
        manager.cleanup(first.path)
        manager.cleanup(second.path)
        assert not first.path.exists()
        assert not second.path.exists()

    asyncio.run(scenario())


def test_workspace_rejects_traversal_symlinks_and_quota_overflow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def scenario() -> None:
        source_uri = "s3://memory/source/large.bin"
        source = b"x" * 1024
        store = MemoryObjectStore({source_uri: source})
        manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
        reference = TaskFileReference(
            uri=source_uri,
            sizeBytes=len(source),
            checksumSha256=hashlib.sha256(source).hexdigest(),
        )
        with pytest.raises(WorkingDirectoryQuotaError):
            await manager.prepare(
                tenant_id="default",
                execution_id="execution-1",
                task_run_id="task-1",
                attempt_id="attempt-1",
                scope_id=None,
                input_files={"large.bin": source_uri},
                file_references={"large.bin": reference},
                quota_bytes=100,
            )

        workspace = await manager.prepare(
            tenant_id="default",
            execution_id="execution-2",
            task_run_id="task-2",
            attempt_id="attempt-2",
            scope_id=None,
            input_files={},
            file_references={},
            quota_bytes=10_000,
        )
        outside = tmp_path / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = workspace.path / "escape.txt"
        try:
            link.symlink_to(outside)
        except OSError:
            link.write_text("simulated link", encoding="utf-8")
            original_is_symlink = Path.is_symlink

            def is_symlink(path: Path) -> bool:
                return path == link or original_is_symlink(path)

            monkeypatch.setattr(Path, "is_symlink", is_symlink)
        with pytest.raises(WorkingDirectoryError, match="symlink"):
            await manager.collect(
                workspace,
                tenant_id="default",
                execution_id="execution-2",
                task_run_id="task-2",
                attempt=1,
                patterns=("escape.txt",),
                manifest_path=None,
                quota_bytes=10_000,
            )
        assert outside.read_text(encoding="utf-8") == "outside"
        manager.cleanup(workspace.path)

    asyncio.run(scenario())


def test_workspace_rolls_back_a_multi_file_upload_when_one_object_fails(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = MemoryObjectStore()
        store.fail_suffix = "second.txt"
        manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
        workspace = await manager.prepare(
            tenant_id="default",
            execution_id="execution-1",
            task_run_id="task-1",
            attempt_id="attempt-1",
            scope_id=None,
            input_files={},
            file_references={},
            quota_bytes=10_000,
        )
        (workspace.path / "first.txt").write_text("first", encoding="utf-8")
        (workspace.path / "second.txt").write_text("second", encoding="utf-8")

        with pytest.raises(RuntimeError, match="injected upload failure"):
            await manager.collect(
                workspace,
                tenant_id="default",
                execution_id="execution-1",
                task_run_id="task-1",
                attempt=1,
                patterns=("*.txt",),
                manifest_path=None,
                quota_bytes=10_000,
            )
        assert len(store.deleted) == 1
        assert not any(uri.endswith("first.txt") for uri in store.objects)
        manager.cleanup(workspace.path)

    asyncio.run(scenario())
