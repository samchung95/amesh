# ADR-047: Versioned declarative admission policy

- **Status:** Accepted
- **Date:** 2026-08-23
- **Scope:** EPIC-802

## Context

Workflow policy must be enforced during authoring and execution without requiring a separately
operated policy service for the local and compact profiles. Decisions must be reproducible,
tenant-scoped, explainable and safe to retain as audit evidence. The existing plugin supply-chain
policy is intentionally narrower and remains independent.

## Decision

AMESH uses the documented `amesh.policy/v1` declarative format. Policies are immutable revisions
identified by a stable key, revision number and SHA-256 digest. Effective instance, tenant and
namespace revisions are evaluated in that order at `VALIDATE`, `SAVE`, `PROMOTE`, `LAUNCH` and
`DISPATCH` boundaries.

Each rule selects one or more stages, contains an all-of condition set and produces `ALLOW`, `DENY`,
`WARN`, `MUTATE_DEFAULT` or `REQUIRE_APPROVAL`. Denial takes precedence. Required approvals use the
stable `<policy-key>/<rule-id>` key. Default mutations apply only to absent values and are limited to
flow, runner, image, network and resource context; they cannot set secret or credential paths.

The evaluator accepts typed actor, tenant, namespace, flow, plugin, runner, image, secret-scope,
network and resource context. Secret values are never policy input: sensitive workflow inputs are
redacted and the secret context contains scopes only. Stored decisions exclude the internal mutated
input and retain bounded evidence: outcome, reasons, condition evidence, mutations, approvals,
policy pins, input hash and evaluation time.

Each policy has a 1–5,000 ms limit. An enforcing policy that exhausts its limit denies; an advisory
policy emits a warning and allows evaluation to continue. Every evaluation and policy revision is
written to the tenant audit ledger. Launch decisions are linked from execution trigger metadata and
dispatch decisions from task control evidence.

## Consequences

- Local, compact and distributed roles share one deterministic evaluator and PostgreSQL revision
  store without another runtime dependency.
- Policy behavior is reviewable as JSON/YAML-compatible data and can be tested against fixtures.
- Replaying a decision can identify the exact active policy digests, although live lifecycle stages
  deliberately evaluate the revisions effective at that boundary.
- Extending the language requires a new schema or engine version; silently changing v1 semantics is
  not permitted.
