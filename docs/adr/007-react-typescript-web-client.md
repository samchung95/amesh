# ADR-007: React/TypeScript web client

- **Status:** Accepted
- **Decision question:** Q-007
- **Date:** 2026-08-15

## Context

AMESH needs a schema-aware code editor, visual topology, execution timeline, dashboards and administration UI without cloning Kestra’s visual design.

## Decision

Use React and TypeScript for the primary web application. Consume only versioned public REST and realtime APIs. Maintain AMESH-owned design tokens, component contracts and WCAG 2.2 AA acceptance tests.

## Consequences

- Strong ecosystem for editors, graph views and generated clients.
- Frontend and backend remain independently deployable and contract-tested.
- A design-system selection is still required, but framework selection is closed.

## Revisit triggers

- React no longer meets accessibility, performance or maintenance requirements.
- A native client requires a separate UI technology without changing the web contract.

## Traceability

See `EPIC-404` through `EPIC-411` and `docs/architecture/api-and-ui.md`.
