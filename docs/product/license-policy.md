# Licence policy

## Decision

AMESH is distributed under **GNU Affero General Public License version 3 only** (`AGPL-3.0-only`). The “only” form does not automatically grant use under a future AGPL version.

This is the strongest network-copyleft direction selected while preserving AMESH’s fully open-source objective. AMESH does not add a non-commercial clause, hosted-service prohibition or other field-of-use restriction.

## Why this is the practical open-source boundary

AGPL requires a modified version that supports remote network interaction to offer its corresponding source to users interacting with it remotely, subject to the licence terms.

Open-source software must allow use in any field of endeavour, including commercial use. A licence that prohibits competitors, hosted services or commercial use would be source-available rather than open source.

AMESH therefore uses strong copyleft instead of pretending that “open source but competitors cannot use it” is a coherent licence category.

## What AGPL does not do

AGPL does not:

- prohibit commercial use;
- prohibit a company from operating a hosted AMESH service;
- guarantee that every separate service, workflow or plugin is automatically a derivative work;
- replace trademark, privacy, export-control or service-contract rules;
- make AMESH affiliated with Kestra;
- provide certification or warranty.

Specific derivative-work and network-deployment questions require legal advice for the actual architecture and distribution model.

## Distribution requirements

Official AMESH distributions must include:

- the AGPL-3.0-only licence text;
- appropriate copyright and modification notices;
- corresponding source for official binaries and images;
- reproducible build instructions where practical;
- source-offer functionality in the network UI for modified deployments as required by the licence;
- dependency licence inventory and SBOM;
- no incompatible dependency or additional restriction.

## Plugins, SDKs and independent works

Plugin and SDK licences require an explicit decision before publication. The default project policy is:

- AMESH server and first-party UI code: `AGPL-3.0-only`;
- generated API schemas and compatibility data: licence stated per artifact;
- client SDKs: may use a more permissive licence when needed for adoption, subject to an ADR;
- independent workflow definitions and user data: not relicensed merely by being processed by AMESH;
- separately communicating plugins: licence reviewed according to coupling, distribution and legal advice.

No plugin may impose a term that prevents compliant distribution of the combined official release.

## Trademark and official builds

Software copyright permission and trademark permission are separate. Forks may exercise AGPL rights but must not imply that they are official AMESH releases or use protected marks in a confusing way.

A future trademark policy may define use of the AMESH name, compatibility marks and “certified plugin” claims without reducing software freedoms.

## Governance

Licence changes require:

- explicit product-owner or steering-group approval;
- named human approval under Q-021;
- dependency and contributor-rights analysis;
- an ADR;
- updated source headers, notices, build artifacts and release documentation.

AI agents may prepare a licence-change analysis but may not approve or publish the change autonomously.
