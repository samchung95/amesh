# ADR-061: Agent harness conformance and portability

- **Status:** Accepted
- **Date:** 2026-08-26
- **Epic:** EPIC-824

## Context

AMESH now runs Pi behind an AMESH-owned session port, but a passing adapter test alone does not prove
that another harness can preserve model, tool, credential, state, recovery and evidence boundaries.
The release gate needs one provider-free, versioned test kit, exact dependency provenance and a probe
against the production image.

## Decision

Define a harness-neutral conformance manifest and machine-readable compatibility report. The report is
bound to the manifest digest, source version, adapter and worker protocol versions, runtime versions,
exact lockfile package integrity/licenses and each fixture result. CI runs it twice in one environment,
compares canonical output, and uploads the result. A production-image probe invokes the real Pi
adapter with a deterministic in-process gateway; it never contacts an LLM provider.

Adapters remain explicitly registered behind `AgentSessionHarness`. A missing, unknown or protocol-
violating adapter fails closed. Pi remains the production default, and active sessions cannot switch
harnesses. Future adapters must run the same kit without changing the public `agent.session`
contract.

## Consequences

- Provider-free CI can qualify authority, malformed-action, budget, timeout, recovery, compaction,
  cache-evidence and large-frame behavior without exposing credentials or spending credits.
- Dependency and license drift becomes visible in the compatibility report.
- A paid OpenRouter/Luna smoke remains opt-in and local/secret-gated.
- DSH and Goose remain evaluation targets, not production dependencies, until they pass the same kit.
