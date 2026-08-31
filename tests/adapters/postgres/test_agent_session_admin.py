from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import agent_session_admin as fleet_adapter
from amesh.adapters.postgres.agent_session_admin import (
    PostgresAgentSessionFleetRepository,
    _decode_cursor,
    _encode_cursor,
    _predicates,
    _row_item,
)
from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.adapters.postgres.tenant_repository import PostgresTenantRepository
from amesh.domain import AgentSessionFleetQuery, TenantDefinition
from amesh.dsl import FlowDefinition
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.ports import AgentSessionFleetCursorError

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")


def test_fleet_cursor_is_bound_to_tenant_and_filters() -> None:
    query = AgentSessionFleetQuery(namespace="research")
    created_at = datetime(2026, 8, 30, tzinfo=UTC)
    execution_id = uuid4()
    cursor = _encode_cursor(
        tenant_id="tenant-a",
        fingerprint=query.fingerprint(),
        created_at=created_at,
        execution_id=execution_id,
    )

    assert _decode_cursor(
        cursor,
        tenant_id="tenant-a",
        fingerprint=query.fingerprint(),
    ) == (created_at, execution_id)
    with pytest.raises(AgentSessionFleetCursorError):
        _decode_cursor(cursor, tenant_id="tenant-b", fingerprint=query.fingerprint())
    with pytest.raises(AgentSessionFleetCursorError):
        _decode_cursor(cursor, tenant_id="tenant-a", fingerprint=AgentSessionFleetQuery().fingerprint())


def test_fleet_filters_are_parameterized_and_applied_to_executions() -> None:
    query = AgentSessionFleetQuery(
        state="RUNNING",
        namespace="research",
        agentRef="research/analyst@1",
        createdFrom=datetime(2026, 8, 1, tzinfo=UTC),
        createdTo=datetime(2026, 9, 1, tzinfo=UTC),
        ownerId="principal-a",
        harness="pi",
    )

    sql, fleet_sql, params = _predicates(query)

    assert "e.namespace_name = :namespace" in sql
    assert "e.trigger_context->>'ameshAgentRef' = :agent_ref" in sql
    assert "e.created_at >= :created_from" in sql
    assert "e.created_at < :created_to" in sql
    assert "e.state = 'SUCCESS'" in sql
    assert "e.trigger_context->>'ameshActorId' = :owner_id" in sql
    assert "f.harness_adapter = :harness" in fleet_sql
    assert params["namespace"] == "research"
    assert params["agent_ref"] == "research/analyst@1"


def test_fleet_item_maps_only_bounded_redacted_metadata() -> None:
    now = datetime.now(UTC)
    service_session_id = uuid4()
    row = {
        "service_session_id": str(service_session_id),
        "attempt_session_id": uuid4(),
        "namespace_name": "research",
        "session_namespace": "research",
        "agent_ref": "research/analyst@1",
        "application_id": None,
        "owner_id": "owner-a",
        "execution_id": uuid4(),
        "task_run_id": uuid4(),
        "attempt": 1,
        "lifecycle_state": "RUNNING",
        "phase": "MODEL",
        "session_version": 2,
        "execution_version": 4,
        "execution_epoch": 3,
        "capability_pin_id": uuid4(),
        "envelope_digest": "sha256:" + "a" * 64,
        "harness_adapter": "pi",
        "harness_version": "0.84.3",
        "harness_protocol": "amesh.agent-session/v1",
        "counters": {"turns": 2, "totalTokens": 10, "costUsd": "0.25"},
        "dependency_keys": [f"provider-{index}" for index in range(30)],
        "model_count": 2,
        "tool_count": 3,
        "failed_count": 1,
        "session_created_at": now,
        "session_updated_at": now,
        "session_completed_at": None,
        "execution_created_at": now,
        "execution_updated_at": now,
        "execution_terminal_at": None,
        "policy_provenance": None,
    }

    item = _row_item(row, "tenant-a")

    assert item.tenant_id == "tenant-a"
    assert item.owner_id == "owner-a"
    assert len(item.dependency_keys) == 20
    assert item.dependency_health == "DEGRADED"
    assert not hasattr(item, "checkpoint")
    assert not hasattr(item, "final_result")


