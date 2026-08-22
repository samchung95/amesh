from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCacheMode(StrEnum):
    USE = "USE"
    BYPASS = "BYPASS"
    REFRESH = "REFRESH"


class TaskCacheDecision(StrEnum):
    HIT = "HIT"
    MISS = "MISS"
    MISS_EXPIRED = "MISS_EXPIRED"
    MISS_INVALIDATED = "MISS_INVALIDATED"
    MISS_CONCURRENT = "MISS_CONCURRENT"
    REFRESH = "REFRESH"
    BYPASS = "BYPASS"


class TaskCacheKey(BaseModel):
    model_config = ConfigDict(frozen=True)

    key_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    key_prefix: str = Field(min_length=1, max_length=1024)
    cache_namespace: str = Field(min_length=1, max_length=128)
    scope: str = Field(min_length=1, max_length=32)
    namespace: str = Field(min_length=1, max_length=255)
    flow_id: str = Field(min_length=1, max_length=128)
    flow_revision: int = Field(ge=1)
    task_id: str = Field(min_length=1, max_length=128)
    task_type: str = Field(min_length=1, max_length=512)
    security_context_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    invalidation_policy: str = Field(min_length=1, max_length=64)
    ttl: timedelta
    population_lease: timedelta = timedelta(hours=1)


class TaskCacheLookup(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision: TaskCacheDecision
    reason: str
    key_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    owner_token: UUID | None = None
    output: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    source_execution_id: UUID | None = None
    source_task_run_id: UUID | None = None
    source_attempt: int | None = Field(default=None, ge=1)
    expires_at: datetime | None = None


class TaskCacheEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry_id: UUID
    key_hash: str
    key_prefix: str
    cache_namespace: str
    scope: str
    namespace: str
    flow_id: str
    flow_revision: int
    task_id: str
    task_type: str
    state: str
    source_execution_id: UUID | None = None
    source_task_run_id: UUID | None = None
    source_attempt: int | None = None
    expires_at: datetime | None = None
    hit_count: int = 0
    last_hit_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    invalidation_reason: str | None = None


class TaskCachePurgeResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    invalidated_count: int = Field(ge=0)
    reason: str


class TaskCacheRepository(Protocol):
    async def lookup_or_reserve(
        self,
        key: TaskCacheKey,
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
        mode: TaskCacheMode = TaskCacheMode.USE,
    ) -> TaskCacheLookup: ...

    async def publish(
        self,
        key_hash: str,
        owner_token: UUID,
        output: dict[str, Any],
        evidence: dict[str, Any],
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
    ) -> bool: ...

    async def record_bypass(
        self,
        key: TaskCacheKey,
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
        reason: str,
    ) -> None: ...

    async def abandon(
        self,
        key_hash: str,
        owner_token: UUID,
        *,
        tenant_id: str,
        execution_id: UUID,
        task_run_id: UUID,
        attempt: int,
        reason: str,
    ) -> bool: ...

    async def list_entries(
        self,
        *,
        tenant_id: str,
        key_prefix: str | None = None,
        namespace: str | None = None,
        flow_id: str | None = None,
        task_id: str | None = None,
        limit: int = 100,
    ) -> list[TaskCacheEntry]: ...

    async def purge(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
        key_prefix: str | None = None,
        namespace: str | None = None,
        flow_id: str | None = None,
        task_id: str | None = None,
    ) -> TaskCachePurgeResult: ...
