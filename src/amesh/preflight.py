from __future__ import annotations

import argparse
import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.config import Settings, get_settings
from amesh.database import create_database_engine
from amesh.migrations import migration_directory
from amesh.observability import configure_structured_logging, database_readiness
from amesh.storage import VerifiedObjectStore
from amesh.storage.factory import build_object_store


class DependencyCondition(StrEnum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class PreflightDependency(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    condition: DependencyCondition
    required: bool = True
    detail: str


class PreflightReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    status: Literal["ready", "degraded", "not-ready"]
    ready: bool
    observed_at: datetime = Field(alias="observedAt")
    dependencies: tuple[PreflightDependency, ...]
    migrations_applied: int = Field(alias="migrationsApplied", ge=0)
    migrations_expected: int = Field(alias="migrationsExpected", ge=0)
    latest_migration: str | None = Field(default=None, alias="latestMigration")

    @property
    def dependency_states(self) -> dict[str, str]:
        return {item.name: item.condition.value for item in self.dependencies}

    @property
    def degraded_dependencies(self) -> tuple[str, ...]:
        return tuple(
            item.name
            for item in self.dependencies
            if item.condition is DependencyCondition.DEGRADED
        )

    @property
    def error(self) -> str | None:
        failed = [
            item.name
            for item in self.dependencies
            if item.required and item.condition is not DependencyCondition.READY
        ]
        return f"required dependencies not ready: {', '.join(failed)}" if failed else None


class PreflightFailed(RuntimeError):
    def __init__(self, report: PreflightReport) -> None:
        super().__init__(report.error or "startup preflight failed")
        self.report = report


async def run_preflight(
    settings: Settings,
    *,
    engine: AsyncEngine | None = None,
    object_store: VerifiedObjectStore | None = None,
    check_storage: bool = True,
    write_storage_probe: bool = False,
) -> PreflightReport:
    checks = [
        PreflightDependency(
            name="configuration",
            condition=DependencyCondition.READY,
            detail="typed configuration accepted",
        ),
        PreflightDependency(
            name="credentials",
            condition=DependencyCondition.READY,
            detail=_credential_summary(settings),
        ),
    ]
    selected_engine = engine or create_database_engine(settings)
    owns_engine = engine is None
    applied = 0
    expected = 0
    latest: str | None = None
    try:
        try:
            database = await asyncio.wait_for(
                database_readiness(selected_engine, migration_directory()),
                timeout=settings.preflight_timeout_seconds,
            )
        except Exception as exc:
            checks.extend(
                (
                    PreflightDependency(
                        name="database",
                        condition=DependencyCondition.UNAVAILABLE,
                        detail=exc.__class__.__name__,
                    ),
                    PreflightDependency(
                        name="migrations",
                        condition=DependencyCondition.UNAVAILABLE,
                        detail="migration state could not be inspected",
                    ),
                )
            )
        else:
            applied = database.applied
            expected = database.expected
            latest = database.latest_migration
            database_available = database.error is None
            checks.extend(
                (
                    PreflightDependency(
                        name="database",
                        condition=(
                            DependencyCondition.READY
                            if database_available
                            else DependencyCondition.UNAVAILABLE
                        ),
                        detail="connection accepted"
                        if database_available
                        else database.error or "unavailable",
                    ),
                    PreflightDependency(
                        name="migrations",
                        condition=(
                            DependencyCondition.READY
                            if database.ready
                            else DependencyCondition.DEGRADED
                            if database_available
                            else DependencyCondition.UNAVAILABLE
                        ),
                        detail=f"{database.applied}/{database.expected} migrations applied",
                    ),
                )
            )
    finally:
        if owns_engine:
            await selected_engine.dispose()

    if check_storage:
        try:
            store = object_store or build_object_store(settings)
            await asyncio.wait_for(
                _probe_storage(
                    store,
                    tenant_id=settings.single_tenant_slug,
                    write=write_storage_probe,
                ),
                timeout=settings.preflight_timeout_seconds,
            )
        except Exception as exc:
            checks.append(
                PreflightDependency(
                    name="object-storage",
                    condition=DependencyCondition.UNAVAILABLE,
                    detail=exc.__class__.__name__,
                )
            )
        else:
            checks.append(
                PreflightDependency(
                    name="object-storage",
                    condition=DependencyCondition.READY,
                    detail=f"{store.backend.value} access accepted",
                )
            )
    else:
        checks.append(
            PreflightDependency(
                name="object-storage",
                condition=DependencyCondition.DEGRADED,
                required=False,
                detail="runtime storage readiness probe is disabled",
            )
        )

    ready = all(item.condition is DependencyCondition.READY for item in checks if item.required)
    degraded = any(item.condition is DependencyCondition.DEGRADED for item in checks)
    status: Literal["ready", "degraded", "not-ready"] = (
        "not-ready" if not ready else "degraded" if degraded else "ready"
    )
    return PreflightReport(
        status=status,
        ready=ready,
        observedAt=datetime.now(UTC),
        dependencies=tuple(checks),
        migrationsApplied=applied,
        migrationsExpected=expected,
        latestMigration=latest,
    )


async def _probe_storage(
    store: VerifiedObjectStore,
    *,
    tenant_id: str,
    write: bool,
) -> None:
    if write:
        metadata = await store.put(
            tenant_id,
            f"_amesh/preflight/{uuid4().hex}",
            _empty_chunks(),
            content_type="application/octet-stream",
            creator="system:preflight",
        )
        try:
            await store.head(tenant_id, metadata.uri)
        finally:
            await store.delete(tenant_id, metadata.uri)
        return

    iterator = store.iter_objects(tenant_id)
    try:
        await anext(iterator, None)
    finally:
        close = getattr(iterator, "aclose", None)
        if close is not None:
            await close()


async def _empty_chunks() -> AsyncIterator[bytes]:
    if False:
        yield b""


def _credential_summary(settings: Settings) -> str:
    if settings.object_storage_backend == "local":
        storage = "local storage requires no external credential"
    elif settings.object_storage_workload_identity:
        storage = "storage workload identity configured"
    else:
        storage = "storage credential configured"
    if settings.auth_mode == "development":
        auth = "development bootstrap credential configured"
    else:
        auth = "durable authentication mode configured"
    return f"{auth}; {storage}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate AMESH startup dependencies")
    parser.add_argument("--read-only-storage", action="store_true")
    args = parser.parse_args()
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    report = asyncio.run(run_preflight(settings, write_storage_probe=not args.read_only_storage))
    print(report.model_dump_json(by_alias=True, indent=2))
    raise SystemExit(0 if report.ready else 1)


if __name__ == "__main__":
    main()
