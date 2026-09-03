"""Read and write the partitioned epic catalog."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

DEFAULT_ARCHIVE_PATH = "backlog/archive/epics.done.json"
ACTIVE_PATH = Path("backlog/epics.json")
TRANSITION_METADATA_KEY = "partition_transition"


class EpicCatalogError(ValueError):
    """Raised when the epic catalog is missing, malformed, or inconsistent."""


@dataclass(frozen=True)
class EpicCatalog:
    """The active manifest and all of its active and archived epic records."""

    manifest: dict[str, Any]
    epics: list[dict[str, Any]]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as exc:
        raise EpicCatalogError(f"catalog document is missing: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EpicCatalogError(f"catalog document cannot be read: {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise EpicCatalogError(f"catalog document must be a JSON object: {path}")
    return document


def _records(document: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    records = document.get("epics")
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise EpicCatalogError(f"catalog document has no valid epics list: {path}")
    return records


def _archive_paths(
    root: Path, manifest: dict[str, Any], *, default_if_missing: bool = False
) -> list[Path]:
    metadata = manifest.get("metadata")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise EpicCatalogError("catalog metadata must be a JSON object")

    declared = metadata.get("archive_files")
    if declared is None:
        if not default_if_missing:
            raise EpicCatalogError("metadata.archive_files must declare at least one archive")
        declared = [DEFAULT_ARCHIVE_PATH]
    if (
        not isinstance(declared, list)
        or not declared
        or any(not isinstance(item, str) for item in declared)
    ):
        raise EpicCatalogError(
            "metadata.archive_files must be a non-empty list of repository-relative strings"
        )

    root_resolved = root.resolve()
    active_resolved = (root / ACTIVE_PATH).resolve()
    paths: list[Path] = []
    seen: set[str] = set()
    for raw_path in declared:
        normalized = raw_path.replace("\\", "/")
        pure_posix = PurePosixPath(normalized)
        pure_windows = PureWindowsPath(raw_path)
        if (
            not normalized
            or "\x00" in raw_path
            or pure_posix.is_absolute()
            or pure_windows.is_absolute()
            or pure_windows.drive
            or ".." in pure_posix.parts
        ):
            raise EpicCatalogError(f"unsafe archive path: {raw_path!r}")

        path = root / Path(*pure_posix.parts)
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(root_resolved)
        except ValueError as exc:
            raise EpicCatalogError(f"unsafe archive path: {raw_path!r}") from exc
        if resolved == active_resolved:
            raise EpicCatalogError(f"archive path overlaps active catalog: {raw_path!r}")

        key = str(relative).replace("\\", "/").casefold()
        if key in seen:
            raise EpicCatalogError(f"duplicate archive path: {raw_path!r}")
        seen.add(key)
        paths.append(path)
    return paths


def _validate_records(
    records: Sequence[dict[str, Any]],
    *,
    archived: bool,
    source: str,
    enforce_partition: bool = True,
) -> None:
    for record in records:
        epic_id = record.get("id")
        if not isinstance(epic_id, str) or not epic_id:
            raise EpicCatalogError(f"epic in {source} must have a non-empty string id")
        if enforce_partition and archived and record.get("state") != "done":
            raise EpicCatalogError(f"archive {source} contains non-done epic {epic_id}")
        if enforce_partition and not archived and record.get("state") == "done":
            raise EpicCatalogError(f"active catalog contains done epic {epic_id}")


def _sorted_records(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        return sorted(records, key=lambda record: (record.get("wave", 0), record["id"]))
    except (KeyError, TypeError) as exc:
        raise EpicCatalogError("epic records must have comparable wave and id values") from exc


def _reject_duplicate_ids(records: Sequence[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for record in records:
        epic_id = record["id"]
        if epic_id in seen:
            raise EpicCatalogError(f"duplicate epic id: {epic_id}")
        seen.add(epic_id)


def load_epic_catalog(root: Path, *, allow_state_moves: bool = False) -> EpicCatalog:
    """Load the active manifest and all declared archive documents."""

    active_path = root / ACTIVE_PATH
    manifest = _read_json(active_path)
    active = _records(manifest, active_path)
    archive_paths = _archive_paths(root, manifest)
    _validate_records(
        active,
        archived=False,
        source=str(active_path),
        enforce_partition=not allow_state_moves,
    )

    archived_records: list[dict[str, Any]] = []
    for archive_path in archive_paths:
        archive = _read_json(archive_path)
        archived = _records(archive, archive_path)
        _validate_records(
            archived,
            archived=True,
            source=str(archive_path),
            enforce_partition=not allow_state_moves,
        )
        archived_records.extend(archived)

    _reject_duplicate_ids(active)
    _reject_duplicate_ids(archived_records)
    combined = list(active)
    active_by_id = {record["id"]: record for record in active}
    metadata = manifest.get("metadata")
    transition_pending = isinstance(metadata, dict) and metadata.get(TRANSITION_METADATA_KEY) == 1
    for archived in archived_records:
        active_record = active_by_id.get(archived["id"])
        if active_record is None:
            combined.append(archived)
        elif not allow_state_moves or not transition_pending:
            raise EpicCatalogError(f"duplicate epic id: {archived['id']}")
    return EpicCatalog(manifest=copy.deepcopy(manifest), epics=_sorted_records(combined))


def _metadata_for_write(
    manifest: dict[str, Any], total: int, active: int, archived: int, archive_files: list[str]
) -> dict[str, Any]:
    metadata = manifest.get("metadata")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise EpicCatalogError("catalog metadata must be a JSON object")
    result = copy.deepcopy(metadata)
    result["epic_count"] = total
    result["active_epic_count"] = active
    result["archived_epic_count"] = archived
    result["archive_files"] = archive_files
    result.pop(TRANSITION_METADATA_KEY, None)
    return result


def _write_json(path: Path, document: dict[str, Any]) -> None:
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except OSError as exc:
        raise EpicCatalogError(f"catalog document cannot be written: {path}: {exc}") from exc
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def write_epic_catalog(
    root: Path, manifest: dict[str, Any], epics: Sequence[dict[str, Any]]
) -> None:
    """Write active and done records into the canonical catalog partitions."""

    if not isinstance(manifest, dict):
        raise EpicCatalogError("catalog manifest must be a JSON object")
    if any(not isinstance(record, dict) for record in epics):
        raise EpicCatalogError("epics must be a sequence of JSON objects")

    archive_paths = _archive_paths(root, manifest, default_if_missing=True)
    if len(archive_paths) != 1:
        raise EpicCatalogError("writing an epic catalog requires exactly one archive path")

    records = [copy.deepcopy(record) for record in epics]
    _validate_records(
        [record for record in records if record.get("state") != "done"],
        archived=False,
        source="input",
    )
    _validate_records(
        [record for record in records if record.get("state") == "done"],
        archived=True,
        source="input",
    )
    _reject_duplicate_ids(records)
    ordered = _sorted_records(records)
    active = [record for record in ordered if record.get("state") != "done"]
    archived = [record for record in ordered if record.get("state") == "done"]

    output_manifest = copy.deepcopy(manifest)
    metadata = output_manifest.get("metadata")
    declared_archive_files = metadata.get("archive_files") if isinstance(metadata, dict) else None
    if declared_archive_files is None:
        declared_archive_files = [DEFAULT_ARCHIVE_PATH]
    output_manifest["metadata"] = _metadata_for_write(
        output_manifest,
        len(ordered),
        len(active),
        len(archived),
        list(declared_archive_files),
    )
    output_manifest["epics"] = active
    archive_manifest = {
        "metadata": copy.deepcopy(output_manifest["metadata"]),
        "epics": archived,
    }
    desired_by_id = {record["id"]: record for record in ordered}
    current_active = _records(manifest, root / ACTIVE_PATH)
    staging_by_id = {
        record["id"]: copy.deepcopy(desired_by_id.get(record["id"], record))
        for record in current_active
    }
    staging_by_id.update({record["id"]: copy.deepcopy(record) for record in active})
    staging_manifest = copy.deepcopy(output_manifest)
    staging_manifest["metadata"][TRANSITION_METADATA_KEY] = 1
    staging_manifest["epics"] = _sorted_records(list(staging_by_id.values()))

    # Stage a superset before either partition removes a record. An interrupted publish can leave
    # a marked cross-partition transition, which regeneration mode can safely finish, but never
    # leaves a moved epic absent from both files.
    _write_json(root / ACTIVE_PATH, staging_manifest)
    _write_json(archive_paths[0], archive_manifest)
    _write_json(root / ACTIVE_PATH, output_manifest)
