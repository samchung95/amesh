# Operate enterprise identity federation

AMESH supports multiple OpenID Connect providers. Provider definitions are process configuration; client secrets are read from files when used so operators can rotate mounted material without rebuilding the image. SAML, LDAP and SCIM were removed by [ADR-085](../adr/085-remove-unused-compatibility-transfer-and-federation-surfaces.md).

## Configure providers

Set `AUTH_POLICY=hybrid` to keep local recovery accounts or `federated-only` to hide and reject local login. `IDENTITY_PROVIDERS` is a JSON array. Every provider has an `id`, `kind`, `displayName`, optional `domains` and `tenants`, configurable claim names, explicit external-to-platform group mappings, and an optional default tenant role.

OIDC authorization-code flow always uses PKCE S256, state and nonce. Discovery issuer and endpoint transport are validated; signed ID tokens enforce issuer, audience, expiry, nonce and an allowlist of asymmetric algorithms.

```json
[
  {
    "id": "corporate-oidc",
    "kind": "oidc",
    "displayName": "Corporate OIDC",
    "domains": ["example.com"],
    "tenants": ["default"],
    "issuerUrl": "https://idp.example.com",
    "clientId": "amesh",
    "clientSecretFile": "/var/run/secrets/amesh/identity/oidc-client-secret",
    "redirectUri": "https://amesh.example.com/api/v1/auth/federated/corporate-oidc/callback",
    "subjectClaim": "sub",
    "emailClaim": "email",
    "displayClaim": "name",
    "groupsClaim": "groups",
    "groupMappings": [{"external": "Engineering", "platformGroup": "engineers"}],
    "defaultTenant": "default",
    "defaultRole": "viewer"
  }
]
```

## Identity linking and mapping

AMESH links only the immutable `(provider id, subject)` pair. It never automatically links a local or federated account by email. A changed email for an existing subject, or an email already owned by another provider/subject, is rejected as ambiguous. The provider result is observable as a bounded authentication metric and an audit event without storing tokens, passwords or raw subject values in resource metadata.

Group mappings name existing platform groups. At login AMESH synchronizes only memberships it previously created for that provider. Missing groups, roles or tenants fail closed. Provider `domains` and `tenants` drive the login-screen route and are rechecked after the signed ID token is validated.

## Rotate credentials

1. Write new material to a new file in the mounted Secret, Vault or CSI volume.
2. For OIDC client secrets, atomically replace the referenced file. The next request reads the new value; accepted sessions and durable work continue.
3. Confirm provider routing through `GET /api/v1/auth/providers?identifier=user@example.com&tenant=default`, perform a test login, then inspect authentication metrics and audit events.

Helm accepts the provider JSON from `identity.providerConfigExistingSecret` and mounts credential files from `identity.credentialSecret` at `identity.mountPath`. Updating those Kubernetes Secrets does not rebuild the image; use the platform's projected-volume refresh and normal configuration reload or rolling restart policy for JSON definition changes.

## Failure behavior

- Invalid, expired, replayed or mismatched state or ID tokens return a generic authentication failure.
- OIDC discovery, JWKS or token endpoint outages return `503` and require a fresh login start after recovery.
- Logout revokes the AMESH browser session immediately. IdP sessions remain governed by the configured provider logout policy.

The implementation follows [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html).
