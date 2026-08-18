# EPIC-223 — Cloud batch, VM and serverless runners

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Should
- **Domain:** `runner`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Offload task execution to managed cloud compute through interchangeable adapters.

## In scope

- [ ] **URS-F-0281** — The system shall define adapter contracts for batch jobs, temporary virtual machines and serverless job services.
- [ ] **URS-F-0282** — The system shall submit jobs with deterministic external identifiers and idempotency tokens.
- [ ] **URS-F-0283** — The system shall poll or subscribe to state while tolerating eventual consistency and API throttling.
- [ ] **URS-F-0284** — The system shall stream or collect logs and outputs through cloud-native storage integrations.
- [ ] **URS-F-0285** — The system shall cancel and reconcile externally running jobs after control-plane failure.
- [ ] **URS-F-0286** — The system shall map provider failure states into normalized runner failure categories.
- [ ] **URS-F-0287** — The system shall estimate and record provider resource usage and cost metadata.
- [ ] **URS-F-0288** — The system shall ship reference adapters for at least one AWS, Azure and Google Cloud service before GA.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-209
- EPIC-309

## Architecture impact

- Primary bounded area: `runner`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Runner contract tests against disposable execution environments.
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

- Functional requirements: URS-F-0281, URS-F-0282, URS-F-0283, URS-F-0284, URS-F-0285, URS-F-0286, URS-F-0287, URS-F-0288
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
