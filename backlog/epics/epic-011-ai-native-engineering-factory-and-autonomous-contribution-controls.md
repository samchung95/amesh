# EPIC-011 — AI-native engineering factory and autonomous contribution controls

- **Milestone:** M0 — Foundation and clean-room baseline
- **Priority:** Must
- **Domain:** `engineering`
- **Primary persona:** AI engineering lead
- **Parity scope:** AMESH engineering differentiator; not a Kestra-parity claim

## Outcome

Make elastic AI engineering teams productive while preserving independent review, clean-room provenance, isolation and deterministic release evidence.

## In scope

- [ ] **URS-F-0798** — The system shall represent every implementation assignment as a requirement-linked machine-readable work item with scope, dependencies, allowed files and acceptance evidence.
- [ ] **URS-F-0799** — The system shall assign architect, implementer, test engineer, reviewer and verifier roles using independent task contexts.
- [ ] **URS-F-0800** — The system shall confine AI changes to isolated branches or worktrees and prevent direct writes to protected release branches.
- [ ] **URS-F-0801** — The system shall require every AI-authored pull request to record changed requirement IDs, implementation plan, risk, provenance and test evidence.
- [ ] **URS-F-0802** — The system shall prohibit an implementation agent from approving or being the sole verifier of its own change.
- [ ] **URS-F-0803** — The system shall execute AI-generated builds and tests in ephemeral least-privilege environments without production credentials.
- [ ] **URS-F-0804** — The system shall apply explicit token, cost, retry and elapsed-time budgets to engineering agents and escalate exhausted work with evidence.
- [ ] **URS-F-0805** — The system shall generate a signed evidence bundle containing reviews, test results, compatibility results, schemas, SBOM and traceability before release.
- [ ] **URS-F-0836** — The system shall allow a normal protected-branch change to merge only after deterministic gates pass and a configured quorum of independent review and verification agents approves it.
- [ ] **URS-F-0837** — The system shall require named human approval for security-sensitive changes, licensing or governance changes, destructive production migrations and every stable release.

## Explicit non-goals

- Treating model confidence as verification
- Allowing an implementer to approve its own change

## Non-functional requirements

- [ ] **URS-NFR-AIENGINEERING-001** — Every AI-authored production change shall receive review and verification from agents that did not implement the change. Target: 100% of protected-branch changes contain distinct implementer, reviewer and verifier identities.
- [ ] **URS-NFR-AIENGINEERING-002** — AI contributions shall preserve model, tool, input-source and artifact provenance without storing secrets or prohibited source material. Target: 100% of AI-authored pull requests and releases have a valid provenance record and pass clean-room scans.
- [ ] **URS-NFR-AIENGINEERING-003** — Engineering agents shall operate with least privilege and shall not receive production credentials or unreviewed default-branch write access. Target: Zero production credentials in agent sandboxes and zero direct protected-branch mutations in policy tests.
- [ ] **URS-NFR-AIENGINEERING-004** — Merge and release eligibility shall be computed from reproducible policy and evidence rather than model confidence. Target: Repeated evaluation of the same evidence bundle produces the same eligibility result.

## Dependencies

- EPIC-000
- EPIC-001

## Architecture impact

- Primary bounded area: `engineering`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- AI engineering workflow, isolation and evidence-gate tests.
- AI merge-policy, quorum and evidence-replay tests.
- Protected-branch and release-authority policy tests.
- Repository policy and pull-request evidence audit.
- Provenance-schema, secret-scan and clean-room gate tests.
- Credential canary and branch-protection integration tests.
- Golden evidence-bundle and policy replay tests.
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

- Agents may reinforce the same incorrect assumption across roles
- Unbounded retries can consume cost without improving evidence
- Prohibited upstream source can leak through prompts or retrieval indexes
- Autonomous changes can outrun product or release authority

## Traceability

- Functional requirements: URS-F-0798, URS-F-0799, URS-F-0800, URS-F-0801, URS-F-0802, URS-F-0803, URS-F-0804, URS-F-0805, URS-F-0836, URS-F-0837
- Non-functional requirements: URS-NFR-AIENGINEERING-001, URS-NFR-AIENGINEERING-002, URS-NFR-AIENGINEERING-003, URS-NFR-AIENGINEERING-004
- Source scope: AMESH engineering differentiator; not a Kestra-parity claim
