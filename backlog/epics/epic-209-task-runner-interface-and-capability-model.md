# EPIC-209 — Task runner interface and capability model

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `runner`
- **Primary persona:** Platform operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Separate task semantics from the environment that executes user code.

## In scope

- [x] **URS-F-0250** — The system shall define a runner-neutral request containing image or command, files, environment, resources, network and security policy.
- [x] **URS-F-0251** — The system shall advertise runner capabilities and reject unsupported requests before dispatch.
- [x] **URS-F-0252** — The system shall return normalized process status, logs, metrics, outputs and infrastructure diagnostics.
- [x] **URS-F-0253** — The system shall propagate cancellation and timeout with a documented escalation sequence.
- [x] **URS-F-0254** — The system shall support runner-specific configuration through typed extension fields.
- [x] **URS-F-0255** — The system shall isolate credentials so a runner receives only the scoped capability required for one attempt.
- [x] **URS-F-0256** — The system shall clean up orphan runtime resources through idempotent reconciliation.
- [x] **URS-F-0257** — The system shall allow namespace and worker-group policy to select or prohibit runners.

## MVP implementation progress

- 2026-08-21 — W3 verified the accepted MVP slice: a runner port with command, environment, working-directory and deadline inputs; normalized status, output, exit-code and duration results; and fenced cancellation. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) and [`test_process_runner.py`](../../tests/adapters/local/test_process_runner.py).
- 2026-08-21 — W5 verified that the same port drives owned Kubernetes Jobs and returns normalized pod results without changing PostgreSQL attempt fencing. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) and [`test_job_runner.py`](../../tests/adapters/kubernetes/test_job_runner.py). Capability advertisement, policy and the broader runner contract remain open.

## Implementation completion evidence

- 2026-08-22 — EPIC-209 is complete. Contract `1.0` now covers the full runner-neutral request/result surface; local and Kubernetes adapters publish authorized capabilities and validate before dispatch; cancellation, timeout, scoped credentials and typed extensions cross the same fenced port; idempotent reconciliation removes orphan processes/Jobs; and typed namespace/worker-group rules select or prohibit runners. Evidence: [`test_runner_contract.py`](../../tests/test_runner_contract.py), [`test_process_runner.py`](../../tests/adapters/local/test_process_runner.py), [`test_job_runner.py`](../../tests/adapters/kubernetes/test_job_runner.py), [`workers-and-runners.md`](../../docs/architecture/workers-and-runners.md) and [`configuration.md`](../../docs/operations/configuration.md). The runner contribution to shared URS-NFR-SECURITY-008 and URS-NFR-PORTABILITY-003 is verified; language-neutral plugin isolation and the other extensible backend categories remain In Progress with their owning epics.

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

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0250, URS-F-0251, URS-F-0252, URS-F-0253, URS-F-0254, URS-F-0255, URS-F-0256, URS-F-0257
- Non-functional requirements: URS-NFR-SECURITY-008, URS-NFR-PORTABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
