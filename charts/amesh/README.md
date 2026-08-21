# AMESH MVP Helm quickstart

This chart installs AMESH as three roles: a pre-install/pre-upgrade migration Job, one API server
Deployment and one recovery-worker Deployment. PostgreSQL is external to the chart. Credentials are
read from existing Kubernetes Secrets; the chart does not create production defaults. The default is
single-tenant compatibility mode. Set `tenancy.mode=multi` and select `worker.group` to enable explicit
tenant requests and tenant-aware worker routing; see the
[multi-tenancy runbook](../../docs/operations/multi-tenancy.md).
The worker performs bounded durable-state reconciliation every 60 seconds by default; tune the three
`worker.reconciliation*` values using the [reconciliation runbook](../../docs/operations/reconciliation.md).

`database.migrationExistingSecret` can hold a table-owner/migration login separately from the
application login in `database.existingSecret`. Restricted tenant-repository logins need the roles
documented in the multi-tenancy runbook; the combined server still needs its existing authorization
and credential-store grants. Leaving the migration Secret empty uses the application Secret for
development compatibility. Full per-component least-privilege qualification remains EPIC-612 work.

## Requirements

- Docker, kind, kubectl and Helm 4
- uv 0.11 or newer
- an OpenRouter API key with access to `openai/gpt-5.6-luna`

The commands below use a disposable cluster and a development-only PostgreSQL Deployment so the full path can be reproduced locally. Operated environments should provide PostgreSQL separately.

## Build the locked image and cluster

```bash
uv sync --extra runtime --extra dev
docker build -t amesh:mvp .
kind create cluster --name amesh-mvp --wait 120s
kind load docker-image amesh:mvp --name amesh-mvp
kubectl --context kind-amesh-mvp create namespace amesh-system
```

## Provide external PostgreSQL and Secrets

```bash
kubectl --context kind-amesh-mvp -n amesh-system create deployment postgres --image=postgres:17
kubectl --context kind-amesh-mvp -n amesh-system set env deployment/postgres \
  POSTGRES_DB=amesh POSTGRES_USER=amesh POSTGRES_PASSWORD=amesh
kubectl --context kind-amesh-mvp -n amesh-system expose deployment postgres \
  --port=5432 --target-port=5432
kubectl --context kind-amesh-mvp -n amesh-system wait \
  --for=condition=Available deployment/postgres --timeout=120s

kubectl --context kind-amesh-mvp -n amesh-system create secret generic amesh-database \
  --from-literal=database-url=postgresql+asyncpg://amesh:amesh@postgres:5432/amesh
kubectl --context kind-amesh-mvp -n amesh-system create secret generic amesh-admin \
  --from-literal=token=development-token
kubectl --context kind-amesh-mvp -n amesh-system create secret generic amesh-openrouter \
  --from-literal=api-key="$OPENROUTER_API_KEY"
```

## Install and verify

```bash
helm --kube-context kind-amesh-mvp install amesh charts/amesh \
  --namespace amesh-system \
  --set openRouter.existingSecret=amesh-openrouter \
  --set openRouter.key=api-key \
  --wait --timeout 5m

kubectl --context kind-amesh-mvp -n amesh-system port-forward \
  service/amesh-amesh 28081:8000
```

Keep the port-forward running and use a second terminal:

```bash
curl -fsS http://127.0.0.1:28081/health
curl -fsS http://127.0.0.1:28081/metrics | grep amesh_build_info

uv run --extra runtime python -m amesh \
  --api-url http://127.0.0.1:28081 \
  --token development-token \
  apply examples/agent-shell-http.yaml

uv run --extra runtime python -m amesh \
  --api-url http://127.0.0.1:28081 \
  --token development-token \
  run examples.mvp agent_shell_http \
  --runner kubernetes \
  --input 'topic=durable Helm workflows' \
  --input 'callbackUrl=http://amesh-amesh:8000/api/v1/flows/validate'
```

The execution and all three task runs must report `SUCCESS`. The callback deliberately targets the public validation endpoint; its JSON response proves the final HTTP step without adding another service.

## Cleanup

The following removes the entire disposable quickstart cluster and its PostgreSQL data:

```bash
kind delete cluster --name amesh-mvp
```
