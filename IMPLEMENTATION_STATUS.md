# Implementation status

AMESH has a delivered `v0.2.0-mvp` foundation and a merge-candidate post-MVP program on PR #1. The
canonical roadmap contains 127 epics mapped to 900 requirements; board and epic completion marks mean
the stated local definition of done was met, not that every production, cloud or compatibility
qualification is complete.

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
- Versioned REST/OpenAPI, CLI and generated Python, TypeScript, Java and Go clients.
- Default, compact, hardened and verification Compose profiles plus a Kubernetes/Helm reference.

## Current merge boundary

The supported merge gate runs locally through Docker. It covers backend lint/type/tests, frontend
unit/build checks, Pi harness conformance, planning and clean-room contracts, current review
regressions, all Compose configurations, the production-image probe and local release-archive
creation. See [Run local verification](docs/how-to/run-local-verification.md) for exact commands and
named deferrals.

Current-head merge-blocking review fixes preserve one MCP invocation identity across retries and defer
tenant API-quota consumption until authorization succeeds. The complete review disposition is in
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
