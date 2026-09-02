from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import cast

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

import amesh.adapters.postgres.search_repository as search_module
from amesh.adapters.postgres.search_repository import PostgresSearchRepository
from amesh.ports.search_repository import SearchUnavailableError


def test_record_failure_logs_and_raises_when_state_write_fails(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    class FailingConnection:
        async def execute(self, *_args: object, **_kwargs: object) -> None:
            raise SQLAlchemyError("state write failed")

        async def scalar(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("the first state write should fail")

    @asynccontextmanager
    async def failing_transaction(_engine: AsyncEngine, _tenant_id: str) -> object:
        yield FailingConnection(), "tenant-uuid"

    monkeypatch.setattr(search_module, "tenant_transaction", failing_transaction)
    repository = PostgresSearchRepository(cast(AsyncEngine, object()))

    with (
        caplog.at_level("ERROR"),
        pytest.raises(SearchUnavailableError, match="failure state unavailable"),
    ):
        asyncio.run(repository.record_failure(tenant_id="default", error="broken"))

    assert "failed to persist search projection failure state" in caplog.text
