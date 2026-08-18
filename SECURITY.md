# Security policy

## Reporting

Do not open a public issue for a suspected vulnerability. Use GitHub private security advisories after
the repository is published. Until then, contact the repository owner privately through a verified
channel.

Include the affected commit/version, deployment mode, impact, prerequisites, minimal reproduction and
whether secrets or cross-tenant data may be involved. Do not include real user secrets or private data.

## Initial support policy

This repository is pre-alpha and has no production security support commitment. A formal supported
version and response policy is a GA requirement under EPIC-612 and EPIC-805.

## Security boundaries

The current skeleton is not a secure execution sandbox. Production claims require:

- isolated runners for untrusted code;
- isolated third-party plugins;
- real authentication and authorization;
- external secret management;
- hardened deployment configuration;
- audit coverage;
- vulnerability and penetration testing;
- recovery evidence.

## Dependency and disclosure process

Critical advisories block release unless a documented risk acceptance exists. Security fixes should
receive a private review, coordinated release and public advisory after users can upgrade.
