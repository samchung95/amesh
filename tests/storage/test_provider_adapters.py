from __future__ import annotations

import asyncio
import io
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest

from amesh.adapters.azure import AzureBlobObjectStore
from amesh.adapters.gcs import GoogleCloudStorageObjectStore
from amesh.adapters.s3 import S3ObjectStore


async def chunks(*values: bytes) -> AsyncIterator[bytes]:
    for value in values:
        yield value


class FakeBody:
    def __init__(self, content: bytes) -> None:
        self.content = content
        self.offset = 0

    async def __aenter__(self) -> FakeBody:
        return self

    async def __aexit__(self, *args: object) -> None:
        pass

    async def iter_chunks(self, *, chunk_size: int) -> AsyncIterator[bytes]:
        for offset in range(0, len(self.content), chunk_size):
            yield self.content[offset : offset + chunk_size]

    async def read(self, chunk_size: int) -> bytes:
        chunk = self.content[self.offset : self.offset + chunk_size]
        self.offset += len(chunk)
        return chunk

    def close(self) -> None:
        pass


class FakePaginator:
    def __init__(self, client: FakeS3Client) -> None:
        self.client = client

    async def paginate(self, *, Bucket: str, Prefix: str) -> AsyncIterator[dict[str, object]]:
        del Bucket
        yield {
            "Contents": [
                {"Key": key} for key in sorted(self.client.objects) if key.startswith(Prefix)
            ]
        }


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.tags: dict[str, list[dict[str, str]]] = {}
        self.uploads: dict[str, dict[int, bytes]] = {}
        self.upload_options: dict[str, dict[str, object]] = {}

    async def __aenter__(self) -> FakeS3Client:
        return self

    async def __aexit__(self, *args: object) -> None:
        pass

    async def create_multipart_upload(self, *, Bucket: str, Key: str, **kwargs: object):
        del Bucket
        self.uploads[Key] = {}
        self.upload_options[Key] = kwargs
        return {"UploadId": Key}

    async def upload_part(
        self,
        *,
        Bucket: str,
        Key: str,
        UploadId: str,
        PartNumber: int,
        Body: bytes,
    ) -> dict[str, str]:
        del Bucket, UploadId
        self.uploads[Key][PartNumber] = Body
        return {"ETag": f"part-{PartNumber}"}

    async def complete_multipart_upload(self, *, Bucket: str, Key: str, **kwargs: object) -> None:
        del Bucket, kwargs
        self.objects[Key] = b"".join(self.uploads.pop(Key).values())

    async def abort_multipart_upload(self, **kwargs: object) -> None:
        self.uploads.pop(str(kwargs["Key"]), None)

    async def put_object_tagging(
        self, *, Bucket: str, Key: str, Tagging: dict[str, object]
    ) -> None:
        del Bucket
        self.tags[Key] = list(Tagging["TagSet"])  # type: ignore[arg-type]

    async def get_object_tagging(
        self, *, Bucket: str, Key: str, VersionId: str | None = None
    ) -> dict[str, object]:
        del Bucket, VersionId
        return {"TagSet": self.tags.get(Key, [])}

    async def head_object(
        self, *, Bucket: str, Key: str, VersionId: str | None = None
    ) -> dict[str, object]:
        del Bucket, VersionId
        options = self.upload_options[Key]
        return {
            "ContentLength": len(self.objects[Key]),
            "ContentType": options.get("ContentType"),
            "Metadata": options.get("Metadata", {}),
            "SSEKMSKeyId": options.get("SSEKMSKeyId"),
            "VersionId": "v1",
        }

    async def get_object(
        self,
        *,
        Bucket: str,
        Key: str,
        VersionId: str | None = None,
        Range: str | None = None,
    ) -> dict[str, object]:
        del Bucket, VersionId
        content = self.objects[Key]
        if Range is not None:
            start, end = (int(value) for value in Range.removeprefix("bytes=").split("-"))
            content = content[start : end + 1]
        return {"Body": FakeBody(content)}

    async def delete_object(self, *, Bucket: str, Key: str) -> None:
        del Bucket
        self.objects.pop(Key)

    def get_paginator(self, name: str) -> FakePaginator:
        assert name == "list_objects_v2"
        return FakePaginator(self)


class FakeS3Session:
    def __init__(self, client: FakeS3Client) -> None:
        self.client_instance = client

    def client(self, *args: object, **kwargs: object) -> FakeS3Client:
        del args, kwargs
        return self.client_instance


