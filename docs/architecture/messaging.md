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
  "trace_context": {"traceparent": "...", "tracestate": "..."},
  "payload": {}
}
```

## Durable publication

The producing transaction inserts the state transition, immutable event and outbox/queue row together. Consumers claim eligible rows with `FOR UPDATE SKIP LOCKED`, commit the fenced lease, process outside the claim transaction and record an inbox identity before applying a logical effect.

Queue order is preserved for one lane and partition key, not globally. The claim query admits only the
oldest non-terminal row from that lane/partition. Priority and fairness rules choose between partition
heads but cannot overtake an earlier message in the same ordered stream.

## Wake-up and polling

`LISTEN/NOTIFY` may wake idle consumers. Because PostgreSQL notifications are not durable and can be coalesced or lost, every consumer also polls from its durable checkpoint. Correctness must be identical with notifications disabled.

## Redelivery

Delivery is at least once. A claim becomes eligible again when its lease expires or processing requests a retry. The consumer must use `message_id`, attempt identity and the relevant entity version to return the prior result or apply one logical effect.

## Poison messages

Each queue or outbox row has a positive `max_attempts`. Exhaustion quarantines payload-safe evidence
with source identity, schema, failure class, payload checksum, attempt count and error; diagnostics do
not return the payload. An authorized operator may replay a pending dead letter, which resets delivery
attempts while retaining the resolved quarantine record. Consumers never skip poison rows silently.

## Schema evolution

- Additive compatible changes remain in the same schema version only when permitted by policy.
- Incompatible changes use a new schema version.
- Consumers declare accepted ranges.
- Upcasters are deterministic and tested.
- Rolling upgrades require an overlap in producer/consumer ranges.
- Stored events are never mutated merely to simplify a new consumer.

## Operational signals

`DurableTransport.diagnostics()` returns tenant-authorized queue depth, oldest eligible/outbox age,
claimed and expired-claim counts, redelivery totals, poison/dead-letter totals and outbox retry/dead
letter totals. Database pool/query saturation remains available from `/metrics`.

## External side-effect responsibility

Internal delivery is at least once; AMESH does not claim exactly-once behavior for an HTTP request,
model call, database write or other external effect. A consumer must persist its inbox identity and
logical state change in one local transaction where possible, pass a stable destination idempotency key
derived from `message_id` or the logical operation, or implement an explicit probe/compensation policy.
Acknowledging a queue claim without one of those strategies can duplicate an external effect after a
crash and is the plugin/task author's responsibility.

See [PostgreSQL durable transport](postgresql-transport.md) for table and failure design.
