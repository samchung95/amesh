# ADR-003: At-least-once delivery with idempotency and fencing

- **Status:** Accepted
- **Decision question:** Q-008
- **Date:** 2026-08-15

## Context

Process failure, network failure and external side effects prevent a generic exactly-once execution guarantee.

## Decision

Use stable message and attempt identities, transactional outbox/inbox records, bounded retries, expiring leases and monotonically increasing fencing tokens. Do not market generic exactly-once external side effects.

## Consequences

- Duplicate delivery is expected and tested.
- Plugins and runners declare idempotency, compensation and ambiguous-outcome behavior.
- Users receive explicit evidence when the result of an external side effect cannot be proven.
- PostgreSQL row claims and notifications implement the transport without changing these semantics.

## Revisit triggers

- Conformance or fault-injection tests invalidate an invariant.
- A narrower operation can prove exactly-once behavior and documents its scope precisely.

## Traceability

See `docs/architecture/execution-semantics.md`, `docs/architecture/postgresql-transport.md`, `EPIC-007`, `EPIC-009` and `EPIC-101`.
