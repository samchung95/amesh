from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresAgentPrimitiveRepository
from amesh.domain import (
    AgentInvocationKind,
    AgentInvocationStart,
    AgentInvocationState,
    McpConnectionSpec,
    McpToolImpact,
    McpToolPin,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_connection_revisions_and_invocation_journal_are_tenant_scoped() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        repository = PostgresAgentPrimitiveRepository(engine)
        try:
            await apply_migrations(database.database_url, migration_directory())
            first_spec = McpConnectionSpec(
                key="catalog",
                namespace="agents.demo",
                endpoint="https://mcp.example.test/mcp",
                credentialRef="mcp-token",
                toolAllowlist=("lookup",),
                tools=(
                    McpToolPin(
                        name="lookup",
                        inputSchema={"type": "object", "additionalProperties": False},
                        impact=McpToolImpact.READ_ONLY,
                    ),
                ),
            )
            first = await repository.save_mcp_connection(
                "default",
                first_spec,
                actor_id="agent-author",
            )
            second = await repository.save_mcp_connection(
                "default",
                first_spec.model_copy(update={"endpoint": "https://mcp-v2.example.test/mcp"}),
                actor_id="agent-author",
            )
            assert (first.revision, second.revision) == (1, 2)
            assert first.connection_id == second.connection_id
            assert (await repository.list_mcp_connections("default", "agents.demo")) == (second,)
            assert (
                await repository.get_mcp_connection(
                    "default",
                    "agents.demo",
                    "catalog",
                    revision=1,
                )
            ).digest == first.digest
            with pytest.raises(LookupError):
                await repository.get_mcp_connection(
                    "amesh-system",
                    "agents.demo",
                    "catalog",
                )

            start = AgentInvocationStart(
                tenantId="default",
                namespace="agents.demo",
                executionId=uuid4(),
                taskRunId=uuid4(),
                attempt=1,
                kind=AgentInvocationKind.MCP,
                operation="catalog.lookup",
                requestHash="a" * 64,
                requestMetadata={"connectionDigest": second.digest},
            )
            begun = await repository.begin_invocation(start)
            duplicate = await repository.begin_invocation(
                start.model_copy(update={"invocation_id": uuid4()})
            )
            assert begun.created is True
            assert duplicate.created is False
            assert duplicate.record.invocation_id == begun.record.invocation_id
            assert duplicate.record.state is AgentInvocationState.STARTED

            with pytest.raises(ValueError, match="different request"):
                await repository.begin_invocation(
                    start.model_copy(update={"invocation_id": uuid4(), "request_hash": "b" * 64})
                )

            completed = await repository.complete_invocation(
                begun.record.invocation_id,
                tenant_id="default",
                state=AgentInvocationState.SUCCEEDED,
                result={"structuredContent": {"count": 1}},
            )
            assert completed.state is AgentInvocationState.SUCCEEDED
            assert completed.result == {"structuredContent": {"count": 1}}
            assert (
                await repository.complete_invocation(
                    begun.record.invocation_id,
                    tenant_id="default",
                    state=AgentInvocationState.SUCCEEDED,
                    result={"structuredContent": {"count": 1}},
                )
            ).state is AgentInvocationState.SUCCEEDED
            with pytest.raises(LookupError):
                await repository.complete_invocation(
                    begun.record.invocation_id,
                    tenant_id="amesh-system",
                    state=AgentInvocationState.SUCCEEDED,
                    result={},
                )

            async with engine.connect() as connection:
                audit_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM audit_events "
                        "WHERE resource_type IN ('agent_mcp_connection', 'agent_invocation')"
                    )
                )
            assert audit_count == 4
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
