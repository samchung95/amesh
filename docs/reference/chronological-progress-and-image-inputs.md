# Chronological progress and governed image contracts

This page defines the EPIC-828 contracts that provider, harness, workflow, task, plugin, API and UI
implementations share. It does not make session orchestration the owner of image support.

## Platform image value

`amesh.image-ref/v1` is the platform image value. It wraps one existing
`amesh.artifact-ref/v1` record and decoded display facts. The artifact supplies tenant, namespace,
opaque asset reference, version, checksum, content address, byte size, provenance and retention.
The image contract permits PNG, JPEG, WebP and GIF and bounds each image to 20 MiB, 16,384 pixels
per dimension and 40 million decoded pixels.

Workflow inputs, ordinary task and plugin inputs or outputs, expressions, branches, loops and
subflows may carry the value unchanged. They do not copy its bytes. A node that only routes an image
does not need image-processing capability. A node that reads or transforms image content must
declare image-input capability and resolve the authorized artifact through its governed invocation
boundary.

Model messages use `amesh`'s ordered text and `image_ref` content parts. Array order is placement
order. A portable message supports at most 16 images and 80 MiB in aggregate. Durable state never
contains base64, a data URL, an arbitrary remote URL, a signed storage URL or credentials. A provider
adapter may create its transient provider-specific representation only after tenant authorization,
digest verification and exact-route capability negotiation.

The canonical `session.started` event projects each accepted image as
`amesh.image-display/v1`. That authorized UI projection contains only its SHA-256 content identity,
media type, byte size, checksum and decoded dimensions. It excludes binary data, object-store access
material, namespace paths, filenames, alt text and provenance display strings. All three run
inspectors derive attached-image metadata from this durable event, so it survives reload and retry.

Checked-in schemas:

- `schemas/image-ref.schema.json`
- `schemas/multimodal-message.schema.json`

## Safe chronological progress

`amesh.agent-progress/v1` is a bounded input frame. It identifies the attempt, turn, activity,
segment, source and source sequence. Its detail is a discriminated union with only two forms:

- `STATUS`: an AMESH-owned factual code and optional fixed label.
- `PUBLIC_SUMMARY`: reserved bounded text for a producer with an independent safety qualification.

There is no generic payload field. Raw reasoning, chain-of-thought, rationale, scratchpads, prompts,
messages, continuations, credentials, secret values, personal data and raw provider errors are not
valid progress fields. The current model-provider gateway never persists provider-supplied summary
text: it preserves the segment boundary but replaces the text with the fixed `model.processing`
status. A future producer may use `PUBLIC_SUMMARY` only after an independent safety qualification.

AMESH accepts frames into the existing session journal. Journal acceptance order is authoritative;
`occurredAt` is informational. `(sourceId, sourceSequence)` is contiguous and idempotent within an
attempt. Reusing a sequence with different content fails. Thinking and delta frames have a stable
segment identity. Only adjacent deltas from the same segment may coalesce in a projection. Any
intervening unsegmented activity or completed, failed, cancelled or truncated status closes the
segment permanently.

Default bounds are 16 KiB per frame, 128 frames per segment, 1,024 segments and 4,096 frames per
session, a 256-frame producer buffer and 20 frames per second. An idle stream sends one initial
heartbeat and then no more often than every five seconds while polling the durable journal once per
second. The first hard-limit overflow commits exactly one `TRUNCATED` marker; later frames are
acknowledged as truncated no-ops and do not extend the journal. This terminal state applies only to
progress telemetry: the model invocation, session and workflow continue, and final result, tool,
usage, cost and terminal evidence remain durable. Observers read the journal and cannot block
execution. Clients may filter, collapse or sample accepted events for presentation, but AMESH
retains validation, redaction, ordering, idempotency and hard ingestion/storage limits.

Checked-in schemas:

- `schemas/agent-progress-frame.schema.json`
- `schemas/agent-progress-event.schema.json`
- `schemas/agent-session-event-cursor.schema.json`

## Reconnect cursor

The opaque `amesh.agent-session-cursor/v1` token binds a logical service session to the current
attempt session, attempt number and attempt-local journal index. Its ordering position is
`(attempt, eventIndex)`, so a cursor does not reset or skip accepted events when a retry starts a new
attempt. Clients pass the token back without inspecting it. AMESH rejects malformed tokens and tokens
bound to another service session. The legacy `afterEventIndex` contract remains available for
compatible latest-attempt reads.

Read a bounded page with:

```text
GET /api/v1/agent-sessions/{sessionId}/progress?after={opaqueCursor}&limit=100
```

The response is `{sessionId, events, nextCursor}`. Watch live NDJSON at
`/api/v1/agent-sessions/{sessionId}/progress/stream`; pass the last handled cursor as `after` or
`Last-Event-ID`. Event lines use `amesh.agent-progress-event/v1`; heartbeat lines carry only
`type`, `sessionId` and the current cursor. A bounded stream may close before a non-terminal run
finishes, so clients reconnect from the last cursor. A terminal event closes only after the server
checks that no later retry-attempt event is already committed.

Architecture rationale is recorded in
[ADR-068](../adr/068-chronological-progress-and-governed-image-inputs.md).
