# EPIC-109 — Task and execution cache

- **Milestone:** M1 — Single-node durable engine
- **Priority:** Must
- **Domain:** `engine`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Reuse deterministic task results without hiding provenance or serving stale data unexpectedly.

## In scope

- [ ] **URS-F-0156** — The system shall derive cache keys from declared inputs, code or plugin version, flow revision and selected contextual values.
- [ ] **URS-F-0157** — The system shall support explicit cache time-to-live, namespace, scope and invalidation policy.
- [ ] **URS-F-0158** — The system shall store outputs, metrics and artifact references with the cached result.
- [ ] **URS-F-0159** — The system shall prevent reuse across tenants or security contexts unless explicitly permitted.
- [ ] **URS-F-0160** — The system shall explain cache hit, miss, bypass and invalidation reasons in execution details.
- [ ] **URS-F-0161** — The system shall allow users to disable, refresh or purge caches by key prefix and resource scope.
- [ ] **URS-F-0162** — The system shall handle concurrent cache population with single-flight or safe duplicate computation.
- [ ] **URS-F-0163** — The system shall include cache provenance in lineage and audit records.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-002** — State, admission, retry, cache, policy and authorization decisions shall expose human-readable evidence to authorized users. Target: Decision evidence is present in all catalogued decision scenarios.

## Dependencies

- EPIC-010
- EPIC-100

## Architecture impact

- Primary bounded area: `engine`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated unit, integration, crash-recovery and conformance tests.
- Scenario-based UI and API acceptance tests.
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

- Functional requirements: URS-F-0156, URS-F-0157, URS-F-0158, URS-F-0159, URS-F-0160, URS-F-0161, URS-F-0162, URS-F-0163
- Non-functional requirements: URS-NFR-USABILITY-002
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
