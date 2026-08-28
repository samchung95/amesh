# ADR-053: Durable agent sessions as recoverable workflow tasks

**Status:** Accepted

**Date:** 2026-08-25

**Owner:** EPIC-808 / board card `c107`

## Context

An agent session may perform several nondeterministic model turns and externally observable tool
calls before it produces a valid result. Keeping that progress only in worker memory would repeat
accepted work after restart. Expanding model-proposed actions into workflow nodes would let a model
mutate the durable graph and create a second orchestration lifecycle for approvals and recovery.

## Decision

Represent `agent.session` as one recoverable task in the existing execution state machine. Resolve
and pin its exact capability envelope before the first turn. Persist the session checkpoint and an
ordered, idempotent event journal after every accepted model response, policy decision, tool result,
approval observation and output-validation decision.

The model may propose either one pinned tool call or a final structured output. AMESH validates each
proposal, dispatches tools only through the existing fenced MCP primitive, and enforces cumulative
turn, loop, tool-call, token, cost and duration limits independently of the prompt. At most one
external operation is in flight. A stable per-turn invocation key lets recovery reuse an accepted
primitive result without repeating its external call; an unfinished primitive remains an explicitly
ambiguous outcome.

High-impact tools continue to require an approved direct `core.approval` predecessor. Final output
must satisfy the pinned schema and configured deterministic business assertions. Invalid output is
either rejected or returned to the bounded repair loop. Memory, learned evaluations, release
promotion and multi-agent routing remain subsequent staged owners.

## Consequences

- Agent progress is visible through ordinary execution evidence and survives worker restart.
- Models cannot add graph nodes, select unpinned tools, access transports or expand authority.
- Recovery reuses persisted accepted operations while disclosing nondeterministic model boundaries.
- A session with an ambiguous external operation fails closed instead of repeating it.
- Evaluation and promotion gates can extend the journal without creating another execution engine.
