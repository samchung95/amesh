from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Protocol
from uuid import UUID, uuid5

import asyncpg  # type: ignore[import-untyped]
import psutil
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.agent_session_harness import (
    PI_ADAPTER,
    PI_ADAPTER_VERSION,
    PI_WORKER_PROTOCOL,
)
from amesh.adapters.postgres import PostgresAgentSessionRepository
from amesh.entrypoints.migrations import (
    EphemeralDatabase,
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

DEFAULT_DURABLE_SESSIONS = 10_000
DEFAULT_CONCURRENT_STREAM_READERS = 1_000
DEFAULT_REPLICAS = 3
QUALIFICATION_PROFILE = "agent-session-service-local-reference-v1"

_QUALIFICATION_NAMESPACE = UUID("d707f981-42e0-56b0-bb5a-02101ed78155")
_TENANT_SLUGS = ("default", "qualification-shadow")
_NAMESPACE_NAME = "qualification.agent-sessions"
_FLOW_KEY = "session-reference"
_AGENT_KEY = "qualification-agent"
_BATCH_SIZE = 1_000


@dataclass(frozen=True)
class QualificationConfig:
    durable_sessions: int = DEFAULT_DURABLE_SESSIONS
    concurrent_stream_readers: int = DEFAULT_CONCURRENT_STREAM_READERS
    replicas: int = DEFAULT_REPLICAS

    def __post_init__(self) -> None:
        if self.durable_sessions < 1:
            raise ValueError("durable session count must be positive")
        if self.concurrent_stream_readers < 1:
            raise ValueError("concurrent stream reader count must be positive")
        if self.concurrent_stream_readers > self.durable_sessions:
            raise ValueError("concurrent stream readers cannot exceed durable sessions")
        if self.replicas < 1:
            raise ValueError("replica count must be positive")


@dataclass(frozen=True)
class SessionReference:
    ordinal: int
    tenant_id: str
    other_tenant_id: str
    service_session_id: UUID
    execution_id: UUID
    task_run_id: UUID
    attempt: int
    expected_result_digest: str


@dataclass(frozen=True)
class CursorObservation:
    service_session_id: UUID
    execution_id: UUID
    event_count: int
    result_digest: str | None


@dataclass(frozen=True)
class IntegritySnapshot:
    durable_sessions: int
    unique_service_session_ids: int
    terminal_results: int
    matched_results: int
    agent_events: int
    duplicate_service_session_ids: int
    duplicate_event_keys: int
    cross_tenant_rows: int


class QualificationProjection(Protocol):
    async def seed(self, count: int) -> tuple[SessionReference, ...]: ...

    async def read_cursor(
        self,
        replica_index: int,
        reference: SessionReference,
    ) -> CursorObservation: ...

    async def cross_tenant_event_count(
        self,
        replica_index: int,
        reference: SessionReference,
    ) -> int: ...

    async def session_guard_claim_count(
        self,
        leader_replica_index: int,
        reference: SessionReference,
    ) -> int: ...

    async def inspect_integrity(self) -> IntegritySnapshot: ...

    async def environment(self) -> dict[str, object]: ...


class PostgresQualificationProjection:
    """Synthetic fixture writer plus the real PostgreSQL session projection readers."""

    def __init__(self, database_url: str, replicas: Sequence[AsyncEngine], run_id: UUID) -> None:
        if not replicas:
            raise ValueError("at least one PostgreSQL projection replica is required")
        self._database_url = database_url
        self._engines = tuple(replicas)
        self._repositories = tuple(PostgresAgentSessionRepository(engine) for engine in replicas)
        self._run_id = run_id

    @classmethod
    def connect(
        cls,
        database_url: str,
        *,
        replica_count: int,
        run_id: UUID,
    ) -> PostgresQualificationProjection:
        pool_size = max(1, min(10, 90 // replica_count))
        engines = tuple(
            create_async_engine(
                database_url,
                pool_size=pool_size,
                max_overflow=0,
                pool_pre_ping=True,
            )
            for _ in range(replica_count)
        )
        return cls(database_url, engines, run_id)

    async def close(self) -> None:
        await asyncio.gather(*(engine.dispose() for engine in self._engines))

    async def seed(self, count: int) -> tuple[SessionReference, ...]:
        connection = await asyncpg.connect(_asyncpg_url(self._database_url))
        try:
            async with connection.transaction():
                authorities = await _seed_authorities(connection)
                references: list[SessionReference] = []
                for start in range(0, count, _BATCH_SIZE):
                    batch = tuple(
                        _session_reference(index)
                        for index in range(start, min(start + _BATCH_SIZE, count))
                    )
                    await _seed_batch(connection, authorities, batch, self._run_id)
                    references.extend(batch)
        finally:
            await connection.close()
        return tuple(references)

    async def read_cursor(
        self,
        replica_index: int,
        reference: SessionReference,
    ) -> CursorObservation:
        repository = self._repositories[replica_index % len(self._repositories)]
        execution_id = await repository.get_execution_by_service_session_id(
            reference.tenant_id,
            reference.service_session_id,
        )
        records = await repository.list_execution_sessions(reference.tenant_id, execution_id)
        if not records:
            raise LookupError("the service session has no durable agent attempt")
        record = max(records, key=lambda item: (item.attempt, item.updated_at, item.session_id))
        detail = await repository.get_session(
            reference.tenant_id,
            record.task_run_id,
            record.attempt,
        )
        result_digest = None
        if detail.session.final_result is not None:
            candidate = detail.session.final_result.get("resultDigest")
            if isinstance(candidate, str):
                result_digest = candidate
        return CursorObservation(
            service_session_id=reference.service_session_id,
            execution_id=execution_id,
            event_count=len(detail.events),
            result_digest=result_digest,
        )

    async def cross_tenant_event_count(
        self,
        replica_index: int,
        reference: SessionReference,
    ) -> int:
        repository = self._repositories[replica_index % len(self._repositories)]
        try:
            execution_id = await repository.get_execution_by_service_session_id(
                reference.other_tenant_id,
                reference.service_session_id,
            )
        except LookupError:
            return 0
        records = await repository.list_execution_sessions(reference.other_tenant_id, execution_id)
        leaked_events = 0
        for record in records:
            detail = await repository.get_session(
                reference.other_tenant_id,
                record.task_run_id,
                record.attempt,
            )
            leaked_events += len(detail.events)
        return leaked_events

    async def session_guard_claim_count(
        self,
        leader_replica_index: int,
        reference: SessionReference,
    ) -> int:
        leader = self._repositories[leader_replica_index % len(self._repositories)]
        followers = tuple(
            repository
            for index, repository in enumerate(self._repositories)
            if index != leader_replica_index % len(self._repositories)
        )
        async with leader.session_guard(
            reference.tenant_id,
            reference.task_run_id,
            reference.attempt,
        ):
            follower_claims = await asyncio.gather(
                *(_try_session_guard(repository, reference) for repository in followers)
            )
        return 1 + sum(follower_claims)

    async def inspect_integrity(self) -> IntegritySnapshot:
        connection = await asyncpg.connect(_asyncpg_url(self._database_url))
        try:
            summary = await connection.fetchrow(
                """
                WITH qualified_executions AS (
                    SELECT id, tenant_id,
                           trigger_context->>'ameshAgentSessionId' AS service_session_id,
                           trigger_context->>'qualificationResultDigest' AS expected_digest
                    FROM executions
                    WHERE trigger_context->>'qualificationRunId' = $1
                ), qualified_sessions AS (
                    SELECT sessions.*, qualified.service_session_id, qualified.expected_digest
                    FROM qualified_executions AS qualified
                    JOIN agent_sessions AS sessions
                      ON sessions.tenant_id = qualified.tenant_id
                     AND sessions.execution_id = qualified.id
                )
                SELECT
                    (SELECT count(*) FROM qualified_executions) AS durable_sessions,
                    (SELECT count(DISTINCT service_session_id) FROM qualified_executions)
                        AS unique_service_session_ids,
                    count(*) FILTER (WHERE sessions.final_result IS NOT NULL)
                        AS terminal_results,
                    count(*) FILTER (
                        WHERE sessions.final_result->>'resultDigest' = sessions.expected_digest
                    ) AS matched_results,
                    (SELECT count(*)
                     FROM agent_session_events AS events
                     JOIN qualified_sessions AS selected
                       ON selected.session_id = events.session_id)
                        AS agent_events,
                    (SELECT COALESCE(sum(duplicates.count - 1), 0)
                     FROM (
                         SELECT count(*) AS count
                         FROM qualified_executions
                         GROUP BY service_session_id
                         HAVING count(*) > 1
                     ) AS duplicates) AS duplicate_service_session_ids,
                    (SELECT COALESCE(sum(duplicates.count - 1), 0)
                     FROM (
                         SELECT count(*) AS count
                         FROM agent_session_events AS events
                         JOIN qualified_sessions AS selected
                           ON selected.session_id = events.session_id
                         GROUP BY events.tenant_id, events.session_id, events.event_key
                         HAVING count(*) > 1
                     ) AS duplicates) AS duplicate_event_keys,
                    (SELECT count(*)
                     FROM agent_session_events AS events
                     JOIN qualified_sessions AS selected
                       ON selected.session_id = events.session_id
                     WHERE events.tenant_id <> selected.tenant_id
                        OR events.execution_id <> selected.execution_id
                        OR events.task_run_id <> selected.task_run_id)
                        AS cross_tenant_rows
                FROM qualified_sessions AS sessions
                """,
                str(self._run_id),
            )
            if summary is None:
                raise RuntimeError("PostgreSQL returned no session qualification integrity row")
            return IntegritySnapshot(
                durable_sessions=int(summary["durable_sessions"]),
                unique_service_session_ids=int(summary["unique_service_session_ids"]),
                terminal_results=int(summary["terminal_results"]),
                matched_results=int(summary["matched_results"]),
                agent_events=int(summary["agent_events"]),
                duplicate_service_session_ids=int(summary["duplicate_service_session_ids"]),
                duplicate_event_keys=int(summary["duplicate_event_keys"]),
                cross_tenant_rows=int(summary["cross_tenant_rows"]),
            )
        finally:
            await connection.close()

    async def environment(self) -> dict[str, object]:
        connection = await asyncpg.connect(_asyncpg_url(self._database_url))
        try:
            version = str(await connection.fetchval("SELECT version()"))
            server_version_number = int(await connection.fetchval("SHOW server_version_num"))
        finally:
            await connection.close()
        return {
            "postgresVersion": version,
            "postgresVersionNumber": server_version_number,
            "projectionReplicas": len(self._repositories),
            "databaseName": self._database_url.rsplit("/", maxsplit=1)[-1].split("?", maxsplit=1)[
                0
            ],
        }


async def qualify_projection(
    projection: QualificationProjection,
    config: QualificationConfig,
    *,
    hardware: dict[str, object] | None = None,
) -> dict[str, object]:
    seed_started = perf_counter()
    references = await projection.seed(config.durable_sessions)
    seed_seconds = perf_counter() - seed_started
    if len(references) != config.durable_sessions:
        raise RuntimeError(
            f"projection returned {len(references)} references for "
            f"{config.durable_sessions} seeded sessions"
        )
    selected = _sample_references(references, config.concurrent_stream_readers)

    stream_started = asyncio.Event()

    async def timed_cursor_read(
        index: int,
        reference: SessionReference,
    ) -> tuple[float, CursorObservation]:
        await stream_started.wait()
        started = perf_counter()
        observation = await projection.read_cursor(index % config.replicas, reference)
        return (perf_counter() - started) * 1_000, observation

    reader_tasks = tuple(
        asyncio.create_task(timed_cursor_read(index, reference))
        for index, reference in enumerate(selected)
    )
    stream_wall_started = perf_counter()
    stream_started.set()
    reader_results = await asyncio.gather(*reader_tasks, return_exceptions=True)
    stream_wall_seconds = perf_counter() - stream_wall_started

    stream_latencies: list[float] = []
    reader_errors: list[str] = []
    reader_mismatches = 0
    for reference, outcome in zip(selected, reader_results, strict=True):
        if isinstance(outcome, BaseException):
            reader_errors.append(_safe_error(outcome))
            continue
        latency_ms, observation = outcome
        stream_latencies.append(latency_ms)
        if (
            observation.service_session_id != reference.service_session_id
            or observation.execution_id != reference.execution_id
            or observation.event_count < 1
            or observation.result_digest != reference.expected_result_digest
        ):
            reader_mismatches += 1

    isolation_outcomes = await asyncio.gather(
        *(
            projection.cross_tenant_event_count(index % config.replicas, reference)
            for index, reference in enumerate(selected)
        ),
        return_exceptions=True,
    )
    isolation_errors = [
        _safe_error(outcome) for outcome in isolation_outcomes if isinstance(outcome, BaseException)
    ]
    cross_tenant_probe_events = sum(
        outcome for outcome in isolation_outcomes if isinstance(outcome, int)
    )

    claim_latencies: list[float] = []
    duplicate_claims = 0
    claim_errors: list[str] = []
    for index, reference in enumerate(selected):
        started = perf_counter()
        try:
            claims = await projection.session_guard_claim_count(index % config.replicas, reference)
        except Exception as exc:  # qualification must report failed probes as data
            claim_errors.append(_safe_error(exc))
        else:
            claim_latencies.append((perf_counter() - started) * 1_000)
            duplicate_claims += max(0, claims - 1)

    integrity = await projection.inspect_integrity()
    environment = await projection.environment()
    missing_seeded_result_projections = max(
        0,
        config.durable_sessions - integrity.matched_results,
    )
    cross_tenant_events = integrity.cross_tenant_rows + cross_tenant_probe_events
    failures: list[str] = []
    if integrity.durable_sessions != config.durable_sessions:
        failures.append("durable session count differs from the configured target")
    if integrity.unique_service_session_ids != config.durable_sessions:
        failures.append("service session identifiers are not unique")
    if integrity.terminal_results != config.durable_sessions or missing_seeded_result_projections:
        failures.append("one or more durable terminal results are missing or mismatched")
    if integrity.agent_events < config.durable_sessions:
        failures.append("one or more durable sessions have no event")
    if integrity.duplicate_service_session_ids or integrity.duplicate_event_keys:
        failures.append("duplicate durable projection identities were observed")
    if duplicate_claims:
        failures.append("more than one replica acquired a session guard concurrently")
    if cross_tenant_events:
        failures.append("a cross-tenant session event was visible")
    if reader_mismatches or reader_errors:
        failures.append("one or more concurrent cursor readers returned an invalid result")
    if isolation_errors:
        failures.append("one or more cross-tenant isolation probes failed to complete")
    if claim_errors:
        failures.append("one or more session guard probes failed to complete")

    return {
        "profile": QUALIFICATION_PROFILE,
        "passed": not failures,
        "failures": failures,
        "scope": {
            "type": "synthetic-local-postgresql-reference",
            "includes": [
                "PostgreSQL-authoritative execution/session/result rows",
                "real AMESH tenant-scoped session projection readers",
                "real AMESH PostgreSQL advisory session guards",
                "logical stateless projection replicas",
            ],
            "excludes": [
                "model or provider latency and output quality",
                "network load balancers and remote stream transport",
                "production high availability, backup, restore, and disaster recovery",
                "a production SLO claim for the recorded local latency",
            ],
        },
        "target": {
            "durableSessions": config.durable_sessions,
            "concurrentStreamReaders": config.concurrent_stream_readers,
            "projectionReplicas": config.replicas,
            "sessionGuardProbes": len(selected),
        },
        "hardware": hardware if hardware is not None else _hardware_profile(),
        "database": environment,
        "latency": {
            "seed": {
                "elapsedSeconds": round(seed_seconds, 6),
                "sessionsPerSecond": round(config.durable_sessions / seed_seconds, 3),
            },
            "streamCursorReads": {
                "samples": len(stream_latencies),
                "wallSeconds": round(stream_wall_seconds, 6),
                **_latency_summary(stream_latencies),
            },
            "sessionGuardClaims": {
                "samples": len(claim_latencies),
                **_latency_summary(claim_latencies),
            },
        },
        "integrity": {
            "durableSessionsObserved": integrity.durable_sessions,
            "uniqueServiceSessionIds": integrity.unique_service_session_ids,
            "terminalResultsObserved": integrity.terminal_results,
            "matchedResults": integrity.matched_results,
            "agentEventsObserved": integrity.agent_events,
            "missingSeededResultProjections": missing_seeded_result_projections,
            "duplicateClaims": duplicate_claims,
            "duplicateServiceSessionIds": integrity.duplicate_service_session_ids,
            "duplicateEventKeys": integrity.duplicate_event_keys,
            "crossTenantEvents": cross_tenant_events,
            "readerMismatches": reader_mismatches,
            "readerErrors": reader_errors,
            "isolationErrors": isolation_errors,
            "claimErrors": claim_errors,
            "zeroMissingSeededResultProjections": missing_seeded_result_projections == 0,
            "zeroDuplicateClaims": duplicate_claims == 0,
            "zeroCrossTenantEvents": cross_tenant_events == 0,
        },
    }


async def qualify_postgres_session_service(
    admin_database_url: str,
    config: QualificationConfig,
    *,
    retain_database: bool = False,
) -> dict[str, object]:
    database: EphemeralDatabase | None = None
    projection: PostgresQualificationProjection | None = None
    try:
        database = await create_ephemeral_database(admin_database_url)
        await apply_migrations(database.database_url, migration_directory())
        run_id = uuid5(_QUALIFICATION_NAMESPACE, database.name)
        projection = PostgresQualificationProjection.connect(
            database.database_url,
            replica_count=config.replicas,
            run_id=run_id,
        )
        report = await qualify_projection(projection, config)
        database_report = report["database"]
        if not isinstance(database_report, dict):
            raise RuntimeError("qualification database metadata is not an object")
        report["database"] = {
            **database_report,
            "retainedForInspection": retain_database,
        }
        return report
    finally:
        if projection is not None:
            await projection.close()
        if database is not None and not retain_database:
            await drop_ephemeral_database(admin_database_url, database.name)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Run the local PostgreSQL agent-session reference qualification"
    )
    result.add_argument(
        "--database-url",
        default=os.getenv("AMESH_TEST_DATABASE_URL"),
        help=(
            "admin PostgreSQL URL used only to create an amesh_test_* database "
            "(default: AMESH_TEST_DATABASE_URL)"
        ),
    )
    result.add_argument("--durable-sessions", type=int, default=DEFAULT_DURABLE_SESSIONS)
    result.add_argument(
        "--concurrent-stream-readers",
        type=int,
        default=DEFAULT_CONCURRENT_STREAM_READERS,
    )
    result.add_argument("--replicas", type=int, default=DEFAULT_REPLICAS)
    result.add_argument("--output", type=Path)
    result.add_argument(
        "--retain-database",
        action="store_true",
        help="retain the generated amesh_test_* database for manual inspection",
    )
    return result


def main() -> int:
    arguments = parser().parse_args()
    if not arguments.database_url:
        raise SystemExit(
            "--database-url or AMESH_TEST_DATABASE_URL is required; "
            "the URL must point to a PostgreSQL server, not a shared application database"
        )
    try:
        config = QualificationConfig(
            durable_sessions=arguments.durable_sessions,
            concurrent_stream_readers=arguments.concurrent_stream_readers,
            replicas=arguments.replicas,
        )
        report = asyncio.run(
            qualify_postgres_session_service(
                arguments.database_url,
                config,
                retain_database=arguments.retain_database,
            )
        )
    except Exception as exc:
        report = {
            "profile": QUALIFICATION_PROFILE,
            "passed": False,
            "failures": [_safe_error(exc)],
            "scope": {
                "type": "synthetic-local-postgresql-reference",
                "excludes": [
                    "model or provider latency and output quality",
                    "production high availability, backup, restore, and disaster recovery",
                ],
            },
            "hardware": _hardware_profile(),
        }
    encoded = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["passed"] else 1


async def _seed_authorities(
    connection: asyncpg.Connection[asyncpg.Record],
) -> dict[str, dict[str, UUID]]:
    shadow_tenant_id = uuid5(_QUALIFICATION_NAMESPACE, "tenant:qualification-shadow")
    await connection.execute(
        """
        INSERT INTO tenants (
            id, slug, display_name, status, storage_prefix, created_by, updated_by
        ) VALUES ($1, $2, $3, 'ACTIVE', $4, 'qualification', 'qualification')
        ON CONFLICT (slug) DO NOTHING
        """,
        shadow_tenant_id,
        _TENANT_SLUGS[1],
        "Agent session qualification shadow tenant",
        f"tenants/{_TENANT_SLUGS[1]}/",
    )
    authorities: dict[str, dict[str, UUID]] = {}
    for tenant_slug in _TENANT_SLUGS:
        tenant_id = await connection.fetchval(
            "SELECT id FROM tenants WHERE slug = $1",
            tenant_slug,
        )
        if not isinstance(tenant_id, UUID):
            raise RuntimeError(f"qualification tenant {tenant_slug!r} is unavailable")
        namespace_id = uuid5(_QUALIFICATION_NAMESPACE, f"namespace:{tenant_slug}")
        flow_id = uuid5(_QUALIFICATION_NAMESPACE, f"flow:{tenant_slug}")
        flow_revision_id = uuid5(_QUALIFICATION_NAMESPACE, f"flow-revision:{tenant_slug}:1")
        agent_resource_id = uuid5(_QUALIFICATION_NAMESPACE, f"agent:{tenant_slug}")
        await connection.execute(
            """
            INSERT INTO namespaces (id, tenant_id, name, created_by, updated_by)
            VALUES ($1, $2, $3, 'qualification', 'qualification')
            ON CONFLICT (tenant_id, name) DO NOTHING
            """,
            namespace_id,
            tenant_id,
            _NAMESPACE_NAME,
        )
        await connection.execute(
            """
            INSERT INTO flows (
                id, tenant_id, namespace_id, flow_key, status, created_by, updated_by
            ) VALUES ($1, $2, $3, $4, 'DRAFT', 'qualification', 'qualification')
            ON CONFLICT (tenant_id, namespace_id, flow_key) DO NOTHING
            """,
            flow_id,
            tenant_id,
            namespace_id,
            _FLOW_KEY,
        )
        canonical_flow = json.dumps(
            {
                "id": _FLOW_KEY,
                "namespace": _NAMESPACE_NAME,
                "revision": 1,
                "tasks": [{"id": "agent", "type": "agent.session"}],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        await connection.execute(
            """
            INSERT INTO flow_revisions (
                id, tenant_id, flow_id, revision, semantic_hash,
                canonical_definition, plugin_resolution, created_by
            ) VALUES ($1, $2, $3, 1, $4, $5::jsonb, $6::jsonb, 'qualification')
            ON CONFLICT (tenant_id, flow_id, revision) DO NOTHING
            """,
            flow_revision_id,
            tenant_id,
            flow_id,
            hashlib.sha256(canonical_flow.encode()).hexdigest(),
            canonical_flow,
            json.dumps(
                {"resources": [{"kind": "task", "type": "agent.session"}]},
                separators=(",", ":"),
            ),
        )
        await connection.execute(
            """
            UPDATE flows
            SET active_revision = 1, status = 'ACTIVE', updated_by = 'qualification'
            WHERE tenant_id = $1 AND id = $2
            """,
            tenant_id,
            flow_id,
        )
        agent_spec = json.dumps(
            {
                "key": _AGENT_KEY,
                "namespace": _NAMESPACE_NAME,
                "title": "Qualification agent",
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        await connection.execute(
            """
            INSERT INTO agent_resource_revisions (
                resource_id, revision, tenant_id, namespace_name, resource_kind,
                resource_key, digest, spec, created_by
            ) VALUES ($1, 1, $2, $3, 'AGENT', $4, $5, $6::jsonb, 'qualification')
            ON CONFLICT (resource_id, revision) DO NOTHING
            """,
            agent_resource_id,
            tenant_id,
            _NAMESPACE_NAME,
            _AGENT_KEY,
            _sha256(agent_spec),
            agent_spec,
        )
        authorities[tenant_slug] = {
            "tenant_id": tenant_id,
            "flow_id": flow_id,
            "flow_revision_id": flow_revision_id,
            "agent_resource_id": agent_resource_id,
        }
    return authorities


async def _seed_batch(
    connection: asyncpg.Connection[asyncpg.Record],
    authorities: dict[str, dict[str, UUID]],
    references: Sequence[SessionReference],
    run_id: UUID,
) -> None:
    created_at = datetime.now(UTC)
    execution_rows: list[tuple[object, ...]] = []
    task_rows: list[tuple[object, ...]] = []
    pin_rows: list[tuple[object, ...]] = []
    session_rows: list[tuple[object, ...]] = []
    event_rows: list[tuple[object, ...]] = []
    for reference in references:
        authority = authorities[reference.tenant_id]
        session_id = uuid5(_QUALIFICATION_NAMESPACE, f"attempt:{reference.service_session_id}")
        pin_id = uuid5(_QUALIFICATION_NAMESPACE, f"pin:{reference.service_session_id}")
        event_id = uuid5(_QUALIFICATION_NAMESPACE, f"event:{reference.service_session_id}:1")
        ordinal = reference.ordinal
        final_result = {
            "accepted": True,
            "ordinal": ordinal,
            "resultDigest": reference.expected_result_digest,
        }
        envelope_digest = _sha256(f"qualification-envelope:{ordinal}")
        execution_rows.append(
            (
                reference.execution_id,
                authority["tenant_id"],
                authority["flow_id"],
                authority["flow_revision_id"],
                _NAMESPACE_NAME,
                _FLOW_KEY,
                "SUCCESS",
                1,
                4,
                f"qualification:{run_id}:{ordinal}",
                "{}",
                json.dumps(
                    {
                        "ameshAgentSessionId": str(reference.service_session_id),
                        "ameshAgentRef": f"{_NAMESPACE_NAME}/{_AGENT_KEY}@1",
                        "qualificationResultDigest": reference.expected_result_digest,
                        "qualificationRunId": str(run_id),
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                '{"amesh.io/qualification":"agent-session-service"}',
                "qualification",
                "qualification",
                created_at,
                created_at,
                created_at,
            )
        )
        task_rows.append(
            (
                reference.task_run_id,
                authority["tenant_id"],
                reference.execution_id,
                "agent",
                "SUCCESS",
                1,
                3,
                json.dumps(final_result, separators=(",", ":"), sort_keys=True),
            )
        )
        pin_rows.append(
            (
                pin_id,
                authority["tenant_id"],
                _NAMESPACE_NAME,
                authority["agent_resource_id"],
                f"qualification:{reference.task_run_id}:1",
                envelope_digest,
                json.dumps(
                    {"agent": _AGENT_KEY, "revision": 1},
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            )
        )
        session_rows.append(
            (
                session_id,
                authority["tenant_id"],
                reference.execution_id,
                reference.task_run_id,
                pin_id,
                envelope_digest,
                json.dumps(
                    {"messages": [], "nextTurn": 1},
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                json.dumps(
                    {"turns": 1, "totalTokens": 0, "costUsd": "0"},
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                json.dumps(final_result, separators=(",", ":"), sort_keys=True),
                PI_ADAPTER,
                PI_ADAPTER_VERSION,
                PI_WORKER_PROTOCOL,
                created_at,
                created_at,
            )
        )
        event_rows.append(
            (
                event_id,
                authority["tenant_id"],
                reference.execution_id,
                reference.task_run_id,
                session_id,
                json.dumps(
                    {"result": final_result, "schemaValid": True},
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                created_at,
            )
        )

    await connection.executemany(
        """
        INSERT INTO executions (
            id, tenant_id, flow_id, flow_revision_id, namespace_name, flow_key,
            state, epoch, version, idempotency_key, inputs, trigger_context, labels,
            created_by, updated_by, created_at, updated_at, terminal_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
            $11::jsonb, $12::jsonb, $13::jsonb, $14, $15, $16, $17, $18
        )
        """,
        execution_rows,
    )
    await connection.executemany(
        """
        INSERT INTO task_runs (
            id, tenant_id, execution_id, task_path, state,
            current_attempt, version, terminal_result
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
        """,
        task_rows,
    )
    await connection.executemany(
        """
        INSERT INTO agent_capability_pins (
            pin_id, tenant_id, namespace_name, agent_resource_id, agent_revision,
            subject_ref, envelope_digest, envelope, created_by
        ) VALUES ($1, $2, $3, $4, 1, $5, $6, $7::jsonb, 'qualification')
        """,
        pin_rows,
    )
    await connection.executemany(
        """
        INSERT INTO agent_sessions (
            session_id, tenant_id, namespace_name, execution_id, task_run_id, attempt,
            capability_pin_id, envelope_digest, state, phase, version,
            checkpoint, counters, final_result, harness_adapter, harness_version,
            harness_protocol, created_at, updated_at, completed_at
        ) VALUES (
            $1, $2, $3, $4, $5, 1, $6, $7, 'SUCCEEDED', 'COMPLETE', 1,
            $8::jsonb, $9::jsonb, $10::jsonb, $11, $12, $13,
            $14, $15, $15
        )
        """,
        [
            (
                row[0],
                row[1],
                _NAMESPACE_NAME,
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                row[12],
                row[13],
            )
            for row in session_rows
        ],
    )
    await connection.executemany(
        """
        INSERT INTO agent_session_events (
            event_id, tenant_id, execution_id, task_run_id, session_id,
            event_index, event_key, event_type, payload, occurred_at
        ) VALUES ($1, $2, $3, $4, $5, 1, 'output.accepted', 'output.accepted', $6::jsonb, $7)
        """,
        event_rows,
    )


async def _try_session_guard(
    repository: PostgresAgentSessionRepository,
    reference: SessionReference,
) -> int:
    try:
        async with repository.session_guard(
            reference.tenant_id,
            reference.task_run_id,
            reference.attempt,
        ):
            return 1
    except RuntimeError as exc:
        if str(exc) != "agent session is already running on another worker":
            raise
        return 0


def _session_reference(index: int) -> SessionReference:
    tenant_index = index % len(_TENANT_SLUGS)
    tenant_id = _TENANT_SLUGS[tenant_index]
    other_tenant_id = _TENANT_SLUGS[(tenant_index + 1) % len(_TENANT_SLUGS)]
    service_session_id = uuid5(_QUALIFICATION_NAMESPACE, f"service-session:{index}")
    return SessionReference(
        ordinal=index,
        tenant_id=tenant_id,
        other_tenant_id=other_tenant_id,
        service_session_id=service_session_id,
        execution_id=uuid5(_QUALIFICATION_NAMESPACE, f"execution:{index}"),
        task_run_id=uuid5(_QUALIFICATION_NAMESPACE, f"task-run:{index}"),
        attempt=1,
        expected_result_digest=_sha256(f"qualification-result:{index}"),
    )


def _sample_references(
    references: Sequence[SessionReference],
    count: int,
) -> tuple[SessionReference, ...]:
    return tuple(references[(index * len(references)) // count] for index in range(count))


def _latency_summary(samples: Sequence[float]) -> dict[str, float | None]:
    if not samples:
        return {"meanMs": None, "p50Ms": None, "p95Ms": None, "p99Ms": None, "maxMs": None}
    ordered = sorted(samples)
    return {
        "meanMs": round(mean(ordered), 3),
        "p50Ms": round(_percentile(ordered, 0.50), 3),
        "p95Ms": round(_percentile(ordered, 0.95), 3),
        "p99Ms": round(_percentile(ordered, 0.99), 3),
        "maxMs": round(ordered[-1], 3),
    }


def _percentile(ordered: Sequence[float], percentile: float) -> float:
    index = max(0, min(len(ordered) - 1, int(len(ordered) * percentile + 0.999999) - 1))
    return ordered[index]


def _hardware_profile() -> dict[str, object]:
    return {
        "operatingSystem": platform.system(),
        "operatingSystemRelease": platform.release(),
        "architecture": platform.machine(),
        "pythonVersion": platform.python_version(),
        "pythonImplementation": platform.python_implementation(),
        "logicalCpuCount": psutil.cpu_count(logical=True),
        "physicalCpuCount": psutil.cpu_count(logical=False),
        "memoryTotalBytes": psutil.virtual_memory().total,
        "processId": os.getpid(),
    }


def _sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode()).hexdigest()


def _asyncpg_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


def _safe_error(error: BaseException) -> str:
    message = str(error).strip()
    return f"{type(error).__name__}: {message}" if message else type(error).__name__


if __name__ == "__main__":
    sys.exit(main())