def test_s3_adapter_conformance() -> None:
    async def scenario() -> None:
        client = FakeS3Client()
        store = S3ObjectStore(
            endpoint="https://s3.private.example",
            region="us-east-1",
            bucket="amesh",
            access_key=None,
            secret_key=None,
            encryption_key_id="kms-key",
            proxy_url="http://proxy:8080",
            ca_file="/ca.pem",
            session=FakeS3Session(client),
        )
        written = await store.put(
            "tenant-a",
            "report.bin",
            chunks(b"abc", b"def"),
            creator="principal-a",
            lineage=("execution:123",),
        )
        assert written.size == 6 and written.encryption_key_id == "kms-key"
        assert written.creator == "principal-a" and written.lineage == ("execution:123",)
        assert b"".join([part async for part in store.get("tenant-a", written.uri)]) == b"abcdef"
        assert (
            b"".join([part async for part in store.get_range("tenant-a", written.uri, 1, 5)])
            == b"bcde"
        )
        versioned = await store.head("tenant-a", written.uri)
        assert (
            b"".join(
                [
                    part
                    async for part in store.get_version(
                        "tenant-a", written.uri, versioned.version_id or ""
                    )
                ]
            )
            == b"abcdef"
        )
        updated = await store.set_lifecycle(
            "tenant-a", written.uri, retention_until=None, legal_hold=True
        )
        assert updated.legal_hold
        assert [item.key async for item in store.iter_objects("tenant-a")] == ["report.bin"]
        with pytest.raises(ValueError, match="tenant storage prefix"):
            await store.head("tenant-b", written.uri)
        await store.delete("tenant-a", written.uri)
        assert not client.objects

    asyncio.run(scenario())


class FakeAzureDownloader:
    def __init__(self, content: bytes) -> None:
        self.content = content

    async def chunks(self) -> AsyncIterator[bytes]:
        yield self.content


class FakeAzureBlob:
    def __init__(self, name: str) -> None:
        self.name = name
        self.blocks: dict[str, bytes] = {}
        self.content = b""
        self.metadata: dict[str, str] = {}
        self.content_type: str | None = None
        self.encryption_scope: str | None = None

    async def stage_block(self, *, block_id: str, data: bytes, **kwargs: object) -> None:
        self.blocks[block_id] = data
        self.encryption_scope = kwargs.get("encryption_scope")  # type: ignore[assignment]

    async def commit_block_list(self, block_ids: list[str], **kwargs: object) -> None:
        self.content = b"".join(self.blocks[item] for item in block_ids)
        self.metadata = dict(kwargs["metadata"])  # type: ignore[arg-type]
        settings = kwargs["content_settings"]
        self.content_type = settings.content_type  # type: ignore[attr-defined]

    async def download_blob(
        self, *, offset: int | None = None, length: int | None = None
    ) -> FakeAzureDownloader:
        start = offset or 0
        end = None if length is None else start + length
        return FakeAzureDownloader(self.content[start:end])

    async def delete_blob(self, **kwargs: object) -> None:
        del kwargs
        self.content = b""

    async def get_blob_properties(self) -> SimpleNamespace:
        return self.properties()

    async def set_blob_metadata(self, metadata: dict[str, str]) -> None:
        self.metadata = metadata

    def properties(self) -> SimpleNamespace:
        return SimpleNamespace(
            name=self.name,
            size=len(self.content),
            metadata=self.metadata,
            content_settings=SimpleNamespace(content_type=self.content_type),
            version_id="v1",
            encryption_scope=self.encryption_scope,
        )


class FakeAzureContainer:
    def __init__(self, blobs: dict[str, FakeAzureBlob]) -> None:
        self.blobs = blobs

    async def list_blobs(self, *, name_starts_with: str, include: list[str]):
        del include
        for key in sorted(self.blobs):
            if key.startswith(name_starts_with) and self.blobs[key].content:
                yield self.blobs[key].properties()


class FakeAzureService:
    def __init__(self) -> None:
        self.blobs: dict[str, FakeAzureBlob] = {}

    def get_blob_client(
        self, *, container: str, blob: str, version_id: str | None = None
    ) -> FakeAzureBlob:
        del container, version_id
        return self.blobs.setdefault(blob, FakeAzureBlob(blob))

    def get_container_client(self, container: str) -> FakeAzureContainer:
        del container
        return FakeAzureContainer(self.blobs)


