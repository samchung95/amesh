from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import aioboto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]

from amesh.ports import ObjectMetadata, StorageBackend
from amesh.storage.keys import (
    decode_lineage,
    encode_lineage,
    parse_tenant_uri,
    relative_tenant_key,
    tenant_object_key,
    validate_byte_range,
)

_PART_BYTES = 5 * 1024 * 1024


class S3ObjectStore:
    def __init__(
        self,
        *,
        endpoint: str,
        region: str,
        bucket: str,
        access_key: str | None,
        secret_key: str | None,
        encryption_key_id: str | None = None,
        proxy_url: str | None = None,
        ca_file: str | None = None,
        session: Any | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._region = region
        self._bucket = bucket
        self._encryption_key_id = encryption_key_id
        self._verify: bool | str = ca_file or True
        self._config = Config(
            proxies={"http": proxy_url, "https": proxy_url} if proxy_url else None,
        )
        self._session = session or aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    @property
    def backend(self) -> StorageBackend:
        return StorageBackend.S3

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
        object_key = self._tenant_key(tenant_id, key)
        created_at = datetime.now(UTC)
        digest = hashlib.sha256()
        size = 0
        parts: list[dict[str, object]] = []
        buffer = bytearray()
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint,
            region_name=self._region,
            verify=self._verify,
            config=self._config,
        ) as client:
            encryption = self._encryption_parameters()
            upload = await client.create_multipart_upload(
                Bucket=self._bucket,
                Key=object_key,
                Metadata={
                    "amesh-created-at": created_at.isoformat(),
                    "amesh-creator": creator,
                    "amesh-lineage": encode_lineage(lineage),
                },
                **encryption,
                **({"ContentType": content_type} if content_type else {}),
            )
            upload_id = str(upload["UploadId"])
            try:
                async for chunk in chunks:
                    if not chunk:
                        continue
                    digest.update(chunk)
                    size += len(chunk)
                    buffer.extend(chunk)
                    while len(buffer) >= _PART_BYTES:
                        part = bytes(buffer[:_PART_BYTES])
                        del buffer[:_PART_BYTES]
                        parts.append(
                            await self._upload_part(
                                client,
                                object_key,
                                upload_id,
                                len(parts) + 1,
                                part,
                            )
                        )
                if buffer or not parts:
                    parts.append(
                        await self._upload_part(
                            client,
                            object_key,
                            upload_id,
                            len(parts) + 1,
                            bytes(buffer),
                        )
                    )
                await client.complete_multipart_upload(
                    Bucket=self._bucket,
                    Key=object_key,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )
                await client.put_object_tagging(
                    Bucket=self._bucket,
                    Key=object_key,
                    Tagging={"TagSet": [{"Key": "amesh-sha256", "Value": digest.hexdigest()}]},
                )
            except Exception:
                await client.abort_multipart_upload(
                    Bucket=self._bucket,
                    Key=object_key,
                    UploadId=upload_id,
                )
                raise
        return ObjectMetadata(
            uri=f"s3://{self._bucket}/{object_key}",
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
            async with self._session.client(
                "s3",
                endpoint_url=self._endpoint,
                region_name=self._region,
                verify=self._verify,
                config=self._config,
            ) as client:
                response = await client.get_object(
                    Bucket=self._bucket,
                    Key=object_key,
                    **({"VersionId": version_id} if version_id is not None else {}),
                    **(
                        {"Range": f"bytes={byte_range[0]}-{byte_range[1] - 1}"}
                        if byte_range is not None
                        else {}
                    ),
                )
                body = response["Body"]
                try:
                    while chunk := await body.read(64 * 1024):
                        yield bytes(chunk)
                finally:
                    body.close()

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        object_key = self._uri_key(tenant_id, uri)
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint,
            region_name=self._region,
            verify=self._verify,
            config=self._config,
        ) as client:
            await client.delete_object(Bucket=self._bucket, Key=object_key)

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
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint,
            region_name=self._region,
            verify=self._verify,
            config=self._config,
        ) as client:
            version = {"VersionId": version_id} if version_id is not None else {}
            response = await client.head_object(Bucket=self._bucket, Key=object_key, **version)
            tags = await client.get_object_tagging(
                Bucket=self._bucket,
                Key=object_key,
                **version,
            )
        values = {item["Key"]: item["Value"] for item in tags.get("TagSet", [])}
        return self._metadata(tenant_id, object_key, response, values)

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        async def objects() -> AsyncIterator[ObjectMetadata]:
            prefix = f"tenants/{tenant_id}/"
            async with self._session.client(
                "s3",
                endpoint_url=self._endpoint,
                region_name=self._region,
                verify=self._verify,
                config=self._config,
            ) as client:
                paginator = client.get_paginator("list_objects_v2")
                async for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
                    for item in page.get("Contents", []):
                        object_key = str(item["Key"])
                        uri = f"s3://{self._bucket}/{object_key}"
                        yield await self.head(tenant_id, uri)

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
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint,
            region_name=self._region,
            verify=self._verify,
            config=self._config,
        ) as client:
            existing = await client.get_object_tagging(Bucket=self._bucket, Key=object_key)
            values = {item["Key"]: item["Value"] for item in existing.get("TagSet", [])}
            if retention_until is None:
                values.pop("amesh-retention-until", None)
            else:
                values["amesh-retention-until"] = retention_until.isoformat()
            values["amesh-legal-hold"] = str(legal_hold).lower()
            await client.put_object_tagging(
                Bucket=self._bucket,
                Key=object_key,
                Tagging={
                    "TagSet": [
                        {"Key": key, "Value": value} for key, value in sorted(values.items())
                    ]
                },
            )
        return await self.head(tenant_id, uri)

    async def _upload_part(
        self,
        client: object,
        object_key: str,
        upload_id: str,
        part_number: int,
        body: bytes,
    ) -> dict[str, object]:
        response = await client.upload_part(  # type: ignore[attr-defined]
            Bucket=self._bucket,
            Key=object_key,
            UploadId=upload_id,
            PartNumber=part_number,
            Body=body,
        )
        return {"ETag": response["ETag"], "PartNumber": part_number}

    def _tenant_key(self, tenant_id: str, key: str) -> str:
        return tenant_object_key(tenant_id, key)

    def _uri_key(self, tenant_id: str, uri: str) -> str:
        return parse_tenant_uri(tenant_id, uri, scheme="s3", container=self._bucket)

    def _metadata(
        self,
        tenant_id: str,
        object_key: str,
        response: dict[str, object],
        tags: dict[str, str],
    ) -> ObjectMetadata:
        checksum = tags.get("amesh-sha256")
        if checksum is None:
            raise ValueError(f"object s3://{self._bucket}/{object_key} has no SHA-256 metadata")
        retention = tags.get("amesh-retention-until")
        content_length = response["ContentLength"]
        if not isinstance(content_length, int):
            raise ValueError("S3 object ContentLength is invalid")
        content_type = response.get("ContentType")
        version_id = response.get("VersionId")
        encryption_key_id = response.get("SSEKMSKeyId")
        provider_metadata = response.get("Metadata")
        custom = provider_metadata if isinstance(provider_metadata, dict) else {}
        created_at = custom.get("amesh-created-at")
        provider_created_at = response.get("LastModified")
        return ObjectMetadata(
            uri=f"s3://{self._bucket}/{object_key}",
            tenant_id=tenant_id,
            size=content_length,
            checksum_sha256=checksum,
            content_type=content_type if isinstance(content_type, str) else None,
            key=relative_tenant_key(tenant_id, object_key),
            backend=self.backend,
            version_id=version_id if isinstance(version_id, str) else None,
            encryption_key_id=(
                encryption_key_id if isinstance(encryption_key_id, str) else self._encryption_key_id
            ),
            created_at=(
                datetime.fromisoformat(created_at)
                if isinstance(created_at, str)
                else provider_created_at
                if isinstance(provider_created_at, datetime)
                else datetime.now(UTC)
            ),
            creator=str(custom.get("amesh-creator", "system")),
            lineage=decode_lineage(
                custom.get("amesh-lineage")
                if isinstance(custom.get("amesh-lineage"), str)
                else None
            ),
            retention_until=datetime.fromisoformat(retention) if retention else None,
            legal_hold=tags.get("amesh-legal-hold") == "true",
        )

    def _encryption_parameters(self) -> dict[str, str]:
        if self._encryption_key_id is None:
            return {}
        return {
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self._encryption_key_id,
        }
