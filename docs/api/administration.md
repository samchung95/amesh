# Administration API

The administration surface composes existing namespace, authorization, credential, topology,
configuration, feature-flag, search and audit contracts. Every endpoint resolves the tenant from
the authenticated request and applies its own server-side permission check; the web control room is
not an authorization boundary.

## Guarded tenant controls

`GET /api/v1/admin/controls` returns the effective retention, announcement, maintenance and
execution-kill-switch controls. Defaults are returned even before a control has been persisted.

High-risk changes are a two-request workflow:

1. `POST /api/v1/admin/controls/preview` accepts a typed draft with `key`, `enabled`, `value`,
   `reason` and optional `expectedVersion`.
2. The response describes impact and recovery, supplies the exact confirmation phrase, and carries
   a five-minute HMAC approval bound to the actor, tenant and complete draft.
3. `PUT /api/v1/admin/controls/{key}` accepts that unchanged draft, approval and confirmation.

Changing the actor, tenant, path, draft, expiry or confirmation rejects the request with `409`.
Optimistic version conflicts also return `409`. A successful apply persists the control and its
`SUCCESS` administration audit event in one database transaction. Rejected approvals and version
conflicts write `REJECTED` evidence without changing the control.

The four controls are encoded as reserved tenant feature flags so the existing versioned
configuration store remains authoritative:

| Control | Reserved flag | Value |
| --- | --- | --- |
| `RETENTION` | `admin-retention-executions` | 1–3650 days |
| `ANNOUNCEMENT` | `admin-announcement-banner` | Message up to 1,000 characters |
| `MAINTENANCE` | `admin-maintenance-mode` | Enabled state |
| `KILL_SWITCH` | `admin-execution-kill-switch` | Enabled state |

`GET /api/v1/admin/audit?limit=200` reads the immediate immutable control decision history. The
general `/api/v1/search` audit projection provides the broader indexed administration ledger.

## Supporting administration contracts

- `/api/v1/admin/principals`, `/groups`, `/roles`, `/bindings` and principal credential endpoints
  manage users, groups, service accounts, roles, scope bindings and API tokens.
- `/api/v1/auth/providers` lists configured identity entry points. Provider secrets and deployment
  configuration are never returned.
- `/api/v1/operations/topology`, `/api/v1/workers`, `/api/v1/admissions/diagnostics`, `/ready` and
  `/api/v1/search/status` expose service, worker, queue, migration, storage and search posture.
- `/api/v1/configuration` returns the effective value, winning source and reload behavior. Every
  secret-typed value is `[REDACTED]` before serialization.
- `/api/v1/feature-flags` remains available for ordinary tenant or namespace rollout controls;
  callers should not create keys beginning with `admin-`.

See the [administration runbook](../operations/administration.md) for the operator workflow.
