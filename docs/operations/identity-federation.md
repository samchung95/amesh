# Operate enterprise identity federation

AMESH supports multiple OpenID Connect, SAML 2.0 and LDAP providers plus tenant-bound SCIM 2.0 provisioning. Provider definitions are process configuration; client secrets, certificates, LDAP trust anchors and SCIM tokens are read from files when used so operators can rotate mounted material without rebuilding the image.

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

SAML runs as a strict service provider. Assertions must be signed, deprecated signature algorithms are rejected, AuthnRequests and logout messages are signed, and IdP certificate bundles support overlapping signing keys. `nextSpCertFile` publishes the next service-provider certificate in metadata before cutover.

```json
{
  "id": "corporate-saml",
  "kind": "saml",
  "displayName": "Corporate SAML",
  "subjectClaim": "NameID",
  "emailClaim": "email",
  "displayClaim": "displayName",
  "groupsClaim": "groups",
  "idpEntityId": "https://idp.example.com/metadata",
  "ssoUrl": "https://idp.example.com/sso",
  "sloUrl": "https://idp.example.com/slo",
  "idpSigningCertFiles": [
    "/var/run/secrets/amesh/identity/idp-current.crt",
    "/var/run/secrets/amesh/identity/idp-next.crt"
  ],
  "spEntityId": "https://amesh.example.com/saml/metadata",
  "acsUrl": "https://amesh.example.com/api/v1/auth/federated/corporate-saml/callback",
  "spCertFile": "/var/run/secrets/amesh/identity/sp-current.crt",
  "spPrivateKeyFile": "/var/run/secrets/amesh/identity/sp-current.key",
  "nextSpCertFile": "/var/run/secrets/amesh/identity/sp-next.crt"
}
```

Publish service-provider metadata from `GET /api/v1/auth/federated/{provider}/saml/metadata`.

LDAP authentication requires certificate verification and either LDAPS or StartTLS. The authenticated user bind performs the user and group lookup; AMESH never accepts cleartext LDAP.

```json
{
  "id": "directory",
  "kind": "ldap",
  "displayName": "Corporate directory",
  "domains": ["example.com"],
  "ldapHost": "ldap.example.com",
  "ldapPort": 636,
  "ldapCaFile": "/var/run/secrets/amesh/identity/ldap-ca.pem",
  "ldapUserDnTemplate": "uid={identifier},ou=people,dc=example,dc=com",
  "ldapGroupSearchBase": "ou=groups,dc=example,dc=com",
  "ldapGroupFilter": "(member={user_dn})",
  "ldapGroupNameAttribute": "cn"
}
```

## Identity linking and mapping

AMESH links only the immutable `(provider id, subject)` pair. It never automatically links a local or federated account by email. A changed email for an existing subject, or an email already owned by another provider/subject, is rejected as ambiguous. The provider result is observable as a bounded authentication metric and an audit event without storing tokens, passwords or raw subject values in resource metadata.

Group mappings name existing platform groups. At login AMESH synchronizes only memberships it previously created for that provider. Missing groups, roles or tenants fail closed. Provider `domains` and `tenants` drive the login-screen route and are rechecked after the signed assertion is validated.

## Configure SCIM

`SCIM_PROVIDERS` binds each bearer token file to one tenant and default role. For example:

```json
[
  {
    "id": "entra-default",
    "tenant": "default",
    "role": "viewer",
    "tokenFile": "/var/run/secrets/amesh/identity/scim-token"
  }
]
```

The service implements `/scim/v2/ServiceProviderConfig`, Users and Groups list/get/create/PATCH/delete. User disable or delete increments the credential epoch and revokes active browser sessions. Delete tombstones the principal while removing the provider-visible SCIM resource. A token can see and mutate only resources created through its provider id, even if another provider targets the same tenant.

## Rotate credentials and certificates

1. Write new material to a new file in the mounted Secret, Vault or CSI volume.
2. For OIDC client secrets, LDAP CAs and SCIM bearer tokens, atomically replace the referenced file. The next request reads the new value; accepted sessions and durable work continue.
3. For SAML IdP keys, overlap current and next certificate paths in `idpSigningCertFiles`, update the mounted provider configuration, complete the IdP cutover, then remove the retired certificate.
4. For SAML SP keys, set `nextSpCertFile`, let the IdP ingest refreshed AMESH metadata, then switch `spCertFile` and `spPrivateKeyFile` together.
5. Confirm provider routing through `GET /api/v1/auth/providers?identifier=user@example.com&tenant=default`, perform a test login, then inspect authentication metrics and audit events.

Helm accepts the provider JSON from `identity.providerConfigExistingSecret` and mounts certificate/credential files from `identity.credentialSecret` at `identity.mountPath`. Updating those Kubernetes Secrets does not rebuild the image; use the platform's projected-volume refresh and normal configuration reload or rolling restart policy for JSON definition changes.

## Failure behavior

- Invalid, expired, replayed or mismatched state/assertions return a generic authentication failure.
- OIDC discovery, JWKS or token endpoint outages return `503` and require a fresh login start after recovery.
- LDAP invalid credentials return the same `401` as other invalid identities; TLS or directory outages return `503`.
- Logout revokes the AMESH browser session immediately. IdP sessions remain governed by the configured provider logout policy.

The implementation follows [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html), [SAML 2.0](https://docs.oasis-open.org/security/saml/v2.0/), LDAPv3 over TLS, and [SCIM RFC 7643](https://www.rfc-editor.org/rfc/rfc7643) / [RFC 7644](https://www.rfc-editor.org/rfc/rfc7644).
