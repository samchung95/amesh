from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class StorageBackend(StrEnum):
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"


class ObjectMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    uri: str
    tenant_id: str
    size: int = Field(ge=0)
    checksum_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content_type: str | None = None
    key: str | None = None
    backend: StorageBackend = StorageBackend.S3
    version_id: str | None = None
    encryption_key_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    creator: str = "system"
    lineage: tuple[str, ...] = ()
    retention_until: datetime | None = None
    legal_hold: bool = False


class ObjectLifecycleResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: ObjectMetadata
    deleted: bool = False
    deletion_marker: bool = False
    blocked_by: str | None = None


class StorageMigrationCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_backend: StorageBackend
    destination_backend: StorageBackend
    last_key: str | None = None
    objects_copied: int = Field(default=0, ge=0)
    bytes_copied: int = Field(default=0, ge=0)
    complete: bool = False


class ObjectStore(Protocol):
    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata: ...

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]: ...

    async def delete(self, tenant_id: str, uri: str) -> None: ...


class ObjectStorageBackend(ObjectStore, Protocol):
    @property
    def backend(self) -> StorageBackend: ...

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
        creator: str = "system",
        lineage: tuple[str, ...] = (),
    ) -> ObjectMetadata: ...

    def get_range(
        self,
        tenant_id: str,
        uri: str,
        start: int,
        end_exclusive: int,
    ) -> AsyncIterator[bytes]: ...

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata: ...

    def get_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> AsyncIterator[bytes]: ...

    async def head_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> ObjectMetadata: ...

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]: ...

    async def set_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
    ) -> ObjectMetadata: ...
