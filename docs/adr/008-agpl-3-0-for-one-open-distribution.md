# ADR-008: AGPL-3.0-only for one open distribution

- **Status:** Accepted and confirmed
- **Decision questions:** Q-004, Q-022
- **Date:** 2026-08-15

## Context

AMESH is network server software. The product owner wants the complete production capability set to remain open when modified versions are offered over a network and asked for the most restrictive licence compatible with the stated fully open-source objective.

Open-source licensing cannot prohibit commercial use or particular fields of endeavour. Moving to a hosted-service or non-commercial restriction would make AMESH source-available rather than open source.

## Decision

License the AMESH server and first-party UI under **GNU Affero General Public License version 3 only**, expressed as `AGPL-3.0-only`.

Ship identity, governance, distributed operation, agent capabilities and administration in the same public distribution without licence-key gates. Do not add a field-of-use, non-commercial, competitor or hosted-service prohibition.

Treat trademark and official-build policy separately from software copyright permissions.

## Consequences

- Modified network deployments are subject to AGPL source-offer obligations under the licence terms.
- Commercial use, support and hosted offerings remain permitted.
- Some organisations may decline adoption or contribution because of copyleft policy.
- A clear source link and legal notice are required in the interactive web interface where applicable.
- Dependencies, SDKs and separately distributed plugins require licence-boundary review.
- Licence or governance changes require named human approval under Q-021.
- Final public launch should receive qualified legal review.

## Rejected alternatives

- **AGPL-3.0-or-later:** rejected because the product owner selected the more fixed `only` grant.
- **SSPL or field-of-use restrictions:** rejected because they conflict with the fully open-source objective.
- **Permissive licensing:** rejected because it does not provide the requested network copyleft.

## Traceability

See `LICENSE`, `NOTICE`, `docs/product/license-policy.md`, `EPIC-000`, `EPIC-804` and `docs/product/decision-register.md`.
