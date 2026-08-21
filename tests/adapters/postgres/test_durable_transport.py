from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresDurableTransport, PostgresTenantRepository
from amesh.domain import TenantDefinition
from amesh.ports import (
    DeadLetterReplayError,
    DurableEnvelope,
    MessageIdentityConflict,
    StaleWorkClaimError,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def envelope(
    message_id: UUID,
    *,
    tenant_id: str = "default",
    partition_key: str | None = None,
) -> DurableEnvelope:
    return DurableEnvelope(
        message_id=message_id,
        message_type="TaskDispatchRequested",
        schema_version=1,
        tenant_id=tenant_id,
        partition_key=partition_key or f"execution:{message_id}",
        correlation_id=uuid4(),
        produced_at=datetime.now(UTC),
        trace_context={"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},
        payload={"taskRunId": "task-1"},
    )


@asynccontextmanager
async def transport_for(*message_ids: UUID) -> AsyncIterator[PostgresDurableTransport]:
    if TEST_DATABASE_URL is None:
        raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
    engine: AsyncEngine = create_async_engine(TEST_DATABASE_URL)
    try:
        yield PostgresDurableTransport(engine)
    finally:
        async with engine.begin() as connection:
            for message_id in message_ids:
                for table in (
                    "durable_dead_letters",
                    "consumed_messages",
                    "durable_work_queue",
                    "messages_outbox",
                ):
                    await connection.execute(
                        text(f"DELETE FROM {table} WHERE message_id = :message_id"),
                        {"message_id": message_id},
                    )
        await engine.dispose()


def test_enqueue_claim_and_acknowledge() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        async with transport_for(message_id) as transport:
            message = envelope(message_id)
            queue_id = await transport.enqueue("task-dispatch", message)
            duplicate_id = await transport.enqueue("task-dispatch", message)
            assert duplicate_id == queue_id
            with pytest.raises(MessageIdentityConflict):
                await transport.enqueue(
                    "task-dispatch",
                    message.model_copy(update={"payload": {"taskRunId": "different"}}),
                )

            claims = await transport.claim(
                "task-dispatch",
                "worker-1",
                tenant_id="default",
                limit=1,
                lease_duration=timedelta(seconds=30),
            )
            assert len(claims) == 1
            claim = claims[0]
            assert claim.queue_id == queue_id
            assert claim.fencing_token == 1
            assert claim.delivery_attempt == 1
            assert claim.envelope.message_id == message_id
            assert "traceparent" in claim.envelope.trace_context

            extended_until = await transport.extend(
                queue_id,
                "worker-1",
                claim.fencing_token,
                timedelta(seconds=60),
                tenant_id="default",
            )
            assert extended_until > claim.lease_expires_at
            await transport.acknowledge(
                queue_id,
                "worker-1",
                claim.fencing_token,
                tenant_id="default",
            )
            assert (
                await transport.claim(
                    "task-dispatch",
                    "worker-2",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
                == []
            )

    asyncio.run(scenario())


def test_partition_head_of_line_is_claimed_in_order() -> None:
    async def scenario() -> None:
        first_id = uuid4()
        second_id = uuid4()
        partition = f"execution:{uuid4()}"
        async with transport_for(first_id, second_id) as transport:
            first_queue_id = await transport.enqueue(
                "ordered",
                envelope(first_id, partition_key=partition),
            )
            second_queue_id = await transport.enqueue(
                "ordered",
                envelope(second_id, partition_key=partition),
            )

            first_claims = await transport.claim(
                "ordered",
                "worker-1",
                tenant_id="default",
                limit=2,
                lease_duration=timedelta(seconds=30),
            )
            assert [claim.queue_id for claim in first_claims] == [first_queue_id]
            await transport.acknowledge(
                first_queue_id,
                "worker-1",
                first_claims[0].fencing_token,
                tenant_id="default",
            )
            second_claims = await transport.claim(
                "ordered",
                "worker-2",
                tenant_id="default",
                limit=2,
                lease_duration=timedelta(seconds=30),
            )
            assert [claim.queue_id for claim in second_claims] == [second_queue_id]
            await transport.acknowledge(
                second_queue_id,
                "worker-2",
                second_claims[0].fencing_token,
                tenant_id="default",
            )

    asyncio.run(scenario())


def test_listen_notify_wakes_the_requested_lane() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        async with transport_for(message_id) as transport:
            waiting = asyncio.create_task(
                transport.wait_for_work(
                    "wake-test",
                    tenant_id="default",
                    timeout_seconds=2,
                )
            )
            await asyncio.sleep(0.1)
            await transport.enqueue("wake-test", envelope(message_id))

            assert await waiting is True
            assert (
                await transport.wait_for_work(
                    "other-lane",
                    tenant_id="default",
                    timeout_seconds=0.05,
                )
                is False
            )

    asyncio.run(scenario())


def test_expired_claim_is_reclaimed_with_a_new_fencing_token() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        async with transport_for(message_id) as transport:
            queue_id = await transport.enqueue("task-dispatch", envelope(message_id))
            first = (
                await transport.claim(
                    "task-dispatch",
                    "worker-1",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(milliseconds=20),
                )
            )[0]
            await asyncio.sleep(0.05)
            second = (
                await transport.claim(
                    "task-dispatch",
                    "worker-2",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]

            assert second.queue_id == queue_id
            assert second.fencing_token == first.fencing_token + 1
            assert second.delivery_attempt == first.delivery_attempt + 1
            with pytest.raises(StaleWorkClaimError):
                await transport.acknowledge(
                    queue_id,
                    "worker-1",
                    first.fencing_token,
                    tenant_id="default",
                )
            await transport.acknowledge(
                queue_id,
                "worker-2",
                second.fencing_token,
                tenant_id="default",
            )

    asyncio.run(scenario())


def test_release_makes_claim_available_for_retry() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        async with transport_for(message_id) as transport:
            queue_id = await transport.enqueue("task-dispatch", envelope(message_id))
            first = (
                await transport.claim(
                    "task-dispatch",
                    "worker-1",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            await transport.release(
                queue_id,
                "worker-1",
                first.fencing_token,
                tenant_id="default",
                retry_at=datetime.now(UTC),
                reason="transient failure",
            )
            second = (
                await transport.claim(
                    "task-dispatch",
                    "worker-2",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            assert second.fencing_token == first.fencing_token + 1
            assert second.delivery_attempt == first.delivery_attempt + 1
            await transport.acknowledge(
                queue_id,
                "worker-2",
                second.fencing_token,
                tenant_id="default",
            )

    asyncio.run(scenario())


def test_bounded_queue_retry_quarantines_and_replays_poison_message() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        async with transport_for(message_id) as transport:
            queue_id = await transport.enqueue(
                "poison-test",
                envelope(message_id),
                max_attempts=2,
            )
            for consumer_id in ("worker-1", "worker-2"):
                claim = (
                    await transport.claim(
                        "poison-test",
                        consumer_id,
                        tenant_id="default",
                        limit=1,
                        lease_duration=timedelta(seconds=30),
                    )
                )[0]
                await transport.release(
                    queue_id,
                    consumer_id,
                    claim.fencing_token,
                    tenant_id="default",
                    retry_at=datetime.now(UTC),
                    reason="invalid payload",
                    failure_class="poison.schema",
                )

            assert (
                await transport.claim(
                    "poison-test",
                    "worker-3",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
                == []
            )
            dead_letter = (await transport.list_dead_letters(tenant_id="default"))[-1]
            assert dead_letter.message_id == message_id
            assert dead_letter.failure_class == "poison.schema"
            assert dead_letter.attempt_count == 2
            assert len(dead_letter.payload_checksum) == 64
            diagnostics = await transport.diagnostics(tenant_id="default")
            assert diagnostics.poison_message_count >= 1
            assert diagnostics.dead_letter_count >= 1
            assert diagnostics.redelivery_count >= 1

            await transport.replay_dead_letter(
                dead_letter.dead_letter_id,
                tenant_id="default",
                actor_id="test:transport",
            )
            with pytest.raises(DeadLetterReplayError):
                await transport.replay_dead_letter(
                    dead_letter.dead_letter_id,
                    tenant_id="default",
                    actor_id="test:transport",
                )
            replayed = (
                await transport.claim(
                    "poison-test",
                    "worker-3",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            assert replayed.delivery_attempt == 1
            await transport.acknowledge(
                queue_id,
                "worker-3",
                replayed.fencing_token,
                tenant_id="default",
            )

    asyncio.run(scenario())


def test_bounded_outbox_failure_quarantines_and_replays_publication() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        message = envelope(message_id)
        lane = f"outbox-failure-{message_id}"
        async with transport_for(message_id) as transport:
            sequence = await transport.enqueue_outbox(lane, message, max_attempts=2)
            assert (
                await transport.record_outbox_failure(
                    sequence,
                    tenant_id="default",
                    retry_at=datetime.now(UTC),
                    reason="publisher unavailable",
                    failure_class="postgres.transient",
                )
                is False
            )
            assert (
                await transport.record_outbox_failure(
                    sequence,
                    tenant_id="default",
                    retry_at=datetime.now(UTC),
                    reason="publisher unavailable",
                    failure_class="postgres.transient",
                )
                is True
            )
            dead_letter = (await transport.list_dead_letters(tenant_id="default"))[-1]
            assert dead_letter.source_type == "OUTBOX"
            assert dead_letter.message_id == message_id
            diagnostics = await transport.diagnostics(tenant_id="default")
            assert diagnostics.outbox_dead_letter_count >= 1
            assert diagnostics.outbox_retry_count >= 2

            await transport.replay_dead_letter(
                dead_letter.dead_letter_id,
                tenant_id="default",
                actor_id="test:transport",
            )
            assert await transport.publish_outbox(tenant_id="default", limit=1) == 1
            claim = (
                await transport.claim(
                    lane,
                    "worker-1",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            await transport.acknowledge(
                claim.queue_id,
                "worker-1",
                claim.fencing_token,
                tenant_id="default",
            )

    asyncio.run(scenario())


def test_outbox_publish_and_consumer_inbox_are_idempotent() -> None:
    async def scenario() -> None:
        message_id = uuid4()
        message = envelope(message_id)
        subject = f"task-dispatch-{message_id}"
        async with transport_for(message_id) as transport:
            sequence = await transport.enqueue_outbox(subject, message)
            duplicate_sequence = await transport.enqueue_outbox(subject, message)
            assert duplicate_sequence == sequence

            assert await transport.publish_outbox(tenant_id="default", limit=10) >= 1
            claims = await transport.claim(
                subject,
                "worker-1",
                tenant_id="default",
                limit=1,
                lease_duration=timedelta(seconds=30),
            )
            assert len(claims) == 1
            claim = claims[0]
            assert claim.envelope.message_id == message_id

            assert await transport.record_consumed("executor", claim.envelope) is True
            assert await transport.record_consumed("executor", claim.envelope) is False
            await transport.acknowledge(
                claim.queue_id,
                "worker-1",
                claim.fencing_token,
                tenant_id="default",
            )
            assert await transport.publish_outbox(tenant_id="default", limit=10) == 0

    asyncio.run(scenario())


def test_process_crash_after_inbox_commit_redelivers_without_duplicate_effect() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        message_id = uuid4()
        message = envelope(message_id)
        subject = f"task-dispatch-{message_id}"
        async with transport_for(message_id) as transport:
            await transport.enqueue_outbox(subject, message)
            assert await transport.publish_outbox(tenant_id="default", limit=10) >= 1

            crashing_worker = Path(__file__).with_name("crash_after_inbox.py")
            result = subprocess.run(
                [sys.executable, str(crashing_worker), TEST_DATABASE_URL, subject],
                capture_output=True,
                check=False,
                timeout=15,
            )
            assert result.returncode == 0, result.stderr.decode(errors="replace")

            await asyncio.sleep(0.15)
            redelivered = (
                await transport.claim(
                    subject,
                    "replacement-worker",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            assert redelivered.fencing_token == 2
            assert await transport.record_consumed("executor", redelivered.envelope) is False
            await transport.acknowledge(
                redelivered.queue_id,
                "replacement-worker",
                redelivered.fencing_token,
                tenant_id="default",
            )

    asyncio.run(scenario())


def test_queue_claims_and_notifications_are_tenant_isolated() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        transport = PostgresDurableTransport(engine)
        tenant_repository = PostgresTenantRepository(engine)
        suffix = uuid4().hex[:10]
        tenant = TenantDefinition(
            slug=f"queue-tenant-{suffix}",
            display_name="Queue isolation tenant",
        )
        actor_id = f"test:queue-isolation:{suffix}"
        message_id = uuid4()
        lane = f"tenant-isolation-{suffix}"
        try:
            await tenant_repository.create(tenant, actor_id=actor_id)
            waiting_for_default = asyncio.create_task(
                transport.wait_for_work(
                    lane,
                    tenant_id="default",
                    timeout_seconds=0.2,
                )
            )
            await asyncio.sleep(0.05)
            queue_id = await transport.enqueue(
                lane,
                envelope(message_id, tenant_id=tenant.slug),
            )
            assert await waiting_for_default is False
            assert (
                await transport.claim(
                    lane,
                    "default-worker",
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
                == []
            )
            tenant_claim = (
                await transport.claim(
                    lane,
                    "tenant-worker",
                    tenant_id=tenant.slug,
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            assert tenant_claim.envelope.tenant_id == tenant.slug
            with pytest.raises(StaleWorkClaimError):
                await transport.acknowledge(
                    queue_id,
                    "tenant-worker",
                    tenant_claim.fencing_token,
                    tenant_id="default",
                )
            await transport.acknowledge(
                queue_id,
                "tenant-worker",
                tenant_claim.fencing_token,
                tenant_id=tenant.slug,
            )
        finally:
            async with engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM durable_work_queue WHERE message_id = :message_id"),
                    {"message_id": message_id},
                )
                await connection.execute(
                    text("DELETE FROM audit_events WHERE actor_id = :actor_id"),
                    {"actor_id": actor_id},
                )
                await connection.execute(
                    text("DELETE FROM tenants WHERE id = :tenant_id"),
                    {"tenant_id": tenant.id},
                )
            await engine.dispose()

    asyncio.run(scenario())
