# ADR-043: API-driven Kubernetes operator boundary

- Status: Accepted
- Date: 2026-08-23
- Scope: EPIC-702

## Decision

AMESH ships a Python Kubernetes operator that reconciles namespaced `platform.amesh.io` custom
resources through the public AMESH `/api/v1` and SCIM APIs. The operator never reads or writes AMESH
tables directly. PostgreSQL remains authoritative for platform configuration and execution state;
Kubernetes stores desired configuration, reconciliation conditions and opaque remote identifiers.
Executions, attempts, queues, leases and checkpoints are deliberately not custom resources.

The first API version is `v1alpha1`. Every CRD enables the status subresource and reports
`observedGeneration`, `Ready` and `DriftDetected` conditions. A periodic resync corrects remote drift,
while resource watches avoid reconciling status-only updates. The operator uses
`platform.amesh.io/finalizer`; `spec.deletionPolicy` explicitly chooses `Delete` or `Retain` for the
remote object.

Operator targets bind one tenant to one AMESH endpoint and one Kubernetes Secret reference. The
Secret is fetched for each reconciliation so rotation does not require a CR update or pod restart.
Plaintext credentials are not accepted by the CRDs and are never copied into status, events or error
messages. Watches are limited to configured Kubernetes namespaces and an optional label selector.
Run one operator deployment per Kubernetes cluster; a deployment may contain multiple tenant target
credentials.

CRD schemas are generated from the checked-in resource descriptor registry. `v1alpha1` is the sole
served and storage version until a second version exists. A future breaking schema change must add a
new served version, migrate stored objects and provide either a conversion webhook or an explicit
storage-version migration before `v1alpha1` is removed.

## Consequences

- The operator can be upgraded independently while remaining constrained by the public API contract.
- Kubernetes loss does not erase AMESH execution truth; recreating CRs rehydrates configuration state.
- Finalizer progress depends on the selected AMESH endpoint and credential only for `Delete` policy.
- Cross-cluster operation uses separate scoped deployments rather than cluster-admin credentials in
  one global controller.
