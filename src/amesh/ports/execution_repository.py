from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import ExecutionState, ResourceMetadata
from amesh.dsl import FlowDefinition


class TaskRunState(StrEnum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    RETRY_DELAY = "RETRY_DELAY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TaskStateConflictError(RuntimeError):
    """Raised when persisted task state no longer permits the requested transition."""


class ExecutionStateConflictError(RuntimeError):
    """Raised when an execution transition uses a stale epoch or illegal state."""


class PersistedExecution(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    tenant_id: str
    state: ExecutionState
    epoch: int = Field(ge=1)
    version: int = Field(ge=0)
    namespace: str
    flow_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class PersistedFlow(BaseModel):
    model_config = ConfigDict(frozen=True)

    resource_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    revision: int = Field(ge=1)
    semantic_hash: str
    metadata: ResourceMetadata
    etag: str


class PersistedTaskRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_run_id: UUID
    execution_id: UUID
    task_id: str
    state: TaskRunState
    current_attempt: int = Field(ge=0)
    version: int = Field(ge=0)
    retry_at: datetime | None = None
    result: dict[str, Any] | None = None


class ExecutionRepository(Protocol):
    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        expected_etag: str | None = None,
    ) -> PersistedFlow: ...

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> FlowDefinition: ...

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]: ...

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> PersistedExecution: ...

    async def get_execution(self, execution_id: UUID) -> PersistedExecution: ...

    async def list_executions(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> list[PersistedExecution]: ...

    async def list_task_runs(self, execution_id: UUID) -> list[PersistedTaskRun]: ...

    async def start_task(self, task_run_id: UUID) -> PersistedTaskRun: ...

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, Any],
    ) -> PersistedTaskRun: ...

    async def retry_task(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        retry_at: datetime,
        reason: str,
    ) -> PersistedTaskRun: ...

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
    ) -> PersistedTaskRun: ...

    async def complete_execution(
        self,
        execution_id: UUID,
        *,
        expected_epoch: int,
    ) -> PersistedExecution: ...

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
        *,
        expected_epoch: int,
    ) -> PersistedExecution: ...
