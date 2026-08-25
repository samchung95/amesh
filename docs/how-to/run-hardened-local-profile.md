# Run the hardened local profile

Use this guide to expose AMESH to a local client on loopback with real, scoped
authentication. The profile does not publish PostgreSQL, does not grant a
container runtime authority, and does not contain credentials for a model,
broker, or other client-domain service.

## Prepare secret files

Create a directory readable by the account running Compose. Each file must
contain one value followed by a newline; do not commit this directory.

```sh
mkdir -p .amesh-hardened-secrets
umask 077
openssl rand -hex 32 > .amesh-hardened-secrets/admin-token
openssl rand -hex 32 > .amesh-hardened-secrets/token-pepper
openssl rand -hex 32 > .amesh-hardened-secrets/webhook-signing-key
openssl rand -hex 32 > .amesh-hardened-secrets/registry-signing-key
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > .amesh-hardened-secrets/model-continuation-key
postgres_password="$(openssl rand -hex 32)"
printf '%s\n' "$postgres_password" > .amesh-hardened-secrets/postgres-password
printf '*:*:amesh:amesh:%s\n' "$postgres_password" > .amesh-hardened-secrets/postgres-pgpass
```

Set the externalized connection settings. The PostgreSQL URL must be
password-free; asyncpg reads the password from the mounted `PGPASSFILE` secret.
Do not put credentials in the checked-in profile.

```sh
export AMESH_HARDENED_SECRETS_DIR="$PWD/.amesh-hardened-secrets"
export AMESH_POSTGRES_DB=amesh
export AMESH_POSTGRES_USER=amesh
export AMESH_DATABASE_URL='postgresql+asyncpg://amesh@postgres:5432/amesh'
export AMESH_DATABASE_TLS_MODE=disable
```

The checked-in PostgreSQL container is reachable only on the internal Compose network and does
not enable TLS, so the qualified local profile uses `disable`. When replacing it with a
TLS-enabled external PostgreSQL instance, use `require` or `verify-full` and replace `<password>`
and update both `postgres-password` and `postgres-pgpass` together.

## Validate and start

Run the static gate before starting Compose. It checks loopback publication,
the internal network, explicit enabled roles, secret references, password-free database URL, egress policy,
and the absence of runtime authority or domain credentials.

```sh
uv run amesh-hardened-preflight --compose compose.hardened.yaml
uv run --with PyYAML python -m amesh.deployment_profile --compose compose.hardened.yaml
docker compose -f compose.hardened.yaml config --quiet
docker compose -f compose.hardened.yaml up -d
```

The `migrate` service runs first. The `preflight` service then validates the
resolved settings and must complete successfully before `api`, `executor`, or
`scheduler` starts; a bounded one-shot storage initializer prepares the
unprivileged local volume before those roles run. Scheduler health uses its role readiness check, so a
disabled or unregistered scheduler is reported as unavailable rather than
healthy.

The only client-facing listener is `127.0.0.1:${AMESH_HARDENED_PORT:-8000}`.
The private Compose network is marked `internal`; PostgreSQL and role services
have no published ports.

`postgres-pgpass` is a PostgreSQL passfile in the Compose secret store. It is
mounted read-only at `/run/secrets/postgres-pgpass`; the application never
receives the database password through `DATABASE_URL` or a normal environment
variable. Keep its permissions restricted and rotate it together with
`postgres-password` when changing the local database password.

`model-continuation-key` is an AMESH-owned Fernet key used to protect opaque
provider continuation state at rest. It is not a provider credential and must
never be reused as an OpenRouter, broker, or other client-domain secret.

## Issue a scoped client credential

Do not use the profile's bootstrap secret as a client credential. After the
first local administrator is bootstrapped, create a service-account principal,
bind it to the required tenant or namespace role, and issue an expiring token
with only the resource actions the client needs. Follow the
[service-account credential runbook](../operations/credentials.md), then store
the returned token outside the repository and send it as `Authorization:
Bearer <token>`.

Every client operation is authenticated by the durable credential store and
authorization evaluates the token's scopes together with its principal
bindings. A missing, expired, revoked, or over-scoped token is rejected; the
development bootstrap credential is unavailable because `AUTH_MODE=credentials`.

## Stop and remove the local profile

```sh
docker compose -f compose.hardened.yaml down
```

The trust boundary is the local machine and the loopback listener. This profile
does not qualify public exposure, multi-region hosting, or storage of client
broker/domain credentials. Egress is allowlisted and private-host access is
denied unless a separate, explicitly reviewed profile authorizes it.
