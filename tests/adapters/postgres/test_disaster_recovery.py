from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text

from amesh.adapters.postgres import PostgresOperationsRepository
from amesh.config import Settings
from amesh.database import create_database_engine
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.ports import ObjectMetadata, StorageBackend
from amesh.recovery import RecoveryService
from amesh.storage.service import VerifiedObjectStore

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None
    or shutil.which("pg_dump") is None
    or shutil.which("pg_restore") is None,
    reason="AMESH_TEST_DATABASE_URL and PostgreSQL client tools are required",
)


class MemoryVersionedBackend:
    backend = StorageBackend.S3

    def __init__(self) -> None:
        self.current: dict[tuple[str, str], str] = {}
        self.versions: dict[tuple[str, str, str], bytes] = {}
        self.metadata: dict[tuple[str, str, str], ObjectMetadata] = {}

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        content = b"".join([part async for part in chunks])
        identity = (tenant_id, key)
        version = f"v{sum(1 for item in self.versions if item[:2] == identity) + 1}"
        metadata = ObjectMetadata(
            uri=f"memory://{tenant_id}/{key}",
            tenant_id=tenant_id,
            key=key,
            size=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
            version_id=version,
        )
        self.current[identity] = version
        self.versions[(tenant_id, key, version)] = content
        self.metadata[(tenant_id, key, version)] = metadata
        return metadata

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        key = self._key(tenant_id, uri)
        return self.get_version(tenant_id, uri, self.current[(tenant_id, key)])

    def get_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            yield self.versions[(tenant_id, self._key(tenant_id, uri), version_id)]

        return chunks()

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        key = self._key(tenant_id, uri)
        return self.metadata[(tenant_id, key, self.current[(tenant_id, key)])]

    async def head_version(
        self,
        tenant_id: str,
        uri: str,
        version_id: str,
    ) -> ObjectMetadata:
        return self.metadata[(tenant_id, self._key(tenant_id, uri), version_id)]

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        async def objects() -> AsyncIterator[ObjectMetadata]:
            for (item_tenant, key), version in sorted(self.current.items()):
                if item_tenant == tenant_id:
                    yield self.metadata[(tenant_id, key, version)]

        return objects()

    async def delete(self, tenant_id: str, uri: str) -> None:
        key = self._key(tenant_id, uri)
        self.current.pop((tenant_id, key), None)

    async def set_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
    ) -> ObjectMetadata:
        metadata = await self.head(tenant_id, uri)
        updated = metadata.model_copy(
            update={"retention_until": retention_until, "legal_hold": legal_hold}
        )
        assert metadata.key is not None and metadata.version_id is not None
        self.metadata[(tenant_id, metadata.key, metadata.version_id)] = updated
        return updated

    @staticmethod
    def _key(tenant_id: str, uri: str) -> str:
        prefix = f"memory://{tenant_id}/"
        if not uri.startswith(prefix):
            raise ValueError("tenant storage prefix mismatch")
        return uri.removeprefix(prefix)


async def bytes_chunks(value: bytes) -> AsyncIterator[bytes]:
    yield value


def test_backup_is_restored_reconciled_and_version_verified() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        settings = Settings(_env_file=None, database_url=database.database_url)
        engine = create_database_engine(settings)
        backend = MemoryVersionedBackend()
        store = VerifiedObjectStore(backend)
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            async with engine.begin() as connection:
                tenant_id = await connection.scalar(
                    text("SELECT id FROM tenants WHERE slug = 'default'")
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO durable_work_queue (
                            tenant_id, message_id, lane, partition_key, message_type,
                            schema_version, envelope, state, claimed_by, fencing_token,
                            lease_expires_at
                        ) VALUES (
                            :tenant_id, :message_id, 'tasks', 'recovery', 'RunTask',
                            1, '{}'::jsonb, 'CLAIMED', 'lost-worker', 1,
                            clock_timestamp() + interval '1 hour'
                        )
                        """
                    ),
                    {"tenant_id": tenant_id, "message_id": uuid4()},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO workers (
                            id, tenant_id, worker_group, instance_name, version,
                            capabilities, labels, status, last_heartbeat_at
                        ) VALUES (
                            :id, :tenant_id, 'default', 'lost-worker', 'test',
                            '{}'::jsonb, '{}'::jsonb, 'READY', clock_timestamp()
                        )
                        """
                    ),
                    {"id": uuid4(), "tenant_id": tenant_id},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO service_instances (
                            id, role, instance_name, version, state
                        ) VALUES (:id, 'worker', 'lost-service', 'test', 'READY')
                        """
                    ),
                    {"id": uuid4()},
                )
                await connection.execute(
                    text("CREATE MATERIALIZED VIEW amesh_search_recovery AS SELECT 1 AS value")
                )
            first = await store.put("default", "artifact.bin", bytes_chunks(b"before"))
            service = RecoveryService(settings, store)
            backup = await service.create_backup(actor_id="test:backup")
            inventory = next(
                item for item in backup.manifest.tenant_inventories if item.tenant_slug == "default"
            )
            assert inventory.objects[0].version_id == first.version_id

            await store.put("default", "artifact.bin", bytes_chunks(b"after"))
            exercise = await service.verify_latest(
                actor_id="test:recovery",
                profile="v1",
            )

            assert exercise.state == "PASSED"
            assert exercise.objects_verified == exercise.objects_total
            assert exercise.readiness["claimedQueue"] == 0
            assert exercise.readiness["liveWorkers"] == 0
            assert exercise.readiness["liveServices"] == 0
            assert exercise.projections["rebuilt"] == ["amesh_search_recovery"]
            assert exercise.reconciliation["repairs"] == 1
            assert not exercise.unresolved_gaps
            repository = PostgresOperationsRepository(engine)
            assert await repository.get_recovery_exercise(exercise.exercise_id) == exercise
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
