# EPIC-801 — Agentic authoring and operational assistant

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** Workflow author
- **Parity scope:** AMESH differentiator; not a Kestra-parity claim

## Outcome

Use AI to assist authoring and diagnosis while keeping changes reviewable and policy-bound.

## In scope

- [ ] **URS-F-0758** — The system shall generate draft flows from natural-language intent using installed plugin schemas and organization examples.
- [ ] **URS-F-0759** — The system shall explain flow behavior, expressions, validation errors and execution failures with cited platform evidence.
- [ ] **URS-F-0760** — The system shall propose minimal patches as reviewable diffs rather than silently mutating active flows.
- [ ] **URS-F-0761** — The system shall run validation, simulation and unit tests before presenting a proposed change.
- [ ] **URS-F-0762** — The system shall respect tenant, namespace, plugin, secret and data-access permissions during retrieval and tool use.
- [ ] **URS-F-0763** — The system shall record model, prompt, context sources, tool calls, cost and user acceptance or rejection.
- [ ] **URS-F-0764** — The system shall require human or policy approval before deployment or high-impact execution actions.
- [ ] **URS-F-0765** — The system shall support provider-neutral models and complete disablement without reducing core platform functionality.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-312
- EPIC-510
- EPIC-800

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

- Functional requirements: URS-F-0758, URS-F-0759, URS-F-0760, URS-F-0761, URS-F-0762, URS-F-0763, URS-F-0764, URS-F-0765
- Non-functional requirements: none specifically mapped
- Source scope: AMESH differentiator; not a Kestra-parity claim
