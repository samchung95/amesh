# EPIC-221 — Docker and OCI task runner

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `runner`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Execute isolated task containers with governed images, mounts, networking and cleanup.

## In scope

- [ ] **URS-F-0265** — The system shall pull images by immutable digest or resolve tags under explicit policy.
- [ ] **URS-F-0266** — The system shall create containers with declared CPU, memory, user, capabilities, filesystem and network restrictions.
- [ ] **URS-F-0267** — The system shall transfer input and output files without exposing the host control plane filesystem.
- [ ] **URS-F-0268** — The system shall stream container logs and collect exit, OOM and runtime diagnostics.
- [ ] **URS-F-0269** — The system shall support rootless engines and remote OCI runtimes where practical.
- [ ] **URS-F-0270** — The system shall enforce image registry allowlists, signature verification and vulnerability policy.
- [ ] **URS-F-0271** — The system shall remove containers, volumes and temporary credentials idempotently after completion.
- [ ] **URS-F-0272** — The system shall avoid mounting the host Docker socket into untrusted task containers.

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

- Functional requirements: URS-F-0265, URS-F-0266, URS-F-0267, URS-F-0268, URS-F-0269, URS-F-0270, URS-F-0271, URS-F-0272
- Non-functional requirements: URS-NFR-SECURITY-008
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
