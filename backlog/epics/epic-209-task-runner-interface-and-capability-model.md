# EPIC-209 — Task runner interface and capability model

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `runner`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Separate task semantics from the environment that executes user code.

## In scope

- [ ] **URS-F-0250** — The system shall define a runner-neutral request containing image or command, files, environment, resources, network and security policy.
- [ ] **URS-F-0251** — The system shall advertise runner capabilities and reject unsupported requests before dispatch.
- [ ] **URS-F-0252** — The system shall return normalized process status, logs, metrics, outputs and infrastructure diagnostics.
- [ ] **URS-F-0253** — The system shall propagate cancellation and timeout with a documented escalation sequence.
- [ ] **URS-F-0254** — The system shall support runner-specific configuration through typed extension fields.
- [ ] **URS-F-0255** — The system shall isolate credentials so a runner receives only the scoped capability required for one attempt.
- [ ] **URS-F-0256** — The system shall clean up orphan runtime resources through idempotent reconciliation.
- [ ] **URS-F-0257** — The system shall allow namespace and worker-group policy to select or prohibit runners.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-008** — Untrusted user code and third-party plugins shall not execute inside the webserver, scheduler, executor or metadata database process. Target: All untrusted reference tasks and plugins run through isolated runners or plugin services.
- [ ] **URS-NFR-PORTABILITY-003** — Core transport semantics shall be isolated from PostgreSQL claim mechanics, while object storage, secret providers, model providers and task runners shall use documented capability interfaces. Target: PostgreSQL remains the sole supported internal durable transport and metadata database; every backend category explicitly marked extensible passes its conformance suite.

## Dependencies

- EPIC-101
- EPIC-200

## Architecture impact

- Primary bounded area: `runner`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Runner contract tests against disposable execution environments.
- Architecture test and runtime process inspection.
- Static architecture checks plus adapter contract tests for each extensible backend category.
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

- Functional requirements: URS-F-0250, URS-F-0251, URS-F-0252, URS-F-0253, URS-F-0254, URS-F-0255, URS-F-0256, URS-F-0257
- Non-functional requirements: URS-NFR-SECURITY-008, URS-NFR-PORTABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
