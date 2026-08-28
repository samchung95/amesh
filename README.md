# AMESH — Agent Mesh

> **Status:** the product-owner-amended two-month MVP is delivered as `v0.2.0-mvp`. AMESH is not yet a production-ready orchestrator and does not claim Kestra compatibility; the uninterrupted 24-hour qualification remains deferred to EPIC-611.

AMESH is a strict clean-room, fully open-source durable workflow and agent orchestration platform. Its first compatibility baseline is pinned to **Kestra 1.3.30** at commit `db49f3b2c2af60d61df10adb6f9fc34e4776b65b`, allowing compatibility to be measured against a stable target rather than an undefined “latest” release.

The product target is broader than OSS feature parity. AMESH also independently implements publicly documented advanced capabilities and adds a first-class, governed agent-mesh runtime. All production capabilities are intended to ship in one **AGPL-3.0** distribution.

## Locked direction

| Area | Decision |
|---|---|
| Product | **AMESH**, meaning **Agent Mesh** |
| Implementation | Strict clean room; public specifications, observable behavior and independently authored conformance tests only |
| Scope | Kestra OSS parity, independently implemented advanced capabilities and AMESH differentiators |
| Compatibility | YAML, Pebble expressions, REST API, CLI, execution semantics and documented import/export formats |
| Durable state and internal transport | PostgreSQL only; `LISTEN/NOTIFY` is a wake-up optimization, not delivery truth |
| Object storage | S3-compatible, Azure Blob and GCS adapters; MinIO in the development stack |
| Production core | Python 3.12 asyncio, confirmed by [ADR-016](docs/adr/016-python-production-core.md); robustness comes from the PostgreSQL/fencing/pure-reducer design, and performance claims are earned by measurement |
| Frontend | React and TypeScript |
| First runners | Local process, Docker/OCI and Kubernetes |
| Plugins | Isolated language-neutral protocol; Java, Python and TypeScript SDKs first |
| Primary users | AI workflow developers, software engineers and platform engineers |
| Production | On-premises Kubernetes/Helm reference; Docker Compose development; single-host secondary |
| Scale | Profile M: 100,000 executions/day, 1,000 active task runs, 50 starts/s, 10 million retained |
| Availability and recovery | 99.9% monthly control-plane target; v1 RPO <= 48h and RTO <= 8h |
| Migration | Full side-by-side resources, identity/governance, history, logs, artifacts and audit evidence |
| Compliance | SOC 2 and ISO/IEC 27001 readiness; certification is not claimed |
| Engineering model | Independent agent quorum for normal merges; human approval for high-risk changes and stable releases |
| Licence | AGPL-3.0-only, confirmed as the strongest selected copyleft while retaining open-source status |

**Python is confirmed as the production core.** The checked-in foundation is the seed of the production engine, not a throwaway specification; the previously accepted Java 25 plan ([ADR-010](docs/adr/010-production-core-language.md), [historical evaluation](docs/architecture/backend-language-evaluation.md)) was superseded before implementation began. The durability guarantees come from PostgreSQL authority, fenced leases, idempotent commands and a pure reducer — properties independent of language — while throughput targets must be demonstrated by measurement, not assumed. See [ADR-016](docs/adr/016-python-production-core.md).

## Repository contents

- **837 functional requirements** and **63 non-functional requirements** in Markdown, JSON and CSV.
- **122 implementation epics** across nine milestone waves.
- **1,000 requirement-to-epic traceability links**.
- A machine-readable parity matrix and GitHub-ready issue bodies.
- A requirement-level compatibility inventory with pinned source provenance, explicit gaps and evidence.
- Architecture for deterministic execution, PostgreSQL queues, leases, fencing, scheduling, plugins, tenancy, security, HA and disaster recovery.
- Full compatibility workstreams for Kestra YAML, Pebble, REST, CLI, execution behavior and import/export.
- AMESH-specific workstreams for agent meshes, deterministic simulation, policy-as-code and evidence-backed AI assistance.
- A running Python/FastAPI MVP control plane with durable PostgreSQL execution, cron/manual/webhook triggers, local and Kubernetes Job runners, agent tasks, recovery worker, REST/CLI access, typed Python/TypeScript/Java/Go clients, metrics and structured logs.
- A PostgreSQL + MinIO Docker Compose development topology.
- Reproducible planning, contract, validation and packaging scripts.

