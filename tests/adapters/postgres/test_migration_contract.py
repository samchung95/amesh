from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from amesh.migration_planning import (
    DestructiveMigration,
    destructive_migration_backup_warning,
    destructive_migration_manifest,
    validate_destructive_migration_backup,
)
from amesh.migrations import migration_body, migration_plan

ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS = ROOT / "migrations"
_OBVIOUS_DESTRUCTIVE_SQL = re.compile(
    r"\b(?:DELETE\s+FROM|TRUNCATE(?:\s+TABLE)?|DROP\s+TABLE|DROP\s+COLUMN)\b",
    re.IGNORECASE,
)
_NOW = datetime(2026, 9, 27, 9, 0, tzinfo=UTC)
_DESTRUCTIVE = (
    DestructiveMigration("0034_flow_revision_event_retention.sql", "Deletes queued outbox rows"),
)


def _strip_sql_comments(sql: str) -> str:
    without_blocks = re.sub(
        r"/\*.*?\*/",
        lambda match: "\n" * match.group(0).count("\n"),
        sql,
        flags=re.DOTALL,
    )
    return re.sub(r"--.*", "", without_blocks)


def _marker(delta: timedelta) -> str:
    return (_NOW + delta).isoformat().replace("+00:00", "Z")


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
            (19, "admission_control"),
            (20, "backfills"),
            (21, "runnable_task_contract"),
            (22, "postgresql_operations"),
            (23, "distributed_queue_profile"),
            (24, "reconciliation_runs"),
            (25, "service_registry"),
            (26, "disaster_recovery"),
            (27, "interactive_authentication"),
            (28, "execution_evidence"),
            (29, "task_cache"),
            (30, "trigger_occurrence_runtime"),
            (31, "execution_checks"),
            (32, "configuration_feature_flags"),
            (33, "flow_revisions"),
            (34, "flow_revision_event_retention"),
            (35, "conditional_task_control"),
            (36, "execution_lifecycle_hooks"),
            (37, "execution_data_contracts"),
            (38, "workflow_metadata"),
            (39, "namespace_shared_resources"),
            (40, "execution_file_lineage"),
            (41, "realtime_webhook_subscriptions"),
            (42, "execution_debug_evidence"),
            (43, "dashboards"),
            (44, "search_projection"),
            (45, "identity_federation"),
            (46, "audit_evidence_ledger"),
            (47, "plugin_governance"),
            (48, "asset_catalog_lineage"),
            (49, "workflow_apps_human_tasks"),
            (50, "operational_controls"),
            (51, "flow_tests_quality_gates"),
            (52, "search_projection_backend"),
            (53, "observability_trace_context"),
            (54, "retention_lifecycle"),
            (55, "admission_policy"),
            (56, "agent_primitives"),
            (57, "agent_resources"),
            (58, "agent_sessions"),
            (59, "agent_memory"),
            (60, "service_role_health"),
            (61, "canonical_evidence_bundles"),
            (62, "tool_provider_invocations"),
            (63, "protected_model_continuations"),
            (64, "promotion_release_gates"),
            (65, "differential_shadow"),
            (66, "evidence_event_kinds"),
            (67, "protected_trigger_payloads"),
            (68, "agent_session_harness_pins"),
            (69, "agent_session_administration"),
            (70, "agent_session_policies"),
            (71, "transfer_imports"),
            (72, "agent_session_progress"),
            (73, "agent_invocation_accounting"),
            (74, "agent_session_policy_ceiling_mode"),
            (75, "restricted_repository_roles"),
            (76, "authorization_binding_lock_grant"),
            (77, "restricted_operations_role"),
            (78, "projection_rebuild_execution_scope"),
            (79, "agent_progress_incremental_state"),
            (80, "flow_test_tenant_runtime_grants"),
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


def test_destructive_manifest_covers_obvious_destructive_sql_and_existing_files() -> None:
    assert (
        _OBVIOUS_DESTRUCTIVE_SQL.search(_strip_sql_comments("-- DELETE FROM ignored\nSELECT 1"))
        is None
    )
    declared = {item.filename for item in destructive_migration_manifest(MIGRATIONS)}
    obvious = {
        path.name
        for path in MIGRATIONS.glob("*.sql")
        if _OBVIOUS_DESTRUCTIVE_SQL.search(_strip_sql_comments(path.read_text(encoding="utf-8")))
    }

    assert sorted(obvious - declared) == []
    assert all((MIGRATIONS / filename).is_file() for filename in declared)


