# EPIC-312 — AI, agent and MCP plugin pack

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Integrate model calls and tool-using agents without making the core engine provider-specific.

## In scope

- [ ] **URS-F-0383** — The system shall provide provider-neutral chat, embedding, structured-output and tool-call tasks.
- [ ] **URS-F-0384** — The system shall support model endpoint, credential, budget, timeout, retry and data-handling policy.
- [ ] **URS-F-0385** — The system shall expose workflows and approved operations through an authenticated MCP server.
- [ ] **URS-F-0386** — The system shall invoke external MCP tools through scoped allowlists and auditable tool calls.
- [ ] **URS-F-0387** — The system shall store prompts, model parameters, usage, cost and response provenance subject to redaction policy.
- [ ] **URS-F-0388** — The system shall validate structured outputs against JSON Schema before downstream use.
- [ ] **URS-F-0389** — The system shall require approval or policy checks for high-impact tools and sensitive data movement.
- [ ] **URS-F-0390** — The system shall support replay with pinned model and prompt metadata while acknowledging provider nondeterminism.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-303
- EPIC-508

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Functional requirements: URS-F-0383, URS-F-0384, URS-F-0385, URS-F-0386, URS-F-0387, URS-F-0388, URS-F-0389, URS-F-0390
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
