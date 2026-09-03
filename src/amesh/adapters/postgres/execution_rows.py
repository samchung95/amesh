"""Leaf row mappers shared by PostgreSQL execution repository facets."""

from __future__ import annotations

from sqlalchemy.engine import RowMapping

from amesh.domain import (
    AdmissionDecision,
    AdmissionScope,
    FlowRevisionRecord,
    ResourceMetadata,
    TaskRunLifecyclePhase,
    resource_etag,
)
from amesh.ports.execution_repository import (
    PersistedExecution,
    PersistedFlow,
    PersistedFlowRevision,
    PersistedSubflow,
    PersistedTaskDeferral,
    PersistedTaskRun,
    SubflowPropagation,
)
from amesh.ports.repository_support import JsonCodec


def execution_from_row(row: RowMapping) -> PersistedExecution:
    return PersistedExecution(
        execution_id=row["id"],
        tenant_id=row["tenant_slug"],
        state=row["state"],
        epoch=row["epoch"],
        version=row["version"],
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        flow_revision=row["flow_revision"],
        inputs=row["inputs"],
        outputs=row["outputs"],
        labels=row["labels"],
        trigger=row["trigger_context"],
        created_by=row["created_by"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        timeout_at=row["timeout_at"],
        cancel_deadline_at=row["cancel_deadline_at"],
        lifecycle_evidence=row.get("lifecycle_evidence") or {},
    )


def subflow_from_row(row: RowMapping) -> PersistedSubflow:
    return PersistedSubflow(
        relationship_id=row["id"],
        parent_execution_id=row["parent_execution_id"],
        parent_task_run_id=row["parent_task_run_id"],
        parent_attempt=row["parent_attempt"],
        child_execution_id=row["child_execution_id"],
        invocation_key=row["invocation_key"],
        mode=row["mode"],
        depth=row["depth"],
        target_revision=row["target_revision"],
        propagation=SubflowPropagation.model_validate(row["propagation"]),
        output_mapping=row["output_mapping"],
        parent_namespace=row["parent_namespace"],
        parent_flow_id=row["parent_flow_id"],
        parent_flow_revision=row["parent_flow_revision"],
        child_namespace=row["child_namespace"],
        child_flow_id=row["child_flow_id"],
        child_state=row["child_state"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def flow_from_row(row: RowMapping) -> PersistedFlow:
    created_at = row["created_at"]
    updated_at = max(created_at, row["updated_at"])
    metadata = ResourceMetadata(
        labels=row["labels"],
        annotations=row["annotations"],
        created_at=created_at,
        updated_at=updated_at,
        created_by=row["created_by"],
        updated_by=row["updated_by"],
        resource_version=row["version"],
        lifecycle=row["lifecycle"],
        archived_at=row["archived_at"],
        deleted_at=row["deleted_at"],
    )
    representation = {
        "resourceId": str(row["id"]),
        "tenantId": row["tenant_slug"],
        "namespace": row["namespace"],
        "flowId": row["flow_key"],
        "revision": row["revision"],
        "semanticHash": row["semantic_hash"],
        "metadata": metadata.model_dump(mode="json", exclude_none=True),
    }
    return PersistedFlow(
        resource_id=row["id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        revision=row["revision"],
        semantic_hash=row["semantic_hash"],
        lifecycle=row["status"],
        metadata=metadata,
        etag=resource_etag(representation),
    )


def flow_revision_from_row(row: RowMapping) -> FlowRevisionRecord:
    return FlowRevisionRecord(
        resource_id=row["id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        revision=row["revision"],
        semantic_hash=row["semantic_hash"],
        plugin_resolution=row["plugin_resolution"],
        source=row["source"],
        source_commit=row["source_commit"],
        environment=row["environment"],
        deployment=row["deployment_metadata"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def persisted_flow_revision_from_row(
    row: RowMapping,
    codec: JsonCodec,
) -> PersistedFlowRevision:
    canonical_definition = row["canonical_definition"]
    plugin_resolution = row["plugin_resolution"]
    if not isinstance(canonical_definition, dict):
        raise TypeError("persisted flow revision definition must be a JSON object")
    if not isinstance(plugin_resolution, dict):
        raise TypeError("persisted flow revision plugin resolution must be a JSON object")
    return PersistedFlowRevision(
        resource_id=row["id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        revision=row["revision"],
        semantic_hash=row["semantic_hash"],
        canonical_definition_json=codec.dumps(canonical_definition, canonical=True),
        plugin_resolution_json=codec.dumps(plugin_resolution, canonical=True),
    )


def task_run_from_row(row: RowMapping) -> PersistedTaskRun:
    return PersistedTaskRun(
        task_run_id=row["id"],
        execution_id=row["execution_id"],
        task_id=row["task_path"],
        iteration_key=row.get("iteration_key"),
        state=row["state"],
        current_attempt=row["current_attempt"],
        version=row["version"],
        retry_at=row["retry_at"],
        result=row["result"],
        failure_category=row["failure_category"],
        evidence=row.get("evidence") or {},
        lifecycle_phase=row.get("lifecycle_phase") or TaskRunLifecyclePhase.MAIN,
        labels=dict(row.get("labels") or {}),
    )


def task_deferral_from_row(row: RowMapping) -> PersistedTaskDeferral:
    return PersistedTaskDeferral(
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        state=row["state"],
        metadata=row["metadata"],
        expires_at=row["expires_at"],
        deferred_at=row["deferred_at"],
        resumed_at=row["resumed_at"],
    )


def admission_decision_from_row(row: RowMapping) -> AdmissionDecision:
    limiting_scope = row["limiting_scope"]
    return AdmissionDecision(
        request_id=row["request_id"],
        resource_type=row["resource_type"],
        resource_id=row["resource_id"],
        outcome=row["outcome"],
        reason=row["reason"],
        limiting_policy_id=row["limiting_policy_id"],
        limiting_scope=AdmissionScope(limiting_scope) if limiting_scope else None,
        limiting_bucket=row["limiting_bucket"],
        active_count=row["active_count"],
        limit=row["limit_value"],
        queue_position=row.get("queue_position"),
        queue_age_seconds=float(row.get("queue_age_seconds") or 0),
        priority=row["priority"],
        created_at=row["created_at"],
        admitted_at=row["admitted_at"],
        released_at=row["finished_at"],
        replaced_resource_id=row["replaced_resource_id"],
    )


__all__ = [
    "admission_decision_from_row",
    "execution_from_row",
    "flow_from_row",
    "flow_revision_from_row",
    "persisted_flow_revision_from_row",
    "subflow_from_row",
    "task_deferral_from_row",
    "task_run_from_row",
]
