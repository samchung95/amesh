# EPIC-203 — Loops, foreach, while and until

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Repeat work over data or conditions while maintaining bounded, resumable state.

## In scope

- [x] **URS-F-0203** — The system shall iterate over arrays, maps, ranges, batches and streamed item manifests.
- [x] **URS-F-0204** — The system shall expose stable iteration index, key, value and parent context to each child run.
- [x] **URS-F-0205** — The system shall apply per-loop parallelism and preserve deterministic output ordering.
- [x] **URS-F-0206** — The system shall evaluate while and until conditions at documented checkpoints.
- [x] **URS-F-0207** — The system shall enforce maximum iterations, duration and generated task-run limits.
- [x] **URS-F-0208** — The system shall resume loops after restart without repeating acknowledged iterations.
- [x] **URS-F-0209** — The system shall support break, continue and failure aggregation policies.
- [x] **URS-F-0210** — The system shall store large iteration payloads in object storage rather than execution metadata.

## Implementation completion evidence

- 2026-08-22 — EPIC-203 functional scope is complete. Durable foreach loops consume arrays, sorted maps, ranges, batches and streamed JSONL manifests with stable iteration context, bounded parallelism and deterministic aggregates. While and until checkpoints, expansion limits, restart recovery, break/continue and all failure policies are verified against PostgreSQL. Large aggregates spill through the tenant-scoped object-store port, and execution graphs expose bounded per-template summaries. The shared 100,000-task-run UI NFR remains In Progress under EPIC-407. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`execution-semantics.md`](../../docs/architecture/execution-semantics.md), [`loops.yaml`](../../examples/loops.yaml), [`test_loops.py`](../../tests/executor/test_loops.py), [`test_api.py`](../../tests/test_api.py) and [`FlowGraphView.tsx`](../../frontend/src/features/workflows/FlowGraphView.tsx).

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

- Functional requirements: URS-F-0203, URS-F-0204, URS-F-0205, URS-F-0206, URS-F-0207, URS-F-0208, URS-F-0209, URS-F-0210
- Non-functional requirements: URS-NFR-PERFORMANCE-006
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
