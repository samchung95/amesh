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
