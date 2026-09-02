from datetime import UTC, datetime, timedelta

import pytest

from amesh.compatibility.kestra import (
    FileMigrationStore,
    MigrationBundle,
    MigrationCheckpoint,
    MigrationImporter,
    MigrationRecord,
    MigrationResourceKind,
    SecretReference,
    plan_migration,
)


def _record(
    kind: MigrationResourceKind,
    source_id: str,
    *,
    occurred_at: datetime | None = None,
    references: tuple[str, ...] = (),
    payload: dict[str, object] | None = None,
    secrets: tuple[SecretReference, ...] = (),
) -> MigrationRecord:
    return MigrationRecord.create(
        kind=kind,
        source_id=source_id,
        tenant="tenant-a",
        namespace="company.team",
        occurred_at=occurred_at,
        references=references,
        payload=payload or {"source": source_id},
        secret_references=secrets,
        source_fingerprint="kestra-export-sha256",
    )


def test_every_declared_bundle_kind_round_trips_with_stable_identifiers() -> None:
    now = datetime(2026, 8, 23, 8, tzinfo=UTC)
    execution_id = "execution-1"
    records = []
    history_index = 0
    for kind in MigrationResourceKind:
        source_id = execution_id if kind is MigrationResourceKind.EXECUTION else f"{kind.value}-1"
        occurred_at = None
        references: tuple[str, ...] = ()
        if kind in {
            MigrationResourceKind.STATE_EVENT,
            MigrationResourceKind.LOG,
            MigrationResourceKind.AUDIT_EVENT,
        }:
            occurred_at = now + timedelta(seconds=history_index)
            references = (execution_id,)
            history_index += 1
        records.append(_record(kind, source_id, occurred_at=occurred_at, references=references))

    bundle = MigrationBundle.create(
        source_fingerprint="kestra-export-sha256",
        records=records,
        created_at=now,
    )
    restored = MigrationBundle.model_validate_json(bundle.model_dump_json(by_alias=True))

    restored.verify()
    assert {record.kind for record in restored.records} == set(MigrationResourceKind)
    assert [record.payload for record in restored.records] == [record.payload for record in records]
    assert [item.target_id for item in restored.identifier_map] == [
        item.target_id for item in records
    ]
    assert (
        _record(MigrationResourceKind.FLOW, "flow-1").target_id
        == _record(MigrationResourceKind.FLOW, "flow-1").target_id
    )
    assert plan_migration(restored).cutover_allowed is True


def test_plan_blocks_plaintext_unresolved_secrets_and_reversed_history() -> None:
    now = datetime(2026, 8, 23, 8, tzinfo=UTC)
    execution = _record(MigrationResourceKind.EXECUTION, "execution-1")
    plaintext = _record(
        MigrationResourceKind.SYSTEM_CONFIGURATION,
        "configuration-1",
        payload={"apiToken": "not-a-reference"},
        secrets=(SecretReference(provider="vault", key="api", binding="vault/api"),),
    )
    later = _record(
        MigrationResourceKind.STATE_EVENT,
        "state-2",
        occurred_at=now + timedelta(minutes=1),
        references=(execution.source_id,),
    )
    earlier = _record(
        MigrationResourceKind.STATE_EVENT,
        "state-1",
        occurred_at=now,
        references=(execution.source_id,),
    )
    bundle = MigrationBundle.create(
        source_fingerprint="kestra-export-sha256",
        records=(execution, plaintext, later, earlier),
        created_at=now,
    )

    plan = plan_migration(bundle)

    assert plan.cutover_allowed is False
    assert {issue.code for issue in plan.issues} == {
        "SECRET_PLAINTEXT",
        "SECRET_BINDING_UNRESOLVED",
        "CHRONOLOGY_REVERSED",
    }


def test_import_is_bounded_resumable_idempotent_and_reconciled(tmp_path) -> None:
    records = (
        _record(MigrationResourceKind.FLOW, "flow-1"),
        _record(MigrationResourceKind.NAMESPACE_FILE, "file-1"),
    )
    bundle = MigrationBundle.create(
        source_fingerprint="kestra-export-sha256",
        records=records,
        created_at=datetime(2026, 8, 23, 8, tzinfo=UTC),
    )
    store = FileMigrationStore(tmp_path)
    importer = MigrationImporter(store)

    first = importer.import_bundle(bundle, max_records=1)
    second = importer.import_bundle(bundle)

    assert first.imported == 1 and first.complete is False
    assert second.imported == 1 and second.complete is True
    assert importer.reconcile(bundle) == ()

    store.write_checkpoint(MigrationCheckpoint(bundleChecksum=bundle.checksum_sha256))
    replay = importer.import_bundle(bundle)
    assert replay.imported == 0
    assert replay.skipped == 2
    assert replay.complete is True

    with pytest.raises(ValueError, match="positive integer"):
        importer.import_bundle(bundle, max_records=0)


def test_identifier_map_drift_blocks_cutover() -> None:
    record = _record(MigrationResourceKind.FLOW, "flow-1")
    bundle = MigrationBundle.create(
        source_fingerprint="kestra-export-sha256",
        records=(record,),
        created_at=datetime(2026, 8, 23, 8, tzinfo=UTC),
    ).model_copy(update={"identifier_map": ()})

    plan = plan_migration(bundle)

    assert plan.cutover_allowed is False
    assert "IDENTIFIER_MAP_MISMATCH" in {issue.code for issue in plan.issues}
