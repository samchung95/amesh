# Messaging and delivery

AMESH uses PostgreSQL as its internal durable message transport. The logical message contract remains independent of table layout so that services do not couple domain code to SQL claim mechanics.

## Envelope

```json
{
  "message_id": "uuid",
  "message_type": "TaskDispatchRequested",
  "schema_version": 1,
  "tenant_id": "tenant",
  "partition_key": "execution-or-trigger-key",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "produced_at": "RFC3339 timestamp",
  "producer": {"service": "executor", "instance": "uuid", "version": "semver"},
  "traceparent": "...",
  "payload": {}
}
```

## Durable publication

The producing transaction inserts the state transition, immutable event and outbox/queue row together. Consumers claim eligible rows with `FOR UPDATE SKIP LOCKED`, commit the fenced lease, process outside the claim transaction and record an inbox identity before applying a logical effect.

Queue order is preserved for one partition key, not globally. Priority and fairness rules may choose between partition keys but cannot reorder a single execution where ordering is semantically required.

## Wake-up and polling

`LISTEN/NOTIFY` may wake idle consumers. Because PostgreSQL notifications are not durable and can be coalesced or lost, every consumer also polls from its durable checkpoint. Correctness must be identical with notifications disabled.

## Redelivery

Delivery is at least once. A claim becomes eligible again when its lease expires or processing requests a retry. The consumer must use `message_id`, attempt identity and the relevant entity version to return the prior result or apply one logical effect.

## Poison messages

After bounded retries, a poison message is quarantined with schema, producer, stack class, payload checksum and redacted payload. Operators may discard, repair through an approved migration, or replay. Consumers never skip poison rows silently.

## Schema evolution

- Additive compatible changes remain in the same schema version only when permitted by policy.
- Incompatible changes use a new schema version.
- Consumers declare accepted ranges.
- Upcasters are deterministic and tested.
- Rolling upgrades require an overlap in producer/consumer ranges.
- Stored events are never mutated merely to simplify a new consumer.

## Operational signals

At minimum, export queue depth, oldest eligible age, claim latency, lease expiry, redelivery count, dead-letter count, hot-partition distribution, transaction latency and database saturation.

See [PostgreSQL durable transport](postgresql-transport.md) for table and failure design.
