from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from collections.abc import AsyncIterator, Callable
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any
from uuid import UUID

import asyncpg  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh import __version__
from amesh.adapters.postgres import (
    PostgresOperationsRepository,
    PostgresReconciliationRepository,
)
from amesh.config import Settings
from amesh.database import create_database_engine, database_ssl_argument
from amesh.domain import ReconciliationMode, ReconciliationRequest
from amesh.migrations import create_ephemeral_database, drop_ephemeral_database
from amesh.ports import (
    ObjectMetadata,
    OperationsRepository,
    ReconciliationRepository,
    RecoveryExercise,
)
from amesh.reconciliation import ReconciliationService
from amesh.storage.service import ObjectIntegrityError, VerifiedObjectStore

_BACKUP_TENANT = "amesh-system"
_PG_VERSION = re.compile(r"(?P<major>[0-9]+)(?:\.[0-9]+)?")


async def _cleanup_restored_database(
    settings: Settings,
    restored_engine: AsyncEngine | None,
    database_name: str | None,
    gaps: list[str],
) -> None:
    if restored_engine is not None:
        try:
            await restored_engine.dispose()
        except Exception as exc:
            gaps.append(f"restored engine disposal failed: {type(exc).__name__}: {str(exc)[:512]}")
    if database_name is not None:
        try:
            await drop_ephemeral_database(
                settings.database_url,
                database_name,
                ssl_argument=database_ssl_argument(settings),
            )
        except Exception as exc:
            gaps.append(f"restored database cleanup failed: {type(exc).__name__}: {str(exc)[:512]}")


