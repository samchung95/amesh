from __future__ import annotations

import json
import logging
import logging.config
import logging.handlers
import queue
import re
import sys
from collections import deque
from collections.abc import Callable, Coroutine, Iterator, Mapping, Sequence
from contextlib import contextmanager, suppress
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from time import perf_counter
from typing import Any, ParamSpec, TypeVar
from weakref import WeakSet

from opentelemetry import propagate, trace
from opentelemetry.context import Context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Event, ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.trace import Link, Span, SpanKind, Status, StatusCode
from prometheus_client import Counter, Gauge, Histogram, Info
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh import __version__

HTTP_REQUESTS = Counter(
    "amesh_http_requests",
    "AMESH HTTP requests by method, route and status.",
    ("method", "route", "status"),
)
HTTP_REQUEST_DURATION = Counter(
    "amesh_http_request_duration_seconds",
    "Cumulative AMESH HTTP request duration by method and route.",
    ("method", "route"),
)
BUILD_INFO = Info("amesh_build", "AMESH build information.")
BUILD_INFO.info({"version": __version__})
DATABASE_HEALTH = Gauge("amesh_database_health", "Whether the AMESH database is reachable.")
DATABASE_POOL_SIZE = Gauge(
    "amesh_database_pool_size",
    "Configured size of the AMESH database connection pool.",
)
DATABASE_POOL_CHECKED_OUT = Gauge(
    "amesh_database_pool_checked_out",
    "AMESH database connections currently checked out.",
)
DATABASE_QUERY_DURATION = Histogram(
    "amesh_database_query_duration_seconds",
    "Duration of successful AMESH database statements.",
)
DATABASE_SLOW_QUERIES = Counter(
    "amesh_database_slow_queries",
    "AMESH database statements exceeding the configured slow-query threshold.",
)
DATABASE_MIGRATIONS_APPLIED = Gauge(
    "amesh_database_migrations_applied",
    "Number of recorded AMESH schema migrations.",
)
DATABASE_MIGRATIONS_EXPECTED = Gauge(
    "amesh_database_migrations_expected",
    "Number of migrations in the checked-in AMESH migration manifest.",
)
RECONCILIATION_RUNS = Counter(
    "amesh_reconciliation_runs",
    "Completed AMESH reconciliation runs by mode.",
    ("mode",),
)
RECONCILIATION_FINDINGS = Counter(
    "amesh_reconciliation_findings",
    "AMESH reconciliation findings by bounded invariant and disposition.",
    ("invariant", "disposition"),
)
RECONCILIATION_UNRESOLVED = Gauge(
    "amesh_reconciliation_unresolved",
    "Unresolved findings from the latest AMESH reconciliation run by invariant.",
    ("invariant",),
)
RECONCILIATION_DURATION = Histogram(
    "amesh_reconciliation_duration_seconds",
    "Duration of AMESH reconciliation runs.",
)
STORAGE_REQUESTS = Counter(
    "amesh_storage_requests",
    "AMESH object-storage requests by backend, operation and outcome.",
    ("backend", "operation", "outcome"),
)
STORAGE_REQUEST_DURATION = Histogram(
    "amesh_storage_request_duration_seconds",
    "Duration of AMESH object-storage requests by backend and operation.",
    ("backend", "operation"),
)
STORAGE_TRANSFER_BYTES = Counter(
    "amesh_storage_transfer_bytes",
    "Bytes transferred through AMESH object storage by backend and direction.",
    ("backend", "direction"),
)
STORAGE_OBJECT_BYTES = Gauge(
    "amesh_storage_object_bytes",
    "Bytes observed in the latest AMESH object-storage inventory by backend.",
    ("backend",),
)
STORAGE_OBJECTS = Gauge(
    "amesh_storage_objects",
    "Objects observed in the latest AMESH object-storage inventory by backend.",
    ("backend",),
)
STORAGE_CORRUPTION = Counter(
    "amesh_storage_corruption",
    "AMESH object checksum mismatches by backend.",
    ("backend",),
)
AUTHENTICATION_ATTEMPTS = Counter(
    "amesh_authentication_attempts",
    "AMESH interactive authentication attempts by provider and bounded outcome.",
    ("provider", "outcome"),
)
AUTHENTICATION_LOCKOUTS = Counter(
    "amesh_authentication_lockouts",
    "AMESH local account lockouts.",
)
PLUGIN_CALLBACKS = Counter(
    "amesh_plugin_callbacks",
    "Trusted in-process plugin callbacks by package, entry point, operation and outcome.",
    ("plugin", "version", "entry_point", "operation", "outcome"),
)
PLUGIN_CALLBACK_DURATION = Histogram(
    "amesh_plugin_callback_duration_seconds",
    "Trusted in-process plugin callback duration.",
    ("plugin", "version", "entry_point", "operation"),
)
PLUGIN_CALLBACK_ERRORS = Counter(
    "amesh_plugin_callback_errors",
    "Trusted in-process plugin callback errors by stable code.",
    ("plugin", "version", "code"),
)
PLUGIN_MEMORY_BYTES = Gauge(
    "amesh_plugin_memory_bytes",
    "Trusted plugin-reported owned memory and observed host process memory.",
    ("plugin", "version", "measurement"),
)
PLUGIN_CIRCUIT_OPEN = Gauge(
    "amesh_plugin_circuit_open",
    "Whether a trusted in-process plugin circuit is open.",
    ("plugin", "version"),
)
PLUGIN_QUARANTINES = Counter(
    "amesh_plugin_quarantines",
    "Trusted in-process plugin quarantines by invariant reason.",
    ("plugin", "version", "reason"),
)
COMPONENT_OPERATIONS = Counter(
    "amesh_component_operations",
    "AMESH component operations by bounded component, operation and outcome.",
    ("component", "operation", "outcome"),
)
COMPONENT_OPERATION_DURATION = Histogram(
    "amesh_component_operation_duration_seconds",
    "AMESH component operation duration by bounded component and operation.",
    ("component", "operation"),
)
TELEMETRY_EXPORT_FAILURES = Counter(
    "amesh_telemetry_export_failures",
    "AMESH optional telemetry export failures by bounded exporter type.",
    ("exporter",),
)
LOG_RECORDS_DROPPED = Counter(
    "amesh_log_records_dropped",
    "AMESH application log records dropped when the bounded shipping queue is full.",
    ("destination",),
)
QUEUE_DEPTH = Gauge("amesh_queue_depth", "Current durable work queue depth.")
QUEUE_OLDEST_AGE = Gauge(
    "amesh_queue_oldest_eligible_age_seconds",
    "Age of the oldest currently eligible durable work item.",
)
WORKER_CAPACITY = Gauge(
    "amesh_worker_capacity",
    "Current worker-role capacity advertised by this process.",
)
ADMISSION_PRESSURE = Gauge(
    "amesh_admission_pressure_ratio",
    "Current bounded admission-pressure ratio from zero to one.",
)
SEARCH_PROJECTION_LAG = Gauge(
    "amesh_search_projection_lag_seconds",
    "Current search projection lag in seconds.",
)
STUCK_WORK = Gauge(
    "amesh_stuck_work",
    "Current stuck-work findings from the latest reconciliation cycle.",
)

