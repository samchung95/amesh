## Outcome

Describe the user or operator outcome, not only the code change.

## Traceability

- Epic:
- Requirements:
- ADRs:
- Compatibility target and fixtures:

## Implementation and invariants

- Implementer identity/agent:
- Files and public contracts changed:
- State, delivery, authorization or isolation invariants affected:
- Rollback or forward-fix path:

## Independent evidence

- Reviewer identity/agent:
- Verifier identity/agent:
- Required quorum and approvals:
- Security/compliance classification:
- Human approver and evidence-bundle hash, when required:
- [ ] Reviewer and verifier are independent from the implementer
- [ ] Configured independent-agent quorum is satisfied
- [ ] Named human approval is attached when this change is security-sensitive, licensing/governance-related, destructive or release-bound
- [ ] Unit/property tests
- [ ] Contract/integration tests
- [ ] Failure/restart/duplicate/stale-owner scenario where relevant
- [ ] Authorization and tenant-isolation scenario where relevant
- [ ] Compatibility/differential fixtures where relevant
- [ ] Documentation, migration and operational notes
- [ ] Performance evidence where relevant
- [ ] `make verify-local-all` or `.\scripts\verify-local.ps1 -Suite all`
- [ ] Any separately tracked format, frontend-lint or specialist qualification deferral is named

## AI provenance

- Models and tools used:
- Input-source classes used, excluding secrets and prohibited source:
- Budget/retry exceptions:
- [ ] No raw secrets, sensitive prompts or private user data are recorded
- [ ] Merge eligibility is based on reproducible gates, not model confidence

## Clean room and licensing

- [ ] I authored this change or have the right to contribute it.
- [ ] I did not copy Kestra source, UI assets, documentation prose or proprietary material.
- [ ] New dependencies and copied snippets have compatible licences and preserved notices.
- [ ] No secrets or private user data are included.

## Operational consequences

Describe schema, event, API, plugin, storage, deployment, rollback, compatibility and observability impact.
