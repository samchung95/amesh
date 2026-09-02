# ADR-073: Bind protected model continuations to retained assistant messages

- **Status:** Accepted
- **Date:** 2026-09-02
- **Epic:** EPIC-835
- **Issues:** #16

## Context

ADR-057 keeps provider reasoning continuation encrypted per model invocation and exposes only a safe
handle. A session checkpoint, however, retained only the latest handle. On turn two the adapter
reattached turn one's opaque reasoning to assistant message one. On turn three it rebuilt assistant
message one without that reasoning and attached only turn two's continuation to assistant message
two. The provider-visible prefix therefore changed before any harness compaction, limiting prompt
cache reuse to the initial system and user prefix.

## Decision

Keep every continuation body in the existing tenant-, invocation-, provider- and revision-bound
encrypted invocation record. Add an ordered checkpoint binding from each accepted canonical
assistant message index to its safe continuation handle. Retain the singular latest handle for
backwards-compatible checkpoint reads; an old checkpoint can recover only that latest binding.

Carry safe bindings through the provider-neutral harness model-call contract. After the harness
selects context, the model gateway must use the verified context receipt's retained source indexes
to discard omitted bindings and remap retained source-message indexes to the selected transcript.
The model task loads only those protected invocation records and passes private in-memory
`messageIndex` plus secret-token bindings to the provider adapter. The OpenAI-compatible adapter
attaches each decoded envelope to that exact assistant message and rejects an out-of-range,
duplicate or non-assistant target.

Public checkpoints, events, evidence and logs may contain only safe handles, indexes and digests;
they never contain continuation plaintext. A clean checkpoint remains ineligible for transfer while
either the legacy handle or binding history is present because transfer bundles intentionally omit
the encrypted continuation bodies.

## Consequences

- Retained, non-compacted assistant/tool-result history remains provider-prefix stable across three
  or more turns, enabling later cache reads to advance beyond the opening prefix.
- Harness compaction explicitly defines the continuation boundary: omitted assistant bindings are
  neither decrypted nor sent, while retained bindings are remapped without changing their content.
- Existing encrypted storage and key rotation remain unchanged; no database migration is required.
- Checkpoint metadata grows linearly by one safe binding per continued assistant message.
- Legacy checkpoints resume the latest continuation but cannot recreate handles discarded by older
  software.

## Rejected alternatives

- Encrypt a cumulative continuation blob after every turn: this duplicates protected data
  quadratically and makes compaction filtering ambiguous.
- Put opaque reasoning into canonical messages: this crosses the public checkpoint and evidence
  privacy boundary.
- Continue attaching only the latest continuation: this preserves correctness for one follow-up but
  invalidates earlier assistant prefixes on later turns.
