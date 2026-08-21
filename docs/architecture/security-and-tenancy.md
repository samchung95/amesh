# Security and tenancy

## Trust zones

1. Browser and external API clients.
2. Webserver and identity boundary.
3. Orchestration control plane.
4. Worker control channel.
5. Isolated task and plugin workloads.
6. User infrastructure and external services.
7. Metadata, object storage, event bus and search.
8. Identity and secret providers.

Traffic crossing a zone is authenticated, authorized, bounded and observable.

## Authentication

Local bootstrap is limited to initial administration. Production supports OIDC, SAML and LDAP, with SCIM
for lifecycle management. API tokens are hashed or asymmetric, scoped, expiring and visible only once.
Service-to-service identity uses short-lived workload credentials where possible.

## Authorization

Permissions are evaluated by resource/action at instance, tenant and namespace scopes. UI permission
checks improve usability but are never authoritative. Every repository and message handler receives
explicit tenant and actor context.

EPIC-500 implements this boundary through typed actor, permission, role, binding, scope, boundary and
decision contracts. Explicit denies override allows. Namespace grants inherit down dotted namespace
trees until a declared authorization boundary. PostgreSQL stores principals, group memberships,
roles, permissions, bindings and boundaries as the authority.

Decision-cache entries include the monotonic PostgreSQL policy version. Principal, membership, role,
permission, binding and boundary mutations increment that version transactionally; the next request
cannot reuse an older grant. Ordinary denials return only `not authorized`. The detailed
`/api/v1/authorization/explain` evidence is itself restricted to authorization administrators.

The built-in roles are `instance-admin`, `tenant-admin`, `namespace-admin`, `flow-author`, `operator`
and `viewer`. Built-in definitions are immutable, and repository transactions reject removal of the
final effective instance administrator, including administrators granted through a group.

## Tenant isolation

- Tenant ID is present in resources, messages, cache keys, object paths and index documents.
- Repositories cannot execute unscoped tenant queries outside super-administration modules.
- Object storage uses independent prefixes, buckets or credentials.
- Workers and plugins receive one tenant-scoped capability at a time.
- Search documents are constructed and queried with tenant filters that callers cannot override.
- Adversarial tests cover identifier guessing, pagination, timing, logs, metrics and error messages.

## Secrets

Flow definitions contain secret references, never plaintext. Resolution occurs at the worker or isolated
plugin just before use. Values are held for a bounded time, excluded from persistence and protected by
redaction canaries in tests.

## Untrusted content

Flow YAML, expressions, webhook payloads, namespace files, plugin metadata, logs and AI-retrieved content
are untrusted. Parsers have size and recursion limits. Expressions are sandboxed. Archive extraction
prevents traversal and decompression bombs. HTTP capabilities enforce destination policy.

## Administrative safety

High-risk operations support step-up authentication, impact preview and durable audit. Emergency controls
have reason, actor, scope and optional expiry. Audit access is itself audited.

The development bootstrap bearer token is accepted only when both `APP_ENV=development` and
`AUTH_MODE=development`; every other mode fails closed until the durable authentication entry points
from EPIC-403 and EPIC-501 are configured. See the
[authorization runbook](../operations/authorization.md).
