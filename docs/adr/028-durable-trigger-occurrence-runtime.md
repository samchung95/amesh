# ADR 028: Durable trigger occurrence runtime

- Status: Accepted
- Date: 2026-08-22
- Scope: EPIC-103

## Context

Schedules, webhooks, polling connectors, realtime connectors and flow-completion triggers need the
same durable identity, retry and operator-control semantics. A source may repeat delivery or lose its
connection after AMESH commits an event but before the source receives an acknowledgement. Process
memory therefore cannot be the authoritative trigger queue or checkpoint.

## Decision

Store trigger revision state, checkpoints and occurrences in tenant-RLS-protected PostgreSQL tables.
An occurrence key is supplied by the connector or derived from canonical source data and is unique
within an immutable trigger revision. Occurrences move through `ACCEPTED`, `DEFERRED`, `PROCESSING`,
`RETRY_WAIT`, `SUCCEEDED` and `DEAD_LETTERED`; claims use database-time leases and fencing tokens.

Flow application transactionally deactivates prior trigger revisions and activates the new revision.
Backpressure is a per-trigger pending limit. Operators may pause or resume a trigger and replay a
dead-lettered occurrence into a new, linked occurrence without mutating retained evidence.

Polling and realtime adapters share typed contracts. They must durably accept an occurrence and, for
polling, commit the new checkpoint before acknowledging it to the source. Flow completion writes
matching `core.flow` occurrences in the source execution's terminal transaction. A scheduler role
claims non-temporal occurrences and creates idempotent executions; no source-flow polling is used.

## Alternatives considered

- Independent queues for every trigger type were rejected because deduplication, pause, replay and
  health behavior would diverge by connector.
- A process-local channel was rejected because restart can lose accepted events and checkpoints.
- Routing flow completions through a polling query was rejected because it adds avoidable latency and
  cannot commit the routing decision with the terminal source transition.

## Consequences

- PostgreSQL remains the authoritative delivery, occurrence and recovery boundary.
- At-least-once source delivery produces one logical occurrence and execution per trigger revision.
- Connectors may implement transport-specific connection behavior, but cannot bypass durable accept,
  checkpoint or acknowledgement ordering.
- Occurrence evidence remains queryable after success, dead-letter or manual replay.

## References

- [Scheduler and trigger architecture](../architecture/scheduler-and-triggers.md)
- [Trigger operations](../operations/triggers.md)
- [At-least-once delivery ADR](003-at-least-once-delivery-with-idempotency-and-fencing.md)
