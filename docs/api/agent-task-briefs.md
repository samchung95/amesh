# Versioned consumer task briefs

Use `taskBrief` when a long-running canonical session needs approved task state to remain visible
after context compaction. The consumer owns the domain schema, approval and source data. AMESH
provides an authenticated, immutable checkpoint binding and a bounded projection slot.

## Create and refresh

Include an optional brief when creating a canonical session:

```json
{
  "agentRef": "research/helper@1",
  "idempotencyKey": "workspace-task-1",
  "input": {"question": "Continue the approved task"},
  "taskBrief": {
    "schemaId": "consumer/task-state",
    "schemaVersion": "1",
    "content": {"goal": "Consumer-defined goal", "approvedRevision": "revision-7"},
    "artifacts": [],
    "maxEstimatedTokens": 2048
  }
}
```

`schemaId` and `schemaVersion` identify your schema; AMESH treats `content` as generic JSON data.
The producer is the authenticated launching principal. AMESH binds the accepted document to that
principal, tenant, namespace, logical session and accepting turn. The stored revision uses
`amesh.task-brief/v1`; its `briefId` and SHA-256 `digest` identify the complete immutable binding.
The `revision` ordinal is the accepting execution turn, so inherited revisions can skip ordinals.
Use the ID/digest together when referring to a revision.

After the current turn succeeds, send a new `taskBrief` with the ordinary
`POST /api/v1/agent-sessions/{sessionId}/messages` request. Supply `expectedBriefDigest` from the
current `briefPin` in session/context events. A mismatch returns 409 before launching another
turn. For the first brief on a previously unconfigured session, omit that expected digest.
Omitting `taskBrief` inherits the accepted revision unchanged. Refresh is available only at the
existing authenticated between-turn message boundary; model arguments cannot update the slot.
Use the normal stable message idempotency key: a duplicate accepted message returns the original
execution rather than creating another brief revision or turn.

Accepted revisions live in execution metadata and durable checkpoints. Refreshing a later turn
does not rewrite earlier checkpoints or canonical dialogue. Recovery must use the checkpoint's
accepted revision. The launching producer and logical session scope remain fixed.

## Budget and projection

The serialized document is limited to 16,384 UTF-8 bytes, including reference metadata. Its
`maxEstimatedTokens` allocation defaults to 2,048 and must be between 64 and 4,096. AMESH estimates
the complete brief message using rounded-up serialized UTF-8 bytes divided by four. Exceeding
either bound returns a request validation error before provider I/O; AMESH does not truncate the
brief or summarize it automatically.

For model context only, the runtime inserts one reference-data message after the initial system
message. This message belongs to the mandatory retained prefix, so compaction can omit older
complete dialogue groups while retaining the brief. It consumes one message and its actual bytes
and estimated tokens inside the existing context limits. It grants no additional total-token,
cost, output or physical model-window allowance. If the pinned prefix, brief and newest complete
turn cannot fit, the model gateway rejects the call before provider I/O.

The canonical transcript remains unchanged. Context receipt source indexes and `transcriptDigest`
refer to the virtual source with the inserted brief. Context events additionally include
`canonicalTranscriptDigest` and a safe `briefPin` containing ID, digest, revision, schema identity,
allocation and estimated usage. Those fields identify the selected revision without publishing
its contents. The brief document is omitted from public execution metadata and session summaries.

## Referenced evidence

`artifacts` accepts up to 32 existing `amesh.artifact-ref/v1` objects. Obtain an exact version from
`GET /api/v1/namespaces/{namespace}/artifacts/{path}?version=N`. Brief references must belong to
the session's tenant and namespace. Admission requires current `namespace_file:READ` authority
and verifies the stored reference, digest and size using metadata; it does not load artifact bytes.
Inherited references are checked again at follow-up admission. A missing artifact, a mismatched
version/digest or unauthorized scope prevents admission.

The model sees reference metadata, never automatically embedded files. A consumer can select one
approved reference and read just that evidence through the existing authorized
`GET /api/v1/namespaces/{namespace}/files/{path}?version=N` endpoint, or expose a pinned retrieval
tool that verifies its own consumer grant and approved evidence manifest. Every retrieval must
revalidate current access. A reference is an identifier, not a bearer credential or permission to
read another artifact. AMESH does not connect to consumer application tables or interpret browser
recording and automation fields.

## Compatibility and validation

Without `taskBrief`, sessions keep their existing context selection, receipts and capability and
harness pins. This slot is distinct from memory policy (cross-session recall), total-token budgets
(cumulative usage), UI hydration (`/snapshot`) and semantic summaries (model-generated statements
with separate accuracy/approval requirements).

The existing consumer-owned fallback remains bounded new-turn input plus authorized retrieval
tools. There is no requirement to replay the full conversation, screenshots or network payloads.
Provider-free tests exercise real Pi compaction, interrupted-tool recovery, immutable between-turn
refresh, stale/unauthorized admission, reference-only evidence and oversized rejection. See
[ADR-079](../adr/079-checkpoint-bound-consumer-task-brief.md).
