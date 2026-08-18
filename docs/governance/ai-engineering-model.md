# AI engineering operating model

AMESH is intended to be implemented primarily by AI engineering agents. This increases parallelism but does not remove the need for independence, deterministic evidence, provenance and accountable release authority.

Q-021 selects **independent agent quorum for ordinary merges** and **named human approval for high-risk changes and stable releases**.

## Agent roles

- **Product planner:** converts approved outcomes into requirement-linked epics and acceptance criteria.
- **Architect:** owns ADR proposals, boundaries, invariants and compatibility impact.
- **Implementer:** changes only the assigned worktree and declared files.
- **Test engineer:** creates adversarial, property, differential and fault-injection tests independently from the implementation context.
- **Reviewer:** inspects the diff, requirement traceability, security impact and failure behavior.
- **Verifier:** runs clean-room, build, test, migration, compatibility and reproducibility gates.
- **Security reviewer:** is mandatory for identity, secrets, sandboxing, deserialization, networking, cryptography and supply-chain changes.
- **Compliance reviewer:** checks control mappings and evidence impact where SOC 2 or ISO/IEC 27001 readiness is affected.
- **Release agent:** assembles evidence but cannot waive failed gates or approve its own constituent changes.
- **Human release authority:** approves specified high-risk changes and every stable release.

## Separation rules

1. No agent may approve its own implementation.
2. The implementer and primary verifier use separate task contexts and independently derived test expectations.
3. Protected branches reject direct writes and unsigned release artifacts.
4. Agents receive least-privilege, short-lived credentials and isolated worktrees or containers.
5. A failed gate cannot be bypassed by retrying with a different agent unless the failure and remediation are recorded.
6. Requirements, ADRs and public contracts change in the same pull request as affected code or through an explicitly linked predecessor.
7. Clean-room implementers must not be given prohibited upstream source material in prompts, retrieval indexes or workspaces.
8. Agent identities, role assignments, model/tool provenance and conflicts of interest are recorded in the evidence bundle.
9. A security-sensitive classification may be escalated automatically but cannot be downgraded solely by the implementation agent.

## Ordinary merge quorum

A normal protected-branch change may merge without per-change human approval only when:

- all deterministic required gates pass;
- the implementer is distinct from the reviewer and verifier;
- the configured independent-agent quorum approves;
- no reviewer has an unresolved blocking finding;
- the change is not classified as human-approval-required;
- requirement, contract, migration and operational evidence are complete;
- branch policy evaluates the same evidence bundle reproducibly.

The initial policy should require at least:

- one independent review-agent approval; and
- one independent verifier-agent approval;

with stricter quorum for high-risk bounded areas. The exact quorum is repository policy, not hard-coded into the orchestration engine.

## Human approval required

A named human must approve:

- security-sensitive changes;
- authentication, authorization, secret, sandbox or cryptographic control weakening;
- licence, trademark, governance or contributor-rights changes;
- destructive production migrations or data-deletion procedures;
- waivers of Must requirements or failed release gates;
- emergency bypass activation;
- every stable release and security release.

A human approval records identity, scope, evidence bundle hash, decision, expiry where applicable and rationale.

## Required pull-request evidence

Every implementation pull request includes:

- linked epic and requirement IDs;
- an implementation plan and changed invariants;
- files and public contracts changed;
- unit, contract, integration and compatibility evidence;
- failure, rollback and migration notes;
- model/tool provenance without storing secrets or prohibited source material;
- independent review and verification results;
- security/compliance classification;
- unresolved risks and known parity gaps;
- deterministic merge-policy result.

## Merge policy

A change is eligible to merge only when:

- formatting, compilation, static analysis and tests pass;
- generated files and schemas are reproducible;
- clean-room and licence scans pass;
- relevant compatibility fixtures pass;
- the reviewer and verifier are not the implementer;
- required security and compliance review is complete;
- no Must requirement is silently weakened;
- the required quorum approves;
- any required human approval is present and bound to the evidence hash;
- the designated release authority has not blocked the change.

## Emergency procedure

An emergency procedure may shorten normal review only through an explicit policy with:

- named human authorization;
- narrowly defined scope;
- automatic expiry;
- preserved audit and evidence;
- no disabling of clean-room, secret or artifact-integrity checks;
- mandatory retrospective review and remediation issue.

Emergency authority cannot silently change licensing or publish an untraceable stable release.

## Autonomy boundaries

AI agents may plan, code, test, review, document, merge ordinary eligible changes and prepare releases. They may not silently redefine product scope, accept legal risk, alter licensing, waive security controls, destroy persistent production data or publish a stable release without the required human authority.
