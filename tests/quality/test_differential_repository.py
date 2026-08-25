from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.quality.differential import DifferentialSpec, RunObservation
from amesh.quality.durable import DurableDifferentialService
from amesh.quality.repository import (
    DifferentialRunRecord,
    DifferentialState,
    PostgresDifferentialShadowRepository,
    _request_hash,
)

ROOT = Path(__file__).resolve().parents[2]
TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")


def _spec() -> DifferentialSpec:
    return DifferentialSpec(
        tenantId="tenant-a",
        namespace="quality",
        left={"key": "flow", "revision": 1, "digest": "sha256:" + "1" * 64},
        right={"key": "flow", "revision": 2, "digest": "sha256:" + "2" * 64},
        inputs={"value": 1},
        idempotencyKey="request-1",
    )


def test_migration_creates_rls_command_event_and_outbox_contract() -> None:
    migration = (ROOT / "migrations" / "0065_differential_shadow.sql").read_text()
    for table in ("differential_specs", "differential_runs", "differential_events"):
        assert f"CREATE TABLE {table}" in migration
        assert f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY" in migration
        assert f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY" in migration
        assert f"CREATE POLICY tenant_runtime_isolation ON {table}" in migration
    assert "commands_inbox" not in migration
    assert "left_run_id uuid NULL" in migration
    assert "right_run_id uuid NULL" in migration
    assert "CREATE FUNCTION amesh_enqueue_differential_event" in migration
    assert "'differential-shadow'" in migration


def test_idempotency_hash_excludes_generated_spec_identity() -> None:
    first = _spec()
    second = first.model_copy(update={"spec_id": uuid4()})
    assert first.spec_id != second.spec_id
    assert _request_hash(first) == _request_hash(second)


@pytest.mark.anyio
async def test_repository_rejects_mutated_frozen_inputs_before_database() -> None:
    spec = _spec()
    spec.inputs["value"] = 2
    with pytest.raises(ValueError, match="frozen inputs changed"):
        await PostgresDifferentialShadowRepository(None).create_or_get(spec, actor_id="operator")


def test_run_record_preserves_independent_lineage() -> None:
    spec = _spec()
    run = DifferentialRunRecord(
        runId=uuid4(),
        tenantId=spec.tenant_id,
        specId=spec.spec_id,
        side="left",
        configurationDigest=spec.left.digest,
        inputDigest=spec.input_digest,
        state=DifferentialState.SUCCEEDED,
        attempt=1,
        observation={"output": {"ok": True}},
        createdAt="2026-08-25T00:00:00Z",
        updatedAt="2026-08-25T00:00:01Z",
        completedAt="2026-08-25T00:00:01Z",
    )
    assert run.shadow_run().lineage.side == "left"
    assert run.shadow_run().lineage.configuration_digest == spec.left.digest


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
@pytest.mark.anyio
async def test_postgres_shadow_run_is_durable_idempotent_and_tenant_isolated() -> None:
    assert TEST_DATABASE_URL is not None
    database = await create_ephemeral_database(TEST_DATABASE_URL)
    engine = create_async_engine(database.database_url)
    try:
        await apply_migrations(database.database_url, migration_directory())
        repository = PostgresDifferentialShadowRepository(engine)
        spec = _spec().model_copy(update={"tenant_id": "default", "idempotency_key": "repo-e2e"})
        created = await repository.create_or_get(spec, actor_id="quality-test")
        duplicate = await repository.create_or_get(spec, actor_id="quality-test")
        assert duplicate.spec == created.spec

        left = await repository.claim_side("default", spec.spec_id, "left")
        right = await repository.claim_side("default", spec.spec_id, "right")
        from amesh.quality.differential import RunObservation, compare_runs

        left = await repository.record_observation(
            "default", left.run_id, RunObservation(output={"value": 1})
        )
        right = await repository.record_observation(
            "default", right.run_id, RunObservation(output={"value": 1})
        )
        report = compare_runs(spec, left.shadow_run(), right.shadow_run())
        completed = await repository.complete("default", spec.spec_id, report)
        assert completed.report == report
        assert (
            await repository.get("default", spec.namespace, spec.idempotency_key)
        ).report == report
        assert len(await repository.events("default", spec.spec_id)) >= 5

        restarted = PostgresDifferentialShadowRepository(engine)
        assert (
            await restarted.claim_side("default", spec.spec_id, "left")
        ).state.value == "SUCCEEDED"
        with pytest.raises(LookupError):
            await restarted.get("amesh-system", spec.namespace, spec.idempotency_key)
        with pytest.raises(ValueError, match="frozen inputs changed"):
            mutated = spec.model_copy(deep=True)
            mutated.inputs["value"] = 2
            await restarted.create_or_get(mutated, actor_id="quality-test")
    finally:
        await engine.dispose()
        await drop_ephemeral_database(TEST_DATABASE_URL, database.name)


@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
@pytest.mark.anyio
async def test_durable_service_reuses_report_after_restart_without_reexecution() -> None:
    assert TEST_DATABASE_URL is not None
    database = await create_ephemeral_database(TEST_DATABASE_URL)
    engine = create_async_engine(database.database_url)
    try:
        await apply_migrations(database.database_url, migration_directory())
        spec = _spec().model_copy(update={"tenant_id": "default", "idempotency_key": "service-e2e"})
        calls: list[int] = []

        def execute(configuration: object, inputs: object, context: object) -> RunObservation:
            del configuration, context
            calls.append(1)
            return RunObservation(output=inputs)

        service = DurableDifferentialService(PostgresDifferentialShadowRepository(engine))
        first = await service.run(spec, execute, actor_id="quality-test")
        restarted = DurableDifferentialService(PostgresDifferentialShadowRepository(engine))
        second = await restarted.run(spec, execute, actor_id="quality-test")

        assert first == second
        assert len(calls) == 2
        assert await restarted.get("default", "quality", "service-e2e") == first
    finally:
        await engine.dispose()
        await drop_ephemeral_database(TEST_DATABASE_URL, database.name)