class TenantObjectInventory(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_slug: str
    objects: tuple[ObjectMetadata, ...] = ()


class RecoveryManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    format_version: int = 1
    backup_id: UUID
    snapshot_at: datetime
    database_lsn: str
    schema_version: str
    database_server_version: str
    database_dump: ObjectMetadata
    tenant_inventories: tuple[TenantObjectInventory, ...]
    release_version: str
    configuration_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    configuration_references: dict[str, str]
    created_by: str


class BackupResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    checkpoint_id: UUID
    manifest_uri: str
    manifest_checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    manifest: RecoveryManifest


class NativePostgresTools:
    def __init__(
        self,
        *,
        ssl_mode: str = "prefer",
        ssl_ca_file: str | None = None,
    ) -> None:
        self._ssl_mode = ssl_mode
        self._ssl_ca_file = ssl_ca_file

    async def version(self) -> tuple[int, str]:
        output = await self._run("pg_dump", "--version")
        match = _PG_VERSION.search(output)
        if match is None:
            raise RuntimeError("pg_dump returned an unrecognized version")
        return int(match.group("major")), output.strip()

    async def dump(self, database_url: str, snapshot: str, destination: Path) -> None:
        safe_url, environment = _native_postgres_url(
            database_url,
            ssl_mode=self._ssl_mode,
            ssl_ca_file=self._ssl_ca_file,
        )
        await self._run(
            "pg_dump",
            "--format=custom",
            "--no-owner",
            f"--snapshot={snapshot}",
            f"--file={destination}",
            safe_url,
            environment=environment,
        )

    async def restore(self, database_url: str, archive: Path) -> None:
        safe_url, environment = _native_postgres_url(
            database_url,
            ssl_mode=self._ssl_mode,
            ssl_ca_file=self._ssl_ca_file,
        )
        await self._run(
            "pg_restore",
            "--exit-on-error",
            "--no-owner",
            f"--dbname={safe_url}",
            str(archive),
            environment=environment,
        )

    async def _run(
        self,
        *command: str,
        environment: dict[str, str] | None = None,
    ) -> str:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=environment,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            detail = stderr.decode(errors="replace").strip()[-1_024:]
            raise RuntimeError(f"{command[0]} failed with exit {process.returncode}: {detail}")
        return stdout.decode(errors="replace")


class RecoveryService:
    def __init__(
        self,
        settings: Settings,
        object_store: VerifiedObjectStore,
        *,
        postgres_tools: NativePostgresTools | None = None,
        operations_factory: Callable[[AsyncEngine], OperationsRepository] = (
            PostgresOperationsRepository
        ),
        reconciliation_factory: Callable[[AsyncEngine], ReconciliationRepository] = (
            PostgresReconciliationRepository
        ),
    ) -> None:
        self._settings = settings
        self._object_store = object_store
        self._postgres_tools = postgres_tools or NativePostgresTools(
            ssl_mode=settings.database_tls_mode,
            ssl_ca_file=settings.database_tls_ca_file,
        )
        self._operations_factory = operations_factory
        self._reconciliation_factory = reconciliation_factory

    async def create_backup(self, *, actor_id: str) -> BackupResult:
        from amesh.domain import new_runtime_id

        backup_id = new_runtime_id()
        connection = await asyncpg.connect(
            self._settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1),
            ssl=database_ssl_argument(self._settings),
        )
        transaction = connection.transaction(isolation="repeatable_read", readonly=True)
        transaction_started = False
        with TemporaryDirectory(prefix="amesh-recovery-") as directory:
            dump_path = Path(directory) / "database.dump"
            try:
                await transaction.start()
                transaction_started = True
                snapshot = str(await connection.fetchval("SELECT pg_export_snapshot()"))
                database_lsn = str(await connection.fetchval("SELECT pg_current_wal_lsn()::text"))
                snapshot_at = await connection.fetchval("SELECT clock_timestamp()")
                schema_version = str(
                    await connection.fetchval("SELECT max(version) FROM amesh_schema_migrations")
                )
                server_version = str(await connection.fetchval("SHOW server_version"))
                server_major = int(await connection.fetchval("SHOW server_version_num")) // 10_000
                tenant_slugs = [
                    str(row["slug"])
                    for row in await connection.fetch(
                        "SELECT slug FROM tenants WHERE lifecycle = 'ACTIVE' ORDER BY slug"
                    )
                ]
                client_major, _ = await self._postgres_tools.version()
                if client_major < server_major:
                    raise RuntimeError(
                        f"pg_dump major {client_major} cannot qualify PostgreSQL {server_major}"
                    )
                inventories = await self._inventory_tenants(tenant_slugs)
                await self._postgres_tools.dump(
                    self._settings.database_url,
                    snapshot,
                    dump_path,
                )
                await transaction.rollback()
                transaction_started = False
            except BaseException:
                if transaction_started:
                    await transaction.rollback()
                raise
            finally:
                await connection.close()

            database_dump = await self._object_store.put(
                _BACKUP_TENANT,
                f"recovery/{backup_id}/database.dump",
                _file_chunks(dump_path),
                content_type="application/vnd.postgresql.custom",
            )
            manifest = RecoveryManifest(
                backup_id=backup_id,
                snapshot_at=snapshot_at,
                database_lsn=database_lsn,
                schema_version=schema_version,
                database_server_version=server_version,
                database_dump=database_dump,
                tenant_inventories=inventories,
                release_version=__version__,
                configuration_sha256=_configuration_fingerprint(self._settings),
                configuration_references=_configuration_references(self._settings),
                created_by=actor_id,
            )
            manifest_metadata = await self._object_store.put(
                _BACKUP_TENANT,
                f"recovery/{backup_id}/manifest.json",
                _bytes_chunks(_canonical_json(manifest)),
                content_type="application/json",
            )

        engine = create_database_engine(self._settings)
        try:
            checkpoint = await self._operations_factory(engine).record_backup_checkpoint(
                manifest_metadata.uri,
                manifest_metadata.checksum_sha256,
                created_by=actor_id,
                database_lsn=database_lsn,
            )
        finally:
            await engine.dispose()
        return BackupResult(
            checkpoint_id=checkpoint.checkpoint_id,
            manifest_uri=manifest_metadata.uri,
            manifest_checksum=manifest_metadata.checksum_sha256,
            manifest=manifest,
        )

    async def verify_latest(
        self,
        *,
        actor_id: str,
        profile: str,
        scheduled: bool = False,
    ) -> RecoveryExercise:
        source_engine = create_database_engine(self._settings)
        source_operations = self._operations_factory(source_engine)
        checkpoint = await source_operations.latest_backup_checkpoint()
        if checkpoint is None:
            await source_engine.dispose()
            raise LookupError("no backup checkpoint is available")
        exercise = await source_operations.start_recovery_exercise(
            checkpoint.checkpoint_id,
            profile=profile,
            scheduled=scheduled,
            actor_id=actor_id,
        )
        started = perf_counter()
        rpo_seconds = 0.0
        client_version = "unavailable"
        restored_schema: str | None = None
        object_total = 0
        object_verified = 0
        reconciliation: dict[str, Any] = {}
        projections: dict[str, Any] = {}
        readiness: dict[str, Any] = {}
        gaps: list[str] = []
        database_name: str | None = None
        restored_engine = None
        try:
            manifest, manifest_checksum = await self._load_manifest(checkpoint.object_manifest_uri)
            if manifest_checksum != checkpoint.object_manifest_checksum:
                raise ObjectIntegrityError("recovery manifest checksum differs from its checkpoint")
            rpo_seconds = max(
                (exercise.started_at - manifest.snapshot_at).total_seconds(),
                0.0,
            )
            object_total = sum(len(item.objects) for item in manifest.tenant_inventories) + 1
            client_major, client_version = await self._postgres_tools.version()
            server_major = int(manifest.database_server_version.split(".", maxsplit=1)[0])
            if client_major < server_major:
                raise RuntimeError(
                    f"pg_restore major {client_major} cannot qualify PostgreSQL {server_major}"
                )
            with TemporaryDirectory(prefix="amesh-restore-") as directory:
                dump_path = Path(directory) / "database.dump"
                await _write_stream(
                    dump_path,
                    self._object_store.get_version(_BACKUP_TENANT, manifest.database_dump),
                )
                object_verified += 1
                for inventory in manifest.tenant_inventories:
                    for metadata in inventory.objects:
                        async for _ in self._object_store.get_version(
                            inventory.tenant_slug,
                            metadata,
                        ):
                            pass
                        object_verified += 1
                database = await create_ephemeral_database(
                    self._settings.database_url,
                    ssl_argument=database_ssl_argument(self._settings),
                )
                database_name = database.name
                await self._postgres_tools.restore(database.database_url, dump_path)
                restored_settings = self._settings.model_copy(
                    update={"database_url": database.database_url}
                )
                restored_engine = create_database_engine(restored_settings)
                restored_operations = self._operations_factory(restored_engine)
                recovery_state = await restored_operations.prepare_restored_state()
                rebuilt = await restored_operations.rebuild_disposable_projections()
                projections = {"rebuilt": rebuilt, "count": len(rebuilt)}
                reconciliation = await self._reconcile_restored_tenants(
                    restored_engine,
                    manifest,
                    exercise.exercise_id,
                )
                async with restored_engine.connect() as connection:
                    row = (
                        (
                            await connection.execute(
                                text(
                                    """
                                SELECT
                                    (SELECT max(version) FROM amesh_schema_migrations) AS schema_version,
                                    (SELECT count(*) FROM tenants WHERE lifecycle = 'ACTIVE') AS tenants,
                                    (SELECT count(*) FROM durable_work_queue WHERE state = 'CLAIMED') AS claimed_queue,
                                    (SELECT count(*) FROM workers WHERE status <> 'STOPPED') AS live_workers,
                                    (SELECT count(*) FROM service_instances WHERE state <> 'STOPPED') AS live_services,
                                    (SELECT count(*) FROM scheduler_states WHERE owner_id IS NOT NULL) AS scheduler_owners
                                """
                                )
                            )
                        )
                        .mappings()
                        .one()
                    )
                restored_schema = str(row["schema_version"])
                readiness = {
                    "schemaVersion": restored_schema,
                    "tenants": int(row["tenants"]),
                    "claimedQueue": int(row["claimed_queue"]),
                    "liveWorkers": int(row["live_workers"]),
                    "liveServices": int(row["live_services"]),
                    "schedulerOwners": int(row["scheduler_owners"]),
                    "recoveryState": recovery_state,
                }
                if restored_schema != manifest.schema_version:
                    gaps.append("restored schema version differs from the backup manifest")
                if any(
                    int(row[key])
                    for key in (
                        "claimed_queue",
                        "live_workers",
                        "live_services",
                        "scheduler_owners",
                    )
                ):
                    gaps.append("restored runtime ownership was not fully fenced")
                if int(reconciliation.get("unresolved", 0)):
                    gaps.append("restored-state reconciliation has unresolved findings")
        except Exception as exc:
            gaps.append(f"{type(exc).__name__}: {str(exc)[:512]}")
        finally:
            await _cleanup_restored_database(
                self._settings,
                restored_engine,
                database_name,
                gaps,
            )

        rto_seconds = perf_counter() - started
        passed = not gaps and object_verified == object_total
        if object_verified != object_total:
            gaps.append(f"verified {object_verified} of {object_total} versioned objects")
            passed = False
        completed = await source_operations.complete_recovery_exercise(
            exercise.exercise_id,
            passed=passed,
            rpo_seconds=rpo_seconds,
            rto_seconds=rto_seconds,
            postgres_client_version=client_version,
            restored_schema_version=restored_schema,
            objects_total=object_total,
            objects_verified=object_verified,
            reconciliation=reconciliation,
            projections=projections,
            readiness=readiness,
            unresolved_gaps=gaps,
        )
        await source_engine.dispose()
        return completed

    async def exercise(
        self,
        *,
        actor_id: str,
        profile: str,
        scheduled: bool = False,
    ) -> RecoveryExercise:
        await self.create_backup(actor_id=actor_id)
        return await self.verify_latest(
            actor_id=actor_id,
            profile=profile,
            scheduled=scheduled,
        )

    async def _inventory_tenants(
        self,
        tenant_slugs: list[str],
    ) -> tuple[TenantObjectInventory, ...]:
        inventories: list[TenantObjectInventory] = []
        for tenant_slug in tenant_slugs:
            objects = tuple(
                [
                    metadata
                    async for metadata in self._object_store.iter_objects(tenant_slug)
                    if not (
                        tenant_slug == _BACKUP_TENANT
                        and metadata.key is not None
                        and metadata.key.startswith("recovery/")
                    )
                ]
            )
            inventories.append(
                TenantObjectInventory(
                    tenant_slug=tenant_slug,
                    objects=tuple(sorted(objects, key=lambda item: item.key or item.uri)),
                )
            )
        return tuple(inventories)

    async def _load_manifest(self, uri: str) -> tuple[RecoveryManifest, str]:
        encoded = bytearray()
        async for chunk in self._object_store.get(_BACKUP_TENANT, uri):
            encoded.extend(chunk)
        return RecoveryManifest.model_validate_json(encoded), hashlib.sha256(encoded).hexdigest()

    async def _reconcile_restored_tenants(
        self,
        engine: AsyncEngine,
        manifest: RecoveryManifest,
        exercise_id: UUID,
    ) -> dict[str, Any]:
        service = ReconciliationService(self._reconciliation_factory(engine))
        reports: dict[str, Any] = {}
        repairs = 0
        unresolved = 0
        for inventory in manifest.tenant_inventories:
            run = await service.run(
                ReconciliationRequest(
                    mode=ReconciliationMode.APPLY,
                    staleAfterSeconds=30,
                    maxFindings=1_000,
                    maxRepairs=100,
                    idempotencyKey=f"recovery:{exercise_id}:{inventory.tenant_slug}",
                    reason="isolated disaster-recovery restore exercise",
                ),
                tenant_id=inventory.tenant_slug,
                actor_id="system:recovery-exercise",
            )
            repairs += run.repairs_applied
            unresolved += run.unresolved_count
            reports[inventory.tenant_slug] = {
                "runId": str(run.run_id),
                "findings": run.finding_count,
                "repairs": run.repairs_applied,
                "unresolved": run.unresolved_count,
            }
        return {"tenants": reports, "repairs": repairs, "unresolved": unresolved}


