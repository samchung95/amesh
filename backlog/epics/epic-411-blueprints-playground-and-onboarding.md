# EPIC-411 — Blueprints, playground and onboarding

- **Milestone:** M4 — API, UI and self-service
- **Priority:** Must
- **Domain:** `ui`
- **Primary persona:** New user
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Help users learn and start workflows without weakening production controls.

## In scope

- [ ] **URS-F-0486** — The system shall provide versioned blueprint templates with parameters, documentation, license and provenance.
- [ ] **URS-F-0487** — The system shall search and preview built-in, organization and community blueprint catalogs.
- [ ] **URS-F-0488** — The system shall instantiate a blueprint into a draft flow without executing it automatically.
- [ ] **URS-F-0489** — The system shall provide a playground that validates and simulates supported expressions and flow fragments.
- [ ] **URS-F-0490** — The system shall isolate playground execution from production credentials and infrastructure by default.
- [ ] **URS-F-0491** — The system shall guide first-time administrators through storage, database, runner and authentication readiness.
- [ ] **URS-F-0492** — The system shall provide sample data and local-only examples that run in the reference Compose environment.
- [ ] **URS-F-0493** — The system shall track onboarding completion locally without requiring external telemetry.

## Non-functional requirements

- [ ] **URS-NFR-USABILITY-003** — A new contributor shall be able to start the reference stack and run a sample flow from documented steps. Target: Median completion below 20 minutes on a clean supported workstation, excluding image download time.

## Dependencies

- EPIC-405
- EPIC-305

## Architecture impact

- Primary bounded area: `ui`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Automated browser, accessibility and manual usability tests.
- Quarterly external documentation usability test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [ ] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [ ] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [ ] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [ ] Security, tenant isolation, redaction and audit behavior are reviewed.
- [ ] Documentation, examples, migration notes and operational runbooks are updated.
- [ ] Performance and recovery budgets are measured when this epic is on a critical path.
- [ ] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Compatibility is version-pinned; gaps must remain explicit and release-scoped.
- Qualification claims are valid only for the published profile, topology, configuration and evidence set.

## Traceability

- Functional requirements: URS-F-0486, URS-F-0487, URS-F-0488, URS-F-0489, URS-F-0490, URS-F-0491, URS-F-0492, URS-F-0493
- Non-functional requirements: URS-NFR-USABILITY-003
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
