# EPIC-826 — Multi-tenant agent session service and compatibility gateway

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI application platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Expose AMESH's governed agent-session runtime as an independently consumable multi-tenant product surface so applications can create, observe and control large numbers of bounded user requests from immutable agent revisions without embedding workflow-specific orchestration.

## In scope

- [x] A versioned provider-neutral session API lets an authenticated client create, list, inspect, stream durable events, pause, cancel, resume, retry and retrieve the result of one bounded agent session without first authoring a workflow; a later conversational turn is a new request containing the desired history.
- [x] Each public session maps to exactly one canonical execution, task run, checkpoint journal and evidence bundle; the session plane introduces no second executor, transcript store, queue or source of truth.
- [x] An immutable session profile resolves exact agent, model policy, system prompt, skill, MCP tool, output schema, memory, evaluation, budget and harness revisions before admission, and active sessions cannot silently change those pins.
- [x] Model profiles may reference an existing provider-side fine-tuned model identifier, while model training and dataset upload remain outside AMESH.
- [x] Pi remains the production default behind the typed harness port, while the public API contains no Pi-specific fields and a future conformant harness can serve new sessions without changing client contracts.
- [x] An OpenAI-compatible adapter maps the documented text-only Chat Completions and Responses subset, buffered SSE, profile-pinned structured output, durable usage and error semantics onto the canonical API without claiming compatibility with proprietary ChatGPT session internals.
- [x] Session creation is idempotent and actor-, tenant- and namespace-authorized; the session facade scopes identity and default visibility to the creating AMESH principal, while existing namespace execution VIEW and MANAGE grants remain explicit privileged access to canonical execution records.
- [x] Every model and tool action remains bounded by AMESH authorization, approvals, invocation journals, egress policy, token, cost, turn, tool-call and duration ceilings; the harness receives no provider, MCP or platform credential.
- [x] Cursor-based streams reconnect from durable events and expose safe state, tool, approval, usage, cache, cost, final-result and failure observations without prompts, checkpoint internals, credentials or hidden reasoning.
- [x] Existing tenant quotas plus generated agent-revision, actor and provider-route-set concurrency buckets enforce admission and backpressure, while provider credential quotas and the pinned envelope retain their existing per-provider request, token, cost, turn, tool-call and duration authority.
- [x] Stateless webserver and execution-worker roles recover work through PostgreSQL claims, leases and fencing without sticky sessions, lost accepted results or duplicated governed tool effects.
- [x] The control room and CLI let users choose authorized agent revisions, start sessions, see what is active, follow a simple trace, inspect budgets and harness provenance, stop or recover work and retrieve structured results and safe errors.
- [x] Operators can combine ordinary readiness and aggregate metrics with tenant-authorized session state, durable cursors and canonical execution evidence without creating session-specific process state.
- [x] A published synthetic local reference profile exercises three independent projection repositories, 10,000 durable terminal sessions and 1,000 concurrent logical cursor readers, reports hardware and latency, and clearly separates local PostgreSQL qualification from external-provider, remote-transport and production-HA claims.

## Implementation completion evidence

- 2026-08-29 — EPIC-826 is complete for the published local reference profile. The existing execution reducer and PostgreSQL session journal now expose a provider- and harness-neutral create/list/detail/event-stream/result/control API, CLI and React Session Control Room, plus documented text-only OpenAI Chat Completions and Responses adapters with buffered SSE. Actor-scoped idempotency, owner-first pagination, typed failures, durable usage, immutable capability/budget/harness pins, exact-pin resume rejection, admission buckets and public evidence redaction passed focused contract and PostgreSQL regressions. Pi remains the current exact `pi-agent-core` 0.84.3 adapter behind a registry/factory port; future adapters can implement the same conformance boundary without changing the public API, and arbitrary harness metadata cannot enter public evidence. OpenAPI and Python, TypeScript, Java and Go SDKs regenerated deterministically. The complete Docker-local gate passed 735 backend tests, 97 frontend tests, the Chromium journey, the 23-case Pi conformance suite twice, contract/license/review checks, production-image probing and packaging. The published synthetic PostgreSQL report passed with 10,000 seeded terminal sessions, 1,000 concurrent logical cursor readers, three projection repositories, zero duplicate projection identities, zero cross-tenant events and zero missing seeded final-result projections. The opt-in `openai/gpt-5.6-luna` Pi smoke passed with two model turns, one AMESH-mediated tool effect, structured final output, bounded context evidence and normalized prompt-cache status; external-provider performance and scale, remote transport, production HA, backup and restore qualification remain explicit non-claims. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`agent-session-reference-qualification.json`](../../docs/reference/agent-session-reference-qualification.json), [`agent-session-service.md`](../../docs/api/agent-session-service.md), [`use-agent-session-service.md`](../../docs/how-to/use-agent-session-service.md), [`agent-session-service.md`](../../docs/operations/agent-session-service.md), and [`066-session-plane-over-existing-authorities.md`](../../docs/adr/066-session-plane-over-existing-authorities.md).

