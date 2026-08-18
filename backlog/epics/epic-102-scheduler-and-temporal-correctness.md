# EPIC-102 — Scheduler and temporal correctness

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Create due executions exactly according to declared temporal semantics despite restarts and multiple scheduler replicas.

## In scope

- [ ] **URS-F-0100** — The system shall evaluate cron and interval schedules in explicit IANA time zones.
- [ ] **URS-F-0101** — The system shall define deterministic behavior for daylight-saving gaps, overlaps and historical timezone changes.
- [ ] **URS-F-0102** — The system shall persist next-fire state and acquire scheduler leases using fencing to prevent competing owners.
- [ ] **URS-F-0103** — The system shall recover missed schedules according to catch-up, skip, coalesce or backfill policy.
- [ ] **URS-F-0104** — The system shall apply start, end, disabled, paused and condition constraints before launch.
- [ ] **URS-F-0105** — The system shall deduplicate schedule launches with a stable trigger occurrence identity.
- [ ] **URS-F-0106** — The system shall preview future occurrences and explain why a schedule did or did not fire.
- [ ] **URS-F-0107** — The system shall operate safely with multiple scheduler replicas and PostgreSQL failover or connection interruption.

## Non-functional requirements

- [ ] **URS-NFR-RELIABILITY-003** — The platform shall prevent an expired scheduler, worker or service owner from committing after ownership transfers. Target: Zero accepted stale mutations in lease-expiry and partition tests.
- [ ] **URS-NFR-RELIABILITY-008** — Temporal decisions shall tolerate bounded clock skew and use monotonic time for local deadlines where possible. Target: Correct schedule, lease and timeout behavior with plus or minus 30 seconds node skew.
- [ ] **URS-NFR-PERFORMANCE-003** — Due schedules shall create occurrences within a bounded delay under supported load. Target: Provisional target: p99 within 5 seconds of due time, excluding declared catch-up throttling.

## Dependencies

- EPIC-008
- EPIC-009
- EPIC-100

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Chaos tests with paused processes, network partitions and delayed completions.
- Virtual-clock and multi-node skew tests.
- Virtual-clock and real-time scheduler benchmark.
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

- Functional requirements: URS-F-0100, URS-F-0101, URS-F-0102, URS-F-0103, URS-F-0104, URS-F-0105, URS-F-0106, URS-F-0107
- Non-functional requirements: URS-NFR-RELIABILITY-003, URS-NFR-RELIABILITY-008, URS-NFR-PERFORMANCE-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
