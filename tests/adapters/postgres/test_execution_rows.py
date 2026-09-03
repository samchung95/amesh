from __future__ import annotations

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from sqlalchemy.engine import RowMapping

from amesh.adapters.postgres.execution_rows import (
    admission_decision_from_row,
    execution_from_row,
    flow_from_row,
    flow_revision_from_row,
    subflow_from_row,
    task_deferral_from_row,
    task_run_from_row,
)
from amesh.domain import AdmissionOutcome, ExecutionState, FlowLifecycle, TaskRunState

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
RESOURCE_ID = UUID("00000000-0000-0000-0000-000000000002")
EXECUTION_ID = UUID("00000000-0000-0000-0000-000000000003")
TASK_RUN_ID = UUID("00000000-0000-0000-0000-000000000004")


def _row(**values: object) -> RowMapping:
    return cast(RowMapping, values)


def test_execution_row_mapper_preserves_the_persisted_contract() -> None:
    execution = execution_from_row(
        _row(
            id=EXECUTION_ID,
            tenant_slug="default",
            state="RUNNING",
            epoch=2,
            version=3,
            namespace_name="orders",
            flow_key="ingest",
            flow_revision=4,
            inputs={"input": True},
            outputs={"output": 1},
            labels={"team": "platform"},
            trigger_context={"type": "api"},
            created_by="user:test",
            created_at=NOW,
            updated_at=NOW,
            timeout_at=None,
            cancel_deadline_at=None,
            lifecycle_evidence={"phase": "main"},
        )
    )

    assert execution.model_dump(mode="json") == {
        "execution_id": str(EXECUTION_ID),
        "tenant_id": "default",
        "state": ExecutionState.RUNNING,
        "epoch": 2,
        "version": 3,
        "namespace": "orders",
        "flow_id": "ingest",
        "flow_revision": 4,
        "inputs": {"input": True},
        "outputs": {"output": 1},
        "labels": {"team": "platform"},
        "trigger": {"type": "api"},
        "created_by": "user:test",
        "created_at": NOW.isoformat().replace("+00:00", "Z"),
        "updated_at": NOW.isoformat().replace("+00:00", "Z"),
        "timeout_at": None,
        "cancel_deadline_at": None,
        "lifecycle_evidence": {"phase": "main"},
    }


def test_flow_and_revision_row_mappers_preserve_resource_metadata() -> None:
    row = _row(
        id=RESOURCE_ID,
        tenant_slug="default",
        namespace="orders",
        flow_key="ingest",
        revision=4,
        semantic_hash="sha256:flow",
        labels={"team": "platform"},
        annotations={"owner": "ops"},
        created_at=NOW,
        updated_at=NOW,
        created_by="user:create",
        updated_by="user:update",
        version=7,
        lifecycle="ACTIVE",
        status="ACTIVE",
        archived_at=None,
        deleted_at=None,
        plugin_resolution={"catalog": "v1"},
        source="GIT",
        source_commit="abc123",
        environment="prod",
        deployment_metadata={"region": "sg"},
    )

    flow = flow_from_row(row)
    revision = flow_revision_from_row(row)

    assert flow.resource_id == RESOURCE_ID
    assert flow.lifecycle is FlowLifecycle.ACTIVE
    assert flow.metadata.resource_version == 7
    assert flow.metadata.labels == {"team": "platform"}
    assert flow.etag.startswith('"sha256:')
    assert revision.resource_id == RESOURCE_ID
    assert revision.plugin_resolution == {"catalog": "v1"}
    assert revision.deployment == {"region": "sg"}


def test_task_and_deferral_row_mappers_preserve_attempt_state() -> None:
    task = task_run_from_row(
        _row(
            id=TASK_RUN_ID,
            execution_id=EXECUTION_ID,
            task_path="extract",
            iteration_key="items:0",
            state="RUNNING",
            current_attempt=2,
            version=5,
            retry_at=None,
            result={"value": 1},
            failure_category=None,
            evidence={"trace": "ok"},
            lifecycle_phase="MAIN",
            labels={"kind": "reader"},
        )
    )
    deferral = task_deferral_from_row(
        _row(
            task_run_id=TASK_RUN_ID,
            attempt=2,
            state="DEFERRED",
            metadata={"approval": "required"},
            expires_at=None,
            deferred_at=NOW,
            resumed_at=None,
        )
    )

    assert task.state is TaskRunState.RUNNING
    assert task.iteration_key == "items:0"
    assert task.evidence == {"trace": "ok"}
    assert deferral.task_run_id == TASK_RUN_ID
    assert deferral.metadata == {"approval": "required"}


def test_subflow_and_admission_row_mappers_preserve_relationships() -> None:
    parent_task_run_id = TASK_RUN_ID
    child_execution_id = UUID("00000000-0000-0000-0000-000000000005")
    relationship = subflow_from_row(
        _row(
            id=RESOURCE_ID,
            parent_execution_id=EXECUTION_ID,
            parent_task_run_id=parent_task_run_id,
            parent_attempt=1,
            child_execution_id=child_execution_id,
            invocation_key="child:one",
            mode="SYNC",
            depth=1,
            target_revision=2,
            propagation={"success": True, "failure": False},
            output_mapping={"result": "child.result"},
            parent_namespace="orders",
            parent_flow_id="parent",
            parent_flow_revision=3,
            child_namespace="orders",
            child_flow_id="child",
            child_state="RUNNING",
            created_by="user:test",
            created_at=NOW,
        )
    )
    decision = admission_decision_from_row(
        _row(
            request_id=RESOURCE_ID,
            resource_type="EXECUTION",
            resource_id=EXECUTION_ID,
            outcome="ADMITTED",
            reason="capacity available",
            limiting_policy_id=None,
            limiting_scope=None,
            limiting_bucket=None,
            active_count=1,
            limit_value=2,
            queue_position=None,
            queue_age_seconds=0,
            priority=3,
            created_at=NOW,
            admitted_at=NOW,
            finished_at=None,
            replaced_resource_id=None,
        )
    )

    assert relationship.child_execution_id == child_execution_id
    assert relationship.propagation.failure is False
    assert relationship.output_mapping == {"result": "child.result"}
    assert decision.outcome is AdmissionOutcome.ADMITTED
    assert decision.resource_id == EXECUTION_ID
    assert decision.priority == 3
