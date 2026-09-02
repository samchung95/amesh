"""Pure migration-manifest planning shared by runtime and readiness checks."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

_MIGRATION_NAME = re.compile(r"^(?P<version>[0-9]{4})_[a-z0-9_]+\.sql$")
_ONLINE_BLOCKED = re.compile(
    r"\b(?:DROP\s+(?:TABLE|COLUMN)|TRUNCATE|ALTER\s+COLUMN\s+[^;]+\s+TYPE)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MigrationDescriptor:
    filename: str
    mode: Literal["bootstrap", "expand", "exclusive"]
    online_compatible: bool
    rollback_guidance: str
    checksum: str
    body: str


def migration_body(source: str) -> str:
    body = source.strip()
    if body.startswith("BEGIN;"):
        body = body[len("BEGIN;") :].lstrip()
    if body.endswith("COMMIT;"):
        body = body[: -len("COMMIT;")].rstrip()
    return body


def migration_plan(directory: Path) -> tuple[MigrationDescriptor, ...]:
    """Validate and return the canonical ordered forward-migration plan."""

    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"migration manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("migrations"), list):
        raise RuntimeError("migration manifest must use schemaVersion 1 and a migrations list")
    entries = manifest["migrations"]
    listed = [entry.get("file") for entry in entries]
    discovered = [path.name for path in sorted(directory.glob("*.sql"))]
    if listed != discovered:
        raise RuntimeError(
            f"migration manifest order differs from SQL files: listed={listed}, found={discovered}"
        )
    versions: list[int] = []
    plan: list[MigrationDescriptor] = []
    for entry in entries:
        filename = entry.get("file")
        if not isinstance(filename, str) or (match := _MIGRATION_NAME.fullmatch(filename)) is None:
            raise RuntimeError(f"invalid migration filename in manifest: {filename!r}")
        versions.append(int(match.group("version")))
        mode = entry.get("mode")
        if mode not in {"bootstrap", "expand", "exclusive"}:
            raise RuntimeError(f"invalid migration mode for {filename}: {mode!r}")
        online_compatible = entry.get("onlineCompatible")
        if not isinstance(online_compatible, bool):
            raise RuntimeError(f"onlineCompatible must be boolean for {filename}")
        rollback = entry.get("rollbackGuidance")
        if not isinstance(rollback, str) or not rollback.strip():
            raise RuntimeError(f"rollback guidance is required for {filename}")
        source = (directory / filename).read_text(encoding="utf-8")
        stripped = source.strip()
        if not stripped.startswith("BEGIN;") or not stripped.endswith("COMMIT;"):
            raise RuntimeError(f"migration {filename} must have one explicit transaction wrapper")
        body = migration_body(source)
        if online_compatible and _ONLINE_BLOCKED.search(body):
            raise RuntimeError(f"online-compatible migration {filename} contains contract DDL")
        plan.append(
            MigrationDescriptor(
                filename=filename,
                mode=mode,
                online_compatible=online_compatible,
                rollback_guidance=rollback.strip(),
                checksum=hashlib.sha256(source.encode()).hexdigest(),
                body=body,
            )
        )
    if versions != list(range(versions[0], versions[-1] + 1)):
        raise RuntimeError(f"migration versions must be contiguous: {versions}")
    return tuple(plan)
