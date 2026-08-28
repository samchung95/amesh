from __future__ import annotations

import asyncio
import hashlib
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import google.auth
from google.api_core.client_options import ClientOptions
from google.auth.transport.requests import AuthorizedSession
from google.cloud import storage  # type: ignore[import-untyped]
from google.oauth2 import service_account

from amesh.ports import ObjectMetadata, StorageBackend
from amesh.storage.keys import (
    decode_lineage,
    encode_lineage,
    parse_tenant_uri,
    relative_tenant_key,
    tenant_object_key,
    validate_byte_range,
)

_PART_BYTES = 8 * 1024 * 1024
_READ_BYTES = 64 * 1024


class GoogleCloudStorageObjectStore:
    def __init__(
        self,
        *,
        bucket: str,
        project: str | None = None,
        endpoint: str | None = None,
        credentials_file: str | None = None,
        encryption_key_id: str | None = None,
        proxy_url: str | None = None,
        ca_file: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._bucket = bucket
        self._project = project
        self._endpoint = endpoint
        self._credentials_file = credentials_file
        self._encryption_key_id = encryption_key_id
        self._proxy_url = proxy_url
        self._ca_file = ca_file
        self._injected_client = client

    @property
    def backend(self) -> StorageBackend:
        return StorageBackend.GCS

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
        blob = self._blob(object_key)
        writer = await asyncio.to_thread(
            blob.open,
            "wb",
            chunk_size=_PART_BYTES,
            content_type=content_type,
            ignore_flush=True,
        )
        digest = hashlib.sha256()
        size = 0
        try:
            async for chunk in chunks:
                if not chunk:
                    continue
                digest.update(chunk)
                size += len(chunk)
                await asyncio.to_thread(writer.write, chunk)
        except BaseException:
            terminate = getattr(writer, "terminate", None)
            if callable(terminate):
                await asyncio.to_thread(terminate)
            raise
        else:
            await asyncio.to_thread(writer.close)
        blob.metadata = {
            "amesh_sha256": digest.hexdigest(),
            "amesh_created_at": created_at.isoformat(),
            "amesh_creator": creator,
            "amesh_lineage": encode_lineage(lineage),
        }
        await asyncio.to_thread(blob.patch)
        await asyncio.to_thread(blob.reload)
        return self._metadata(tenant_id, object_key, blob)

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
            blob = self._blob(object_key, generation=version_id)
            reader = await asyncio.to_thread(blob.open, "rb", chunk_size=_READ_BYTES)
            try:
                remaining = None
                if byte_range is not None:
                    await asyncio.to_thread(reader.seek, byte_range[0])
                    remaining = byte_range[1] - byte_range[0]
                while remaining is None or remaining > 0:
                    read_size = _READ_BYTES if remaining is None else min(_READ_BYTES, remaining)
                    chunk = await asyncio.to_thread(reader.read, read_size)
                    if not chunk:
                        break
                    yield bytes(chunk)
                    if remaining is not None:
                        remaining -= len(chunk)
            finally:
                await asyncio.to_thread(reader.close)

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        object_key = self._uri_key(tenant_id, uri)
        blob = self._blob(object_key)
        await asyncio.to_thread(blob.reload)
        await asyncio.to_thread(blob.delete, if_generation_match=blob.generation)

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
        blob = self._blob(object_key, generation=version_id)
        await asyncio.to_thread(blob.reload)
        return self._metadata(tenant_id, object_key, blob)

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        async def objects() -> AsyncIterator[ObjectMetadata]:
            client = self._client()
            prefix = f"tenants/{tenant_id}/"
            blobs = await asyncio.to_thread(
                lambda: list(client.list_blobs(self._bucket, prefix=prefix))
            )
            for blob in blobs:
                yield self._metadata(tenant_id, str(blob.name), blob)

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
        blob = self._blob(object_key)
        await asyncio.to_thread(blob.reload)
        metadata = dict(blob.metadata or {})
        if retention_until is None:
            metadata.pop("amesh_retention_until", None)
        else:
            metadata["amesh_retention_until"] = retention_until.isoformat()
        metadata["amesh_legal_hold"] = str(legal_hold).lower()
        blob.metadata = metadata
        blob.temporary_hold = legal_hold or retention_until is not None
        await asyncio.to_thread(blob.patch, if_metageneration_match=blob.metageneration)
        await asyncio.to_thread(blob.reload)
        return self._metadata(tenant_id, object_key, blob)

    def _client(self) -> Any:
        if self._injected_client is not None:
            return self._injected_client
        credentials: Any
        project = self._project
        if self._credentials_file is not None:
            credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
                self._credentials_file,
                scopes=("https://www.googleapis.com/auth/devstorage.read_write",),
            )
        else:
            credentials, detected_project = google.auth.default(
                scopes=("https://www.googleapis.com/auth/devstorage.read_write",)
            )
            project = project or detected_project
        session = AuthorizedSession(credentials)  # type: ignore[no-untyped-call]
        if self._proxy_url is not None:
            session.proxies.update({"http": self._proxy_url, "https": self._proxy_url})
        if self._ca_file is not None:
            session.verify = self._ca_file
        options = ClientOptions(api_endpoint=self._endpoint) if self._endpoint else None
        self._injected_client = storage.Client(
            project=project,
            credentials=credentials,
            _http=session,
            client_options=options,
        )
        return self._injected_client

    def _blob(self, object_key: str, *, generation: str | None = None) -> Any:
        bucket = self._client().bucket(self._bucket)
        if generation is None:
            return bucket.blob(object_key, kms_key_name=self._encryption_key_id)
        return bucket.blob(
            object_key,
            generation=int(generation),
            kms_key_name=self._encryption_key_id,
        )

    def _uri_key(self, tenant_id: str, uri: str) -> str:
        return parse_tenant_uri(tenant_id, uri, scheme="gs", container=self._bucket)

    def _metadata(self, tenant_id: str, object_key: str, blob: Any) -> ObjectMetadata:
        metadata = dict(blob.metadata or {})
        checksum = metadata.get("amesh_sha256")
        if checksum is None:
            raise ValueError(f"object gs://{self._bucket}/{object_key} has no SHA-256 metadata")
        retention = metadata.get("amesh_retention_until")
        created_at = metadata.get("amesh_created_at")
        provider_created_at = getattr(blob, "time_created", None)
        return ObjectMetadata(
            uri=f"gs://{self._bucket}/{object_key}",
            tenant_id=tenant_id,
            size=int(blob.size),
            checksum_sha256=checksum,
            content_type=blob.content_type,
            key=relative_tenant_key(tenant_id, object_key),
            backend=self.backend,
            version_id=str(blob.generation) if blob.generation is not None else None,
            encryption_key_id=getattr(blob, "kms_key_name", None) or self._encryption_key_id,
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
