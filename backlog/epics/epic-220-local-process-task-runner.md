# EPIC-220 — Local process task runner

- **Milestone:** M2 — Workflow semantics and core runners
- **Priority:** Must
- **Domain:** `runner`
- **Primary persona:** Developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run trusted scripts and commands directly on a worker for local development and controlled environments.

## In scope

- [x] **URS-F-0258** — The system shall execute argv-based commands without implicit shell parsing unless explicitly requested.
- [x] **URS-F-0259** — The system shall set working directory, environment, standard input, user and resource limits.
- [x] **URS-F-0260** — The system shall stream stdout and stderr while preserving ordering metadata and severity mapping.
- [x] **URS-F-0261** — The system shall terminate process groups reliably on cancellation or timeout.
- [x] **URS-F-0262** — The system shall support Linux and macOS development with documented Windows constraints.
- [x] **URS-F-0263** — The system shall disable the runner by default in untrusted multi-tenant deployments.
- [x] **URS-F-0264** — The system shall capture exit code, signal, duration and peak resource use.

## MVP implementation progress

- 2026-08-21 — W3 verified the accepted MVP slice: argv-based local execution without shell parsing, environment and working-directory support, stdout/stderr capture, timeout and cancellation termination, and exit-code/duration capture. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md) and [`test_process_runner.py`](../../tests/adapters/local/test_process_runner.py). Streaming metadata, resource limits and cross-platform process-group qualification remain open.

## Implementation completion evidence

- 2026-08-22 — EPIC-220 is complete. The local adapter now provides literal argv and explicit single-string shell modes; working directory, bounded environment, stdin, POSIX UID and typed resource limits; live ordered severity-mapped stdout/stderr; POSIX process-group and Windows process-tree escalation; fail-closed multi-tenant enablement; and exit/signal/duration/CPU/peak-memory evidence. Evidence: [`test_process_runner_epic220.py`](../../tests/adapters/local/test_process_runner_epic220.py), [`local-process-runner.md`](../../docs/operations/local-process-runner.md) and [`workers-and-runners.md`](../../docs/architecture/workers-and-runners.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-209

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

- Functional requirements: URS-F-0258, URS-F-0259, URS-F-0260, URS-F-0261, URS-F-0262, URS-F-0263, URS-F-0264
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
