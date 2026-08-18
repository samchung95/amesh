# EPIC-108 — Recovery, reconciliation and invariant repair

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `reliability`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Continuously detect and safely repair drift caused by process, PostgreSQL, worker, runner or object-storage failure.

## In scope

- [ ] **URS-F-0148** — The system shall scan for expired leases, orphan task runs, stuck executions, missing dispatches and unprojected events.
- [ ] **URS-F-0149** — The system shall rebuild disposable projections from authoritative state and event records.
- [ ] **URS-F-0150** — The system shall apply only idempotent, version-checked repairs and record every repair as an auditable event.
- [ ] **URS-F-0151** — The system shall quarantine ambiguous cases for operator review instead of guessing.
- [ ] **URS-F-0152** — The system shall provide targeted reconciliation by execution, trigger, worker, tenant or time range.
- [ ] **URS-F-0153** — The system shall rate-limit repair work so recovery cannot overwhelm the primary workload.
- [ ] **URS-F-0154** — The system shall publish repair metrics, unresolved invariant counts and runbook links.
- [ ] **URS-F-0155** — The system shall prove recovery scenarios through fault-injection and crash-consistency tests.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-001** — The platform shall not lose an accepted state-changing command after the API or durable PostgreSQL transport acknowledges it. Target: Zero lost acknowledged commands in crash-consistency and failover tests.
- [ ] **URS-NFR-RELIABILITY-007** — Automated reconciliation shall converge recoverable invariant violations without creating new violations. Target: Reference fault scenarios converge within 10 minutes after dependencies recover.

## Dependencies

- EPIC-007
- EPIC-009
- EPIC-100
- EPIC-101

## Architecture impact

- Primary bounded area: `reliability`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Fault-injection, replay and invariant tests.
- Fault-injection tests that terminate services and PostgreSQL connections at every commit, claim and acknowledgement boundary.
- End-to-end recovery suite with invariant counters.
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

- Functional requirements: URS-F-0148, URS-F-0149, URS-F-0150, URS-F-0151, URS-F-0152, URS-F-0153, URS-F-0154, URS-F-0155
- Non-functional requirements: URS-NFR-RELIABILITY-001, URS-NFR-RELIABILITY-007
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
