# EPIC-510 — Flow unit tests and quality gates

- **Milestone:** M5 — Open governance and enterprise-class controls
- **Priority:** Must
- **Domain:** `governance`
- **Primary persona:** Workflow author
- **Parity scope:** Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation

## Outcome

Test workflow behavior deterministically before deployment or promotion.

## In scope

- [x] **URS-F-0574** — The system shall define tests with a flow revision, inputs, variables, mocked tasks or plugins and expected states or outputs.
- [x] **URS-F-0575** — The system shall simulate expressions, branches, retries, handlers and generated task graphs without external side effects.
- [x] **URS-F-0576** — The system shall run selected tests through API, CLI, UI and CI with machine-readable results.
- [x] **URS-F-0577** — The system shall provide plugin fixtures and recorded responses for external integrations.
- [x] **URS-F-0578** — The system shall measure covered tasks, branches, handlers and conditions without claiming full semantic proof.
- [x] **URS-F-0579** — The system shall require passing tests through namespace promotion or policy gates.
- [x] **URS-F-0580** — The system shall pin test results to flow revision, plugin set and simulator version.
- [x] **URS-F-0581** — The system shall isolate test data, secrets, artifacts and executions from production by default.

## Implementation completion evidence

- 2026-08-23 — EPIC-510 is complete for the local reference profile. Migration 0051 adds tenant-isolated, optimistic-versioned flow-test definitions, immutable run results and namespace quality gates with RLS, grants and audit evidence. The deterministic amesh.flow-test/v1 simulator covers expressions, branches, retries, handlers and generated loop graphs using inline, plugin or recorded fixtures without production executions, artifacts or secret access. API, JSON CLI, graphical Unit tests UI and CI exit codes expose selected runs, observed coverage and exact flow-semantic/plugin-set/simulator pins; enabled gates block ACTIVE promotion and place new revisions in DRAFT until exact tests pass. Focused fresh-PostgreSQL, backend, frontend and Chromium verification passed, generated OpenAPI and four SDKs are current, Compose is healthy at migration 51/51, and the live tests.flowtests.live.promotion_demo gate blocked, passed at 66.67% observed coverage with zero side effects, then promoted. Broader EPIC-800 simulator estimation, plan-diff and signing are not claimed. Evidence: [`flow-tests.md`](../../docs/api/flow-tests.md), [`0051_flow_tests_quality_gates.sql`](../../migrations/0051_flow_tests_quality_gates.sql), [`test_flow_testing.py`](../../tests/test_flow_testing.py), [`test_flow_tests_api.py`](../../tests/api/test_flow_tests_api.py), and [`flow-tests.spec.ts`](../../frontend/e2e/flow-tests.spec.ts).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-004
- EPIC-800

## Architecture impact

- Primary bounded area: `governance`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Authorization, audit and administrative end-to-end tests.
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

- Observed simulator coverage is execution evidence rather than full semantic proof; broad simulator estimation, plan-diff and signing remain scoped to EPIC-800.

## Traceability

- Functional requirements: URS-F-0574, URS-F-0575, URS-F-0576, URS-F-0577, URS-F-0578, URS-F-0579, URS-F-0580, URS-F-0581
- Non-functional requirements: none specifically mapped
- Source scope: Publicly documented Kestra enterprise-class capability; independent fully-OSS implementation
