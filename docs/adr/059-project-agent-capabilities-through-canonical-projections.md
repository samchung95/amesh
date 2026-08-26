# ADR-059: Project agent capabilities through canonical projections

- **Status:** Accepted
- **Date:** 2026-08-26

## Context

Pi now owns transient agent-turn mechanics, but users still need bounded long-session context,
discoverable node authoring, understandable run inspection, capability connection, generic document
inputs and a durable way to prove that another harness would preserve AMESH behavior. The platform
already has canonical workflow YAML, immutable agent and plugin ledgers, PostgreSQL session events,
object storage, replay controls and evidence APIs. Parallel stores or UI-only execution paths would
weaken those boundaries.

## Decision

Execute EPIC-819 through EPIC-824 sequentially. Context is a deterministic bounded projection over
the immutable transcript with a content-addressed receipt. Agent builder, inspector and capability
wizard surfaces are authorized projections and commands over existing resources. Documents enter as
typed artifacts and are decoded by exactly pinned isolated extractor plugins. A versioned harness
conformance kit targets the existing port; Pi remains the explicit production adapter with no silent
fallback.

Use existing dependencies for projection, validation, storage and UI state. Any PDF parsing package
must receive a separate current build-versus-buy and license decision before it enters the lock.

## Consequences

- Each user-facing feature can be removed without migrating authoritative workflow or execution data.
- UI convenience cannot bypass policy, credentials, journals, exact revisions or evidence.
- Document formats remain extensible without putting client-specific parsing logic in core.
- EPIC-104, cloud qualification and additional production harness adapters remain separate work.