def _native_postgres_url(
    database_url: str,
    *,
    ssl_mode: str,
    ssl_ca_file: str | None,
) -> tuple[str, dict[str, str]]:
    url = make_url(database_url).set(drivername="postgresql")
    environment = os.environ.copy()
    if url.password is not None:
        environment["PGPASSWORD"] = url.password
        url = url.set(password=None)
    environment["PGSSLMODE"] = ssl_mode
    if ssl_ca_file is not None:
        environment["PGSSLROOTCERT"] = ssl_ca_file
    return url.render_as_string(hide_password=False), environment


def _configuration_references(settings: Settings) -> dict[str, str]:
    return {
        "database": "DATABASE_URL secret and PostgreSQL WAL archive",
        "objectStorage": (f"{settings.object_storage_backend}:{settings.object_storage_bucket}"),
        "tenancy": settings.tenancy_mode,
        "release": __version__,
    }


def _configuration_fingerprint(settings: Settings) -> str:
    return hashlib.sha256(
        json.dumps(
            _configuration_references(settings),
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def _canonical_json(model: BaseModel) -> bytes:
    return json.dumps(
        model.model_dump(mode="json"),
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


async def _file_chunks(path: Path) -> AsyncIterator[bytes]:
    with path.open("rb") as source:
        while chunk := source.read(64 * 1024):
            yield chunk


async def _bytes_chunks(value: bytes) -> AsyncIterator[bytes]:
    yield value


async def _write_stream(path: Path, chunks: AsyncIterator[bytes]) -> None:
    with path.open("wb") as destination:
        async for chunk in chunks:
            destination.write(chunk)
