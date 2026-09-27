"""Pure migration-manifest planning and destructive-upgrade guards."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

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


@dataclass(frozen=True)
class DestructiveMigration:
    filename: str
    reason: str


@dataclass(frozen=True)
class DestructiveMigrationBackupDecision:
    destructive_pending: tuple[DestructiveMigration, ...]
    backup_confirmed_at: datetime | None = None


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


def destructive_migration_manifest(directory: Path) -> tuple[DestructiveMigration, ...]:
    """Return destructive forward migrations declared outside checksum-protected SQL files."""

    manifest_path = directory / "destructive.json"
    if not manifest_path.is_file():
        return ()
    manifest: Any = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise RuntimeError("destructive migration manifest must be an object")
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("migrations"), list):
        raise RuntimeError(
            "destructive migration manifest must use schemaVersion 1 and a migrations list"
        )
    existing_files = {path.name for path in directory.glob("*.sql")}
    seen: set[str] = set()
    destructive: list[DestructiveMigration] = []
    for entry in manifest["migrations"]:
        if not isinstance(entry, dict):
            raise RuntimeError("destructive migration manifest entries must be objects")
        filename = entry.get("file")
        if not isinstance(filename, str) or _MIGRATION_NAME.fullmatch(filename) is None:
            raise RuntimeError(f"invalid destructive migration filename: {filename!r}")
        if filename in seen:
            raise RuntimeError(f"duplicate destructive migration entry: {filename}")
        if filename not in existing_files:
            raise RuntimeError(f"destructive migration entry names a missing file: {filename}")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise RuntimeError(f"destructive migration reason is required for {filename}")
        seen.add(filename)
        destructive.append(DestructiveMigration(filename=filename, reason=reason.strip()))
    return tuple(destructive)


def validate_destructive_migration_backup(
    *,
    applied_versions: Collection[str],
    pending_migrations: Sequence[MigrationDescriptor | str],
    destructive_manifest: Sequence[DestructiveMigration] | Mapping[str, str],
    backup_confirmed_at: str | None,
    backup_max_age_hours: float,
    now: datetime,
) -> DestructiveMigrationBackupDecision:
    """Validate that destructive upgrade migrations have a recent verified-backup marker."""

    if backup_max_age_hours <= 0:
        raise ValueError("backup_max_age_hours must be positive")
    destructive_by_file = _destructive_reasons(destructive_manifest)
    destructive_pending = tuple(
        DestructiveMigration(filename=filename, reason=destructive_by_file[filename])
        for filename in (_migration_filename(item) for item in pending_migrations)
        if filename in destructive_by_file
    )
    if not destructive_pending or len(applied_versions) == 0:
        return DestructiveMigrationBackupDecision(destructive_pending=destructive_pending)

    marker = (backup_confirmed_at or "").strip()
    if not marker:
        raise RuntimeError(
            _destructive_refusal_message(
                destructive_pending,
                backup_max_age_hours,
                problem="No verified backup marker was supplied.",
            )
        )
    confirmed_at = _parse_backup_marker(marker, destructive_pending, backup_max_age_hours)
    now_utc = _to_utc(now)
    if confirmed_at > now_utc:
        raise RuntimeError(
            _destructive_refusal_message(
                destructive_pending,
                backup_max_age_hours,
                problem=(
                    "MIGRATION_BACKUP_CONFIRMED_AT is in the future "
                    f"({confirmed_at.isoformat().replace('+00:00', 'Z')})."
                ),
            )
        )
    if now_utc - confirmed_at > timedelta(hours=backup_max_age_hours):
        raise RuntimeError(
            _destructive_refusal_message(
                destructive_pending,
                backup_max_age_hours,
                problem=(
                    "MIGRATION_BACKUP_CONFIRMED_AT is older than "
                    f"{_format_hours(backup_max_age_hours)} hour(s)."
                ),
            )
        )
    return DestructiveMigrationBackupDecision(
        destructive_pending=destructive_pending,
        backup_confirmed_at=confirmed_at,
    )


def destructive_migration_backup_warning(
    decision: DestructiveMigrationBackupDecision,
) -> str | None:
    if decision.backup_confirmed_at is None or not decision.destructive_pending:
        return None
    names = ", ".join(item.filename for item in decision.destructive_pending)
    marker = decision.backup_confirmed_at.isoformat().replace("+00:00", "Z")
    return (
        "Applying destructive forward-only migration(s) after verified backup marker "
        f"{marker}: {names}. Rollback is restore the pre-upgrade backup and redeploy "
        "the previous AMESH release; no down migrations will be run."
    )


def _destructive_reasons(
    destructive_manifest: Sequence[DestructiveMigration] | Mapping[str, str],
) -> dict[str, str]:
    if isinstance(destructive_manifest, Mapping):
        return {filename: reason for filename, reason in destructive_manifest.items()}
    return {item.filename: item.reason for item in destructive_manifest}


def _migration_filename(migration: MigrationDescriptor | str) -> str:
    return migration if isinstance(migration, str) else migration.filename


def _parse_backup_marker(
    marker: str,
    destructive_pending: Sequence[DestructiveMigration],
    backup_max_age_hours: float,
) -> datetime:
    normalized = f"{marker[:-1]}+00:00" if marker.endswith("Z") else marker
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RuntimeError(
            _destructive_refusal_message(
                destructive_pending,
                backup_max_age_hours,
                problem="MIGRATION_BACKUP_CONFIRMED_AT is not a valid ISO-8601 timestamp.",
            )
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise RuntimeError(
            _destructive_refusal_message(
                destructive_pending,
                backup_max_age_hours,
                problem="MIGRATION_BACKUP_CONFIRMED_AT must be an ISO-8601 UTC timestamp.",
            )
        )
    return parsed.astimezone(UTC)


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _destructive_refusal_message(
    destructive_pending: Sequence[DestructiveMigration],
    backup_max_age_hours: float,
    *,
    problem: str,
) -> str:
    migrations = "; ".join(f"{item.filename} ({item.reason})" for item in destructive_pending)
    return (
        f"{problem} Refusing to apply destructive forward-only migration(s) to an existing "
        f"database: {migrations}. AMESH migrations have no down path; rollback is to restore "
        "the verified pre-upgrade PostgreSQL/object-storage backup and redeploy the previous "
        "release, or to use expand/contract forward fixes. Take and verify a backup first "
        "(for example pg_dump -Fc plus pg_restore --list), then set "
        "MIGRATION_BACKUP_CONFIRMED_AT to the backup verification time as an ISO-8601 UTC "
        f"timestamp no older than {_format_hours(backup_max_age_hours)} hour(s). Adjust "
        "MIGRATION_BACKUP_MAX_AGE_HOURS only under an approved change record."
    )


def _format_hours(hours: float) -> str:
    return f"{hours:g}"
