# Implementation status

AMESH has a delivered `v0.2.0-mvp` foundation and a merged post-MVP program on `main`. Its product
focus is the governed agent-session runtime on a durable workflow backbone
([ADR-081](docs/adr/081-focus-on-governed-agent-session-runtime.md)). The canonical catalog holds
135 epics (116 done, 19 open) mapped to 900 requirements. Board and epic completion marks mean the
stated local definition of done was met. They do not mean every production, cloud or compatibility
qualification is complete.

The open epics are ecosystem and production gates. ADR-081 prioritizes session-runtime
reliability, security and production qualification (EPIC-606, EPIC-611, EPIC-612) and session
depth (EPIC-801, EPIC-806). It defers the plugin packs (EPIC-308–311), Git sync (EPIC-700), cloud
batch runners (EPIC-223), multi-region (EPIC-803) and enterprise distribution (EPIC-804) until a
consumer needs them. `tests/documentation/test_status_consistency.py` checks the counts in this
file against the catalog.

## What is implemented

- A Python 3.12 asyncio control plane with PostgreSQL-authoritative workflow, scheduling, queue,
  execution, identity, policy and evidence state.
- Durable DAGs, sequential/parallel flowables, conditions, bounded loops, subflows, backfills, replay,
  retries, cancellation and restart recovery.
- A React control room with guided workflow creation, catalog-backed choices, active-run monitoring,
  simple execution traces, expert logs/topology/data views and agent-run inspection.
- Local authentication, service/API credentials, users, groups, RBAC, tenant isolation, federation
  contracts, SCIM, audit evidence and administrative controls.
- Local-process, Docker/OCI and Kubernetes runner implementations behind a common capability contract.
- Plugin manifests, discovery, isolated runtimes, version policy, certification surfaces and a
  capability/connection catalog for provider-neutral tools.
- Provider-neutral model, MCP and structured-output primitives; versioned prompts, skills and agent
  definitions; Pi-backed bounded sessions; context compaction, cache evidence, memory, evaluation,
  multi-agent hand-offs, differential shadow runs and promotion controls.
- An independently consumable agent-session API with required tool plans (ordered and unordered),
  approvals, checkpoint-bound consumer briefs, execution-scoped MCP grants, snapshot/resume and
  subscription-backed Codex/Copilot model engines.
- Versioned REST/OpenAPI, CLI and generated Python, TypeScript, Java and Go clients.
- Default, compact, hardened and verification Compose profiles plus a Kubernetes/Helm reference.

## Current merge boundary

The supported merge gate runs locally through Docker. It covers backend lint/type/tests, frontend
unit/build checks, Pi harness conformance, planning and clean-room contracts, current review
regressions, all Compose configurations, the production-image probe and local release-archive
creation. See [Run local verification](docs/how-to/run-local-verification.md) for exact commands and
named deferrals. The required remote checks are the `verify` and `image` GitHub Actions jobs
([ADR-080](docs/adr/080-minimal-hosted-ci-mirroring-docker-local-gate.md)). They run the same gate
except local release-archive creation.

Open defects and audit findings are tracked as GitHub issues; the 2026-09-26 repository audit is
labelled `audit-2026-09-26`. The historical MVP review disposition is in
[MVP PR #1 review risk triage](docs/reviews/mvp-pr-1-risk-triage.md).

## Explicitly not claimed

AMESH does not yet claim full Kestra YAML/Pebble/runtime parity, profile-M scale, production HA or
backup/restore qualification, current-head PostgreSQL 15–18 matrix qualification, cloud-provider
reference qualification, air-gapped/multi-architecture release qualification, uninterrupted 24-hour
soak completion, compliance certification, production qualification of the agent-session surface
beyond its published local reference profile, or automatic artifact publication. The exact open and
deferred boundaries remain authoritative in the repository board and canonical epic backlog.

See [the documentation index](docs/README.md), [the accepted MVP scope](docs/product/mvp-scope.md),
[the verification log](docs/reviews/TESTLOG.md), [the active plan](PLAN.md) and [the progress log](PROGRESS.md).
