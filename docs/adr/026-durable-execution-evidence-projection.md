# ADR-026 — Durable execution evidence projection

## Status

Accepted — 2026-08-22

## Context

Task completion already stores bounded output and an evidence JSON document, while separate log and
metric tables are not connected to the execution path. The existing log API therefore reconstructs
task results instead of serving task-produced evidence, and it has no durable reconnect cursor.

## Decision

- Project logs, metrics, output metadata and artifact references inside the same PostgreSQL
  transaction that fences and commits a task attempt.
- Keep the attempt JSON as immutable source evidence and maintain query-oriented projection tables;
  large artifacts remain in object storage and projections contain only metadata and opaque URIs.
- Append execution state, task state and task evidence to one tenant-isolated evidence stream with a
  monotonic cursor. Additive page and NDJSON endpoints expose that stream after execution
  authorization and support reconnect from the last cursor.
- Redact declared sensitive output keys and resolved secret values before persistence. Apply bounded
  retention, sampling and a second redaction pass before optional external export. Export failure is
  recorded but never participates in task completion.
- Keep current execution and log endpoints compatible; the evidence API is additive.

## Consequences

The UI and future realtime transports consume one stable event model, restart recovery does not need
to reconstruct transient buffers, and exporter outages cannot block orchestration. PostgreSQL retains
the authoritative small evidence projection; retention and large-scale export operations remain
bounded and can be extended without changing task completion contracts.
