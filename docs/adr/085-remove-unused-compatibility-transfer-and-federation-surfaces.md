# ADR-085: Remove unused compatibility, transfer and federation surfaces

Status: accepted by the product owner on 2026-10-07. Supersedes ADR-009, ADR-013 and ADR-045. Amends
ADR-081, which re-ordered priorities without deleting code.

Context: ADR-081 made the governed agent-session runtime the product focus and deferred Kestra parity
and the enterprise distribution. The surfaces built for those horizons stayed in the tree. The
2026-10-07 review found no deployment, test client or document that used them outside their own tests:

- The Kestra 1.3.30 compatibility façade: flow import, the `kestra` CLI group, the compatibility REST
  routes, conformance fixtures and the `amesh.compatibility.kestra` and `amesh.kestra_compatibility`
  modules.
- Import and transfer tooling: tenant, profile and agent-session export/import, the session
  portability panel and the `tenant-transfer` CLI.
- SAML, LDAP and SCIM federation, and the Terraform `amesh_user` and `amesh_group` resources and data
  sources that wrote through SCIM.

Together they were about 10,600 lines of code, tests and documentation that every change still had to type-check, test, document and
secure, with two extra runtime dependencies (`python3-saml`, `ldap3`).

Decision:
- Delete the Kestra façade, the transfer tooling and the SAML, LDAP and SCIM paths, with their routes,
  CLI commands, configuration, Helm and Compose settings, UI, tests and documentation.
- Keep OIDC federation, local accounts, browser sessions and the rest of the identity plane unchanged.
- Move whole deployments by PostgreSQL backup and restore (ADR-084). There is no per-tenant or
  per-session export.
- Keep the database tables these surfaces created (`agent_transfer_imports`, `auth_scim_resources`,
  `auth_federation_replays`). Migrations are forward-only and checksum-protected, and dropping tables
  is destructive. A later migration can drop them once no supported deployment holds their rows.
- Leave the `requirements/*.json` evidence references to deleted tests in place as history; they no
  longer verify anything. The affected requirements are not delivered.

Alternatives: keeping the code behind a feature flag still carries its maintenance and dependency
cost. Moving it to a separate package needs a consumer to own it, and there is none. Reverting this
change restores it if a consumer appears.

Consequences: API clients, generated SDKs and Terraform configurations that used the removed routes or
resources break; none are known. Restoring a surface means reverting this change and re-qualifying it.
SAML, LDAP or SCIM identity must be brokered through an OIDC provider.
