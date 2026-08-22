from __future__ import annotations

import hashlib
import shutil
import stat
import zipfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskHandler
from amesh.workflow.working_directory import WorkingDirectoryManager

_ARCHIVE_ENTRY_LIMIT = 10_000
_ARCHIVE_BYTES_LIMIT = 100 * 1024 * 1024
_ARCHIVE_RATIO_LIMIT = 100


def core_file_handlers(workspace_manager: WorkingDirectoryManager) -> dict[str, TaskHandler]:
    return {
        f"core.files.{operation}": _file_handler(operation, workspace_manager)
        for operation in ("compress", "extract", "checksum", "copy", "move", "delete")
    }


def _file_handler(operation: str, workspace_manager: WorkingDirectoryManager) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        quota = context.workspace_quota_bytes or task.workspace_quota_bytes
        workspace = await workspace_manager.prepare(
            tenant_id=context.tenant_id,
            execution_id=str(context.execution_id),
            task_run_id=str(context.task_run_id),
            attempt_id=str(context.attempt_id),
            scope_id=context.workspace_scope_id,
            input_files=context.files,
            file_references=context.file_references,
            quota_bytes=quota,
        )
        try:
            output = _operate(operation, task, workspace.path)
            collected = await workspace_manager.collect(
                workspace,
                tenant_id=context.tenant_id,
                execution_id=str(context.execution_id),
                task_run_id=str(context.task_run_id),
                attempt=context.attempt,
                patterns=task.output_files,
                manifest_path=task.output_manifest,
                quota_bytes=quota,
            )
            return TaskCompletion(
                output={**output, "outputFiles": dict(collected.output_files)},
                artifacts=collected.artifacts,
            )
        finally:
            if not workspace.shared:
                workspace_manager.cleanup(workspace.path)

    return run


