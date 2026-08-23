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
- **103 implementation epics** across nine milestone waves.
- **992 requirement-to-epic traceability links**.
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

Start with the [architecture overview](docs/architecture/README.md), [on-premises Kubernetes reference](docs/architecture/on-premises-kubernetes.md), [execution semantics](docs/architecture/execution-semantics.md), [PostgreSQL transport design](docs/architecture/postgresql-transport.md), [configuration and feature flags](docs/operations/configuration.md), [distributed queue operations](docs/operations/distributed-queue.md), [PostgreSQL operations guide](docs/operations/postgresql.md), [object-storage operations](docs/operations/object-storage.md), [full migration architecture](docs/architecture/migration.md) and [compatibility architecture](docs/architecture/compatibility.md).

CLI profiles, secure token storage, output modes, declarative workflows, completion and generated
client usage are documented in the [CLI and generated clients guide](docs/cli/README.md).

## Repository map

```text
.github/                    CI, ownership, issue and pull-request policy
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
docker compose up -d postgres minio minio-init
uv sync --extra runtime --extra dev
uv run --extra runtime amesh auth bootstrap-admin --handle root-admin --display-name "Root administrator"
uv run --extra runtime --extra dev pytest
uv run --extra runtime python -m amesh.server
```

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

For the graphical first run, open `http://localhost:8000` with the development token, then use
**Blueprints → Hello, workflow → Open unsaved draft**. Review and save the draft before explicitly
running it from Flow details. The [first-run guide](docs/operations/onboarding.md) covers readiness,
the isolated playground and the under-20-minute local path.

Apply `examples/nested-flowables.yaml`, then open **Flows → Open graph** to inspect its expanded
sequential, bounded-parallel and DAG plan before execution. Execution details show the same graph with
live task states.

Apply `examples/loops.yaml` to try bounded foreach, while and until execution. The live graph shows one
aggregated node per loop child and its completed iteration count instead of rendering every generated
task run.

The production container also serves the graphical control room at `http://localhost:8000`. Sign in
with the bootstrapped local user and tenant `default`; the development-only `development-token` remains
available through the UI's API-token mode. See the
[frontend guide](frontend/README.md) for the Vite workflow, supported browsers and accessibility
qualification boundary.

The API also supports flow/execution lists, pre-execution and live execution graphs, execution details and logs, durable task-result caching, durable trigger occurrences, execution checks, a tamper-evident audit ledger and signed compliance evidence packages, PostgreSQL-backed users/groups/roles/scoped bindings, local browser sessions, OIDC/SAML/LDAP federation, tenant-bound SCIM provisioning, authorization explanations, OpenRouter/OpenAI-compatible LLM tasks, MCP tool calls, local-process tasks and Kubernetes Job tasks. Prometheus metrics are exposed at `http://localhost:8000/metrics`. See the [trigger lifecycle](docs/operations/triggers.md), [execution checks](docs/operations/execution-checks.md), [audit evidence](docs/operations/audit-evidence.md), [task cache](docs/operations/task-cache.md), [authentication](docs/operations/authentication.md), [identity federation](docs/operations/identity-federation.md) and [authorization](docs/operations/authorization.md) runbooks.

For the reference Kubernetes path—external PostgreSQL, existing Secrets, Helm migration/server/worker roles, a real Luna → Job → HTTP run and cleanup—follow the [MVP Helm quickstart](charts/amesh/README.md).

## Planning workflow

`requirements/urs.json` and structured epic fields in `backlog/epics.json` are canonical. After changing either:

```bash
uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
uv run --extra runtime --extra dev python scripts/validate_backlog.py
```

The regeneration script updates the human URS, CSV exports, traceability matrix, parity matrix, epic issue bodies, backlog index, GitHub issue records and roadmap. CI rejects generated drift.

Useful validation commands:

```bash
uv run --extra runtime --extra dev pytest
uv run --extra runtime --extra dev ruff format --check src tests scripts
uv run --extra runtime --extra dev ruff check src tests scripts
uv run --extra runtime --extra dev mypy src
uv run --extra runtime --extra dev python scripts/generate_contracts.py
uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py --check
```

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

No remote repository has been created or pushed by this working-tree update. Publication scripts are guarded and default to a private repository:

```bash
export GITHUB_OWNER=samchung95
export GITHUB_REPO=amesh
export GITHUB_VISIBILITY=private
export CONFIRM_PUBLISH=samchung95/amesh

bash scripts/publish_github.sh
bash scripts/bootstrap_github_backlog.sh --dry-run
bash scripts/bootstrap_github_backlog.sh
```

Review the working tree and authorize commit, push and issue creation as separate actions.

## License

AMESH is licensed under **GNU Affero General Public License v3.0 only** (`AGPL-3.0-only`). This decision is confirmed. AMESH does not add a non-commercial, competitor or hosted-service restriction because doing so would conflict with the fully open-source objective. See the [licence policy](docs/product/license-policy.md).
