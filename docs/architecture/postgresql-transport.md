# PostgreSQL durable transport

## Decision

AMESH uses PostgreSQL as the only reference transport for orchestration commands, events, task dispatch, trigger work and projection checkpoints. External brokers are workflow integrations, not internal platform dependencies.

## Non-negotiable rules

- A committed message is a durable row written in the same transaction as the state change that produced it.
- `LISTEN/NOTIFY` is an optional latency optimization. Notifications may be lost; workers must always recover by querying durable rows.
- Delivery is at least once. Inbox identities and idempotent reducers prevent duplicate logical effects.
- Ordering is guaranteed only within a declared partition key such as tenant plus execution or trigger identity.
- Claims use `FOR UPDATE SKIP LOCKED`, expiring leases and monotonically increasing fencing tokens.
- A stale owner cannot complete a task after lease transfer, cancellation, retry or restart.
- Queue backlog, oldest age, claim latency, redelivery and dead-letter counts are first-class metrics.

## Logical tables

```text
orchestration_outbox
  message_id, tenant_id, partition_key, type, schema_version,
  payload, available_at, created_at, published_at

orchestration_queue
  queue_id, message_id, lane, priority, partition_key,
  available_at, lease_owner, lease_token, lease_expires_at,
  delivery_count, last_error, state

orchestration_inbox
  consumer_name, message_id, processed_at, result_checksum

durable_dead_letters
  id, tenant_id, source_type, source_id, message_id, lane, partition_key,
  message_type, schema_version, failure_class, payload_checksum,
  attempt_count, last_error, quarantined_at, resolution, resolved_at, resolved_by

projection_checkpoint
  projection_name, shard, last_event_position, updated_at
```

The physical design may combine outbox and queue records, but their semantic responsibilities remain distinct.

## Claim algorithm

1. Begin a short database transaction.
2. Select eligible rows for one lane and shard using `FOR UPDATE SKIP LOCKED`.
3. Increment a fencing token and set lease owner/expiry.
4. Commit before performing network or user work.
5. Renew the lease with a compare-and-set on owner and token.
6. Commit completion only when attempt, owner and fencing token still match.
7. On expiry, another worker may claim the row with a larger token.

The candidate query admits only the oldest `READY` or `CLAIMED` row for a tenant/lane/partition. A
completed or explicitly quarantined head releases the next row. Exhausting `max_attempts` atomically
moves the queue row to `DEAD_LETTER` and creates one pending `durable_dead_letters` record. Outbox
failure recording follows the same bounded policy. Replay resolves that immutable evidence and resets
the retained source row for another bounded delivery cycle.

## Scaling strategy

- Partition large queue and event tables by time and/or tenant hash.
- Separate latency-sensitive lanes from bulk backfill, logs and maintenance work.
- Limit claim batch size and transaction duration.
- Use read replicas only for explicitly stale, non-authoritative queries.
- Use connection-pool budgets per role and admission control before database saturation.
- Archive old immutable events and logs to object storage according to retention policy.
- Scale API, executor, scheduler, trigger, indexer and worker roles independently while sharing PostgreSQL truth.

## Failure behavior

| Failure | Required behavior |
|---|---|
| Worker dies after claim | Lease expires; another worker reclaims with a higher token. |
| Worker completes after losing lease | Completion is rejected as stale. |
| Notification is lost | Polling discovers the durable row. |
| Process dies after commit but before notification | Outbox publisher or queue poller resumes from the row. |
| Duplicate delivery | Inbox/reducer returns the existing logical result. |
| PostgreSQL unavailable | No state-changing request is acknowledged; running external tasks may continue but cannot commit until recovery and lease validation. |
| Poison payload | Row is quarantined after bounded retries; no silent skip. |
| Hot partition | Admission control, sharding and observable fairness policies prevent one tenant from starving others. |

## Trade-off

A PostgreSQL-only design reduces operational dependencies and gives strong transactional coupling between state and dispatch. Its cost is that database capacity becomes the dominant scaling boundary. AMESH must therefore publish benchmark envelopes and reject unsupported load rather than hiding saturation behind unbounded queues.
