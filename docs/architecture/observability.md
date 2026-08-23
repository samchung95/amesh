# Observability

## Signals

- Metrics: request, command, transition, queue, scheduler, worker, runner, plugin, storage and database
  rates, errors, duration and saturation.
- Traces: API command through transaction, outbox, executor, dispatch, worker, runner and completion.
- Logs: structured component diagnostics and user task logs with separate retention and access.
- Events: durable execution and audit evidence.

The implementation uses the vendor-neutral OpenTelemetry Python SDK with explicit OTLP/HTTP export.
Each process owns bounded trace and log queues; exporters do not participate in control-plane
transactions. The operational configuration, metric catalog and default alert response are in the
[observability runbook](../operations/observability.md).

Task handlers return a bounded `TaskCompletion` envelope. The executor redacts declared sensitive
output keys and resolved secret values, then commits the attempt and its query projection together.
`execution_logs`, `execution_metrics`, `execution_outputs` and `execution_artifacts` remain separate
typed projections; artifact records contain only an internal `s3://`, `azure://` or `gs://` reference
and metadata, never the artifact payload.

Execution and task transitions plus projected task evidence feed `execution_evidence_events`. Its
monotonic cursor is exposed by `GET /api/v1/executions/{execution_id}/evidence` and the reconnectable
NDJSON `/evidence/stream` endpoint after normal execution authorization. The execution detail UI
opens that stream from the last received cursor and presents state, logs, metrics, outputs and
artifacts as one live timeline. Browser retention is bounded to the newest 5,000 events. Task runs are
requested in pages of 100 with a database-computed state summary, and graphs above 1,000 task runs use
the aggregate view instead of materializing the full topology.

Migration `0042_execution_debug_evidence.sql` enriches newly projected execution and task state
evidence with actor, causation, correlation and transition-reason fields. Existing evidence remains
immutable; the UI displays those fields when available and never invents missing historical context.

## Cardinality

Tenant, flow, execution and task-run IDs are trace/log fields, not unbounded default metric labels.
Metrics use bounded dimensions such as component, state, task type, runner, worker group and error class.

## SLOs

Reference SLOs cover API availability, command acceptance, schedule delay, dispatch latency, stuck
executions, queue lag, projection lag and recovery convergence. Alert rules link to versioned runbooks.

## Degraded telemetry

OpenTelemetry and log export are failure-isolated from core work. An unavailable collector increments
a bounded failure metric; a full log queue drops telemetry and increments its drop counter. Neither
condition blocks API, scheduling, execution, task completion or durable message processing.

External evidence export reads batches of at most 1,000 committed events. The policy applies a
retention cutoff, deterministic sampling and a second sensitive-field redaction pass before calling
an optional sink. Sink failures keep the prior cursor for retry and cannot roll back or otherwise
participate in execution completion. Task completion envelopes have explicit output, log and artifact
byte limits; evidence outside those bounds is rejected before persistence.

The PostgreSQL projection uses batched inserts rather than a row-by-row application loop. The
published qualification result must state the database profile, batch shape and measured rate; the
50,000-record/second cluster target remains provisional until its shared EPIC-607 qualification.

## Support bundle

An authorized administrator can generate configuration summaries, component health, version matrix,
recent redacted errors and selected metrics. Bundles are scanned for seeded canary secrets and cannot
include another tenant's data.
