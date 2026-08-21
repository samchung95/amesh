from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator
from urllib.parse import urlsplit

import aioboto3  # type: ignore[import-untyped]

from amesh.ports import ObjectMetadata

_PART_BYTES = 5 * 1024 * 1024


class S3ObjectStore:
    def __init__(
        self,
        *,
        endpoint: str,
        region: str,
        bucket: str,
        access_key: str,
        secret_key: str,
    ) -> None:
        self._endpoint = endpoint
        self._region = region
        self._bucket = bucket
        self._session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        object_key = self._tenant_key(tenant_id, key)
        digest = hashlib.sha256()
        size = 0
        parts: list[dict[str, object]] = []
        buffer = bytearray()
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint,
            region_name=self._region,
        ) as client:
            upload = await client.create_multipart_upload(
                Bucket=self._bucket,
                Key=object_key,
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
        )

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            object_key = self._uri_key(tenant_id, uri)
            async with self._session.client(
                "s3",
                endpoint_url=self._endpoint,
                region_name=self._region,
            ) as client:
                response = await client.get_object(Bucket=self._bucket, Key=object_key)
                async with response["Body"] as body:
                    async for chunk in body.iter_chunks(chunk_size=64 * 1024):
                        if chunk:
                            yield bytes(chunk)

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        object_key = self._uri_key(tenant_id, uri)
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint,
            region_name=self._region,
        ) as client:
            await client.delete_object(Bucket=self._bucket, Key=object_key)

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
        normalized = key.strip("/")
        if not normalized or ".." in normalized.split("/"):
            raise ValueError("object key must be a non-empty normalized relative path")
        return f"tenants/{tenant_id}/{normalized}"

    def _uri_key(self, tenant_id: str, uri: str) -> str:
        parsed = urlsplit(uri)
        key = parsed.path.lstrip("/")
        prefix = f"tenants/{tenant_id}/"
        if parsed.scheme != "s3" or parsed.netloc != self._bucket or not key.startswith(prefix):
            raise ValueError("object URI is outside the tenant storage prefix")
        return key
