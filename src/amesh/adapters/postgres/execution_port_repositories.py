"""Narrow PostgreSQL execution-port views over the compatibility repository."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

from amesh.domain import (
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionResourceType,
    FailureCategory,
    FlowLifecycle,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    PolicyDecision,
    PolicyStage,
    ResolvedAdmissionPolicy,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.ports.execution_repository import (
    AdmissionRepository,
    ExecutionControlRepository,
    ExecutionInterventionAction,
    ExecutionInterventionRecord,
    ExecutionLaunchSource,
    ExecutionLifecycleRepository,
    ExecutionRepositoryPorts,
    FlowRegistryRepository,
    PersistedExecution,
    PersistedFlow,
    PersistedFlowRevision,
    PersistedIterationSummary,
    PersistedSubflow,
    PersistedTaskDeferral,
    PersistedTaskRun,
    PersistedTaskRunSummary,
    SubflowLaunchContext,
    TaskRunRepository,
)
from amesh.workflow.metadata import (
    NamespaceWorkflowMetadata,
    NamespaceWorkflowMetadataUpdate,
    NamespaceWorkflowMetadataView,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from .execution_repository import PostgresExecutionRepository
    from .repository_support import PostgresRepositoryServices


class _PostgresExecutionPort:
    """Share one aggregate's transaction and support-service authority."""

    def __init__(self, repository: PostgresExecutionRepository) -> None:
        self._repository = repository

    @property
    def _engine(self) -> AsyncEngine:
        return self._repository._engine

    @property
    def _services(self) -> PostgresRepositoryServices:
        return self._repository._services


class PostgresFlowRegistryRepository(_PostgresExecutionPort, FlowRegistryRepository):
    """Flow-registry operations delegated to the compatibility repository."""

    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        expected_etag: str | None = None,
        actor_id: str = "system:flow-manager",
        revision_source: FlowRevisionSource | None = None,
    ) -> PersistedFlow:
        return await self._repository.apply_flow(
            flow,
            tenant_id=tenant_id,
            expected_etag=expected_etag,
            actor_id=actor_id,
            revision_source=revision_source,
        )

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> FlowDefinition:
        return await self._repository.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )

    async def get_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> PersistedFlowRevision:
        return await self._repository.get_flow_revision(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]:
        return await self._repository.list_flows(tenant_id=tenant_id)

    async def upsert_namespace_workflow_metadata(
        self,
        namespace: str,
        update: NamespaceWorkflowMetadataUpdate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> NamespaceWorkflowMetadata:
        return await self._repository.upsert_namespace_workflow_metadata(
            namespace,
            update,
            tenant_id=tenant_id,
            actor_id=actor_id,
        )

    async def get_namespace_workflow_metadata(
        self,
        namespace: str,
        *,
        tenant_id: str,
    ) -> NamespaceWorkflowMetadataView:
        return await self._repository.get_namespace_workflow_metadata(
            namespace,
            tenant_id=tenant_id,
        )

    async def list_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> list[FlowRevisionRecord]:
        return await self._repository.list_flow_revisions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
        )

    async def diff_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        from_revision: int,
        to_revision: int,
        *,
        tenant_id: str,
    ) -> FlowRevisionDiff:
        return await self._repository.diff_flow_revisions(
            namespace,
            flow_id,
            from_revision,
            to_revision,
            tenant_id=tenant_id,
        )

    async def promote_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        lifecycle: FlowLifecycle,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
        reason: str | None = None,
    ) -> PersistedFlow:
        return await self._repository.promote_flow_revision(
            namespace,
            flow_id,
            revision,
            lifecycle,
            tenant_id=tenant_id,
            actor_id=actor_id,
            reason=reason,
        )

    async def restore_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
        reason: str | None = None,
    ) -> PersistedFlow:
        return await self._repository.restore_flow_revision(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
            actor_id=actor_id,
            reason=reason,
        )

    async def delete_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
    ) -> None:
        await self._repository.delete_flow_revision(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
            actor_id=actor_id,
        )


