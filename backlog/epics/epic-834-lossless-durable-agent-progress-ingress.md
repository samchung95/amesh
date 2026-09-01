# EPIC-834 — Lossless durable agent-progress ingress

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `observability`
- **Primary persona:** AI application developer and agent-session operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Preserve every valid safe agent-progress frame in canonical order, apply producer backpressure instead of runtime truncation and durably close active activity when a caught producer failure interrupts the stream.

## In scope

- [x] Default frames-per-second, frames-per-segment, segments-per-session and frames-per-session ceilings do not truncate valid activity, and AMESH generates no new TRUNCATED progress frames.
- [x] Every valid provider or harness progress frame is committed as an individual PostgreSQL agent-session journal event before its receipt returns, so database latency backpressures the awaited producer without an acknowledged volatile tail.
- [x] Accepted frames retain individual event indexes, cursors and evidence records; exact retries remain idempotent and conflicting reuse of a source identity remains rejected.
- [x] Invalid or oversized frames fail before acceptance and receive no durable receipt instead of being reported as partial success.
- [x] A caught provider-stream or Pi harness failure durably appends one FAILED progress closure for an active segment when PostgreSQL is available, while canonical lifecycle and recovery evidence remains authoritative for the session outcome.
- [x] Accepted frames and a durable failure closure survive repository recreation, and repeated closure requests do not append duplicates.
- [x] Historical TRUNCATED journal rows and receipt fields remain readable for compatibility, while newly submitted TRUNCATED frames are rejected as historical-only.
- [x] Reference, API and operations documentation plus architecture diagrams explain durability, backpressure, failure closure, 500 millisecond client polling and host-controlled retention; focused checks and the complete Docker-local quality gate pass.

## Implementation completion evidence

- 2026-09-01 — EPIC-834 is complete. Default progress rate/count ceilings are disabled and the PostgreSQL sink no longer generates runtime TRUNCATED events; every valid frame awaits its individual canonical journal commit and receipt, so storage latency supplies lossless producer backpressure. Provider and Pi failure paths durably append one idempotent FAILED closure for an active segment when PostgreSQL is available. PostgreSQL regressions prove complete same-second bursts, individual cursors/evidence, exact retries, conflict rejection, historical marker compatibility, graceful closure and repository-restart durability. Ruff, strict mypy, generated contracts, planning/backlog validation, strict documentation and the complete Docker-local gate passed with 909 backend tests, 122 frontend tests, two application and eight documentation Playwright journeys, all 27 Pi conformance cases, production-image probing and repository/four-SDK packaging.

## Explicit non-goals

- Persisting or exposing hidden chain-of-thought content
- Changing how clients render, collapse or filter accepted progress
- Adding a second broker or volatile acknowledged progress queue
- Removing frame schema, size, chronology, identity, redaction or idempotency validation
- Adding provider-, model-, client- or use-case-specific progress behavior

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-808
- EPIC-812
- EPIC-816
- EPIC-826
- EPIC-828
- EPIC-833

## Architecture impact

- Primary bounded area: `observability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Exercise more than the former same-second default limit and assert every frame is accepted without truncation.
- Verify individual durable receipts, journal rows, cursors and evidence across exact retries, conflicts and repository recreation in PostgreSQL.
- Interrupt provider and Pi progress producers and verify an active segment closes once with durable FAILED progress.
- Verify historical TRUNCATED replay remains compatible while novel TRUNCATED submissions fail before acceptance.
- Run focused domain, harness, task and PostgreSQL tests plus Ruff, strict mypy, planning/documentation drift checks and the complete Docker-local quality gate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] Normal progress volume and cadence cannot produce a new TRUNCATED journal event.
- [x] A progress receipt proves that its individual event is already committed to the canonical PostgreSQL journal.
- [x] Backpressure preserves FIFO chronology without Redis, Kafka, NATS or an acknowledged in-memory queue.
- [x] Caught producer failures close active progress durably and idempotently when the journal is available.
- [x] Restart, exact-retry, conflict, historical-compatibility and high-rate regressions pass against PostgreSQL.
- [x] User, API, operations and architecture documentation and diagrams match the implemented contract.
- [x] Focused verification and the complete Docker-local gate pass with evidence recorded in TESTLOG.md.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- One transaction per accepted frame can slow a fast provider stream, so that latency is an intentional correctness-preserving backpressure signal.
- A database outage prevents both progress acceptance and immediate durable closure, so no receipt is returned and existing lifecycle recovery records the terminal outcome when persistence becomes available.
- Removing default volume ceilings transfers retained-volume capacity planning to the host's existing retention and storage policies.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
