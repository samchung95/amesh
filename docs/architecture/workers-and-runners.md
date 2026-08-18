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

## Runner boundary

The runner request is declarative. It includes immutable task identity, image/command, environment
references, files, resource limits, network policy and security context. The worker never passes
long-lived control-plane credentials into the workload.

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
