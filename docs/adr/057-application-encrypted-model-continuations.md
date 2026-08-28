# ADR-057: Application-encrypted provider continuations

- **Status:** Accepted
- **Date:** 2026-08-25
- **Epic:** EPIC-813

## Context

Reasoning-capable providers may require an opaque response block on the next turn, especially around
tool calls. That state can contain hidden rationale or provider ciphertext. Keeping it only in process
prevents restart recovery; putting it in task results, session checkpoints or traces exposes private
provider state. PostgreSQL `pgcrypto` would also require sending decryption material and plaintext
through SQL execution.

## Decision

Keep continuation semantics on the provider-neutral request/response port. Persist only a public
invocation handle in workflow and session state. Store the provider token in private
`agent_invocations` columns after authenticated application-side encryption with PyCA Fernet.
Bind the encrypted envelope to contract version, tenant, invocation id, provider id and exact provider
revision, and verify its SHA-256 token digest after decryption. Use `MultiFernet` with a named primary
write key and bounded previous read keys for rotation. Load all keys through secret-typed process
configuration; no key enters PostgreSQL, an API response or evidence.

The OpenAI-compatible adapter translates reasoning continuation fields at the transport edge and
removes them from its returned public payload. Capability negotiation requires
`opaque_continuation` before resumption and exact provider-revision mismatch fails before external
I/O.

## Consequences

- Executor restarts can resume supported multi-turn provider sessions from tenant-RLS state.
- Database readers without the application key cannot recover continuation plaintext.
- Losing every configured read key makes old continuation state unavailable; operators must overlap
  old and new keys during rotation.
- Fernet is now a direct runtime dependency owned through `uv`; AMESH does not implement custom
  cryptography.
- Provider output remains nondeterministic. Preserving continuation state does not claim replayed
  output equivalence.

## Rejected alternatives

- Store provider reasoning in the public checkpoint or evidence bundle: this violates the privacy
  boundary and makes accidental logging likely.
- Store unencrypted opaque values in PostgreSQL: opaque does not mean non-sensitive.
- Use database-side encryption: keys and plaintext would cross the SQL boundary and database
  administration would share application decryption authority.
- Implement a custom cipher: a maintained authenticated-encryption construction already satisfies
  the requirement.
