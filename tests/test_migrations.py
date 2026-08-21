from __future__ import annotations

import json
from pathlib import Path

import pytest

from amesh.migrations import migration_body, migration_plan

ROOT = Path(__file__).resolve().parents[1]


def test_migration_body_removes_outer_transaction() -> None:
    assert migration_body("BEGIN;\nSELECT 1;\nCOMMIT;\n") == "SELECT 1;"


def test_checked_in_migration_manifest_is_complete_and_ordered() -> None:
    plan = migration_plan(ROOT / "migrations")

    assert [item.filename for item in plan] == [
        f"{version:04d}_{name}.sql"
        for version, name in (
            (1, "foundation"),
            (2, "mvp_task_retry"),
            (3, "canonical_resource_metadata"),
            (4, "authorization"),
            (5, "service_credentials"),
            (6, "multi_tenancy"),
            (7, "tenant_queue_notifications"),
            (8, "restricted_tenant_resolution"),
            (9, "tenant_administration_role"),
            (10, "execution_trigger_context"),
            (11, "execution_event_model"),
            (12, "metadata_repository"),
            (13, "transport_dead_letters"),
            (14, "executor_dispatch"),
            (15, "scheduler_state"),
            (16, "worker_protocol"),
            (17, "execution_interventions"),
            (18, "subflow_relationships"),
        )
    ]
    assert all(item.rollback_guidance for item in plan)


def test_migration_manifest_rejects_unlisted_sql(tmp_path: Path) -> None:
    (tmp_path / "0001_first.sql").write_text("BEGIN;\nSELECT 1;\nCOMMIT;\n", encoding="utf-8")
    (tmp_path / "0002_unlisted.sql").write_text("BEGIN;\nSELECT 2;\nCOMMIT;\n", encoding="utf-8")
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "migrations": [
                    {
                        "file": "0001_first.sql",
                        "mode": "bootstrap",
                        "onlineCompatible": False,
                        "rollbackGuidance": "Drop the empty test database.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="manifest order differs"):
        migration_plan(tmp_path)
