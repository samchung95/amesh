# Sprint UX-01: Find and understand active work

## Outcome

An authenticated operator can identify running or unhealthy work, narrow the view without knowing
internal identifiers, open an execution, and understand its trigger-to-result story without first
using raw JSON, logs, topology or Gantt views.

The target is discovery within 30 seconds and three interactions, and diagnosis of a representative
failed run within 60 seconds.

## Committed backlog

| Card | Deliverable |
|---|---|
| `c102` | Playwright visual audit and exported baseline evidence |
| `c97` | Discoverable schema- and resource-backed selectors |
| `c98` | Mission Control for running work and items needing attention |
| `c99` | Simple ordered execution trace with advanced evidence preserved |
| `c104` | Sprint integration, deployment and acceptance |

Guided workflow creation (`c100`), production determinism assurance (`c101`) and closure of the
umbrella overhaul (`c103`) are deliberately outside this sprint.

## Product and architecture contract

- Preserve the established graphite-and-paper visual system.
- Use existing authorized APIs; the browser never becomes a second runtime authority.
- Present plain-language operational projections first and retain expert evidence under Advanced.
- Use selectors for finite/resource-backed values. Keep text entry for authored names, expressions
  and explicitly selected custom values.
- Keep tenant and namespace context visible, and make loading, empty, stale, denied and redacted
  states understandable.
- Build Mission Control and trace from pure, unit-tested view-model functions so the same evidence
  always produces the same presentation.

ADR-048 records the durable decision. The detailed visual baseline and screenshot inventory live in
[`ui-audit/README.md`](ui-audit/README.md).

## Delivery order

1. Capture desktop, tablet and mobile baselines plus representative non-happy states.
2. Add the shared selector patterns and replace constrained fields in the sprint's primary journeys.
3. Make Mission Control the first dashboard content while preserving saved analytics.
4. Make the ordered simple trace the execution default while preserving every advanced surface.
5. Run focused unit, accessibility and browser checks; rebuild the Compose frontend; perform an
   authenticated live smoke; export after screenshots and reconcile the board.

## Definition of done

- The four child cards satisfy their acceptance criteria and the board reflects verified reality.
- Desktop (1440×900), tablet (768×1024) and mobile (390×844) before/after captures are exported.
- The audited primary journeys have no critical/serious axe findings, unexpected console errors or
  failed requests.
- An authenticated local-Compose smoke demonstrates active, successful and failed execution states.
- Topology, Gantt, logs, data, history, dashboards and YAML authoring remain reachable.
- The rebuilt frontend is deployed and the demo/test instructions match the running product.

## Completion evidence

Completed on 2026-08-24. The deterministic after-state manifest records 19 populated responsive
captures, five representative non-happy states, a two-interaction discovery path, zero critical or
serious axe findings, zero console errors and zero unexpected failed API requests. The authenticated
Compose gate records nonzero running, failed-recently and completed-recently states, opens the live
running task in the simple trace, and verifies that Advanced evidence remains reachable. See
[`ui-audit/screenshots/after/manifest.json`](ui-audit/screenshots/after/manifest.json) and
[`ui-audit/screenshots/live/manifest.json`](ui-audit/screenshots/live/manifest.json).
