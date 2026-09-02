# EPIC-107 — Subflows, dependencies and system flows

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Compose workflows while preserving parent-child state, outputs, cancellation and authorization.

## In scope

- [x] **URS-F-0140** — The system shall invoke another flow by tenant, namespace, identifier and selected or current revision.
- [x] **URS-F-0141** — The system shall pass typed inputs, labels, correlation and trace context from parent to child.
- [x] **URS-F-0142** — The system shall choose synchronous wait, asynchronous launch or detached invocation semantics.
- [x] **URS-F-0143** — The system shall propagate success, failure, cancellation, pause and restart according to explicit policy.
- [x] **URS-F-0144** — The system shall map child outputs and artifacts back to the parent with schema validation.
- [x] **URS-F-0145** — The system shall prevent recursive invocation beyond configured depth and detect dependency cycles.
- [x] **URS-F-0146** — The system shall support privileged system flows for notifications, governance and operational automation.
- [x] **URS-F-0147** — The system shall authorize parent and child resources independently and record cross-namespace access.

## Implementation completion evidence

- 2026-08-22 — EPIC-107 is complete. The `core.subflow` task now launches current or pinned child revisions in synchronous, asynchronous or detached mode and persists tenant-scoped parent/child lineage with invocation identity, depth, policy, actor and cross-namespace evidence. Typed inputs, inherited labels, correlation/trace context, schema-validated output and artifact mappings, cycle/depth rejection, configurable state/restart propagation and privileged system-flow authorization are covered by engine and API tests. Authorized child and parent relationship endpoints expose the durable graph. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`0018_subflow_relationships.sql`](../../migrations/0018_subflow_relationships.sql), [`test_subflows.py`](../../tests/executor/test_subflows.py), and [`test_subflow_api.py`](../../tests/api/test_subflow_api.py).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-100

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
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

- Functional requirements: URS-F-0140, URS-F-0141, URS-F-0142, URS-F-0143, URS-F-0144, URS-F-0145, URS-F-0146, URS-F-0147
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
