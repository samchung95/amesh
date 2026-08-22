from __future__ import annotations

import asyncio
import hashlib
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, datetime
from tempfile import SpooledTemporaryFile
from time import perf_counter

from pydantic import BaseModel, ConfigDict, Field

from amesh.observability import (
    STORAGE_CORRUPTION,
    STORAGE_OBJECT_BYTES,
    STORAGE_OBJECTS,
    STORAGE_REQUEST_DURATION,
    STORAGE_REQUESTS,
    STORAGE_TRANSFER_BYTES,
)
from amesh.ports import (
    ObjectLifecycleResult,
    ObjectMetadata,
    ObjectStorageBackend,
    StorageBackend,
    StorageMigrationCheckpoint,
)


class ObjectIntegrityError(RuntimeError):
    """Raised before object bytes are yielded when integrity verification fails."""


class ObjectLifecycleBlocked(RuntimeError):
    """Raised when retention, legal hold or a reference prevents deletion."""


class StorageValidationReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    backend: str
    objects: int = Field(ge=0)
    bytes: int = Field(ge=0)
    verified: int = Field(ge=0)
    corrupt: tuple[str, ...] = ()


CheckpointWriter = Callable[[StorageMigrationCheckpoint], Awaitable[None]]


class VerifiedObjectStore:
    """Integrity, consistency, lifecycle and migration policy over one storage backend."""

    def __init__(
        self,
        backend: ObjectStorageBackend,
        *,
        consistency_attempts: int = 5,
        consistency_delay_seconds: float = 0.1,
        spool_memory_bytes: int = 8 * 1024 * 1024,
    ) -> None:
        if consistency_attempts < 1:
            raise ValueError("consistency_attempts must be positive")
        if consistency_delay_seconds < 0:
            raise ValueError("consistency_delay_seconds cannot be negative")
        if spool_memory_bytes < 64 * 1024:
            raise ValueError("spool_memory_bytes must be at least 64 KiB")
        self._backend = backend
        self._consistency_attempts = consistency_attempts
        self._consistency_delay_seconds = consistency_delay_seconds
        self._spool_memory_bytes = spool_memory_bytes

    @property
    def backend(self) -> StorageBackend:
        return self._backend.backend

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        started = perf_counter()
        try:
            metadata = await self._backend.put(
                tenant_id,
                key,
                chunks,
                content_type=content_type,
            )
            visible = await self._wait_until_visible(tenant_id, metadata)
            if visible.size != metadata.size or visible.checksum_sha256 != metadata.checksum_sha256:
                self._corrupt()
                raise ObjectIntegrityError(f"read-after-write metadata mismatch for {metadata.uri}")
            STORAGE_TRANSFER_BYTES.labels(self.backend.value, "write").inc(metadata.size)
            self._request("put", "success", started)
            return visible
        except Exception:
            self._request("put", "error", started)
            raise

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        async def verified_chunks() -> AsyncIterator[bytes]:
            started = perf_counter()
            size = 0
            try:
                metadata = await self._backend.head(tenant_id, uri)
                digest = hashlib.sha256()
                with SpooledTemporaryFile(max_size=self._spool_memory_bytes, mode="w+b") as spool:
                    async for chunk in self._backend.get(tenant_id, uri):
                        if not chunk:
                            continue
                        size += len(chunk)
                        digest.update(chunk)
                        spool.write(chunk)
                    if size != metadata.size or digest.hexdigest() != metadata.checksum_sha256:
                        self._corrupt()
                        raise ObjectIntegrityError(f"checksum verification failed for {uri}")
                    STORAGE_TRANSFER_BYTES.labels(self.backend.value, "read").inc(size)
                    spool.seek(0)
                    while chunk := spool.read(64 * 1024):
                        yield chunk
                self._request("get", "success", started)
            except Exception:
                self._request("get", "error", started)
                raise

        return verified_chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        started = perf_counter()
        try:
            await self._backend.delete(tenant_id, uri)
            self._request("delete", "success", started)
        except Exception:
            self._request("delete", "error", started)
            raise

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        started = perf_counter()
        try:
            metadata = await self._backend.head(tenant_id, uri)
            self._request("head", "success", started)
            return metadata
        except Exception:
            self._request("head", "error", started)
            raise

    def get_version(self, tenant_id: str, metadata: ObjectMetadata) -> AsyncIterator[bytes]:
        if metadata.tenant_id != tenant_id:
            raise ValueError("object metadata belongs to another tenant")
        version_id = metadata.version_id
        if version_id is None:
            return self.get(tenant_id, metadata.uri)

        async def verified_chunks() -> AsyncIterator[bytes]:
            started = perf_counter()
            size = 0
            try:
                selected = await self._backend.head_version(
                    tenant_id,
                    metadata.uri,
                    version_id,
                )
                if (
                    selected.version_id != version_id
                    or selected.size != metadata.size
                    or selected.checksum_sha256 != metadata.checksum_sha256
                ):
                    self._corrupt()
                    raise ObjectIntegrityError(
                        f"version metadata mismatch for {metadata.uri}@{version_id}"
                    )
                digest = hashlib.sha256()
                with SpooledTemporaryFile(max_size=self._spool_memory_bytes, mode="w+b") as spool:
                    async for chunk in self._backend.get_version(
                        tenant_id,
                        metadata.uri,
                        version_id,
                    ):
                        if not chunk:
                            continue
                        size += len(chunk)
                        digest.update(chunk)
                        spool.write(chunk)
                    if size != metadata.size or digest.hexdigest() != metadata.checksum_sha256:
                        self._corrupt()
                        raise ObjectIntegrityError(
                            f"version checksum verification failed for {metadata.uri}"
                        )
                    STORAGE_TRANSFER_BYTES.labels(self.backend.value, "read").inc(size)
                    spool.seek(0)
                    while chunk := spool.read(64 * 1024):
                        yield chunk
                self._request("get_version", "success", started)
            except Exception:
                self._request("get_version", "error", started)
                raise

        return verified_chunks()

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        return self._backend.iter_objects(tenant_id)

    async def apply_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
        referenced: bool,
        delete: bool = False,
    ) -> ObjectLifecycleResult:
        if retention_until is not None and retention_until.tzinfo is None:
            raise ValueError("retention_until must be timezone-aware")
        metadata = await self._backend.set_lifecycle(
            tenant_id,
            uri,
            retention_until=retention_until,
            legal_hold=legal_hold,
        )
        if not delete:
            return ObjectLifecycleResult(metadata=metadata)
        blocked_by = None
        if referenced:
            blocked_by = "referenced"
        elif legal_hold:
            blocked_by = "legal_hold"
        elif retention_until is not None and retention_until > datetime.now(UTC):
            blocked_by = "retention"
        if blocked_by is not None:
            return ObjectLifecycleResult(metadata=metadata, blocked_by=blocked_by)
        await self.delete(tenant_id, uri)
        return ObjectLifecycleResult(metadata=metadata, deleted=True, deletion_marker=True)

    async def migrate_to(
        self,
        destination: VerifiedObjectStore,
        tenant_id: str,
        *,
        checkpoint: StorageMigrationCheckpoint | None = None,
        write_checkpoint: CheckpointWriter | None = None,
    ) -> StorageMigrationCheckpoint:
        current = checkpoint or StorageMigrationCheckpoint(
            source_backend=self.backend,
            destination_backend=destination.backend,
        )
        if current.source_backend is not self.backend:
            raise ValueError("checkpoint source backend does not match")
        if current.destination_backend is not destination.backend:
            raise ValueError("checkpoint destination backend does not match")
        if current.complete:
            return current
        async for metadata in self.iter_objects(tenant_id):
            if metadata.key is None:
                raise ValueError(f"object {metadata.uri} has no resumable key")
            if current.last_key is not None and metadata.key <= current.last_key:
                continue
            copied = await destination.put(
                tenant_id,
                metadata.key,
                self.get(tenant_id, metadata.uri),
                content_type=metadata.content_type,
            )
            if copied.checksum_sha256 != metadata.checksum_sha256:
                destination._corrupt()
                raise ObjectIntegrityError(f"migration checksum mismatch for {metadata.uri}")
            current = current.model_copy(
                update={
                    "last_key": metadata.key,
                    "objects_copied": current.objects_copied + 1,
                    "bytes_copied": current.bytes_copied + metadata.size,
                }
            )
            if write_checkpoint is not None:
                await write_checkpoint(current)
        current = current.model_copy(update={"complete": True})
        if write_checkpoint is not None:
            await write_checkpoint(current)
        return current

    async def validate_inventory(
        self,
        tenant_id: str,
        *,
        verify_content: bool = True,
    ) -> StorageValidationReport:
        objects = 0
        total_bytes = 0
        verified = 0
        corrupt: list[str] = []
        async for metadata in self.iter_objects(tenant_id):
            objects += 1
            total_bytes += metadata.size
            if not verify_content:
                continue
            try:
                async for _ in self.get(tenant_id, metadata.uri):
                    pass
            except ObjectIntegrityError:
                corrupt.append(metadata.uri)
            else:
                verified += 1
        STORAGE_OBJECTS.labels(self.backend.value).set(objects)
        STORAGE_OBJECT_BYTES.labels(self.backend.value).set(total_bytes)
        return StorageValidationReport(
            backend=self.backend.value,
            objects=objects,
            bytes=total_bytes,
            verified=verified,
            corrupt=tuple(corrupt),
        )

    async def _wait_until_visible(
        self,
        tenant_id: str,
        metadata: ObjectMetadata,
    ) -> ObjectMetadata:
        last_error: Exception | None = None
        for attempt in range(self._consistency_attempts):
            try:
                return await self._backend.head(tenant_id, metadata.uri)
            except Exception as exc:
                last_error = exc
                if attempt + 1 < self._consistency_attempts:
                    await asyncio.sleep(self._consistency_delay_seconds * (attempt + 1))
        assert last_error is not None
        raise last_error

    def _request(self, operation: str, outcome: str, started: float) -> None:
        STORAGE_REQUESTS.labels(self.backend.value, operation, outcome).inc()
        STORAGE_REQUEST_DURATION.labels(self.backend.value, operation).observe(
            perf_counter() - started
        )

    def _corrupt(self) -> None:
        STORAGE_CORRUPTION.labels(self.backend.value).inc()
