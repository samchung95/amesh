# ADR-010: Production core language

- **Status:** Accepted
- **Decision question:** Q-006
- **Date proposed:** 2026-08-15
- **Accepted:** 2026-08-16

## Context

The Python foundation is useful for rapid specification work, but the production engine must sustain exact JVM-adjacent compatibility, durable PostgreSQL concurrency, on-premises operation and years of AI-authored maintenance.

## Decision

Use **Java 25** for the modular durable control plane; React/TypeScript for the UI; Java, Python and TypeScript for initial plugin SDKs; and optional Go or Rust worker, sandbox or native components only after profiling or threat analysis demonstrates a measurable benefit.

Keep the existing Python reducer and validator as an independent executable specification until the Java implementation passes equivalent golden, property and differential tests.

## Why

- Pebble is a Java templating engine, so Java minimizes semantic reimplementation or sidecar overhead.
- AMESH is an I/O-heavy transactional server where mature PostgreSQL, observability and service tooling matter.
- Java supplies strong compile-time feedback and widely represented implementation patterns for AI engineering agents.
- Virtual threads support a straightforward model for I/O-heavy concurrency while task workloads remain isolated in runners.
- A transitional JVM plugin bridge remains possible without making in-process plugins the default.

## Consequences

- AMESH accepts a higher baseline memory and image footprint than a Go implementation.
- Build speed, garbage collection, allocation, startup and dependency patching require explicit budgets and qualification.
- The project must avoid reflection-heavy framework coupling and prohibit arbitrary in-process third-party plugins.
- The repository transitions from Python executable specification to Java production implementation without discarding golden fixtures.
- Polyglot service boundaries are deferred until measured evidence justifies them.

## Guardrails

- The deterministic reducer must not depend on web, persistence or dependency-injection frameworks.
- Persisted and public contracts must not rely on preview Java features.
- Correctness-critical PostgreSQL behavior must be verified against a real PostgreSQL instance.
- Third-party plugins remain isolated by default even when authored in Java.
- Replacing Java requires a superseding ADR with compatibility, migration, operational and performance evidence.

## Alternatives

See `docs/architecture/backend-language-evaluation.md`.
