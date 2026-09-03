from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

FORBIDDEN_APPLICATION_DATABASE_PATTERNS = (
    re.compile(r"create_async_engine\(\s*_?TEST_DATABASE_URL\b"),
    re.compile(r"asyncpg\.connect\(\s*_?TEST_DATABASE_URL\b"),
    re.compile(r"database_url\s*=\s*_?TEST_DATABASE_URL\b"),
)

POSTGRES_LIFECYCLE_EXCEPTIONS = {
    (
        "tests/adapters/postgres/test_migration_contract.py::"
        "test_fresh_databases_are_repeatable_and_migrations_are_idempotent"
    ): "requires two fresh databases and verifies migration reapplication",
    (
        "tests/adapters/postgres/test_upgrade_repository.py::"
        "test_current_binary_requires_admin_grants_before_upgrade_repository_work"
    ): "verifies upgrades across historical schema boundaries",
    (
        "tests/adapters/postgres/test_agent_session_repository.py::"
        "test_progress_state_backfills_from_0078_and_enforces_tenant_event_ownership"
    ): "seeds schema version 0078 before applying the 0079 backfill",
}
POSTGRES_LIFECYCLE_CALLS = {
    "apply_migrations",
    "create_ephemeral_database",
    "drop_ephemeral_database",
}
POSTGRES_LIFECYCLE_EXCEPTION_CALLS = {
    (
        "tests/adapters/postgres/test_migration_contract.py::"
        "test_fresh_databases_are_repeatable_and_migrations_are_idempotent"
    ): Counter(
        {
            "apply_migrations": 3,
            "create_ephemeral_database": 2,
            "drop_ephemeral_database": 2,
        }
    ),
    (
        "tests/adapters/postgres/test_upgrade_repository.py::"
        "test_current_binary_requires_admin_grants_before_upgrade_repository_work"
    ): Counter(
        {
            "apply_migrations": 3,
            "create_ephemeral_database": 1,
            "drop_ephemeral_database": 1,
        }
    ),
    (
        "tests/adapters/postgres/test_agent_session_repository.py::"
        "test_progress_state_backfills_from_0078_and_enforces_tenant_event_ownership"
    ): Counter(
        {
            "apply_migrations": 2,
            "create_ephemeral_database": 1,
            "drop_ephemeral_database": 1,
        }
    ),
}


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = _dotted_name(node.value)
        if owner is not None:
            return f"{owner}.{node.attr}"
    return None


def _lifecycle_bindings(tree: ast.AST) -> tuple[dict[str, str], set[str]]:
    symbols: dict[str, str] = {}
    module_aliases = {"amesh.migrations"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "amesh.migrations" and alias.asname:
                    module_aliases.add(alias.asname)
        elif isinstance(node, ast.ImportFrom) and node.module == "amesh.migrations":
            for alias in node.names:
                if alias.name in POSTGRES_LIFECYCLE_CALLS:
                    symbols[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module == "amesh":
            for alias in node.names:
                if alias.name == "migrations":
                    module_aliases.add(alias.asname or alias.name)

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            value: ast.AST | None = None
            targets: list[ast.Name] = []
            if isinstance(node, ast.Assign):
                value = node.value
                targets = [target for target in node.targets if isinstance(target, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                value = node.value
                targets = [node.target]
            if value is None:
                continue
            if _dotted_name(value) in module_aliases:
                for target in targets:
                    if target.id not in module_aliases:
                        module_aliases.add(target.id)
                        changed = True
                continue
            symbol = _lifecycle_reference(value, symbols, module_aliases)
            if symbol is None:
                continue
            for target in targets:
                if symbols.get(target.id) != symbol:
                    symbols[target.id] = symbol
                    changed = True
    return symbols, module_aliases


def _lifecycle_reference(
    node: ast.AST,
    symbols: dict[str, str],
    module_aliases: set[str],
) -> str | None:
    if isinstance(node, ast.Name):
        return symbols.get(node.id)
    if isinstance(node, ast.Attribute) and node.attr in POSTGRES_LIFECYCLE_CALLS:
        owner = _dotted_name(node.value)
        if owner in module_aliases:
            return node.attr
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "getattr"
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Constant)
        and isinstance(node.args[1].value, str)
        and node.args[1].value in POSTGRES_LIFECYCLE_CALLS
        and _dotted_name(node.args[0]) in module_aliases
    ):
        return node.args[1].value
    return None


def _resolved_lifecycle_calls(tree: ast.AST) -> tuple[tuple[ast.Call, str], ...]:
    symbols, module_aliases = _lifecycle_bindings(tree)
    return tuple(
        (call, symbol)
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call))
        if (symbol := _lifecycle_reference(call.func, symbols, module_aliases)) is not None
    )


