# Session-runtime qualification

This runbook measures the governed agent-session runtime without a model provider: a load test, a
24-hour soak and a timed backup/restore drill. It qualifies one Compose topology on one host. It is
not the Profile M Kubernetes qualification that EPIC-611 still owes, and it says nothing about
workflow, scheduling or plugin workloads.

## What is measured

`docker/compose.session-qualification.yaml` starts a fresh PostgreSQL 17, the migrator, and the API,
executor and scheduler roles from one image. A stub replaces the model provider. The stub is the
`stub` command of `scripts/qualify_session_load.py`, an OpenAI-compatible endpoint that answers
every request with a final action echoing the session's nonce. Each session therefore runs the real
create path, admission, the execution and task-run lifecycle, the session harness, schema
evaluation, budget accounting and audit, and spends no money.

The `run` command of the same script is the driver. It:

1. creates the agent `qualification.sessions/echo` with its model policy and secret binding when it
   is missing;
2. starts sessions at `--rate` per second with `Prefer: respond-async`, each with a random nonce as
   input and as its idempotency key, keeping at most `--concurrency` sessions in flight;
3. polls each session until it is terminal, then re-reads every session in a final independent pass;
4. writes a JSON report every `--report-every` seconds and at the end.

A run passes only when all of the following hold:

- every launched session `SUCCEEDED` with its own nonce as the answer;
- it did so on its first attempt and first execution epoch;
- it owns an execution and a task run that no other session shares;
- no create or read request failed;
- the run lasted at least `--duration-seconds`.

A wrong answer is `MISMATCHED`. A session that was retried or recovered is `RETRIED`, because the run
injects no faults. A session whose execution or task run is shared is `DUPLICATED`. A session still
running after `--drain-seconds` is `LOST`. Any of these fails the run.
The report records the configuration, the server version and migration, the client host and the
create, end-to-end and server-side latency percentiles.

The agent's `hardLimits.maxConcurrency` is also its admission ceiling per agent, per actor and per
provider. The driver sets it to 64, above its own in-flight cap, so it measures the runtime rather
than a one-at-a-time session queue. A real agent with `maxConcurrency: 1` runs its sessions one after
another.

## Run it

Build the image from the revision under test and start the stack:

```powershell
docker build -t amesh:qualification .
docker compose -f docker/compose.session-qualification.yaml up -d --wait api
docker compose -f docker/compose.session-qualification.yaml up -d
```

A short load test from the host (the API listens on `127.0.0.1:18611`):

```powershell
uv run python scripts/qualify_session_load.py run --rate 2 --duration-seconds 60 `
  --revision (git rev-parse HEAD) --report data/session-load-2.json
```

The soak runs inside the stack, so it does not depend on the operator's shell. At 1.2 starts per
second it runs about 104,000 sessions a day, above the URS target of 100,000 executions a day. The
stub waits one second per answer so that sessions overlap. The report is written to
`data/session-load-report.json` and replaced atomically while the run continues:

```powershell
$env:STUB_DELAY_MS = "1000"
docker compose -f docker/compose.session-qualification.yaml up -d --force-recreate model-stub
$env:QUALIFICATION_ARGS = "--rate 1.2 --duration-seconds 86400 --stub-delay-ms 1000 --revision $(git rev-parse HEAD)"
docker compose -f docker/compose.session-qualification.yaml --profile driver up -d driver
docker compose -f docker/compose.session-qualification.yaml logs -f driver
```

The container exits 0 only when the final report has `status: PASSED`. Remove the stack and its
volumes with `docker compose -f docker/compose.session-qualification.yaml down -v`.

## Backup and restore drill

Run the product's recovery exercise against the qualification database after a load or soak run. It
creates a recovery point, restores it into a disposable database on the same server, fences restored
ownership, and checks reconciliation and readiness:

```powershell
docker compose -f docker/compose.session-qualification.yaml exec api `
  amesh recovery exercise --profile v1 --actor operator:qualification
```

On 2026-10-07 the drill ran after the load tests, against a 125 MB database (755 executions, 10,128
audit events). It `PASSED` in 8.7 seconds of wall time: RTO 4.4 seconds, RPO 1.0 second, 1 of 1
stored objects verified, no reconciliation findings and no unresolved gaps. RTO grows with the
database, so repeat the drill on a production-sized copy before quoting it for a deployment.

