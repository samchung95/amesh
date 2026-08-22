# EPIC-000 — Clean-room governance and parity baseline

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Maintainer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Establish a defensible, repeatable method for reproducing observable capabilities without copying protected expression.

## In scope

- [x] **URS-F-0001** — The system shall maintain a version-pinned parity inventory against Kestra v1.3.30 and its documented public behavior.
- [x] **URS-F-0002** — The system shall record source provenance for every compatibility requirement and prohibit copying source code, UI assets, trademarks, or documentation prose.
- [x] **URS-F-0003** — The system shall separate reference researchers from implementers when a strict clean-room mode is selected.
- [x] **URS-F-0004** — The system shall run automated similarity and license scans before every release.
- [x] **URS-F-0005** — The system shall document trademark-safe naming, attribution, notices, and contribution provenance.
- [x] **URS-F-0006** — The system shall track parity gaps, intentional differences, deferred features, and evidence in a machine-readable matrix.
- [x] **URS-F-0007** — The system shall provide a repeatable procedure for rebasing the parity target to a later upstream release.

## Implementation completion evidence

- 2026-08-22 — EPIC-000 is complete. A generated requirement-level compatibility inventory now pins every functional requirement to the Kestra 1.3.30 target, known public source identifiers, explicit compatible/gap/deferred/intentional-difference disposition and evidence. Strict-mode researcher/implementer/reviewer/verifier handoffs are machine-readable. Local and release gates validate lexical markers, target/provenance coherence, SPDX licensing through REUSE 6.2.0 and isolated one-way token-shingle similarity without emitting reference content. Trademark, attribution and contributor provenance policy remains explicit, and a checked target-rebase procedure preserves clean-room separation. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`compatibility-inventory.json`](../../requirements/compatibility-inventory.json), [`source-provenance.json`](../../requirements/source-provenance.json), [`check_clean_room.py`](../../scripts/check_clean_room.py), [`test_clean_room.py`](../../tests/test_clean_room.py), [`rebase-compatibility-target.md`](../../docs/how-to/rebase-compatibility-target.md) and [`030-versioned-clean-room-evidence-contract.md`](../../docs/adr/030-versioned-clean-room-evidence-contract.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- None

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
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

- Accidental source or UI copying
- Ambiguous compatibility claims
- Trademark confusion

## Traceability

- Functional requirements: URS-F-0001, URS-F-0002, URS-F-0003, URS-F-0004, URS-F-0005, URS-F-0006, URS-F-0007
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
