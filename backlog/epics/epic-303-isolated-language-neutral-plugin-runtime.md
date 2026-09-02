# EPIC-303 — Isolated language-neutral plugin runtime

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Plugin developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Execute third-party plugins out of process or in OCI sandboxes through a language-neutral protocol.

## In scope

- [x] **URS-F-0313** — The system shall define an RPC protocol for schema discovery, validation, execution, cancellation, heartbeats, logs, metrics and artifacts.
- [x] **URS-F-0314** — The system shall launch plugin services as managed local processes, containers or remote endpoints.
- [x] **URS-F-0315** — The system shall authenticate every plugin session with short-lived workload identity.
- [x] **URS-F-0316** — The system shall grant per-call capabilities for secrets, files, network destinations and platform APIs.
- [x] **URS-F-0317** — The system shall enforce CPU, memory, wall-time, output and concurrency limits.
- [x] **URS-F-0318** — The system shall restart crashed plugin services without losing durable task ownership semantics.
- [x] **URS-F-0319** — The system shall support SDKs for at least Python, Java, JavaScript or TypeScript and Go before GA.
- [x] **URS-F-0320** — The system shall version the wire protocol and negotiate compatible features.

## Implementation completion evidence

- 2026-08-23 — EPIC-303 is complete for the managed local-process profile. AMESH supervises exact revision-pinned third-party packages outside platform processes through versioned JSON-RPC 2.0 newline frames covering manifest/schema discovery, validation, execution, cancellation, heartbeats, logs, metrics and artifacts. Every session negotiates required features and uses a short-lived workload token; every call receives only declared-and-resolved secrets/files, declared egress, fresh capability tokens and administrator-approved platform APIs. Per-package concurrency plus child-tree CPU, memory, wall-time and combined output/frame limits fail deterministically. Unexpected exits and heartbeat loss are retryable, and a PostgreSQL-backed executor test proved a crashed service restarts on attempt two while retaining the same durable task run. The generated wire schema and Python service SDK plus compile-verified Java, TypeScript and Go contracts are documented. Authorized runtime status exposes starts, restarts, crashes, active/completed calls, PID and stable error codes. Evidence: [`test_isolated_runtime.py`](../../tests/plugins/test_isolated_runtime.py), [`test_wire_sdks.py`](../../tests/plugins/test_wire_sdks.py), [`plugin-wire.schema.json`](../../schemas/plugin-wire.schema.json), [`isolated-runtime.md`](../../docs/plugin-sdk/isolated-runtime.md) and [`TESTLOG.md`](../../docs/reviews/TESTLOG.md). Shared URS-NFR-SECURITY-002 and URS-NFR-SECURITY-008 remain In Progress for their other owning epics and deployment-level privilege/isolation qualification.

## Non-functional requirements

- [ ] **URS-NFR-SECURITY-002** — Components, workers, plugins and runners shall receive only the identities and capabilities required for their role and current operation. Target: Reference deployments pass privilege review with no shared administrator credentials.
- [ ] **URS-NFR-SECURITY-008** — Untrusted user code and third-party plugins shall not execute inside the webserver, scheduler, executor or metadata database process. Target: All untrusted reference tasks and plugins run through isolated runners or plugin services.

## Dependencies

- EPIC-300
- EPIC-209

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Plugin SDK contract, sandbox and integration tests.
- Threat-model review and deployment policy tests.
- Architecture test and runtime process inspection.
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

- Functional requirements: URS-F-0313, URS-F-0314, URS-F-0315, URS-F-0316, URS-F-0317, URS-F-0318, URS-F-0319, URS-F-0320
- Non-functional requirements: URS-NFR-SECURITY-002, URS-NFR-SECURITY-008
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
