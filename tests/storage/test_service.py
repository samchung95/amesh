from __future__ import annotations

import asyncio
import hashlib
import tracemalloc
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from prometheus_client import generate_latest

from amesh.ports import ObjectMetadata, StorageBackend, StorageMigrationCheckpoint
from amesh.storage import ObjectIntegrityError, VerifiedObjectStore


class MemoryBackend:
    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend
        self.objects: dict[str, tuple[bytes, ObjectMetadata]] = {}
        self.head_failures = 0

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        content = b"".join([chunk async for chunk in chunks])
        scheme = {StorageBackend.S3: "s3", StorageBackend.AZURE: "azure", StorageBackend.GCS: "gs"}[
            self.backend
        ]
        uri = f"{scheme}://test/tenants/{tenant_id}/{key}"
        metadata = ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
            key=key,
            backend=self.backend,
        )
        self.objects[uri] = (content, metadata)
        return metadata

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            content, metadata = self.objects[uri]
            if metadata.tenant_id != tenant_id:
                raise ValueError("object URI is outside the tenant storage prefix")
            for offset in range(0, len(content), 3):
                yield content[offset : offset + 3]

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        metadata = await self.head(tenant_id, uri)
        del self.objects[metadata.uri]

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        if self.head_failures:
            self.head_failures -= 1
            raise FileNotFoundError(uri)
        _, metadata = self.objects[uri]
        if metadata.tenant_id != tenant_id:
            raise ValueError("object URI is outside the tenant storage prefix")
        return metadata

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        async def objects() -> AsyncIterator[ObjectMetadata]:
            for _, metadata in sorted(self.objects.values(), key=lambda item: item[1].key or ""):
                if metadata.tenant_id == tenant_id:
                    yield metadata

        return objects()

    async def set_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
    ) -> ObjectMetadata:
        content, metadata = self.objects[uri]
        if metadata.tenant_id != tenant_id:
            raise ValueError("object URI is outside the tenant storage prefix")
        metadata = metadata.model_copy(
            update={"retention_until": retention_until, "legal_hold": legal_hold}
        )
        self.objects[uri] = (content, metadata)
        return metadata


async def chunks(*values: bytes) -> AsyncIterator[bytes]:
    for value in values:
        yield value


def test_verified_storage_retries_visibility_and_detects_corruption_before_yield() -> None:
    async def scenario() -> None:
        backend = MemoryBackend(StorageBackend.S3)
        backend.head_failures = 2
        store = VerifiedObjectStore(backend, consistency_delay_seconds=0)
        metadata = await store.put("tenant-a", "reports/result.json", chunks(b"abc", b"def"))
        assert metadata.checksum_sha256 == hashlib.sha256(b"abcdef").hexdigest()
        assert b"".join([part async for part in store.get("tenant-a", metadata.uri)]) == b"abcdef"

        content, original = backend.objects[metadata.uri]
        backend.objects[metadata.uri] = (content + b"corrupt", original)
        iterator = store.get("tenant-a", metadata.uri)
        with pytest.raises(ObjectIntegrityError, match="checksum verification"):
            await anext(iterator)

        with pytest.raises(ValueError, match="tenant storage prefix"):
            await store.head("tenant-b", metadata.uri)

    asyncio.run(scenario())


def test_lifecycle_never_deletes_referenced_held_or_retained_objects() -> None:
    async def scenario() -> None:
        backend = MemoryBackend(StorageBackend.S3)
        store = VerifiedObjectStore(backend)
        metadata = await store.put("tenant-a", "artifact.bin", chunks(b"artifact"))
        future = datetime.now(UTC) + timedelta(days=1)

        referenced = await store.apply_lifecycle(
            "tenant-a",
            metadata.uri,
            retention_until=None,
            legal_hold=False,
            referenced=True,
            delete=True,
        )
        held = await store.apply_lifecycle(
            "tenant-a",
            metadata.uri,
            retention_until=None,
            legal_hold=True,
            referenced=False,
            delete=True,
        )
        retained = await store.apply_lifecycle(
            "tenant-a",
            metadata.uri,
            retention_until=future,
            legal_hold=False,
            referenced=False,
            delete=True,
        )
        deleted = await store.apply_lifecycle(
            "tenant-a",
            metadata.uri,
            retention_until=None,
            legal_hold=False,
            referenced=False,
            delete=True,
        )

        assert [referenced.blocked_by, held.blocked_by, retained.blocked_by] == [
            "referenced",
            "legal_hold",
            "retention",
        ]
        assert deleted.deleted and deleted.deletion_marker
        assert metadata.uri not in backend.objects

    asyncio.run(scenario())


