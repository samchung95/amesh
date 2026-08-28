# EPIC-302 — Trusted in-process plugin runtime

- **Milestone:** M3 — Plugin platform and integration packs
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Operator
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Run selected high-trust plugins with low overhead while containing dependency and lifecycle failures.

## In scope

- [x] **URS-F-0305** — The system shall load only administrator-approved in-process plugins.
- [x] **URS-F-0306** — The system shall initialize and stop plugin components through bounded lifecycle hooks.
- [x] **URS-F-0307** — The system shall isolate plugin namespaces or classloaders where the implementation language supports it.
- [x] **URS-F-0308** — The system shall apply timeouts and circuit breakers to plugin callbacks invoked by control-plane services.
- [x] **URS-F-0309** — The system shall prevent one plugin from registering or overriding another plugin's identities.
- [x] **URS-F-0310** — The system shall report plugin memory, error and latency telemetry.
- [x] **URS-F-0311** — The system shall quarantine a plugin version that repeatedly violates runtime invariants.
- [x] **URS-F-0312** — The system shall document that in-process plugins share the host security boundary.

## Implementation completion evidence

- 2026-08-23 — EPIC-302 is complete. AMESH loads only exact administrator-approved Python package name/version/content-digest triples, imports them under digest-derived private namespaces without changing `sys.path`, invokes bounded async start/stop hooks and dispatches task callbacks through the immutable plugin resolution pinned to the flow revision. Per-package timeout, closed/open/half-open circuit and repeated-invariant quarantine state contain callback failures; registration ownership checks prevent cross-package type overrides. Authorized runtime status and Prometheus metrics expose lifecycle, circuit, error, latency, quarantine, plugin-owned and host-process memory observations. Compose shares `plugin-data` with API and executor. The documented boundary states that namespace isolation is not a security sandbox and trusted plugins share the host process and its permissions. Evidence: [`test_trusted_runtime.py`](../../tests/plugins/test_trusted_runtime.py), generated OpenAPI, [`trusted-in-process-runtime.md`](../../docs/plugin-sdk/trusted-in-process-runtime.md) and [`TESTLOG.md`](../../TESTLOG.md). Untrusted third-party execution remains with EPIC-303.

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-301

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

- Functional requirements: URS-F-0305, URS-F-0306, URS-F-0307, URS-F-0308, URS-F-0309, URS-F-0310, URS-F-0311, URS-F-0312
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
