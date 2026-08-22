import asyncio

import pytest
from fastapi import HTTPException

from amesh.app import authenticate_bearer_actor
from amesh.config import Settings
from amesh.ports import StorageBackend
from amesh.storage.factory import build_object_store


def test_reference_configuration_is_postgresql_only() -> None:
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert not hasattr(settings, "nats_url")
    assert settings.object_storage_bucket == "amesh"
    assert settings.object_storage_backend == "s3"
    assert settings.object_storage_gc_safety_window_seconds == 86_400
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
        asyncio.run(authenticate_bearer_actor(settings, None, "Bearer test-token"))

    assert caught.value.status_code == 401


def test_object_storage_backend_configuration_and_workload_identity() -> None:
    azure = Settings(
        _env_file=None,
        object_storage_backend="azure",
        object_storage_azure_account_url="https://account.blob.core.windows.net",
        object_storage_workload_identity=True,
        object_storage_encryption_key_id="scope-a",
        object_storage_proxy_url="http://proxy.internal:8080",
        object_storage_ca_file="/etc/amesh/storage-ca.pem",
    )
    gcs = Settings(
        _env_file=None,
        object_storage_backend="gcs",
        object_storage_workload_identity=True,
        object_storage_gcs_project="project-a",
        object_storage_gcs_endpoint="https://storage.private.example",
    )

    assert build_object_store(azure).backend is StorageBackend.AZURE
    assert build_object_store(gcs).backend is StorageBackend.GCS
    with pytest.raises(ValueError, match="AZURE_ACCOUNT_URL"):
        Settings(_env_file=None, object_storage_backend="azure")
    with pytest.raises(ValueError, match="GCS requires workload identity"):
        Settings(_env_file=None, object_storage_backend="gcs")
