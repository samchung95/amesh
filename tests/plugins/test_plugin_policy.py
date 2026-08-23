from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain.plugin_policy import (
    PluginPolicyEffect,
    PluginPolicyRule,
    PluginPolicyRuleCreate,
    PluginPolicyScope,
    PluginPolicySelector,
    PluginPolicyStage,
    PluginPolicySubject,
    PluginQuarantine,
    evaluate_plugin_policy,
)


def _subject() -> PluginPolicySubject:
    return PluginPolicySubject(
        package="vendor.analytics",
        version="1.4.2",
        vendor="Example Corp",
        pluginTypes=("task:vendor.query",),
        capabilities=("network:restricted", "secret:warehouse"),
    )


def _rule(
    effect: PluginPolicyEffect,
    *,
    stage: PluginPolicyStage = PluginPolicyStage.EXECUTION,
) -> PluginPolicyRule:
    return PluginPolicyRule(
        id=uuid4(),
        tenantId="default",
        scope=PluginPolicyScope.TENANT,
        effect=effect,
        stages=(stage,),
        selector=PluginPolicySelector(
            package="vendor.*",
            versionRange=">=1.0.0,<2.0.0",
            vendor="Example *",
            pluginTypes=("task:vendor.query",),
            capabilities=("secret:warehouse",),
        ),
        reason=f"test {effect.value.lower()}",
        createdBy="tester",
        updatedBy="tester",
    )


def test_explicit_deny_overrides_allow_and_reports_every_source() -> None:
    decision = evaluate_plugin_policy(
        (_subject(),),
        (_rule(PluginPolicyEffect.ALLOW), _rule(PluginPolicyEffect.DENY)),
        (),
        tenant_id="default",
        namespace="analytics",
        stage=PluginPolicyStage.EXECUTION,
        default_allow=False,
    )

    assert decision.allowed is False
    assert decision.subjects[0].reason_code == "EXPLICIT_DENY"
    assert decision.subjects[0].sources[0].effect is PluginPolicyEffect.DENY
    assert decision.subjects[0].sources[0].source_id


def test_stages_are_independent_and_secure_default_is_fail_closed() -> None:
    validation = evaluate_plugin_policy(
        (_subject(),),
        (_rule(PluginPolicyEffect.ALLOW, stage=PluginPolicyStage.VALIDATION),),
        (),
        tenant_id="default",
        namespace="analytics",
        stage=PluginPolicyStage.VALIDATION,
        default_allow=False,
    )
    execution = evaluate_plugin_policy(
        (_subject(),),
        (_rule(PluginPolicyEffect.ALLOW, stage=PluginPolicyStage.VALIDATION),),
        (),
        tenant_id="default",
        namespace="analytics",
        stage=PluginPolicyStage.EXECUTION,
        default_allow=False,
    )

    assert validation.allowed is True
    assert execution.allowed is False
    assert execution.subjects[0].sources[0].source_id == "secure-default"


def test_quarantine_is_an_emergency_deny_and_core_is_otherwise_allowed() -> None:
    core = PluginPolicySubject(
        package="amesh.core",
        version="1.0.0",
        vendor="AMESH",
    )
    baseline = evaluate_plugin_policy(
        (core,),
        (),
        (),
        tenant_id="default",
        namespace="core",
        stage=PluginPolicyStage.EXECUTION,
        default_allow=False,
    )
    quarantine = PluginQuarantine(
        id=uuid4(),
        scope=PluginPolicyScope.INSTANCE,
        package="amesh.core",
        version="1.0.0",
        reason="security incident",
        createdBy="operator",
    )
    blocked = evaluate_plugin_policy(
        (core,),
        (),
        (quarantine,),
        tenant_id="default",
        namespace="core",
        stage=PluginPolicyStage.EXECUTION,
        default_allow=False,
    )

    assert baseline.allowed is True
    assert blocked.allowed is False
    assert blocked.subjects[0].reason_code == "PLUGIN_QUARANTINED"


def test_namespace_scope_and_semver_selectors_are_validated() -> None:
    with pytest.raises(ValidationError, match="namespace is required"):
        PluginPolicyRuleCreate(
            scope=PluginPolicyScope.NAMESPACE,
            effect=PluginPolicyEffect.ALLOW,
            stages=(PluginPolicyStage.AUTHORING,),
            reason="invalid missing namespace",
        )
    with pytest.raises(ValidationError, match="semantic-version range"):
        PluginPolicySelector(versionRange="not semver")
