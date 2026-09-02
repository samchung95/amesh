# EPIC-832 — Harness-owned context budgets and DeepSeek V4 parity

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI application developer and agent-session platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Keep workflow agent nodes isolated behind explicit schema-validated inputs and final outputs, delegate model-visible context projection to the replaceable session harness under AMESH-enforced context budgets, and qualify DeepSeek V4 Flash Vision through the same provider-neutral contract as Luna.

## In scope

- [x] An A-to-B-to-C agent workflow does not share private transcripts, hidden reasoning or tool history between nodes; each agent session receives only the workflow input explicitly rendered into that task, validates it against the pinned agent input schema and exposes only its schema-valid final task result for an explicit downstream binding.
- [x] Existing dependency-visible workflow outputs remain available to explicit expressions for compatibility, but dependency order alone never injects an upstream output into a model or harness context and this non-implicit behavior is covered by an executable three-node fixture.
- [x] The provider-neutral AgentSessionHarness request carries the canonical session messages and a calculated context budget containing model context-window tokens, maximum model-input tokens, reserved completion tokens, compaction-trigger tokens, message count and canonical-byte ceilings.
- [x] The configured harness owns model-visible context projection through its native context hook and returns a privacy-safe content-addressed receipt; AMESH retains the append-only canonical transcript and no longer chooses the successful turn's model-visible message subset in the session task.
- [x] The AMESH model gateway permits a harness to change only model-visible messages, rejects message, byte or estimated-token overflow before provider I/O, preserves the immutable provider, model, schema, budget, timeout, continuation, credential and invocation identity, and verifies the returned model result.
- [x] Workflow agent.session nodes and standalone canonical session launches accept the same backwards-compatible contextPolicy, including an optional model context window and completion reserve; the effective maximum input and compaction trigger are deterministic and leave completion headroom.
- [x] Pi uses its locked transformContext seam to preserve pinned instructions and newest complete action/result groups, emits a versioned receipt and remains isolated from provider credentials, native tool authority, repositories and workflow state; v1 and v2 AMESH-produced receipts remain readable for existing checkpoints.
- [x] The exact OpenRouter model deepseek/deepseek-v4-flash-vision-exp is selectable through provider-neutral model policy and guided authoring surfaces and is covered by the same deterministic fixtures as Luna for governed image input, structured output and repair, chronological progress, mediated tools, multi-turn and workflow handoff, compaction, cache, usage, cost, timeout and budget evidence.
- [x] OpenRouter routes that do not enforce JSON Schema provider-side remain usable through AMESH structured-output validation and bounded repair without a DeepSeek-specific core execution path.
- [x] An opt-in OPENROUTER_API_KEY-gated DeepSeek qualification mirrors the Luna journey and writes redacted JUnit evidence; focused tests, harness conformance, generated contracts, strict documentation and Docker-local verification pass without adding GitHub-hosted CI.

## Implementation completion evidence

- 2026-09-01 — ADR-070, the versioned harness request/budget/receipt contracts, Pi protocol v2, standalone and workflow contextPolicy, explicit three-node handoff fixture, exact DeepSeek model profile, guided authoring choice and OpenRouter structured-output routing are implemented.
- 2026-09-01 — GitHub issue #13 is fixed locally through immutable model-profile completion-token defaults and provider-route overrides: Luna azure/eu retains max_completion_tokens, Luna OpenAI routes and DeepSeek use max_tokens, and require_parameters no longer changes the negotiated alias. The 44-test focused regression, Ruff and strict mypy passed.
- 2026-09-01 — The affected provider-free matrix passed 168 tests with three expected live skips; Pi passed six worker tests and all 27 conformance cases. The final complete Docker-local aggregate passed with 907 backend tests, 122 frontend tests, two application and eight documentation Playwright journeys, generated contracts/SDKs, strict documentation, backlog/provenance/REUSE, image and packaging gates.
- 2026-09-01 — Both parameterized plain OpenRouter smoke cases passed before the remaining account credit was exhausted. The operator explicitly accepted deferring the final Luna/DeepSeek Pi session rerun until funded credit is available; safe JUnit evidence is retained at .artifacts/live-openrouter/junit.xml, no protected content is recorded, and no live-provider qualification claim is made.

## Explicit non-goals

- Sharing hidden reasoning, private session transcripts or complete tool histories between workflow nodes
- Changing global workflow expression visibility or unrelated task-output semantics
- Giving a harness provider credentials, native tool effects, policy authority or an authoritative session store
- Adding DeepSeek-specific workflow primitives, tools, prompts or client-domain behavior
- Adding hosted CI, cloud qualification or broker access

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-813
- EPIC-819
- EPIC-824
- EPIC-826
- EPIC-828
- EPIC-830

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Run domain tests for calculated context budgets, legacy receipt loading, deterministic Pi receipts, complete-turn preservation and fail-closed minimum-context overflow.
- Run harness port and Pi worker tests proving transformContext owns the selected messages and an over-budget or identity-mutating call is rejected before the scripted provider is invoked.
- Run agent-session task and API tests for workflow and standalone contextPolicy parity, restart-safe receipt persistence, canonical-transcript preservation and an explicit A-to-B-to-C schema-boundary fixture.
- Run provider-free OpenRouter fixtures parameterized for Luna and deepseek/deepseek-v4-flash-vision-exp across multimodal input, structured validation and repair, progress ordering, tools, continuation, cache, usage, cost, timeout and budgets.
- Run the opt-in live DeepSeek Docker qualification with OPENROUTER_API_KEY and inspect the redacted JUnit evidence without retaining prompts, image bytes, tool arguments or hidden reasoning.
- Run Ruff, strict mypy, Pi npm tests, harness conformance, generated-contract drift, strict documentation, canonical planning validation and the complete Docker-local aggregate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] ADR-070 records harness-owned projection, AMESH hard-limit enforcement, explicit workflow data boundaries and failure behavior, and the implementation matches that contract.
- [x] The session task passes the canonical transcript and calculated context budget to the harness, Pi selects the bounded context through transformContext, and AMESH rejects any over-budget model call before external I/O.
- [x] The canonical transcript remains append-only, successful projections retain durable privacy-safe receipts, and existing v1/v2 checkpoint receipts continue to load.
- [x] Canonical standalone sessions and workflow agent.session nodes expose equivalent contextPolicy controls without changing legacy defaults.
- [x] Three-node tests prove no implicit transcript propagation and schema-valid final-result handoffs, while existing explicitly referenced transitive workflow outputs remain compatible.
- [x] DeepSeek V4 Flash Vision is exposed as an exact model choice and passes the provider-free Luna-parity matrix; the opt-in live qualification passes when a valid OpenRouter key and model route are available.
- [x] Focused, conformance, generated-contract, documentation and complete Docker-local gates pass with evidence recorded in docs/reviews/TESTLOG.md.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A permissive harness model-call mutation boundary could let an adapter alter provider, schema, credentials or budgets; AMESH must allow only bounded message projection and fail before provider I/O.
- A context window without reserved completion headroom can admit a prompt that leaves no room for a result, so the calculated input cap must be strictly below the model window.
- Pi and AMESH message shapes differ for system, image and tool content; conversion must preserve order and governed references without exposing binary data or authority.
- Provider-reported DeepSeek reasoning, cache and structured-output behavior can vary by OpenRouter route; unavailable evidence must remain explicit and AMESH validation remains authoritative.
- Changing receipt ownership must not make existing persisted v1/v2 checkpoints unreadable or change canonical transcript recovery.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