def test_fleet_repository_uses_one_bounded_page_and_aggregate_read(monkeypatch) -> None:
    now = datetime.now(UTC)
    execution_id = uuid4()
    page_row = {
        "service_session_id": str(uuid4()),
        "attempt_session_id": None,
        "namespace_name": "research",
        "session_namespace": None,
        "agent_ref": "research/analyst@1",
        "application_id": None,
        "owner_id": "owner-a",
        "execution_id": execution_id,
        "task_run_id": None,
        "attempt": None,
        "lifecycle_state": "QUEUED",
        "phase": None,
        "session_version": None,
        "execution_version": 1,
        "execution_epoch": 1,
        "capability_pin_id": None,
        "envelope_digest": None,
        "harness_adapter": None,
        "harness_version": None,
        "harness_protocol": None,
        "counters": None,
        "dependency_keys": [],
        "model_count": 0,
        "tool_count": 0,
        "failed_count": 0,
        "session_created_at": None,
        "session_updated_at": None,
        "session_completed_at": None,
        "execution_created_at": now,
        "execution_updated_at": now,
        "execution_terminal_at": None,
        "policy_provenance": None,
    }
    aggregate_row = {
        "matched_executions": 1,
        "active": 1,
        "terminal": 0,
        "by_state": {"QUEUED": 1},
        "total_turns": 0,
        "total_tool_calls": 0,
        "total_tokens": 0,
        "total_cost_usd": 0,
        "model_invocations": 0,
        "tool_invocations": 0,
        "failed_invocations": 0,
        "degraded_dependencies": 0,
    }

    class Result:
        def __init__(self, rows: list[dict[str, object]]) -> None:
            self.rows = rows

        def mappings(self) -> Result:
            return self

        def all(self) -> list[dict[str, object]]:
            return self.rows

        def one(self) -> dict[str, object]:
            return self.rows[0]

    class Connection:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict[str, object]]] = []

        async def execute(self, statement, parameters=None):
            sql = str(statement)
            self.calls.append((sql, parameters or {}))
            if "SELECT f.*" in sql:
                return Result([page_row])
            return Result([aggregate_row])

    connection = Connection()
    tenant_uuid = uuid4()

    @asynccontextmanager
    async def transaction(engine, tenant_id):
        assert tenant_id == "default"
        yield connection, tenant_uuid

    monkeypatch.setattr(fleet_adapter, "tenant_transaction", transaction)

    async def scenario() -> None:
        page = await fleet_adapter.PostgresAgentSessionFleetRepository(None).list_fleet(
            "default", AgentSessionFleetQuery(limit=1)
        )
        assert len(page.items) == 1
        assert page.aggregates.matched_executions == 1

    asyncio.run(scenario())
    page_sql, page_params = connection.calls[0]
    assert "LIMIT :limit" in page_sql
    assert "trigger_context ? 'ameshAgentSessionId'" in page_sql
    assert page_params["tenant_uuid"] == tenant_uuid
    assert len(connection.calls) == 2


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_fleet_keyset_filters_aggregates_and_instance_totals_use_canonical_rows() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        executions = PostgresExecutionRepository(engine)
        fleet = PostgresAgentSessionFleetRepository(engine)
        other_tenant = TenantDefinition(slug="fleet-other", display_name="Fleet other")
        flow = FlowDefinition.model_validate(
            {
                "id": "session-fleet",
                "namespace": "agents.fleet",
                "tasks": [{"id": "agent", "type": "agent.session"}],
            }
        )
        try:
            await apply_migrations(database.database_url, migration_directory())
            await PostgresTenantRepository(engine).create(other_tenant, actor_id="test:fleet")
            expected: set[UUID] = set()
            for index, owner in enumerate(("owner-a", "owner-a", "owner-b"), start=1):
                session_id = uuid4()
                execution = await executions.create_execution(
                    flow,
                    tenant_id="default",
                    inputs={},
                    trigger={
                        "ameshAgentSessionId": str(session_id),
                        "ameshAgentRef": f"agents.fleet/helper@{index}",
                        "ameshActorId": owner,
                    },
                    actor_id=owner,
                )
                expected.add(execution.execution_id)
            other = await executions.create_execution(
                flow,
                tenant_id=other_tenant.slug,
                inputs={},
                trigger={
                    "ameshAgentSessionId": str(uuid4()),
                    "ameshAgentRef": "agents.fleet/helper@1",
                    "ameshActorId": "owner-a",
                },
                actor_id="owner-a",
            )

            first = await fleet.list_fleet("default", AgentSessionFleetQuery(limit=2))
            assert len(first.items) == 2
            assert first.next_cursor is not None
            second = await fleet.list_fleet(
                "default", AgentSessionFleetQuery(limit=2, cursor=first.next_cursor)
            )
            traversed = {item.execution_id for item in (*first.items, *second.items)}
            assert traversed == expected
            assert other.execution_id not in traversed
            assert first.aggregates.matched_executions == 3
            assert first.aggregates.active == 3

            owner_page = await fleet.list_fleet(
                "default", AgentSessionFleetQuery(ownerId="owner-a", state="RUNNING")
            )
            assert len(owner_page.items) == 2
            assert {item.agent_ref for item in owner_page.items} == {
                "agents.fleet/helper@1",
                "agents.fleet/helper@2",
            }

            instance = await fleet.instance_aggregate()
            totals = {item.tenant_slug: item.matched_executions for item in instance.tenants}
            assert totals == {"default": 3, other_tenant.slug: 1}
            assert instance.matched_executions == 4
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
