# ADR-035 — Canonical flow data contracts

- **Status:** Accepted
- **Date:** 2026-08-22
- **Epic:** EPIC-205

## Context

Input definitions already existed in the flow DSL, but runtime validation was limited to synchronous
subflows, supported only a few primitive types and was not shared with the API or control room. Flow
outputs were expressions used by subflow mapping but were not materialized on terminal executions.
Separate API, UI and executor interpretations would drift and could expose sensitive values.

## Decision

AMESH uses one Pydantic-backed flow definition to derive a Draft 2020-12 input schema, control-room
form metadata and runtime validation. The contract supports string, integer/number, boolean, datetime,
duration, enum, array, object, file and secret-reference inputs. Required/default, display, prefill,
validation, item/schema, size and sensitivity metadata remain part of the canonical flow revision.

All PostgreSQL execution creation paths validate the same contract before opening a transaction that
could create execution or task rows. API and webhook launches additionally replace inline base64 file
objects with tenant-scoped object-storage references. Secret inputs accept only `secret://` references;
resolved secret plaintext continues to enter tasks only through the existing scoped context provider.
Legacy revisions with no input declarations retain bounded ad-hoc maps; declaring any input opts the
revision into strict unknown-name rejection.

On successful terminalization the executor renders declared flow outputs from the completed task
context, validates typed outputs and writes them to the execution aggregate in the same transaction as
the terminal event. Public execution, task-result, log and evidence projections redact schema-marked
input and output values. Static flow `variables`, execution `inputs` and mutable key-value context
remain separate expression namespaces.

## Alternatives considered

### Store only caller-supplied JSON Schema

This is standards-based but loses the concise workflow DSL and makes editor metadata, secret policy
and file staging conventions a second contract.

### Generate a Pydantic model per flow revision

Generated runtime classes add caching and lifecycle complexity without improving validation over the
canonical JSON Schema plus explicit datetime, duration, file and secret checks.

### Validate only in API handlers

This misses scheduler, trigger, subflow and internal launches. The repository boundary is the final
common point before runnable state exists.

## Consequences

- Migration 0037 adds materialized execution outputs.
- `GET /api/v1/flows/{namespace}/{flowId}/data-contract` is the authorized schema/form contract.
- Inline files are bounded and staged before execution metadata is written.
- Plaintext secret inputs are rejected, including failed requests, before durable work exists.
- Invalid terminal output rendering changes an otherwise successful execution to a documented
  configuration failure.
