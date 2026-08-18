# ADR-016: Python confirmed as the production core

- **Status:** Accepted
- **Decision question:** Q-006 (amends the answer recorded in ADR-010)
- **Date proposed:** 2026-08-19
- **Accepted:** 2026-08-19
- **Supersedes:** ADR-010; amends ADR-001

## Context

ADR-010 selected Java 25 for the production durable control plane, with the Python foundation retained as an executable specification until Java reached differential parity. Two things have changed since acceptance:

1. The two-month MVP re-scope (`docs/product/mvp-scope.md`) removed Kestra/Pebble parity from the critical path. Exact Pebble/JVM-adjacent compatibility was the strongest single argument for a Java core; with parity deferred and expressions namespaced as AMESH-native, that driver no longer justifies building the engine twice.
2. The engine will be built MVP-first on the existing Python foundation. Maintaining a second, differential-parity Java implementation would double the correctness surface for a solo-plus-agents team without adding user-visible capability.

The product owner accepted keeping the current architecture on 2026-08-19: Python may be slower, and its robustness must come from the design.

## Decision

The **Python 3.12 asyncio codebase is the production durable control plane**. The "executable specification awaiting a Java port" framing is retired; the checked-in validator, reducer and ports are the seed of the production engine, and tests against them are tests of production behavior.

React/TypeScript for the UI, the language-neutral Protobuf/gRPC plugin and worker boundary, and Java/Python/TypeScript as initial plugin SDK languages are unchanged. Go or Rust remain available for isolated components only after profiling or threat analysis demonstrates a measurable benefit — the same guardrail ADR-010 carried.

## Why

- Robustness in this architecture derives from PostgreSQL as the single source of truth, fenced leases, idempotent commands and a pure reducer — properties that are language-independent and already embodied in the Python code and schema.
- The control plane is an I/O-bound state machine; `docs/architecture/postgresql-transport.md` already identifies PostgreSQL capacity, not compute, as the scaling boundary. Comparable Python orchestrators operate well beyond the Profile M target.
- One implementation eliminates the differential-parity test suite, the dual-toolchain CI, and the risk that the "oracle" and the engine drift apart.
- The team's velocity with AI-assisted engineering is highest in a single, typed (mypy strict), pure-core Python codebase.

## Consequences

- AMESH accepts a lower single-process throughput ceiling than a JVM core. Performance claims (Profile M: 100k executions/day, 50 task starts/s) must be earned through measurement and horizontal scale-out of API/executor/worker processes over the existing lease-and-fencing design, not assumed.
- CPU-heavy per-event work (expression rendering, bulk JSON serialization) is the watch item under the GIL; profiling gates decide if any hot path moves to a native extension or an isolated component.
- If exact Pebble compatibility is ever re-promoted to a requirement, the options are a conformance-tested Python subset or an isolated JVM expression-evaluation service — not a core rewrite.
- The backlog's Java-first sequencing (EPIC-001 build bootstrap, fixture-replay tracks in the implementation kickoff) is superseded; the post-MVP reconciliation pass re-words affected epics and requirements.
- `docs/architecture/backend-language-evaluation.md` is retained as the historical evaluation behind ADR-010; its recommendation no longer binds.

## Guardrails

- The deterministic reducer stays pure: no web, persistence or dependency-injection framework imports.
- Correctness-critical PostgreSQL behavior is verified against a real PostgreSQL instance, including crash, duplicate-delivery and fencing tests.
- `mypy --strict`, ruff and the coverage gate remain mandatory; dynamic-typing shortcuts are not an accepted trade for velocity.
- Third-party plugins remain isolated by default; Python being the core language is not permission to load plugin code in-process.
- Replacing Python requires a superseding ADR with measured operational or performance evidence — the same bar this ADR met to replace Java.

## Alternatives

Retaining the Java plan (rejected: doubles the correctness surface for a deferred benefit) and hybrid Java-engine/Python-spec (rejected: the differential-parity tax lands before any user value). The full option analysis remains in `docs/architecture/backend-language-evaluation.md`.