def _operate(operation: str, task: TaskDefinition, root: Path) -> dict[str, Any]:
    extra = task.model_extra or {}
    if operation == "compress":
        return _compress(root, extra)
    source_name = _required_path(extra, "source")
    source = _safe_path(root, source_name, require_exists=True)
    if operation == "extract":
        destination_name = _required_path(extra, "destination")
        destination = _safe_path(root, destination_name)
        return _extract(source, source_name, destination, destination_name, extra)
    if operation == "checksum":
        algorithm = str(extra.get("algorithm", "sha256")).lower()
        if algorithm not in {"sha256", "sha512"}:
            raise ValueError("checksum algorithm must be sha256 or sha512")
        digest = hashlib.new(algorithm)
        with source.open("rb") as stream:
            while chunk := stream.read(64 * 1024):
                digest.update(chunk)
        return {
            "operation": operation,
            "source": source_name,
            "algorithm": algorithm,
            "checksum": digest.hexdigest(),
            "sizeBytes": source.stat().st_size,
        }
    if operation in {"copy", "move"}:
        destination_name = _required_path(extra, "destination")
        destination = _safe_path(root, destination_name)
        if destination.exists():
            raise ValueError(f"destination already exists: {destination_name}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if operation == "copy":
            shutil.copyfile(source, destination)
        else:
            source.replace(destination)
        return {
            "operation": operation,
            "source": source_name,
            "destination": destination_name,
            "sizeBytes": destination.stat().st_size,
        }
    if operation == "delete":
        size = source.stat().st_size
        source.unlink()
        return {"operation": operation, "source": source_name, "sizeBytes": size}
    raise ValueError(f"unsupported file operation: {operation}")


def _compress(root: Path, extra: Mapping[str, Any]) -> dict[str, Any]:
    raw_sources = extra.get("sources")
    if (
        not isinstance(raw_sources, list)
        or not raw_sources
        or not all(isinstance(item, str) for item in raw_sources)
    ):
        raise ValueError("compress sources must be a non-empty array of paths")
    destination_name = _required_path(extra, "destination")
    destination = _safe_path(root, destination_name)
    if destination.exists():
        raise ValueError(f"destination already exists: {destination_name}")
    sources = [(name, _safe_path(root, name, require_exists=True)) for name in raw_sources]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, source in sources:
            if not source.is_file() or source.is_symlink():
                raise ValueError(f"archive source must be a regular file: {name}")
            archive.write(source, arcname=name)
    return {
        "operation": "compress",
        "sources": raw_sources,
        "destination": destination_name,
        "sizeBytes": destination.stat().st_size,
    }


def _extract(
    source: Path,
    source_name: str,
    destination: Path,
    destination_name: str,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    entry_limit = _bounded_limit(extra.get("maxEntries"), _ARCHIVE_ENTRY_LIMIT, "maxEntries")
    bytes_limit = _bounded_limit(
        extra.get("maxUncompressedBytes"), _ARCHIVE_BYTES_LIMIT, "maxUncompressedBytes"
    )
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    total = 0
    try:
        with zipfile.ZipFile(source) as archive:
            members = archive.infolist()
            if len(members) > entry_limit:
                raise ValueError("archive exceeds the configured entry limit")
            for member in members:
                name = member.filename.rstrip("/")
                if not name:
                    continue
                relative = _relative_path(name)
                if stat.S_ISLNK(member.external_attr >> 16):
                    raise ValueError(f"archive symlink is not allowed: {name}")
                total += member.file_size
                if total > bytes_limit:
                    raise ValueError("archive exceeds the configured uncompressed-size limit")
                if member.compress_size == 0 and member.file_size > 0:
                    raise ValueError("archive entry exceeds the configured compression ratio")
                if (
                    member.compress_size
                    and member.file_size / member.compress_size > _ARCHIVE_RATIO_LIMIT
                ):
                    raise ValueError("archive entry exceeds the configured compression ratio")
                target = destination.joinpath(*relative.parts)
                if not target.resolve(strict=False).is_relative_to(destination.resolve()):
                    raise ValueError("archive entry escapes the extraction destination")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as input_stream, target.open("xb") as output_stream:
                    shutil.copyfileobj(input_stream, output_stream, length=64 * 1024)
                extracted.append(f"{destination_name}/{relative.as_posix()}")
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return {
        "operation": "extract",
        "source": source_name,
        "destination": destination_name,
        "files": extracted,
        "uncompressedBytes": total,
    }


def _required_path(extra: Mapping[str, Any], field: str) -> str:
    value = extra.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"file task requires {field}")
    _relative_path(value)
    return value


def _relative_path(value: str) -> PurePosixPath:
    if not value or len(value) > 4096 or "\\" in value or value.startswith("/"):
        raise ValueError("file paths must use bounded relative POSIX syntax")
    path = PurePosixPath(value)
    if not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("file paths cannot traverse their assigned workspace")
    if ":" in path.parts[0]:
        raise ValueError("file paths cannot contain a drive or URI scheme")
    return path


def _safe_path(root: Path, logical_path: str, *, require_exists: bool = False) -> Path:
    relative = _relative_path(logical_path)
    candidate = root.joinpath(*relative.parts)
    if not candidate.resolve(strict=False).is_relative_to(root.resolve()):
        raise ValueError("file path escapes its assigned workspace")
    for parent in (
        root.joinpath(*relative.parts[:index]) for index in range(1, len(relative.parts))
    ):
        if parent.exists() and parent.is_symlink():
            raise ValueError(f"workspace symlink is not allowed: {logical_path}")
    if candidate.exists() and candidate.is_symlink():
        raise ValueError(f"workspace symlink is not allowed: {logical_path}")
    if require_exists and not candidate.is_file():
        raise ValueError(f"source file does not exist: {logical_path}")
    return candidate


def _bounded_limit(value: object, maximum: int, field: str) -> int:
    selected = maximum if value is None else value
    if not isinstance(selected, int) or isinstance(selected, bool) or not 0 < selected <= maximum:
        raise ValueError(f"{field} must be between 1 and {maximum}")
    return selected
