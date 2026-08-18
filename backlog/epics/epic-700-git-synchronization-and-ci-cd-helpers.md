# EPIC-700 — Git synchronization and CI/CD helpers

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `devops`
- **Primary persona:** Platform engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Manage workflow resources through source control and automated promotion.

## In scope

- [ ] **URS-F-0694** — The system shall export canonical flows, namespace files, dashboards, apps, tests and policy resources to repository-friendly files.
- [ ] **URS-F-0695** — The system shall apply creates, updates, deletes and moves from Git commits with dry-run and conflict detection.
- [ ] **URS-F-0696** — The system shall support one-way Git-to-platform synchronization as the safe default.
- [ ] **URS-F-0697** — The system shall link deployed revisions to repository, commit, actor, pipeline and environment metadata.
- [ ] **URS-F-0698** — The system shall provide CI helpers for validate, test, diff, plan, apply and deployment status.
- [ ] **URS-F-0699** — The system shall support GitHub, GitLab, Bitbucket and generic Git providers through adapters.
- [ ] **URS-F-0700** — The system shall prevent sync loops and protect UI edits according to declared ownership mode.
- [ ] **URS-F-0701** — The system shall sign or verify deployment provenance where the Git provider supports it.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-006
- EPIC-402
- EPIC-510

## Architecture impact

- Primary bounded area: `devops`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Declarative apply, drift and CI integration tests.
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

- Functional requirements: URS-F-0694, URS-F-0695, URS-F-0696, URS-F-0697, URS-F-0698, URS-F-0699, URS-F-0700, URS-F-0701
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
