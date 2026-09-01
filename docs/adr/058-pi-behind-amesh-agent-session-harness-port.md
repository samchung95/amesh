# ADR-058: Pi behind an AMESH-owned agent-session harness port

- **Status:** Accepted; context-projection ownership superseded by ADR-070
- **Date:** 2026-08-26
- **Epic:** EPIC-819 / board card `c121`

## Context

AMESH already owns durable `agent.session` checkpoints, provider and tool invocation journals,
capability pins, approvals, cumulative budgets and final-output validation. Long sessions still need a
replaceable agent-loop implementation with bounded context and provider-cache evidence. Letting a
third-party harness own credentials, invoke tools directly or persist authoritative session state
would create a second execution engine and break the recovery guarantees in ADR-053.

The candidate evaluation used current upstream documentation, release metadata and package artifacts
on 2026-08-26. Scores are local AMESH integration fit from 1 (poor) to 5 (strong), not general product
quality.

| Criterion | Weight | DSH | Pi | Goose |
|---|---:|---:|---:|---:|
| Preserves AMESH model/tool authority | 25% | 3 | 4 | 2 |
| Small embeddable integration seam | 20% | 3 | 4 | 2 |
| Windows and deployable package availability | 15% | 1 | 5 | 1 |
| Provider neutrality and OpenRouter fit | 15% | 3 | 5 | 4 |
| Context-compaction and cache evidence hooks | 15% | 5 | 4 | 4 |
| Maintenance state and license | 10% | 2 | 4 | 5 |
| **Weighted fit** | **100%** | **58/100** | **86/100** | **55/100** |

Evidence behind the decision:

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) has the strongest native
  compaction and event-sourced session concepts, but its 0.1 release-candidate line is a developer
  preview and its Python SDK bundles runtime wheels that do not include Windows.
- [Pi](https://github.com/earendil-works/pi) publishes a small typed
  [`Agent`](https://github.com/earendil-works/pi/blob/v0.84.3/packages/agent/README.md) core, a custom
  model `streamFn`, agent events and first-class OpenRouter/provider usage fields. Version 0.84.3 is
  installable with the repository's Node 22 runtime on Windows, macOS and Linux. The newer
  `AgentHarness` facade is incomplete in that release, so the adapter will use the established direct
  `Agent` API instead.
- [Goose](https://github.com/aaif-goose/goose) is a mature Apache-2.0 application with useful context
  management, but its embeddable Python GDK is alpha and its current wheel is macOS ARM-only. The
  complete Goose agent is a much larger subprocess boundary that would duplicate more AMESH policy
  and session behavior.

## Decision

Select `@earendil-works/pi-agent-core` as the first third-party harness implementation. Integrate it
behind an AMESH-owned, typed `AgentSessionHarness` port in stages.

The port is a one-turn, side-effect-free boundary. AMESH supplies exactly one authorized model call
through an injected model gateway. The harness may return one tool proposal or one final structured
result; it receives no model credential value, MCP client, approval service, repository or checkpoint
writer. The gateway rejects any provider, model, route, budget, continuation or invocation-key change
before provider I/O. AMESH continues to own route order and fallback, model invocation journaling,
action normalization, tool policy and dispatch, checkpoints, limits, evidence and output acceptance.

The initial compatibility adapter was used only to extract and compare the port. Following the
product-owner cutover directive, Pi is now required by the session task factory and explicitly
injected by both production composition roots; there is no built-in runtime fallback. The Pi adapter
runs the direct Pi `Agent` API in an isolated Node worker. Its custom `streamFn` proxies model requests
through the AMESH gateway, and any future Pi tool callback must round-trip through an AMESH-governed
tool request before an effect occurs. Pi session files, provider credentials and native tool
implementations are never authoritative.

Python dependencies and commands remain locked and executed with `uv`. Pi is a TypeScript package, so
its isolated worker uses an exact npm lockfile; it is not represented as a Python dependency.

Before every harness turn, AMESH projects the append-only checkpoint transcript through
`amesh.recent-complete-turns/v2`. The projection keeps the pinned prefix and newest complete
assistant/result groups inside operator-declared message, canonical-byte and estimated-token limits;
it fails closed when that minimum safe context cannot fit. Its model-visible compaction marker is
stable as the transcript grows; a durable per-turn receipt still binds the full transcript and
derived context by SHA-256, identifies retained and omitted source indexes and records remaining
headroom. Persisted `amesh.agent-context/v1` receipts remain readable. This keeps compaction
deterministic, inspectable and independent of Pi.

Provider usage normalization treats prompt caching as provider evidence rather than an AMESH cache.
OpenRouter `prompt_tokens_details.cached_tokens`, `cache_write_tokens` and `cache_discount` are
projected into explicit read tokens, write tokens, hit ratio and signed cost effect. Absence is
recorded as `unavailable`; it is never converted into a false zero or mixed with task-cache and
invocation-replay records.

## Consequences

- Existing workflow YAML and the public `agent.session` result contract do not gain a harness-specific
  field.
- Pi worker startup or protocol failure is an infrastructure failure; AMESH never silently falls back
  to the removed built-in harness.
- Every accepted model response records the harness adapter/version alongside the existing provider
  and invocation evidence.
- A different harness can replace Pi without changing AMESH's workflow, policy, durability or tool
  contracts.
- Pi adds a Node worker and an inter-process protocol that require their own lock, compatibility tests
  and deployment qualification.

## Rejected alternatives

- Replace the AMESH session task and PostgreSQL journal with a harness-native loop or session store:
  this makes recovery and policy depend on a second engine.
- Let Pi call OpenRouter or MCP directly: this bypasses AMESH credentials, invocation journals,
  budgets and ambiguous-outcome handling.
- Select DSH now: its current runtime cannot be exercised on the supported Windows development path
  and its public API is still release-candidate.
- Select Goose now: the practical embeddable seam is not cross-platform and the full agent boundary is
  substantially larger than the required loop library.
