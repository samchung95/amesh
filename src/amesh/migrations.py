from __future__ import annotations

import asyncio
import hashlib
import os
from pathlib import Path

import asyncpg  # type: ignore[import-untyped]

from amesh.config import get_settings
from amesh.observability import configure_structured_logging

_MIGRATION_LOCK = 280465470280


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


async def apply_migrations(database_url: str, directory: Path) -> list[str]:
    connection = await asyncpg.connect(
        database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    )
    applied: list[str] = []
    try:
        async with connection.transaction():
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
            for path in sorted(directory.glob("*.sql")):
                source = path.read_text(encoding="utf-8")
                checksum = hashlib.sha256(source.encode()).hexdigest()
                current = await connection.fetchval(
                    "SELECT checksum FROM amesh_schema_migrations WHERE version = $1",
                    path.name,
                )
                if current is not None:
                    if current != checksum:
                        raise RuntimeError(f"applied migration {path.name!r} checksum changed")
                    continue
                await connection.execute(migration_body(source))
                await connection.execute(
                    "INSERT INTO amesh_schema_migrations (version, checksum) VALUES ($1, $2)",
                    path.name,
                    checksum,
                )
                applied.append(path.name)
    finally:
        await connection.close()
    return applied


def main() -> None:
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    applied = asyncio.run(apply_migrations(settings.database_url, migration_directory()))
    print(f"applied {len(applied)} migration(s): {', '.join(applied) or 'none'}")


if __name__ == "__main__":
    main()