def test_checksum_verified_migration_resumes_from_durable_checkpoint() -> None:
    async def scenario() -> None:
        source_backend = MemoryBackend(StorageBackend.S3)
        destination_backend = MemoryBackend(StorageBackend.AZURE)
        source = VerifiedObjectStore(source_backend)
        destination = VerifiedObjectStore(destination_backend)
        await source.put("tenant-a", "a.bin", chunks(b"a"))
        await source.put("tenant-a", "b.bin", chunks(b"bb"))
        checkpoints: list[StorageMigrationCheckpoint] = []

        async def interrupt(checkpoint: StorageMigrationCheckpoint) -> None:
            checkpoints.append(checkpoint)
            if checkpoint.objects_copied == 1:
                raise RuntimeError("simulated operator interruption")

        with pytest.raises(RuntimeError, match="interruption"):
            await source.migrate_to(
                destination,
                "tenant-a",
                write_checkpoint=interrupt,
            )

        resumed = await source.migrate_to(
            destination,
            "tenant-a",
            checkpoint=checkpoints[-1],
        )
        assert resumed.complete
        assert resumed.objects_copied == 2
        assert resumed.bytes_copied == 3
        assert len(destination_backend.objects) == 2
        report = await destination.validate_inventory("tenant-a")
        assert (report.objects, report.bytes, report.verified, report.corrupt) == (2, 3, 2, ())

    asyncio.run(scenario())


class StreamingSinkBackend(MemoryBackend):
    def __init__(self) -> None:
        super().__init__(StorageBackend.S3)
        self.metadata: ObjectMetadata | None = None

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        size = 0
        async for chunk in chunks:
            size += len(chunk)
        self.metadata = ObjectMetadata(
            uri=f"s3://sink/tenants/{tenant_id}/{key}",
            tenant_id=tenant_id,
            size=size,
            checksum_sha256="0" * 64,
            content_type=content_type,
            key=key,
        )
        return self.metadata

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        assert self.metadata is not None
        assert self.metadata.tenant_id == tenant_id and self.metadata.uri == uri
        return self.metadata


def test_ten_gibibyte_logical_upload_stays_below_memory_budget() -> None:
    async def source() -> AsyncIterator[bytes]:
        chunk = b"x" * (8 * 1024 * 1024)
        for _ in range(1280):
            yield chunk

    async def scenario() -> tuple[int, int]:
        backend = StreamingSinkBackend()
        tracemalloc.start()
        try:
            metadata = await VerifiedObjectStore(backend).put("tenant-a", "large.bin", source())
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        return metadata.size, peak

    size, peak = asyncio.run(scenario())
    assert size == 10 * 1024**3
    assert peak < 256 * 1024**2


def test_storage_metrics_are_published_without_tenant_labels() -> None:
    async def scenario() -> None:
        store = VerifiedObjectStore(MemoryBackend(StorageBackend.GCS))
        metadata = await store.put("secret-tenant", "item", chunks(b"payload"))
        async for _ in store.get("secret-tenant", metadata.uri):
            pass
        await store.validate_inventory("secret-tenant", verify_content=False)

    asyncio.run(scenario())
    metrics = generate_latest().decode()
    for name in (
        "amesh_storage_requests_total",
        "amesh_storage_request_duration_seconds_count",
        "amesh_storage_transfer_bytes_total",
        "amesh_storage_object_bytes",
        "amesh_storage_objects",
        "amesh_storage_corruption_total",
    ):
        assert name in metrics
    assert "secret-tenant" not in metrics
