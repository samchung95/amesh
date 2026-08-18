# Strict clean-room implementation policy

## Purpose

AMESH may reproduce observable outcomes and public interfaces of a workflow product, but it must not copy protected expression, branding or implementation. This policy reduces—not eliminates—legal risk and is not legal advice.

## Permitted specification inputs

- public product documentation, schemas and API references;
- behavior observed through lawfully accessed public releases and public hosted interfaces;
- public standards and third-party service documentation;
- public bug reports and release notes as leads for independently designed tests;
- independently created fixtures, measurements and behavioral descriptions;
- public licence and trademark information required to describe compatibility honestly.

## Prohibited implementation inputs

- Kestra source code, source diffs or translated source logic;
- copied UI layouts, icons, illustrations, branding or distinctive prose;
- proprietary enterprise code, leaked material or credentials;
- decompiled, circumvented or access-controlled components;
- issue comments, prompts or retrieval indexes containing pasted upstream implementation;
- AI-generated code produced from prohibited upstream source context;
- tests copied verbatim from upstream source repositories.

Implementation agents must not receive prohibited material in prompts, workspaces, vector stores, tool outputs or hidden context.

## Researcher/implementer separation

For compatibility-sensitive areas:

1. A **reference researcher** records a neutral observable specification, source provenance and black-box fixture.
2. An **implementation agent** receives the specification and fixture, not upstream implementation material.
3. An independent **reviewer** checks provenance, similarity, licences and compatibility evidence.
4. A **verifier** runs differential tests against the pinned public target where lawful and practical.

The same AI model family may perform different roles only in separate contexts with no prohibited source transfer. Separate models or providers are preferable for high-risk areas.

## Required records

Each compatibility requirement records:

- target product version and interface surface;
- public documentation or observed behavior used;
- neutral expected behavior and edge cases;
- independent fixture and result checksum;
- known tolerances or explicit gaps;
- researcher, implementer, reviewer and verifier identities;
- model/tool provenance for AI-authored work.

Pull requests include a clean-room declaration and affected requirement IDs.

## Automated gates

The repository includes lexical and provenance checks. Release engineering must add code-similarity, dependency-licence, SBOM, secret and signed-provenance scans. Automated checks cannot replace independent review.

## Names and claims

Use AMESH branding and an independent visual system. “Kestra” may identify the comparison and migration target, but no affiliation, endorsement or official status may be implied. A compatibility claim must name the tested target version and surface.
