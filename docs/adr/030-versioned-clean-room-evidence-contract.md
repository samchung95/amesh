# ADR-030: Versioned clean-room evidence contract

Status: accepted

## Context

AMESH pins compatibility to Kestra 1.3.30, but the existing epic-level CSV and prose source register do not prove requirement-level provenance, explicit gaps or target-rebase coherence. Release checks also need a similarity and file-license gate without exposing reference source to implementation agents.

## Decision

Generate `requirements/compatibility-inventory.json` from the canonical URS, epic labels, target baseline, source registry and existing evidence. Validate that every functional compatibility requirement has one pinned target, known source identifiers, disposition and evidence list. Keep raw reference source outside the repository and compare normalized token shingles through one-way SHA-256 fingerprints in an isolated release job.

Use REUSE 6.2.0 for SPDX file-license validation. Extend the existing AMESH clean-room script for repository-specific provenance, role-separation, target-coherence and similarity policy. Do not introduce runtime dependencies.

## Alternatives

- ScanCode Toolkit 32.5.0 is maintained and comprehensive, but its broader dependency, vulnerability and SBOM surface belongs to EPIC-001 and EPIC-612.
- JPlag 6.3.0 is maintained, but its Python parser targets Python 3.6 and its strongest comparison mode assumes same-language submissions; it does not fit Java-to-Python/TypeScript clean-room review.
- A lexical denylist alone cannot demonstrate requirement provenance or detect longer copied sequences.

## Consequences

Local validation stays deterministic and lightweight. Release similarity jobs may access the pinned public reference only in a separate reviewer context and emit findings rather than reference content. Hash overlap is a review gate, not a legal conclusion; reviewers still decide whether a flagged sequence is generic, required by a public interface or prohibited expression.