class PostgresAdmissionRepository(_PostgresExecutionPort, AdmissionRepository):
    """Admission operations delegated to the compatibility repository."""

    @property
    def has_admission_policy_enforcer(self) -> bool:
        return self._repository.has_admission_policy_enforcer

    async def enforce_admission_policy(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        stage: PolicyStage,
        actor_id: str,
        inputs: dict[str, object] | None = None,
        task: TaskDefinition | None = None,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        return await self._repository.enforce_admission_policy(
            flow,
            tenant_id=tenant_id,
            stage=stage,
            actor_id=actor_id,
            inputs=inputs,
            task=task,
            execution_id=execution_id,
            task_run_id=task_run_id,
        )

    async def request_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
        *,
        tenant_id: str,
        priority: int = 0,
    ) -> AdmissionDecision:
        return await self._repository.request_admission(
            resource_type,
            resource_id,
            policies,
            tenant_id=tenant_id,
            priority=priority,
        )

    async def get_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
    ) -> AdmissionDecision | None:
        return await self._repository.get_admission(
            resource_type,
            resource_id,
            tenant_id=tenant_id,
        )

    async def release_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
        reason: str = "resource completed",
    ) -> bool:
        return await self._repository.release_admission(
            resource_type,
            resource_id,
            tenant_id=tenant_id,
            reason=reason,
        )

    async def reconcile_admission(self, *, tenant_id: str, limit: int = 100) -> int:
        return await self._repository.reconcile_admission(tenant_id=tenant_id, limit=limit)

    async def admission_diagnostics(self, *, tenant_id: str) -> AdmissionDiagnostics:
        return await self._repository.admission_diagnostics(tenant_id=tenant_id)


