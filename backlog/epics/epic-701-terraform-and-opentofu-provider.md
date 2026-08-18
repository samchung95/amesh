# EPIC-701 — Terraform and OpenTofu provider

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `devops`
- **Primary persona:** Platform engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Manage platform configuration declaratively through standard infrastructure-as-code tooling.

## In scope

- [ ] **URS-F-0702** — The system shall provide resources and data sources for flows, namespaces, files, key-values, dashboards, apps, users, groups, roles, bindings, service accounts, tenants, worker groups and plugin policies.
- [ ] **URS-F-0703** — The system shall implement import, refresh, plan, apply and drift detection with stable identifiers.
- [ ] **URS-F-0704** — The system shall treat secret values as sensitive and avoid returning provider-resolved plaintext.
- [ ] **URS-F-0705** — The system shall support YAML file content and semantic diff suppression where safe.
- [ ] **URS-F-0706** — The system shall generate provider documentation and examples from schemas.
- [ ] **URS-F-0707** — The system shall test provider compatibility against supported platform releases.
- [ ] **URS-F-0708** — The system shall publish signed provider binaries for major operating systems and architectures.
- [ ] **URS-F-0709** — The system shall define behavior for server-managed defaults and immutable fields.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-500

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

- Functional requirements: URS-F-0702, URS-F-0703, URS-F-0704, URS-F-0705, URS-F-0706, URS-F-0707, URS-F-0708, URS-F-0709
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
