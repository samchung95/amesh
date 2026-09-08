from __future__ import annotations

import ast
import asyncio
from collections.abc import Mapping
from inspect import Parameter, Signature, getsource, isfunction, signature
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAdmissionRepository,
    PostgresExecutionControlRepository,
    PostgresExecutionLifecycleRepository,
    PostgresFlowRegistryRepository,
    PostgresTaskRunRepository,
    execution_port_repositories,
)
from amesh.adapters.postgres import (
    PostgresExecutionRepository as BarrelRepository,
)
from amesh.adapters.postgres.execution_control_repository import _ExecutionControlMixin
from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
from amesh.adapters.postgres.repository_support import build_repository_services
from amesh.domain import (
    AdmissionResourceType,
    TaskRunEventType,
    TaskRunLifecyclePhase,
    TaskRunState,
)
from amesh.dsl import FlowDefinition
from amesh.ports.execution_repository import (
    AdmissionRepository,
    ExecutionControlRepository,
    ExecutionLifecycleRepository,
    ExecutionRepository,
    FlowRegistryRepository,
    TaskRunRepository,
    split_execution_repository,
)

PORT_TYPES = (
    ("flow_registry", PostgresFlowRegistryRepository, FlowRegistryRepository),
    ("admission", PostgresAdmissionRepository, AdmissionRepository),
    ("lifecycle", PostgresExecutionLifecycleRepository, ExecutionLifecycleRepository),
    ("task_runs", PostgresTaskRunRepository, TaskRunRepository),
    ("control", PostgresExecutionControlRepository, ExecutionControlRepository),
)


