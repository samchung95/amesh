from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from uuid import uuid4

import pytest

from amesh.adapters.s3 import S3ObjectStore
from amesh.storage import VerifiedObjectStore

MINIO_ENDPOINT = os.getenv("AMESH_TEST_S3_ENDPOINT")


@pytest.mark.skipif(
    MINIO_ENDPOINT is None,
    reason="AMESH_TEST_S3_ENDPOINT is required for MinIO integration tests",
)
def test_minio_stream_integrity_lifecycle_inventory_and_versioned_delete() -> None:
    async def scenario() -> None:
        if MINIO_ENDPOINT is None:
            raise RuntimeError("AMESH_TEST_S3_ENDPOINT is required")
        tenant_id = f"storage-test-{uuid4().hex}"
        content = b"a" * (5 * 1024 * 1024) + b"tail"

        async def upload() -> AsyncIterator[bytes]:
            yield content[: 3 * 1024 * 1024]
            yield content[3 * 1024 * 1024 :]

        store = VerifiedObjectStore(
            S3ObjectStore(
                endpoint=MINIO_ENDPOINT,
                region="us-east-1",
                bucket="amesh",
                access_key="minio",
                secret_key="minio-development-only",
            ),
            consistency_delay_seconds=0.01,
        )
        metadata = await store.put(
            tenant_id,
            "integration/multipart.bin",
            upload(),
            content_type="application/octet-stream",
            creator="integration-principal",
            lineage=("execution:integration",),
        )
        assert metadata.size == len(content)
        assert metadata.creator == "integration-principal"
        assert metadata.lineage == ("execution:integration",)
        assert b"".join([chunk async for chunk in store.get(tenant_id, metadata.uri)]) == content
        assert (
            b"".join(
                [
                    chunk
                    async for chunk in store.get_range(
                        tenant_id,
                        metadata.uri,
                        len(content) - 4,
                        len(content),
                    )
                ]
            )
            == b"tail"
        )
        lifecycle = await store.apply_lifecycle(
            tenant_id,
            metadata.uri,
            retention_until=None,
            legal_hold=False,
            referenced=True,
            delete=True,
        )
        assert lifecycle.blocked_by == "referenced"
        report = await store.validate_inventory(tenant_id)
        assert (report.objects, report.bytes, report.verified, report.corrupt) == (
            1,
            len(content),
            1,
            (),
        )
        deleted = await store.apply_lifecycle(
            tenant_id,
            metadata.uri,
            retention_until=None,
            legal_hold=False,
            referenced=False,
            delete=True,
        )
        assert deleted.deleted and deleted.deletion_marker

    asyncio.run(scenario())
