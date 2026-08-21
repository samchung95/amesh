# Implementation status

AMESH has implemented and verified the product-owner-amended two-month MVP vertical slice and tagged it as `v0.2.0-mvp`. The broader 103-epic roadmap and all parity claims remain open.

## Implemented MVP slice

- Python 3.12 asyncio control plane with PostgreSQL as authoritative state.
- Durable PostgreSQL transport with `SKIP LOCKED` claims, expiring leases, fencing, inbox/outbox deduplication and `LISTEN/NOTIFY` wake-ups.
- Persisted executions, task runs and attempts; restartable top-level DAG execution; retry, timeout, cancellation and fenced terminal writes.
- AMESH-native sandboxed expressions for inputs, outputs, variables and `runIf`.
- Timezone-aware `core.cron` scheduling with one PostgreSQL-idempotent execution per occurrence; manual and webhook triggers.
- Local-process and Kubernetes Job runners with captured outputs and recovery of an in-flight Job after pod or worker loss.
- In-process `core.log`, `core.return`, `core.http`, OpenAI-compatible `agent.llm` and MCP `agent.mcp` task handlers.
- Static-token REST API and CLI for validation, flow apply/list, execution create/get/list/logs and webhook invocation.
- JSON logs, Prometheus `/metrics`, a uv-locked numeric non-root container and a Helm chart for migration, server and recovery-worker roles against external PostgreSQL.
- Checked-in Luna → Kubernetes shell → HTTP demo flow and reproducible kind quickstart.

## Current verification

- 47 tests pass at 80.47% branch coverage with real PostgreSQL, kind and live OpenRouter `openai/gpt-5.6-luna` enabled.
- Ruff formatting/lint and strict mypy pass.
- A fresh kind v0.32.0 / Kubernetes v1.36.1 installation completed migrations, rollouts, health and metrics checks and the live demo.
- A second clean-cluster quickstart reproduction passed.
- The exact release-candidate image passed an in-cluster cron occurrence test.
- The owner-accepted W8 failure run completed 270 unique single-attempt executions while deleting 270 task pods, 27 server pods and 13 worker pods; independent API rereads found zero lost or duplicated executions.
- Source and wheel artifacts build with `uv`; isolated wheel import and CLI checks report version `0.2.0`; the exact release image runs as numeric user `100:101` and exposes healthy `/health` and `/metrics` endpoints.
- The remaining uninterrupted 86,400-second qualification is explicitly deferred to EPIC-611 and must pass before broader availability, scale or production-readiness claims.

## Explicitly not claimed

The MVP does not claim Kestra/Pebble compatibility, multi-tenant identity or RBAC, web UI, HA, backup/restore, distributed scheduler leases, Docker standalone execution, isolated plugin packaging, profile-M performance, air-gapped/multi-architecture release artifacts, compliance evidence or the other deferred capabilities in the accepted deferral register.

The 900 roadmap requirements remain `Proposed`. Evidence-linked MVP progress is recorded on affected epics without marking those broader epics or requirements complete.

See [the accepted MVP scope](docs/product/mvp-scope.md), [the verification log](TESTLOG.md), [the active plan](PLAN.md) and [the progress log](PROGRESS.md).
