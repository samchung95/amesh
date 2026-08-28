# AMESH documentation

Use this page as the entry point; canonical product scope and verification evidence live in the
linked source documents rather than duplicated summaries.

## Start and operate locally

- [Repository quick start](../README.md#local-quick-start)
- [First-run onboarding](operations/onboarding.md)
- [Docker-local verification and packaging](how-to/run-local-verification.md)
- [Compact deployment](operations/compact-deployment.md)
- [Authentication](operations/authentication.md) and [authorization](operations/authorization.md)
- [PostgreSQL operations](operations/postgresql.md) and [supported upgrades](operations/upgrades.md)

## Build workflows and agents

- [Flow DSL](../schemas/flow.schema.json) and [API/OpenAPI](api/openapi.json)
- [Agent primitives](api/agent-primitives.md)
- [Bounded agent sessions](how-to/run-bounded-agent-session.md)
- [Agent memory, evaluations and release gates](how-to/configure-agent-memory-evaluations.md)
- [MCP connections](how-to/register-mcp-connection.md)
- [Plugin manifest and SDK entry point](plugin-sdk/manifest.md)

## Understand the system

- [Architecture overview](architecture/README.md)
- [Execution semantics](architecture/execution-semantics.md)
- [API and UI architecture](architecture/api-and-ui.md)
- [ADR index](adr/README.md)
- [Product roadmap](product/roadmap.md) and [MVP boundary](product/mvp-scope.md)

## Evidence and current status

- [Implementation status](../IMPLEMENTATION_STATUS.md)
- [Verification log](../TESTLOG.md)
- [Progress log](../PROGRESS.md)
- [PR #1 risk triage](reviews/mvp-pr-1-risk-triage.md)
- [UI/UX audit](product/ui-audit/README.md)

`requirements/urs.json` and `backlog/epics.json` are the canonical requirement and epic sources.
Generated Markdown, CSV, traceability and issue files must be refreshed through
`scripts/regenerate_planning_artifacts.py` rather than edited independently.
