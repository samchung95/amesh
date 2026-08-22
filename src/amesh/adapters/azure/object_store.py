from __future__ import annotations

import base64
import hashlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from amesh.ports import ObjectMetadata, StorageBackend
from amesh.storage.keys import (
    decode_lineage,
    encode_lineage,
    parse_tenant_uri,
    relative_tenant_key,
    tenant_object_key,
    validate_byte_range,
)

_PART_BYTES = 4 * 1024 * 1024


class AzureBlobObjectStore:
    def __init__(
        self,
        *,
        account_url: str,
        container: str,
        account_key: str | None = None,
        encryption_key_id: str | None = None,
        proxy_url: str | None = None,
        ca_file: str | None = None,
        service_client: Any | None = None,
    ) -> None:
        self._account_url = account_url
        self._container = container
        self._account_key = account_key
        self._encryption_key_id = encryption_key_id
        self._proxy_url = proxy_url
        self._ca_file = ca_file
        self._injected_client = service_client

    @property
    def backend(self) -> StorageBackend:
        return StorageBackend.AZURE

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
        creator: str = "system",
        lineage: tuple[str, ...] = (),
    ) -> ObjectMetadata:
        object_key = tenant_object_key(tenant_id, key)
        created_at = datetime.now(UTC)
        digest = hashlib.sha256()
        size = 0
        block_ids: list[str] = []
        buffer = bytearray()
        async with self._service() as service:
            blob = service.get_blob_client(container=self._container, blob=object_key)
            async for chunk in chunks:
                if not chunk:
                    continue
                digest.update(chunk)
                size += len(chunk)
                buffer.extend(chunk)
                while len(buffer) >= _PART_BYTES:
                    block_ids.append(
                        await self._stage_block(
                            blob, len(block_ids) + 1, bytes(buffer[:_PART_BYTES])
                        )
                    )
                    del buffer[:_PART_BYTES]
            if buffer or not block_ids:
                block_ids.append(await self._stage_block(blob, len(block_ids) + 1, bytes(buffer)))
            await blob.commit_block_list(
                block_ids,
                content_settings=ContentSettings(content_type=content_type),
                metadata={
                    "amesh_sha256": digest.hexdigest(),
                    "amesh_created_at": created_at.isoformat(),
                    "amesh_creator": creator,
                    "amesh_lineage": encode_lineage(lineage),
                },
                **self._encryption_parameters(),
            )
        return ObjectMetadata(
            uri=f"azure://{self._container}/{object_key}",
            tenant_id=tenant_id,
            size=size,
            checksum_sha256=digest.hexdigest(),
            content_type=content_type,
            key=key.strip("/"),
            backend=self.backend,
            encryption_key_id=self._encryption_key_id,
            created_at=created_at,
            creator=creator,
            lineage=lineage,
        )

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        return self._get(tenant_id, uri, version_id=None, byte_range=None)

    def get_range(
        self,
        tenant_id: str,
        uri: str,
        start: int,
        end_exclusive: int,
    ) -> AsyncIterator[bytes]:
        return self._get(
            tenant_id,
            uri,
            version_id=None,
            byte_range=validate_byte_range(start, end_exclusive),
        )

    def get_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> AsyncIterator[bytes]:
        return self._get(tenant_id, uri, version_id=version_id, byte_range=None)

    def _get(
        self,
        tenant_id: str,
        uri: str,
        *,
        version_id: str | None,
        byte_range: tuple[int, int] | None,
    ) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            object_key = self._uri_key(tenant_id, uri)
            async with self._service() as service:
                options = {"version_id": version_id} if version_id is not None else {}
                blob = service.get_blob_client(
                    container=self._container,
                    blob=object_key,
                    **options,
                )
                downloader = await blob.download_blob(
                    **(
                        {
                            "offset": byte_range[0],
                            "length": byte_range[1] - byte_range[0],
                        }
                        if byte_range is not None
                        else {}
                    )
                )
                async for chunk in downloader.chunks():
                    if chunk:
                        yield bytes(chunk)

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        object_key = self._uri_key(tenant_id, uri)
        async with self._service() as service:
            blob = service.get_blob_client(container=self._container, blob=object_key)
            await blob.delete_blob(delete_snapshots="include")

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return await self._head(tenant_id, uri, version_id=None)

    async def head_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> ObjectMetadata:
        return await self._head(tenant_id, uri, version_id=version_id)

    async def _head(
        self,
        tenant_id: str,
        uri: str,
        *,
        version_id: str | None,
    ) -> ObjectMetadata:
        object_key = self._uri_key(tenant_id, uri)
        async with self._service() as service:
            options = {"version_id": version_id} if version_id is not None else {}
            blob = service.get_blob_client(
                container=self._container,
                blob=object_key,
                **options,
            )
            properties = await blob.get_blob_properties()
        return self._metadata(tenant_id, object_key, properties)

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        async def objects() -> AsyncIterator[ObjectMetadata]:
            prefix = f"tenants/{tenant_id}/"
            async with self._service() as service:
                container = service.get_container_client(self._container)
                async for item in container.list_blobs(
                    name_starts_with=prefix, include=["metadata"]
                ):
                    yield self._metadata(tenant_id, str(item.name), item)

        return objects()

    async def set_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
    ) -> ObjectMetadata:
        object_key = self._uri_key(tenant_id, uri)
        async with self._service() as service:
            blob = service.get_blob_client(container=self._container, blob=object_key)
            properties = await blob.get_blob_properties()
            metadata = dict(properties.metadata or {})
            if retention_until is None:
                metadata.pop("amesh_retention_until", None)
            else:
                metadata["amesh_retention_until"] = retention_until.isoformat()
            metadata["amesh_legal_hold"] = str(legal_hold).lower()
            await blob.set_blob_metadata(metadata)
            properties = await blob.get_blob_properties()
        return self._metadata(tenant_id, object_key, properties)

    async def _stage_block(self, blob: Any, number: int, data: bytes) -> str:
        block_id = base64.b64encode(number.to_bytes(8, "big")).decode()
        await blob.stage_block(block_id=block_id, data=data, **self._encryption_parameters())
        return block_id

    @asynccontextmanager
    async def _service(self) -> AsyncIterator[Any]:
        if self._injected_client is not None:
            yield self._injected_client
            return
        credential: Any = self._account_key
        owned_credential: DefaultAzureCredential | None = None
        if credential is None:
            owned_credential = DefaultAzureCredential()
            credential = owned_credential
        kwargs: dict[str, object] = {}
        if self._proxy_url is not None:
            kwargs["proxies"] = {"http": self._proxy_url, "https": self._proxy_url}
        if self._ca_file is not None:
            kwargs["connection_verify"] = self._ca_file
        try:
            async with BlobServiceClient(
                account_url=self._account_url,
                credential=credential,
                **kwargs,  # type: ignore[arg-type]
            ) as service:
                yield service
        finally:
            if owned_credential is not None:
                await owned_credential.close()

    def _uri_key(self, tenant_id: str, uri: str) -> str:
        return parse_tenant_uri(
            tenant_id,
            uri,
            scheme="azure",
            container=self._container,
        )

    def _metadata(self, tenant_id: str, object_key: str, properties: Any) -> ObjectMetadata:
        metadata = dict(properties.metadata or {})
        checksum = metadata.get("amesh_sha256")
        if checksum is None:
            raise ValueError(
                f"object azure://{self._container}/{object_key} has no SHA-256 metadata"
            )
        retention = metadata.get("amesh_retention_until")
        created_at = metadata.get("amesh_created_at")
        provider_created_at = getattr(properties, "creation_time", None)
        content_settings = getattr(properties, "content_settings", None)
        return ObjectMetadata(
            uri=f"azure://{self._container}/{object_key}",
            tenant_id=tenant_id,
            size=int(properties.size),
            checksum_sha256=checksum,
            content_type=getattr(content_settings, "content_type", None),
            key=relative_tenant_key(tenant_id, object_key),
            backend=self.backend,
            version_id=getattr(properties, "version_id", None),
            encryption_key_id=(
                getattr(properties, "encryption_scope", None) or self._encryption_key_id
            ),
            created_at=(
                datetime.fromisoformat(created_at)
                if created_at
                else provider_created_at or datetime.now(UTC)
            ),
            creator=metadata.get("amesh_creator", "system"),
            lineage=decode_lineage(metadata.get("amesh_lineage")),
            retention_until=datetime.fromisoformat(retention) if retention else None,
            legal_hold=metadata.get("amesh_legal_hold") == "true",
        )

    def _encryption_parameters(self) -> dict[str, str]:
        if self._encryption_key_id is None:
            return {}
        return {"encryption_scope": self._encryption_key_id}
