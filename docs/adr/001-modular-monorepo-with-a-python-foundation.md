# ADR-001: Modular monorepo with a transitional Python foundation

- **Status:** Accepted / transitional
- **Decision question:** Q-006
- **Date proposed:** 2026-08-15
- **Accepted:** 2026-08-16

## Context

The initial repository contains a small Python/FastAPI validator and reducer. Java 25 is now accepted as the production durable-control-plane language.

## Decision

Keep one modular monorepo and retain the Python code as an independent executable specification, schema generator and golden-fixture producer while the Java implementation is established. Do not expand Python into a competing production engine.

Domain, database, runner and plugin wire contracts remain independent of FastAPI and Python packaging. Java must replay the same golden, property and differential fixtures before replacing any Python behavior as the production reference.

## Consequences

- Existing tests and examples remain immediately useful as an independent oracle.
- Java production work can begin without discarding the validated flow and reducer fixtures.
- Temporary duplicate behavior is intentional and must be retired or clearly scoped after Java conformance parity.
- New production-only orchestration behavior belongs in Java and must be represented in language-neutral fixtures where practical.

## Revisit triggers

- Java covers every checked-in Python behavior and the remaining Python runtime adds no independent conformance value.
- A fixture cannot be expressed language-neutrally without distorting the required behavior.

## Traceability

See `docs/architecture/backend-language-evaluation.md` and `docs/adr/010-production-core-language.md`.
