from __future__ import annotations

import asyncio
import json
import logging
import queue
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from prometheus_client import generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.app import app
from amesh.config import load_configuration
from amesh.domain import (
    ExecutionCommand,
    ExecutionCommandType,
    ExecutionSnapshot,
    TaskRunCommand,
    TaskRunCommandType,
    TaskRunSnapshot,
    decide_execution,
    decide_task_run,
)
from amesh.executor.trace_context import attach_current_trace_context
from amesh.migrations import migration_plan
from amesh.observability import (
    JsonFormatter,
    _BoundedQueueHandler,
    configure_structured_logging,
    configure_telemetry,
    current_trace_context,
    database_readiness,
    diagnostic_metric_samples,
    instrument_database,
    observe_operation,
    recent_redacted_logs,
    shutdown_observability,
)
from amesh.plugin_sdk import PluginOperation, PluginRequest, PluginSession
from amesh.ports import DurableEnvelope, RunnerRequest

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


def test_metrics_endpoint_exposes_amesh_and_http_metrics() -> None:
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "amesh_build_info" in response.text
    assert 'amesh_http_requests_total{method="GET",route="/health",status="200"}' in response.text


def test_json_formatter_emits_structured_context() -> None:
    record = logging.LogRecord("amesh.test", logging.INFO, __file__, 1, "ready", (), None)
    record.execution_id = uuid4()
    record.tenant_id = "tenant-must-not-be-emitted"

    payload = json.loads(JsonFormatter(component="executor").format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "ready"
    assert payload["execution_id"] == str(record.execution_id)
    assert payload["component"] == "executor"
    assert payload["version"]
    assert "tenant_id" not in payload


def test_spans_cover_components_propagate_and_redact() -> None:
    canary = "telemetry-canary-secret"
    load_configuration(environment={"APP_ENV": "development", "AMESH_TOKEN_PEPPER": canary})
    exporter = InMemorySpanExporter()
    configure_telemetry(component="webserver", exporter=exporter)
    try:
        with observe_operation("api", "request", attributes={"credential": canary}) as root:
            root.add_event("accepted", {"token": canary})
            carrier = current_trace_context()
        for component in (
            "scheduler",
            "executor",
            "worker",
            "storage",
            "messaging",
            "plugin",
            "runner",
        ):
            with observe_operation(component, "test", carrier=carrier):
                pass

        spans = exporter.get_finished_spans()
        assert {span.name for span in spans} == {
            "amesh.api.request",
            "amesh.scheduler.test",
            "amesh.executor.test",
            "amesh.worker.test",
            "amesh.storage.test",
            "amesh.messaging.test",
            "amesh.plugin.test",
            "amesh.runner.test",
        }
        root_span = next(span for span in spans if span.name == "amesh.api.request")
        assert all(
            span.parent is not None and span.parent.span_id == root_span.context.span_id
            for span in spans
            if span is not root_span
        )
        rendered = json.dumps(
            [
                {
                    "attributes": dict(span.attributes or {}),
                    "events": [
                        {"name": event.name, "attributes": dict(event.attributes or {})}
                        for event in span.events
                    ],
                }
                for span in spans
            ],
            default=str,
        )
        assert canary not in rendered
        assert "[REDACTED]" in rendered
    finally:
        shutdown_observability()


class _FailingExporter(SpanExporter):
    def export(self, spans: object) -> SpanExportResult:
        del spans
        raise OSError("collector unavailable")

    def shutdown(self) -> None:
        return None


def test_exporter_failure_does_not_fail_core_operation() -> None:
    before = diagnostic_metric_samples()["telemetryExportFailures"]
    configure_telemetry(component="executor", exporter=_FailingExporter())
    try:
        with observe_operation("executor", "reduce"):
            result = "committed"
        assert result == "committed"
        assert diagnostic_metric_samples()["telemetryExportFailures"] == before + 1
    finally:
        shutdown_observability()


def test_file_log_shipping_is_json_redacted_and_tenant_scoped(tmp_path: Path) -> None:
    root = logging.getLogger()
    prior_handlers = list(root.handlers)
    prior_level = root.level
    target = tmp_path / "amesh.jsonl"
    tenant_id = f"tenant-{uuid4().hex}"
    configure_structured_logging(
        "INFO",
        component="worker",
        destination="file",
        file_path=str(target),
        queue_capacity=100,
    )
    try:
        logging.getLogger("amesh.test").error(
            "worker failed safely",
            extra={"tenant_id": tenant_id, "execution_id": uuid4()},
        )
    finally:
        shutdown_observability()
        root.handlers = prior_handlers
        root.setLevel(prior_level)

    records = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    assert records[-1]["component"] == "worker"
    assert records[-1]["message"] == "worker failed safely"
    assert "tenant_id" not in records[-1]
    assert recent_redacted_logs(tenant_id=tenant_id)[-1] == records[-1]
    assert recent_redacted_logs(tenant_id=f"other-{tenant_id}") == ()


def test_full_log_queue_drops_telemetry_without_blocking() -> None:
    records: queue.Queue[logging.LogRecord] = queue.Queue(maxsize=1)
    records.put_nowait(logging.LogRecord("first", logging.INFO, __file__, 1, "one", (), None))
    handler = _BoundedQueueHandler(records, destination="file")
    before = diagnostic_metric_samples()["logRecordsDropped"]

    handler.emit(logging.LogRecord("second", logging.INFO, __file__, 1, "two", (), None))

    assert records.qsize() == 1
    assert diagnostic_metric_samples()["logRecordsDropped"] == before + 1


def test_trace_context_flows_through_durable_contracts_and_reducers() -> None:
    exporter = InMemorySpanExporter()
    configure_telemetry(component="executor", exporter=exporter)
    try:
        with observe_operation("executor", "contracts"):
            carrier = current_trace_context()
            execution_command = attach_current_trace_context(
                ExecutionCommand(
                    command_type=ExecutionCommandType.QUEUE,
                    idempotency_key="observability-execution",
                )
            )
            task_command = attach_current_trace_context(
                TaskRunCommand(
                    command_type=TaskRunCommandType.CREATE,
                    idempotency_key="observability-task",
                )
            )
            envelope = DurableEnvelope(
                message_id=uuid4(),
                message_type="TaskDispatchRequested",
                schema_version=1,
                tenant_id="default",
                partition_key="execution:observability",
                correlation_id=uuid4(),
                produced_at=datetime.now(UTC),
                payload={},
            )
            runner = RunnerRequest(
                tenant_id="default",
                execution_id="execution-1",
                task_run_id="task-1",
                attempt_id="attempt-1",
                fencing_token=1,
                command=["true"],
            )
            plugin = PluginRequest(
                plugin="tests.observability",
                entryPoint="execute",
                operation=PluginOperation.EXECUTE,
                session=PluginSession(tenantId="default", invocationId="invocation-1"),
            )

        execution_result = decide_execution(
            ExecutionSnapshot(
                execution_id=uuid4(),
                tenant_id="default",
                namespace="tests",
                flow_id="observability",
                flow_revision=1,
            ),
            execution_command,
        )
        task_result = decide_task_run(
            TaskRunSnapshot(
                task_run_id=uuid4(),
                execution_id=uuid4(),
                task_id="task-1",
            ),
            task_command,
        )
        assert carrier
        assert execution_command.trace_context == carrier
        assert task_command.trace_context == carrier
        assert envelope.trace_context == carrier
        assert runner.trace_context == carrier
        assert plugin.trace_context == carrier
        assert execution_result.events[0].trace_context == carrier
        assert task_result.events[0].trace_context == carrier
    finally:
        shutdown_observability()


def test_database_readiness_pool_slow_query_and_migration_metrics(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = instrument_database(
            create_async_engine(migrated_test_database_url),
            slow_query_seconds=0.000001,
        )
        try:
            readiness = await database_readiness(engine, MIGRATIONS)
            plan = migration_plan(MIGRATIONS)
            assert readiness.ready
            assert readiness.applied == readiness.expected == len(plan)
            assert readiness.latest_migration == plan[-1].filename
            async with engine.connect() as connection:
                await connection.execute(text("SELECT pg_sleep(0.005)"))
        finally:
            await engine.dispose()

        metrics = generate_latest().decode()
        for name in (
            "amesh_database_health",
            "amesh_database_pool_size",
            "amesh_database_pool_checked_out",
            "amesh_database_query_duration_seconds_count",
            "amesh_database_slow_queries_total",
            "amesh_database_migrations_applied",
            "amesh_database_migrations_expected",
            "amesh_reconciliation_runs_total",
            "amesh_reconciliation_findings_total",
            "amesh_reconciliation_unresolved",
            "amesh_reconciliation_duration_seconds_count",
            "amesh_storage_requests_total",
            "amesh_storage_request_duration_seconds",
            "amesh_storage_transfer_bytes_total",
            "amesh_storage_object_bytes",
            "amesh_storage_objects",
            "amesh_storage_corruption_total",
            "amesh_component_operations_total",
            "amesh_component_operation_duration_seconds_count",
            "amesh_telemetry_export_failures_total",
            "amesh_log_records_dropped_total",
            "amesh_queue_depth",
            "amesh_queue_oldest_eligible_age_seconds",
            "amesh_worker_capacity",
            "amesh_admission_pressure_ratio",
            "amesh_search_projection_lag_seconds",
            "amesh_stuck_work",
        ):
            assert name in metrics

    asyncio.run(scenario())
