from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain import ReconciliationMode, ReconciliationRequest, ReconciliationTargetType


def test_reconciliation_request_selects_one_supported_target() -> None:
    execution_id = uuid4()
    request = ReconciliationRequest.model_validate(
        {
            "mode": "APPLY",
            "executionId": execution_id,
            "maxRepairs": 3,
            "idempotencyKey": "repair-execution",
            "reason": "recover durable state",
        }
    )

    assert request.mode is ReconciliationMode.APPLY
    assert request.target_type is ReconciliationTargetType.EXECUTION
    assert request.target_id == str(execution_id)


@pytest.mark.parametrize(
    "payload",
    [
        {
            "mode": "APPLY",
            "maxRepairs": 0,
            "idempotencyKey": "no-repairs",
            "reason": "invalid apply",
        },
        {
            "executionId": str(uuid4()),
            "workerId": str(uuid4()),
            "idempotencyKey": "two-targets",
            "reason": "invalid target",
        },
        {
            "since": datetime.now(UTC),
            "until": datetime.now(UTC) - timedelta(minutes=1),
            "idempotencyKey": "reverse-range",
            "reason": "invalid range",
        },
    ],
)
def test_reconciliation_request_rejects_unsafe_bounds(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ReconciliationRequest.model_validate(payload)
