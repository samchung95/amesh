from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Generator, Iterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.migrations import (
    EphemeralDatabase,
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

MISSING_POSTGRES_REASON_PREFIX = "AMESH_TEST_DATABASE_URL is required"
MISSING_POSTGRES_FIXTURE_REASON = (
    f"{MISSING_POSTGRES_REASON_PREFIX} for PostgreSQL integration tests"
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.getgroup("amesh").addoption(
        "--fail-on-missing-postgres",
        action="store_true",
        help="fail when a PostgreSQL test skips because AMESH_TEST_DATABASE_URL is missing",
    )


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[object],
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield
    if (
        item.config.getoption("--fail-on-missing-postgres")
        and report.skipped
        and MISSING_POSTGRES_REASON_PREFIX in str(report.longrepr)
    ):
        report.outcome = "failed"
        report.longrepr = (
            f"{report.nodeid}: PostgreSQL verification requires AMESH_TEST_DATABASE_URL; "
            "the database suite may not be skipped"
        )
    return report


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
        pytest.skip(MISSING_POSTGRES_FIXTURE_REASON)
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
