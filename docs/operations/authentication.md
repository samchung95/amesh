# Operate local authentication

Use this guide to bootstrap local administration, create additional login users and manage browser sessions.

## Bootstrap the first administrator

Apply all database migrations, then run the one-time bootstrap command from a trusted terminal:

```powershell
uv run --extra runtime amesh auth bootstrap-admin --handle root-admin --display-name "Root administrator"
```

The command prompts twice and never accepts a password argument. For a protected automation channel,
pipe one line with `--password-stdin`. The operation creates one `USER` principal, one Argon2id hash and
one instance-administrator binding atomically. It fails after the first local credential exists; AMESH
ships no universal username or password.

## Add another login user

1. As an instance or delegated principal administrator, create a `USER` through
   `POST /api/v1/admin/principals`.
2. Grant the user one or more instance, tenant or namespace role bindings.
3. Set the initial local password through
   `PUT /api/v1/admin/principals/{principal_id}/local-password` over TLS.
4. Give the user their handle and password through an approved secret-delivery channel.

The password endpoint increments the principal credential epoch and revokes every existing browser
session. Users rotate their own password through `POST /api/v1/auth/password`; it verifies the current
password and performs the same revocation.

## Sign in and revoke sessions

Open the AMESH root URL, keep **Local account** selected, and enter the user handle, password and tenant.
The server sets an HTTP-only session cookie and a separate CSRF cookie. Unsafe browser requests must send
the CSRF value in `X-Amesh-CSRF`. Sessions rotate during use, expire after inactivity and have an absolute
lifetime. In production, both cookies use the `__Host-` prefix and require HTTPS.

- `POST /api/v1/auth/logout` revokes the current browser session.
- `POST /api/v1/auth/logout-all` revokes every session for the current user.
- `DELETE /api/v1/admin/principals/{principal_id}/sessions` performs administrator revocation.
- Disabling a user or changing its credential epoch fences existing sessions at the next request.

API and CLI clients continue to use the scoped, expiring bearer credentials documented in the
[credential runbook](credentials.md).

## Configure policy and limits

`AUTH_POLICY=local` enables local login; `hybrid` enables local accounts and configured enterprise
identity providers; `federated-only` removes the local provider and rejects local login or bootstrap.
Configure OIDC, SAML, LDAP and SCIM integrations through the
[identity federation runbook](identity-federation.md). Configure inactivity,
absolute lifetime, rotation, overlap, source rate, account failure and lockout limits with the
`AUTH_SESSION_*` and `AUTH_LOGIN_*` settings shown in `.env.example` and the Helm `auth` values.

Authentication metrics use only bounded provider/outcome labels. Audit rows record the provider, result,
reason and affected identifiers, never passwords, browser tokens, CSRF material or raw source addresses.
