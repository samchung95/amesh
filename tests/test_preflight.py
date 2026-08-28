from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from amesh.config import Settings
from amesh.preflight import DependencyCondition, run_preflight


def test_preflight_checks_database_migrations_credentials_and_storage(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    async def ready_database(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        return SimpleNamespace(
            ready=True,
            applied=53,
            expected=53,
            latest_migration="0053_observability_trace_context.sql",
            error=None,
        )

    monkeypatch.setattr("amesh.preflight.database_readiness", ready_database)
    settings = Settings(
        _env_file=None,
        object_storage_backend="local",
        object_storage_local_root=str(tmp_path),
    )

    async def scenario() -> None:
        report = await run_preflight(
            settings,
            engine=object(),  # type: ignore[arg-type]
            write_storage_probe=True,
        )
        assert report.ready and report.status == "ready"
        assert report.dependency_states == {
            "configuration": "READY",
            "credentials": "READY",
            "database": "READY",
            "migrations": "READY",
            "object-storage": "READY",
        }
        assert report.migrations_applied == report.migrations_expected == 53
        assert not list((tmp_path / "metadata").glob("*.json"))

    asyncio.run(scenario())


def test_preflight_exposes_optional_degradation_and_blocks_migration_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def drifted_database(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        return SimpleNamespace(
            ready=False,
            applied=50,
            expected=51,
            latest_migration="0050_operational_controls.sql",
            error=None,
        )

    monkeypatch.setattr("amesh.preflight.database_readiness", drifted_database)
    settings = Settings(_env_file=None)

    async def scenario() -> None:
        report = await run_preflight(
            settings,
            engine=object(),  # type: ignore[arg-type]
            check_storage=False,
        )
        assert not report.ready and report.status == "not-ready"
        assert report.dependency_states["migrations"] == DependencyCondition.DEGRADED
        assert report.dependency_states["object-storage"] == DependencyCondition.DEGRADED
        assert report.degraded_dependencies == ("migrations", "object-storage")
        assert report.error == "required dependencies not ready: migrations"

    asyncio.run(scenario())
