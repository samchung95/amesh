# EPIC-006 — Flow revisions, change history and promotion

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `domain`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make workflow definitions immutable by revision and safely promotable across environments.

## In scope

- [x] **URS-F-0045** — The system shall create a new immutable revision for each semantic flow change.
- [x] **URS-F-0046** — The system shall show human-readable and machine-readable diffs between revisions.
- [x] **URS-F-0047** — The system shall pin every execution to the exact flow revision and plugin resolution set used at launch.
- [x] **URS-F-0048** — The system shall restore or clone an earlier revision without rewriting history.
- [x] **URS-F-0049** — The system shall support draft, active, disabled and archived lifecycle states.
- [x] **URS-F-0050** — The system shall attach actor, source, commit, environment and deployment metadata to revisions.
- [x] **URS-F-0051** — The system shall prevent incompatible revision deletion while executions or audit records reference it.

## Implementation completion evidence

- 2026-08-22 — EPIC-006 is complete. PostgreSQL now allocates immutable content-addressed revisions for semantic changes, records actor/source/commit/environment/deployment provenance and the exact resource-catalog resolution, exposes authorized history and RFC 6902-compatible diff APIs, supports draft/active/disabled/archived promotion and pointer-based restore, pins executions to revision rows, emits transactional flow revision events/outbox messages and rejects deletion of selected or execution/audit-referenced revisions. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`flow-revisions.md`](../../docs/operations/flow-revisions.md), [`0033_flow_revisions.sql`](../../migrations/0033_flow_revisions.sql) and [`test_flow_revision_api.py`](../../tests/api/test_flow_revision_api.py).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-004

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

- Functional requirements: URS-F-0045, URS-F-0046, URS-F-0047, URS-F-0048, URS-F-0049, URS-F-0050, URS-F-0051
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
