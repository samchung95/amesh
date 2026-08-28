from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresToolInvocationJournal
from amesh.domain import (
    ToolInvocationEvidence,
    ToolInvocationRequest,
    ToolInvocationResult,
    ToolInvocationState,
    ToolProviderKind,
    ToolProviderRef,
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


def test_tool_journal_is_tenant_scoped_and_restart_safe() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        journal = PostgresToolInvocationJournal(engine)
        request = ToolInvocationRequest(
            provider=ToolProviderRef(
                kind=ToolProviderKind.PLUGIN, key="example.neutral", revision=1
            ),
            toolName="example.echo",
            tenantId="default",
            namespace="agents.demo",
            executionId=uuid4(),
            taskRunId=uuid4(),
            attempt=1,
            invocationId=uuid4(),
        )
        metadata = {
            "schemaDigest": "sha256:" + "1" * 64,
            "policyDigest": "sha256:" + "2" * 64,
            "arguments": {"value": "[REDACTED]"},
        }
        started = ToolInvocationResult(
            output={},
            evidence=ToolInvocationEvidence(
                provider=request.provider,
                toolName=request.tool_name,
                schemaDigest=metadata["schemaDigest"],
                invocationId=request.invocation_id,
                requestHash="a" * 64,
                policyDigest=metadata["policyDigest"],
                state=ToolInvocationState.AMBIGUOUS,
                ambiguousExternalOutcome=True,
            ),
        )
        try:
            await apply_migrations(database.database_url, migration_directory())
            assert await journal.begin(request, request_hash="a" * 64, metadata=metadata) is None
            with pytest.raises(ValueError, match="different request"):
                await journal.begin(request, request_hash="b" * 64, metadata=metadata)
            # Ambiguous completion deliberately leaves STARTED for restart recovery.
            await journal.complete(request, started)
            duplicate = await journal.begin(request, request_hash="a" * 64, metadata=metadata)
            assert duplicate is not None
            assert duplicate.evidence.state is ToolInvocationState.STARTED
            with pytest.raises(LookupError):
                await journal.begin(
                    request.model_copy(update={"tenant_id": "amesh-system"}),
                    request_hash="a" * 64,
                    metadata=metadata,
                )
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
