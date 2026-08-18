# Scheduler and triggers

## Scheduler ownership

Schedules are sharded by a stable trigger key. A scheduler replica acquires a lease with an ownership
epoch. Every occurrence write includes that epoch; a newer epoch fences a paused or partitioned replica.

## Temporal model

Each schedule records IANA timezone, expression, calendar constraints, next due instant, last evaluated
instant, misfire policy and revision. Calendar calculation produces instants; display converts them back
to local time. DST gaps and overlaps are explicit conformance fixtures.

## Misfire policies

- `SKIP`: move to the next future occurrence.
- `CATCH_UP`: create every missed occurrence subject to admission.
- `COALESCE`: create one occurrence representing a missed range.
- `BACKFILL`: create a first-class backfill resource.
- `FAIL`: mark the trigger degraded and require intervention.

## Trigger occurrence protocol

A trigger source proposes an occurrence with a stable source identity. The platform transaction:

1. validates active revision and conditions;
2. inserts the occurrence if its identity is new;
3. advances the checkpoint where safe;
4. creates an execution command or marks it delayed by admission;
5. commits before acknowledging the source when connector semantics allow.

Webhook triggers use signed or authenticated endpoints, request size limits, replay protection and
idempotency keys. Realtime trigger connectors apply backpressure and cannot retain unbounded memory.
