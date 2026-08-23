# EPIC-701 — Terraform and OpenTofu provider

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `devops`
- **Primary persona:** Platform engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Manage platform configuration declaratively through standard infrastructure-as-code tooling.

## In scope

- [x] **URS-F-0702** — The system shall provide resources and data sources for flows, namespaces, files, key-values, dashboards, apps, users, groups, roles, bindings, service accounts, tenants, worker groups and plugin policies.
- [x] **URS-F-0703** — The system shall implement import, refresh, plan, apply and drift detection with stable identifiers.
- [x] **URS-F-0704** — The system shall treat secret values as sensitive and avoid returning provider-resolved plaintext.
- [x] **URS-F-0705** — The system shall support YAML file content and semantic diff suppression where safe.
- [x] **URS-F-0706** — The system shall generate provider documentation and examples from schemas.
- [x] **URS-F-0707** — The system shall test provider compatibility against supported platform releases.
- [x] **URS-F-0708** — The system shall publish signed provider binaries for major operating systems and architectures.
- [x] **URS-F-0709** — The system shall define behavior for server-managed defaults and immutable fields.

## Implementation completion evidence

- 2026-08-23 — EPIC-701 is complete for the locally reproducible provider profile. A first-party Go module serves Terraform plugin protocol v5 and registers 14 named resources plus 14 matching data sources for every scoped platform kind. Public API/SCIM transport supports stable IDs, import, refresh, plan, apply, native deletes, declared retained lifecycles, immutable replacement, server defaults, JSON/YAML semantic diff suppression, environment-only secret expansion and recursive response redaction. Terraform 1.15.8 and OpenTofu 1.12.1 loaded the complete schema; a live key-value scenario passed create, clean refresh, out-of-band drift plan, reconciliation, clean cross-CLI refresh, import and destroy. Schema-generated documentation covers all 28 surfaces. GoReleaser built Linux, macOS and Windows amd64/arm64 archives, all checksums and the protocol manifest verified, and an ephemeral RSA qualification key produced a valid detached signature; the release workflow requires the operator production GPG key. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`terraform-provider.md`](../../docs/operations/terraform-provider.md), [`042-terraform-provider-protocol.md`](../../docs/adr/042-terraform-provider-protocol.md), [`compatibility.json`](../../providers/terraform/compatibility.json), [`provider.go`](../../providers/terraform/internal/provider/provider.go), and [`document_test.go`](../../providers/terraform/internal/provider/document_test.go).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-500

## Architecture impact

- Primary bounded area: `devops`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Declarative apply, drift and CI integration tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Public registry and GitHub release publication require operator-owned repository access and a production RSA/DSA GPG key; local qualification verifies the identical six-archive, manifest, checksum and detached-signature workflow without making an external publication claim.

## Traceability

- Functional requirements: URS-F-0702, URS-F-0703, URS-F-0704, URS-F-0705, URS-F-0706, URS-F-0707, URS-F-0708, URS-F-0709
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