The first attempt failed. The runtime image installed Debian bookworm's PostgreSQL 15 client, and the
exercise refuses a `pg_dump` older than the server. The image now installs the PostgreSQL 17 client
from the PostgreSQL project's repository.

## Results

All runs are from 2026-10-07 on one workstation (32 CPUs, Windows 11, Docker Desktop). Each used one
API process with the default pool (`DATABASE_POOL_SIZE` 10, `DATABASE_MAX_OVERFLOW` 10) unless the
pool column says otherwise. Latencies are 95th percentiles in seconds, and end-to-end runs from the
create request until the driver sees the session terminal.

| Starts/s | Stub delay | Pool | Result | Succeeded / launched | Create | End-to-end | Server |
| ---: | ---: | --- | --- | --- | ---: | ---: | ---: |
| 2 | 0 | 10 + 10 | PASSED | 120 / 120 | 0.22 | 1.12 | 0.42 |
| 5 | 0 | 10 + 10 | FAILED | 87 / 88 | 34.5 | 96.9 | 32.5 |
| 10 | 0 | 10 + 10 | FAILED | 19 / 26 | 59.8 | 65.1 | 61.1 |
| 20 | 0 | 10 + 10 | FAILED | 30 / 39 | 34.2 | 97.9 | 32.7 |
| 40 | 0 | 10 + 10 | FAILED | 30 / 43 | 34.1 | 99.3 | 60.9 |
| 1 | 5 s | 10 + 10 | PASSED | 60 / 60 | 0.27 | 6.25 | 5.48 |
| 2 | 5 s | 10 + 10 | FAILED | 30 / 37 | 58.6 | 173.1 | 36.6 |
| 2 | 5 s | 30 + 30 | PASSED | 120 / 120 | 0.48 | 6.83 | 5.70 |

Each run lasted 60 seconds. The driver started from inside the stack at 2 per second for 15 seconds
and also passed, with 30 of 30.

The failing runs failed on connections, not CPU. Creates and session steps waited the full 30 seconds
for a pooled connection and failed with `QueuePool limit of size 10 overflow 10 reached`. The driver
saw HTTP 500s and read timeouts, and could start only 0.4 to 0.8 sessions per second. The API's CPU
stayed near zero throughout. What predicts failure is the number of sessions in flight, not the start
rate. Two per second with a 5-second stub keeps about 10 in flight and fails. One per second keeps
about 5 and passes. The same load passes with three times the pool.
[Issue #147](https://github.com/samchung95/amesh/issues/147) records the cause: each in-flight
session holds two pooled connections for its whole run.

Load testing found and fixed two other defects:

- Concurrent session creates deadlocked on the tenant row and returned HTTP 500.
- Each create re-validated every built-in resource schema, which cost about 1.7 seconds of API CPU.
  An idle create's median fell from 1.69 to 0.12 seconds.

The 24-hour soak was started on 2026-10-07. Its result is recorded in `docs/reviews/TESTLOG.md` when
it finishes.

## Known limits

- One API process runs every session. Async sessions run as background tasks in the webserver, and
  the executor role only recovers abandoned work. Each in-flight session holds two pooled database
  connections for its whole run (#147). With the default pool, one process therefore tops out near
  10 concurrent sessions, and beyond that it fails instead of slowing down. Until #147 is fixed, set
  `DATABASE_POOL_SIZE` plus `DATABASE_MAX_OVERFLOW` to at least twice the expected in-flight sessions
  per API process, plus headroom, and keep the total across processes under PostgreSQL's
  `max_connections`.
- This stack does not reach the URS target of 50 sustained task starts per second, and it makes no
  claim to.
- The stub answers in about a millisecond. Real providers take seconds, so real sessions stay in
  flight far longer, and in-flight capacity is what matters, not start rate. To model that, start the
  stack with `STUB_DELAY_MS` set and pass the same value to the driver's `--stub-delay-ms`, which
  records it in the report.
- Every driver poll writes an audit event, about 14 per session. The database grows by about 120 KB
  per session, which comes to about 12 GB for the 24-hour soak.
- Results come from one developer workstation. They are a regression baseline for this topology, not
  a capacity claim for a deployment.
