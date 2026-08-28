from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.domain.retention import (
    LifecycleJob,
    LifecycleJobState,
    LifecycleScheduleResult,
    LifecycleTrigger,
)
from amesh.ports.object_store import ObjectLifecycleResult, ObjectMetadata
from amesh.ports.retention_repository import RetentionRepository


class LifecycleObjectStore(Protocol):
    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata: ...

    async def apply_lifecycle(
        self,
        tenant_id: str,
        uri: str,
        *,
        retention_until: datetime | None,
        legal_hold: bool,
        referenced: bool,
        delete: bool = False,
    ) -> ObjectLifecycleResult: ...


class RetentionService:
    def __init__(
        self,
        repository: RetentionRepository,
        object_store: LifecycleObjectStore,
    ) -> None:
        self._repository = repository
        self._object_store = object_store

    async def confirm_and_process(
        self,
        tenant_id: str,
        job_id: UUID,
        confirmation: str,
    ) -> LifecycleJob:
        await self._repository.confirm(tenant_id, job_id, confirmation)
        return await self.process_once(tenant_id, job_id)

    async def process_once(self, tenant_id: str, job_id: UUID) -> LifecycleJob:
        batch = await self._repository.process_batch(tenant_id, job_id)
        if not batch.objects:
            return batch.job
        for item in batch.objects:
            error: str | None = None
            try:
                metadata = await self._object_store.head(tenant_id, item.uri)
                result = await self._object_store.apply_lifecycle(
                    tenant_id,
                    item.uri,
                    retention_until=metadata.retention_until,
                    legal_hold=metadata.legal_hold,
                    referenced=False,
                    delete=True,
                )
                if not result.deleted:
                    raise RuntimeError(
                        f"object lifecycle deletion blocked by {result.blocked_by or 'policy'}"
                    )
            except Exception as exc:  # the durable job records provider-specific failures for retry
                error = f"{type(exc).__name__}: {exc}"
            await self._repository.record_object_result(
                tenant_id,
                job_id,
                item.ordinal,
                error=error,
            )
        return await self._repository.finish_external(tenant_id, job_id)

    async def run_scheduled_once(self, tenant_ids: tuple[str, ...]) -> LifecycleScheduleResult:
        jobs_created = 0
        batches_processed = 0
        records_processed = 0
        for tenant_id in tenant_ids:
            created = await self._repository.create_due_jobs(tenant_id)
            jobs_created += len(created)
            existing = await self._repository.list_jobs(tenant_id, limit=100)
            runnable = {
                job.job_id: job
                for job in (*created, *existing)
                if job.trigger is LifecycleTrigger.SCHEDULED
                and job.state
                in {
                    LifecycleJobState.READY,
                    LifecycleJobState.RUNNING,
                    LifecycleJobState.WAITING_EXTERNAL,
                    LifecycleJobState.FAILED,
                }
            }
            for job in runnable.values():
                before = job.processed_records
                result = await self.process_once(tenant_id, job.job_id)
                batches_processed += 1
                records_processed += max(0, result.processed_records - before)
        return LifecycleScheduleResult(
            jobsCreated=jobs_created,
            batchesProcessed=batches_processed,
            recordsProcessed=records_processed,
        )
