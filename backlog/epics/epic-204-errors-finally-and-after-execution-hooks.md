# EPIC-204 — Errors, finally and after-execution hooks

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run recovery and cleanup logic predictably for task, branch and execution outcomes.

## In scope

- [ ] **URS-F-0211** — The system shall attach error handlers at task-group, flowable and flow scopes.
- [ ] **URS-F-0212** — The system shall select handlers by state, error category, task identity or safe expression.
- [ ] **URS-F-0213** — The system shall execute finally tasks after success, failure or cancellation under documented rules.
- [ ] **URS-F-0214** — The system shall execute after-execution tasks after terminal state persistence and expose the terminal context.
- [ ] **URS-F-0215** — The system shall preserve the primary failure while recording cleanup failures separately.
- [ ] **URS-F-0216** — The system shall prevent cleanup retries or recursive handlers from creating unbounded loops.
- [ ] **URS-F-0217** — The system shall allow handlers to emit notifications, compensation commands and diagnostic artifacts.
- [ ] **URS-F-0218** — The system shall visualize handler execution and its relationship to the primary task graph.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-104
- EPIC-201

## Architecture impact

- Primary bounded area: `workflow`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- DSL validation plus end-to-end workflow conformance tests.
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

- Functional requirements: URS-F-0211, URS-F-0212, URS-F-0213, URS-F-0214, URS-F-0215, URS-F-0216, URS-F-0217, URS-F-0218
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
