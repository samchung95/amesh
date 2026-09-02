# EPIC-703 — Public SDKs and embedded integration libraries

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** Application developer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Integrate the orchestrator into applications using supported language libraries.

## In scope

- [x] **URS-F-0718** — The system shall publish supported SDKs for Python, JavaScript or TypeScript, Java and Go.
- [x] **URS-F-0719** — The system shall provide typed models, authentication, retries, idempotency, pagination, streaming and error helpers.
- [x] **URS-F-0720** — The system shall support execution launch, monitoring, cancellation, logs, artifacts and webhook verification.
- [x] **URS-F-0721** — The system shall maintain semantic-version compatibility aligned with API support policy.
- [x] **URS-F-0722** — The system shall generate most models from OpenAPI while hand-crafting ergonomic high-level operations.
- [x] **URS-F-0723** — The system shall publish examples for web applications, CLIs, CI systems and event consumers.
- [x] **URS-F-0724** — The system shall test SDKs against live conformance environments in the release qualification gate.
- [x] **URS-F-0725** — The system shall document thread safety, async support and transport customization.

## Implementation completion evidence

- 2026-08-23 — EPIC-703 is complete for the locally reproducible release profile. The pinned OpenAPI generator produces typed Python, TypeScript, Java and Go packages, then copies compact language-native execution facades for authenticated idempotent launch, bounded safe retry, terminal waiting, fenced cancellation, logs, artifacts, NDJSON streaming, normalized errors and replay-bounded webhook verification. Python sync/async, TypeScript async, Java and Go concurrency and injectable transports are documented. Web, CLI, CI and event-consumer examples are checked in. The Docker-local gate compiles and unit-tests all clients, then the local conformance profile runs the four-language launch/get/wait/log/artifact scenario. No hosted GitHub CI or release publication is claimed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`sdks.md`](../../docs/api/sdks.md), [`044-generated-sdks-with-handwritten-execution-facades.md`](../../docs/adr/044-generated-sdks-with-handwritten-execution-facades.md), [`test_python_execution_client.py`](../../tests/sdk/test_python_execution_client.py), and [`examples/sdk`](../../examples/sdk/README.md).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-401

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- OpenAPI contract and authenticated end-to-end API tests.
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

- Public PyPI, npm and Maven Central registry publication requires operator-owned registry accounts; deterministic checked-in packages and locally generated archives/checksums are the qualified release surface.
- Live conformance covers the local Kubernetes profile; independently operated remote environments can point the same release tests at their endpoint and credential.

## Traceability

- Functional requirements: URS-F-0718, URS-F-0719, URS-F-0720, URS-F-0721, URS-F-0722, URS-F-0723, URS-F-0724, URS-F-0725
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
