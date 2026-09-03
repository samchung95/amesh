# EPIC-822 — Capability catalog and connection wizard

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let users discover, configure, test and attach prompts, skills, plugins, MCP connections and API-backed tools without manual identifiers.

## In scope

- [x] One authorized catalog projection lists capability kind, human label, exact revision, status, schemas, impact, permissions, provider compatibility and attachment constraints.
- [x] Search, filter and detail UI covers prompts, skills, model policies, agent definitions, plugins, MCP connections and resolved tools using existing immutable ledgers.
- [x] Guided connection setup validates endpoint or transport, secret references, allowlists and schemas while plaintext credentials are never returned or persisted in public resource bodies.
- [x] A bounded connection or tool test records redacted evidence, applies ordinary policy and timeouts and cannot perform an undeclared effect.
- [x] Attach actions return canonical exact references consumable by the guided agent node builder.
- [x] Empty, incompatible, denied, unavailable and schema-drift states are actionable and tested.

## Implementation completion evidence

- 2026-08-26 — EPIC-822 is complete. Added one independently authorized, redacted catalog projection over immutable agent-resource, MCP connection/tool and plugin-registry ledgers; server-side filtering; a guided MCP connection wizard; and exact-reference attachment into agent definitions or new guided workflow drafts. Exact connection tests perform discovery only through ordinary secret-binding, egress and timeout policy, compare pinned schemas, and persist fixed-shape redacted audit evidence without invoking tools. Eighteen focused Python/API/PostgreSQL/generated-contract tests, strict mypy, Ruff, 40 frontend assertions, targeted ESLint, the production build, a responsive Playwright journey and a real local MCP HTTP journey passed; the local API/frontend image was rebuilt, readiness stayed full at migration 66, and authenticated deployed catalog/filter plus missing-pin redaction smokes passed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`agent-primitives.md`](../../docs/api/agent-primitives.md), [`register-mcp-connection.md`](../../docs/how-to/register-mcp-connection.md), [`CapabilityCatalog.tsx`](../../frontend/src/features/agents/CapabilityCatalog.tsx), and [`ConnectionWizard.tsx`](../../frontend/src/features/agents/ConnectionWizard.tsx).

## Explicit non-goals

- Bundling client-domain integrations in core
- Persisting plaintext connection secrets

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-300
- EPIC-312
- EPIC-807
- EPIC-814
- EPIC-820

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Cross-resource catalog projection and tenant authorization tests.
- Connection validation, secret-redaction and schema-drift tests.
- Bounded MCP and plugin tool-test integration tests.
- Frontend search, setup, test and attach component tests.
- Responsive Playwright and live local connection journeys.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] Users can discover and attach exact compatible capabilities without copying opaque identifiers.
- [x] Connection tests cannot disclose credentials or bypass ordinary policy and invocation evidence.
- [x] The catalog remains a projection over existing immutable resources rather than a duplicate registry.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Aggregating catalogs can accidentally weaken tenant or resource-level authorization.
- A connection test can become an undeclared effect path if it does more than bounded discovery or explicitly selected invocation.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
