from __future__ import annotations

import pytest
from pydantic import ValidationError

from amesh.domain import TenantDefinition, TenantPolicy, tenant_storage_key


def test_tenant_policy_and_storage_prefix_are_typed_and_isolated() -> None:
    tenant = TenantDefinition(
        slug="acme",
        display_name="Acme",
        policy=TenantPolicy(
            plugin_allowlist=("core.http",),
            worker_groups=("regulated",),
            feature_flags={"executions": False},
        ),
    )

    assert tenant.storage_prefix == "tenants/acme/"
    assert tenant_storage_key(tenant, "/artifacts/result.json") == (
        "tenants/acme/artifacts/result.json"
    )
    assert tenant.policy.allows_plugin("core.http")
    assert not tenant.policy.allows_plugin("agent.llm")
    assert not tenant.policy.feature_enabled("executions")


def test_tenant_contract_rejects_arbitrary_prefixes_and_traversal() -> None:
    with pytest.raises(ValidationError):
        TenantDefinition(
            slug="acme",
            display_name="Acme",
            storage_prefix="tenants/another/",
        )
    with pytest.raises(ValueError):
        tenant_storage_key(TenantDefinition(slug="acme", display_name="Acme"), "../secret")