_P = ParamSpec("_P")
_R = TypeVar("_R")
_DIMENSION = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
_TRACE_KEYS = frozenset({"traceparent"})
_TRACER_PROVIDER: TracerProvider | None = None
_LOG_LISTENER: logging.handlers.QueueListener | None = None
_RECENT_LOGS: deque[tuple[str | None, dict[str, Any]]] = deque(maxlen=200)


def _dimension(value: str) -> str:
    normalized = value.strip().casefold().replace("_", "-")
    return normalized if _DIMENSION.fullmatch(normalized) else "other"


def current_trace_context() -> dict[str, str]:
    """Return the current W3C trace carrier without baggage or application data."""

    carrier: dict[str, str] = {}
    propagate.inject(carrier)
    return {
        key: value[:512]
        for key, value in carrier.items()
        if key.casefold() in _TRACE_KEYS and isinstance(value, str)
    }


def propagated_trace_context(existing: Mapping[str, str] | None = None) -> dict[str, str]:
    """Prefer the active span carrier, otherwise retain a validated incoming carrier."""

    active = current_trace_context()
    if active:
        return active
    return {
        key.casefold(): value[:512]
        for key, value in (existing or {}).items()
        if key.casefold() in _TRACE_KEYS and isinstance(value, str)
    }


def normalize_trace_context(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return current_trace_context()
    return propagated_trace_context(
        {str(key): str(item) for key, item in value.items() if isinstance(item, str)}
    )


def _parent_context(carrier: Mapping[str, str] | None) -> Context | None:
    if not carrier:
        return None
    safe = propagated_trace_context(carrier)
    return propagate.extract(safe) if safe else None


def _tracer() -> trace.Tracer:
    provider = _TRACER_PROVIDER
    return (
        provider.get_tracer("io.amesh", __version__)
        if provider is not None
        else trace.get_tracer("io.amesh", __version__)
    )


@contextmanager
def observe_operation(
    component: str,
    operation: str,
    *,
    carrier: Mapping[str, str] | None = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Mapping[str, str | bool | int | float] | None = None,
) -> Iterator[Span]:
    """Record one bounded Prometheus operation and one OpenTelemetry span."""

    safe_component = _dimension(component)
    safe_operation = _dimension(operation)
    started = perf_counter()
    outcome = "success"
    parent = _parent_context(carrier)
    with _tracer().start_as_current_span(
        f"amesh.{safe_component}.{safe_operation}",
        context=parent,
        kind=kind,
        attributes={
            "amesh.component": safe_component,
            "amesh.operation": safe_operation,
            **_safe_attributes(attributes or {}),
        },
    ) as span:
        try:
            yield span
        except BaseException:
            outcome = "error"
            span.set_status(Status(StatusCode.ERROR, "operation failed"))
            raise
        finally:
            COMPONENT_OPERATIONS.labels(safe_component, safe_operation, outcome).inc()
            COMPONENT_OPERATION_DURATION.labels(safe_component, safe_operation).observe(
                perf_counter() - started
            )


def instrument_async_operation(
    component: str,
    operation: str,
) -> Callable[
    [Callable[_P, Coroutine[Any, Any, _R]]],
    Callable[_P, Coroutine[Any, Any, _R]],
]:
    """Decorate an async operation with bounded vendor-neutral telemetry."""

    def decorate(
        function: Callable[_P, Coroutine[Any, Any, _R]],
    ) -> Callable[_P, Coroutine[Any, Any, _R]]:
        @wraps(function)
        async def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            with observe_operation(component, operation):
                return await function(*args, **kwargs)

        return wrapped

    return decorate


def _safe_value(
    value: Any,
) -> str | bool | int | float | Sequence[str] | Sequence[bool] | Sequence[int] | Sequence[float]:
    from amesh.config import redact_runtime_text

    if isinstance(value, str):
        return redact_runtime_text(value)[:1_024]
    if isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        if all(isinstance(item, str) for item in value):
            return tuple(redact_runtime_text(str(item))[:1_024] for item in value[:128])
        if all(isinstance(item, bool) for item in value):
            return tuple(bool(item) for item in value[:128])
        if all(isinstance(item, int) and not isinstance(item, bool) for item in value):
            return tuple(int(item) for item in value[:128])
        if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
            return tuple(float(item) for item in value[:128])
    return redact_runtime_text(str(value))[:1_024]


def _safe_attributes(
    attributes: Mapping[str, Any],
) -> dict[
    str,
    str | bool | int | float | Sequence[str] | Sequence[bool] | Sequence[int] | Sequence[float],
]:
    return {str(key)[:128]: _safe_value(value) for key, value in list(attributes.items())[:128]}


def _safe_span(span: ReadableSpan) -> ReadableSpan:
    from amesh.config import redact_runtime_text

    events = tuple(
        Event(
            redact_runtime_text(event.name)[:128],
            _safe_attributes(event.attributes or {}),
            event.timestamp,
        )
        for event in span.events[:128]
    )
    links = tuple(
        Link(link.context, _safe_attributes(link.attributes or {})) for link in span.links[:128]
    )
    resource = Resource(_safe_attributes(span.resource.attributes if span.resource else {}))
    return ReadableSpan(
        name=redact_runtime_text(span.name)[:128],
        context=span.context,
        parent=span.parent,
        resource=resource,
        attributes=_safe_attributes(span.attributes or {}),
        events=events,
        links=links,
        kind=span.kind,
        instrumentation_scope=span.instrumentation_scope,
        status=span.status,
        start_time=span.start_time,
        end_time=span.end_time,
    )


class RedactingSpanExporter(SpanExporter):
    """Redact bounded trace fields and isolate optional exporter failures."""

    def __init__(self, exporter: SpanExporter) -> None:
        self._exporter = exporter

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            return self._exporter.export(tuple(_safe_span(span) for span in spans))
        except Exception:
            TELEMETRY_EXPORT_FAILURES.labels("otlp").inc()
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        with suppress(Exception):
            self._exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        try:
            return self._exporter.force_flush(timeout_millis)
        except Exception:
            TELEMETRY_EXPORT_FAILURES.labels("otlp").inc()
            return False


def configure_telemetry(
    *,
    component: str,
    endpoint: str | None = None,
    headers: Mapping[str, str] | None = None,
    queue_size: int = 2_048,
    batch_size: int = 512,
    export_timeout_seconds: float = 5,
    exporter: SpanExporter | None = None,
) -> TracerProvider:
    """Configure one process-local tracer provider with optional non-blocking OTLP export."""

    global _TRACER_PROVIDER
    if _TRACER_PROVIDER is not None:
        _TRACER_PROVIDER.shutdown()
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "amesh",
                "service.version": __version__,
                "service.namespace": "io.amesh",
                "service.instance.role": _dimension(component),
            }
        )
    )
    selected_exporter = exporter
    normalized_endpoint = (endpoint or "").strip()
    if selected_exporter is None and normalized_endpoint:
        trace_endpoint = (
            normalized_endpoint
            if normalized_endpoint.rstrip("/").endswith("/v1/traces")
            else normalized_endpoint.rstrip("/") + "/v1/traces"
        )
        selected_exporter = OTLPSpanExporter(endpoint=trace_endpoint, headers=dict(headers or {}))
    if selected_exporter is not None:
        safe_exporter = RedactingSpanExporter(selected_exporter)
        if exporter is not None:
            provider.add_span_processor(SimpleSpanProcessor(safe_exporter))
        else:
            provider.add_span_processor(
                BatchSpanProcessor(
                    safe_exporter,
                    max_queue_size=queue_size,
                    max_export_batch_size=min(batch_size, queue_size),
                    export_timeout_millis=max(1, int(export_timeout_seconds * 1_000)),
                )
            )
    _TRACER_PROVIDER = provider
    return provider


