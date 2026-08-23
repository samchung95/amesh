# EPIC-704 — Kestra migration importer and conformance suite

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `compatibility`
- **Primary persona:** Migration engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide version-pinned compatibility plus full side-by-side migration of resources, identity and governance configuration, execution history, logs, artifacts and audit evidence.

## In scope

- [x] **URS-F-0726** — The system shall parse Kestra v1.3.30 flow YAML into a source-preserving compatibility model.
- [x] **URS-F-0727** — The system shall map every declared Kestra core property, expression, flowable, trigger, retry, timeout, concurrency, error and output behavior for the pinned target.
- [x] **URS-F-0728** — The system shall classify mappings as exact, compatibility-adapted or blocked; approximate mappings shall not satisfy a full-compatibility release claim.
- [x] **URS-F-0729** — The system shall generate source-located migration patches or adapters without silently discarding or defaulting configuration.
- [x] **URS-F-0730** — The system shall import and round-trip documented namespace files, key-values, labels, revisions, dashboards and export-bundle resources.
- [x] **URS-F-0731** — The system shall run black-box differential scenarios against the pinned Kestra target and AMESH using non-destructive reference plugins.
- [x] **URS-F-0732** — The system shall compare validation, state transitions, task graph, outputs, API payloads, CLI results, timing windows and failure behavior with explicit tolerances.
- [x] **URS-F-0733** — The system shall support side-by-side shadow execution that suppresses, mocks or idempotently isolates external side effects.
- [x] **URS-F-0820** — The system shall provide a version-pinned REST compatibility façade matching declared paths, methods, schemas, pagination, status codes and error classes.
- [x] **URS-F-0821** — The system shall provide a version-pinned CLI compatibility mode matching declared commands, flags, exit codes and machine-readable output.
- [x] **URS-F-0822** — The system shall match declared Pebble parsing, escaping, functions, filters, null behavior and error behavior through differential expression fixtures.
- [x] **URS-F-0823** — The system shall import and export every documented bundle type in the declared compatibility surface without silent information loss.
- [x] **URS-F-0824** — The system shall publish a machine-readable compatibility manifest naming the target version, tested surfaces, evidence and unresolved gaps.
- [x] **URS-F-0825** — The system shall block a full-compatibility release claim when any Must surface remains approximate, unknown or untested.
- [x] **URS-F-0829** — The system shall import and export users, groups, roles, bindings, service accounts, tenants, namespaces, system configuration, plugin inventory and audit configuration through versioned migration bundles.
- [x] **URS-F-0830** — The system shall migrate historical executions, task runs, state events, logs, metrics, artifacts and audit evidence while preserving chronology, provenance and tenant boundaries.
- [x] **URS-F-0831** — The system shall generate a stable source-to-target identifier map and validate referential integrity across resources, revisions, executions, task runs, logs, artifacts and audit records.
- [x] **URS-F-0832** — The system shall perform migration as a dry-runnable, resumable and idempotent side-by-side process with checkpoints, checksums, reconciliation reports and an explicit cutover or rollback plan.
- [x] **URS-F-0833** — The system shall migrate secret references, provider metadata and required bindings without extracting secret plaintext, and shall block cutover when mandatory references remain unresolved.

## Implementation completion evidence

- 2026-08-23 — EPIC-704 is complete for the manifest-declared Kestra 1.3.30 surface. Source-preserving flow import, mapping classifications and patches, bounded REST/CLI/Pebble conformance, safe shadow execution, full checksum-protected migration bundles and a digest-pinned upstream black-box validator passed. The compatibility manifest still blocks a full-version claim for undeclared plugin, complete-Pebble and unimplemented REST/CLI surfaces. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`045-version-pinned-kestra-compatibility-and-migration.md`](../../docs/adr/045-version-pinned-kestra-compatibility-and-migration.md), [`kestra-migration.md`](../../docs/operations/kestra-migration.md), and [`tests/compatibility`](../../tests/compatibility/README.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-000
- EPIC-004
- EPIC-005
- EPIC-510

## Architecture impact

- Primary bounded area: `compatibility`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Black-box differential and migration fixture tests.
- Black-box differential API, CLI, expression and import/export conformance tests.
- Full-fidelity identity and governance migration fixtures.
- Historical execution, log, artifact and audit migration fixtures.
- Identifier-mapping, collision and referential-integrity tests.
- Interrupted, repeated and rolled-back migration end-to-end tests.
- Secret-reference migration, redaction and unresolved-binding tests.
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

- A moving upstream target can make compatibility claims stale.
- Undocumented behavior requires careful black-box fixtures and tolerances.
- Historical data models may not map one-to-one and must never be silently approximated.
- Large migrations require resumability, throttling, storage planning and explicit cutover rehearsal.

## Traceability

- Functional requirements: URS-F-0726, URS-F-0727, URS-F-0728, URS-F-0729, URS-F-0730, URS-F-0731, URS-F-0732, URS-F-0733, URS-F-0820, URS-F-0821, URS-F-0822, URS-F-0823, URS-F-0824, URS-F-0825, URS-F-0829, URS-F-0830, URS-F-0831, URS-F-0832, URS-F-0833
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
