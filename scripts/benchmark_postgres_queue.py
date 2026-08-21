from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime, timedelta
from math import ceil
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from sqlalchemy import text

from amesh.adapters.postgres import PostgresDurableTransport
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.config import Settings
from amesh.database import create_database_engine
from amesh.ports import DurableEnvelope


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Benchmark the AMESH PostgreSQL work queue")
    result.add_argument("--duration-seconds", type=float, default=60)
    result.add_argument("--starts-per-second", type=float, default=50)
    result.add_argument("--consumers", type=int, default=4)
    result.add_argument("--claim-batch", type=int, default=25)
    result.add_argument("--tenant", default="default")
    result.add_argument("--output", type=Path)
    result.add_argument("--retain-rows", action="store_true")
    return result


async def benchmark(
    settings: Settings,
    *,
    duration_seconds: float,
    starts_per_second: float,
    consumers: int,
    claim_batch: int,
    tenant_id: str,
    retain_rows: bool,
) -> dict[str, object]:
    if duration_seconds <= 0 or starts_per_second <= 0:
        raise ValueError("duration and target rate must be positive")
    if consumers < 1 or claim_batch < 1:
        raise ValueError("consumer and claim-batch counts must be positive")
    expected = max(1, round(duration_seconds * starts_per_second))
    lane = f"benchmark-{uuid4()}"
    engine = create_database_engine(settings)
    transport = PostgresDurableTransport(engine)
    producer_done = asyncio.Event()
    latencies: list[float] = []
    started = perf_counter()

    async def produce() -> None:
        try:
            for index in range(expected):
                scheduled = started + index / starts_per_second
                delay = scheduled - perf_counter()
                if delay > 0:
                    await asyncio.sleep(delay)
                message_id = uuid4()
                await transport.enqueue(
                    lane,
                    DurableEnvelope(
                        message_id=message_id,
                        message_type="QueueBenchmarkDispatch",
                        schema_version=1,
                        tenant_id=tenant_id,
                        partition_key=f"execution:{message_id}",
                        correlation_id=message_id,
                        produced_at=datetime.now(UTC),
                        trace_context={"traceparent": f"benchmark-{message_id.hex}"},
                        payload={"sequence": index},
                    ),
                )
        finally:
            producer_done.set()

    async def consume(shard_id: int) -> None:
        consumer_id = f"benchmark-consumer-{shard_id}"
        while not producer_done.is_set() or len(latencies) < expected:
            claims = await transport.claim(
                lane,
                consumer_id,
                tenant_id=tenant_id,
                limit=claim_batch,
                lease_duration=timedelta(seconds=10),
                shard_id=shard_id,
                shard_count=consumers,
                supported_schema_versions=(1,),
            )
            if not claims:
                await asyncio.sleep(0.005)
                continue
            for claim in claims:
                latencies.append((datetime.now(UTC) - claim.envelope.produced_at).total_seconds())
                await transport.acknowledge(
                    claim.queue_id,
                    consumer_id,
                    claim.fencing_token,
                    tenant_id=tenant_id,
                )

    try:
        async with asyncio.timeout(duration_seconds + 60):
            await asyncio.gather(produce(), *(consume(index) for index in range(consumers)))
        elapsed = perf_counter() - started
        async with tenant_transaction(engine, tenant_id) as (connection, tenant_uuid):
            lag = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                count(*) FILTER (
                                    WHERE state IN ('READY', 'CLAIMED')
                                ) AS active,
                                EXTRACT(EPOCH FROM clock_timestamp() - min(available_at) FILTER (
                                    WHERE state = 'READY' AND available_at <= clock_timestamp()
                                )) AS oldest_age
                            FROM durable_work_queue
                            WHERE tenant_id = :tenant_id AND lane = :lane
                            """
                        ),
                        {"tenant_id": tenant_uuid, "lane": lane},
                    )
                )
                .mappings()
                .one()
            )
        ordered = sorted(latencies)
        p95_index = max(0, min(len(ordered) - 1, ceil(len(ordered) * 0.95) - 1))
        p95_latency = ordered[p95_index] if ordered else None
        throughput = len(latencies) / elapsed
        active = int(lag["active"])
        passed = (
            len(latencies) == expected
            and throughput >= starts_per_second * 0.95
            and p95_latency is not None
            and p95_latency < 3
            and active == 0
        )
        return {
            "profile": "M-postgresql-distributed-queue",
            "passed": passed,
            "target": {
                "durationSeconds": duration_seconds,
                "startsPerSecond": starts_per_second,
                "maximumP95DispatchLatencySeconds": 3,
                "consumers": consumers,
                "claimBatch": claim_batch,
            },
            "result": {
                "produced": expected,
                "processed": len(latencies),
                "elapsedSeconds": round(elapsed, 3),
                "throughputPerSecond": round(throughput, 3),
                "p95DispatchLatencySeconds": (
                    round(p95_latency, 6) if p95_latency is not None else None
                ),
                "maximumDispatchLatencySeconds": round(max(ordered), 6) if ordered else None,
                "remainingQueueDepth": active,
                "oldestEligibleAgeSeconds": lag["oldest_age"],
            },
        }
    finally:
        if not retain_rows:
            async with tenant_transaction(engine, tenant_id) as (connection, tenant_uuid):
                await connection.execute(
                    text(
                        "DELETE FROM durable_work_queue "
                        "WHERE tenant_id = :tenant_id AND lane = :lane"
                    ),
                    {"tenant_id": tenant_uuid, "lane": lane},
                )
        await engine.dispose()


def main() -> int:
    arguments = parser().parse_args()
    report = asyncio.run(
        benchmark(
            Settings(),
            duration_seconds=arguments.duration_seconds,
            starts_per_second=arguments.starts_per_second,
            consumers=arguments.consumers,
            claim_batch=arguments.claim_batch,
            tenant_id=arguments.tenant,
            retain_rows=arguments.retain_rows,
        )
    )
    encoded = json.dumps(report, indent=2, default=str, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
