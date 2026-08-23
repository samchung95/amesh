# Kubernetes operator

The opt-in AMESH operator reconciles declarative Kubernetes resources into an AMESH server. It uses
the public API, reads bearer credentials from Kubernetes Secrets on every reconciliation and exposes
Prometheus metrics on port 9090. Kubernetes is desired-state storage only; AMESH/PostgreSQL remains
authoritative for runtime and execution state.

## Supported resources

| Kubernetes kind | AMESH configuration |
|---|---|
| `AmeshFlow` | Flow document and revision |
| `AmeshNamespace` | Namespace resource bundle |
| `AmeshFile` | Namespace file |
| `AmeshKeyValue` | Namespace key-value |
| `AmeshDashboard` | Dashboard |
| `AmeshApp` | Workflow app |
| `AmeshRole` | Authorization role |
| `AmeshBinding` | Scoped role binding |
| `AmeshPluginPolicy` | Plugin-policy rule |

The CRDs do not model executions, attempts, queues, leases, checkpoints or backfill runtime state.

## Install

The default target uses the release tenant, in-cluster AMESH Service and the existing administrator
token Secret. Enable namespace-scoped RBAC and the operator with:

```console
helm upgrade --install amesh charts/amesh --namespace amesh-system \
  --set operator.enabled=true
kubectl wait --for=condition=Available deployment/amesh-amesh-operator \
  --namespace amesh-system --timeout=120s
```

Apply the example after the `examples.mvp` AMESH namespace exists:

```console
kubectl apply -f charts/amesh/examples/operator/key-value.yaml
kubectl wait --for=condition=Ready ameshkeyvalues.platform.amesh.io/epic702-live \
  --namespace amesh-system --timeout=60s
kubectl get ameshkeyvalues.platform.amesh.io/epic702-live \
  --namespace amesh-system -o yaml
```

`status.observedGeneration` must match `metadata.generation`; `Ready=True` confirms that AMESH
accepted the desired document. `status.remoteRevision` and digests are safe reconciliation evidence,
not a copy of the credential.

## Scope and targets

`operator.watchNamespaces` defaults to the Helm release namespace. List explicit namespaces to add
Role/RoleBinding pairs, and use `operator.labelSelector` to narrow resources further. Cluster-wide
RBAC is opt-in through `operator.clusterWideRBAC=true`; configured watch namespaces still bound the
controller's actual watches.

For several tenants or endpoints, set `operator.targets`:

```yaml
operator:
  enabled: true
  watchNamespaces: [amesh-team-a, amesh-team-b]
  targets:
    - tenant: team-a
      endpoint: https://amesh-a.example.test
      credentialSecretRef:
        namespace: amesh-system
        name: amesh-team-a-api
        key: token
    - tenant: team-b
      endpoint: https://amesh-b.example.test
      credentialSecretRef:
        namespace: amesh-system
        name: amesh-team-b-api
        key: token
```

Each CR's `spec.tenant` must match exactly one configured target. The chart grants `get` only for the
named credential Secrets in the release namespace. If a target references another namespace, create
an equivalent Secret `Role` and `RoleBinding` there for the release service account. Rotate the
Secret value in place; the next reconciliation reads the new value. For several Kubernetes clusters,
install one scoped operator in each cluster and supply that cluster's target credentials.

## Reconciliation and deletion

The operator reacts to added or changed generations and periodically resyncs to detect out-of-band
changes. Successful correction reports `Ready=True` with reason `DriftCorrected`, sets
`DriftDetected=False` with reason `Corrected`, and emits a Kubernetes event. Transient API failures
use bounded exponential backoff; permanent document errors report `Ready=False` without including
HTTP response bodies or credentials.

`spec.deletionPolicy` controls the finalizer:

- `Delete` removes the remote AMESH object before releasing the finalizer.
- `Retain` releases the finalizer without reading the server credential or changing AMESH.

Watch events with `kubectl get events --field-selector involvedObject.name=<name>`. Scrape
`amesh_operator_reconciliations_total` and
`amesh_operator_reconciliation_duration_seconds` from the operator metrics Service.

## CRD version upgrades

The generated CRDs currently serve and store only `platform.amesh.io/v1alpha1`. Regenerate them with
`uv run python scripts/generate_operator_crds.py` after changing the descriptor registry. Additive
optional fields may remain in `v1alpha1`; a breaking change requires a new served version plus a
conversion webhook or an explicit storage migration. Do not remove `v1alpha1` until every stored
object has migrated and `status.storedVersions` no longer lists it.

Back up CR YAML for desired-state recovery, but use AMESH's database and object-store backup process
for authoritative configuration, history and execution recovery.
