from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from prometheus_client import generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.app import app
from amesh.observability import JsonFormatter, database_readiness, instrument_database

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
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
    record.execution_id = "execution-1"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "ready"
    assert payload["execution_id"] == "execution-1"


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_database_readiness_pool_slow_query_and_migration_metrics() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = instrument_database(
            create_async_engine(TEST_DATABASE_URL),
            slow_query_seconds=0.000001,
        )
        try:
            readiness = await database_readiness(engine, MIGRATIONS)
            assert readiness.ready
            assert readiness.applied == readiness.expected == 23
            assert readiness.latest_migration == "0023_distributed_queue_profile.sql"
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
        ):
            assert name in metrics

    asyncio.run(scenario())
