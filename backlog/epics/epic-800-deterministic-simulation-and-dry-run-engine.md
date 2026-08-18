# EPIC-800 — Deterministic simulation and dry-run engine

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Workflow author
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Preview workflow behavior and policy impact without performing undeclared external side effects.

## In scope

- [ ] **URS-F-0750** — The system shall compile a flow revision into an expanded execution plan using supplied sample inputs and trigger context.
- [ ] **URS-F-0751** — The system shall evaluate expressions, conditions, task graph, retries, concurrency keys and policy decisions in simulation mode.
- [ ] **URS-F-0752** — The system shall replace external tasks with declared mocks, recorded fixtures or schema-only placeholders.
- [ ] **URS-F-0753** — The system shall estimate task count, critical path, runner demand, storage, API calls and cost where models exist.
- [ ] **URS-F-0754** — The system shall show unknown or nondeterministic behavior explicitly rather than fabricating results.
- [ ] **URS-F-0755** — The system shall compare simulation plans between flow revisions and plugin sets.
- [ ] **URS-F-0756** — The system shall sign simulation evidence used by promotion gates.
- [ ] **URS-F-0757** — The system shall keep simulator semantics versioned and conformance-tested against the real reducer.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-004
- EPIC-005
- EPIC-100

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Feature-specific end-to-end and policy tests.
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

- Functional requirements: URS-F-0750, URS-F-0751, URS-F-0752, URS-F-0753, URS-F-0754, URS-F-0755, URS-F-0756, URS-F-0757
- Non-functional requirements: none specifically mapped
- Source scope: AMESH differentiator; not a Kestra-parity claim
