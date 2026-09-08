"""Shared execution-port dependencies; SQL stays with its owning repository."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, cast
from uuid import UUID

from amesh.domain import PluginPolicyStage, PolicyDecision, PolicyStage
from amesh.dsl import FlowDefinition, TaskDefinition

from .repository_support import PostgresRepositoryBase

if TYPE_CHECKING:
    from .execution_repository import PostgresExecutionRepository


class PostgresExecutionPort(PostgresRepositoryBase):
    _plugin_resolution_provider: Callable[[FlowDefinition], dict[str, object]] | None
    _plugin_policy_enforcer: (
        Callable[[FlowDefinition, str, PluginPolicyStage, str], Awaitable[None]] | None
    )
    _admission_policy_enforcer: (
        Callable[
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
        | None
    )

    def __init__(self, repository: PostgresExecutionRepository) -> None:
        super().__init__(repository._engine, services=repository._services)
        self._port_repository = repository
        self._plugin_resolution_provider = repository._plugin_resolution_provider
        self._plugin_policy_enforcer = repository._plugin_policy_enforcer
        self._admission_policy_enforcer = repository._admission_policy_enforcer

    @property
    def _repository(self) -> PostgresExecutionRepository:
        # The compatibility aggregate inherits these implementations so legacy
        # subclass hooks still dispatch on that same instance.
        return cast("PostgresExecutionRepository", self.__dict__.get("_port_repository", self))
