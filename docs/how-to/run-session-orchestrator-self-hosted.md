# Run the self-hosted Agent Session Orchestrator

This profile runs the Agent Session Orchestrator roles in Docker while keeping
the deployment boundary separate from the development stack. The webserver is
published on loopback only. Execution uses the local-process runner; Docker
runner access, Docker group membership, and the Docker socket are absent.

## Docker-local profile

Provide a directory containing the following files, with values managed by the
operator rather than committed to source:

`admin-token`, `token-pepper`, `model-continuation-key`, `webhook-signing-key`,
`registry-signing-key`, `object-storage-access-key`, `object-storage-secret-key`,
and `postgres-pgpass`.

Signing and encryption keys must be non-development values of the lengths required by the runtime
configuration validator.

Set the required connection references before rendering the profile:

```powershell
$env:AMESH_SESSION_SECRETS_DIR = "C:\path\to\session-secrets"
$env:AMESH_SESSION_DATABASE_URL = "postgresql+asyncpg://db.example/amesh"
$env:AMESH_SESSION_DATABASE_TLS_MODE = "verify-full"
$env:AMESH_SESSION_OBJECT_STORAGE_ENDPOINT = "https://s3.example"
$env:AMESH_SESSION_OBJECT_STORAGE_REGION = "us-east-1"
$env:AMESH_SESSION_OBJECT_STORAGE_BUCKET = "amesh"
$env:AMESH_SESSION_EGRESS_ALLOWED_HOSTS = '["s3.example"]'
```

Validate and start the profile with:

```text
docker compose -f docker/compose.session-orchestrator.yaml config
docker compose -f docker/compose.session-orchestrator.yaml up --build
```

The API is available at `http://127.0.0.1:8000` by default; set
`AMESH_SESSION_ORCHESTRATOR_PORT` to choose another loopback port. The profile
expects PostgreSQL and S3-compatible object storage to be reachable through the
references above. This Docker-local profile starts in credential-auth mode with the file-backed
admin token; create additional principals, roles and credentials through the administration API.
External identity-provider and SCIM configuration is available through the Helm profile below.
Broker and model-provider credentials are not part of this profile.

## Helm profile

The equivalent values overlay is
`charts/amesh/profiles/session-orchestrator.yaml`:

```text
helm upgrade --install session-orchestrator charts/amesh \
  --namespace amesh --create-namespace \
  -f charts/amesh/profiles/session-orchestrator.yaml
```

Provision these existing Secrets in the target namespace before installing:

- `amesh-session-orchestrator-database` (`database-url`)
- `amesh-session-orchestrator-object-storage` (`access-key`, `secret-key`)
- `amesh-session-orchestrator-encryption` (`model-continuation-key`)
- `amesh-session-orchestrator-auth` (`admin-token`, `token-pepper`, `webhook-signing-key`,
  `registry-signing-key`)
- `amesh-session-orchestrator-identity` (`identity-providers`, `scim-providers`)

The overlay enables only `webserver`, `executor`, and `scheduler`; worker,
indexer, and maintenance roles are disabled. The chart templates use
`secretKeyRef` for runtime credentials and do not mount `docker.sock`.

For a coordinated move between deployments, follow the
[whole-cluster migration runbook](../operations/session-orchestrator-migration.md). Do not copy
containers or Kubernetes process state as session authority.
