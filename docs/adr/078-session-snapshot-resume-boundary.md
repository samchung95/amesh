# ADR-078: Session snapshot and resume boundary

Status: accepted for issue #81.

## Context

Consumers restore their own chat and need one execution-bound hydration response. Existing
summary/result requests can select different follow-up executions. The durable journal already
provides opaque cursors and stable event IDs across attempts and turns.

## Decision

Add a versioned, read-only canonical `/snapshot` endpoint. Use an optimistic read bracket: select
and authorize the latest execution, read its latest attempt and journal, then recheck the selected
execution identity/version/epoch and latest attempt identity. Retry a changing selection up to
three times, then return 503 with `Retry-After: 1`. No database migration is needed.

The attempt record's monotonic version is its journal watermark. Bound the result and activity to
events at or below that version, even if the event query sees a later commit. Return the exact
execution/turn and attempt identities, execution and session versions, existing safe lifecycle
projection, one safe activity event and the opaque cursor of the last included event. A session
without an event returns the initial cursor, allowing replay of previous turns when a follow-up
is queued. It never attaches a previous execution's result to the queued turn.

Resume the existing progress endpoint after this cursor and deduplicate by `eventId`. Changes
after the read point are delivered by the existing journal. After an empty/terminal stream,
rehydrate to discover a queued or newly committed turn; when no later turn exists the existing
terminal reconnect behavior is unchanged. Repeated hydration has no write side effects.

## Alternatives and consequences

A new database-wide atomic snapshot would couple execution storage and session projections;
returning unrelated summary/result/cursor reads leaves their race implicit. The bounded optimistic
protocol uses existing monotonic versions and makes retries explicit. It may return a retryable
503 during repeated execution transitions. Continuous progress alone does not force retries.
Existing summary, result and progress clients remain compatible; consumer documentation gives
their multi-request reconciliation fallback. AMESH does not store consumer chat or replay browser
actions during hydration.
