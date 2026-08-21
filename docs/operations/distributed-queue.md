# Distributed PostgreSQL queue operations

AMESH uses PostgreSQL queue, outbox, inbox, lease and dead-letter rows as its only internal durable
transport. `LISTEN/NOTIFY` reduces idle latency, but consumers always poll durable rows and retain the
same behavior if a notification or connection is lost.

## Lanes, partitions and virtual shards

Each message belongs to one tenant, independent consumer lane and execution/trigger partition key.
Migration 0023 stores a stable 16-bit virtual shard derived from the partition key's SHA-256 digest.
Consumers divide those virtual shards with `shard_key % consumer_count`; changing the consumer count
does not rewrite queue rows. A claim still admits only the oldest non-terminal row in one
tenant/lane/partition, so replicas cannot reorder an execution stream.

`PostgresDurableTransport.claim()` accepts `shard_id`, `shard_count` and an explicit tuple of
`supported_schema_versions`. Invalid shard assignments and empty/invalid schema ranges fail before a
transaction begins.

## Rolling schema upgrades

Use this sequence for an incompatible envelope change:

1. Apply the additive database migration while current producers and consumers continue running.
2. Deploy consumers that accept both the current and new schema versions.
3. Deploy producers that write the new version.
4. Wait until diagnostics show no retained old-version work, then remove old-version support.

An old consumer does not claim an unsupported head. It also cannot overtake that head to process a
later message in the same partition. The overlapping consumer drains both versions without mutating
stored envelopes.

## Diagnostics and retention

`DurableTransport.diagnostics()` returns tenant-bounded depth, oldest eligible age, active and expired
claims, redeliveries, poison/dead-letter and outbox counts, one-minute completion throughput, p95 claim
latency, virtual-shard depth/skew, PostgreSQL version/recovery state and the diagnostics transaction
latency. `/metrics` additionally exposes label-free database health, pool pressure and query latency.
No payload or high-cardinality partition key appears in either surface.

Terminal queue, published outbox, consumed inbox and resolved dead-letter evidence can be purged in a
bounded transaction after the operator's retention horizon:

```bash
uv run python scripts/purge_transport.py \
  --tenant default \
  --before 2026-08-01T00:00:00+00:00 \
  --limit 1000
```

Pending, claimed, retryable and unresolved dead-letter rows are never selected. Repeat bounded passes
until all returned counts are zero.

## Profile M qualification command

Run the checked-in fixed-profile benchmark against the target PostgreSQL deployment:

```bash
uv run python scripts/benchmark_postgres_queue.py \
  --duration-seconds 60 \
  --starts-per-second 50 \
  --consumers 4 \
  --claim-batch 25
```

The 2026-08-22 local PostgreSQL 17 functional run produced and completed 3,000 independently
partitioned messages in 60.014 seconds: 49.988 starts/second, 0.029011-second p95 dispatch latency,
0.111138-second maximum latency and zero remaining queue depth. This clears the short fixed-profile
gate. The canonical NFR requires the same 50 starts/second for 60 minutes; that soak remains In
Progress and no 60-minute capacity claim is made here.

| Property | Single consumer / host | Horizontally assigned consumers |
| --- | --- | --- |
| Durable truth | Same PostgreSQL rows | Same PostgreSQL rows |
| Work allocation | All virtual shards map to shard 0 of 1 | Each consumer owns its shard id modulo the declared count |
| Ordering | Per tenant/lane/partition | Identical per-partition ordering across replicas |
| Wake-up | PostgreSQL notification plus polling | Each replica uses notification plus polling |
| Failure recovery | Lease expiry returns work to the same process | Another replica reclaims with a larger fence |
| Capacity | Bound by one consumer and its pool | Adds consumers until PostgreSQL/pool/admission limits dominate |

The subprocess crash test recovers a committed inbox/queue claim in under one second, and the
connection-replacement test publishes and completes a committed outbox row through a fresh engine.
Credentialed zone-loss and managed PostgreSQL failover qualification remains part of the HA reference
environment rather than this local capacity claim.