## Architecture at a glance

```text
React / TypeScript web client
CLI and generated client SDKs
               |
REST / WebSocket / compatibility facade
               |
Python durable control plane
- resource and revision services
- source-preserving YAML + Pebble compatibility
- command validation and deterministic reducer
- executor, scheduler and trigger services
- authorization, audit, policy and tenancy
               |
PostgreSQL
- authoritative resources and execution snapshots
- immutable events
- transactional inbox/outbox
- partitioned work queues
- leases and fencing tokens
- PostgreSQL search and analytics projections
               |
Workers and isolated plugin hosts
- local process runner
- Docker/OCI runner
- Kubernetes runner
- Java / Python / TypeScript plugin SDKs
               |
S3-compatible, Azure Blob or GCS artifact and internal file storage
```

Core correctness rules:

1. PostgreSQL is authoritative for committed orchestration state and internal durable delivery.
2. State-changing commands and results are idempotent.
3. Delivery is at least once; arbitrary external side effects are not advertised as exactly once.
4. Workers, schedulers and reconcilers use expiring leases with monotonically increasing fencing tokens.
5. A stale owner cannot commit after reassignment, retry, cancellation or restart.
6. Large files and artifacts live in object storage rather than PostgreSQL queue payloads.
7. Search and analytics are rebuildable PostgreSQL projections, never execution truth.
8. Untrusted user code and third-party plugins run outside control-plane processes.
9. Tenant and authorization context is mandatory at API, persistence, queue, storage and plugin boundaries.
10. Compatibility claims require version-pinned differential evidence.

Start with the [architecture overview](docs/architecture/README.md), [on-premises Kubernetes reference](docs/architecture/on-premises-kubernetes.md), [execution semantics](docs/architecture/execution-semantics.md), [PostgreSQL transport design](docs/architecture/postgresql-transport.md), [configuration and feature flags](docs/operations/configuration.md), [distributed queue operations](docs/operations/distributed-queue.md), [PostgreSQL operations guide](docs/operations/postgresql.md), [object-storage operations](docs/operations/object-storage.md), [full migration architecture](docs/architecture/migration.md), [Kestra migration runbook](docs/operations/kestra-migration.md) and [compatibility architecture](docs/architecture/compatibility.md).

CLI profiles, secure token storage, output modes, declarative workflows, completion and generated
client usage are documented in the [CLI and generated clients guide](docs/cli/README.md).

## Repository map

```text
.github/                    Ownership, issue and pull-request policy (no hosted CI/CD)
backlog/
  epics/                    One implementation-ready issue body per epic
  epics.json                Canonical epic metadata and generated bodies
  github-issues.ndjson      GitHub-ready issue import records
  labels.json               Proposed labels
  milestones.json           Milestone definitions
requirements/
  URS.md                    Human-readable User Requirements Specification
  urs.json                  Canonical requirement records
  urs.csv                   Flat requirement export
  traceability.csv          Requirement-to-epic evidence map
  parity-matrix.csv         Parity and intentional-difference scope
  compatibility-inventory.json  Requirement-level compatibility status, sources and evidence
  source-provenance.json    Pinned public source catalog and strict-mode handoff rules
docs/
  adr/                      Architecture decision records
  architecture/             Runtime, storage, security and compatibility design
  governance/               Clean-room, threat and AI-engineering controls
  product/                  Vision, decisions, personas, roadmap and differentiators
charts/amesh/               Minimal external-PostgreSQL Kubernetes/Helm MVP
src/amesh/                  Python MVP control plane, workers, ports and adapters
tests/                      Specification tests
migrations/                 Provisional PostgreSQL schema
proto/                      Worker and isolated-plugin protocol drafts
scripts/                    Regeneration, validation, packaging and publication tools
```

## Local quick start

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker with Compose v2 and Git.

