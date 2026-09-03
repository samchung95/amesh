from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).parents[3]
POSTGRES_ROOT = ROOT / "src" / "amesh" / "adapters" / "postgres"
QUALITY_REPOSITORY = ROOT / "src" / "amesh" / "quality" / "repository.py"
SUPPORT_MODULES = {"repository_support.py", "tenant_context.py"}


def _repository_sources() -> tuple[Path, ...]:
    return (*sorted(POSTGRES_ROOT.glob("*.py")), QUALITY_REPOSITORY)


def test_postgres_repositories_use_shared_transaction_authority() -> None:
    violations: list[str] = []
    for path in _repository_sources():
        if path.name in SUPPORT_MODULES:
            continue
        source = path.read_text(encoding="utf-8")
        if re.search(r"tenant_(?:admin_)?transaction\(self\._engine", source):
            violations.append(str(path.relative_to(ROOT)))

    assert violations == []


def test_postgres_audit_writes_have_one_implementation() -> None:
    violations: list[str] = []
    for path in _repository_sources():
        if path.name == "repository_support.py":
            continue
        source = path.read_text(encoding="utf-8")
        if re.search(r"INSERT\s+INTO\s+audit_events", source, re.IGNORECASE):
            violations.append(str(path.relative_to(ROOT)))

    assert violations == []


def test_postgres_repositories_raise_the_shared_not_found_error() -> None:
    violations: list[str] = []
    for path in _repository_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            if isinstance(node.exc.func, ast.Name) and node.exc.func.id == "LookupError":
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}")

    assert violations == []


def test_postgres_tenant_resolution_sql_is_centralized() -> None:
    violations: list[str] = []
    for path in _repository_sources():
        if path.name == "tenant_context.py":
            continue
        source = path.read_text(encoding="utf-8")
        if "amesh_resolve_active_tenant" in source:
            violations.append(str(path.relative_to(ROOT)))

    assert violations == []


def test_engine_owned_postgres_classes_inherit_repository_base() -> None:
    violations: list[str] = []
    for path in _repository_sources():
        if path.name == "repository_support.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not node.name.startswith("Postgres"):
                continue
            constructor = next(
                (
                    member
                    for member in node.body
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and member.name == "__init__"
                ),
                None,
            )
            if constructor is None:
                continue
            parameter_names = {
                argument.arg
                for argument in (
                    *constructor.args.posonlyargs,
                    *constructor.args.args,
                    *constructor.args.kwonlyargs,
                )
            }
            if "engine" not in parameter_names:
                continue
            base_names = {base.id for base in node.bases if isinstance(base, ast.Name)}
            if "PostgresRepositoryBase" not in base_names:
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}:{node.name}")

    assert violations == []
