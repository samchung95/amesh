# Kubernetes task runner

The Kubernetes adapter creates one deterministic, fenced Job per task attempt. Operator-owned runner
profiles choose the kubeconfig context, target namespace, service account, node selector, runtime
class and typed Job template. A task may add non-reserved labels, but cannot override profile-owned
placement or identity.

## Configure profiles

`KUBERNETES_RUNNER_PROFILES` is a JSON array. Selection uses the most-specific matching
`namespacePrefix` and `workerGroup`; include an unscoped profile when Kubernetes should be available
as a fallback.

```json
[
  {
    "name": "default",
    "context": "kind-amesh",
    "namespace": "amesh-tasks",
    "serviceAccountName": "amesh-task",
    "nodeSelector": {"pool": "jobs"},
    "runtimeClassName": "gvisor",
    "workloadIdentity": true,
    "template": {
      "labels": {"team": "platform"},
      "annotations": {"example.com/policy": "isolated"},
      "imagePullSecrets": ["registry"],
      "priorityClassName": "batch",
      "schedulerName": "default-scheduler",
      "tolerations": [{"key": "batch", "operator": "Exists"}],
      "affinity": {},
      "backoffLimit": 1,
      "ttlSecondsAfterFinished": 600,
      "transferImage": "busybox:1.37.0"
    }
  }
]
```

When profiles are omitted, `KUBERNETES_CONTEXT` and `KUBERNETES_TASK_NAMESPACE` form one
backward-compatible default profile. The Helm chart accepts the same objects at
`taskRunner.profiles` and serializes them into the worker environment.

Set `workloadIdentity: true` only with `serviceAccountName`. AMESH then mounts the Kubernetes service
account token and does not add cloud access keys to the task. Configure the provider's identity
binding on that service account. With workload identity disabled, service-account token automounting
is disabled unless a task-level service account is explicitly selected in the legacy single-profile
mode.

## Task controls

Kubernetes accepts either flat resources, which become equal requests and limits, or independent
maps:

```yaml
resources:
  requests: {cpu: 100m, memory: 64Mi}
  limits: {cpu: 500m, memory: 256Mi, ephemeralStorage: 1Gi}
networkPolicy:
  access: restricted
  allowedEgress: [10.20.0.0/16]
```

`networkPolicy.access: none` creates a deny-all egress NetworkPolicy. `restricted` accepts CIDRs and
creates explicit `ipBlock` egress rules. NetworkPolicy enforcement still requires a cluster network
plugin that implements the Kubernetes NetworkPolicy API.

The task security policy maps privileged mode, UID, read-only root filesystem, capability add/drop,
privilege escalation and the runtime-default seccomp profile. `ephemeralStorage` also limits the
workspace `emptyDir`.

## Workspace and recovery

Input files are archived into an `emptyDir` through a gated init container. The task image runs its
declared argv unchanged in `/workspace`. After task termination, a hardened transfer sidecar returns
the workspace through the Kubernetes exec API and exits. Archive restoration rejects absolute,
escaping, symlink, hard-link and device entries.

The runner polls Job/Pod status and logs through the Kubernetes API, retains per-pod log offsets, and
reconnects after transient API errors. Each API operation gets a fresh retry budget, so intermittent
success resets failure counting; persistent failures stop after `KUBERNETES_API_RETRY_ATTEMPTS`.
`KUBERNETES_API_RETRY_MAX_SECONDS` caps each exponential delay. A fresh worker reuses the
deterministic Job and can collect the original Pod's result without incrementing the AMESH attempt.
Pod replacement is supported within the configured `backoffLimit`. Cleanup failures are logged and
cannot replace an active execution or cancellation failure.

Scheduling, image, infrastructure, eviction and user-process failures have distinct diagnostic
reasons. Cancellation is fencing-token protected. Cleanup deletes the owned NetworkPolicy, removes
the `amesh.io/task-cleanup` finalizer and deletes the Job with foreground propagation; reconciliation
repeats the same operation for resources whose attempt/fence is no longer active.

The worker identity needs `create/get` on `pods/exec`, `get` on `pods/log`, patch access to Jobs and
create/delete/get/list/watch access to NetworkPolicies. The Helm Role includes these verbs for its
release namespace. For profiles targeting another namespace or cluster, provision equivalent RBAC
there before enabling the profile.

## Local qualification

Use a migrated disposable database and existing kind context:

```powershell
$env:AMESH_TEST_DATABASE_URL='postgresql+asyncpg://amesh:amesh@localhost:5432/amesh_test'
$env:AMESH_KIND_CONTEXT='kind-amesh'
uv run pytest tests/adapters/kubernetes/test_job_runner.py -q
```

The live suite deletes a running Pod, reconnects with a fresh runner, transfers a real input/output
workspace, inspects profile placement and workload identity, and verifies NetworkPolicy creation.
