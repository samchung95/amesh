# AMESH implementation kickoff

**Status:** Ready to begin M0  
**Architecture lock:** 2026-08-16  
**Production core:** Java 25  
**First production topology:** On-premises Kubernetes through Helm

## Objective

Begin implementation without reopening accepted product decisions. The first vertical slice must prove that the Java core can reproduce the checked-in Python flow-validation and execution-reducer behavior before broader orchestration work expands.

## First implementation sequence

### Track A — governance and repository controls

Start `EPIC-000`, `EPIC-001` and `EPIC-011`.

1. Preserve the clean-room source boundary and provenance register.
2. Add the Java 25 modular build, formatter, static analysis, architecture tests and dependency policy.
3. Make generated artifacts and golden fixtures reproducible in CI.
4. Enforce independent agent review, issue ownership and protected high-risk paths.

### Track B — canonical domain and compatibility fixtures

Start `EPIC-002`, followed by `EPIC-004` and `EPIC-007`.

1. Freeze the current Python validator and reducer examples as language-neutral fixtures.
2. Define canonical identifiers, resource revisions, commands, events and execution states in Java.
3. Replay the fixtures against Java and require byte-stable or semantically equivalent outputs.
4. Add property tests for legal transitions, idempotency, restart epochs and invalid dependency graphs.

### Track C — configuration and storage foundations

Start `EPIC-003` and `EPIC-010` in parallel, then `EPIC-008` and `EPIC-009` after their dependencies are satisfied.

1. Define layered configuration with explicit secret and tenant boundaries.
2. Define content-addressed object and artifact references.
3. Implement PostgreSQL migrations and repositories against a real test database.
4. Implement inbox, outbox, queue claims, leases and fencing with crash and duplicate-delivery tests.

### Track D — expression compatibility

Begin `EPIC-005` only after the source-preserving flow model in `EPIC-004` is stable enough to host expression fixtures.

1. Establish a version-pinned Pebble compatibility harness.
2. Catalogue filters, functions, escaping, null handling and error behavior.
3. Keep AMESH-native extensions namespaced and separate from compatibility behavior.

## Recommended first pull-request queue

1. `build(java): bootstrap the Java 25 modular build and CI gates` — `EPIC-001`
2. `test(conformance): freeze Python golden fixtures and cross-language fixture schema` — `EPIC-000`, `EPIC-007`
3. `feat(domain): add canonical resource identifiers and revision model` — `EPIC-002`
4. `feat(execution): port the deterministic reducer to Java` — `EPIC-007`
5. `feat(flow): add source-preserving YAML model and validation` — `EPIC-004`
6. `feat(config): add typed layered configuration` — `EPIC-003`
7. `feat(storage): add artifact addressing contracts` — `EPIC-010`
8. `feat(pebble): establish the compatibility fixture harness` — `EPIC-005`
9. `feat(postgres): add resource, event and snapshot repositories` — `EPIC-008`
10. `feat(transport): add PostgreSQL inbox, outbox, queue and fenced leases` — `EPIC-009`

Each pull request should remain narrow enough for an independent agent to reproduce, test and review without relying on hidden context.

## First vertical-slice exit gate

The first Java slice is complete only when:

- the Java build runs from a clean checkout using a pinned Java 25 toolchain;
- Java validates every checked-in example accepted by Python and rejects the same invalid fixtures;
- Java produces equivalent reducer results for every checked-in event sequence;
- duplicate-event, invalid-transition and restart-epoch properties pass;
- public fixture formats are language-neutral and versioned;
- no production domain module depends on the web framework, PostgreSQL adapter or Python runtime;
- clean-room, licence, static-analysis, unit, property and architecture gates pass;
- evidence is linked to the applicable URS requirements and epic issue bodies.

## Do not start with

Do not begin with the visual editor, marketplace, broad integration packs, cloud runners or distributed scale tuning. Those depend on stable flow, state, plugin and persistence contracts and would create expensive rework if started first.

## Product-owner escalation rule

Implementation agents should proceed using accepted ADRs. Escalate only when a proposed change would alter a compatibility surface, AGPL policy, tenant/security boundary, release SLO, migration guarantee, supported production topology or human-approval requirement.
