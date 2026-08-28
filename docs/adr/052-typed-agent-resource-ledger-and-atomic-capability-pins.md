# ADR-052: Typed agent-resource ledger and atomic capability pins

**Status:** Accepted

**Date:** 2026-08-25

**Owner:** EPIC-807 / board card `c106`

## Context

Agent definitions compose prompts, skills, model routes, tools, permissions, budgets and output
contracts. Embedding mutable copies in flows is not reusable; separate tables for every resource
kind multiply repository and migration behavior; resolving latest revisions at run time is not
replayable.

## Decision

Use one immutable PostgreSQL revision ledger for typed `PROMPT`, `SKILL`, `MODEL_POLICY` and `AGENT`
resources. Pydantic discriminated contracts validate each body before persistence. MCP connection
revisions remain in their existing credential-free ledger.

An agent definition contains exact revision references. One repository transaction loads every
reference, validates tenant/namespace scope, tool-schema pins and capability containment, then
persists a content-addressed effective envelope. A future session may start only from that pin.

Skills contain declarative instructions and requested capability names only; they cannot carry code,
credentials or transport settings. Provider fallback is an ordered, provider-neutral model-policy
contract. Migration diagnostics disclose route changes and output nondeterminism; they never mutate
an existing revision or pin.

## Consequences

- Every effective agent boundary is immutable, inspectable and restart-safe.
- Resource-kind schemas stay independent while persistence, RLS, audit and revision logic remain
  shared.
- Provider replacement does not require an orchestration-state schema change.
- Autonomous turns, checkpoints and tool execution remain outside this decision and belong to
  EPIC-808.
