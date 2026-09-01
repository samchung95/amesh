# ADR-068: Journal chronological progress and reference governed image inputs

Status: accepted

Context: agent sessions already commit durable events in order, but provider and Pi progress is
discarded until a complete model response exists. The public stream reads only the latest attempt
through an attempt-local integer, so reconnecting after a retry can hide earlier activity. Agent and
model messages are text-only even though namespace artifacts already provide tenant-scoped,
content-addressed storage. Passing raw provider chunks or image bytes through generic payloads would
create a second transcript, weaken ordering, and risk exposing hidden reasoning or storage access.

Decision: keep the existing PostgreSQL agent-session journal as the only transcript authority. A
provider or harness may emit a versioned, bounded `amesh.agent-progress/v1` frame through an
AMESH-owned sink. The frame contains only activity, lifecycle status, correlation identities,
source sequence, timestamps, fixed status detail or a provider-declared public summary. It has no
generic payload. AMESH assigns order when the frame is accepted into the journal; source timestamps
never reorder accepted events. Stable source identity and sequence form the idempotency key.

A logical service-session cursor is an opaque encoding of service session, attempt session, attempt
number and attempt-local event index. Its lexicographic `(attempt, eventIndex)` position spans
retries without changing the legacy `afterEventIndex` contract. New cursor reads include all
attempts, reject cursors for another service session, and return the exact next committed event.
Only contiguous deltas with the same segment identity may coalesce in a projection. Any intervening
journal event or terminal segment status closes that segment; a later thinking region uses a new
segment identity.

Public thinking is not chain-of-thought. AMESH may expose factual lifecycle codes and bounded text
that a provider explicitly labels as a public summary. Raw reasoning fields, rationale, scratchpads,
prompts, messages, continuations, credentials, secret values, personal data and raw provider errors
are rejected from the typed progress contract rather than filtered after persistence. Slow observers
read the journal and never backpressure execution. Producers use bounded frames, segments, session
counts, buffers and rates; overflow is represented by an explicit truncated terminal frame.

Clarification (2026-09-01, EPIC-833): AMESH owns progress validation, redaction, ordering,
idempotency and hard ingestion/storage limits. The first hard-limit overflow commits one durable
`TRUNCATED` marker; later progress frames are acknowledged as truncated no-ops. `TRUNCATED` is
terminal for progress telemetry on that attempt, not for the model invocation, agent session or
workflow, so final result, tool, usage, cost and terminal evidence continue durably. Clients may
filter, collapse or sample accepted events for presentation, but cannot disable or replace AMESH's
server-side bounds.

Image input is a shared platform value over artifact, workflow, task and plugin contracts, not a
session-plane feature. An image reference wraps the existing `ArtifactRef`, plus bounded display and
decoded-dimension metadata. Ordered model content parts reuse that reference. Ingestion verifies the supported
media signature, checksum, size, dimensions, count and tenant ownership before the reference is
accepted. Durable messages, workflow state and events contain only immutable artifact references;
image bytes remain in governed object storage. Expressions, branches, loops and subflows may carry
the reference through any node input, but only a task, exact model route, provider and harness that
declare image-input capability may consume it. Admission fails before provider I/O otherwise.
Consumers resolve authorized bytes only at their governed invocation boundary. OpenRouter maps them to its multipart image
shape there; Pi remains behind the same AMESH model gateway and never receives provider credentials
or object-store authority. Arbitrary remote image URLs, data URLs and signed storage URLs are not
canonical inputs.

Use Pillow 12.3.0 for decoded signature, format and dimension validation instead of maintaining
custom binary parsers. Open only the PNG, JPEG, WebP and GIF format allowlist, treat Pillow
decompression-bomb warnings as failures, retain its pixel protection and verify the image before
storing a governed reference. Byte and AMESH pixel limits are checked before any consumer runs.

Consequences: live clients can observe truthful progress and reconnect across attempts without a
second event store. Existing unary providers and legacy event-index clients remain compatible while
streaming and image capability are additive and fail closed. More journal writes and artifact reads
require explicit limits, Pillow becomes a locked runtime dependency, and provider-public summaries still require adapter qualification because
AMESH cannot infer whether arbitrary model prose is safe.

Alternatives: a separate token/progress transcript would split ordering authority; buffering progress
until model completion would preserve the current misleading chronology; embedding base64 or remote
URLs in messages would bypass storage governance; persisting raw reasoning and redacting it later
would make privacy depend on an incomplete denylist.
