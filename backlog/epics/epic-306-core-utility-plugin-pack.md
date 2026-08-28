# EPIC-306 — Core utility plugin pack

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Workflow author
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Ship dependable generic building blocks for control flow, HTTP, files, data conversion and diagnostics.

## In scope

- [x] **URS-F-0336** — The system shall provide HTTP request and download tasks with authentication, retry, pagination and response limits.
- [x] **URS-F-0337** — The system shall provide file compression, archive extraction, checksum, copy, move and delete tasks.
- [x] **URS-F-0338** — The system shall provide JSON, YAML, CSV, XML and text parsing or transformation tasks.
- [x] **URS-F-0339** — The system shall provide sleep, fail, log, return, debug and assertion tasks.
- [x] **URS-F-0340** — The system shall provide webhook, schedule, flow and manual trigger implementations in the core distribution.
- [x] **URS-F-0341** — The system shall provide notification primitives for email and generic webhooks.
- [x] **URS-F-0342** — The system shall apply SSRF, decompression bomb, path traversal and payload size protections.
- [x] **URS-F-0343** — The system shall cover all core utilities with deterministic integration fixtures.

## MVP implementation progress

- 2026-08-21 — W6 verified the accepted in-process utility slice: `core.return` persists native values, `core.log` emits a structured execution-aware record and persists its message, and `core.http` captures JSON/text responses and completes the Kubernetes demo callback. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py), [`test_handlers.py`](../../tests/tasks/test_handlers.py), and [`test_agent_shell_http.py`](../../tests/e2e/test_agent_shell_http.py). The broader utility plugin pack remains open.

## Implementation completion evidence

- 2026-08-23 — EPIC-306 is complete. The built-in catalog and runtime now provide protected HTTP requests and downloads with bearer/basic/API-key auth, shared retry semantics, bounded pagination/redirects/responses and operator-owned private-host policy; workspace-confined ZIP, extraction, checksum, copy, move and delete tasks; deterministic JSON, YAML, CSV, XML and text adapters; sleep, fail, log, return, debug and assertion controls; core manual, webhook, schedule and flow trigger entries backed by the existing execution/occurrence runtime; and SMTP plus generic webhook notification primitives. SSRF, path traversal, symlink, archive expansion/compression-ratio and payload limits fail closed. Evidence: [`test_core_utilities.py`](../../tests/tasks/test_core_utilities.py), [`test_postgres_executor.py`](../../tests/executor/test_postgres_executor.py), [`resource-catalog.json`](../../schemas/resource-catalog.json), [`core-utilities.md`](../../docs/plugin-sdk/core-utilities.md), [`core-utilities.yaml`](../../examples/core-utilities.yaml) and [`TESTLOG.md`](../../TESTLOG.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-300

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
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

- Functional requirements: URS-F-0336, URS-F-0337, URS-F-0338, URS-F-0339, URS-F-0340, URS-F-0341, URS-F-0342, URS-F-0343
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
