from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from amesh import role
from amesh.config import Settings
from amesh.domain import ServiceRole


def test_independent_roles_route_only_their_owned_cycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, tuple[str, ...]]] = []

    async def scheduled(*args: object, tenant_ids: list[str], **kwargs: object) -> int:
        del args, kwargs
        calls.append(("scheduler", tuple(tenant_ids)))
        return 2

    async def backfilled(*args: object, tenant_ids: list[str], **kwargs: object) -> int:
        del args, kwargs
        calls.append(("backfill", tuple(tenant_ids)))
        return 3

    async def recovered(*args: object, tenant_ids: list[str], **kwargs: object) -> int:
        del args, kwargs
        calls.append(("executor", tuple(tenant_ids)))
        return 4

    async def reconciled(*args: object, tenant_ids: list[str], **kwargs: object) -> int:
        del args, kwargs
        calls.append(("maintenance", tuple(tenant_ids)))
        return 5

    class Workers:
        async def recover_expired_claims(self, *, tenant_id: str, **kwargs: object) -> int:
            del kwargs
            calls.append(("worker", (tenant_id,)))
            return 1

    class Transport:
        async def publish_outbox(self, *, tenant_id: str, limit: int) -> int:
            del limit
            calls.append(("indexer", (tenant_id,)))
            return 2

    monkeypatch.setattr(role, "schedule_once", scheduled)
    monkeypatch.setattr(role, "backfill_once", backfilled)
    monkeypatch.setattr(role, "recover_once", recovered)
    monkeypatch.setattr(role, "reconcile_once", reconciled)
    settings = Settings(_env_file=None)
    service = SimpleNamespace(instance=SimpleNamespace(instance_id=uuid4()))
    common = {
        "settings": settings,
        "tenant_ids": ["first", "second"],
        "service": service,
        "executions": object(),
        "scheduler": object(),
        "backfills": object(),
        "reconciliations": object(),
        "workers": Workers(),
        "transport": Transport(),
    }

    async def scenario() -> None:
        assert await role._run_cycle(ServiceRole.SCHEDULER, **common) == 5  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.EXECUTOR, **common) == 4  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.WORKER, **common) == 2  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.INDEXER, **common) == 4  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.MAINTENANCE, **common) == 5  # type: ignore[arg-type]

    asyncio.run(scenario())

    assert calls == [
        ("scheduler", ("first", "second")),
        ("backfill", ("first", "second")),
        ("executor", ("first", "second")),
        ("worker", ("first",)),
        ("worker", ("second",)),
        ("indexer", ("first",)),
        ("indexer", ("second",)),
        ("maintenance", ("first", "second")),
    ]
