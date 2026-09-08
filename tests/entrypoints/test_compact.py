from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

import pytest

from amesh import compact
from amesh.config import Settings
from amesh.domain import ServiceRole
from amesh.preflight import PreflightDependency, PreflightFailed, PreflightReport


def _report(*, ready: bool) -> PreflightReport:
    return PreflightReport(
        status="ready" if ready else "not-ready",
        ready=ready,
        observedAt=datetime.now(UTC),
        dependencies=(
            PreflightDependency(
                name="database",
                condition="READY" if ready else "UNAVAILABLE",
                detail="test",
            ),
        ),
        migrationsApplied=51 if ready else 0,
        migrationsExpected=51,
        latestMigration="0053_observability_trace_context.sql" if ready else None,
    )


def test_compact_runtime_starts_all_roles_then_drains_and_stops(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    started: set[ServiceRole] = set()
    stopped: set[ServiceRole] = set()
    drained: set[ServiceRole] = set()

    async def preflight(*args: object, **kwargs: object) -> PreflightReport:
        del args, kwargs
        return _report(ready=True)

    async def server(settings: Settings, *, stop_event: asyncio.Event) -> None:
        assert settings.service_role == ServiceRole.WEBSERVER
        started.add(ServiceRole.WEBSERVER)
        await stop_event.wait()
        stopped.add(ServiceRole.WEBSERVER)

    async def role(settings: Settings, *, stop_event: asyncio.Event) -> None:
        selected = ServiceRole(settings.service_role)
        started.add(selected)
        await stop_event.wait()
        stopped.add(selected)

    async def drain(settings: Settings) -> bool:
        drained.add(ServiceRole(settings.service_role))
        return True

    monkeypatch.setattr(compact, "run_preflight", preflight)
    monkeypatch.setattr(compact, "run_server", server)
    monkeypatch.setattr(compact, "run_role", role)
    monkeypatch.setattr(compact, "request_self_drain", drain)
    settings = Settings(
        _env_file=None,
        service_instance_name="compact-test",
        object_storage_backend="local",
        object_storage_local_root=str(tmp_path),
        compact_shutdown_grace_seconds=2,
    )

    async def scenario() -> None:
        shutdown = asyncio.Event()
        task = asyncio.create_task(compact.run_compact(settings, shutdown_event=shutdown))
        for _ in range(100):
            if len(started) == 6:
                break
            await asyncio.sleep(0.01)
        assert started == set(ServiceRole)
        shutdown.set()
        await asyncio.wait_for(task, timeout=3)

    asyncio.run(scenario())
    assert stopped == set(ServiceRole)
    assert drained == set(ServiceRole)


def test_compact_runtime_stops_before_admission_when_preflight_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def preflight(*args: object, **kwargs: object) -> PreflightReport:
        del args, kwargs
        return _report(ready=False)

    monkeypatch.setattr(compact, "run_preflight", preflight)
    with pytest.raises(PreflightFailed, match="database"):
        asyncio.run(compact.run_compact(Settings(_env_file=None), shutdown_event=asyncio.Event()))