```bash
cp .env.example .env
docker compose up -d --build
curl -fsS http://localhost:8000/ready
uv sync --extra runtime --extra dev
uv run --extra runtime amesh auth bootstrap-admin --handle root-admin --display-name "Root administrator"
uv run --extra runtime --extra dev pytest
```

The full Compose command runs the one-shot migration service before starting the API and runtime
roles. Use `uv run --extra runtime python -m amesh.server` only for an intentionally host-run API
after the Compose PostgreSQL and migration services are ready.

Open `http://localhost:8000/docs`, then validate and apply a sample flow:

```bash
curl -sS -X POST http://localhost:8000/api/v1/flows/validate \
  -H 'content-type: application/yaml' \
  --data-binary @examples/hello-world.yaml

uv run --extra runtime python -m amesh \
  --token development-token --tenant default apply examples/parallel-dag.yaml
uv run --extra runtime python -m amesh \
  --token development-token --tenant default run examples.engine parallel_dag
```

For the dependency-minimal, all-in-one runtime, use:

```bash
docker compose -f compose.compact.yaml up -d --build
curl -fsS http://localhost:8100/ready
```

This starts PostgreSQL plus one AMESH process containing webserver, executor, scheduler, worker,
indexer and maintenance roles with local versioned storage. See the
[compact deployment guide](docs/operations/compact-deployment.md) for native `uv tool install`,
resource floors, preflight and graceful shutdown.

For the graphical first run, open `http://localhost:8000` with the development token, then use
**Blueprints → Hello, workflow → Open unsaved draft**. Review and save the draft before explicitly
running it from Flow details. The [first-run guide](docs/operations/onboarding.md) covers readiness,
the isolated playground and the under-20-minute local path.

Apply `examples/nested-flowables.yaml`, then open **Flows → Open graph** to inspect its expanded
sequential, bounded-parallel and DAG plan before execution. Execution details show the same graph with
live task states.

On any flow detail page, choose **Preview plan** to compile a signed, side-effect-free simulation with
the current sample inputs. External tasks remain explicit unknowns until mocks, recordings or schemas
are supplied through the [simulation API or CLI](docs/api/simulations.md).

Open **Plugins → Workflow admission policies** to create a versioned tenant or namespace rule and
inspect recent policy evidence. Flow Editor validation, save, promotion, launch and task dispatch use
the same bounded evaluator; see the [admission policy API](docs/api/admission-policies.md).

Apply `examples/loops.yaml` to try bounded foreach, while and until execution. The live graph shows one
aggregated node per loop child and its completed iteration count instead of rendering every generated
task run.

The production container also serves the graphical control room at `http://localhost:8000`. Sign in
with the bootstrapped local user and tenant `default`; the development-only `development-token` remains
available through the UI's API-token mode. Mission Control leads with running and unhealthy work, and
each row opens a simple trace with expert evidence one disclosure away. See the
[frontend guide](frontend/README.md) for the Vite workflow, supported browsers and accessibility
qualification boundary.

The API also supports flow/execution lists, pre-execution and live execution graphs, execution details and logs, durable task-result caching, durable trigger occurrences, execution checks, a tamper-evident audit ledger and signed compliance evidence packages, PostgreSQL-backed users/groups/roles/scoped bindings, local browser sessions, OIDC/SAML/LDAP federation, tenant-bound SCIM provisioning, authorization explanations, bounded provider-neutral model tasks, governed MCP tool calls, durable bounded agent sessions with isolated memory/evaluation/release gates and an authenticated read-only AMESH MCP server, local-process tasks and Kubernetes Job tasks. Prometheus metrics are exposed at `http://localhost:8000/metrics`. See the [agent primitive reference](docs/api/agent-primitives.md), [bounded agent session guide](docs/how-to/run-bounded-agent-session.md), [memory/evaluation/release guide](docs/how-to/configure-agent-memory-evaluations.md), [trigger lifecycle](docs/operations/triggers.md), [execution checks](docs/operations/execution-checks.md), [audit evidence](docs/operations/audit-evidence.md), [task cache](docs/operations/task-cache.md), [authentication](docs/operations/authentication.md), [identity federation](docs/operations/identity-federation.md), [authorization](docs/operations/authorization.md) and [supported upgrade](docs/operations/upgrades.md) runbooks.

