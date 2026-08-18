# ADR-002: PostgreSQL as the authoritative platform and transport store

- **Status:** Accepted
- **Decision questions:** Q-008, Q-009
- **Date:** 2026-08-15

## Context

AMESH needs transactional coupling between durable workflow state and dispatch while keeping the reference deployment operable without a separate broker or alternate relational database.

## Decision

Use PostgreSQL as the only supported authoritative relational backend and the only reference internal durable transport. PostgreSQL stores canonical resources, execution snapshots, immutable events, inbox/outbox records, task and trigger queues, leases, fencing tokens, projection checkpoints and searchable projections.

`LISTEN/NOTIFY` may reduce wake-up latency but is never treated as durable delivery. Object payloads remain in object storage.

## Consequences

- One transaction can atomically commit state and enqueue follow-up work.
- Deployment and disaster recovery have fewer coordinated stateful systems.
- PostgreSQL capacity, table partitioning, autovacuum, connection budgets and hot-row avoidance become critical design concerns.
- Queue and projection benchmark envelopes must be published.
- MySQL/MariaDB and broker-backed internal modes are out of scope unless a future ADR reverses this decision.

## Revisit triggers

- Published reference scale cannot be achieved after schema, partitioning and admission-control optimisation.
- A required compatibility behavior fundamentally cannot be represented safely.
- The product owner changes the single-database deployment objective.

## Traceability

See `docs/architecture/postgresql-transport.md`, `EPIC-009`, `EPIC-602`, `EPIC-603` and `EPIC-604`.
