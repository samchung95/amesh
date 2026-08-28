# ADR-031: Pydantic configuration snapshots and PostgreSQL feature flags

- Status: Accepted
- Date: 2026-08-22
- Owners: EPIC-003

## Context

AMESH already uses a pinned Pydantic Settings model for process configuration and PostgreSQL as the
authoritative control-plane store. EPIC-003 requires explicit source precedence, secret references,
safe reloads, administrative diagnostics and instance/tenant/namespace feature flags.

Pydantic Settings already supplies typed validation and established environment, dotenv, CLI and
secret-file primitives. OpenFeature defines a useful provider/evaluation-details boundary, but adding
its SDK would not supply AMESH's scoped persistence, authorization or audit rules.

## Decision

1. Keep `Settings` as the only typed process-configuration model. An AMESH loader composes defaults,
   ordered YAML/JSON files, environment values and `--set` overrides, resolves `secret://` references,
   migrates declared legacy names and records the winning source for every field.
2. Expose only a redacted immutable configuration snapshot. Secret-typed fields never appear in
   plaintext in API, diagnostic or structured-log output.
3. Reload creates and fully validates a candidate snapshot before publication. Only fields in the
   explicit reloadable registry may differ; any other difference rejects the whole reload.
4. Persist boolean flags and their revisions in PostgreSQL. Resolution is deterministic:
   namespace overrides tenant, tenant overrides instance, and the caller-supplied default is last.
   Results include the matched scope and reason, following the useful portion of OpenFeature's
   provider/evaluation-details contract without adding an SDK dependency.
5. Configuration and flag administration use existing authorization and immutable audit evidence.
   Tenant-scoped reads are filtered to the selected tenant and optional namespace.

## Consequences

- No new dependency is added; pinned Pydantic Settings and PyYAML remain the reused parsing and
  validation primitives.
- Process settings that affect constructed services still require restart unless explicitly listed as
  reloadable.
- Vendor flag providers and advanced targeting rules can later implement the same resolution port;
  EPIC-003 intentionally provides only the required boolean scope hierarchy.
