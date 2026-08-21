from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import SplitResult, urlsplit, urlunsplit
from uuid import uuid4

import asyncpg  # type: ignore[import-untyped]

from amesh.config import get_settings
from amesh.observability import configure_structured_logging

_MIGRATION_LOCK = 280465470280
_MIGRATION_NAME = re.compile(r"^(?P<version>[0-9]{4})_[a-z0-9_]+\.sql$")
_EPHEMERAL_NAME = re.compile(r"^amesh_test_[a-f0-9]{16}$")
_MINIMUM_POSTGRESQL_VERSION = 150000
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
class EphemeralDatabase:
    name: str
    database_url: str


def migration_directory() -> Path:
    configured = os.getenv("AMESH_MIGRATIONS_PATH")
    if configured:
        return Path(configured)
    container_path = Path("/app/migrations")
    if container_path.is_dir():
        return container_path
    return Path(__file__).resolve().parents[2] / "migrations"


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


async def apply_migrations(database_url: str, directory: Path) -> list[str]:
    plan = migration_plan(directory)
    connection = await asyncpg.connect(
        database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    )
    applied: list[str] = []
    try:
        server_version = int(await connection.fetchval("SHOW server_version_num"))
        if server_version < _MINIMUM_POSTGRESQL_VERSION:
            raise RuntimeError(
                f"PostgreSQL 15 or newer is required; server_version_num is {server_version}"
            )
        async with connection.transaction(isolation="serializable"):
            await connection.execute("SELECT pg_advisory_xact_lock($1)", _MIGRATION_LOCK)
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS amesh_schema_migrations (
                    version text PRIMARY KEY,
                    checksum text NOT NULL,
                    applied_at timestamptz NOT NULL DEFAULT now()
                )
                """
            )
            applied_versions = {
                str(row["version"]): str(row["checksum"])
                for row in await connection.fetch(
                    "SELECT version, checksum FROM amesh_schema_migrations"
                )
            }
            planned_versions = {item.filename for item in plan}
            unknown_versions = sorted(set(applied_versions) - planned_versions)
            if unknown_versions:
                raise RuntimeError(
                    f"database contains migrations absent from the manifest: {unknown_versions}"
                )
            for descriptor in plan:
                current = await connection.fetchval(
                    "SELECT checksum FROM amesh_schema_migrations WHERE version = $1",
                    descriptor.filename,
                )
                if current is not None:
                    if current != descriptor.checksum:
                        raise RuntimeError(
                            f"applied migration {descriptor.filename!r} checksum changed"
                        )
                    continue
                await connection.execute(descriptor.body)
                await connection.execute(
                    "INSERT INTO amesh_schema_migrations (version, checksum) VALUES ($1, $2)",
                    descriptor.filename,
                    descriptor.checksum,
                )
                applied.append(descriptor.filename)
    finally:
        await connection.close()
    return applied


async def create_ephemeral_database(database_url: str) -> EphemeralDatabase:
    """Create one exact, isolated PostgreSQL database for migration/repository tests."""

    parts = _split_database_url(database_url)
    name = f"amesh_test_{uuid4().hex[:16]}"
    admin_url = _replace_database(parts, "postgres")
    connection = await asyncpg.connect(admin_url)
    try:
        await connection.execute(f'CREATE DATABASE "{name}" TEMPLATE template0')
    finally:
        await connection.close()
    return EphemeralDatabase(name=name, database_url=_replace_database(parts, name, asyncpg=False))


async def drop_ephemeral_database(database_url: str, name: str) -> None:
    """Drop only databases created by :func:`create_ephemeral_database`."""

    if _EPHEMERAL_NAME.fullmatch(name) is None:
        raise ValueError(f"refusing to drop non-ephemeral database {name!r}")
    parts = _split_database_url(database_url)
    connection = await asyncpg.connect(_replace_database(parts, "postgres"))
    try:
        await connection.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = $1 AND pid <> pg_backend_pid()",
            name,
        )
        await connection.execute(f'DROP DATABASE IF EXISTS "{name}"')
    finally:
        await connection.close()


async def schema_fingerprint(database_url: str) -> str:
    """Hash the canonical public schema, constraints, indexes, policies and triggers."""

    connection = await asyncpg.connect(
        database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    )
    try:
        rows = await connection.fetch(
            """
            SELECT kind, object_name, definition
            FROM (
                SELECT 'column' AS kind,
                       table_name || '.' || column_name AS object_name,
                       data_type || '|' || udt_name || '|' || is_nullable || '|' ||
                           COALESCE(column_default, '') AS definition
                FROM information_schema.columns
                WHERE table_schema = 'public'
                UNION ALL
                SELECT 'constraint', conrelid::regclass::text || '.' || conname,
                       pg_get_constraintdef(oid, true)
                FROM pg_constraint
                WHERE connamespace = 'public'::regnamespace
                UNION ALL
                SELECT 'index', tablename || '.' || indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                UNION ALL
                SELECT 'policy', tablename || '.' || policyname,
                       COALESCE(qual, '') || '|' || COALESCE(with_check, '')
                FROM pg_policies
                WHERE schemaname = 'public'
                UNION ALL
                SELECT 'trigger', event_object_table || '.' || trigger_name,
                       action_timing || '|' || event_manipulation || '|' || action_statement
                FROM information_schema.triggers
                WHERE trigger_schema = 'public'
            ) AS schema_objects
            ORDER BY kind, object_name, definition
            """
        )
    finally:
        await connection.close()
    encoded = json.dumps([tuple(row) for row in rows], separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


async def seed_fingerprint(database_url: str) -> str:
    """Hash deterministic semantic seed values while excluding generated identities/timestamps."""

    connection = await asyncpg.connect(
        database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    )
    try:
        rows = await connection.fetch(
            """
            SELECT slug, display_name, status, version, lifecycle, settings, storage_prefix
            FROM tenants
            ORDER BY slug
            """
        )
    finally:
        await connection.close()
    encoded = json.dumps(
        [dict(row) for row in rows], default=str, separators=(",", ":"), sort_keys=True
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def _split_database_url(database_url: str) -> SplitResult:
    return urlsplit(database_url.replace("postgresql+asyncpg://", "postgresql://", 1))


def _replace_database(parts: SplitResult, database: str, *, asyncpg: bool = True) -> str:
    scheme = "postgresql" if asyncpg else "postgresql+asyncpg"
    return urlunsplit((scheme, parts.netloc, f"/{database}", parts.query, parts.fragment))


def main() -> None:
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    applied = asyncio.run(apply_migrations(settings.database_url, migration_directory()))
    print(f"applied {len(applied)} migration(s): {', '.join(applied) or 'none'}")


if __name__ == "__main__":
    main()
