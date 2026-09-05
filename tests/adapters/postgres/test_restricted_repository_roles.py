from __future__ import annotations

import ast
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast
from uuid import uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuditRepository,
    PostgresAuthenticationRepository,
    PostgresAuthorizationRepository,
    PostgresCredentialRepository,
    PostgresDurableTransport,
    PostgresExecutionRepository,
    PostgresFederationRepository,
    PostgresOperationsRepository,
    PostgresServiceRegistryRepository,
    PostgresUpgradeRepository,
)
from amesh.adapters.postgres.tenant_context import (
    TenantAdminGrantsUnavailableError,
    tenant_admin_transaction,
    tenant_transaction,
)
from amesh.domain import (
    AdmissionOutcome,
    AdmissionResourceType,
    AuthorizationScopeType,
    ExecutionState,
    NamespaceAuthorizationBoundary,
    PrincipalDefinition,
    PrincipalType,
    RoleBinding,
    new_runtime_id,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.ports import ExecutionInterventionAction, TaskRunState, split_execution_repository

POSTGRES_ADAPTER_DIRECTORY = Path(__file__).resolve().parents[3] / "src/amesh/adapters/postgres"
POSTGRES_PACKAGE = "amesh.adapters.postgres"
TENANT_TRANSACTION = "tenant-transaction"
TENANT_ADMIN_TRANSACTION = "tenant-admin-transaction"
SAFE_TRANSACTION_TARGETS = {
    f"{POSTGRES_PACKAGE}.tenant_context.tenant_transaction": TENANT_TRANSACTION,
    f"{POSTGRES_PACKAGE}.tenant_context.tenant_admin_transaction": TENANT_ADMIN_TRANSACTION,
}
TRANSACTION_MANAGER_TARGET_SUFFIXES = {
    ".transactions.tenant": TENANT_TRANSACTION,
    "._transactions.tenant": TENANT_TRANSACTION,
    ".transaction_manager.tenant": TENANT_TRANSACTION,
    ".transactions.admin": TENANT_ADMIN_TRANSACTION,
    "._transactions.admin": TENANT_ADMIN_TRANSACTION,
    ".transaction_manager.admin": TENANT_ADMIN_TRANSACTION,
}
TransactionEntrypoint = tuple[str, str]

# These are the complete raw paths that predate this gate. Issue #47 owns changing
# their role boundaries; every new raw path must fail this exact classification.
EXPECTED_RAW_TRANSACTION_ROLES: dict[TransactionEntrypoint, str] = {
    (
        "agent_sessions.py",
        "PostgresAgentSessionRepository.session_guard",
    ): "login-role",
    (
        "durable_transport.py",
        "PostgresDurableTransport.wait_for_work",
    ): "amesh_runtime",
    (
        "execution_repository.py",
        "PostgresExecutionRepository.execution_guard",
    ): "login-role",
    (
        "execution_repository.py",
        "PostgresExecutionRepository.database_time",
    ): "login-role",
    (
        "scheduler_repository.py",
        "PostgresSchedulerRepository.database_time",
    ): "login-role",
    (
        "tenant_repository.py",
        "PostgresTenantRepository.list_active_for_worker_group",
    ): "amesh_runtime",
}


def _relative_import_module(current_module: str, imported_module: str | None, level: int) -> str:
    if level == 0:
        return imported_module or ""
    package_parts = current_module.split(".")[:-1]
    base_parts = package_parts[: len(package_parts) - (level - 1)]
    if imported_module:
        base_parts.extend(imported_module.split("."))
    return ".".join(base_parts)


def _module_imports(tree: ast.Module, module_name: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            imported_module = _relative_import_module(module_name, node.module, node.level)
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{imported_module}.{alias.name}"
    return aliases


class _FunctionCollector(ast.NodeVisitor):
    def __init__(self, module_name: str, relative_path: str) -> None:
        self._module_name = module_name
        self._relative_path = relative_path
        self._scope: list[str] = []
        self.functions: dict[
            str, tuple[TransactionEntrypoint, ast.FunctionDef | ast.AsyncFunctionDef]
        ] = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._collect_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._collect_function(node)

    def _collect_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._scope.append(node.name)
        qualified_name = ".".join(self._scope)
        self.functions[f"{self._module_name}.{qualified_name}"] = (
            (self._relative_path, qualified_name),
            node,
        )
        self.generic_visit(node)
        self._scope.pop()


def _attribute_target(expression: ast.expr, aliases: dict[str, str]) -> str | None:
    if isinstance(expression, ast.Name):
        return aliases.get(expression.id, expression.id)
    if not isinstance(expression, ast.Attribute):
        return None
    base = _attribute_target(expression.value, aliases)
    return f"{base}.{expression.attr}" if base else None


def _effective_function_role(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    roles = {
        role
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
        for role in ("amesh_runtime", "amesh_tenant_admin")
        if any(f"{statement} {role}" in child.value for statement in ("SET ROLE", "SET LOCAL ROLE"))
    }
    assert len(roles) <= 1, f"transaction entrypoint selects multiple roles: {sorted(roles)}"
    return next(iter(roles), "login-role")


class _FunctionTransactionVisitor(ast.NodeVisitor):
    def __init__(
        self,
        *,
        aliases: dict[str, str],
        current_module: str,
        class_name: str | None,
        raw_role: str,
    ) -> None:
        self._aliases = aliases.copy()
        self._current_module = current_module
        self._class_name = class_name
        self._raw_category = f"raw:{raw_role}"
        self.direct_categories: set[str] = set()
        self.context_helpers: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        del node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        del node

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        del node

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._aliases[alias.asname or alias.name.split(".")[0]] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        imported_module = _relative_import_module(self._current_module, node.module, node.level)
        for alias in node.names:
            self._aliases[alias.asname or alias.name] = f"{imported_module}.{alias.name}"

    def visit_Assign(self, node: ast.Assign) -> None:
        reference = self._callable_reference(node.value)
        if reference is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._aliases[target.id] = reference
        self.generic_visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is None:
            return
        reference = self._callable_reference(node.value)
        if reference is not None and isinstance(node.target, ast.Name):
            self._aliases[node.target.id] = reference
        self.generic_visit(node.value)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        for item in node.items:
            if not isinstance(item.context_expr, ast.Call):
                continue
            target = self._callable_reference(item.context_expr.func)
            if target is not None and self._category_for_target(target) is None:
                self.context_helpers.add(target)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self._record_returned_helper(node.value)
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> None:
        self._record_returned_helper(node.value)
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self._record_returned_helper(node.value)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        target = self._callable_reference(node.func)
        if target is not None:
            category = self._category_for_target(target)
            if category is not None:
                self.direct_categories.add(category)
        self.generic_visit(node)

    def _callable_reference(self, expression: ast.expr) -> str | None:
        if (
            isinstance(expression, ast.Call)
            and isinstance(expression.func, ast.Name)
            and expression.func.id == "getattr"
            and len(expression.args) >= 2
            and isinstance(expression.args[1], ast.Constant)
            and expression.args[1].value in {"begin", "connect"}
        ):
            return self._raw_category
        if (
            isinstance(expression, ast.Attribute)
            and expression.attr == "__call__"
            and isinstance(expression.value, ast.Attribute)
            and expression.value.attr in {"begin", "connect"}
        ):
            return self._raw_category
        if isinstance(expression, ast.Attribute) and expression.attr in {"begin", "connect"}:
            return self._raw_category
        if isinstance(expression, ast.Name):
            target = self._aliases.get(expression.id)
            if target is not None:
                return target
            return f"{self._current_module}.{expression.id}"
        if isinstance(expression, ast.Attribute):
            if isinstance(expression.value, ast.Name) and expression.value.id in {"self", "cls"}:
                if self._class_name is None:
                    return None
                return f"{self._current_module}.{self._class_name}.{expression.attr}"
            return _attribute_target(expression, self._aliases)
        return None

    def _record_returned_helper(self, expression: ast.expr | None) -> None:
        if not isinstance(expression, ast.Call):
            return
        target = self._callable_reference(expression.func)
        if target is not None and self._category_for_target(target) is None:
            self.context_helpers.add(target)

    def _category_for_target(self, target: str) -> str | None:
        if target.startswith("raw:"):
            return target
        direct_category = SAFE_TRANSACTION_TARGETS.get(target)
        if direct_category is not None:
            return direct_category
        return next(
            (
                category
                for suffix, category in TRANSACTION_MANAGER_TARGET_SUFFIXES.items()
                if target.endswith(suffix)
            ),
            None,
        )


def _discover_transaction_entrypoints(
    adapter_directory: Path,
) -> dict[TransactionEntrypoint, frozenset[str]]:
    functions: dict[
        str,
        tuple[
            TransactionEntrypoint,
            ast.FunctionDef | ast.AsyncFunctionDef,
            dict[str, str],
            str,
        ],
    ] = {}
    module_paths = sorted(adapter_directory.rglob("*.py"))
    assert module_paths, f"no PostgreSQL adapter modules found under {POSTGRES_ADAPTER_DIRECTORY}"
    for module_path in module_paths:
        relative_path = module_path.relative_to(adapter_directory).as_posix()
        module_suffix = relative_path.removesuffix(".py").replace("/", ".")
        module_name = f"{POSTGRES_PACKAGE}.{module_suffix}"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imports = _module_imports(tree, module_name)
        collector = _FunctionCollector(module_name, relative_path)
        collector.visit(tree)
        for function_name, (entrypoint, node) in collector.functions.items():
            functions[function_name] = (entrypoint, node, imports, module_name)

    categories: dict[str, set[str]] = {}
    helper_targets: dict[str, set[str]] = {}
    for function_name, (entrypoint, node, aliases, module_name) in functions.items():
        scope_parts = entrypoint[1].split(".")
        class_name = scope_parts[-2] if len(scope_parts) > 1 else None
        visitor = _FunctionTransactionVisitor(
            aliases=aliases,
            current_module=module_name,
            class_name=class_name,
            raw_role=_effective_function_role(node),
        )
        for statement in node.body:
            visitor.visit(statement)
        if function_name in SAFE_TRANSACTION_TARGETS:
            categories[function_name] = {SAFE_TRANSACTION_TARGETS[function_name]}
        else:
            categories[function_name] = visitor.direct_categories
        helper_targets[function_name] = visitor.context_helpers

    changed = True
    while changed:
        changed = False
        for function_name, targets in helper_targets.items():
            inherited = set().union(
                *(categories[target] for target in targets if target in categories)
            )
            if not inherited <= categories[function_name]:
                categories[function_name].update(inherited)
                changed = True

    return {
        functions[function_name][0]: frozenset(function_categories)
        for function_name, function_categories in categories.items()
        if function_categories
    }


def _raw_transaction_roles(
    entrypoints: dict[TransactionEntrypoint, frozenset[str]],
) -> dict[TransactionEntrypoint, str]:
    result: dict[TransactionEntrypoint, str] = {}
    for entrypoint, categories in entrypoints.items():
        raw_roles = {
            category.removeprefix("raw:") for category in categories if category.startswith("raw:")
        }
        assert len(raw_roles) <= 1, f"{entrypoint} has conflicting raw roles: {sorted(raw_roles)}"
        if raw_roles:
            result[entrypoint] = next(iter(raw_roles))
    return result


def test_all_postgres_transaction_entrypoints_have_role_classifications() -> None:
    entrypoints = _discover_transaction_entrypoints(POSTGRES_ADAPTER_DIRECTORY)

    assert _raw_transaction_roles(entrypoints) == EXPECTED_RAW_TRANSACTION_ROLES
    assert entrypoints[("tenant_context.py", "tenant_transaction")] == frozenset(
        {TENANT_TRANSACTION}
    )
    assert entrypoints[("tenant_context.py", "tenant_admin_transaction")] == frozenset(
        {TENANT_ADMIN_TRANSACTION}
    )
    assert entrypoints[
        ("agent_session_admin.py", "PostgresAgentSessionFleetRepository.instance_aggregate")
    ] == frozenset({TENANT_ADMIN_TRANSACTION})
    for method_name in ("save_revision", "get_revision", "effective_revisions", "list_revisions"):
        assert entrypoints[
            ("agent_session_policy.py", f"PostgresAgentSessionPolicyRepository.{method_name}")
        ] == frozenset({TENANT_TRANSACTION})
    assert {TENANT_TRANSACTION, TENANT_ADMIN_TRANSACTION} <= set().union(*entrypoints.values())


def test_tenant_admin_transaction_fails_before_yield_without_canary_grant() -> None:
    entered = False

    class Connection:
        async def execution_options(self, **_options: object) -> Connection:
            return self

        @asynccontextmanager
        async def begin(self) -> AsyncIterator[None]:
            yield

        async def scalar(self, _statement: object) -> bool:
            return False

        async def execute(self, _statement: object) -> None:
            raise AssertionError("SET LOCAL ROLE must not run without the canary grant")

    class Engine:
        @asynccontextmanager
        async def connect(self) -> AsyncIterator[Connection]:
            yield Connection()

    async def scenario() -> None:
        nonlocal entered
        with pytest.raises(
            TenantAdminGrantsUnavailableError,
            match=r"0075_restricted_repository_roles\.sql",
        ):
            async with tenant_admin_transaction(cast(AsyncEngine, Engine())):
                entered = True

    asyncio.run(scenario())
    assert not entered


def test_tenant_admin_transaction_propagates_role_switch_failure() -> None:
    entered = False

    class RoleSwitchError(RuntimeError):
        pass

    class Connection:
        async def execution_options(self, **_options: object) -> Connection:
            return self

        @asynccontextmanager
        async def begin(self) -> AsyncIterator[None]:
            yield

        async def scalar(self, _statement: object) -> bool:
            return True

        async def execute(self, statement: object) -> None:
            assert str(statement) == "SET LOCAL ROLE amesh_tenant_admin"
            raise RoleSwitchError("role switch denied")

    class Engine:
        @asynccontextmanager
        async def connect(self) -> AsyncIterator[Connection]:
            yield Connection()

    async def scenario() -> None:
        nonlocal entered
        with pytest.raises(RoleSwitchError, match="role switch denied"):
            async with tenant_admin_transaction(cast(AsyncEngine, Engine())):
                entered = True

    asyncio.run(scenario())
    assert not entered


def test_transaction_discovery_resists_alias_helper_and_nested_module_bypasses(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "helpers.py").write_text(
        """
def raw_helper(engine):
    opener = engine.connect
    return opener()

def raw_leaf(engine):
    return getattr(engine, "connect")()

def middle(engine):
    return raw_leaf(engine)

def explicit_call_leaf(engine):
    return engine.begin.__call__()
""",
        encoding="utf-8",
    )
    (nested / "repository.py").write_text(
        """
from amesh.adapters.postgres.tenant_context import tenant_admin_transaction as admin_scope
from amesh.adapters.postgres.tenant_context import tenant_transaction as tenant_scope
import amesh.adapters.postgres.tenant_context as transaction_context
from .helpers import explicit_call_leaf, middle, raw_helper as imported_helper

async def parameter_engine(engine):
    async with engine.begin():
        pass

async def explicit_session_role(engine):
    async with engine.connect() as connection:
        await connection.exec_driver_sql("SET ROLE amesh_runtime")

async def aliased_safe_wrapper(engine, tenant_id):
    transaction = tenant_scope
    async with transaction(engine, tenant_id):
        pass

async def module_aliased_safe_wrapper(engine, tenant_id):
    async with transaction_context.tenant_transaction(engine, tenant_id):
        pass

async def imported_raw_helper(engine):
    async with imported_helper(engine):
        pass

async def multi_hop_raw_helper(engine):
    async with middle(engine):
        pass

async def explicit_call_raw_helper(engine):
    async with explicit_call_leaf(engine):
        pass

class AlternateEngineAttribute:
    def helper(self):
        return self.database.begin()

    async def raw_context(self):
        async with self.database.connect():
            pass

    async def raw_context_via_method_helper(self):
        async with self.helper():
            pass

    async def approved_admin_context(self):
        async with admin_scope(self.database):
            pass

    async def approved_transaction_manager_context(self, tenant_id):
        transactions = self._services.transactions
        async with transactions.tenant(tenant_id):
            pass
""",
        encoding="utf-8",
    )

    entrypoints = _discover_transaction_entrypoints(tmp_path)

    assert entrypoints[("nested/repository.py", "parameter_engine")] == frozenset(
        {"raw:login-role"}
    )
    assert entrypoints[("nested/repository.py", "explicit_session_role")] == frozenset(
        {"raw:amesh_runtime"}
    )
    assert entrypoints[("nested/repository.py", "aliased_safe_wrapper")] == frozenset(
        {TENANT_TRANSACTION}
    )
    assert entrypoints[("nested/repository.py", "module_aliased_safe_wrapper")] == frozenset(
        {TENANT_TRANSACTION}
    )
    assert entrypoints[("nested/repository.py", "imported_raw_helper")] == frozenset(
        {"raw:login-role"}
    )
    assert entrypoints[("nested/helpers.py", "raw_leaf")] == frozenset({"raw:login-role"})
    assert entrypoints[("nested/helpers.py", "middle")] == frozenset({"raw:login-role"})
    assert entrypoints[("nested/repository.py", "multi_hop_raw_helper")] == frozenset(
        {"raw:login-role"}
    )
    assert entrypoints[("nested/helpers.py", "explicit_call_leaf")] == frozenset({"raw:login-role"})
    assert entrypoints[("nested/repository.py", "explicit_call_raw_helper")] == frozenset(
        {"raw:login-role"}
    )
    assert entrypoints[("nested/repository.py", "AlternateEngineAttribute.raw_context")] == (
        frozenset({"raw:login-role"})
    )
    assert entrypoints[
        ("nested/repository.py", "AlternateEngineAttribute.raw_context_via_method_helper")
    ] == frozenset({"raw:login-role"})
    assert entrypoints[
        ("nested/repository.py", "AlternateEngineAttribute.approved_admin_context")
    ] == frozenset({TENANT_ADMIN_TRANSACTION})
    assert entrypoints[
        (
            "nested/repository.py",
            "AlternateEngineAttribute.approved_transaction_manager_context",
        )
    ] == frozenset({TENANT_TRANSACTION})


def test_restricted_login_uses_tenant_and_admin_repository_boundaries(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        admin_engine = create_async_engine(migrated_test_database_url)
        restricted_engine: AsyncEngine | None = None
        restricted_role_created = False
        suffix = uuid4().hex[:12]
        restricted_role = f"amesh_test_{suffix}"
        restricted_password = uuid4().hex
        tenant_a_id = new_runtime_id()
        tenant_b_id = new_runtime_id()
        tenant_a_slug = f"restricted-a-{suffix}"
        tenant_b_slug = f"restricted-b-{suffix}"
        actor_id = f"test:restricted-repositories:{suffix}"
        projection_name = f"amesh_search_restricted_{suffix}"

        try:
            async with admin_engine.begin() as connection:
                await connection.execute(
                    text(
                        """
                        INSERT INTO tenants (
                            id, slug, display_name, storage_prefix, created_by, updated_by
                        ) VALUES (
                            :tenant_a_id, :tenant_a_slug, 'Restricted tenant A',
                            :tenant_a_prefix, :actor_id, :actor_id
                        ), (
                            :tenant_b_id, :tenant_b_slug, 'Restricted tenant B',
                            :tenant_b_prefix, :actor_id, :actor_id
                        )
                        """
                    ),
                    {
                        "tenant_a_id": tenant_a_id,
                        "tenant_a_slug": tenant_a_slug,
                        "tenant_a_prefix": f"tenants/{tenant_a_slug}/",
                        "tenant_b_id": tenant_b_id,
                        "tenant_b_slug": tenant_b_slug,
                        "tenant_b_prefix": f"tenants/{tenant_b_slug}/",
                        "actor_id": actor_id,
                    },
                )
                await connection.exec_driver_sql(
                    f'CREATE ROLE "{restricted_role}" LOGIN PASSWORD '
                    f"'{restricted_password}' NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOINHERIT NOBYPASSRLS"
                )
                await connection.exec_driver_sql(f'GRANT amesh_runtime TO "{restricted_role}"')
                await connection.exec_driver_sql(f'GRANT amesh_tenant_admin TO "{restricted_role}"')
                await connection.exec_driver_sql(
                    f'CREATE MATERIALIZED VIEW "{projection_name}" AS SELECT 1 AS value'
                )
            restricted_role_created = True

            async with admin_engine.connect() as connection:
                attributes = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT rolcanlogin, rolinherit, rolsuper, rolcreatedb,
                                       rolcreaterole, rolbypassrls
                                FROM pg_roles
                                WHERE rolname = :role_name
                                """
                            ),
                            {"role_name": restricted_role},
                        )
                    )
                    .mappings()
                    .one()
                )
                memberships = set(
                    await connection.scalars(
                        text(
                            """
                            SELECT granted.rolname
                            FROM pg_auth_members AS memberships
                            JOIN pg_roles AS granted ON granted.oid = memberships.roleid
                            JOIN pg_roles AS member ON member.oid = memberships.member
                            WHERE member.rolname = :role_name
                            """
                        ),
                        {"role_name": restricted_role},
                    )
                )
                admin_bypasses_rls = await connection.scalar(
                    text("SELECT rolbypassrls FROM pg_roles WHERE rolname = 'amesh_tenant_admin'")
                )
            assert dict(attributes) == {
                "rolcanlogin": True,
                "rolinherit": False,
                "rolsuper": False,
                "rolcreatedb": False,
                "rolcreaterole": False,
                "rolbypassrls": False,
            }
            assert memberships == {"amesh_runtime", "amesh_tenant_admin"}
            assert admin_bypasses_rls is True

            restricted_url = make_url(migrated_test_database_url).set(
                username=restricted_role,
                password=restricted_password,
            )
            restricted_engine = create_async_engine(
                restricted_url,
                pool_size=1,
                max_overflow=0,
            )

            with pytest.raises(DBAPIError):
                async with restricted_engine.connect() as connection:
                    assert await connection.scalar(text("SELECT current_user")) == restricted_role
                    await connection.execute(text("SELECT id FROM tenants"))

            with pytest.raises(DBAPIError):
                async with restricted_engine.connect() as connection:
                    await connection.execute(
                        text("SELECT * FROM amesh_rebuild_disposable_projections()")
                    )

            async with restricted_engine.connect() as connection:
                wait_backend_pid = await connection.scalar(text("SELECT pg_backend_pid()"))

            transport = PostgresDurableTransport(restricted_engine)
            assert (
                await transport.wait_for_work(
                    f"restricted-empty-{suffix}",
                    tenant_id=tenant_a_slug,
                    timeout_seconds=0.05,
                )
                is False
            )
            async with restricted_engine.connect() as connection:
                reused_session = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT pg_backend_pid() AS backend_pid,
                                       current_user AS current_user,
                                       current_setting('amesh.tenant_id', true) AS tenant_id,
                                       (SELECT count(*) FROM pg_listening_channels())
                                           AS listener_count
                                """
                            )
                        )
                    )
                    .mappings()
                    .one()
                )
            assert reused_session["backend_pid"] == wait_backend_pid
            assert reused_session["current_user"] == restricted_role
            assert reused_session["tenant_id"] in {None, ""}
            assert reused_session["listener_count"] == 0

            audit = PostgresAuditRepository(restricted_engine)
            authorization = PostgresAuthorizationRepository(restricted_engine)
            authentication = PostgresAuthenticationRepository(restricted_engine)
            credentials = PostgresCredentialRepository(restricted_engine)
            federation = PostgresFederationRepository(
                restricted_engine,
                token_pepper=SecretStr(uuid4().hex),
            )
            operations = PostgresOperationsRepository(restricted_engine)
            service_registry = PostgresServiceRegistryRepository(restricted_engine)
            upgrade = PostgresUpgradeRepository(restricted_engine)

            execution_repository = PostgresExecutionRepository(restricted_engine)
            execution_ports = split_execution_repository(execution_repository)
            flow = FlowDefinition(
                id=f"restricted-lifecycle-{suffix}",
                namespace=f"tests.restricted.{suffix}",
                tasks=[TaskDefinition(id="work", type="core.return", value="done")],
            )
            await execution_ports.flow_registry.apply_flow(flow, tenant_id=tenant_a_slug)
            execution = await execution_ports.lifecycle.create_execution(
                flow,
                tenant_id=tenant_a_slug,
                inputs={},
                actor_id=actor_id,
            )
            assert execution.state is ExecutionState.RUNNING
            admission = await execution_ports.admission.get_admission(
                AdmissionResourceType.EXECUTION,
                execution.execution_id,
                tenant_id=tenant_a_slug,
            )
            assert admission is not None
            assert admission.outcome is AdmissionOutcome.ADMITTED
            paused = await execution_ports.control.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.PAUSE,
                tenant_id=tenant_a_slug,
                expected_version=execution.version,
                expected_epoch=execution.epoch,
                actor_id=actor_id,
                reason="restricted role lifecycle proof",
            )
            resumed = await execution_ports.control.apply_execution_intervention(
                execution.execution_id,
                ExecutionInterventionAction.RESUME,
                tenant_id=tenant_a_slug,
                expected_version=paused.version,
                expected_epoch=paused.epoch,
                actor_id=actor_id,
                reason="restricted role lifecycle proof",
            )
            task_run = (
                await execution_ports.task_runs.list_task_runs(
                    execution.execution_id,
                    tenant_id=tenant_a_slug,
                )
            )[0]
            started = await execution_ports.task_runs.start_task(
                task_run.task_run_id,
                tenant_id=tenant_a_slug,
                dispatch=False,
            )
            completed_task = await execution_ports.task_runs.complete_task(
                started.task_run_id,
                started.current_attempt,
                {"value": "done"},
                tenant_id=tenant_a_slug,
            )
            assert completed_task.state is TaskRunState.SUCCESS
            completed_execution = await execution_ports.lifecycle.complete_execution(
                execution.execution_id,
                tenant_id=tenant_a_slug,
                expected_epoch=resumed.epoch,
                outputs={"value": "done"},
            )
            assert completed_execution.state is ExecutionState.SUCCESS

            audit_a = await audit.record_model_engine_account_action(
                tenant_a_slug,
                actor_id=actor_id,
                namespace="team.alpha",
                adapter="restricted-test",
                engine_ref="tenant-a",
                action="status",
                outcome="SUCCESS",
            )
            audit_b = await audit.record_model_engine_account_action(
                tenant_b_slug,
                actor_id=actor_id,
                namespace="team.beta",
                adapter="restricted-test",
                engine_ref="tenant-b",
                action="status",
                outcome="SUCCESS",
            )
            page_a = await audit.list_events(
                tenant_a_slug,
                actor_id=actor_id,
                action="model_engine.account.status",
                record_access=False,
            )
            page_b = await audit.list_events(
                tenant_b_slug,
                actor_id=actor_id,
                action="model_engine.account.status",
                record_access=False,
            )
            assert {event.event_id for event in page_a.items} == {audit_a}
            assert {event.event_id for event in page_b.items} == {audit_b}

            principal = PrincipalDefinition(
                principal_type=PrincipalType.USER,
                handle=f"restricted-user-{suffix}",
                display_name="Restricted repository user",
            )
            await authorization.create_principal(principal, actor_id=actor_id)
            boundary_a = NamespaceAuthorizationBoundary(
                tenant_id=tenant_a_slug,
                namespace="team.alpha",
            )
            boundary_b = NamespaceAuthorizationBoundary(
                tenant_id=tenant_b_slug,
                namespace="team.beta",
            )
            binding_a = RoleBinding(
                principal_id=principal.id,
                principal_type=PrincipalType.USER,
                role_name="viewer",
                scope_type=AuthorizationScopeType.NAMESPACE,
                tenant_id=tenant_a_slug,
                namespace=boundary_a.namespace,
            )
            binding_b = RoleBinding(
                principal_id=principal.id,
                principal_type=PrincipalType.USER,
                role_name="viewer",
                scope_type=AuthorizationScopeType.NAMESPACE,
                tenant_id=tenant_b_slug,
                namespace=boundary_b.namespace,
            )
            await authorization.set_namespace_boundary(boundary_a, actor_id=actor_id)
            await authorization.set_namespace_boundary(boundary_b, actor_id=actor_id)
            await authorization.create_binding(binding_a, actor_id=actor_id)
            await authorization.create_binding(binding_b, actor_id=actor_id)

            for tenant_slug, tenant_id, boundary, binding in (
                (tenant_a_slug, tenant_a_id, boundary_a, binding_a),
                (tenant_b_slug, tenant_b_id, boundary_b, binding_b),
            ):
                async with tenant_transaction(restricted_engine, tenant_slug) as (
                    connection,
                    resolved_tenant_id,
                ):
                    assert resolved_tenant_id == tenant_id
                    assert await connection.scalar(text("SELECT current_user")) == "amesh_runtime"
                    visible_tenant_slugs = set(
                        await connection.scalars(text("SELECT slug FROM tenants"))
                    )
                    visible_boundaries = set(
                        (
                            await connection.execute(
                                text(
                                    "SELECT tenant_id, namespace_name "
                                    "FROM auth_namespace_boundaries"
                                )
                            )
                        ).all()
                    )
                    visible_bindings = set(
                        (
                            await connection.execute(
                                text(
                                    "SELECT id, tenant_id FROM auth_role_bindings "
                                    "WHERE tenant_id IS NOT NULL"
                                )
                            )
                        ).all()
                    )
                assert visible_tenant_slugs == {tenant_slug}
                assert visible_boundaries == {(tenant_id, boundary.namespace)}
                assert visible_bindings == {(binding.id, tenant_id)}

            async with tenant_admin_transaction(restricted_engine) as connection:
                assert await connection.scalar(text("SELECT current_user")) == "amesh_tenant_admin"
                admin_visible_tenant_slugs = set(
                    await connection.scalars(
                        text("SELECT slug FROM tenants WHERE slug IN (:tenant_a, :tenant_b)"),
                        {"tenant_a": tenant_a_slug, "tenant_b": tenant_b_slug},
                    )
                )
            assert admin_visible_tenant_slugs == {tenant_a_slug, tenant_b_slug}

            with pytest.raises(DBAPIError):
                async with tenant_admin_transaction(restricted_engine) as connection:
                    await connection.execute(text("SELECT entry_id FROM task_cache_entries"))

            with pytest.raises(DBAPIError):
                async with tenant_transaction(restricted_engine, tenant_a_slug) as (
                    connection,
                    _tenant_id,
                ):
                    await connection.execute(
                        text("SELECT * FROM amesh_rebuild_disposable_projections()")
                    )

            assert principal.id in {item.id for item in await authorization.list_principals()}
            assert {binding_a.id, binding_b.id} <= {
                item.id for item in await authorization.list_bindings()
            }
            await authorization.delete_binding(binding_a.id, actor_id=actor_id)
            assert binding_a.id not in {item.id for item in await authorization.list_bindings()}
            assert await authentication.load_local_identity(principal.handle) is None
            assert await credentials.list_credentials(principal.id) == []
            assert await federation.list_scim(f"missing-{suffix}", "User") == ()

            checkpoint = await operations.record_backup_checkpoint(
                f"s3://restricted-tests/{suffix}/manifest.json",
                "a" * 64,
                created_by=actor_id,
            )
            assert await operations.latest_backup_checkpoint() == checkpoint
            assert set(await operations.prepare_restored_state()) == {
                "serviceInstancesStopped",
                "workersStopped",
                "queueClaimsExpired",
                "taskAttemptLeasesExpired",
                "genericLeasesExpired",
                "schedulerOwnersCleared",
            }
            assert projection_name in await operations.rebuild_disposable_projections()
            assert (await service_registry.topology()).instances == ()
            inventory = await upgrade.inventory()
            assert "0078_projection_rebuild_execution_scope.sql" in inventory.applied_migrations
            assert {tenant_a_slug, tenant_b_slug} <= set(await upgrade.tenant_slugs())
        finally:
            try:
                if restricted_engine is not None:
                    await restricted_engine.dispose()
                if restricted_role_created:
                    async with admin_engine.begin() as connection:
                        await connection.exec_driver_sql(
                            f'REVOKE amesh_tenant_admin FROM "{restricted_role}"'
                        )
                        await connection.exec_driver_sql(
                            f'REVOKE amesh_runtime FROM "{restricted_role}"'
                        )
                        await connection.exec_driver_sql(f'DROP ROLE "{restricted_role}"')
            finally:
                await admin_engine.dispose()

    asyncio.run(scenario())
