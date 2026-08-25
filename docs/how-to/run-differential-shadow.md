# Run a differential shadow comparison

Use this guide to compare two exact workflow or agent configuration pins against one frozen input
without allowing an uncontrolled external effect.

## Pin the comparison

Create a `DifferentialSpec` with a tenant, namespace, two configuration digests, an idempotency key,
and the input value. AMESH derives `inputDigest` from canonical JSON. Reusing the same idempotency
key and request in one tenant returns the original report; the same key in another tenant is a
separate comparison. Reusing a key with different inputs or pins is rejected.

Each adapter receives one configuration pin, the frozen input and a `ShadowRunContext`. To read a
side effect during a shadow run, call `context.effect(...)` with a certified `SAFE_FIXTURE` or a
selected `RECORDING`. The certificate is a SHA-256 digest of the fixture key, source and value.
Calling an effect without one of those fixtures raises `ShadowExecutionError` before the adapter
can treat it as successful. Adapters must route all side effects through this context; the quality
core never opens a network, filesystem or provider connection.

## Read the report

The structural comparator checks schema, deterministic assertions, task and tool chronology,
evidence, usage, cost and latency. Configure numeric absolute or relative tolerances where small
measurement variance is expected. Declare model/provider output paths in `nondeterministicPaths`;
those differences are reported as `NONDETERMINISTIC_OBSERVATION`, not as a pass or a failure.

The report keeps three separate collections:

- `deterministicFailures` contains contract, policy, schema, chronology, evidence and out-of-
  tolerance regressions.
- `toleratedDifferences` records differences accepted by configured usage, cost or latency bounds.
- `nondeterministicObservations` records declared model/provider variation.

Only an empty `deterministicFailures` collection makes `report.passed` true. Comparator extensions
implement the provider-neutral `Comparator` protocol and are appended to the core structural
comparison; they do not change shadow safety or tenant/idempotency rules.

Shadow comparison is observational. It does not promote a candidate, change workflow state, or
perform client cutover.

## Use the transport boundary

The application mounts the quality routes at the paths below and stores their state in PostgreSQL.
The quality package also exposes `build_differential_router` for embedders and a small async client
for SDK integrations. The application router uses AMESH authentication and tenant context, checks
that the body tenant and namespace match the request context, and authorizes `execute` or `view`
before reading or writing a report:

- `POST /api/v1/namespaces/{namespace}/differentials` runs an idempotent comparison. An optional
  `Idempotency-Key` header must equal the body key.
- `GET /api/v1/namespaces/{namespace}/differentials/{idempotencyKey}` retrieves the report within
  the authenticated tenant.

The router factory does not choose an authorization implementation or a provider adapter. The
composition root supplies both, keeping REST, CLI and SDK callers on the same neutral contract. Its
baseline executor compares the frozen input without external I/O; deployments replace that
executor with the workflow or agent configuration adapter they want to qualify.

The PostgreSQL adapter stores the specification, each side's checkpoint/observation, the final
report, and an ordered event journal in tenant-RLS tables. Event inserts enqueue one outbox message
in the same transaction. A side that is already `RUNNING` is treated as an ambiguous in-flight
operation and is not silently duplicated after restart; `PENDING` or `FAILED` sides can be claimed
again with a new attempt number. `SUCCEEDED` observations and reports are immutable.

To compose the command-line surface, call `add_differential_commands` on the existing parser. The
`differential run <spec.yaml>` and `differential report <namespace> <idempotency-key>` helpers send
the caller's bearer-token transport with the tenant and idempotency headers. A deterministic
failure exits with code `1`; authorization, transport and contract errors exit with code `2`.
