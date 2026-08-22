from __future__ import annotations

from datetime import timedelta

from amesh.adapters.azure import AzureBlobObjectStore
from amesh.adapters.gcs import GoogleCloudStorageObjectStore
from amesh.adapters.s3 import S3ObjectStore
from amesh.config import Settings
from amesh.ports import ObjectStorageBackend

from .service import VerifiedObjectStore


def build_object_store(settings: Settings) -> VerifiedObjectStore:
    backend: ObjectStorageBackend
    common = {
        "encryption_key_id": settings.object_storage_encryption_key_id,
        "proxy_url": settings.object_storage_proxy_url,
        "ca_file": settings.object_storage_ca_file,
    }
    if settings.object_storage_backend == "s3":
        backend = S3ObjectStore(
            endpoint=settings.object_storage_endpoint,
            region=settings.object_storage_region,
            bucket=settings.object_storage_bucket,
            access_key=(
                None
                if settings.object_storage_workload_identity
                else settings.object_storage_access_key.get_secret_value()
            ),
            secret_key=(
                None
                if settings.object_storage_workload_identity
                else settings.object_storage_secret_key.get_secret_value()
            ),
            **common,
        )
    elif settings.object_storage_backend == "azure":
        assert settings.object_storage_azure_account_url is not None
        backend = AzureBlobObjectStore(
            account_url=settings.object_storage_azure_account_url,
            container=settings.object_storage_bucket,
            account_key=(
                None
                if settings.object_storage_workload_identity
                or settings.object_storage_azure_account_key is None
                else settings.object_storage_azure_account_key.get_secret_value()
            ),
            **common,
        )
    else:
        backend = GoogleCloudStorageObjectStore(
            bucket=settings.object_storage_bucket,
            project=settings.object_storage_gcs_project,
            endpoint=settings.object_storage_gcs_endpoint,
            credentials_file=(
                None
                if settings.object_storage_workload_identity
                else settings.object_storage_gcs_credentials_file
            ),
            **common,
        )
    return VerifiedObjectStore(
        backend,
        consistency_attempts=settings.object_storage_consistency_attempts,
        consistency_delay_seconds=settings.object_storage_consistency_delay_seconds,
        spool_memory_bytes=settings.object_storage_spool_memory_bytes,
        gc_safety_window=timedelta(seconds=settings.object_storage_gc_safety_window_seconds),
    )
