# ADR-071: Persist complete progress with producer backpressure

Status: accepted

Context: chronological agent progress currently applies default rate and session-count limits. Real
model streams can legitimately emit more than 20 safe progress frames per second, so those limits
can replace useful activity with `TRUNCATED`. A volatile 500 millisecond write buffer would reduce
transactions but could lose its uncommitted tail if the service process failed. The product owner
prefers complete durable information and accepts throttling when persistence is slower than the
producer.

Decision: keep the PostgreSQL agent-session journal as both the durable ingress queue and canonical
progress log. A provider or harness awaits `AgentProgressSink.append()` for every valid frame. The
receipt is returned only after the frame and session version commit, so accepted progress survives
process restart and database latency naturally backpressures the producer. Clients may poll the
current projection every 500 milliseconds or consume the existing reconnectable stream; their read
frequency does not change write durability.

Disable default frames-per-second, frames-per-segment, segments-per-session and frames-per-session
ceilings. Do not generate new `TRUNCATED` frames. Retain the enum and receipt field only to decode
historical journals written before EPIC-834. A frame that violates the typed frame-size or content
contract is rejected before acceptance rather than represented as partial success. If persistence
fails, the producer call fails without an acknowledgement. When a producer or harness fails with an
active progress segment, the sink attempts to append one durable `FAILED` progress closure when
PostgreSQL is available; the session's existing lifecycle and fenced recovery paths remain
authoritative for the session terminal state. Accepted progress always precedes that lifecycle
evidence in the same canonical ordering authority.

Use the existing SQLAlchemy/PostgreSQL stack and do not add Redis, Kafka, NATS or an in-memory
acknowledged queue. A second durable broker still performs one durable write per frame and adds
credentials, deployment and recovery coordination; a volatile queue weakens the restart guarantee.
Revisit batched durable ingress only if measured throughput proves awaited PostgreSQL acceptance is
insufficient and a producer acknowledgement/replay protocol can preserve the same semantics.

Consequences: normal activity is complete rather than sampled or truncated. PostgreSQL performs one
transaction per accepted frame and may slow model-stream consumption under load; that slowdown is
intentional backpressure. The host controls retained duration and volume through the existing
session retention and storage-capacity policies. Existing event indexes, cursors, evidence triggers,
idempotency and client contracts remain unchanged, and historical `TRUNCATED` events remain readable.

Alternatives: a 500 millisecond in-memory batch reduces commits but can lose generated frames on
process death; one JSON batch row breaks event-level cursors and evidence; an external broker adds a
second durable authority without reducing the required durable ingress operations.
