from __future__ import annotations

import pytest
from pydantic import ValidationError

from amesh.domain.retention import (
    LifecycleLegalHoldDraft,
    LifecyclePolicyDraft,
    LifecycleResourceType,
    LifecycleScope,
)


def test_lifecycle_policy_scope_shape_is_explicit() -> None:
    policy = LifecyclePolicyDraft(
        resourceType=LifecycleResourceType.LOG,
        scope=LifecycleScope.NAMESPACE,
        namespace="finance.daily",
        retentionDays=30,
        reason="retain finance logs for thirty days",
    )

    assert policy.namespace == "finance.daily"
    with pytest.raises(ValidationError, match="label scope requires labelSelector"):
        LifecyclePolicyDraft(
            resourceType="EXECUTION",
            scope="LABEL",
            retentionDays=30,
            reason="missing selector",
        )


def test_lifecycle_legal_hold_rejects_an_inverted_data_range() -> None:
    with pytest.raises(ValidationError, match="dataTo must be after dataFrom"):
        LifecycleLegalHoldDraft.model_validate(
            {
                "name": "investigation",
                "reason": "preserve investigation evidence",
                "dataFrom": "2026-08-23T01:00:00Z",
                "dataTo": "2026-08-23T00:00:00Z",
            }
        )
