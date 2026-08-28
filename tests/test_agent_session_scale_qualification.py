from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import replace
from pathlib import Path
from uuid import UUID, uuid5

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.qualify_agent_session_service import (  # noqa: E402
    DEFAULT_CONCURRENT_STREAM_READERS,
    DEFAULT_DURABLE_SESSIONS,
    DEFAULT_REPLICAS,
    CursorObservation,
    IntegritySnapshot,
    QualificationConfig,
    SessionReference,
    parser,
    qualify_postgres_session_service,
    qualify_projection,
)

_TEST_NAMESPACE = UUID("2e8d4265-3804-59ab-93d2-e69d74013e17")
_TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")


class FakeProjection:
    def __init__(
        self,
        *,
        integrity: IntegritySnapshot | None = None,
        guard_claims: int = 1,
    ) -> None:
        self._references: tuple[SessionReference, ...] = ()
        self._integrity = integrity
        self._guard_claims = guard_claims
        self.active_readers = 0
        self.maximum_active_readers = 0
        self.reader_replicas: set[int] = set()

    async def seed(self, count: int) -> tuple[SessionReference, ...]:
        self._references = tuple(_reference(index) for index in range(count))
        return self._references

    async def read_cursor(
        self,
        replica_index: int,
        reference: SessionReference,
    ) -> CursorObservation:
        self.reader_replicas.add(replica_index)
        self.active_readers += 1
        self.maximum_active_readers = max(self.maximum_active_readers, self.active_readers)
        await asyncio.sleep(0)
        self.active_readers -= 1
        return CursorObservation(
            service_session_id=reference.service_session_id,
            execution_id=reference.execution_id,
            event_count=1,
            result_digest=reference.expected_result_digest,
        )

    async def cross_tenant_event_count(
        self,
        replica_index: int,
        reference: SessionReference,
    ) -> int:
        del replica_index, reference
        return 0

    async def session_guard_claim_count(
        self,
        leader_replica_index: int,
        reference: SessionReference,
    ) -> int:
        del leader_replica_index, reference
        return self._guard_claims

    async def inspect_integrity(self) -> IntegritySnapshot:
        if self._integrity is not None:
            return self._integrity
        count = len(self._references)
        return IntegritySnapshot(
            durable_sessions=count,
            unique_service_session_ids=count,
            terminal_results=count,
            matched_results=count,
            agent_events=count,
            duplicate_service_session_ids=0,
            duplicate_event_keys=0,
            cross_tenant_rows=0,
        )

    async def environment(self) -> dict[str, object]:
        return {"postgresVersionNumber": 160000, "projectionReplicas": 3}


def test_reference_defaults_are_the_required_opt_in_profile() -> None:
    arguments = parser().parse_args([])

    assert arguments.durable_sessions == DEFAULT_DURABLE_SESSIONS == 10_000
    assert arguments.concurrent_stream_readers == DEFAULT_CONCURRENT_STREAM_READERS == 1_000
    assert arguments.replicas == DEFAULT_REPLICAS == 3


@pytest.mark.parametrize(
    ("durable_sessions", "stream_readers", "replicas", "message"),
    (
        (0, 1, 1, "durable session count"),
        (1, 0, 1, "stream reader count"),
        (1, 2, 1, "cannot exceed"),
        (1, 1, 0, "replica count"),
    ),
)
def test_configuration_rejects_non_executable_workloads(
    durable_sessions: int,
    stream_readers: int,
    replicas: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        QualificationConfig(
            durable_sessions=durable_sessions,
            concurrent_stream_readers=stream_readers,
            replicas=replicas,
        )


def test_small_reference_workload_emits_machine_readable_integrity_and_latency() -> None:
    projection = FakeProjection()
    config = QualificationConfig(
        durable_sessions=12,
        concurrent_stream_readers=6,
        replicas=3,
    )

    report = asyncio.run(qualify_projection(projection, config, hardware={"fixture": True}))

    assert report["passed"] is True
    assert report["target"] == {
        "durableSessions": 12,
        "concurrentStreamReaders": 6,
        "projectionReplicas": 3,
        "sessionGuardProbes": 6,
    }
    assert report["hardware"] == {"fixture": True}
    assert report["integrity"]["zeroMissingSeededResultProjections"] is True
    assert report["integrity"]["zeroDuplicateClaims"] is True
    assert report["integrity"]["zeroCrossTenantEvents"] is True
    assert report["latency"]["streamCursorReads"]["samples"] == 6
    assert projection.maximum_active_readers == 6
    assert projection.reader_replicas == {0, 1, 2}
    exclusions = report["scope"]["excludes"]
    assert any("provider latency" in item for item in exclusions)
    assert any("production high availability" in item for item in exclusions)


def test_integrity_failures_do_not_produce_a_passing_claim() -> None:
    baseline = IntegritySnapshot(
        durable_sessions=8,
        unique_service_session_ids=8,
        terminal_results=8,
        matched_results=8,
        agent_events=8,
        duplicate_service_session_ids=0,
        duplicate_event_keys=0,
        cross_tenant_rows=0,
    )
    projection = FakeProjection(
        integrity=replace(
            baseline,
            terminal_results=7,
            matched_results=7,
            cross_tenant_rows=1,
        ),
        guard_claims=2,
    )

    report = asyncio.run(
        qualify_projection(
            projection,
            QualificationConfig(
                durable_sessions=8,
                concurrent_stream_readers=4,
                replicas=3,
            ),
            hardware={"fixture": True},
        )
    )

    assert report["passed"] is False
    assert report["integrity"]["missingSeededResultProjections"] == 1
    assert report["integrity"]["duplicateClaims"] == 4
    assert report["integrity"]["crossTenantEvents"] == 1
    assert report["failures"]


@pytest.mark.skipif(
    _TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL qualification tests",
)
def test_live_postgres_projection_passes_the_small_reference_workload() -> None:
    if _TEST_DATABASE_URL is None:
        raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

    report = asyncio.run(
        qualify_postgres_session_service(
            _TEST_DATABASE_URL,
            QualificationConfig(
                durable_sessions=12,
                concurrent_stream_readers=6,
                replicas=3,
            ),
        )
    )

    assert report["passed"] is True
    assert report["integrity"]["durableSessionsObserved"] == 12
    assert report["integrity"]["missingSeededResultProjections"] == 0
    assert report["integrity"]["duplicateClaims"] == 0
    assert report["integrity"]["crossTenantEvents"] == 0


def _reference(index: int) -> SessionReference:
    service_session_id = uuid5(_TEST_NAMESPACE, f"service-session:{index}")
    return SessionReference(
        ordinal=index,
        tenant_id="default" if index % 2 == 0 else "qualification-shadow",
        other_tenant_id="qualification-shadow" if index % 2 == 0 else "default",
        service_session_id=service_session_id,
        execution_id=uuid5(_TEST_NAMESPACE, f"execution:{index}"),
        task_run_id=uuid5(_TEST_NAMESPACE, f"task-run:{index}"),
        attempt=1,
        expected_result_digest=f"sha256:{index:064x}",
    )
