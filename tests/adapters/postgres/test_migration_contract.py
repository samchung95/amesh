from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    schema_fingerprint,
    seed_fingerprint,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_fresh_databases_are_repeatable_and_migrations_are_idempotent() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        first = await create_ephemeral_database(TEST_DATABASE_URL)
        second = await create_ephemeral_database(TEST_DATABASE_URL)
        try:
            expected = [path.name for path in sorted(MIGRATIONS.glob("*.sql"))]
            assert await apply_migrations(first.database_url, MIGRATIONS) == expected
            assert await apply_migrations(second.database_url, MIGRATIONS) == expected
            assert await apply_migrations(first.database_url, MIGRATIONS) == []
            assert await schema_fingerprint(first.database_url) == await schema_fingerprint(
                second.database_url
            )
            assert await seed_fingerprint(first.database_url) == await seed_fingerprint(
                second.database_url
            )
        finally:
            await drop_ephemeral_database(TEST_DATABASE_URL, first.name)
            await drop_ephemeral_database(TEST_DATABASE_URL, second.name)

    asyncio.run(scenario())