## Explicit non-goals

- Creating a second workflow engine, broker, session executor, transcript store or evidence ledger
- Implementing proprietary ChatGPT accounts, history synchronization, UI behavior or hidden protocols
- Training or fine-tuning model weights, uploading training datasets or operating a model registry
- Adding domain-specific assistants, prompts, skills, tools, MCP servers or client adapters
- Replacing application-owned end-user identity or the existing namespace execution authorization model with a new end-user authentication product
- Giving Pi or any future harness direct provider credentials, MCP credentials, native tool execution or workflow-state authority
- Persisting or exposing hidden chain-of-thought or claiming deterministic LLM output
- Hot-swapping a harness, model, prompt, skill, tool, schema or policy revision inside an active session
- Claiming multi-region, production HA or external-provider scale beyond the published local reference profile

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-105
- EPIC-401
- EPIC-403
- EPIC-503
- EPIC-607
- EPIC-807
- EPIC-808
- EPIC-809
- EPIC-811
- EPIC-812
- EPIC-813
- EPIC-814
- EPIC-819
- EPIC-824

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Canonical OpenAPI and application-service contract tests for every lifecycle operation and typed failure.
- OpenAI-compatible fixtures for non-streaming, buffered SSE, pinned structured output, malformed or unsupported requests, durable usage and safe errors.
- Harness-neutral request and provenance tests plus the existing Pi conformance suite.
- PostgreSQL and contract tests for idempotent create, cursor reconnect, immutable harness pins, authorization and tenant isolation.
- Existing recovery and Pi conformance suites plus exact-pin resume tests that reject an adapter, version or protocol change before work.
- Admission tests for tenant quota and generated agent-revision, actor and provider-route-set concurrency buckets.
- React unit and Playwright tests covering creation, active and terminal inspection, lifecycle controls, empty state, harness provenance and accessibility.
- Deterministic synthetic scale run across three independent projection repositories with a machine-readable capacity report.
- Opt-in live OpenRouter openai/gpt-5.6-luna smoke through Pi for one multi-turn structured-output session.
- Complete Docker-local verification aggregate and production-image probe.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] The independently consumable session API, compatibility gateway, CLI and control-room paths run on the existing webserver and execution roles over the canonical execution and session authorities.
- [x] The canonical contract is provider- and harness-neutral; Pi is an exact current pin and another adapter can pass the same conformance boundary without a client API change.
- [x] Focused lifecycle, compatibility, idempotency, tenant-isolation, admission, harness-pin, evidence and UI tests pass with linked machine-readable evidence.
- [x] The published reference workload meets the stated local session-count and concurrency profile without duplicate projection rows, cross-tenant events or missing seeded final-result projections.
- [x] The Docker-local CI aggregate passes, and the opt-in live Luna smoke is recorded separately from the default offline gate.
- [x] API, profile, compatibility, deployment, security, operations and user documentation accurately describe supported behavior and explicit non-claims.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A second session engine or transcript authority would create split-brain state and duplicate external effects; the facade must remain a projection over the existing reducer and journal.
- Provider-compatible streaming and retry semantics can imply stronger delivery guarantees than the durable AMESH event record actually provides unless deviations are explicit.
- High-cardinality session telemetry and long-lived streams can exhaust shared resources unless admission and retention limits are enforced before allocation.
- Harness-specific fields can leak Pi into the public contract and make later adapter substitution a breaking migration.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
