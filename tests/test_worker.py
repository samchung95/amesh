from __future__ import annotations

import asyncio

import pytest

from amesh import worker
from amesh.config import Settings


class StopWorker(BaseException):
    pass


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


class InterruptedTenantRepository:
    def __init__(self) -> None:
        self.calls = 0

    async def list_active_for_worker_group(self, worker_group: str) -> list[str]:
        del worker_group
        self.calls += 1
        if self.calls == 1:
            raise OSError("simulated PostgreSQL connection interruption")
        raise StopWorker


def test_worker_retries_after_database_connection_interruption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def scenario() -> None:
        engine = FakeEngine()
        tenants = InterruptedTenantRepository()
        monkeypatch.setattr(worker, "create_database_engine", lambda settings: engine)
        monkeypatch.setattr(worker, "PostgresExecutionRepository", lambda value: object())
        monkeypatch.setattr(worker, "PostgresSchedulerRepository", lambda value: object())
        monkeypatch.setattr(worker, "PostgresTenantRepository", lambda value: tenants)

        async def no_wait(delay: float) -> None:
            del delay

        monkeypatch.setattr(worker.asyncio, "sleep", no_wait)
        settings = Settings(database_url="postgresql+asyncpg://amesh:amesh@localhost/amesh")

        with pytest.raises(StopWorker):
            await worker.run_worker(settings)

        assert tenants.calls == 2
        assert engine.disposed

    asyncio.run(scenario())
