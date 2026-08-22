from __future__ import annotations

import pytest

from amesh.domain import (
    FeatureFlag,
    FeatureFlagScope,
    resolve_feature_flag,
)


def _flag(
    scope: FeatureFlagScope,
    enabled: bool,
    *,
    tenant: str | None = None,
    namespace: str | None = None,
) -> FeatureFlag:
    return FeatureFlag(
        key="new-engine",
        scope=scope,
        enabled=enabled,
        tenant_id=tenant,
        namespace=namespace,
        updated_by="test",
    )


def test_namespace_tenant_instance_and_default_precedence() -> None:
    flags = (
        _flag(FeatureFlagScope.INSTANCE, False),
        _flag(FeatureFlagScope.TENANT, True, tenant="alpha"),
        _flag(
            FeatureFlagScope.NAMESPACE,
            False,
            tenant="alpha",
            namespace="finance.payments",
        ),
    )

    namespace = resolve_feature_flag("new-engine", flags, default=True)
    tenant = resolve_feature_flag("new-engine", flags[:2], default=False)
    instance = resolve_feature_flag("new-engine", flags[:1], default=True)
    fallback = resolve_feature_flag("unknown", flags, default=True)

    assert (namespace.enabled, namespace.reason) == (False, "NAMESPACE_MATCH")
    assert (tenant.enabled, tenant.reason) == (True, "TENANT_MATCH")
    assert (instance.enabled, instance.reason) == (False, "INSTANCE_MATCH")
    assert (fallback.enabled, fallback.reason, fallback.matched_scope) == (True, "DEFAULT", None)


def test_feature_flag_scope_contract_rejects_contradictory_identifiers() -> None:
    with pytest.raises(ValueError, match="instance feature flag"):
        _flag(FeatureFlagScope.INSTANCE, True, tenant="alpha")
    with pytest.raises(ValueError, match="requires only tenant_id"):
        _flag(FeatureFlagScope.TENANT, True)
    with pytest.raises(ValueError, match="requires tenant_id and namespace"):
        _flag(FeatureFlagScope.NAMESPACE, True, tenant="alpha")
