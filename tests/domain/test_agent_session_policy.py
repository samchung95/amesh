from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain import (
    AgentSessionPolicy,
    AgentSessionPolicyRevision,
    evaluate_agent_session_policies,
)


def _policy() -> AgentSessionPolicy:
    return AgentSessionPolicy(
        admissionEnabled=True,
        maxConcurrency=8,
        maxTotalTokens=100_000,
        maxCostUsd=Decimal("12.50"),
        maxDurationSeconds=3_600,
        retentionSeconds=86_400,
        allowedProviderIds=("openai", "anthropic"),
        allowedHarnessIds=("pi",),
        allowedToolIds=("search", "write"),
    )


def test_session_policy_is_deterministically_digested_and_alias_serialized() -> None:
    policy = _policy()

    assert policy.digest.startswith("sha256:")
    assert policy.digest == _policy().digest
    assert policy.model_dump(by_alias=True)["maxTotalTokens"] == 100_000
    assert policy.model_dump(by_alias=True)["allowedProviderIds"] == ("openai", "anthropic")


@pytest.mark.parametrize(
    "field, value",
    [
        ("maxConcurrency", 0),
        ("maxTotalTokens", 0),
        ("maxDurationSeconds", 0),
        ("retentionSeconds", -1),
        ("allowedToolIds", ("search", "search")),
    ],
)
def test_session_policy_rejects_unsafe_values(field: str, value: object) -> None:
    values = _policy().model_dump(by_alias=True)
    values[field] = value

    with pytest.raises(ValidationError):
        AgentSessionPolicy.model_validate(values)


def test_session_policy_revision_requires_matching_digest() -> None:
    policy = _policy()

    revision = AgentSessionPolicyRevision(
        policyId=uuid4(),
        tenantId="tenant-a",
        namespace="research",
        revision=1,
        spec=policy,
        digest=policy.digest,
        createdBy="admin",
        createdAt="2026-08-30T00:00:00Z",
    )

    assert revision.policy == policy
    with pytest.raises(ValidationError, match="digest"):
        AgentSessionPolicyRevision.model_validate(
            revision.model_dump(by_alias=True) | {"digest": "sha256:" + "0" * 64}
        )


def _revision(
    policy: AgentSessionPolicy,
    revision: int,
    *,
    namespace: str | None = None,
    application_id: str | None = None,
):
    return AgentSessionPolicyRevision(
        tenantId="tenant-a",
        namespace=namespace,
        applicationId=application_id,
        revision=revision,
        spec=policy,
        digest=policy.digest,
        createdBy="admin",
        createdAt="2026-08-30T00:00:00Z",
    )


def test_cumulative_policy_precedence_caps_concurrency_and_records_provenance() -> None:
    tenant = _policy().model_copy(update={"max_concurrency": 8, "retention_seconds": 100})
    namespace = _policy().model_copy(update={"max_concurrency": 4, "retention_seconds": 50})
    application = _policy().model_copy(update={"max_concurrency": 2, "retention_seconds": 25})

    result = evaluate_agent_session_policies(
        (
            _revision(tenant, 1),
            _revision(namespace, 1, namespace="research"),
            _revision(application, 1, namespace="research", application_id="app-a"),
        ),
        envelope_max_total_tokens=100_000,
        envelope_max_cost_usd=Decimal("5"),
        envelope_max_duration_seconds=1_800,
        envelope_max_concurrency=10,
        requested_timeout_seconds=1_000,
        provider_ids=("openai", "anthropic"),
        harness_id="pi",
        tool_ids=("search", "write"),
    )

    assert result.max_concurrency == 2
    assert result.retention_seconds == 25
    assert [item["revision"] for item in result.provenance["policies"]] == [1, 1, 1]
    assert result.provenance["policies"][2]["applicationId"] == "app-a"


def test_session_policy_fails_closed_for_disabled_admission_and_allowlist_mismatch() -> None:
    disabled = _policy().model_copy(update={"admission_enabled": False})
    with pytest.raises(ValueError, match="disabled"):
        evaluate_agent_session_policies(
            (_revision(disabled, 1),),
            envelope_max_total_tokens=1,
            envelope_max_cost_usd=Decimal("0"),
            envelope_max_duration_seconds=1,
            envelope_max_concurrency=1,
            requested_timeout_seconds=None,
            provider_ids=(),
            harness_id="pi",
            tool_ids=(),
        )

    restricted = _policy().model_copy(update={"allowed_provider_ids": ("other",)})
    with pytest.raises(ValueError, match="provider dependency"):
        evaluate_agent_session_policies(
            (_revision(restricted, 1),),
            envelope_max_total_tokens=1,
            envelope_max_cost_usd=Decimal("0"),
            envelope_max_duration_seconds=1,
            envelope_max_concurrency=1,
            requested_timeout_seconds=None,
            provider_ids=("openai",),
            harness_id="pi",
            tool_ids=(),
        )