class PostgresExecutionLifecycleRepository(_PostgresExecutionPort, ExecutionLifecycleRepository):
    """Execution-lifecycle operations delegated to the compatibility repository."""

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, Any],
        trigger: dict[str, Any] | None = None,
        launch_source: ExecutionLaunchSource = ExecutionLaunchSource.MANUAL,
        idempotency_key: str | None = None,
        actor_id: str = "system:executor",
        labels: dict[str, str] | None = None,
        subflow: SubflowLaunchContext | None = None,
        priority: int | None = None,
    ) -> PersistedExecution:
        return await self._repository.create_execution(
            flow,
            tenant_id=tenant_id,
            inputs=inputs,
            trigger=trigger,
            launch_source=launch_source,
            idempotency_key=idempotency_key,
            actor_id=actor_id,
            labels=labels,
            subflow=subflow,
            priority=priority,
        )

    async def get_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedExecution:
        return await self._repository.get_execution(execution_id, tenant_id=tenant_id)

    async def list_executions(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> list[PersistedExecution]:
        return await self._repository.list_executions(tenant_id=tenant_id, limit=limit)

    async def list_recovery_candidates(
        self,
        *,
        tenant_id: str,
        updated_before: datetime,
        limit: int = 100,
    ) -> list[PersistedExecution]:
        return await self._repository.list_recovery_candidates(
            tenant_id=tenant_id,
            updated_before=updated_before,
            limit=limit,
        )

    async def complete_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
        outputs: dict[str, object] | None = None,
    ) -> PersistedExecution:
        return await self._repository.complete_execution(
            execution_id,
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
            outputs=outputs,
        )

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._repository.fail_execution(
            execution_id,
            reason,
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
        )

    async def record_execution_lifecycle(
        self,
        execution_id: UUID,
        evidence: dict[str, object],
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._repository.record_execution_lifecycle(
            execution_id,
            evidence,
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
        )

    async def database_time(self) -> datetime:
        return await self._repository.database_time()

    async def list_subflows(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedSubflow]:
        return await self._repository.list_subflows(execution_id, tenant_id=tenant_id)

    async def get_parent_subflow(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedSubflow | None:
        return await self._repository.get_parent_subflow(execution_id, tenant_id=tenant_id)


class PostgresTaskRunRepository(_PostgresExecutionPort, TaskRunRepository):
    """Task-run operations delegated to the compatibility repository."""

    async def list_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[PersistedTaskRun]:
        return await self._repository.list_task_runs(
            execution_id,
            tenant_id=tenant_id,
            include_iterations=include_iterations,
            limit=limit,
            offset=offset,
        )

    async def summarize_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
    ) -> PersistedTaskRunSummary:
        return await self._repository.summarize_task_runs(
            execution_id,
            tenant_id=tenant_id,
            include_iterations=include_iterations,
        )

    async def list_iteration_summaries(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedIterationSummary]:
        return await self._repository.list_iteration_summaries(
            execution_id,
            tenant_id=tenant_id,
        )

    async def ensure_iteration_task_runs(
        self,
        execution_id: UUID,
        iteration_key: str,
        task_ids: tuple[str, ...],
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]:
        return await self._repository.ensure_iteration_task_runs(
            execution_id,
            iteration_key,
            task_ids,
            tenant_id=tenant_id,
        )

    async def task_attempt_started_at(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
    ) -> datetime:
        return await self._repository.task_attempt_started_at(
            task_run_id,
            attempt,
            tenant_id=tenant_id,
        )

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
        priority: int = 0,
        worker_group: str | None = None,
    ) -> PersistedTaskRun:
        return await self._repository.start_task(
            task_run_id,
            tenant_id=tenant_id,
            dispatch=dispatch,
            priority=priority,
            worker_group=worker_group,
        )

    async def record_task_control(
        self,
        task_run_id: UUID,
        attempt: int,
        evidence: dict[str, object],
        *,
        tenant_id: str,
    ) -> PersistedTaskRun:
        return await self._repository.record_task_control(
            task_run_id,
            attempt,
            evidence,
            tenant_id=tenant_id,
        )

    async def skip_task(
        self,
        task_run_id: UUID,
        result: dict[str, Any],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        return await self._repository.skip_task(
            task_run_id,
            result,
            tenant_id=tenant_id,
            evidence=evidence,
        )

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, Any],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        return await self._repository.complete_task(
            task_run_id,
            attempt,
            result,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            evidence=evidence,
        )

    async def defer_task(
        self,
        task_run_id: UUID,
        attempt: int,
        resume_token: str,
        *,
        tenant_id: str,
        metadata: dict[str, object],
        expires_at: datetime | None = None,
    ) -> PersistedTaskDeferral:
        return await self._repository.defer_task(
            task_run_id,
            attempt,
            resume_token,
            tenant_id=tenant_id,
            metadata=metadata,
            expires_at=expires_at,
        )

    async def get_task_deferral(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedTaskDeferral | None:
        return await self._repository.get_task_deferral(task_run_id, tenant_id=tenant_id)

    async def resume_deferred_task(
        self,
        task_run_id: UUID,
        resume_token: str,
        result: dict[str, object],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        return await self._repository.resume_deferred_task(
            task_run_id,
            resume_token,
            result,
            tenant_id=tenant_id,
            evidence=evidence,
        )

    async def retry_task(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.RETRYABLE,
    ) -> PersistedTaskRun:
        return await self._repository.retry_task(
            task_run_id,
            attempt,
            tenant_id=tenant_id,
            retry_at=retry_at,
            reason=reason,
            worker_id=worker_id,
            fencing_token=fencing_token,
            failure_category=failure_category,
        )

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        result: dict[str, object] | None = None,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        return await self._repository.fail_task(
            task_run_id,
            attempt,
            reason,
            tenant_id=tenant_id,
            result=result,
            worker_id=worker_id,
            fencing_token=fencing_token,
            failure_category=failure_category,
            evidence=evidence,
        )

    async def cancel_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun:
        return await self._repository.cancel_task(
            task_run_id,
            attempt,
            reason,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
        )


class PostgresExecutionControlRepository(_PostgresExecutionPort, ExecutionControlRepository):
    """Execution-control operations delegated to the compatibility repository."""

    async def apply_execution_intervention(
        self,
        execution_id: UUID,
        action: ExecutionInterventionAction,
        *,
        tenant_id: str,
        expected_version: int,
        expected_epoch: int,
        actor_id: str,
        reason: str,
        grace_period: timedelta = timedelta(seconds=30),
        reset_task_ids: tuple[str, ...] = (),
        checkpoint_task_id: str | None = None,
        restart_timeout: timedelta | None = None,
    ) -> PersistedExecution:
        return await self._repository.apply_execution_intervention(
            execution_id,
            action,
            tenant_id=tenant_id,
            expected_version=expected_version,
            expected_epoch=expected_epoch,
            actor_id=actor_id,
            reason=reason,
            grace_period=grace_period,
            reset_task_ids=reset_task_ids,
            checkpoint_task_id=checkpoint_task_id,
            restart_timeout=restart_timeout,
        )

    async def list_execution_interventions(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionInterventionRecord]:
        return await self._repository.list_execution_interventions(
            execution_id,
            tenant_id=tenant_id,
        )

    async def timeout_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._repository.timeout_execution(
            execution_id,
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
        )


def build_execution_repository_ports(
    repository: PostgresExecutionRepository,
) -> ExecutionRepositoryPorts:
    """Build one immutable set of responsibility-specific views."""

    return ExecutionRepositoryPorts(
        flow_registry=PostgresFlowRegistryRepository(repository),
        admission=PostgresAdmissionRepository(repository),
        lifecycle=PostgresExecutionLifecycleRepository(repository),
        task_runs=PostgresTaskRunRepository(repository),
        control=PostgresExecutionControlRepository(repository),
    )


__all__ = [
    "PostgresAdmissionRepository",
    "PostgresExecutionControlRepository",
    "PostgresExecutionLifecycleRepository",
    "PostgresFlowRegistryRepository",
    "PostgresTaskRunRepository",
]
