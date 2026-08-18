# EPIC-005 — Expression and templating engine

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `dsl`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Provide deterministic runtime rendering for dynamic workflow values without granting arbitrary code execution.

## In scope

- [ ] **URS-F-0037** — The system shall render scalar, collection and object values against a documented execution context.
- [ ] **URS-F-0038** — The system shall support conditions, filters, functions, date operations, collection operations, JSON and YAML conversion and safe string handling.
- [ ] **URS-F-0039** — The system shall expose flow, execution, task-run, trigger, input, output, variable, label, namespace, secret and key-value contexts.
- [ ] **URS-F-0040** — The system shall distinguish compile-time validation from runtime rendering failures.
- [ ] **URS-F-0041** — The system shall sandbox expression evaluation with bounded time, memory, recursion and output size.
- [ ] **URS-F-0042** — The system shall redact secret-derived values from previews, errors and logs.
- [ ] **URS-F-0043** — The system shall provide compatibility tests for the selected Kestra Pebble expression subset.
- [ ] **URS-F-0044** — The system shall allow future expression engines through a stable adapter without changing flow storage.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-004

## Architecture impact

- Primary bounded area: `dsl`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Parser, schema, rendering and compatibility tests.
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

- Functional requirements: URS-F-0037, URS-F-0038, URS-F-0039, URS-F-0040, URS-F-0041, URS-F-0042, URS-F-0043, URS-F-0044
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
