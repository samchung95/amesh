from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresAgentPrimitiveRepository
from amesh.domain import (
    AgentInvocationAccounting,
    AgentInvocationCostState,
    AgentInvocationKind,
    AgentInvocationStart,
    AgentInvocationState,
    McpConnectionSpec,
    McpToolImpact,
    McpToolPin,
)
from amesh.model_continuations import ModelContinuationProtector


def test_connection_revisions_and_invocation_journal_are_tenant_scoped(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresAgentPrimitiveRepository(engine)
        try:
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

            retry = await repository.begin_invocation(start.model_copy(update={"attempt": 2}))
            assert retry.created is False
            assert retry.record.invocation_id == begun.record.invocation_id
            assert retry.record.attempt == 1

            with pytest.raises(ValueError, match="different request"):
                await repository.begin_invocation(
                    start.model_copy(update={"attempt": 2, "request_hash": "b" * 64})
                )

            with pytest.raises(ValueError, match="different request"):
                await repository.begin_invocation(
                    start.model_copy(update={"attempt": 2, "task_run_id": uuid4()})
                )

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

    asyncio.run(scenario())


def test_model_continuation_is_encrypted_tenant_scoped_and_restart_resumable(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresAgentPrimitiveRepository(engine)
        key = Fernet.generate_key().decode("ascii")
        invocation_id = uuid4()
        try:
            start = AgentInvocationStart(
                invocationId=invocation_id,
                tenantId="default",
                namespace="agents.demo",
                executionId=uuid4(),
                taskRunId=uuid4(),
                attempt=1,
                kind=AgentInvocationKind.MODEL,
                operation="CHAT#continuation",
                requestHash="c" * 64,
            )
            assert (await repository.begin_invocation(start)).created
            protector = ModelContinuationProtector(
                primary_key_id="current",
                keys={"current": key},
            )
            protected = protector.protect(
                tenant_id="default",
                invocation_id=invocation_id,
                provider_id="fixture",
                provider_revision="3.0.0",
                token=SecretStr("hidden-reasoning-state"),
            )
            await repository.complete_invocation(
                invocation_id,
                tenant_id="default",
                state=AgentInvocationState.SUCCEEDED,
                result={"content": "safe"},
                protected_continuation=protected,
            )

            async with engine.connect() as connection:
                raw = (
                    await connection.execute(
                        text(
                            "SELECT continuation_ciphertext, result::text "
                            "FROM agent_invocations WHERE invocation_id = :invocation_id"
                        ),
                        {"invocation_id": invocation_id},
                    )
                ).one()
            assert b"hidden-reasoning-state" not in bytes(raw[0])
            assert "hidden-reasoning-state" not in raw[1]

            restarted_repository = PostgresAgentPrimitiveRepository(engine)
            reloaded = await restarted_repository.get_model_continuation(
                invocation_id,
                tenant_id="default",
            )
            assert reloaded is not None
            restarted_protector = ModelContinuationProtector(
                primary_key_id="current",
                keys={"current": key},
            )
            assert (
                restarted_protector.reveal(
                    reloaded,
                    tenant_id="default",
                    invocation_id=invocation_id,
                    provider_id="fixture",
                    provider_revision="3.0.0",
                ).get_secret_value()
                == "hidden-reasoning-state"
            )
            with pytest.raises(LookupError):
                await restarted_repository.get_model_continuation(
                    invocation_id,
                    tenant_id="amesh-system",
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_invocation_accounting_first_write_is_idempotent_and_in_doubt_is_terminal(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresAgentPrimitiveRepository(engine)
        try:
            start = AgentInvocationStart(
                tenantId="default",
                namespace="agents.demo",
                executionId=uuid4(),
                taskRunId=uuid4(),
                attempt=1,
                kind=AgentInvocationKind.MODEL,
                operation="STRUCTURED#accounting",
                requestHash="d" * 64,
            )
            invocation = (await repository.begin_invocation(start)).record
            accounting = AgentInvocationAccounting(
                inputTokens=120,
                outputTokens=80,
                reasoningTokens=50,
                totalTokens=200,
                cacheReadTokens=40,
                cacheWriteTokens=10,
                costState=AgentInvocationCostState.BILLED,
                costAmountUsd=Decimal("0.00125"),
            )

            first = await repository.record_invocation_accounting(
                invocation.invocation_id,
                tenant_id="default",
                accounting=accounting,
            )
            repeated = await repository.record_invocation_accounting(
                invocation.invocation_id,
                tenant_id="default",
                accounting=accounting,
            )
            assert first.accounting == repeated.accounting == accounting

            with pytest.raises(RuntimeError, match="accounting conflicts"):
                await repository.record_invocation_accounting(
                    invocation.invocation_id,
                    tenant_id="default",
                    accounting=accounting.model_copy(update={"total_tokens": 201}),
                )
            with pytest.raises(LookupError):
                await repository.record_invocation_accounting(
                    invocation.invocation_id,
                    tenant_id="amesh-system",
                    accounting=accounting,
                )

            terminal = await repository.complete_invocation(
                invocation.invocation_id,
                tenant_id="default",
                state=AgentInvocationState.IN_DOUBT,
                error="provider outcome is unknown after cancellation",
            )
            assert terminal.state is AgentInvocationState.IN_DOUBT
            assert terminal.completed_at is not None
            assert terminal.accounting == accounting
            assert (
                await repository.record_invocation_accounting(
                    invocation.invocation_id,
                    tenant_id="default",
                    accounting=accounting,
                )
            ).state is AgentInvocationState.IN_DOUBT

            missing = (
                await repository.begin_invocation(
                    start.model_copy(
                        update={
                            "invocation_id": uuid4(),
                            "operation": "STRUCTURED#missing-accounting",
                        }
                    )
                )
            ).record
            await repository.complete_invocation(
                missing.invocation_id,
                tenant_id="default",
                state=AgentInvocationState.FAILED,
                error="provider rejected request",
            )
            with pytest.raises(RuntimeError, match=r"must be recorded while.*STARTED"):
                await repository.record_invocation_accounting(
                    missing.invocation_id,
                    tenant_id="default",
                    accounting=accounting,
                )

            async with engine.connect() as connection:
                row = (
                    (
                        await connection.execute(
                            text(
                                "SELECT state, accounting, completed_at FROM agent_invocations "
                                "WHERE invocation_id = :invocation_id"
                            ),
                            {"invocation_id": invocation.invocation_id},
                        )
                    )
                    .mappings()
                    .one()
                )
            assert row["state"] == "IN_DOUBT"
            assert row["accounting"]["reasoningTokens"] == 50
            assert "reasoningContent" not in row["accounting"]
            assert row["completed_at"] is not None
        finally:
            await engine.dispose()

    asyncio.run(scenario())
