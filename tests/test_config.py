import asyncio

import pytest
from fastapi import HTTPException

from amesh.app import authenticate_actor
from amesh.config import Settings


def test_reference_configuration_is_postgresql_only() -> None:
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert not hasattr(settings, "nats_url")
    assert settings.object_storage_bucket == "amesh"
    assert settings.database_pool_size == 10
    assert settings.database_prepared_statement_cache_size == 100


def test_database_urls_require_the_async_postgresql_driver() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings(_env_file=None, database_url="sqlite+aiosqlite:///amesh.db")
    with pytest.raises(ValueError, match="DATABASE_READ_REPLICA_URL"):
        Settings(
            _env_file=None,
            database_read_replica_url="mysql+asyncmy://amesh@replica/amesh",
        )


def test_development_bootstrap_token_fails_closed_outside_development() -> None:
    settings = Settings(
        _env_file=None,
        app_env="production",
        auth_mode="development",
        amesh_admin_token="test-token",
        amesh_token_pepper="test-production-pepper",
    )

    with pytest.raises(HTTPException) as caught:
        asyncio.run(authenticate_actor(settings, None, "Bearer test-token"))

    assert caught.value.status_code == 401
