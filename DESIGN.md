# Design System

## Direction

AMESH uses a dense-data instrument aesthetic: calm paper surfaces, dark operational chrome and
high-signal status color. Execution evidence should read like an operator's timeline, with compact
monospaced context and clear separation between state, logs, metrics, outputs and artifacts.

## Tokens

- Type: IBM Plex Mono / IBM Plex Sans; scale: 11/12/14/16/28/40.
- Color: `--paper`, `--surface`, `--ink`, `--muted`, `--accent`, `--danger` from
  `frontend/src/styles/tokens.css`.
- Spacing: 4px base — 4/8/12/16/20/24/32/48.
- Radius: `--radius-control` and `--radius-panel`; shadows: `--shadow-low` and `--shadow-high`.

## Components

- Panels use a surface background, one-pixel line border and the panel radius.
- Evidence timelines use a narrow type marker, monospaced timestamp/context and readable body text.
- Empty, loading and error states use the shared asynchronous-state components.
- Interactive controls keep a 44px minimum target and the global visible focus treatment.
- Trigger monitoring pairs a compact health table with an occurrence ledger; decision evidence is
  readable inline and pause/replay actions stay adjacent to the affected resource.
- Guided authoring uses a numbered intent-to-run rail and one focused work surface. Common choices
  lead with described catalog controls; advanced YAML remains available without competing with the
  primary action. Readiness evidence sits beside the launch action and uses the same validation,
  policy, simulation and test vocabulary as the rest of the product.
