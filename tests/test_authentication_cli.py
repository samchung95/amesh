from __future__ import annotations

import asyncio
import os
import subprocess
import sys

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_bootstrap_admin_cli_reads_stdin_once_and_creates_no_default_credential() -> None:
    if TEST_DATABASE_URL is None:
        raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

    async def prepare() -> tuple[str, str]:
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, migration_directory())
        return database.name, database.database_url

    database_name, database_url = asyncio.run(prepare())
    password = "cli correct horse battery staple"
    environment = os.environ.copy()
    environment.update(
        {
            "DATABASE_URL": database_url,
            "DATABASE_TLS_MODE": "disable",
            "AUTH_POLICY": "local",
            "AMESH_TOKEN_PEPPER": "cli-bootstrap-test-pepper",
        }
    )
    command = [
        sys.executable,
        "-m",
        "amesh.cli",
        "auth",
        "bootstrap-admin",
        "--handle",
        "cli-admin",
        "--display-name",
        "CLI administrator",
        "--password-stdin",
    ]
    try:
        created = subprocess.run(
            command,
            input=f"{password}\n",
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        assert created.returncode == 0, created.stderr
        assert '"handle": "cli-admin"' in created.stdout
        assert password not in created.stdout
        assert password not in created.stderr

        repeated = subprocess.run(
            command,
            input=f"{password}\n",
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        assert repeated.returncode == 2
        assert "already been completed" in repeated.stderr
        assert password not in repeated.stderr

        async def verify() -> tuple[int, int]:
            engine = create_async_engine(database_url)
            try:
                async with engine.connect() as connection:
                    users = int(
                        await connection.scalar(
                            text(
                                """
                                SELECT count(*)
                                FROM auth_principals
                                WHERE principal_type = 'USER' AND handle = 'cli-admin'
                                """
                            )
                        )
                        or 0
                    )
                    bindings = int(
                        await connection.scalar(
                            text(
                                """
                                SELECT count(*)
                                FROM auth_role_bindings AS bindings
                                JOIN auth_principals AS principals
                                  ON principals.id = bindings.principal_id
                                WHERE principals.handle = 'cli-admin'
                                  AND bindings.role_name = 'instance-admin'
                                  AND bindings.scope_type = 'INSTANCE'
                                """
                            )
                        )
                        or 0
                    )
                return users, bindings
            finally:
                await engine.dispose()

        assert asyncio.run(verify()) == (1, 1)
    finally:
        asyncio.run(drop_ephemeral_database(TEST_DATABASE_URL, database_name))
