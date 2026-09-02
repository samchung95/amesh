# EPIC-836 — Subscription and CLI-backed model engines

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI application developer and agent-session platform operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let authorized users select supported subscription-backed OpenAI Codex and GitHub Copilot runtimes behind the same provider-neutral AMESH model-engine contract as direct API providers.

## In scope

- [x] A versioned provider-neutral model-engine port represents direct HTTP providers, OpenAI Codex App Server and the GitHub Copilot SDK/CLI runtime without leaking engine-specific fields into workflow or agent-session contracts.
- [x] The OpenAI engine uses only the officially documented Codex App Server managed ChatGPT browser or device-code OAuth flow, reports account, plan, rate-limit and token-activity signals when available, and never scrapes cookies or reuses undocumented ChatGPT tokens.
- [x] The GitHub engine uses the officially documented Copilot SDK and version-pinned CLI runtime or its documented JSONL programmatic contract, with supported GitHub OAuth or token authentication and explicit per-user credential isolation.
- [x] Engine capability negotiation covers model selection, reasoning effort, text and image input, structured final output, chronological progress, continuation/session resume, tools, context compaction, timeout/cancellation and usage evidence; unsupported capabilities fail before external work.
- [x] Subscription quota, rate-limit windows and AI-credit usage remain distinct from API token pricing: cost is exact only when the engine reports a billable value and is otherwise marked unavailable or quota-backed rather than synthesized.
- [x] Each tenant or credential binding receives an isolated engine home/session store, encrypted credential lifecycle and audited login/logout/revocation flow; one user's CLI or app-server account cannot be inherited by another session.
- [x] Runtime processes are pinned, health-checked, cancellable and sandboxed with least-privilege tools and paths; AMESH keeps durable execution, policy, progress, output validation and evidence authority.
- [x] Provider-free fakes and conformance fixtures cover both engines, opt-in live qualifications require operator-supplied subscription authentication, and all verification remains Docker-local without GitHub Actions.

## Implementation completion evidence

- 2026-09-02 — EPIC-836 is complete at its provider-free and operator-authorized deployment boundary. A stable engineRef contract now routes direct HTTP, official Codex App Server and GitHub Copilot CLI engines; isolated server-owned account homes, audited status/login/logout APIs, capability preflight, chronological progress, image input, structured output, continuation, context, timeout/cancellation and truthful quota/usage evidence are covered by deterministic process fixtures and production-dispatch regressions. Engine-native tools, MCP, remote access and updater behavior fail closed. Ruff, strict mypy, generated OpenAPI and four SDKs, strict documentation, independent Fable 5 review and the complete Docker-local gate passed. Live subscription qualification remains an explicit opt-in operation because each isolated binding requires the operator to approve the official browser/device login; AMESH neither copies the workstation CLI identity nor scrapes tokens.

## Explicit non-goals

- Cookie, browser-storage or undocumented token scraping
- Treating a ChatGPT or Copilot subscription as an OpenAI API key
- Sharing one interactive CLI identity across unrelated tenants
- Bypassing AMESH tool policy, structured-output validation, journals or execution budgets
- Adding GitHub Actions or hosted CI

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-501
- EPIC-503
- EPIC-813
- EPIC-819
- EPIC-824
- EPIC-826
- EPIC-835

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Record the version-pinned capability and authentication matrix from the official OpenAI Codex App Server and GitHub Copilot SDK/CLI documentation before implementation.
- Run the common model-engine conformance kit against deterministic fake Codex App Server and Copilot runtime processes for streaming, structured output, images, tools, resume, compaction, cancellation and failure mapping.
- Run tenant-isolation tests with separate engine homes and credential bindings, including login, refresh, logout, revocation and process restart.
- Run usage tests proving subscription quota and token activity never become fabricated API dollar cost.
- Run opt-in live OpenAI ChatGPT-subscription and GitHub Copilot qualifications using user-owned browser/device or OAuth authentication without recording protected tokens.
- Run Ruff, strict mypy, generated contracts and SDKs, strict documentation, canonical planning validation and the complete Docker-local aggregate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] Clients can select direct API, OpenAI subscription-backed Codex or GitHub Copilot through one stable AMESH engine selection contract.
- [x] Both subscription engines use only documented authentication and programmatic interfaces, with isolated identities and revocable credentials.
- [x] The common capability, progress, structured-result, timeout, cancellation, context and evidence contract passes for each supported engine.
- [x] Quota and cost semantics are truthful and provider-reported rather than inferred.
- [x] Deployment and administration documentation explains per-user login, runtime isolation, migration and unsupported capabilities.
- [x] Focused verification and the complete Docker-local gate pass with evidence recorded in docs/reviews/TESTLOG.md.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Subscription and CLI terms, quotas and supported interfaces can change, so adapters and qualifications must pin exact documented versions.
- CLI-backed runtimes own local session and credential state that must be isolated per authorized binding in a multi-tenant server.
- Neither subscription engine guarantees API-style dollar cost fields, so billing evidence can remain quota-backed or unavailable.
- Engine-native tools and filesystem permissions could exceed an AMESH capability envelope unless denied by default and explicitly mapped.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
