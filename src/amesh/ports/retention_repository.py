from __future__ import annotations

from typing import Protocol
from uuid import UUID

from amesh.domain.retention import (
    LifecycleBatch,
    LifecycleJob,
    LifecycleLegalHold,
    LifecycleLegalHoldDraft,
    LifecyclePolicy,
    LifecyclePolicyDraft,
)


class RetentionRepository(Protocol):
    async def list_policies(self, tenant_id: str) -> tuple[LifecyclePolicy, ...]: ...

    async def save_policy(
        self,
        tenant_id: str,
        draft: LifecyclePolicyDraft,
        *,
        actor_id: str,
        policy_id: UUID | None = None,
        expected_version: int | None = None,
    ) -> LifecyclePolicy: ...

    async def create_hold(
        self,
        tenant_id: str,
        draft: LifecycleLegalHoldDraft,
        *,
        actor_id: str,
    ) -> LifecycleLegalHold: ...

    async def list_holds(self, tenant_id: str) -> tuple[LifecycleLegalHold, ...]: ...

    async def release_hold(
        self,
        tenant_id: str,
        hold_id: UUID,
        *,
        actor_id: str,
    ) -> LifecycleLegalHold: ...

    async def preview(
        self,
        tenant_id: str,
        policy_id: UUID,
        *,
        actor_id: str,
        reason: str,
    ) -> LifecycleJob: ...

    async def confirm(self, tenant_id: str, job_id: UUID, confirmation: str) -> LifecycleJob: ...

    async def process_batch(self, tenant_id: str, job_id: UUID) -> LifecycleBatch: ...

    async def record_object_result(
        self,
        tenant_id: str,
        job_id: UUID,
        ordinal: int,
        *,
        error: str | None,
    ) -> None: ...

    async def finish_external(self, tenant_id: str, job_id: UUID) -> LifecycleJob: ...

    async def get_job(self, tenant_id: str, job_id: UUID) -> LifecycleJob: ...

    async def list_jobs(self, tenant_id: str, *, limit: int = 50) -> tuple[LifecycleJob, ...]: ...

    async def create_due_jobs(self, tenant_id: str) -> tuple[LifecycleJob, ...]: ...
