from __future__ import annotations

import asyncio
from uuid import uuid4

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


def test_tenant_transactions_persist_redacted_trace_context_on_events(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
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