For the reference Kubernetes path—external PostgreSQL, existing Secrets, Helm migration/server/worker roles, a real Luna → Job → HTTP run and cleanup—follow the [MVP Helm quickstart](charts/amesh/README.md).

## Planning workflow

`requirements/urs.json` and structured epic fields in `backlog/epics.json` are canonical. After changing either:

```bash
uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
uv run --extra runtime --extra dev python scripts/validate_backlog.py
```

The regeneration script updates the human URS, CSV exports, traceability matrix, parity matrix, epic issue bodies, backlog index, GitHub issue records and roadmap. The [Docker-local verification gate](docs/how-to/run-local-verification.md) rejects generated drift.

Useful validation commands:

```bash
uv run --extra runtime --extra dev pytest
uv run --extra runtime --extra dev ruff format --check src tests scripts
uv run --extra runtime --extra dev ruff check src tests scripts
uv run --extra runtime --extra dev mypy src
uv run --extra runtime --extra dev python scripts/generate_contracts.py
uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py --check
```

Run the complete supported gate in Docker with `make verify-local-all` on POSIX systems or
`.\scripts\verify-local.ps1 -Suite all` in PowerShell. AMESH intentionally has no GitHub Actions
workflow or automatic release publication at this stage. Install the repository's per-clone
pre-push guard with `make install-git-hooks` or `.\scripts\install-git-hooks.ps1`; ordinary pushes
then run that same Docker aggregate and stop on failure. The
[local verification guide](docs/how-to/run-local-verification.md) lists every suite, artifact output
and explicitly deferred specialist qualification, plus the local-hook bypass boundary.

## Compatibility and clean-room policy

AMESH is not affiliated with or endorsed by Kestra. The project may study public documentation, public schemas, public API behavior and independently obtained black-box observations. Clean-room implementers must not copy Kestra source code, documentation prose, visual assets or trademarks into AMESH.

A full compatibility claim is blocked until all declared surfaces have green differential fixtures and known gaps are published. Native AMESH contracts may exist internally, but the compatibility façade must reproduce the pinned public behavior where compatibility is declared.

See the [clean-room policy](docs/governance/clean-room-policy.md), [parity charter](docs/product/parity-charter.md) and [source provenance register](SOURCES.md).

## Roadmap and implementation start

The roadmap is dependency-based, not calendar-based. AI engineering capacity can scale horizontally, but milestone exits remain evidence gates.

- [Roadmap](docs/product/roadmap.md)
- [Two-month MVP scope](docs/product/mvp-scope.md)
- [Decision register](docs/product/decision-register.md)
- [Decision status](DECISIONS_NEEDED.md)
- [Implementation kickoff](docs/product/implementation-kickoff.md)
- [Implementation status](IMPLEMENTATION_STATUS.md)

All foundational product decisions are accepted. The two-month MVP completed W1–W8 under the product-owner-approved W8 soak deferral and is tagged `v0.2.0-mvp`; the broader dependency-ordered roadmap remains open. Later implementation choices are captured as ADRs and may not silently weaken the accepted compatibility, security, migration or release guarantees.

## GitHub publication

The source repository is published at [samchung95/amesh](https://github.com/samchung95/amesh).
Repository pushes, backlog issue creation and release publication remain separate operator actions;
the installed local pre-push hook verifies ordinary pushes, and no hosted workflow publishes
artifacts automatically. The guarded bootstrap scripts remain available for a new fork or mirror:

```bash
export GITHUB_OWNER=samchung95
export GITHUB_REPO=amesh
export GITHUB_VISIBILITY=private
export CONFIRM_PUBLISH=samchung95/amesh

bash scripts/publish_github.sh
bash scripts/bootstrap_github_backlog.sh --dry-run
bash scripts/bootstrap_github_backlog.sh
```

Review the working tree and authorize commit, push, issue creation and any release upload as separate
actions.

## License

AMESH is licensed under **GNU Affero General Public License v3.0 only** (`AGPL-3.0-only`). This decision is confirmed. AMESH does not add a non-commercial, competitor or hosted-service restriction because doing so would conflict with the fully open-source objective. See the [licence policy](docs/product/license-policy.md).
