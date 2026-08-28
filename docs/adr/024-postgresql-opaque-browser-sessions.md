# ADR-024: PostgreSQL-backed opaque browser sessions

Status: accepted

Context: AMESH needs local multi-user browser login, revocation, inactivity/absolute expiry, CSRF protection and a future federated identity boundary. EPIC-403 and EPIC-502 previously depended on each other, leaving local login blocked.

Decision: EPIC-403 defines a provider-neutral identity-provider port and ships a local adapter. Local passwords use `pwdlib[argon2]` with the recommended Argon2id profile. PostgreSQL stores password hashes and only HMAC digests of random opaque session and CSRF secrets. The browser uses an HTTP-only same-site session cookie plus a CSRF cookie/header pair; authorization remains the existing separate RBAC service. EPIC-502 will add concrete OIDC, SAML, LDAP and SCIM adapters after this boundary exists.

Consequences: logout, password changes, principal credential epochs and administrative revocation take effect without waiting for token expiry; session validation requires PostgreSQL; production cookies require HTTPS. `pwdlib` is a small MIT-licensed facade recommended by FastAPI and supports hash upgrades, while `argon2-cffi` supplies the maintained RFC 9106 Argon2 implementation. Revisit only if a later federated protocol requires a distinct external session exchange, not to replace server-side revocation.
