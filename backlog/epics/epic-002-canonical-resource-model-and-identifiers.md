# EPIC-002 — Canonical resource model and identifiers

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `domain`
- **Primary persona:** Platform developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Define stable resource identities and lifecycle conventions used across APIs, storage, events and permissions.

## In scope

- [x] **URS-F-0015** — The system shall define canonical identifiers for tenants, namespaces, flows, revisions, executions, task runs, triggers, workers, plugins and assets.
- [x] **URS-F-0016** — The system shall validate identifier syntax, reserved words, length limits and case behavior consistently across all interfaces.
- [x] **URS-F-0017** — The system shall use sortable globally unique identifiers for mutable runtime records while preserving user-facing natural keys.
- [x] **URS-F-0018** — The system shall represent labels, annotations, timestamps, actor identity and resource version on every managed resource.
- [x] **URS-F-0019** — The system shall support optimistic concurrency through entity versions or entity tags.
- [x] **URS-F-0020** — The system shall define deletion, archival, tombstone and restoration semantics for each resource type.
- [x] **URS-F-0021** — The system shall serialize resources deterministically for hashing, diffing, signing and cache keys.

## Implementation completion evidence

- 2026-08-21 — EPIC-002 is complete. AMESH now has shared canonical natural-key models for tenants, namespaces, flows, revisions, task runs, triggers, workers, plugins and assets; RFC 9562 UUIDv7 generation for new runtime records; common resource metadata and lifecycle transitions; deterministic hashing/ETags; persisted flow metadata; and REST `If-Match` enforcement. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`test_identity.py`](../../tests/domain/test_identity.py), [`test_resources.py`](../../tests/domain/test_resources.py), [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py), and [`test_mvp_api.py`](../../tests/api/test_mvp_api.py).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- None

## Architecture impact

- Primary bounded area: `domain`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Domain model unit and serialization compatibility tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0015, URS-F-0016, URS-F-0017, URS-F-0018, URS-F-0019, URS-F-0020, URS-F-0021
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
