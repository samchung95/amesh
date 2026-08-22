from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import shutil
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import gettempdir
from typing import cast

from amesh.executor.contracts import TaskArtifactRecord, TaskFileReference
from amesh.ports import ObjectStore

_CHUNK_BYTES = 64 * 1024
_MARKER_NAME = ".amesh-inputs.json"


class WorkingDirectoryError(RuntimeError):
    """Raised when a task workspace cannot be prepared or collected safely."""


class WorkingDirectoryQuotaError(WorkingDirectoryError):
    """Raised before workspace bytes can exceed the task's declared quota."""


@dataclass(frozen=True)
class PreparedWorkingDirectory:
    path: Path
    shared: bool
    source_uris: tuple[str, ...]


@dataclass(frozen=True)
class WorkspaceCollection:
    artifacts: tuple[TaskArtifactRecord, ...]
    output_files: Mapping[str, str]


class WorkingDirectoryManager:
    """Own bounded local workspaces and streamed object-storage transfer for task attempts."""

    def __init__(self, object_store: ObjectStore | None, *, root: Path | None = None) -> None:
        self._object_store = object_store
        self._root = (root or Path(gettempdir()) / "amesh-workspaces").resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self._source_uris: dict[Path, tuple[str, ...]] = {}

    async def prepare(
        self,
        *,
        tenant_id: str,
        execution_id: str,
        task_run_id: str,
        attempt_id: str,
        scope_id: str | None,
        input_files: Mapping[str, str],
        file_references: Mapping[str, TaskFileReference],
        quota_bytes: int,
    ) -> PreparedWorkingDirectory:
        shared = scope_id is not None
        workspace = self._workspace_path(
            tenant_id=tenant_id,
            execution_id=execution_id,
            task_run_id=task_run_id,
            attempt_id=attempt_id,
            scope_id=scope_id,
        )
        if not shared and workspace.exists():
            self.cleanup(workspace)
        workspace.mkdir(parents=True, exist_ok=shared)
        await self._materialize_inputs(
            workspace,
            tenant_id=tenant_id,
            input_files=input_files,
            file_references=file_references,
            quota_bytes=quota_bytes,
        )
        sources = tuple(
            dict.fromkeys((*self._source_uris.get(workspace, ()), *input_files.values()))
        )
        self._source_uris[workspace] = sources
        return PreparedWorkingDirectory(
            path=workspace,
            shared=shared,
            source_uris=sources,
        )

    async def collect(
        self,
        workspace: PreparedWorkingDirectory,
        *,
        tenant_id: str,
        execution_id: str,
        task_run_id: str,
        attempt: int,
        patterns: Sequence[str],
        manifest_path: str | None,
        quota_bytes: int,
    ) -> WorkspaceCollection:
        if not patterns and manifest_path is None:
            self._enforce_workspace_quota(workspace.path, quota_bytes)
            return WorkspaceCollection(artifacts=(), output_files={})
        if self._object_store is None:
            raise WorkingDirectoryError("declared output files require an object store")

        selected = self._select_outputs(
            workspace.path,
            patterns=patterns,
            manifest_path=manifest_path,
        )
        self._enforce_workspace_quota(workspace.path, quota_bytes)
        uploaded: list[TaskArtifactRecord] = []
        try:
            for logical_path, local_path in selected:
                key = (
                    f"execution-files/{execution_id}/{task_run_id}/"
                    f"attempt-{attempt}/{logical_path}"
                )
                metadata = await self._object_store.put(
                    tenant_id,
                    key,
                    _file_chunks(local_path),
                    content_type=mimetypes.guess_type(logical_path)[0],
                )
                lineage = tuple(
                    dict.fromkeys(
                        (
                            *workspace.source_uris,
                            f"execution:{execution_id}",
                            f"task-run:{task_run_id}:attempt:{attempt}",
                            f"workspace-path:{logical_path}",
                        )
                    )
                )
                uploaded.append(
                    TaskArtifactRecord(
                        uri=metadata.uri,
                        sizeBytes=metadata.size,
                        mediaType=metadata.content_type,
                        checksumSha256=metadata.checksum_sha256,
                        logicalPath=logical_path,
                        lineage=lineage,
                    )
                )
        except Exception:
            for artifact in uploaded:
                await self._object_store.delete(tenant_id, artifact.uri)
            raise
        return WorkspaceCollection(
            artifacts=tuple(uploaded),
            output_files={
                artifact.logical_path or artifact.uri: artifact.uri for artifact in uploaded
            },
        )

    async def retain_failure_diagnostics(
        self,
        workspace: PreparedWorkingDirectory,
        *,
        tenant_id: str,
        execution_id: str,
        task_run_id: str,
        attempt: int,
        details: Mapping[str, object],
        quota_bytes: int,
    ) -> TaskArtifactRecord:
        if self._object_store is None:
            raise WorkingDirectoryError("failure diagnostics require an object store")
        inventory = self._workspace_inventory(workspace.path)
        self._enforce_workspace_quota(workspace.path, quota_bytes)
        payload = json.dumps(
            {"schemaVersion": "amesh.workspace-diagnostics/v1", "files": inventory, **details},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        if len(payload) > min(quota_bytes, 1_048_576):
            raise WorkingDirectoryQuotaError("workspace diagnostics exceed the configured quota")

        async def chunks() -> AsyncIterator[bytes]:
            yield payload

        logical_path = ".amesh/diagnostics.json"
        metadata = await self._object_store.put(
            tenant_id,
            (
                f"execution-files/{execution_id}/{task_run_id}/"
                f"attempt-{attempt}/diagnostics.json"
            ),
            chunks(),
            content_type="application/json",
        )
        return TaskArtifactRecord(
            uri=metadata.uri,
            sizeBytes=metadata.size,
            mediaType=metadata.content_type,
            checksumSha256=metadata.checksum_sha256,
            logicalPath=logical_path,
            lineage=tuple(
                dict.fromkeys(
                    (
                        *workspace.source_uris,
                        f"execution:{execution_id}",
                        f"task-run:{task_run_id}:attempt:{attempt}",
                        "workspace-diagnostics",
                    )
                )
            ),
        )

    def cleanup(self, workspace: Path) -> None:
        resolved = workspace.resolve(strict=False)
        if not resolved.is_relative_to(self._root) or resolved == self._root:
            raise WorkingDirectoryError("refusing to clean a path outside the workspace root")
        if resolved.exists():
            shutil.rmtree(resolved)
        self._source_uris.pop(resolved, None)

    def _workspace_path(
        self,
        *,
        tenant_id: str,
        execution_id: str,
        task_run_id: str,
        attempt_id: str,
        scope_id: str | None,
    ) -> Path:
        tenant_key = hashlib.sha256(tenant_id.encode("utf-8")).hexdigest()[:16]
        execution_key = hashlib.sha256(execution_id.encode("utf-8")).hexdigest()[:24]
        if scope_id is not None:
            leaf = "shared-" + hashlib.sha256(scope_id.encode("utf-8")).hexdigest()[:24]
        else:
            task_key = hashlib.sha256(task_run_id.encode("utf-8")).hexdigest()[:24]
            attempt_key = hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()[:24]
            leaf = f"attempt-{task_key}-{attempt_key}"
        return self._root / tenant_key / execution_key / leaf

    async def _materialize_inputs(
        self,
        workspace: Path,
        *,
        tenant_id: str,
        input_files: Mapping[str, str],
        file_references: Mapping[str, TaskFileReference],
        quota_bytes: int,
    ) -> None:
        if not input_files:
            return
        if self._object_store is None:
            raise WorkingDirectoryError("declared input files require an object store")
        marker_path = workspace / _MARKER_NAME
        marker = self._read_marker(marker_path)
        current_size = sum(
            cast(int, item["sizeBytes"]) for item in self._workspace_inventory(workspace)
        )
        projected_size = sum(
            reference.size_bytes
            for path, reference in file_references.items()
            if path not in marker
        )
        if current_size + projected_size > quota_bytes:
            raise WorkingDirectoryQuotaError(
                "declared input files exceed the configured workspace quota"
            )

        for logical_path, uri in input_files.items():
            reference = file_references.get(logical_path)
            if reference is None:
                reference = await self._head_reference(tenant_id, uri)
            if reference.uri != uri:
                raise WorkingDirectoryError(
                    f"input metadata for {logical_path!r} belongs to another object"
                )
            previous = marker.get(logical_path)
            if previous is not None:
                if previous != reference.checksum_sha256:
                    raise WorkingDirectoryError(
                        f"shared input {logical_path!r} changed during the execution"
                    )
                continue
            if current_size + reference.size_bytes > quota_bytes:
                raise WorkingDirectoryQuotaError(
                    f"input {logical_path!r} exceeds the configured workspace quota"
                )
            target = _safe_target(workspace, logical_path)
            if target.exists():
                raise WorkingDirectoryError(
                    f"input {logical_path!r} would overwrite an existing workspace file"
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f".{target.name}.amesh-part")
            digest = hashlib.sha256()
            size = 0
            try:
                with temporary.open("xb") as stream:
                    async for chunk in self._object_store.get(tenant_id, uri):
                        size += len(chunk)
                        if current_size + size > quota_bytes:
                            raise WorkingDirectoryQuotaError(
                                f"input {logical_path!r} exceeds the configured workspace quota"
                            )
                        digest.update(chunk)
                        stream.write(chunk)
                if size != reference.size_bytes or digest.hexdigest() != reference.checksum_sha256:
                    raise WorkingDirectoryError(
                        f"checksum verification failed for input {logical_path!r}"
                    )
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
            marker[logical_path] = reference.checksum_sha256
            current_size += size
        marker_path.write_text(
            json.dumps(marker, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        self._enforce_workspace_quota(workspace, quota_bytes)

    async def _head_reference(self, tenant_id: str, uri: str) -> TaskFileReference:
        head = getattr(self._object_store, "head", None)
        if head is None:
            raise WorkingDirectoryError("input object checksum metadata is unavailable")
        metadata = await head(tenant_id, uri)
        return TaskFileReference(
            uri=metadata.uri,
            sizeBytes=metadata.size,
            checksumSha256=metadata.checksum_sha256,
        )

    @staticmethod
    def _read_marker(path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in payload.items()
        ):
            raise WorkingDirectoryError("workspace input marker is invalid")
        return payload

    def _select_outputs(
        self,
        workspace: Path,
        *,
        patterns: Sequence[str],
        manifest_path: str | None,
    ) -> tuple[tuple[str, Path], ...]:
        requested = list(patterns)
        if manifest_path is not None:
            manifest = _safe_target(workspace, manifest_path)
            if not manifest.is_file() or manifest.is_symlink():
                raise WorkingDirectoryError("output manifest is missing or unsafe")
            if manifest.stat().st_size > 1_048_576:
                raise WorkingDirectoryError("output manifest exceeds 1 MiB")
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
                raise WorkingDirectoryError("output manifest must be a JSON array of paths")
            requested.extend(payload)

        selected: dict[str, Path] = {}
        for pattern in requested:
            _validate_relative_path(pattern, allow_glob=True)
            matches = sorted(workspace.glob(pattern))
            has_glob = any(character in pattern for character in "*?[]")
            if not matches and not has_glob:
                raise WorkingDirectoryError(f"declared output file {pattern!r} does not exist")
            for candidate in matches:
                logical_path = candidate.relative_to(workspace).as_posix()
                if logical_path == _MARKER_NAME:
                    continue
                safe = _safe_existing_file(workspace, candidate)
                selected[logical_path] = safe
        return tuple(sorted(selected.items()))

    def _enforce_workspace_quota(self, workspace: Path, quota_bytes: int) -> None:
        total = sum(cast(int, item["sizeBytes"]) for item in self._workspace_inventory(workspace))
        if total > quota_bytes:
            raise WorkingDirectoryQuotaError(
                f"workspace contains {total} bytes; quota is {quota_bytes}"
            )

    @staticmethod
    def _workspace_inventory(workspace: Path) -> list[dict[str, object]]:
        inventory: list[dict[str, object]] = []
        for candidate in sorted(workspace.rglob("*")):
            relative = candidate.relative_to(workspace).as_posix()
            if relative == _MARKER_NAME:
                continue
            if candidate.is_symlink():
                raise WorkingDirectoryError(f"workspace symlink is not allowed: {relative}")
            if candidate.is_file():
                inventory.append({"path": relative, "sizeBytes": candidate.stat().st_size})
        return inventory


def _validate_relative_path(value: str, *, allow_glob: bool) -> PurePosixPath:
    if not value or len(value) > 4096 or "\\" in value or value.startswith("/"):
        raise WorkingDirectoryError("workspace paths must use bounded relative POSIX syntax")
    path = PurePosixPath(value)
    if not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise WorkingDirectoryError("workspace paths cannot traverse their assigned root")
    if ":" in path.parts[0]:
        raise WorkingDirectoryError("workspace paths cannot contain a drive or URI scheme")
    if not allow_glob and any(character in value for character in "*?[]"):
        raise WorkingDirectoryError("workspace input paths cannot contain glob syntax")
    return path


def _safe_target(root: Path, logical_path: str) -> Path:
    relative = _validate_relative_path(logical_path, allow_glob=False)
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise WorkingDirectoryError(f"workspace parent is a symlink: {logical_path}")
    candidate = root.joinpath(*relative.parts)
    if candidate.exists() and candidate.is_symlink():
        raise WorkingDirectoryError(f"workspace file is a symlink: {logical_path}")
    if not candidate.resolve(strict=False).is_relative_to(root.resolve()):
        raise WorkingDirectoryError("workspace path escapes its assigned root")
    return candidate


def _safe_existing_file(root: Path, candidate: Path) -> Path:
    relative = candidate.relative_to(root).as_posix()
    safe = _safe_target(root, relative)
    if not safe.is_file():
        raise WorkingDirectoryError(f"declared output is not a regular file: {relative}")
    return safe


async def _file_chunks(path: Path) -> AsyncIterator[bytes]:
    with path.open("rb") as stream:
        while chunk := stream.read(_CHUNK_BYTES):
            yield chunk
