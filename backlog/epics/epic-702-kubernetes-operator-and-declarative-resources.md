# EPIC-702 — Kubernetes operator and declarative resources

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `devops`
- **Primary persona:** Platform engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Reconcile platform resources from Kubernetes custom resources when Kubernetes is the control environment.

## In scope

- [ ] **URS-F-0710** — The system shall define custom resources for flows, namespaces, files, key-values, dashboards, apps and selected governance resources.
- [ ] **URS-F-0711** — The system shall reconcile desired state through server APIs with status conditions and observed generation.
- [ ] **URS-F-0712** — The system shall support finalizers, deletion policy, retry, backoff and drift detection.
- [ ] **URS-F-0713** — The system shall read credentials from Kubernetes Secrets without copying them into status.
- [ ] **URS-F-0714** — The system shall scope watches and server credentials for multi-cluster or multi-tenant operation.
- [ ] **URS-F-0715** — The system shall emit Kubernetes events and metrics for reconciliation outcomes.
- [ ] **URS-F-0716** — The system shall version custom-resource schemas and provide conversion or migration guidance.
- [ ] **URS-F-0717** — The system shall avoid making Kubernetes etcd authoritative for execution runtime state.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-606

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

- Functional requirements: URS-F-0710, URS-F-0711, URS-F-0712, URS-F-0713, URS-F-0714, URS-F-0715, URS-F-0716, URS-F-0717
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
