from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres.repository_support import (
    PostgresAuditWriter,
    PostgresRepositoryBase,
    PostgresRepositoryServices,
    PostgresTransactionManager,
    StandardJsonCodec,
)
from amesh.ports.repository_support import AuditWrite, Clock, JsonCodec


class _Clock(Clock):
    def now(self) -> datetime:
        return datetime(2026, 9, 2, 3, 0, tzinfo=UTC)


class _Codec(JsonCodec):
    def __init__(self) -> None:
        self.values: list[Any] = []

    def dumps(self, value: Any, *, canonical: bool = False) -> str:
        self.values.append(value)
        return f"encoded:{len(self.values)}"

    def loads(self, value: str | bytes | bytearray) -> Any:
        return value


class _Connection:
    def __init__(self) -> None:
        self.parameters: dict[str, object] | None = None

    async def execute(self, statement: object, parameters: dict[str, object]) -> None:
        assert "INSERT INTO audit_events" in str(statement)
        self.parameters = parameters


@pytest.mark.anyio
async def test_postgres_audit_writer_uses_injected_clock_and_codec() -> None:
    codec = _Codec()
    connection = _Connection()
    writer = PostgresAuditWriter(clock=_Clock(), codec=codec)

    event_id = await writer.write(
        cast(AsyncConnection, connection),
        AuditWrite(
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            actor_id="user:operator",
            action="resource.update",
            resource_type="resource",
            resource_id="example",
            source_component="repository-test",
            evidence={"version": 2},
        ),
    )

    assert isinstance(event_id, UUID)
    assert codec.values == [{"component": "repository-test"}, {"version": 2}]
    assert connection.parameters is not None
    assert connection.parameters["source"] == "encoded:1"
    assert connection.parameters["evidence"] == "encoded:2"
    assert connection.parameters["occurred_at"] == datetime(2026, 9, 2, 3, 0, tzinfo=UTC)


def test_repository_base_keeps_one_injected_service_bundle() -> None:
    engine = cast(AsyncEngine, object())
    codec = StandardJsonCodec()
    services = PostgresRepositoryServices(
        transactions=PostgresTransactionManager(engine),
        audit=PostgresAuditWriter(clock=_Clock(), codec=codec),
        codec=codec,
        clock=_Clock(),
    )

    repository = PostgresRepositoryBase(engine, services=services)

    assert repository._engine is engine
    assert repository._services is services
    assert codec.loads(codec.dumps({"b": 1, "a": 2}, canonical=True)) == {"a": 2, "b": 1}