def _enclosing_test_name(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
) -> str | None:
    test_name: str | None = None
    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.AsyncFunctionDef, ast.FunctionDef)) and current.name.startswith(
            "test_"
        ):
            test_name = current.name
    return test_name


def test_configured_postgres_url_is_only_used_as_an_admin_anchor() -> None:
    tests_root = Path(__file__).parents[2]
    violations: list[str] = []

    for test_path in sorted(tests_root.rglob("*.py")):
        source = test_path.read_text(encoding="utf-8")
        if any(pattern.search(source) for pattern in FORBIDDEN_APPLICATION_DATABASE_PATTERNS):
            violations.append(test_path.relative_to(tests_root).as_posix())

    assert not violations, (
        "Tests must create application engines from an isolated child database: "
        + ", ".join(violations)
    )


def test_postgres_lifecycle_is_centralized_with_exact_migration_exceptions() -> None:
    repository_root = Path(__file__).parents[3]
    tests_root = repository_root / "tests"
    violations: list[str] = []
    observed_exceptions: dict[str, Counter[str]] = {}

    assert set(POSTGRES_LIFECYCLE_EXCEPTIONS) == set(POSTGRES_LIFECYCLE_EXCEPTION_CALLS)

    for test_path in sorted(tests_root.rglob("*.py")):
        relative_path = test_path.relative_to(repository_root).as_posix()
        if relative_path == "tests/conftest.py":
            continue
        tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))
        parents = {
            child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)
        }
        for call, symbol in _resolved_lifecycle_calls(tree):
            test_name = _enclosing_test_name(call, parents)
            node_id = f"{relative_path}::{test_name or '<module>'}"
            if node_id in POSTGRES_LIFECYCLE_EXCEPTIONS:
                observed_exceptions.setdefault(node_id, Counter())[symbol] += 1
                continue
            violations.append(f"{node_id}:{call.lineno}: {symbol}")

    assert not violations, (
        "PostgreSQL lifecycle must use tests/conftest.py shared fixtures; "
        "unexpected direct calls: " + ", ".join(violations)
    )
    assert observed_exceptions == POSTGRES_LIFECYCLE_EXCEPTION_CALLS, (
        f"PostgreSQL lifecycle exception registry is stale; observed {observed_exceptions!r}"
    )


def test_postgres_lifecycle_resolution_handles_aliases_without_method_name_false_positives() -> (
    None
):
    tree = ast.parse(
        "\n".join(
            (
                "from amesh.migrations import apply_migrations as migrate",
                "import amesh.migrations as migration_api",
                'provision = getattr(migration_api, "create_ephemeral_database")',
                "migration_alias = migration_api",
                "migrate('database')",
                "provision('database')",
                "migration_alias.drop_ephemeral_database('database')",
                "unrelated.apply_migrations()",
            )
        )
    )

    assert Counter(symbol for _call, symbol in _resolved_lifecycle_calls(tree)) == Counter(
        {
            "apply_migrations": 1,
            "create_ephemeral_database": 1,
            "drop_ephemeral_database": 1,
        }
    )


@pytest.mark.anyio
async def test_shared_postgres_engine_uses_a_migrated_disposable_database(
    postgres_async_engine: AsyncEngine,
) -> None:
    async with postgres_async_engine.connect() as connection:
        database_name = await connection.scalar(text("SELECT current_database()"))
        migration_count = await connection.scalar(
            text("SELECT count(*) FROM amesh_schema_migrations")
        )

    assert isinstance(database_name, str)
    assert re.fullmatch(r"amesh_test_[a-f0-9]{16}", database_name)
    assert isinstance(migration_count, int)
    assert migration_count > 0