_INSTRUMENTED_ENGINES: WeakSet[AsyncEngine] = WeakSet()


class DatabaseReadiness:
    def __init__(
        self,
        *,
        ready: bool,
        applied: int,
        expected: int,
        latest_migration: str | None,
        error: str | None = None,
    ) -> None:
        self.ready = ready
        self.applied = applied
        self.expected = expected
        self.latest_migration = latest_migration
        self.error = error


def instrument_database(engine: AsyncEngine, *, slow_query_seconds: float) -> AsyncEngine:
    """Attach bounded, label-free database metrics to one async engine."""

    if engine in _INSTRUMENTED_ENGINES:
        return engine
    _INSTRUMENTED_ENGINES.add(engine)
    sync_engine = engine.sync_engine

    def update_pool_metrics(*_args: object) -> None:
        pool = sync_engine.pool
        size = getattr(pool, "size", None)
        checkedout = getattr(pool, "checkedout", None)
        if callable(size):
            DATABASE_POOL_SIZE.set(float(size()))
        if callable(checkedout):
            DATABASE_POOL_CHECKED_OUT.set(float(checkedout()))

    def before_cursor_execute(
        connection: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        del cursor, statement, parameters, context, executemany
        connection.info["amesh_query_started"] = perf_counter()

    def after_cursor_execute(
        connection: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        del cursor, statement, parameters, context, executemany
        started = connection.info.pop("amesh_query_started", None)
        if started is None:
            return
        elapsed = perf_counter() - float(started)
        DATABASE_QUERY_DURATION.observe(elapsed)
        if elapsed >= slow_query_seconds:
            DATABASE_SLOW_QUERIES.inc()

    event.listen(sync_engine.pool, "connect", update_pool_metrics)
    event.listen(sync_engine.pool, "checkout", update_pool_metrics)
    event.listen(sync_engine.pool, "checkin", update_pool_metrics)
    event.listen(sync_engine, "before_cursor_execute", before_cursor_execute)
    event.listen(sync_engine, "after_cursor_execute", after_cursor_execute)
    update_pool_metrics()
    return engine


async def database_readiness(
    engine: AsyncEngine,
    migrations_directory: Path,
) -> DatabaseReadiness:
    """Check connectivity and exact manifest/application migration parity."""

    from amesh.migration_planning import migration_plan

    expected = len(migration_plan(migrations_directory))
    DATABASE_MIGRATIONS_EXPECTED.set(expected)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            row = (
                (
                    await connection.execute(
                        text(
                            "SELECT count(*) AS applied, max(version) AS latest "
                            "FROM amesh_schema_migrations"
                        )
                    )
                )
                .mappings()
                .one()
            )
        applied = int(row["applied"])
        latest = str(row["latest"]) if row["latest"] is not None else None
        ready = applied == expected
        DATABASE_HEALTH.set(1 if ready else 0)
        DATABASE_MIGRATIONS_APPLIED.set(applied)
        return DatabaseReadiness(
            ready=ready,
            applied=applied,
            expected=expected,
            latest_migration=latest,
        )
    except SQLAlchemyError as exc:
        DATABASE_HEALTH.set(0)
        DATABASE_MIGRATIONS_APPLIED.set(0)
        return DatabaseReadiness(
            ready=False,
            applied=0,
            expected=expected,
            latest_migration=None,
            error=exc.__class__.__name__,
        )


class JsonFormatter(logging.Formatter):
    """Render one stable JSON object per process log record."""

    def __init__(self, *, component: str = "webserver") -> None:
        super().__init__()
        self._component = _dimension(component)

    def format(self, record: logging.LogRecord) -> str:
        from amesh.config import redact_runtime_text

        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_runtime_text(record.getMessage()),
            "component": self._component,
            "version": __version__,
        }
        for name in (
            "correlation_id",
            "execution_id",
            "http_method",
            "http_route",
            "http_status",
            "span_id",
            "trace_id",
            "worker_id",
        ):
            value = getattr(record, name, None)
            if value is not None:
                payload[name] = _safe_value(value)
        if record.exc_info:
            payload["exception"] = redact_runtime_text(self.formatException(record.exc_info))
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


class _TraceContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            record.trace_id = f"{span_context.trace_id:032x}"
            record.span_id = f"{span_context.span_id:016x}"
        return True


class _BoundedQueueHandler(logging.handlers.QueueHandler):
    def __init__(
        self,
        records: queue.Queue[logging.LogRecord],
        *,
        destination: str,
    ) -> None:
        super().__init__(records)
        self._destination = destination

    def enqueue(self, record: logging.LogRecord) -> None:
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            LOG_RECORDS_DROPPED.labels(self._destination).inc()


class _BoundedQueueListener(logging.handlers.QueueListener):
    def __init__(
        self,
        records: queue.Queue[logging.LogRecord],
        *handlers: logging.Handler,
        destination: str,
    ) -> None:
        super().__init__(records, *handlers, respect_handler_level=True)
        self._records = records
        self._destination = destination

    def enqueue_sentinel(self) -> None:
        try:
            super().enqueue_sentinel()
        except queue.Full:
            with suppress(queue.Empty):
                self._records.get_nowait()
                LOG_RECORDS_DROPPED.labels(self._destination).inc()
            super().enqueue_sentinel()


class _RecentLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            payload = json.loads(self.format(record))
        except (TypeError, ValueError):
            return
        if isinstance(payload, dict):
            tenant_id = getattr(record, "tenant_id", None)
            _RECENT_LOGS.append((str(tenant_id) if tenant_id is not None else None, payload))


def recent_redacted_logs(
    *,
    limit: int = 50,
    tenant_id: str | None = None,
) -> tuple[dict[str, Any], ...]:
    bounded = max(0, min(limit, 200))
    if not bounded:
        return ()
    logs = (
        [payload for _tenant, payload in _RECENT_LOGS]
        if tenant_id is None
        else [payload for _tenant, payload in _RECENT_LOGS if _tenant == tenant_id]
    )
    return tuple(logs[-bounded:])


def diagnostic_metric_samples() -> dict[str, float]:
    """Return a fixed, label-free support snapshot of selected operational metrics."""

    def total(collector: Any) -> float:
        return sum(
            float(sample.value)
            for metric in collector.collect()
            for sample in metric.samples
            if not sample.name.endswith("_created")
        )

    return {
        "admissionPressureRatio": total(ADMISSION_PRESSURE),
        "databaseHealth": total(DATABASE_HEALTH),
        "databasePoolCheckedOut": total(DATABASE_POOL_CHECKED_OUT),
        "databasePoolSize": total(DATABASE_POOL_SIZE),
        "logRecordsDropped": total(LOG_RECORDS_DROPPED),
        "queueDepth": total(QUEUE_DEPTH),
        "queueOldestAgeSeconds": total(QUEUE_OLDEST_AGE),
        "searchProjectionLagSeconds": total(SEARCH_PROJECTION_LAG),
        "stuckWork": total(STUCK_WORK),
        "telemetryExportFailures": total(TELEMETRY_EXPORT_FAILURES),
        "workerCapacity": total(WORKER_CAPACITY),
    }


def _destination_handler(
    destination: str,
    *,
    file_path: str | None,
    syslog_address: str,
) -> logging.Handler:
    if destination == "stdout":
        return logging.StreamHandler(sys.stdout)
    if destination == "file":
        if not file_path:
            raise ValueError("LOG_FILE_PATH is required when LOG_DESTINATION=file")
        selected = Path(file_path)
        selected.parent.mkdir(parents=True, exist_ok=True)
        return logging.handlers.RotatingFileHandler(
            selected,
            maxBytes=100 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
    host, separator, port = syslog_address.rpartition(":")
    if destination != "syslog" or not separator or not host or not port.isdigit():
        raise ValueError("LOG_SYSLOG_ADDRESS must use host:port")
    return logging.handlers.SysLogHandler(address=(host, int(port)))


def configure_structured_logging(
    level: str,
    *,
    component: str = "webserver",
    destination: str = "stdout",
    file_path: str | None = None,
    syslog_address: str = "127.0.0.1:514",
    queue_capacity: int = 10_000,
) -> None:
    """Ship JSON logs through a bounded non-blocking queue."""

    global _LOG_LISTENER
    if _LOG_LISTENER is not None:
        _LOG_LISTENER.stop()
    safe_destination = destination.casefold()
    formatter = JsonFormatter(component=component)
    external = _destination_handler(
        safe_destination,
        file_path=file_path,
        syslog_address=syslog_address,
    )
    recent = _RecentLogHandler()
    external.setFormatter(formatter)
    recent.setFormatter(formatter)
    records: queue.Queue[logging.LogRecord] = queue.Queue(maxsize=queue_capacity)
    queued = _BoundedQueueHandler(records, destination=safe_destination)
    queued.addFilter(_TraceContextFilter())
    root = logging.getLogger()
    root.handlers = [queued]
    root.setLevel(level.upper())
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        selected = logging.getLogger(name)
        selected.handlers = [queued]
        selected.setLevel(level.upper())
        selected.propagate = False
    _LOG_LISTENER = _BoundedQueueListener(
        records,
        external,
        recent,
        destination=safe_destination,
    )
    _LOG_LISTENER.start()


def configure_observability(settings: Any) -> None:
    configure_structured_logging(
        settings.log_level,
        component=settings.service_role,
        destination=settings.log_destination,
        file_path=settings.log_file_path,
        syslog_address=settings.log_syslog_address,
        queue_capacity=settings.log_queue_capacity,
    )
    configure_telemetry(
        component=settings.service_role,
        endpoint=settings.otel_exporter_otlp_endpoint,
        headers={
            key: value.get_secret_value()
            for key, value in settings.otel_exporter_otlp_headers.items()
        },
        queue_size=settings.otel_batch_queue_size,
        batch_size=settings.otel_batch_size,
        export_timeout_seconds=settings.otel_export_timeout_seconds,
    )


def shutdown_observability() -> None:
    global _LOG_LISTENER, _TRACER_PROVIDER
    if _LOG_LISTENER is not None:
        _LOG_LISTENER.stop()
        _LOG_LISTENER = None
    if _TRACER_PROVIDER is not None:
        _TRACER_PROVIDER.shutdown()
        _TRACER_PROVIDER = None
