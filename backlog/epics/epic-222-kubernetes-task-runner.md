# EPIC-222 — Kubernetes task runner

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `runner`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run task attempts as isolated Kubernetes resources across configured clusters.

## In scope

- [ ] **URS-F-0273** — The system shall create Jobs or Pods from a typed runner request and configurable templates.
- [ ] **URS-F-0274** — The system shall select cluster, namespace, service account, node placement and runtime class through policy.
- [ ] **URS-F-0275** — The system shall apply resource requests, limits, security context, network policy and ephemeral storage limits.
- [ ] **URS-F-0276** — The system shall stream logs and status despite API reconnects or worker restarts.
- [ ] **URS-F-0277** — The system shall collect outputs through object storage or a controlled sidecar mechanism.
- [ ] **URS-F-0278** — The system shall propagate cancellation and delete owned resources using finalizers and idempotent cleanup.
- [ ] **URS-F-0279** — The system shall distinguish scheduling, image, infrastructure, eviction and user-process failures.
- [ ] **URS-F-0280** — The system shall support workload identity without long-lived cloud credentials.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-008** — Untrusted user code and third-party plugins shall not execute inside the webserver, scheduler, executor or metadata database process. Target: All untrusted reference tasks and plugins run through isolated runners or plugin services.

## Dependencies

- EPIC-209
- EPIC-612

## Architecture impact

- Primary bounded area: `runner`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Runner contract tests against disposable execution environments.
- Architecture test and runtime process inspection.
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

- Functional requirements: URS-F-0273, URS-F-0274, URS-F-0275, URS-F-0276, URS-F-0277, URS-F-0278, URS-F-0279, URS-F-0280
- Non-functional requirements: URS-NFR-SECURITY-008
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
