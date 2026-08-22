from __future__ import annotations

from datetime import UTC, datetime

import pytest

from amesh.dsl import FlowDefinition, PluginDefaultDefinition
from amesh.workflow import (
    NamespaceWorkflowMetadata,
    WorkflowMetadataPolicy,
    resolve_flow_metadata,
)


def scope(
    namespace: str,
    *defaults: PluginDefaultDefinition,
    policy: WorkflowMetadataPolicy | None = None,
) -> NamespaceWorkflowMetadata:
    now = datetime.now(UTC)
    return NamespaceWorkflowMetadata(
        tenantId="default",
        namespace=namespace,
        pluginDefaults=defaults,
        policy=policy or WorkflowMetadataPolicy(),
        resourceVersion=1,
        createdBy="test",
        updatedBy="test",
        createdAt=now,
        updatedAt=now,
    )


def test_namespace_defaults_merge_with_deterministic_forced_precedence_and_origins() -> None:
    parent = scope(
        "company",
        PluginDefaultDefinition(
            type="core.return",
            values={"resources": {"limit": {"cpu": "1", "memory": "128Mi"}}},
        ),
        PluginDefaultDefinition(
            type="core.return",
            values={"workerGroup": "root-secure"},
            forced=True,
        ),
        policy=WorkflowMetadataPolicy(
            requiredLabels={"team": "platform"},
            normalizeLabels={"environment": "LOWERCASE"},
            requiredDefaults={"core.return": ["resources.limit.cpu"]},
            normalizeDefaults={"core.return": {"region": "LOWERCASE"}},
        ),
    )
    child = scope(
        "company.data",
        PluginDefaultDefinition(
            type="core.return",
            values={"resources": {"limit": {"memory": "256Mi"}}, "region": "APAC"},
        ),
        PluginDefaultDefinition(
            type="core.return",
            values={"workerGroup": "child-secure"},
            forced=True,
        ),
    )
    flow = FlowDefinition.model_validate(
        {
            "id": "metadata",
            "namespace": "company.data.jobs",
            "labels": {"team": "platform", "environment": "PROD"},
            "pluginDefaults": [
                {"type": "core.return", "values": {"timeoutSeconds": 30}},
                {
                    "type": "core.return",
                    "values": {"workerGroup": "flow-secure"},
                    "forced": True,
                },
            ],
            "tasks": [
                {
                    "id": "work",
                    "type": "core.return",
                    "timeoutSeconds": 5,
                    "resources": {"limit": {"memory": "512Mi"}},
                    "value": "ok",
                },
                {"id": "other", "type": "core.log", "message": "unchanged"},
            ],
        }
    )

    resolved, evidence = resolve_flow_metadata(flow, [child, parent])

    work = resolved.tasks[0]
    assert resolved.labels == {"team": "platform", "environment": "prod"}
    assert work.timeout_seconds == 5
    assert work.worker_group == "root-secure"
    assert work.resources == {
        "limit": {"cpu": "1", "memory": "512Mi"},
    }
    assert work.model_extra == {"value": "ok", "region": "apac"}
    assert resolved.tasks[1].model_extra == {"message": "unchanged"}
    task_evidence = evidence["tasks"]["tasks.work"]
    assert task_evidence["origins"]["timeoutSeconds"]["source"] == "task"
    assert task_evidence["origins"]["workerGroup"]["namespace"] == "company"
    assert task_evidence["origins"]["region"]["namespace"] == "company.data"
    assert evidence["namespaceLineage"] == ["company", "company.data"]


def test_metadata_policy_and_protected_prefixes_fail_before_resolution() -> None:
    required = scope(
        "company",
        policy=WorkflowMetadataPolicy(
            requiredLabels={"team": None},
            deniedLabels=["forbidden"],
            requiredDefaults={"core.return": ["region"]},
        ),
    )
    missing = FlowDefinition.model_validate(
        {
            "id": "missing",
            "namespace": "company.data",
            "labels": {"team": "platform"},
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
        }
    )
    with pytest.raises(ValueError, match="required by namespace policy"):
        resolve_flow_metadata(missing, [required])
    with pytest.raises(ValueError, match="protected system prefix"):
        FlowDefinition.model_validate(
            {
                "id": "spoofed",
                "namespace": "company.data",
                "labels": {"amesh.flow.id": "spoofed"},
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
