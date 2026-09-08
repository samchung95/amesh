"""Compatibility aggregate over SQL-owning execution repositories."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain import (
    PluginPolicyStage,
    PolicyDecision,
    PolicyStage,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.ports.execution_repository import (
    ExecutionRepository,
    ExecutionRepositoryPorts,
)

from .admission_repository import PostgresAdmissionRepository as PostgresAdmissionRepository
from .execution_control_repository import (
    PostgresExecutionControlRepository as PostgresExecutionControlRepository,
)
from .execution_lifecycle_repository import (
    PostgresExecutionLifecycleRepository as PostgresExecutionLifecycleRepository,
)
from .execution_port_repositories import build_execution_repository_ports
from .flow_registry_repository import (
    PostgresFlowRegistryRepository as PostgresFlowRegistryRepository,
)
from .flow_registry_repository import _same_flow_semantics as _same_flow_semantics
from .repository_support import (
    PostgresRepositoryBase,
    PostgresRepositoryServices,
    build_repository_services,
)
from .task_run_repository import PostgresTaskRunRepository as PostgresTaskRunRepository


class PostgresExecutionRepository(
    PostgresFlowRegistryRepository,
    PostgresAdmissionRepository,
    PostgresExecutionLifecycleRepository,
    PostgresTaskRunRepository,
    PostgresExecutionControlRepository,
    ExecutionRepository,
):
    def __init__(
        self,
        engine: AsyncEngine,
        *,
        services: PostgresRepositoryServices | None = None,
        plugin_resolution_provider: Callable[[FlowDefinition], dict[str, object]] | None = None,
        plugin_policy_enforcer: Callable[
            [FlowDefinition, str, PluginPolicyStage, str], Awaitable[None]
        ]
        | None = None,
        admission_policy_enforcer: Callable[
            [
                FlowDefinition,
                str,
                PolicyStage,
                str,
                dict[str, object] | None,
                TaskDefinition | None,
                UUID | None,
                UUID | None,
            ],
            Awaitable[PolicyDecision],
        ]
        | None = None,
    ) -> None:
        PostgresRepositoryBase.__init__(
            self, engine, services=services or build_repository_services(engine)
        )
        self._plugin_resolution_provider = plugin_resolution_provider
        self._plugin_policy_enforcer = plugin_policy_enforcer
        self._admission_policy_enforcer = admission_policy_enforcer
        self.__execution_ports = build_execution_repository_ports(self)

    def _execution_repository_ports(self) -> ExecutionRepositoryPorts:
        ports = getattr(self, "_PostgresExecutionRepository__execution_ports", None)
        if (
            ports is None
            or type(self) is not PostgresExecutionRepository
            or any(
                name in self.__dict__
                for name in dir(ExecutionRepository)
                if not name.startswith("_")
            )
        ):
            return ExecutionRepositoryPorts(self, self, self, self, self)
        return cast(ExecutionRepositoryPorts, ports)
