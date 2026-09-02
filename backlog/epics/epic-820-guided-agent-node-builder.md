# EPIC-820 — Guided agent node builder

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** AI workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let a workflow author configure a valid agent.session node without knowing internal identifiers or writing JSON.

## In scope

- [x] The builder loads authorized tenant-scoped catalogs for exact agent, prompt, skill, model-policy, MCP connection, tool, output-schema and environment revisions.
- [x] Constrained fields use accessible selectors with human labels, compatibility filtering, safe defaults and actionable empty or error states while advanced YAML remains available.
- [x] Guided edits round-trip one canonical workflow YAML document and preserve unsupported advanced fields.
- [x] Authors can preview the resolved capability envelope, budgets, permissions and validation diagnostics before saving.
- [x] A test-node action uses the ordinary admission, simulation and flow-test boundaries without bypassing persistence, policy or credentials.
- [x] Responsive Playwright journeys prove create, validate, test, save and reopen behavior with screenshots and no critical accessibility findings.

## Implementation completion evidence

- 2026-08-26 — EPIC-820 is complete. The AI/model starter now emits canonical agent.session YAML with one compatible authorized AGENT key/revision, mapped request input, synchronized secret-scope contract, repair/data-handling controls and deterministic context bounds. The guide preserves unsupported YAML, previews exact nested prompt/skill/model-policy/evaluation pins, model routes, MCP tools, output schema, memory, permissions and hard budgets, and runs the ordinary fixture-backed isolated flow test after save. Eight focused unit tests, targeted ESLint, the production build, desktop/tablet Playwright create-to-reopen journeys, a 390×844 mobile verification, screenshots and axe checks passed. Deployed live flow epic820.guided.agent_builder_smoke_3030a781@1 validated, passed admission, resolved researcher-3030a781@1, passed its isolated test with zero production executions/artifacts/secret lookups and reopened with the exact pin and context limit; API readiness remained full at migration 66. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`guided-workflow-creation.md`](../../docs/product/guided-workflow-creation.md), [`GuidedWorkflowBuilder.tsx`](../../frontend/src/components/GuidedWorkflowBuilder.tsx), and [`shell.spec.ts`](../../frontend/e2e/shell.spec.ts).

## Explicit non-goals

- Replacing the advanced YAML editor
- Creating credentials or domain-specific tools inside the builder

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-406
- EPIC-807
- EPIC-814
- EPIC-819

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Catalog authorization and compatibility-filtering API tests.
- Canonical YAML round-trip and unsupported-field preservation tests.
- Frontend component, accessibility and production-build checks.
- Desktop, tablet and mobile Playwright create-to-reopen journeys.
- Live local test-node and save smoke test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] A user can configure and save a valid agent.session node using discoverable controls rather than internal identifiers or raw JSON.
- [x] The guided and advanced authoring modes remain projections of the same canonical workflow document.
- [x] Preview and test actions preserve AMESH authorization, policy, budget and evidence boundaries.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A wizard-only state model can drift from canonical workflow YAML.
- Catalog selectors can expose unauthorized revisions or become unusable when compatible choices are empty.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
