# Compact deployment

The compact profile runs the webserver, executor, scheduler, worker, indexer and maintenance roles
inside one AMESH process. PostgreSQL remains the authoritative resource, queue, lease and event
store. Local filesystem storage is available for a single-host installation; S3-compatible storage
is the recommended durable production configuration.

## Docker Compose

The smallest checked-in stack needs Docker, Compose and one PostgreSQL container. It uses a named
local-storage volume and starts on port 8100 so it can coexist with the multi-service development
stack:

```powershell
docker compose -f docker/compose.compact.yaml up -d --build
docker compose -f docker/compose.compact.yaml ps
Invoke-RestMethod http://localhost:8100/ready
```

The AMESH container applies the packaged migration manifest before admission. Startup then performs
a bounded write/read/delete storage probe. A failed configuration, credential, PostgreSQL,
migration or storage check exits before the HTTP listener or background roles start.

Run the sample through the compact endpoint:

```powershell
uv run amesh --api-url http://localhost:8100 --token development-token `
  --tenant default apply examples/hello-world.yaml
uv run amesh --api-url http://localhost:8100 --token development-token `
  --tenant default run examples.getting_started hello_world
```

`docker compose -f docker/compose.compact.yaml stop compact` sends SIGTERM. The supervisor requests a
durable drain for every registered role, stops new HTTP admission, lets the current bounded role
cycle finish, checkpoints work through the PostgreSQL transaction that owns it, marks every role
`STOPPED`, and exits within `COMPACT_SHUTDOWN_GRACE_SECONDS`.

## Native Python package

The wheel includes the web application, the four console commands and the complete migration set.
Install from a checkout or a built wheel with `uv`:

```powershell
uv tool install .
$env:DATABASE_URL = 'postgresql+asyncpg://amesh:amesh@localhost:5432/amesh'
$env:OBJECT_STORAGE_BACKEND = 'local'
$env:OBJECT_STORAGE_LOCAL_ROOT = 'C:\amesh\objects'
$env:READINESS_CHECK_STORAGE = 'true'
amesh-migrate
amesh-preflight
amesh-compact
```

`amesh-preflight --read-only-storage` lists the configured storage prefix without writing a probe.
The default startup check writes and removes a zero-byte object so read-only or incorrectly owned
volumes fail closed. A native package still requires PostgreSQL 15 or newer; there is no SQLite or
embedded queue mode.

## Storage selection

Use `OBJECT_STORAGE_BACKEND=local` with `OBJECT_STORAGE_LOCAL_ROOT` for the compact single-host
adapter. It stores tenant-scoped current objects, immutable SHA-256 versions and lifecycle metadata
under one root and rejects cross-tenant URIs. Back up this directory with the matching PostgreSQL
recovery point.

Use `OBJECT_STORAGE_BACKEND=s3` plus the standard endpoint, bucket and credential or workload-
identity settings when object durability must not share the AMESH host. Azure and GCS remain
supported through the common storage contract, but the checked-in compact Compose profile exercises
the dependency-minimal local path.

## Liveness and readiness

`GET /health` is process liveness only. `GET /ready` checks required dependencies and returns each
condition as `READY`, `DEGRADED` or `UNAVAILABLE`. The reference profiles set
`READINESS_CHECK_STORAGE=true`, so configuration, credentials, PostgreSQL, exact migration parity,
object storage and service-registry membership must all be ready. An optional unchecked dependency
can produce HTTP 200 with status `degraded`; a required failure produces HTTP 503 and status
`not-ready` without turning a live process into a restart loop.

## Resource envelope

These are operator planning floors, not throughput guarantees:

| Profile | CPU | Memory | Free disk | Intended use |
| --- | ---: | ---: | ---: | --- |
| Development minimum | 2 cores | 4 GiB | 10 GiB | One user, sample flows, local storage |
| Development recommended | 4 cores | 8 GiB | 20 GiB | UI, tests and several concurrent executions |
| Compact production minimum | 4 cores | 8 GiB | 50 GiB plus retained data | Small single-host control plane |
| Compact production recommended | 8 cores | 16 GiB | Workload-sized PostgreSQL and object storage | Sustained small-team operation |

Size PostgreSQL and object storage from measured execution, log, artifact and retention volume. The
compact process is one failure domain and does not itself satisfy a 99.9% availability objective.
For redundant production roles, topology spread, disruption budgets and rolling drains, use the
[high-availability topology](high-availability.md). The external monthly SLO and long-duration
failure qualification remain release evidence rather than a local compact-profile claim.
