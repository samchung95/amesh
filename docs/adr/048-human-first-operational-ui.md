# ADR-048: Human-first operational UI projections

## Status

Accepted

## Context

AMESH already exposes broad workflow, execution and governance capability, but its default UI makes
operators assemble an answer from analytics, topology, Gantt, logs, data and history. Constrained
values are also frequently entered as opaque identifiers. The product therefore has the evidence
needed to answer “what is running?” and “why did this run stop?”, but does not present those answers
as the primary experience.

The UI must become easier to operate without creating a second source of runtime truth, hiding the
advanced evidence surfaces, or weakening tenant and namespace authorization.

## Decision

1. The dashboard's primary projection is **Mission Control**: state counts, running work and items
   needing attention. Saved analytics remain available below this operational summary.
2. An execution opens on a **simple trace**: a stable ordered projection of persisted execution,
   task-run, subflow, intervention and lifecycle evidence. Topology, Gantt, logs, data and history
   remain available under progressive disclosure.
3. Finite and resource-backed values use shared accessible selectors populated from the existing
   authorized APIs. Free text remains only for authored names, expressions and intentional custom
   values. Human labels are shown alongside stable identifiers where ambiguity is possible.
4. These UI models are pure projections. They do not infer or mutate scheduler state, manufacture
   events, or become authoritative. Streaming updates invalidate or merge server-backed data while
   persisted evidence remains the source of truth.
5. Tenant and namespace boundaries are always visible. Empty, loading, stale, redacted and denied
   states are explicit and do not reveal unavailable catalog values.
6. The graphite-and-paper design language remains. Responsive behavior prioritizes running work,
   failed/waiting steps and the next action before analytics or expert controls.

No new service or frontend dependency is introduced for this sprint.

### Selector build-versus-buy

Use labelled native `select` controls for a single finite choice and native checkbox groups for the
small multi-value catalogs in this sprint. MDN recommends native selects or checkbox groups before a
custom ARIA listbox because the browser supplies the keyboard and assistive-technology behavior. The
existing `cmdk` dependency remains appropriate for the global command palette, but its filtered command
model adds unnecessary focus and form-state behavior to these bounded fields. React Aria was considered
for a fully custom select/combobox, but adding that dependency is disproportionate while authorized lists
remain small. Revisit a maintained accessible combobox library if an option catalog routinely exceeds
100 items or needs server-side search/virtualization.

## Consequences

- Operators get a short path from sign-in to active work and from a failed run to its failed step.
- Existing expert tools and API contracts remain compatible.
- Selector options can only be as complete as the caller's authorized catalog; intentional custom
  entry must be explicit rather than an unlabelled escape hatch.
- Trace wording and ordering are testable as deterministic projection functions, while execution
  determinism continues to be enforced by the backend's pinned revision and persisted decision
  evidence.
