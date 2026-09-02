from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.migrations import (
    EphemeralDatabase,
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)


@pytest.fixture
def postgres_admin_database_url() -> str | None:
    """Return the optional PostgreSQL admin anchor without requiring it at collection."""

    return os.getenv("AMESH_TEST_DATABASE_URL")


@pytest.fixture
def isolated_postgres_database(
    postgres_admin_database_url: str | None,
) -> Iterator[EphemeralDatabase]:
    """Create one fully migrated disposable database for a single test."""

    if postgres_admin_database_url is None:
        pytest.skip("AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests")
    database = asyncio.run(create_ephemeral_database(postgres_admin_database_url))
    try:
        asyncio.run(apply_migrations(database.database_url, migration_directory()))
        yield database
    finally:
        asyncio.run(drop_ephemeral_database(postgres_admin_database_url, database.name))


@pytest.fixture
def migrated_test_database_url(isolated_postgres_database: EphemeralDatabase) -> str:
    """Return the SQLAlchemy URL for the current test's migrated database."""

    return isolated_postgres_database.database_url


@pytest.fixture
async def postgres_async_engine(
    migrated_test_database_url: str,
) -> AsyncIterator[AsyncEngine]:
    """Yield and dispose one async engine on the test's active event loop."""

    engine = create_async_engine(migrated_test_database_url)
    try:
        yield engine
    finally:
        await engine.dispose()
