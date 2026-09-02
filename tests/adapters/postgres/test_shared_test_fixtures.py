from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

FORBIDDEN_APPLICATION_DATABASE_PATTERNS = (
    re.compile(r"create_async_engine\(\s*_?TEST_DATABASE_URL\b"),
    re.compile(r"asyncpg\.connect\(\s*_?TEST_DATABASE_URL\b"),
    re.compile(r"database_url\s*=\s*_?TEST_DATABASE_URL\b"),
)


def test_configured_postgres_url_is_only_used_as_an_admin_anchor() -> None:
    tests_root = Path(__file__).parents[2]
    violations: list[str] = []

    for test_path in sorted(tests_root.rglob("*.py")):
        source = test_path.read_text(encoding="utf-8")
        if any(pattern.search(source) for pattern in FORBIDDEN_APPLICATION_DATABASE_PATTERNS):
            violations.append(test_path.relative_to(tests_root).as_posix())

    assert not violations, (
        "Tests must create application engines from an isolated child database: "
        + ", ".join(violations)
    )


@pytest.mark.anyio
async def test_shared_postgres_engine_uses_a_migrated_disposable_database(
    postgres_async_engine: AsyncEngine,
) -> None:
    async with postgres_async_engine.connect() as connection:
        database_name = await connection.scalar(text("SELECT current_database()"))
        migration_count = await connection.scalar(
            text("SELECT count(*) FROM amesh_schema_migrations")
        )

    assert isinstance(database_name, str)
    assert re.fullmatch(r"amesh_test_[a-f0-9]{16}", database_name)
    assert isinstance(migration_count, int)
    assert migration_count > 0
