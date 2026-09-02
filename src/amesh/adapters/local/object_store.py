from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
import tempfile
from collections.abc import AsyncIterator
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from amesh.ports import ObjectMetadata, StorageBackend
from amesh.storage.keys import relative_tenant_key, tenant_object_key, validate_byte_range

_CHUNK_BYTES = 64 * 1024
_URI_CONTAINER = "storage"


class LocalFilesystemObjectStore:
    """Tenant-scoped, version-preserving object storage for the compact profile."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).expanduser().resolve()
        self._objects = self._root / "objects"
        self._metadata = self._root / "metadata"
        self._versions = self._root / "versions"
        self._temporary = self._root / "tmp"
        for directory in (self._objects, self._metadata, self._versions, self._temporary):
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def backend(self) -> StorageBackend:
        return StorageBackend.LOCAL

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
        key_id = self._key_id(object_key)
        descriptor, temporary_name = tempfile.mkstemp(dir=self._temporary)
        handle = os.fdopen(descriptor, "wb")
        digest = hashlib.sha256()
        size = 0
        try:
            async for chunk in chunks:
                if not chunk:
                    continue
                value = bytes(chunk)
                digest.update(value)
                size += len(value)
                await asyncio.to_thread(handle.write, value)
            await asyncio.to_thread(handle.flush)
            await asyncio.to_thread(os.fsync, handle.fileno())
        except BaseException:
            await asyncio.to_thread(handle.close)
            await asyncio.to_thread(self._unlink_if_present, Path(temporary_name))
            raise
        await asyncio.to_thread(handle.close)

        version_id = digest.hexdigest()
        version_directory = self._versions / key_id
        version_directory.mkdir(parents=True, exist_ok=True)
        version_path = version_directory / f"{version_id}.bin"
        temporary_path = Path(temporary_name)
        if version_path.exists():
            await asyncio.to_thread(self._unlink_if_present, temporary_path)
        else:
            await asyncio.to_thread(os.replace, temporary_path, version_path)
        await asyncio.to_thread(
            self._replace_from,
            version_path,
            self._objects / f"{key_id}.bin",
        )

        created_at = datetime.now(UTC)
        metadata = ObjectMetadata(
            uri=self._uri(object_key),
            tenant_id=tenant_id,
            size=size,
            checksum_sha256=version_id,
            content_type=content_type,
            key=relative_tenant_key(tenant_id, object_key),
            backend=self.backend,
            version_id=version_id,
            created_at=created_at,
            creator=creator,
            lineage=lineage,
        )
        await asyncio.to_thread(
            self._write_metadata,
            version_directory / f"{version_id}.json",
            metadata,
        )
        await asyncio.to_thread(
            self._write_metadata,
            self._metadata / f"{key_id}.json",
            metadata,
        )
        return metadata

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            object_key = self._parse_uri(tenant_id, uri)
            path = self._objects / f"{self._key_id(object_key)}.bin"
            async for chunk in self._read(path):
                yield chunk

        return chunks()

    def get_range(
        self,
        tenant_id: str,
        uri: str,
        start: int,
        end_exclusive: int,
    ) -> AsyncIterator[bytes]:
        selected_range = validate_byte_range(start, end_exclusive)

        async def chunks() -> AsyncIterator[bytes]:
            metadata = await self.head(tenant_id, uri)
            if selected_range[1] > metadata.size:
                raise ValueError("byte range is outside the object")
            object_key = self._parse_uri(tenant_id, uri)
            path = self._objects / f"{self._key_id(object_key)}.bin"
            async for chunk in self._read(
                path,
                start=selected_range[0],
                length=selected_range[1] - selected_range[0],
            ):
                yield chunk

        return chunks()

    def get_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            object_key = self._parse_uri(tenant_id, uri)
            await self.head_version(tenant_id, uri, version_id)
            path = self._versions / self._key_id(object_key) / f"{version_id}.bin"
            async for chunk in self._read(path):
                yield chunk

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        object_key = self._parse_uri(tenant_id, uri)
        key_id = self._key_id(object_key)
        await asyncio.to_thread(self._unlink_if_present, self._objects / f"{key_id}.bin")
        await asyncio.to_thread(self._unlink_if_present, self._metadata / f"{key_id}.json")
        await asyncio.to_thread(shutil.rmtree, self._versions / key_id, True)

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        object_key = self._parse_uri(tenant_id, uri)
        metadata = await asyncio.to_thread(
            self._read_metadata,
            self._metadata / f"{self._key_id(object_key)}.json",
        )
        self._require_selected(metadata, tenant_id, object_key)
        return metadata

    async def head_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> ObjectMetadata:
        object_key = self._parse_uri(tenant_id, uri)
        if len(version_id) != 64 or any(
            character not in "0123456789abcdef" for character in version_id
        ):
            raise ValueError("local object version ID must be a SHA-256 digest")
        metadata = await asyncio.to_thread(
            self._read_metadata,
            self._versions / self._key_id(object_key) / f"{version_id}.json",
        )
        self._require_selected(metadata, tenant_id, object_key)
        if metadata.version_id != version_id:
            raise ValueError("local object version metadata does not match the requested version")
        return metadata

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        tenant_object_key(tenant_id, "probe")

        async def objects() -> AsyncIterator[ObjectMetadata]:
            paths = await asyncio.to_thread(lambda: tuple(sorted(self._metadata.glob("*.json"))))
            selected: list[ObjectMetadata] = []
            for path in paths:
                metadata = await asyncio.to_thread(self._read_metadata, path)
                if metadata.tenant_id == tenant_id:
                    selected.append(metadata)
            for metadata in sorted(selected, key=lambda item: item.key or ""):
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
        object_key = self._parse_uri(tenant_id, uri)
        current = await self.head(tenant_id, uri)
        updated = current.model_copy(
            update={"retention_until": retention_until, "legal_hold": legal_hold}
        )
        key_id = self._key_id(object_key)
        await asyncio.to_thread(
            self._write_metadata,
            self._metadata / f"{key_id}.json",
            updated,
        )
        if updated.version_id is not None:
            await asyncio.to_thread(
                self._write_metadata,
                self._versions / key_id / f"{updated.version_id}.json",
                updated,
            )
        return updated

    async def _read(
        self,
        path: Path,
        *,
        start: int = 0,
        length: int | None = None,
    ) -> AsyncIterator[bytes]:
        handle = await asyncio.to_thread(path.open, "rb")
        remaining = length
        try:
            if start:
                await asyncio.to_thread(handle.seek, start)
            while remaining is None or remaining > 0:
                amount = _CHUNK_BYTES if remaining is None else min(_CHUNK_BYTES, remaining)
                chunk = await asyncio.to_thread(handle.read, amount)
                if not chunk:
                    break
                if remaining is not None:
                    remaining -= len(chunk)
                yield chunk
        finally:
            await asyncio.to_thread(handle.close)

    def _parse_uri(self, tenant_id: str, uri: str) -> str:
        parsed = urlsplit(uri)
        object_key = unquote(parsed.path.lstrip("/"))
        prefix = f"tenants/{tenant_id}/"
        if (
            parsed.scheme != "local"
            or parsed.netloc != _URI_CONTAINER
            or not object_key.startswith(prefix)
        ):
            raise ValueError("object URI is outside the tenant storage prefix")
        relative = relative_tenant_key(tenant_id, object_key)
        if tenant_object_key(tenant_id, relative) != object_key:
            raise ValueError("object URI is outside the tenant storage prefix")
        return object_key

    def _require_selected(
        self,
        metadata: ObjectMetadata,
        tenant_id: str,
        object_key: str,
    ) -> None:
        if metadata.tenant_id != tenant_id or metadata.uri != self._uri(object_key):
            raise ValueError("object metadata is outside the tenant storage prefix")

    @staticmethod
    def _key_id(object_key: str) -> str:
        return hashlib.sha256(object_key.encode()).hexdigest()

    @staticmethod
    def _uri(object_key: str) -> str:
        return f"local://{_URI_CONTAINER}/{quote(object_key, safe='/')}"

    @staticmethod
    def _read_metadata(path: Path) -> ObjectMetadata:
        return ObjectMetadata.model_validate_json(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_metadata(path: Path, metadata: ObjectMetadata) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(metadata.model_dump_json(by_alias=True))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, path)
        except BaseException:
            LocalFilesystemObjectStore._unlink_if_present(Path(temporary_name))
            raise

    @staticmethod
    def _replace_from(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(dir=destination.parent)
        os.close(descriptor)
        try:
            shutil.copyfile(source, temporary_name)
            os.replace(temporary_name, destination)
        except BaseException:
            LocalFilesystemObjectStore._unlink_if_present(Path(temporary_name))
            raise

    @staticmethod
    def _unlink_if_present(path: Path) -> None:
        with suppress(FileNotFoundError):
            path.unlink()
