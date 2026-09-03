from __future__ import annotations

import ast
import asyncio
from collections.abc import Mapping
from inspect import getsource, isfunction, signature
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

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
from amesh.domain import (
    AdmissionResourceType,
    TaskRunEventType,
    TaskRunLifecyclePhase,
    TaskRunState,
)
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
        "(engine: 'AsyncEngine', *, plugin_resolution_provider: "
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
    repository = PostgresExecutionRepository(cast(AsyncEngine, object()))
    ports = split_execution_repository(repository)
    assert ports is split_execution_repository(repository)
    port_values = tuple(getattr(ports, attribute) for attribute, _, _ in PORT_TYPES)
    assert len({id(value) for value in port_values}) == len(PORT_TYPES)
    services = repository._services
    for attribute, implementation, protocol in PORT_TYPES:
        port = getattr(ports, attribute)
        assert type(port) is implementation
        assert protocol in implementation.__mro__
        assert port._repository is repository
        assert port._engine is repository._engine
        assert port._services is services
        assert _public_surface(implementation) == _public_surface(protocol)
        for method_name in _public_surface(protocol) - {"has_admission_policy_enforcer"}:
            assert signature(getattr(implementation, method_name)) == signature(
                getattr(protocol, method_name)
            )


def test_generic_execution_repository_splitter_retains_alias_fallback() -> None:
    repository = cast(ExecutionRepository, object())

    ports = split_execution_repository(repository)

    assert ports.flow_registry is repository
    assert ports.admission is repository
    assert ports.lifecycle is repository
    assert ports.task_runs is repository
    assert ports.control is repository


def test_narrow_port_module_has_no_transaction_authority() -> None:
    source = getsource(execution_port_repositories)

    assert "tenant_transaction" not in source
    assert ".transactions.tenant" not in source
    assert not any(isinstance(node, ast.AsyncWith) for node in ast.walk(ast.parse(source)))


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
