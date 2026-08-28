# ADR-049: Bounded agent sessions inside one execution engine

- **Status:** Accepted
- **Date:** 2026-08-25
- **Epics:** EPIC-312, EPIC-806, EPIC-807, EPIC-808, EPIC-809

## Context

AMESH already runs explicit durable workflows with one-shot model and MCP tasks. The desired agent
mode lets an author declare an input contract, capability envelope and required output while the
agent chooses bounded intermediate actions. Treating that autonomy as an opaque external process or
a second orchestration engine would bypass the reducer, weaken recovery evidence and make tool side
effects difficult to govern.

## Decision

AMESH keeps one PostgreSQL-authoritative execution state machine. An agent session is a supervised
workflow task whose internal model turns, tool proposals, approvals and checkpoints are durable
execution evidence. The model never writes orchestration state, resolves plaintext secrets or calls
tool transports directly; it proposes actions that AMESH validates and dispatches through pinned
capabilities.

The authored envelope pins the agent, model policy, prompts, skills, tool schemas, MCP connections,
permissions, environment boundaries, budgets and structured-output contract. A session succeeds only
when its output validates and every required policy, assertion, evaluation or approval gate passes.
Schema validity establishes shape, not truth, so business correctness remains a separate gate.

Delivery is staged at durable contract boundaries:

1. EPIC-312 completes bounded model, structured-output and MCP primitives.
2. EPIC-807 defines versioned agent resources and capability envelopes.
3. EPIC-808 runs one durable bounded agent session inside an ordinary workflow.
4. EPIC-809 adds isolated memory, evaluation, trace and promotion gates.
5. EPIC-806 adds typed multi-agent hand-offs and explainable routing.

## Consequences

- Deterministic workflows can surround nondeterministic agent sessions without surrendering control.
- Restart and replay reuse persisted accepted evidence and disclose model nondeterminism.
- Hard limits and approvals are enforced independently of prompt compliance.
- Multi-agent features cannot bypass the single-agent envelope or create orphan tool effects.
- The first useful vertical slice arrives before memory, evaluation or mesh topology is complete.
