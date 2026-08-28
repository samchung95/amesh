# ADR-018: PostgreSQL-backed domain authorization

- Status: Accepted
- Date: 2026-08-21
- Scope: EPIC-500

## Context

AMESH needs resource/action authorization for users, groups and service accounts at instance,
tenant and namespace scopes. Decisions must be explainable, explicit denies must override grants,
namespace inheritance must stop at declared boundaries, and a revoked binding or membership must not
remain effective through a stale cache. PostgreSQL is already the authoritative control-plane store.

PyCasbin supports RBAC domains, deny overrides and async enforcement, but its generic string policy
model would duplicate AMESH resource, lifecycle and evidence contracts and would still require a
custom PostgreSQL administration and invalidation layer. Oso Cloud adds an external policy authority,
which conflicts with the on-premises reference architecture. Cedar does not remove the need for the
AMESH-specific binding, boundary, audit and last-administrator rules.

## Decision

Implement the bounded AMESH policy model directly:

1. PostgreSQL stores principals, group memberships, roles, permissions, bindings, namespace
   boundaries and a monotonic policy version.
2. A pure domain evaluator applies deny-overrides, resource/action matching and scope inheritance.
   A namespace boundary prevents bindings above it from flowing into the bounded subtree.
3. All enforcement adapters call one authorization service. REST dependencies, CLI requests, UI
   requests, workers and plugins consume the same actor/request/decision contracts.
4. Decision-cache keys include the authoritative policy version. Every policy or membership mutation
   increments that version in the same transaction, so requests begun after revocation cannot reuse an
   earlier decision.
5. Ordinary denials expose only a stable reason code. Detailed matched-role evidence is available only
   through an administrator-authorized explanation operation.
6. Built-in roles are immutable and least-privilege except for the explicit instance-administrator
   role. Removing the final enabled instance-administrator binding is rejected transactionally.
7. The static bootstrap token is an authenticated development principal only. Non-development modes
   fail closed until EPIC-403/EPIC-501 provide a durable credential entry point.

## Consequences

- Policy semantics remain small, typed, deterministic and covered by exhaustive tests.
- PostgreSQL stays authoritative and no new runtime dependency or external service is introduced.
- Authentication protocols and token lifecycle remain separate work under EPIC-403, EPIC-501 and
  EPIC-502.
- EPIC-503 will extend tenant provisioning and isolation while consuming this authorization boundary.
