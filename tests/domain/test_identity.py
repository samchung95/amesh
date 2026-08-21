from __future__ import annotations

import pytest
from pydantic import ValidationError

from amesh.domain import (
    AssetKey,
    FlowKey,
    FlowRevisionKey,
    NamespaceKey,
    PluginKey,
    RuntimeIdentity,
    RuntimeResourceType,
    TaskRunKey,
    TenantKey,
    TriggerKey,
    WorkerKey,
    new_runtime_id,
)


def test_runtime_ids_are_uuid7_and_sort_in_generation_order() -> None:
    values = [new_runtime_id() for _ in range(20)]

    assert all(value.version == 7 for value in values)
    assert values == sorted(values)


def test_canonical_natural_keys_cover_platform_resources() -> None:
    tenant = TenantKey(slug="default")
    namespace = NamespaceKey(tenant=tenant.slug, namespace="company.team")
    flow = FlowKey(tenant=tenant.slug, namespace=namespace.namespace, flow_id="daily_sync")
    revision = FlowRevisionKey(flow=flow, revision=3)
    runtime = RuntimeIdentity(resource_type=RuntimeResourceType.EXECUTION)

    assert revision.flow == flow
    assert runtime.id.version == 7
    assert TaskRunKey(execution_id=runtime.id, task_path="extract").task_path == "extract"
    assert TriggerKey(flow=flow, trigger_id="hourly").trigger_id == "hourly"
    assert (
        WorkerKey(worker_group="kubernetes", instance_name="worker-1").worker_group == "kubernetes"
    )
    assert (
        PluginKey(
            name="io.amesh.core",
            version="1.0.0",
            digest="sha256:" + "a" * 64,
        ).name
        == "io.amesh.core"
    )
    assert AssetKey(tenant="default", provider="s3", external_key="bucket/key").provider == "s3"


def test_identifier_policy_is_consistent_and_case_preserving() -> None:
    assert FlowKey(tenant="default", namespace="Company.Team", flow_id="DailySync").flow_id == (
        "DailySync"
    )

    invalid_values = (
        {"tenant": "Default", "namespace": "company.team", "flow_id": "flow"},
        {"tenant": "default", "namespace": "company..team", "flow_id": "flow"},
        {"tenant": "default", "namespace": "company.team", "flow_id": "bad value"},
        {"tenant": "default", "namespace": "company.team", "flow_id": "_amesh_internal"},
    )
    for value in invalid_values:
        try:
            FlowKey.model_validate(value)
        except ValidationError:
            continue
        raise AssertionError(f"expected invalid identifier: {value}")


def test_identifier_length_limits_are_enforced_at_the_boundary() -> None:
    assert FlowKey(tenant="default", namespace="company", flow_id="a" * 128).flow_id == ("a" * 128)
    with pytest.raises(ValidationError):
        FlowKey(tenant="default", namespace="company", flow_id="a" * 129)
