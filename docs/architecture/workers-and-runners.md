# Workers and task runners

## Worker role

Workers are data-plane agents. They do not decide the workflow graph. A worker:

1. advertises capabilities, labels, runner types and capacity;
2. receives or claims a dispatch;
3. obtains an expiring lease and fencing token;
4. resolves scoped files, secrets and plugin package;
5. starts a runner or isolated plugin;
6. streams heartbeats, logs and progress;
7. uploads outputs and artifacts;
8. submits a fenced completion;
9. performs idempotent cleanup.

## Dispatch matching

Matching considers tenant, worker group, trust domain, runner, plugin version, labels, resources, region,
egress and data-residency policy. Admission reserves scarce logical capacity before dispatch; the runner
still enforces physical resource limits.

The implemented protocol is version 1. A registration is stable by tenant, worker group and instance
name; reconnecting updates the same worker identity. The registration advertises software version,
task-type capabilities, runner types, labels and logical capacity. Workers pull committed
`DispatchTaskRun` commands from PostgreSQL. `LISTEN/NOTIFY` only wakes the same pull loop and is never
the source of truth.

Claiming locks both the durable queue row and the current task attempt in one transaction. The two rows
receive the same worker identity, database-time lease and monotonically increasing fencing token.
Capacity and task/runner compatibility are evaluated before the claim. A heartbeat renews both rows in
one transaction and records worker/task progress, resource usage and cancellation acknowledgement.
Completion, retry and failure require the current live worker/fence pair and consume the queue claim in
the same transaction; an expired owner cannot commit after reassignment.

Expired claims can be requeued for another fenced delivery or failed and quarantined according to the
selected worker-loss policy. Draining changes a worker to `DRAINING`, which prevents new claims while a
live in-flight claim may still heartbeat and complete. Authorized operators can inspect liveness,
compatibility, capacity, claimed work and utilization at `GET /api/v1/workers`, and fence a drain request
with `POST /api/v1/workers/{worker_id}/drain?expectedVersion=N`.

## Runner boundary

Runner contract `1.0` is declarative and immutable. `RunnerRequest` carries tenant, namespace,
worker-group, execution/task/attempt identity and fencing token plus image or argv, environment,
input-file references, working directory, resource limits, network policy, security policy, deadline,
cancellation grace and one typed runner extension. `RunnerResult` normalizes runner identity, terminal
status, exit code, ordered logs, metrics, outputs, artifact references and infrastructure diagnostics.

Each adapter publishes `RunnerCapabilities`, including accepted request features, contract versions,
network/security support, reconciliation support, extension type and its cancellation escalation. An
unsupported request fails capability validation before a subprocess or external Job is created.
Authorized operators can inspect the built-in descriptors at `GET /api/v1/runners/capabilities`.

Tasks may select a typed runner:

```yaml
tasks:
  - id: isolated
    type: core.shell
    image: busybox:1.37
    command: [sh, -c, echo ok]
    taskRunner:
      type: kubernetes
      serviceAccountName: amesh-task
      nodeSelector: {pool: jobs}
```

`runnerCredentials` explicitly maps environment-variable names to scopes declared in
`contract.secretScopes`. Resolution happens for one attempt; only those values enter the runner
request, Pydantic redacts them, and they are never added to durable task output or runner diagnostics.
The local adapter inherits only a bounded non-secret host environment unless its typed trusted-process
extension explicitly enables broader inheritance.

Runner selection evaluates the most-specific configured namespace-prefix and worker-group rule. A
task-level `taskRunner.type` is the requested runner, then the matching rule's `defaultRunner`, then the
execution fallback. `allowedRunners` always gates the result, so an explicit task request cannot bypass
policy. This follows the separation between task runners and worker groups in the pinned Kestra parity
baseline while allowing both constraints to be combined.

## Isolation levels

1. **Trusted process:** fastest, shared host boundary, disabled for untrusted tenants.
2. **OCI container:** filesystem/process isolation with hardened runtime policy.
3. **Kubernetes job/pod:** cluster-level scheduling and workload identity.
4. **Cloud job/VM:** provider-managed compute.
5. **Remote edge worker:** private network and regional data placement.

## Orphan cleanup

Runtime resources carry owner labels and deterministic external identifiers. Cleanup can be repeated.
A reconciler compares platform attempts with runner resources and quarantines ambiguous active work
rather than deleting it blindly.

The contract reconciler receives the current `{attempt_id: fencing_token}` set. The local adapter
terminates tracked processes whose fence is absent or superseded; the Kubernetes adapter deletes only
owned Jobs with a mismatched or absent active fence. Repeating reconciliation returns no additional
cleanup after the resource is gone.

Cancellation is fenced and reaches the runner through the task cancellation channel. The local
sequence is `terminate` → wait for `cancelGraceSeconds` → `kill`; Kubernetes uses an owned Job delete
with foreground propagation and bounded API retry. Timeout uses the same runner-owned cleanup path and
normalizes to `TIMED_OUT`.
