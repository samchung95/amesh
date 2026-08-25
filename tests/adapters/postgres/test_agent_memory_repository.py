from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAgentMemoryRepository,
    PostgresExecutionRepository,
)
from amesh.domain import (
    AgentMemoryContext,
    AgentMemoryScope,
    AgentMemoryWrite,
)
from amesh.dsl import FlowDefinition
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


def test_memory_is_tenant_scoped_bounded_idempotent_shareable_and_deletable() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        memory = PostgresAgentMemoryRepository(engine)
        executions = PostgresExecutionRepository(engine)
        try:
            await apply_migrations(database.database_url, migration_directory())
            flow = FlowDefinition.model_validate(
                {
                    "id": "memory",
                    "namespace": "agents.memory-test",
                    "tasks": [{"id": "remember", "type": "core.log", "message": "x"}],
                }
            )
            first_execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
            )
            second_execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
            )
            private = AgentMemoryContext(
                namespace=flow.namespace,
                agentKey="helper",
                agentRevision=1,
                executionId=first_execution.execution_id,
                scope=AgentMemoryScope.PRIVATE,
                maxBytes=1000,
                retentionSeconds=3600,
            )
            write = AgentMemoryWrite(
                key="answer",
                value={"answer": "bounded"},
                provenance={"operationKey": "session:1:output:1"},
            )
            first = await memory.write("default", private, write)
            duplicate = await memory.write("default", private, write)
            assert duplicate.entry_id == first.entry_id
            assert duplicate.version == 1

            next_execution = private.model_copy(
                update={"execution_id": second_execution.execution_id}
            )
            recalled = await memory.read("default", next_execution, ("answer",))
            assert recalled[0].value == {"answer": "bounded"}
            assert await memory.read("amesh-system", next_execution, ("answer",)) == ()
            assert (
                await memory.read(
                    "default",
                    next_execution.model_copy(update={"agent_key": "other"}),
                    ("answer",),
                )
                == ()
            )
            assert (
                await memory.read(
                    "default",
                    next_execution.model_copy(update={"agent_revision": 2}),
                    ("answer",),
                )
                == ()
            )

            shared_writer = private.model_copy(
                update={
                    "scope": AgentMemoryScope.SHARED,
                    "shared_scope": "research-team",
                }
            )
            await memory.write(
                "default",
                shared_writer,
                AgentMemoryWrite(
                    key="shared-answer",
                    value={"answer": "shared"},
                    provenance={"operationKey": "session:1:shared:1"},
                ),
            )
            shared_reader = shared_writer.model_copy(update={"agent_key": "reviewer"})
            assert (await memory.read("default", shared_reader, ("shared-answer",)))[0].value == {
                "answer": "shared"
            }

            with pytest.raises(ValueError, match="maxBytes"):
                await memory.write(
                    "default",
                    private.model_copy(update={"max_bytes": 5}),
                    AgentMemoryWrite(
                        key="too-large",
                        value={"answer": "too large"},
                        provenance={"operationKey": "session:1:large:1"},
                    ),
                )

            metadata = await memory.list_metadata(
                "default",
                flow.namespace,
                agent_key="helper",
            )
            assert metadata
            assert "value" not in metadata[0].model_dump()
            expiring = await memory.write(
                "default",
                private,
                AgentMemoryWrite(
                    key="expired",
                    value={"answer": "old"},
                    provenance={"operationKey": "session:1:expired:1"},
                ),
            )
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE agent_memory_entries "
                        "SET expires_at = clock_timestamp() - interval '1 second' "
                        "WHERE entry_id = :entry_id"
                    ),
                    {"entry_id": expiring.entry_id},
                )
            assert await memory.read("default", private, ("expired",)) == ()
            deleted = await memory.delete(
                "default",
                flow.namespace,
                first.entry_id,
                actor_id="test",
            )
            assert deleted.content_digest == first.content_digest
            assert await memory.read("default", next_execution, ("answer",)) == ()

            async with engine.begin() as connection:
                audit_count = await connection.scalar(
                    text(
                        "SELECT count(*) FROM audit_events "
                        "WHERE action = 'agent.memory.delete' AND resource_id = :entry_id"
                    ),
                    {"entry_id": str(first.entry_id)},
                )
            assert audit_count == 1
            with pytest.raises(LookupError):
                await memory.delete(
                    "default",
                    "other.namespace",
                    uuid4(),
                    actor_id="test",
                )
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