def test_azure_adapter_conformance() -> None:
    async def scenario() -> None:
        client = FakeAzureService()
        store = AzureBlobObjectStore(
            account_url="https://account.blob.core.windows.net",
            container="amesh",
            encryption_key_id="scope-a",
            service_client=client,
        )
        written = await store.put(
            "tenant-a",
            "report.bin",
            chunks(b"azure"),
            creator="principal-a",
            lineage=("execution:123",),
        )
        assert written.size == 5 and written.encryption_key_id == "scope-a"
        assert written.creator == "principal-a" and written.lineage == ("execution:123",)
        assert b"".join([part async for part in store.get("tenant-a", written.uri)]) == b"azure"
        assert (
            b"".join([part async for part in store.get_range("tenant-a", written.uri, 1, 4)])
            == b"zur"
        )
        versioned = await store.head("tenant-a", written.uri)
        assert (
            b"".join(
                [
                    part
                    async for part in store.get_version(
                        "tenant-a", written.uri, versioned.version_id or ""
                    )
                ]
            )
            == b"azure"
        )
        updated = await store.set_lifecycle(
            "tenant-a", written.uri, retention_until=None, legal_hold=True
        )
        assert updated.legal_hold
        assert [item.key async for item in store.iter_objects("tenant-a")] == ["report.bin"]
        with pytest.raises(ValueError, match="tenant storage prefix"):
            await store.head("tenant-b", written.uri)

    asyncio.run(scenario())


class CallbackBytesIO(io.BytesIO):
    def __init__(self, callback: Any) -> None:
        super().__init__()
        self.callback = callback

    def close(self) -> None:
        if not self.closed:
            self.callback(self.getvalue())
        super().close()

    def terminate(self) -> None:
        super().close()


class FakeGCSBlob:
    def __init__(self, name: str, *, kms_key_name: str | None = None) -> None:
        self.name = name
        self.kms_key_name = kms_key_name
        self.content = b""
        self.metadata: dict[str, str] = {}
        self.content_type: str | None = None
        self.size = 0
        self.generation = 1
        self.metageneration = 1
        self.temporary_hold = False

    def open(self, mode: str, **kwargs: object):
        if mode == "wb":
            self.content_type = kwargs.get("content_type")  # type: ignore[assignment]

            def commit(content: bytes) -> None:
                self.content = content
                self.size = len(content)

            return CallbackBytesIO(commit)
        return io.BytesIO(self.content)

    def patch(self, **kwargs: object) -> None:
        del kwargs
        self.metageneration += 1

    def reload(self) -> None:
        pass

    def delete(self, **kwargs: object) -> None:
        del kwargs
        self.content = b""
        self.size = 0


class FakeGCSBucket:
    def __init__(self) -> None:
        self.blobs: dict[str, FakeGCSBlob] = {}

    def blob(
        self,
        name: str,
        *,
        generation: int | None = None,
        kms_key_name: str | None = None,
    ) -> FakeGCSBlob:
        del generation
        return self.blobs.setdefault(name, FakeGCSBlob(name, kms_key_name=kms_key_name))


class FakeGCSClient:
    def __init__(self) -> None:
        self.bucket_instance = FakeGCSBucket()

    def bucket(self, name: str) -> FakeGCSBucket:
        del name
        return self.bucket_instance

    def list_blobs(self, bucket: str, *, prefix: str) -> list[FakeGCSBlob]:
        del bucket
        return [
            blob
            for key, blob in sorted(self.bucket_instance.blobs.items())
            if key.startswith(prefix) and blob.content
        ]


def test_gcs_adapter_conformance() -> None:
    async def scenario() -> None:
        client = FakeGCSClient()
        store = GoogleCloudStorageObjectStore(
            bucket="amesh",
            encryption_key_id="projects/p/locations/l/keyRings/r/cryptoKeys/k",
            client=client,
        )
        written = await store.put(
            "tenant-a",
            "report.bin",
            chunks(b"gcs"),
            creator="principal-a",
            lineage=("execution:123",),
        )
        assert written.size == 3 and written.version_id == "1"
        assert written.creator == "principal-a" and written.lineage == ("execution:123",)
        assert b"".join([part async for part in store.get("tenant-a", written.uri)]) == b"gcs"
        assert (
            b"".join([part async for part in store.get_range("tenant-a", written.uri, 1, 3)])
            == b"cs"
        )
        assert (
            b"".join(
                [
                    part
                    async for part in store.get_version(
                        "tenant-a", written.uri, written.version_id or ""
                    )
                ]
            )
            == b"gcs"
        )
        updated = await store.set_lifecycle(
            "tenant-a", written.uri, retention_until=None, legal_hold=True
        )
        assert updated.legal_hold
        assert [item.key async for item in store.iter_objects("tenant-a")] == ["report.bin"]
        with pytest.raises(ValueError, match="tenant storage prefix"):
            await store.head("tenant-b", written.uri)

    asyncio.run(scenario())
