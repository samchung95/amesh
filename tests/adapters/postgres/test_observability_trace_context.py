from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.observability import (
    configure_telemetry,
    current_trace_context,
    observe_operation,
    shutdown_observability,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_tenant_transactions_persist_redacted_trace_context_on_events() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.observability.{uuid4().hex}"
        execution_id = None
        configure_telemetry(component="executor", exporter=InMemorySpanExporter())
        try:
            with observe_operation("api", "create-execution"):
                carrier = current_trace_context()
                execution = await repository.create_execution(
                    FlowDefinition(
                        id="trace_context",
                        namespace=namespace,
                        tasks=[TaskDefinition(id="return", type="core.return")],
                    ),
                    tenant_id="default",
                    inputs={},
                )
                execution_id = execution.execution_id
            async with engine.connect() as connection:
                execution_contexts = list(
                    await connection.scalars(
                        text(
                            "SELECT trace_context FROM execution_events "
                            "WHERE execution_id = :execution_id ORDER BY sequence"
                        ),
                        {"execution_id": execution_id},
                    )
                )
                task_contexts = list(
                    await connection.scalars(
                        text(
                            "SELECT trace_context FROM task_run_events "
                            "WHERE execution_id = :execution_id ORDER BY sequence"
                        ),
                        {"execution_id": execution_id},
                    )
                )
            assert carrier
            assert execution_contexts and all(item == carrier for item in execution_contexts)
            assert task_contexts and all(item == carrier for item in task_contexts)
        finally:
            shutdown_observability()
            if execution_id is not None:
                parameters = {
                    "execution_id": execution_id,
                    "partition_key": f"execution:{execution_id}",
                }
                async with engine.begin() as connection:
                    await connection.execute(
                        text("DELETE FROM durable_work_queue WHERE partition_key = :partition_key"),
                        parameters,
                    )
                    await connection.execute(
                        text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
                        parameters,
                    )
                    await connection.execute(
                        text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
                        parameters,
                    )
                    await connection.execute(
                        text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
                        parameters,
                    )
                    await connection.execute(
                        text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
                        parameters,
                    )
                    await connection.execute(
                        text("DELETE FROM executions WHERE id = :execution_id"),
                        parameters,
                    )
            await engine.dispose()

    asyncio.run(scenario())
