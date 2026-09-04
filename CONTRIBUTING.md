# Contributing to AMESH

Human and AI contributors follow the same evidence, clean-room and security rules. AI authorship never lowers the definition of done.

## Before starting

1. Read `docs/governance/clean-room-policy.md` and `docs/governance/ai-engineering-model.md`.
2. Select an epic and explicit requirement IDs.
3. Resolve or reference any blocking decision or ADR.
4. Define acceptance, failure and compatibility evidence before implementation.
5. Work in an isolated branch, worktree or disposable environment.
6. Never include credentials, private workflow data, copied proprietary material, upstream source or product assets.

## Development

Enable the Docker-local push gate once per clone:

```bash
make install-git-hooks
```

On Windows PowerShell, use `.\scripts\install-git-hooks.ps1`. The hook runs the complete supported
Docker aggregate before every ordinary push and blocks the push on failure.

```bash
uv sync --extra runtime --extra dev
make verify-local-all
```

On Windows PowerShell, run the same Docker-local aggregate with:

```powershell
.\scripts\verify-local.ps1 -Suite all
```

The aggregate uses locked dependencies inside disposable Docker containers. See the
[local verification guide](docs/how-to/run-local-verification.md) for focused suites and the
explicitly deferred specialist gates.

After requirement or epic changes, run:

```bash
uv run --frozen --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
uv run --frozen --extra runtime --extra dev python scripts/validate_backlog.py
```

Add and edit active epic records in `backlog/epics.json`. Do not hand-move completed records:
regeneration partitions them into the archive declared by the active manifest while validation and
GitHub bootstrap consume the combined catalog.

Use small commits and keep generated files synchronized. A pull request must identify its epic, requirements, changed invariants and verification evidence.

## Architecture rules

- Domain and reducer modules do not depend on FastAPI, PostgreSQL claim mechanics, search projections or object-storage SDKs.
- Durable state changes use typed commands/events, optimistic versions and transactional queue/outbox writes.
- PostgreSQL is the sole supported authoritative database and internal durable transport.
- A notification is a wake-up hint, not proof of work ownership or delivery.
- Untrusted execution code belongs behind runner or isolated plugin boundaries.
- Tenant and actor context are explicit at every boundary.
- Repository code uses `transactions.tenant(...)`. Every `transactions.admin()` call needs a
  pull-request review note naming its instance-scoped reason; the transaction allowlist enforces
  module entrypoints, not admin calls inside allowed modules.
- New PostgreSQL repositories inherit `PostgresRepositoryBase` and write audit rows through the
  shared `AuditWriter`.
- New task kinds derive `configuration_schema` from the handler model, following the five model
  kinds in `src/amesh/tasks/llm.py`, instead of adding entries to the digest table in
  `src/amesh/dsl/handler_contracts.py`.
- Public contracts are versioned and compatibility-tested.
- Search and analytics remain rebuildable PostgreSQL projections.
- Arbitrary external side effects are not described as exactly once.

## AI contribution rules

- An implementation agent cannot approve or be the sole verifier of its own change.
- Architect, implementer, test engineer, reviewer and verifier use independent task contexts for protected changes.
- Agents receive least-privilege, short-lived credentials and no production secrets.
- Model confidence is not evidence; deterministic builds, tests, scans and compatibility fixtures are evidence.
- A failed gate cannot be bypassed by retrying with another agent without recording the failure and remediation.
- Prompts, retrieval sources and workspaces used by clean-room implementers must exclude prohibited upstream source.
- Ordinary changes may merge only after the configured independent reviewer/verifier agent quorum and deterministic gates pass.
- Named human approval is mandatory for security-sensitive changes, licensing or governance changes, destructive production migrations and stable releases.

## Clean-room declarations

Contributors must state whether they have recently worked on relevant Kestra source or proprietary components. Prior familiarity does not automatically prohibit contribution, but strict clean-room work may require researcher/implementer separation and maintainer review.

Do not paste upstream code into issues “for reference.” Link allowed public sources in `SOURCES.md` or a research record and describe observable behavior in original wording.

## Definition of done

See `docs/governance/definition-of-done.md`. Implementation without independent review, tests, failure behavior, documentation, traceability and applicable compatibility evidence is incomplete.
