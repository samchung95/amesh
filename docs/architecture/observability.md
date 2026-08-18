# Observability

## Signals

- Metrics: request, command, transition, queue, scheduler, worker, runner, plugin, storage and database
  rates, errors, duration and saturation.
- Traces: API command through transaction, outbox, executor, dispatch, worker, runner and completion.
- Logs: structured component diagnostics and user task logs with separate retention and access.
- Events: durable execution and audit evidence.

## Cardinality

Tenant, flow, execution and task-run IDs are trace/log fields, not unbounded default metric labels.
Metrics use bounded dimensions such as component, state, task type, runner, worker group and error class.

## SLOs

Reference SLOs cover API availability, command acceptance, schedule delay, dispatch latency, stuck
executions, queue lag, projection lag and recovery convergence. Alert rules link to versioned runbooks.

## Degraded telemetry

Exporters use bounded buffers and circuit breakers. Failure to export telemetry cannot block state
commit or task completion. The platform exposes dropped/sampled telemetry counts.

## Support bundle

An authorized administrator can generate configuration summaries, component health, version matrix,
recent redacted errors and selected metrics. Bundles are scanned for seeded canary secrets and cannot
include another tenant's data.
