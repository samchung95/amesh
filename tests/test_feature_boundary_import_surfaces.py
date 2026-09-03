from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

_FEATURE_PACKAGES = ("identity", "lifecycle", "platform")
_LEGACY_FEATURE_MODULES = {
    "amesh.backfills",
    "amesh.credentials",
    "amesh.dashboards",
    "amesh.flow_testing",
    "amesh.tenancy",
}


def _imported_names(
    path: Path,
    node: ast.Import | ast.ImportFrom,
    source_root: Path,
) -> tuple[str, ...]:
    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if node.level == 0:
        module_name = node.module or ""
    else:
        package_parts = ["amesh", *path.relative_to(source_root).parent.parts]
        retained = package_parts[: len(package_parts) - node.level + 1]
        if node.module:
            retained.extend(node.module.split("."))
        module_name = ".".join(retained)
    names = [module_name] if module_name else []
    if not node.module or module_name == "amesh":
        names.extend(f"{module_name}.{alias.name}" for alias in node.names if module_name)
    return tuple(names)


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


def test_canonical_feature_packages_preserve_legacy_symbol_identity() -> None:
    from amesh import (
        backfills,
        credentials,
        dashboards,
        flow_testing,
        identity,
        lifecycle,
        platform,
        tenancy,
    )

    assert credentials.CredentialService is identity.CredentialService
    assert credentials.InvalidCredential is identity.InvalidCredential
    assert tenancy.TenantService is identity.TenantService
    assert backfills.BackfillService is lifecycle.BackfillService
    assert flow_testing.FlowTestService is platform.FlowTestService
    assert flow_testing.FlowTestSimulator is platform.FlowTestSimulator
    assert dashboards.builtin_dashboards is platform.builtin_dashboards


def test_feature_packages_do_not_import_outer_runtime_layers() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src" / "amesh"
    forbidden = ("amesh.adapters", "amesh.api", "amesh.entrypoints")

    violations: list[str] = []
    for package_name in _FEATURE_PACKAGES:
        for path in sorted((source_root / package_name).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                for name in _imported_names(path, node, source_root):
                    if any(name == root or name.startswith(f"{root}.") for root in forbidden):
                        violations.append(f"{path.relative_to(source_root)}:{node.lineno}: {name}")

    assert violations == []


def test_production_consumers_use_canonical_feature_packages() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src" / "amesh"
    compatibility_modules = {
        source_root / f"{name.rsplit('.', 1)[-1]}.py" for name in _LEGACY_FEATURE_MODULES
    }
    violations: list[str] = []

    for path in sorted(source_root.rglob("*.py")):
        if path in compatibility_modules:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            for name in _imported_names(path, node, source_root):
                if name in _LEGACY_FEATURE_MODULES:
                    violations.append(f"{path.relative_to(source_root)}:{node.lineno}: {name}")

    assert violations == []


def test_import_resolution_covers_relative_and_package_level_imports() -> None:
    source_root = Path("repository") / "src" / "amesh"
    path = source_root / "identity" / "sample.py"
    tree = ast.parse("from .. import api\nfrom amesh import credentials\n")
    names = {
        name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for name in _imported_names(path, node, source_root)
    }

    assert "amesh.api" in names
    assert "amesh.credentials" in names


def test_test_filenames_describe_behavior_instead_of_delivery_epics() -> None:
    tests_root = Path(__file__).resolve().parent

    assert not tuple(tests_root.rglob("test_*epic[0-9]*.py"))


def test_dsl_validator_is_loaded_only_when_lazy_surface_is_used() -> None:
    script = "\n".join(
        (
            "import sys",
            "import amesh.dsl as dsl",
            "assert 'amesh.dsl.validator' not in sys.modules",
            "validator_module = dsl.validator",
            "assert 'amesh.dsl.validator' in sys.modules",
            "assert validator_module is sys.modules['amesh.dsl.validator']",
            "validator = dsl.validate_flow_document",
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
