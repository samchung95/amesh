from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from amesh.adapters.postgres import repository_support
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
        self.statement: object | None = None
        self.parameters: dict[str, object] | None = None

    async def execute(self, statement: object, parameters: dict[str, object]) -> None:
        assert "INSERT INTO audit_events" in str(statement)
        self.statement = statement
        self.parameters = parameters


class _RollbackSentinel(Exception):
    pass


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
    assert isinstance(connection.parameters["correlation_id"], UUID)


@pytest.mark.anyio
async def test_postgres_audit_writer_preserves_supplied_metadata_and_timestamp() -> None:
    codec = _Codec()
    connection = _Connection()
    writer = PostgresAuditWriter(clock=_Clock(), codec=codec)
    event_id = UUID("00000000-0000-0000-0000-000000000002")
    correlation_id = UUID("00000000-0000-0000-0000-000000000003")
    occurred_at = datetime(2026, 9, 2, 4, 30, tzinfo=UTC)
    source = {"component": "repository-test", "transport": "http", "attempt": 2}

    returned_id = await writer.write(
        cast(AsyncConnection, connection),
        AuditWrite(
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            actor_id="user:operator",
            action="resource.update",
            resource_type="resource",
            resource_id="example",
            source=source,
            evidence={"version": 2},
            event_id=event_id,
            correlation_id=correlation_id,
            occurred_at=occurred_at,
        ),
    )

    assert returned_id == event_id
    assert codec.values == [source, {"version": 2}]
    assert connection.parameters is not None
    assert connection.parameters["event_id"] == event_id
    assert connection.parameters["correlation_id"] == correlation_id
    assert connection.parameters["occurred_at"] == occurred_at


@pytest.mark.anyio
async def test_postgres_audit_writer_can_use_the_database_clock() -> None:
    connection = _Connection()
    writer = PostgresAuditWriter(clock=_Clock(), codec=_Codec())

    await writer.write(
        cast(AsyncConnection, connection),
        AuditWrite(
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            actor_id="user:operator",
            action="resource.update",
            resource_type="resource",
            resource_id="example",
            source_component="repository-test",
            use_database_clock=True,
            generate_correlation_id=False,
        ),
    )

    assert connection.statement is not None
    assert "clock_timestamp()" in str(connection.statement)
    assert connection.parameters is not None
    assert "occurred_at" not in connection.parameters
    assert connection.parameters["correlation_id"] is None


@pytest.mark.anyio
async def test_tenant_transaction_rolls_back_audit_write(
    migrated_test_database_url: str,
) -> None:
    engine = create_async_engine(migrated_test_database_url)
    transaction_manager = PostgresTransactionManager(engine)
    writer = PostgresAuditWriter(clock=_Clock(), codec=StandardJsonCodec())
    event_id = uuid4()

    try:
        with pytest.raises(_RollbackSentinel):
            async with transaction_manager.tenant("default") as (connection, tenant_id):
                await writer.write(
                    connection,
                    AuditWrite(
                        tenant_id=tenant_id,
                        actor_id="test:repository-support",
                        action="repository.transaction.rollback",
                        resource_type="repository_support_test",
                        resource_id=str(event_id),
                        source_component="repository-support-test",
                        event_id=event_id,
                    ),
                )
                assert (
                    await connection.scalar(
                        text("SELECT count(*) FROM audit_events WHERE event_id = :event_id"),
                        {"event_id": event_id},
                    )
                    == 1
                )
                raise _RollbackSentinel

        async with engine.connect() as connection:
            assert (
                await connection.scalar(
                    text("SELECT count(*) FROM audit_events WHERE event_id = :event_id"),
                    {"event_id": event_id},
                )
                == 0
            )
    finally:
        await engine.dispose()


def test_standard_json_codec_canonical_output_preserves_unicode() -> None:
    codec = StandardJsonCodec()
    value = {"雪": "café", "emoji": "🧭"}

    encoded = codec.dumps(value, canonical=True)

    assert encoded == '{"emoji":"🧭","雪":"café"}'
    assert codec.loads(encoded) == value


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


def test_repository_base_lazily_builds_one_bundle_for_engine_only_subclasses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = cast(AsyncEngine, object())
    codec = StandardJsonCodec()
    services = PostgresRepositoryServices(
        transactions=PostgresTransactionManager(engine),
        audit=PostgresAuditWriter(clock=_Clock(), codec=codec),
        codec=codec,
        clock=_Clock(),
    )
    built_for: list[AsyncEngine] = []

    def build_services(candidate: AsyncEngine) -> PostgresRepositoryServices:
        built_for.append(candidate)
        return services

    monkeypatch.setattr(repository_support, "build_repository_services", build_services)

    class _EngineOnlyRepository(PostgresRepositoryBase):
        def __init__(self, candidate: AsyncEngine) -> None:
            self._engine = candidate

    repository = _EngineOnlyRepository(engine)

    assert built_for == []
    assert repository._services is services
    assert repository._services is services
    assert built_for == [engine]
