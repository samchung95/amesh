# EPIC-304 — Trigger, condition and notification extension contracts

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Make non-task workflow extensions first-class and durable.

## In scope

- [x] **URS-F-0321** — The system shall support polling triggers with durable checkpoints and normalized occurrence identities.
- [x] **URS-F-0322** — The system shall support realtime triggers with connection lifecycle, backpressure and acknowledgement hooks.
- [x] **URS-F-0323** — The system shall support conditions that return boolean results and explainable evaluation evidence.
- [x] **URS-F-0324** — The system shall support notification plugins that receive typed lifecycle events and delivery policy.
- [x] **URS-F-0325** — The system shall apply retry, timeout, cancellation and secret-scope behavior consistently across extension types.
- [x] **URS-F-0326** — The system shall validate trigger and condition configuration without opening external connections.
- [x] **URS-F-0327** — The system shall provide emulator and fault-injection fixtures for connector developers.

## Implementation completion evidence

- 2026-08-23 — EPIC-304 is complete. Versioned Python SDK contracts and a generated language-neutral schema now cover durable polling checkpoints and normalized identities, lifecycle-aware realtime streams with bounded in-flight acknowledgement, explainable condition results, and typed notification lifecycle events with delivery policies. All four extension paths share bounded retry, timeout, cancellation and manifest-declared secret scoping; trigger and condition configuration validates offline; connector emulators inject duplicates, delays, retryable failures and disconnects. The existing trigger runtime persists polling checkpoints before source acknowledgement and accepts realtime occurrences before acknowledgement, and now closes bounded streams deterministically. Evidence: [`test_extension_contracts.py`](../../tests/plugins/test_extension_contracts.py), [`test_trigger_runtime.py`](../../tests/test_trigger_runtime.py), [`plugin-extensions.schema.json`](../../schemas/plugin-extensions.schema.json), [`extension-contracts.md`](../../docs/plugin-sdk/extension-contracts.md) and [`TESTLOG.md`](../../docs/reviews/TESTLOG.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-103
- EPIC-300

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Functional requirements: URS-F-0321, URS-F-0322, URS-F-0323, URS-F-0324, URS-F-0325, URS-F-0326, URS-F-0327
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
