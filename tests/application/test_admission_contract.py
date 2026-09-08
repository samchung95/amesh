from __future__ import annotations

import pytest
from pydantic import ValidationError

from amesh.domain import (
    AdmissionBehavior,
    AdmissionResourceType,
    AdmissionScope,
    ConcurrencyLimit,
    resolve_admission_policies,
)


def test_concurrency_contract_resolves_every_scope_and_dynamic_key() -> None:
    policies = tuple(
        ConcurrencyLimit(
            id=f"scope-{scope.value.lower()}",
            scope=scope,
            limit=2,
            behavior=AdmissionBehavior.QUEUE,
            key="{{ inputs.customer }}" if scope is AdmissionScope.KEY else None,
            workerGroup="gpu" if scope is AdmissionScope.WORKER_GROUP else None,
        )
        for scope in AdmissionScope
    )

    resolved = resolve_admission_policies(
        policies,
        resource_type=AdmissionResourceType.TASK,
        tenant_id="tenant-a",
        namespace="company.team",
        flow_id="orders",
        render_key=lambda value: "customer-42" if value else value,
    )

    assert {item.scope for item in resolved} == set(AdmissionScope)
    assert next(item for item in resolved if item.scope is AdmissionScope.KEY).bucket == (
        "TASK:KEY:tenant-a/customer-42"
    )
    assert (
        next(item for item in resolved if item.scope is AdmissionScope.WORKER_GROUP).bucket
        == "TASK:WORKER_GROUP:tenant-a/gpu"
    )


def test_concurrency_contract_rejects_unsafe_or_incomplete_selectors() -> None:
    with pytest.raises(ValidationError, match="requires key"):
        ConcurrencyLimit(id="missing-key", scope=AdmissionScope.KEY, limit=1)
    with pytest.raises(ValidationError, match="not allowed at GLOBAL"):
        ConcurrencyLimit(
            id="global-replace",
            scope=AdmissionScope.GLOBAL,
            limit=1,
            behavior=AdmissionBehavior.REPLACE,
        )
    policy = ConcurrencyLimit(
        id="dynamic",
        scope=AdmissionScope.KEY,
        limit=1,
        key="{{ inputs.customer }}",
    )
    with pytest.raises(ValueError, match="scalar"):
        resolve_admission_policies(
            (policy,),
            resource_type=AdmissionResourceType.EXECUTION,
            tenant_id="tenant-a",
            namespace="company.team",
            flow_id="orders",
            render_key=lambda _value: {"unsafe": "compound"},
        )
