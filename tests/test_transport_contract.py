from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.ports import DurableEnvelope, WorkClaim


def envelope() -> DurableEnvelope:
    return DurableEnvelope(
        message_id=uuid4(),
        message_type="TaskDispatchRequested",
        schema_version=1,
        tenant_id="default",
        partition_key="execution:123",
        correlation_id=uuid4(),
        produced_at=datetime.now(UTC),
        payload={"taskRunId": "task-1"},
    )


def test_work_claim_requires_positive_fencing_token() -> None:
    with pytest.raises(ValidationError):
        WorkClaim(
            queue_id=1,
            shard_key=0,
            lane="task-dispatch",
            consumer_id="worker-1",
            fencing_token=0,
            lease_expires_at=datetime.now(UTC),
            delivery_attempt=1,
            envelope=envelope(),
        )


def test_durable_envelope_rejects_invalid_schema_version() -> None:
    valid = envelope()
    with pytest.raises(ValidationError):
        DurableEnvelope(
            message_id=valid.message_id,
            message_type=valid.message_type,
            schema_version=0,
            tenant_id=valid.tenant_id,
            partition_key=valid.partition_key,
            correlation_id=valid.correlation_id,
            produced_at=valid.produced_at,
            payload=valid.payload,
        )
