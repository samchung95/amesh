import json
from datetime import UTC, datetime

from amesh.cli import EXIT_SUCCESS, main
from amesh.compatibility.kestra import MigrationBundle, MigrationRecord, MigrationResourceKind

from .test_kestra_flow_import import FIXTURE


def test_flow_validate_migrate_and_manifest_have_machine_output(tmp_path, capsys) -> None:
    target = tmp_path / "amesh-flow.yaml"

    assert main(["kestra", "flow", "validate", str(FIXTURE)]) == EXIT_SUCCESS
    validation = json.loads(capsys.readouterr().out)
    assert validation["valid"] is True

    assert (
        main(
            [
                "kestra",
                "flow",
                "migrate",
                str(FIXTURE),
                "--output-path",
                str(target),
            ]
        )
        == EXIT_SUCCESS
    )
    migration = json.loads(capsys.readouterr().out)
    assert migration["outputPath"] == str(target)
    assert "type: core.log" in target.read_text(encoding="utf-8")

    assert main(["kestra", "compatibility", "manifest"]) == EXIT_SUCCESS
    manifest = json.loads(capsys.readouterr().out)
    assert manifest["releaseClaimAllowed"] is False
    cli = next(item for item in manifest["surfaces"] if item["name"] == "cli")
    assert len(cli["commands"]) == 5
    assert all({"flags", "exitCodes", "machineOutput"} <= set(item) for item in cli["commands"])


def test_migration_plan_and_import_are_resumable_cli_commands(tmp_path, capsys) -> None:
    record = MigrationRecord.create(
        kind=MigrationResourceKind.FLOW,
        source_id="flow-1",
        tenant="tenant-a",
        payload={"id": "flow-1"},
        source_fingerprint="kestra-export-sha256",
    )
    bundle = MigrationBundle.create(
        source_fingerprint="kestra-export-sha256",
        records=(record,),
        created_at=datetime(2026, 8, 23, 8, tzinfo=UTC),
    )
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(bundle.model_dump_json(by_alias=True), encoding="utf-8")
    target = tmp_path / "target"

    assert main(["kestra", "migration", "plan", str(bundle_path)]) == EXIT_SUCCESS
    plan = json.loads(capsys.readouterr().out)
    assert plan["dryRun"] is True
    assert plan["cutoverAllowed"] is True

    assert (
        main(
            [
                "kestra",
                "migration",
                "import",
                str(bundle_path),
                "--target-dir",
                str(target),
                "--max-records",
                "1",
            ]
        )
        == EXIT_SUCCESS
    )
    imported = json.loads(capsys.readouterr().out)
    assert imported["complete"] is True
    assert imported["imported"] == 1
    assert imported["reconciliation"] == []
