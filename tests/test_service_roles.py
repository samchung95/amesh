from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from amesh import role
from amesh.config import Settings
from amesh.domain import ServiceRole
from amesh.ports import SearchUnavailableError


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

    agent_primitives = object()
    agent_resources = object()
    agent_sessions = object()
    agent_memory = object()
    human_tasks = object()
    isolated_runtime = object()

    async def recovered(*args: object, tenant_ids: list[str], **kwargs: object) -> int:
        del args
        assert kwargs["agent_primitives"] is agent_primitives
        assert kwargs["agent_resources"] is agent_resources
        assert kwargs["agent_sessions"] is agent_sessions
        assert kwargs["agent_memory"] is agent_memory
        assert kwargs["human_tasks"] is human_tasks
        assert kwargs["isolated_runtime"] is isolated_runtime
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

    class Webhooks:
        async def run_once(
            self,
            tenant_ids: list[str],
            *,
            worker_id: str,
            limit: int,
        ) -> int:
            del worker_id, limit
            calls.append(("webhook", tuple(tenant_ids)))
            return 3

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
        "operational_controls": object(),
        "webhook_dispatcher": Webhooks(),
        "agent_primitives": agent_primitives,
        "agent_resources": agent_resources,
        "agent_sessions": agent_sessions,
        "agent_memory": agent_memory,
        "human_tasks": human_tasks,
        "isolated_runtime": isolated_runtime,
    }

    async def scenario() -> None:
        assert await role._run_cycle(ServiceRole.SCHEDULER, **common) == 5  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.EXECUTOR, **common) == 4  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.WORKER, **common) == 2  # type: ignore[arg-type]
        assert await role._run_cycle(ServiceRole.INDEXER, **common) == 7  # type: ignore[arg-type]
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
        ("webhook", ("first", "second")),
        ("maintenance", ("first", "second")),
    ]


def test_search_projection_failure_does_not_block_other_indexer_work() -> None:
    calls: list[str] = []

    class Transport:
        async def publish_outbox(self, *, tenant_id: str, limit: int) -> int:
            del limit
            calls.append(f"outbox:{tenant_id}")
            return 2

    class Webhooks:
        async def run_once(
            self,
            tenant_ids: list[str],
            *,
            worker_id: str,
            limit: int,
        ) -> int:
            del worker_id, limit
            calls.append(f"webhooks:{','.join(tenant_ids)}")
            return 3

    class FailedSearch:
        async def project_once(self, *, tenant_id: str, limit: int) -> int:
            assert limit == 5_000
            calls.append(f"search:{tenant_id}")
            raise SearchUnavailableError("projection table unavailable")

        async def record_failure(self, *, tenant_id: str, error: str) -> None:
            assert error == "projection table unavailable"
            calls.append(f"failure:{tenant_id}")

    async def scenario() -> None:
        result = await role._run_cycle(
            ServiceRole.INDEXER,
            Settings(_env_file=None),
            ["default"],
            service=SimpleNamespace(instance=SimpleNamespace(instance_id=uuid4())),
            executions=object(),  # type: ignore[arg-type]
            scheduler=object(),  # type: ignore[arg-type]
            backfills=object(),  # type: ignore[arg-type]
            reconciliations=object(),  # type: ignore[arg-type]
            workers=object(),  # type: ignore[arg-type]
            transport=Transport(),  # type: ignore[arg-type]
            operational_controls=object(),  # type: ignore[arg-type]
            webhook_dispatcher=Webhooks(),  # type: ignore[arg-type]
            search_projector=FailedSearch(),
        )
        assert result == 5

    asyncio.run(scenario())
    assert calls == [
        "outbox:default",
        "webhooks:default",
        "search:default",
        "failure:default",
    ]