def test_apply_flow_replaces_historical_revision_invalid_under_current_constraints(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        flow = FlowDefinition.model_validate(
            {
                "id": "historical",
                "namespace": f"tests.{uuid4().hex}",
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        try:
            first = await repository.apply_flow(flow, tenant_id="default")
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE flow_revisions SET canonical_definition = "
                        "jsonb_set(canonical_definition, '{tasks,0,id}', '\"\"'::jsonb) "
                        "WHERE flow_id = :flow_id AND revision = 1"
                    ),
                    {"flow_id": first.resource_id},
                )
            second = await repository.apply_flow(flow, tenant_id="default")
            assert second.revision == 2
            replay = await repository.apply_flow(
                flow.model_copy(update={"revision": 2}), tenant_id="default"
            )
            assert replay.revision == 2
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def _public_surface(owner: type[object]) -> set[str]:
    return {
        name
        for candidate in owner.__mro__
        for name, value in vars(candidate).items()
        if not name.startswith("_") and (isfunction(value) or isinstance(value, property))
    }


def test_execution_repository_import_and_control_composition() -> None:
    assert BarrelRepository is PostgresExecutionRepository
    assert PostgresExecutionRepository.__module__ == (
        "amesh.adapters.postgres.execution_repository"
    )
    assert issubclass(PostgresExecutionRepository, _ExecutionControlMixin)
    assert str(signature(PostgresExecutionRepository)) == (
        "(engine: 'AsyncEngine', *, services: 'PostgresRepositoryServices | None' = None, plugin_resolution_provider: "
        "'Callable[[FlowDefinition], dict[str, object]] | None' = None, "
        "plugin_policy_enforcer: "
        "'Callable[[FlowDefinition, str, PluginPolicyStage, str], Awaitable[None]] | None' "
        "= None, admission_policy_enforcer: "
        "'Callable[[FlowDefinition, str, PolicyStage, str, dict[str, object] | None, "
        "TaskDefinition | None, UUID | None, UUID | None], Awaitable[PolicyDecision]] | "
        "None' = None) -> 'None'"
    )
    assert all(
        hasattr(PostgresExecutionRepository, name)
        for name in (
            "apply_flow",
            "create_execution",
            "request_admission",
            "complete_execution",
            "start_task",
            "apply_execution_intervention",
            "list_subflows",
        )
    )
    engine = cast(AsyncEngine, object())
    services = build_repository_services(engine)
    repository = PostgresExecutionRepository(engine, services=services)
    ports = split_execution_repository(repository)
    assert ports is split_execution_repository(repository)
    port_values = tuple(getattr(ports, attribute) for attribute, _, _ in PORT_TYPES)
    assert len({id(value) for value in port_values}) == len(PORT_TYPES)
    assert repository._services is services
    for attribute, implementation, protocol in PORT_TYPES:
        port = getattr(ports, attribute)
        assert type(port) is implementation
        assert protocol in implementation.__mro__
        assert port._repository is repository
        assert port._engine is repository._engine
        assert port._services is services
        extra = {"execution_guard"} if attribute == "lifecycle" else set()
        assert _public_surface(implementation) == _public_surface(protocol) | extra
        for method_name in _public_surface(protocol) - {"has_admission_policy_enforcer"}:
            actual = signature(getattr(implementation, method_name))
            expected = signature(getattr(protocol, method_name))
            # Mypy checks structural types; runtime compatibility preserves argument
            # names, kinds and defaults even when an implementation narrows Any.
            assert actual.replace(
                parameters=[
                    p.replace(annotation=Parameter.empty) for p in actual.parameters.values()
                ],
                return_annotation=Signature.empty,
            ) == expected.replace(
                parameters=[
                    p.replace(annotation=Parameter.empty) for p in expected.parameters.values()
                ],
                return_annotation=Signature.empty,
            )


def test_generic_execution_repository_splitter_retains_alias_fallback() -> None:
    repository = cast(ExecutionRepository, object())

    ports = split_execution_repository(repository)

    assert ports.flow_registry is repository
    assert ports.admission is repository
    assert ports.lifecycle is repository
    assert ports.task_runs is repository
    assert ports.control is repository


def test_narrow_port_composition_has_no_sql_and_each_repository_owns_its_transactions() -> None:
    source = getsource(execution_port_repositories)

    assert "tenant_transaction" not in source
    assert ".transactions.tenant" not in source
    assert not any(isinstance(node, ast.AsyncWith) for node in ast.walk(ast.parse(source)))
    for _, implementation, _ in PORT_TYPES:
        implementation_source = getsource(implementation)
        assert ".transactions.tenant" in implementation_source
        assert ".execute(" in implementation_source
        assert "return await self._repository." not in implementation_source


def test_constructor_bypass_retains_compatibility_fallback() -> None:
    repository = object.__new__(PostgresExecutionRepository)
    ports = split_execution_repository(repository)
    assert all(getattr(ports, name) is repository for name, _, _ in PORT_TYPES)


def test_postgres_repository_functions_stay_within_the_reviewed_size_boundary() -> None:
    root = Path(__file__).resolve().parents[3] / "src/amesh/adapters/postgres"
    oversized = []
    for path in root.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = (node.end_lineno or node.lineno) - node.lineno + 1
                if length > 120:
                    oversized.append(f"{path.name}:{node.name}: {length}")
    assert oversized == []


def test_narrow_ports_delegate_through_aggregate_instance_overrides() -> None:
    calls: list[tuple[str, str]] = []
    repository = PostgresExecutionRepository(cast(AsyncEngine, object()))

    async def list_flows(*, tenant_id: str) -> list[object]:
        calls.append(("flow_registry", tenant_id))
        return []

    async def get_admission(
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
    ) -> None:
        calls.append(("admission", tenant_id))

    async def list_executions(*, tenant_id: str, limit: int = 100) -> list[object]:
        calls.append(("lifecycle", tenant_id))
        return []

    async def list_task_runs(
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[object]:
        calls.append(("task_runs", tenant_id))
        return []

    async def list_execution_interventions(
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[object]:
        calls.append(("control", tenant_id))
        return []

    object.__setattr__(repository, "list_flows", list_flows)
    object.__setattr__(repository, "get_admission", get_admission)
    object.__setattr__(repository, "list_executions", list_executions)
    object.__setattr__(repository, "list_task_runs", list_task_runs)
    object.__setattr__(repository, "list_execution_interventions", list_execution_interventions)

    async def scenario() -> None:
        ports = split_execution_repository(repository)
        resource_id = uuid4()
        await ports.flow_registry.list_flows(tenant_id="flow")
        await ports.admission.get_admission(
            AdmissionResourceType.EXECUTION,
            resource_id,
            tenant_id="admission",
        )
        await ports.lifecycle.list_executions(tenant_id="lifecycle")
        await ports.task_runs.list_task_runs(resource_id, tenant_id="task_runs")
        await ports.control.list_execution_interventions(resource_id, tenant_id="control")

    asyncio.run(scenario())
    assert calls == [
        ("flow_registry", "flow"),
        ("admission", "admission"),
        ("lifecycle", "lifecycle"),
        ("task_runs", "task_runs"),
        ("control", "control"),
    ]


def test_execution_control_mixin_keeps_self_dispatch_for_task_events() -> None:
    class ProbeRepository(PostgresExecutionRepository):
        def __init__(self) -> None:
            super().__init__(cast(AsyncEngine, object()))
            self.events: list[TaskRunEventType] = []

        async def _update_task_control(
            self,
            connection: AsyncConnection,
            tenant_id: UUID,
            task: RowMapping,
            state: TaskRunState,
        ) -> RowMapping:
            return cast(
                RowMapping,
                {
                    "id": task["id"],
                    "execution_id": task["execution_id"],
                    "version": 2,
                },
            )

        async def _insert_task_event(
            self,
            connection: AsyncConnection,
            tenant_id: UUID,
            row: RowMapping | Mapping[str, object],
            event_id: UUID,
            event_type: TaskRunEventType,
            correlation_id: UUID,
            *,
            reason: str | None = None,
            payload: dict[str, object] | None = None,
            actor_id: str = "mvp-executor",
        ) -> None:
            self.events.append(event_type)

    async def scenario() -> None:
        repository = ProbeRepository()
        task_id = uuid4()
        await repository._request_task_cancellation(
            cast(AsyncConnection, object()),
            uuid4(),
            [
                cast(
                    RowMapping,
                    {
                        "id": task_id,
                        "execution_id": uuid4(),
                        "state": TaskRunState.WAITING.value,
                        "lifecycle_phase": TaskRunLifecyclePhase.MAIN.value,
                    },
                )
            ],
            actor_id="test",
            reason="test cancellation",
            correlation_id=uuid4(),
        )
        assert repository.events == [TaskRunEventType.CANCELLED]

    asyncio.run(scenario())
