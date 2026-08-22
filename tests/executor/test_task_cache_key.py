from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, validate_flow_document
from amesh.executor import TaskExecutionContext
from amesh.executor.service import derive_task_cache_key
from amesh.ports import PersistedExecution


def _flow(*, revision: int = 1, code_version: str = "plugin:1") -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "cached",
            "namespace": "tests.cache",
            "revision": revision,
            "inputs": [{"id": "value", "type": "STRING", "default": "default"}],
            "tasks": [
                {
                    "id": "result",
                    "type": "test.cached",
                    "value": "{{ inputs.value }}",
                    "taskCache": {
                        "enabled": True,
                        "ttl": "PT1H",
                        "namespace": "acceptance",
                        "scope": "TASK",
                        "invalidationPolicy": "TTL_AND_REVISION",
                        "keyContext": ["inputs", "variables"],
                        "codeVersion": code_version,
                    },
                }
            ],
        }
    )


def _execution(tenant_id: str = "default") -> PersistedExecution:
    now = datetime.now(UTC)
    return PersistedExecution(
        execution_id=uuid4(),
        tenant_id=tenant_id,
        state=ExecutionState.RUNNING,
        epoch=1,
        version=1,
        namespace="tests.cache",
        flow_id="cached",
        flow_revision=1,
        inputs={"value": "alpha"},
        labels={},
        trigger={},
        created_at=now,
        updated_at=now,
    )


def _context(execution: PersistedExecution, secret: str) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id=execution.tenant_id,
        execution_id=execution.execution_id,
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs=execution.inputs,
        outputs={},
        variables={},
        secret_scopes=("service",),
        secrets={"service": secret},
    )


def test_cache_key_is_deterministic_and_fenced_by_revision_code_tenant_and_security() -> None:
    flow = _flow()
    execution = _execution()
    task = flow.tasks[0]
    first = derive_task_cache_key(flow, execution, task, _context(execution, "secret-a"))
    repeated = derive_task_cache_key(flow, execution, task, _context(execution, "secret-a"))

    assert first.key_hash == repeated.key_hash
    assert first.key_prefix == "acceptance/tests.cache/cached/result"
    assert first.security_context_hash == repeated.security_context_hash

    changed_revision = _flow(revision=2)
    changed_code = _flow(code_version="plugin:2")
    other_tenant = _execution("tenant-b")
    assert (
        derive_task_cache_key(
            changed_revision, execution, changed_revision.tasks[0], _context(execution, "secret-a")
        ).key_hash
        != first.key_hash
    )
    assert (
        derive_task_cache_key(
            changed_code, execution, changed_code.tasks[0], _context(execution, "secret-a")
        ).key_hash
        != first.key_hash
    )
    assert (
        derive_task_cache_key(flow, other_tenant, task, _context(other_tenant, "secret-a")).key_hash
        != first.key_hash
    )
    assert (
        derive_task_cache_key(flow, execution, task, _context(execution, "secret-b")).key_hash
        != first.key_hash
    )


def test_enabled_cache_requires_ttl_and_flowables_cannot_be_cached() -> None:
    with pytest.raises(ValidationError, match="positive ttl"):
        FlowDefinition.model_validate(
            {
                "id": "missing_ttl",
                "namespace": "tests.cache",
                "tasks": [
                    {
                        "id": "result",
                        "type": "core.return",
                        "taskCache": {"enabled": True},
                    }
                ],
            }
        )
    with pytest.raises(ValidationError, match="runnable tasks"):
        FlowDefinition.model_validate(
            {
                "id": "flowable",
                "namespace": "tests.cache",
                "tasks": [
                    {
                        "id": "sequence",
                        "type": "core.sequential",
                        "taskCache": {"enabled": True, "ttl": "PT1H"},
                        "tasks": [{"id": "done", "type": "core.return"}],
                    }
                ],
            }
        )


def test_kestra_task_cache_fields_survive_canonical_validation() -> None:
    result = validate_flow_document(
        """id: cached
namespace: tests.cache
tasks:
  - id: result
    type: core.return
    value: ok
    taskCache:
      enabled: true
      ttl: PT1H
"""
    )

    assert result.valid
    assert result.canonical is not None
    assert result.canonical["tasks"][0]["taskCache"] == {
        "enabled": True,
        "ttl": "PT1H",
        "scope": "TASK",
        "invalidationPolicy": "TTL_AND_REVISION",
        "keyContext": ["inputs", "variables", "labels", "trigger", "iteration"],
    }
