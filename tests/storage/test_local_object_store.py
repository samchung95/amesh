from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from amesh.adapters.local import LocalFilesystemObjectStore
from amesh.config import Settings
from amesh.ports import StorageBackend
from amesh.storage.factory import build_object_store


async def _chunks(*values: bytes) -> AsyncIterator[bytes]:
    for value in values:
        yield value


def test_local_filesystem_backend_is_tenant_scoped_versioned_and_durable(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        root = tmp_path / "objects"
        store = LocalFilesystemObjectStore(root)
        first = await store.put(
            "tenant-a",
            "reports/result.json",
            _chunks(b"first", b"-version"),
            content_type="application/json",
            creator="principal-a",
            lineage=("execution:1",),
        )
        second = await store.put(
            "tenant-a",
            "reports/result.json",
            _chunks(b"second-version"),
            content_type="application/json",
            creator="principal-a",
        )

        reloaded = LocalFilesystemObjectStore(root)
        assert reloaded.backend is StorageBackend.LOCAL
        assert (
            b"".join([part async for part in reloaded.get("tenant-a", second.uri)])
            == b"second-version"
        )
        assert (
            b"".join(
                [
                    part
                    async for part in reloaded.get_version(
                        "tenant-a", first.uri, first.version_id or ""
                    )
                ]
            )
            == b"first-version"
        )
        assert (
            b"".join([part async for part in reloaded.get_range("tenant-a", second.uri, 1, 7)])
            == b"econd-"
        )
        retained_until = datetime.now(UTC) + timedelta(days=1)
        governed = await reloaded.set_lifecycle(
            "tenant-a",
            second.uri,
            retention_until=retained_until,
            legal_hold=True,
        )
        assert governed.retention_until == retained_until
        assert governed.legal_hold
        assert [item.key async for item in reloaded.iter_objects("tenant-a")] == [
            "reports/result.json"
        ]
        with pytest.raises(ValueError, match="tenant storage prefix"):
            await reloaded.head("tenant-b", second.uri)

        await reloaded.delete("tenant-a", second.uri)
        with pytest.raises(FileNotFoundError):
            await reloaded.head("tenant-a", second.uri)

    asyncio.run(scenario())


def test_local_backend_is_selected_without_an_external_storage_dependency(
    tmp_path: Path,
) -> None:
    settings = Settings(
        _env_file=None,
        object_storage_backend="local",
        object_storage_local_root=str(tmp_path),
    )
    assert build_object_store(settings).backend is StorageBackend.LOCAL