def test_destructive_pending_on_fresh_database_is_allowed_without_marker() -> None:
    decision = validate_destructive_migration_backup(
        applied_versions=set(),
        pending_migrations=["0034_flow_revision_event_retention.sql"],
        destructive_manifest=_DESTRUCTIVE,
        backup_confirmed_at=None,
        backup_max_age_hours=24,
        now=_NOW,
    )

    assert [item.filename for item in decision.destructive_pending] == [
        "0034_flow_revision_event_retention.sql"
    ]
    assert decision.backup_confirmed_at is None
    assert destructive_migration_backup_warning(decision) is None


def test_destructive_upgrade_without_marker_is_refused() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        validate_destructive_migration_backup(
            applied_versions={"0033_flow_revisions.sql"},
            pending_migrations=["0034_flow_revision_event_retention.sql"],
            destructive_manifest=_DESTRUCTIVE,
            backup_confirmed_at=None,
            backup_max_age_hours=24,
            now=_NOW,
        )

    message = str(exc_info.value)
    assert "0034_flow_revision_event_retention.sql" in message
    assert "MIGRATION_BACKUP_CONFIRMED_AT" in message
    assert "restore" in message


def test_destructive_upgrade_with_stale_marker_is_refused() -> None:
    with pytest.raises(RuntimeError, match="older than 24 hour"):
        validate_destructive_migration_backup(
            applied_versions={"0033_flow_revisions.sql"},
            pending_migrations=["0034_flow_revision_event_retention.sql"],
            destructive_manifest=_DESTRUCTIVE,
            backup_confirmed_at=_marker(timedelta(hours=-25)),
            backup_max_age_hours=24,
            now=_NOW,
        )


@pytest.mark.parametrize("marker", [_marker(timedelta(hours=1)), "not-a-timestamp"])
def test_destructive_upgrade_with_future_or_garbage_marker_is_refused(marker: str) -> None:
    with pytest.raises(RuntimeError):
        validate_destructive_migration_backup(
            applied_versions={"0033_flow_revisions.sql"},
            pending_migrations=["0034_flow_revision_event_retention.sql"],
            destructive_manifest=_DESTRUCTIVE,
            backup_confirmed_at=marker,
            backup_max_age_hours=24,
            now=_NOW,
        )


def test_destructive_upgrade_with_valid_marker_is_allowed_with_warning() -> None:
    decision = validate_destructive_migration_backup(
        applied_versions={"0033_flow_revisions.sql"},
        pending_migrations=["0034_flow_revision_event_retention.sql"],
        destructive_manifest=_DESTRUCTIVE,
        backup_confirmed_at=_marker(timedelta(hours=-2)),
        backup_max_age_hours=24,
        now=_NOW,
    )

    warning = destructive_migration_backup_warning(decision)

    assert decision.backup_confirmed_at == _NOW - timedelta(hours=2)
    assert warning is not None
    assert "destructive forward-only" in warning
    assert "restore the pre-upgrade backup" in warning


def test_no_destructive_pending_is_allowed_without_marker() -> None:
    decision = validate_destructive_migration_backup(
        applied_versions={"0033_flow_revisions.sql"},
        pending_migrations=["0035_conditional_task_control.sql"],
        destructive_manifest=_DESTRUCTIVE,
        backup_confirmed_at=None,
        backup_max_age_hours=24,
        now=_NOW,
    )

    assert decision.destructive_pending == ()
    assert decision.backup_confirmed_at is None


def test_fully_migrated_database_needs_no_backup_marker() -> None:
    applied = {item.filename for item in migration_plan(MIGRATIONS)}

    decision = validate_destructive_migration_backup(
        applied_versions=applied,
        pending_migrations=[],
        destructive_manifest=destructive_migration_manifest(MIGRATIONS),
        backup_confirmed_at=None,
        backup_max_age_hours=24,
        now=_NOW,
    )

    assert len(applied) == 80
    assert decision.destructive_pending == ()
    assert decision.backup_confirmed_at is None
