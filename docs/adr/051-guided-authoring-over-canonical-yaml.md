# ADR-051: Guided authoring over canonical YAML

**Status:** Accepted

**Date:** 2026-08-25

**Owner:** UX-03 / board card `c100`

## Context

AMESH already has round-trip YAML, a visual graph editor, schema-backed controls, validation,
simulation, flow tests and an execution trace. A separate wizard document would duplicate this
model and make switching between beginner and expert surfaces lossy.

## Decision

Guided workflow creation is another projection of the canonical YAML document. Intent starters
seed ordinary valid YAML. Guided edits use narrow document mutations, and the guide re-derives its
supported values after code or visual edits. Fields it does not own are preserved and disclosed as
advanced content.

The guide resolves choices from authorized resource catalogs and composes existing validation,
policy, simulation and isolated-test APIs. It saves through the normal immutable revision API and
launches only the saved revision before navigating to the persisted execution trace.

## Consequences

- All three authoring modes share one serialization and validation contract.
- A user can reach a trace without learning YAML, while experts retain direct source access.
- The guide must never reconstruct the full document from its local form state.
- New workflow concepts become guided controls only when their canonical schema exists.
