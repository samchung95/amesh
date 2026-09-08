"""Compose SQL-owning execution repositories over shared transaction services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from amesh.ports.execution_repository import ExecutionRepositoryPorts

from .admission_repository import PostgresAdmissionRepository as PostgresAdmissionRepository
from .execution_control_repository import (
    PostgresExecutionControlRepository as PostgresExecutionControlRepository,
)
from .execution_lifecycle_repository import (
    PostgresExecutionLifecycleRepository as PostgresExecutionLifecycleRepository,
)
from .flow_registry_repository import (
    PostgresFlowRegistryRepository as PostgresFlowRegistryRepository,
)
from .task_run_repository import PostgresTaskRunRepository as PostgresTaskRunRepository

if TYPE_CHECKING:
    from .execution_repository import PostgresExecutionRepository


def build_execution_repository_ports(
    repository: PostgresExecutionRepository,
) -> ExecutionRepositoryPorts:
    """Build one immutable set of SQL-owning execution repositories."""

    return ExecutionRepositoryPorts(
        flow_registry=PostgresFlowRegistryRepository(repository),
        admission=PostgresAdmissionRepository(repository),
        lifecycle=PostgresExecutionLifecycleRepository(repository),
        task_runs=PostgresTaskRunRepository(repository),
        control=PostgresExecutionControlRepository(repository),
    )
