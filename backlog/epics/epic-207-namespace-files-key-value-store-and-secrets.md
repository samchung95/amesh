# EPIC-207 — Namespace files, key-value store and secrets

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `workflow`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Offer namespace-scoped shared resources with inheritance and fine-grained access control.

## In scope

- [ ] **URS-F-0234** — The system shall upload, list, download, move, version and delete namespace files through API, UI and CLI.
- [ ] **URS-F-0235** — The system shall resolve inherited namespace files from parent namespaces with explicit precedence.
- [ ] **URS-F-0236** — The system shall create typed key-value entries with optional expiry, metadata and atomic compare-and-set.
- [ ] **URS-F-0237** — The system shall watch or poll key-value changes for supported automation use cases.
- [ ] **URS-F-0238** — The system shall resolve secrets only at execution time and never persist plaintext in flow revisions.
- [ ] **URS-F-0239** — The system shall apply independent read, write, list and use permissions to files, key-values and secrets.
- [ ] **URS-F-0240** — The system shall record access and mutation audit events without revealing protected values.
- [ ] **URS-F-0241** — The system shall support import, export and environment promotion without exporting secret plaintext.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-010
- EPIC-500
- EPIC-506

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

- Functional requirements: URS-F-0234, URS-F-0235, URS-F-0236, URS-F-0237, URS-F-0238, URS-F-0239, URS-F-0240, URS-F-0241
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
