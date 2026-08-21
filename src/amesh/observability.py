from __future__ import annotations

import json
import logging
import logging.config
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from weakref import WeakSet

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

    from amesh.migrations import migration_plan

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

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for name in (
            "execution_id",
            "http_method",
            "http_route",
            "http_status",
            "worker_id",
        ):
            value = getattr(record, name, None)
            if value is not None:
                payload[name] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def configure_structured_logging(level: str) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["console"], "level": level.upper()},
            "loggers": {
                "uvicorn": {"handlers": ["console"], "level": level.upper(), "propagate": False},
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": level.upper(),
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": level.upper(),
                    "propagate": False,
                },
            },
        }
    )
