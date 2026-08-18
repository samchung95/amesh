# ADR-005: Isolated language-neutral plugins as the default third-party model

- **Status:** Accepted
- **Decision question:** Q-010
- **Date:** 2026-08-15

## Context

AMESH needs a broad plugin ecosystem without making arbitrary third-party code part of the trusted control plane. Existing Kestra users also need a manageable migration path.

## Decision

Define a versioned RPC/OCI plugin protocol with short-lived scoped capabilities. Native SDKs are provided first for Java, Python and TypeScript. In-process loading is reserved for reviewed first-party modules that pass stricter compatibility and security gates.

Kestra plugin configuration is migrated mechanically where a mapping exists. Existing plugin JARs are not promised to run unchanged. A transitional out-of-process JVM bridge may be implemented only when migration measurements show that the native SDK imposes unacceptable cost.

## Migration-overhead guardrail

The migration path is considered acceptable when:

- supported task configuration imports without manual field rewriting;
- generated scaffolding preserves schemas, examples and tests;
- a simple stateless plugin can be ported and certified in a bounded work session;
- unsupported APIs are reported explicitly rather than emulated incorrectly;
- performance overhead is measured separately from source migration effort.

## Consequences

- Stronger fault, dependency and credential isolation.
- Additional serialization and process-start overhead.
- Multi-language ecosystem growth without coupling the core to one runtime.
- A dedicated migration SDK, compatibility report and certification suite are required.

## Revisit triggers

- Representative plugin migrations consistently exceed the accepted effort budget.
- RPC overhead violates published task-latency targets.
- A required compatibility surface cannot be expressed through the protocol.

## Traceability

See `docs/architecture/plugins.md`, `EPIC-300`, `EPIC-303`, `EPIC-313` and `EPIC-704`.
