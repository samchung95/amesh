# ADR-009: Native core with complete version-pinned Kestra compatibility façades

- **Status:** Accepted
- **Decision question:** Q-005
- **Date:** 2026-08-15

## Context

The product owner requires compatibility with all major public Kestra interfaces while AMESH also needs room for agent-native capabilities and cleaner internal contracts.

## Decision

Maintain a coherent canonical AMESH domain model and reducer, then provide version-pinned compatibility parsers, façades and translators for:

- Kestra flow YAML and source-preserving round trips;
- Pebble expressions, functions and error behavior;
- documented REST resources and response semantics;
- CLI commands, exit codes and machine-readable output;
- execution states, retries, timeouts, concurrency, triggers and cancellation semantics;
- documented import/export bundles and namespace resources.

A declared compatibility release may not silently approximate a required behavior. Unsupported cases fail with source-located evidence and block a full-compatibility claim for that target version.

## Consequences

- The core remains maintainable and agent-native features do not have to masquerade as Kestra constructs.
- Compatibility becomes a permanent, expensive product surface with black-box differential tests.
- Public contracts need separate native and compatibility versioning.
- Some endpoints may share implementation while preserving distinct wire schemas.

## Revisit triggers

- Legal review narrows a compatibility surface.
- An upstream change cannot be reproduced without violating a core invariant; the gap must then be explicit rather than hidden.

## Traceability

See `docs/architecture/compatibility.md`, `EPIC-004`, `EPIC-005`, `EPIC-400`, `EPIC-402` and `EPIC-704`.
