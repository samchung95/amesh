# EPIC-829 — Comprehensive user documentation site

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `documentation`
- **Primary persona:** Platform user, integrator and operator
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Give new and experienced users one searchable, task-oriented documentation site that accurately explains how AMESH works, how to start it, and how to build, run, inspect, integrate, extend and operate workflows and agent sessions.

## In scope

- [x] A Material for MkDocs site presents the existing documentation taxonomy through responsive navigation, built-in search, deep links, readable code samples and a clear path from beginner journeys to API, operations and architecture reference.
- [x] A source-verified getting-started journey covers prerequisites, environment creation, Docker Compose startup, readiness, the development URL and credentials, the first saved workflow, execution inspection, result retrieval and cleanup without assuming prior AMESH knowledge.
- [x] Concept documentation explains AMESH's execution, PostgreSQL, object-storage, worker, scheduler, plugin, provider, harness, evidence and authorization boundaries in plain language, including what is deterministic and what remains external or model-nondeterministic.
- [x] Workflow documentation explains flows, nodes/tasks, inputs, outputs, expressions, files and governed images, sequential and parallel work, branches, loops, subflows, retries, replay and how to inspect a run, with links to exact schemas and runnable examples.
- [x] Agent documentation explains immutable definitions, system prompts, skills, MCP tools, plugins, model routes, structured outputs, budgets, thinking levels, session harnesses, context compaction, cache evidence, image inputs, chronological progress, later turns and where results are stored.
- [x] Integration documentation provides navigable authentication, REST, OpenAPI, CLI, generated SDK, OpenAI-compatible subset, idempotency, pagination, streaming and error-handling guidance without embedding live credentials or claiming unsupported compatibility.
- [x] Extension documentation routes developers through the current plugin manifest/runtime, ToolProvider and MCP contracts, model-provider adapter and swappable session-harness boundaries with tested entry points and explicit authority limits.
- [x] Operations documentation provides a coherent path through development and compact deployment, configuration, roles, authentication and tenancy, PostgreSQL and object storage, observability, retention, upgrades, backup/restore, session administration and Docker-local quality gates, while retaining explicit non-claims.
- [x] New overview and journey pages link to existing canonical details instead of duplicating them; commands, routes, UI labels, sample identifiers and credentials are checked against current repository behavior and broken internal links fail verification.
- [x] Documentation dependencies are managed by uv; strict site build, navigation/search smoke, responsive browser and axe accessibility checks run locally through Docker; a loopback-only Compose profile serves the built site for user testing.

## Explicit non-goals

- Replacing canonical API schemas, ADRs, requirements, backlog or test evidence with documentation prose
- Publishing or hosting a public internet documentation service in this epic
- Adding product behavior solely to make a documentation journey look complete
- Claiming production, cloud, HA, Kestra or provider compatibility beyond existing measured evidence
- Translating the documentation site into additional languages

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-402
- EPIC-404
- EPIC-600
- EPIC-828

## Architecture impact

- Primary bounded area: `documentation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Run `uv run mkdocs build --strict` with warnings promoted to failures for missing pages, links and anchors.
- Run a Docker-local documentation suite that builds the site and uses Playwright plus axe against the home, getting-started, workflow and agent-session journeys at desktop and tablet widths.
- Validate a fresh Compose startup, first-workflow CLI journey and one provider-free agent-session documentation journey against checked-in examples or focused executable tests.
- Check that the published navigation exposes getting started, concepts, workflows, agents, integrations, extensions, operations, reference and architecture without orphaning required user paths.
- Run canonical planning regeneration, backlog validation, generated-contract drift checks and the complete Docker-local aggregate.
- Acceptance criteria 1 and 9-10: site, strict navigation, uv dependency and Docker-local serving evidence is in [`mkdocs.yml`](../../mkdocs.yml), [`Dockerfile.docs`](../../Dockerfile.docs), [`compose.docs.yaml`](../../compose.docs.yaml), [`frontend/e2e/docs-site.spec.ts`](../../frontend/e2e/docs-site.spec.ts) and [`scripts/verify-local.sh`](../../scripts/verify-local.sh).
- Acceptance criteria 2-8 and definition-of-done journeys: task-oriented source pages start at [`docs/index.md`](../../docs/index.md), [`docs/getting-started/index.md`](../../docs/getting-started/index.md), [`docs/workflows/index.md`](../../docs/workflows/index.md), [`docs/agents/index.md`](../../docs/agents/index.md), [`docs/integrations/index.md`](../../docs/integrations/index.md), [`docs/extensions/index.md`](../../docs/extensions/index.md) and [`docs/operations/index.md`](../../docs/operations/index.md).
- Release evidence: [`TESTLOG.md`](../../TESTLOG.md) records the passing strict build, 8 desktop/tablet search and accessibility journeys, live loopback docs profile probe and complete Docker-local aggregate.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] A new user can follow the documented Docker-local path from clone to healthy UI and successful workflow, then locate its chronological execution result without undocumented knowledge.
- [x] An application developer can understand and run the documented provider-neutral agent-session path, attach prompts, skills, tools/MCP and governed images through their actual owning resources, and retrieve progress and structured results.
- [x] A plugin or integration developer can identify the supported extension boundary and reach the exact manifest, ToolProvider, MCP, model-provider, harness, REST, CLI and SDK references from the site.
- [x] An operator can identify deployment choices, runtime roles, authentication and tenancy, state authorities, observability, lifecycle, migration and recovery guidance together with current qualification limits.
- [x] The strict uv build, link and navigation checks, responsive Playwright/axe journeys, Docker-local docs image/profile and complete local aggregate pass with evidence recorded in TESTLOG.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A large undifferentiated navigation tree can reproduce the repository layout without giving a new user a usable learning path.
- Duplicated commands and behavior summaries can drift from tested API, CLI, Compose and UI contracts.
- Strict link checks can become noisy if generated artifacts or intentionally external references are treated as authored user pages.
- Documentation can accidentally turn a locally qualified behavior into a production or compatibility claim unless non-claims remain adjacent to instructions.
- MkDocs Material 9.7.7 is the current security-fixed implementation baseline, but its upstream maintenance window ends on 2026-11-05; the site keeps framework-specific customization shallow so a Zensical or other successor evaluation can occur without rewriting the content corpus.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
