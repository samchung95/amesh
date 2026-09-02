from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_http_policy_legacy_surface_uses_networking_boundary() -> None:
    from amesh import networking
    from amesh.tasks import http

    assert http.HttpTaskPolicy is networking.HttpTaskPolicy
    assert http.validate_http_destination is networking.validate_http_destination


def test_dsl_descriptor_surfaces_preserve_symbol_identity() -> None:
    from amesh.dsl import descriptors, registry
    from amesh.dsl.specifications import common

    assert registry.EditorMetadata is descriptors.EditorMetadata
    assert registry.ResourceKind is descriptors.ResourceKind
    assert registry.ResourceSchemaDescriptor is descriptors.ResourceSchemaDescriptor
    assert common.TaskSpecification is descriptors.TaskSpecification


def test_migration_surfaces_preserve_symbol_identity() -> None:
    from amesh import migration_planning, migrations
    from amesh.entrypoints import migrations as canonical

    assert migrations is canonical
    assert migrations.MigrationDescriptor is migration_planning.MigrationDescriptor
    assert migrations.migration_body is migration_planning.migration_body
    assert migrations.migration_plan is migration_planning.migration_plan


def test_canonical_migration_entrypoint_finds_repository_manifest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from amesh.entrypoints.migrations import migration_directory

    monkeypatch.delenv("AMESH_MIGRATIONS_PATH", raising=False)
    expected = Path(__file__).resolve().parents[1] / "migrations"

    assert migration_directory() == expected
    assert (migration_directory() / "manifest.json").is_file()


def test_authorization_surface_preserves_credential_scope_identity() -> None:
    from amesh.domain import authorization, credentials

    assert credentials.credential_scope_allows is authorization.credential_scope_allows


def test_dsl_validator_is_loaded_only_when_lazy_surface_is_used() -> None:
    script = "\n".join(
        (
            "import sys",
            "import amesh.dsl as dsl",
            "assert 'amesh.dsl.validator' not in sys.modules",
            "validator = dsl.validate_flow_document",
            "assert 'amesh.dsl.validator' in sys.modules",
            "assert validator.__module__ == 'amesh.dsl.validator'",
        )
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("COV_CORE_", "COVERAGE_"))
        },
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
