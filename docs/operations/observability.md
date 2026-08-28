# Observability operations

AMESH exposes Prometheus metrics at `GET /metrics`, emits newline-delimited JSON logs and can export
OpenTelemetry traces over OTLP/HTTP. Telemetry is operational evidence, never orchestration truth:
exporter, collector and log-destination failures cannot roll back or block accepted work.

## Configuration

| Setting | Default | Purpose |
|---|---:|---|
| `LOG_LEVEL` | `INFO` | Python log threshold |
| `LOG_DESTINATION` | `stdout` | `stdout`, rotating `file`, or UDP `syslog` |
| `LOG_FILE_PATH` | empty | Required when the destination is `file` |
| `LOG_SYSLOG_ADDRESS` | `127.0.0.1:514` | `host:port` used by the syslog destination |
| `LOG_QUEUE_CAPACITY` | `10000` | Bounded non-blocking process log queue |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | empty | OTLP/HTTP collector base URL; empty disables export |
| `OTEL_EXPORTER_OTLP_HEADERS` | `{}` | JSON object of sensitive collector headers |
| `OTEL_BATCH_QUEUE_SIZE` | `2048` | In-process span queue bound |
| `OTEL_BATCH_SIZE` | `512` | Maximum export batch |
| `OTEL_EXPORT_TIMEOUT_SECONDS` | `5` | Per-export timeout |

Production containers should normally keep `LOG_DESTINATION=stdout` and let the platform log agent
ship the JSON stream. Direct file and syslog destinations exist for single-host deployments. When the
bounded log queue is full, application work continues and `amesh_log_records_dropped_total` increases.

Set `observability.otlpEndpoint` in Helm to enable trace export. Put collector headers in an existing
Secret selected by `observability.otlpHeadersExistingSecret`; do not put tokens in values files.
`compose.yaml` and `compose.compact.yaml` pass through the same environment settings.

## Trace propagation and redaction

AMESH propagates W3C `traceparent` through HTTP, durable commands, events, messages, task and subflow
requests, and runner/plugin calls. API, scheduler, executor, worker, storage, messaging, plugin and
runner operations emit spans. Span names, attributes, events, resources and JSON logs pass through the
same secret-redaction boundary before export. Trace context and correlation identifiers may appear in
logs; tenant identity and resolved secret values do not.

Only the allow-listed `traceparent` field is persisted. An unavailable OTLP collector causes bounded
export failures recorded by `amesh_telemetry_export_failures_total`; it does not fail the operation
that produced the span.

## Metrics and cardinality

The default operations dashboard uses these signals:

- `amesh_component_operations_total` and `amesh_component_operation_duration_seconds` for bounded
  component/operation outcomes and latency.
- `amesh_database_health`, pool size and checked-out connections for availability and saturation.
- `amesh_queue_depth` and `amesh_queue_oldest_eligible_age_seconds` for durable queue pressure.
- `amesh_worker_capacity`, `amesh_admission_pressure_ratio`, `amesh_search_projection_lag_seconds`,
  `amesh_stuck_work` and reconciliation metrics for capacity, lag and convergence.
- Existing HTTP, storage, plugin, authentication and database metrics for component detail.

Metric labels are bounded enums or code-defined dimensions. Tenant, flow, execution, task-run,
correlation and trace identifiers are forbidden as default Prometheus labels; use traces or redacted
logs for those investigations.

The Helm observability ConfigMap contains `amesh-operations.json` for Grafana and
`amesh-alerts.yaml` for Prometheus-compatible rule loaders. Thresholds are reference defaults and
should be tuned from measured local baselines without removing the runbook links or cause/impact
annotations.

## Collector or log shipper unavailable

1. Confirm `/health` and `/metrics` remain reachable; do not restart healthy orchestration solely for
   an export failure.
2. Check `amesh_telemetry_export_failures_total` and `amesh_log_records_dropped_total`.
3. Validate collector reachability, TLS and the mounted header Secret outside the application.
4. Restore the destination, then confirm counters stop increasing. In-memory queues are bounded and
   are not a durable telemetry spool, so data dropped during the outage is not replayed.

## Alert runbooks

### Control plane unavailable

Confirm `amesh_database_health`, PostgreSQL reachability and migration status. Restore PostgreSQL or
network service first; accepted durable work remains authoritative in PostgreSQL.

### Operation latency high

Identify the component/operation in the duration histogram, then compare database saturation, queue
lag and worker capacity. Scale or repair the constrained component after confirming the dependency.

### Database saturated

Compare checked-out connections with configured pool size and inspect slow-query metrics. Remove the
blocking database condition before increasing application pool sizes.

### Operation failures

Filter `amesh_component_operations_total{outcome="error"}` by component and operation, then correlate
the time window with redacted JSON logs and traces. Preserve durable retries unless the runbook for the
specific operation directs otherwise.

### Queue lag high

Check oldest eligible age, queue depth and worker capacity. Restore or scale the responsible consumer
role and confirm the oldest age converges toward zero.

### Search lag high

Check indexer availability and PostgreSQL pressure. Authoritative execution and flow APIs remain safe;
search may be stale while the disposable projection catches up or is rebuilt.

### Stuck work

Inspect reconciliation findings and the affected role health. Run the bounded reconciliation action
for expired ownership; escalate non-converging or ambiguous findings instead of guessing state.
