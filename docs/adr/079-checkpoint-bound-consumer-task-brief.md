# ADR-079: Checkpoint-bound consumer task brief

Status: accepted for issue #82.

## Decision

Canonical create and follow-up requests may include a consumer-authored `taskBrief`: a generic
schema ID/version, JSON content, exact namespace artifact references and a finite token allocation.
AMESH authenticates the producer, verifies artifact metadata and read authority, and binds the
accepted document to tenant, namespace, logical session and accepting turn. Its content-addressed
ID/digest and turn revision identify an immutable revision. Follow-up refresh checks the previous
digest; omission inherits the existing revision. Existing execution metadata and checkpoint JSON
retain accepted revisions, so no new mutable store or migration is needed.

The runtime verifies this scope and persists the selected revision in each new checkpoint. Recovery
must match the accepted revision. For model context only, AMESH inserts a bounded reference-data
message immediately after the initial system message, inside the harness's mandatory retained
prefix. Canonical dialogue is untouched. Existing context receipts verify the virtual source
transcript, while context events additionally expose a safe brief pin and canonical transcript
digest. Protected continuation indexes are shifted for the inserted message.

The brief consumes one message and its actual estimated tokens/bytes within existing context and
total-token ceilings. Documents exceeding 16 KiB or their explicit allocation (at most 4,096
estimated tokens) fail before provider I/O. Artifact metadata is pinned; bytes are never embedded
automatically. Existing authorized versioned file reads or pinned consumer retrieval tools fetch
only selected evidence and revalidate current authority.

## Alternatives and scope

Consumer-owned new-turn input remains the compatibility fallback. A separate mutable brief CRUD
service would add a second admission/consistency path; a turn-bound slot uses the established
authenticated follow-up boundary. Runtime-generated semantic summaries would require provider
spend and accuracy/approval policy and are excluded. This slot is neither cross-session memory nor
additional token allowance. Non-opt-in sessions retain their current messages, receipts and pins.
