# EPIC-203 — Loops, foreach, while and until

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Repeat work over data or conditions while maintaining bounded, resumable state.

## In scope

- [ ] **URS-F-0203** — The system shall iterate over arrays, maps, ranges, batches and streamed item manifests.
- [ ] **URS-F-0204** — The system shall expose stable iteration index, key, value and parent context to each child run.
- [ ] **URS-F-0205** — The system shall apply per-loop parallelism and preserve deterministic output ordering.
- [ ] **URS-F-0206** — The system shall evaluate while and until conditions at documented checkpoints.
- [ ] **URS-F-0207** — The system shall enforce maximum iterations, duration and generated task-run limits.
- [ ] **URS-F-0208** — The system shall resume loops after restart without repeating acknowledged iterations.
- [ ] **URS-F-0209** — The system shall support break, continue and failure aggregation policies.
- [ ] **URS-F-0210** — The system shall store large iteration payloads in object storage rather than execution metadata.

## Non-functional requirements

- [ ] **URS-NFR-PERFORMANCE-006** — The engine and UI shall handle executions with very large expanded task graphs. Target: Provisional target: 100,000 task runs per execution with aggregated UI views and bounded memory.

## Dependencies

- EPIC-005
- EPIC-201

## Architecture impact

- Primary bounded area: `workflow`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- DSL validation plus end-to-end workflow conformance tests.
- Synthetic large-DAG and loop benchmark.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0203, URS-F-0204, URS-F-0205, URS-F-0206, URS-F-0207, URS-F-0208, URS-F-0209, URS-F-0210
- Non-functional requirements: URS-NFR-PERFORMANCE-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
