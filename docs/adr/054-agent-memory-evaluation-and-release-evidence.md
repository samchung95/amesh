# ADR-054: Agent memory, evaluation and release evidence

- Status: Accepted
- Date: 2026-08-25
- Owners: EPIC-809

## Context

EPIC-808 can recover one bounded agent session, but its envelope deliberately fails closed when
memory, versioned evaluations or human release are required. Those controls must remain part of the
ordinary execution and evidence model. Ambient vector recall, mutable judge prompts or a separate
agent promotion service would make authority and replay impossible to explain.

## Decision

1. Add immutable `EVALUATION` resources to the existing tenant- and namespace-scoped agent resource
   ledger. Agent definitions reference exact evaluation revisions, and capability resolution pins
   their content and any exact judge model-policy revision.
2. Persist agent memory in a tenant-RLS journal separate from session checkpoints. Every entry is
   scoped by namespace, agent revision and one of `EXECUTION`, `PRIVATE` or explicitly named
   `SHARED` scope. Tasks declare exact read keys and at most one output write key. Expiry, byte
   ceiling, redaction, provenance and deletion are enforced by AMESH.
3. Treat recalled memory as untrusted user data, never as system instructions. The session records
   only memory metadata and digests in ordinary execution evidence; protected content is not exposed
   by the catalog API.
4. Run deterministic schema assertions and weighted rubric checks before any optional judge. A judge
   uses an exact model-policy revision and records model, prompt, token, cost, score, rationale and
   uncertainty. A judge result cannot override a deterministic failure or approve a tool or release.
5. When the pinned policy requires human release, the `agent.session` task must name a direct
   `core.approval` predecessor whose durable decision is `APPROVED`. Evaluation and release decisions
   are projected into the same execution evidence timeline as ordinary tasks, tools and approvals.
6. Expose a side-effect-free envelope preview that reports exact memory/evaluation/tool boundaries
   and marks model output unknown. It never calls a provider, tool or memory write path.

## Consequences

- Memory and evaluation state survive process restarts without entering the workflow reducer's
  internal state schema.
- Shared memory requires an explicit stable scope in the pinned policy; it is never tenant- or
  namespace-global by default.
- Provider replacement changes a model-policy/evaluation revision and therefore a reviewed pin, but
  does not change the memory, session or evaluation-result schema.
- Semantic quality remains bounded evidence rather than a deterministic-model-output claim.

## Rejected alternatives

- **Store memory inside session checkpoints:** prevents controlled reuse and independent retention or
  deletion.
- **Use an LLM judge as the release decision:** nondeterministic and correlated evidence cannot be
  the sole authority for production or high-impact actions.
- **Create a separate agent test/promotion engine:** duplicates flow tests, approvals, lifecycle and
  execution evidence instead of composing them.
