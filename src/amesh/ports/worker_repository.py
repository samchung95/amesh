from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .metadata_repository import WorkerStatus

WORKER_PROTOCOL_VERSION = 1


class WorkerFenceError(RuntimeError):
    """Raised when a worker uses an expired or superseded task claim."""


class WorkerCompatibilityError(RuntimeError):
    """Raised when a worker cannot participate in the current protocol."""


class WorkerLiveness(StrEnum):
    LIVE = "LIVE"
    STALE = "STALE"
    STOPPED = "STOPPED"


class WorkerCompatibility(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"


class WorkerLossPolicy(StrEnum):
    REQUEUE = "REQUEUE"
    FAIL = "FAIL"


class WorkerRegistration(BaseModel):
    model_config = ConfigDict(frozen=True)

    worker_id: UUID
    worker_group: str = Field(min_length=1, max_length=128)
    instance_name: str = Field(min_length=1, max_length=256)
    version: str = Field(min_length=1, max_length=128)
    protocol_version: int = Field(default=WORKER_PROTOCOL_VERSION, ge=1)
    capabilities: tuple[str, ...] = ()
    runner_types: tuple[str, ...] = ()
    capacity: int = Field(default=1, ge=1, le=100_000)
    labels: dict[str, str] = Field(default_factory=dict)


class WorkerTaskClaim(BaseModel):
    model_config = ConfigDict(frozen=True)

    queue_id: int = Field(ge=1)
    message_id: UUID
    worker_id: UUID
    task_run_id: UUID
    execution_id: UUID
    task_id: str
    attempt: int = Field(ge=1)
    fencing_token: int = Field(ge=1)
    lease_expires_at: datetime
    delivery_attempt: int = Field(ge=1)
    protocol_version: int = Field(default=WORKER_PROTOCOL_VERSION, ge=1)


class WorkerClaimHeartbeat(BaseModel):
    model_config = ConfigDict(frozen=True)

    queue_id: int = Field(ge=1)
    task_run_id: UUID
    attempt: int = Field(ge=1)
    fencing_token: int = Field(ge=1)
    progress: dict[str, object] = Field(default_factory=dict)
    resource_usage: dict[str, object] = Field(default_factory=dict)
    cancellation_acknowledged: bool = False


class WorkerInventory(BaseModel):
    model_config = ConfigDict(frozen=True)

    worker_id: UUID
    tenant_id: str
    worker_group: str
    instance_name: str
    version: str
    protocol_version: int = Field(ge=1)
    status: WorkerStatus
    liveness: WorkerLiveness
    compatibility: WorkerCompatibility
    capabilities: tuple[str, ...]
    runner_types: tuple[str, ...]
    labels: dict[str, str]
    capacity: int = Field(ge=1)
    claimed_work: int = Field(ge=0)
    utilization: float = Field(ge=0)
    progress: dict[str, object]
    resource_usage: dict[str, object]
    cancellation_acknowledged: bool
    last_heartbeat_at: datetime
    resource_version: int = Field(ge=1)


class WorkerRepository(Protocol):
    async def register_worker(
        self,
        registration: WorkerRegistration,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> WorkerInventory: ...

    async def claim_tasks(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        limit: int,
        lease_duration: timedelta,
    ) -> list[WorkerTaskClaim]: ...

    async def heartbeat_worker(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        expected_version: int,
        status: WorkerStatus,
        lease_duration: timedelta,
        claims: tuple[WorkerClaimHeartbeat, ...] = (),
        progress: dict[str, object] | None = None,
        resource_usage: dict[str, object] | None = None,
        cancellation_acknowledged: bool = False,
        actor_id: str,
    ) -> WorkerInventory: ...

    async def drain_worker(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        expected_version: int,
        actor_id: str,
    ) -> WorkerInventory: ...

    async def recover_expired_claims(
        self,
        *,
        tenant_id: str,
        policy: WorkerLossPolicy,
        limit: int = 100,
    ) -> int: ...

    async def list_worker_inventory(self, *, tenant_id: str) -> list[WorkerInventory]: ...

    async def wait_for_work(
        self,
        *,
        tenant_id: str,
        timeout_seconds: float,
    ) -> bool: ...
