# EPIC-811 — Client-neutral external orchestration contract

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `api`
- **Primary persona:** Integration developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let any external client version workflows, launch idempotent runs, inspect progress and control executions through a stable neutral contract.

## In scope

- [x] A versioned external-client profile covers validate, apply, read exact revision, idempotent launch, inspect and authorized control operations.
- [x] Client correlation and idempotency keys survive retries and return the same logical run without duplicate decisions.
- [x] Cursor-based realtime events and signed webhooks reconnect without event loss or duplicate delivery effects.
- [x] Stable machine-readable errors distinguish terminal, retryable, conflict and ambiguous outcomes.
- [x] Scopes, tenant isolation, redaction, pagination and optimistic concurrency are enforced consistently.
- [x] A neutral client harness validates the published OpenAPI and generated SDK profile against a live deployment.

## Implementation completion evidence

- 2026-08-26 — EPIC-811 is complete. The versioned `amesh.external-orchestration/v1` profile publishes validate, apply, exact-revision read, idempotent launch, inspect and authorized control operations with correlation, cursor pagination, optimistic concurrency and stable terminal/retryable/conflict/ambiguous error categories. OpenAPI and all generated SDKs expose the same neutral surface, and the uv example harness verifies all nine operations without client-specific code. Eleven focused contract/SDK tests and three live PostgreSQL realtime tests passed. Authenticated Compose execution `01a039c5-4225-735e-b4f7-e7af5d4a5dbc` was returned unchanged for correlation/idempotency key `epic-811-live-restart` before and after an API restart. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`external-orchestration.md`](../../docs/api/external-orchestration.md), [`neutral-client.py`](../../examples/sdk/neutral-client.py), [`test_external_orchestration.py`](../../tests/test_external_orchestration.py), and [`test_realtime_api.py`](../../tests/api/test_realtime_api.py).

## Explicit non-goals

- Adding VibeStonks-specific resources, endpoints or adapter code
- Moving client domain validation or migration logic into AMESH

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-405
- EPIC-810

## Architecture impact

- Primary bounded area: `api`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- OpenAPI and generated SDK compatibility checks for the external-client profile.
- REST contract tests for exact revisions, launch idempotency, correlation, pagination and conflicts.
- Realtime reconnect and signed-webhook duplicate-delivery tests.
- Authenticated live neutral-client harness.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The same documented contract is usable without a client-specific adapter in AMESH.
- [x] All profile operations have authorization, tenant-isolation and stable-error evidence.
- [x] Client integration documentation includes runnable uv-based examples.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A loosely defined client profile can force every consumer to reverse-engineer internal routes.
- Reconnect or retry behavior can create duplicate externally observed decisions.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
