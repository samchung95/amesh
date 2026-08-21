from __future__ import annotations

import json
from statistics import mean
from time import perf_counter
from typing import Any

import asyncpg  # type: ignore[import-untyped]

from amesh.config import Settings
from amesh.database import database_ssl_argument

SUPPORTED_POSTGRES_MAJOR_VERSIONS = frozenset({15, 16, 17, 18})
REQUIRED_CRITICAL_INDEXES = frozenset(
    {
        "durable_work_queue_claim_idx",
        "durable_work_queue_expired_claim_idx",
        "durable_work_queue_shard_claim_idx",
        "executions_tenant_state_updated_idx",
        "messages_outbox_pending_idx",
        "scheduler_states_due_idx",
    }
)

_CRITICAL_PLANS = {
    "queue_claim": """
        SELECT id
        FROM durable_work_queue
        WHERE lane = 'task-dispatch'
          AND state = 'READY'
          AND available_at <= clock_timestamp()
        ORDER BY priority DESC, available_at, id
        LIMIT 100
    """,
    "outbox_publish": """
        SELECT sequence
        FROM messages_outbox
        WHERE published_at IS NULL
          AND available_at <= clock_timestamp()
        ORDER BY available_at, sequence
        LIMIT 100
    """,
    "scheduler_due": """
        SELECT tenant_id, namespace_name, flow_key, trigger_key
        FROM scheduler_states
        WHERE next_fire_at <= clock_timestamp()
        ORDER BY next_fire_at
        LIMIT 100
    """,
}


async def qualify_postgres(
    settings: Settings,
    *,
    profile: str,
    require_tls: bool,
    latency_samples: int = 50,
    max_p95_ms: float = 50.0,
) -> dict[str, Any]:
    connection = await asyncpg.connect(
        settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1),
        ssl=database_ssl_argument(settings),
    )
    try:
        server_version_num = int(await connection.fetchval("SHOW server_version_num"))
        major_version = server_version_num // 10_000
        ssl_active = bool(
            await connection.fetchval("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
        )
        timings: list[float] = []
        for _ in range(latency_samples):
            started = perf_counter()
            await connection.fetchval("SELECT 1")
            timings.append((perf_counter() - started) * 1_000)
        ordered = sorted(timings)
        percentile_index = min(len(ordered) - 1, int(len(ordered) * 0.95))
        p95_ms = ordered[percentile_index]
        indexes = {
            str(row["indexname"])
            for row in await connection.fetch(
                "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
            )
        }
        missing_indexes = sorted(REQUIRED_CRITICAL_INDEXES - indexes)
        plans: dict[str, Any] = {}
        async with connection.transaction():
            await connection.execute("SET LOCAL enable_seqscan = off")
            for name, query in _CRITICAL_PLANS.items():
                encoded = await connection.fetchval(f"EXPLAIN (FORMAT JSON) {query}")
                plans[name] = json.loads(encoded) if isinstance(encoded, str) else encoded
        schema_version = await connection.fetchval(
            "SELECT max(version) FROM amesh_schema_migrations"
        )
        latest_checkpoint = await connection.fetchrow(
            """
            SELECT database_lsn::text AS database_lsn,
                   object_manifest_uri,
                   object_manifest_checksum,
                   created_at
            FROM backup_checkpoints
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """
        )
        maintenance = await connection.fetch(
            """
            SELECT
                statistics.relname AS table_name,
                statistics.n_live_tup AS live_rows,
                statistics.n_dead_tup AS dead_rows,
                pg_total_relation_size(statistics.relid) AS total_bytes,
                statistics.last_autovacuum,
                statistics.last_autoanalyze,
                EXISTS (
                    SELECT 1
                    FROM pg_partitioned_table
                    WHERE pg_partitioned_table.partrelid = statistics.relid
                ) AS partitioned
            FROM pg_stat_user_tables AS statistics
            ORDER BY pg_total_relation_size(statistics.relid) DESC, statistics.relname
            """
        )
    finally:
        await connection.close()

    failures: list[str] = []
    if major_version not in SUPPORTED_POSTGRES_MAJOR_VERSIONS:
        failures.append(f"unsupported PostgreSQL major version {major_version}")
    if require_tls and not ssl_active:
        failures.append("TLS is required but the qualification connection is not encrypted")
    if missing_indexes:
        failures.append("missing critical indexes: " + ", ".join(missing_indexes))
    if p95_ms > max_p95_ms:
        failures.append(f"SELECT 1 p95 {p95_ms:.3f} ms exceeds {max_p95_ms:.3f} ms")
    return {
        "profile": profile,
        "passed": not failures,
        "failures": failures,
        "postgresMajor": major_version,
        "postgresVersionNumber": server_version_num,
        "tlsActive": ssl_active,
        "schemaVersion": str(schema_version),
        "latency": {
            "samples": latency_samples,
            "meanMs": round(mean(timings), 3),
            "p95Ms": round(p95_ms, 3),
            "maximumP95Ms": max_p95_ms,
        },
        "criticalIndexes": sorted(REQUIRED_CRITICAL_INDEXES),
        "missingIndexes": missing_indexes,
        "queryPlans": plans,
        "latestBackupCheckpoint": dict(latest_checkpoint) if latest_checkpoint else None,
        "tableMaintenance": [dict(row) for row in maintenance],
    }
