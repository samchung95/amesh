# ADR-076: Separate session finalization and cache-efficient context

Status: Accepted design; implementation in progress under GitHub [#74](https://github.com/samchung95/amesh/issues/74).

## Context

The Core Discovery pilot rejected four specialist sessions before their first tool call.
The current interaction protocol puts tool selection and final business output into one
structured wrapper, including JSON-string-encoded tool arguments. Progress availability
selects streaming, although the configured OpenRouter response-healing plugin supports
only non-streaming requests. Rejection records do not identify the original JSON defect.
These facts justify replacing the interaction protocol, not the durable execution engine.

The successful news session used 424,202 total tokens across seven turns and retained
395,610 bytes of context. This is evidence of repeated context volume, not proof that
provider caching failed. The existing EPIC-830 analyzer and context receipts remain the
measurement foundation.

## Decision and boundaries

```text
Durable session controller
  research -> authorized native tool calls -> durable evidence
       | required-evidence gate and checkpointed phase transition
       v
  finalization -> business-schema result -> validation/release -> committed result
       | rejected output
       +-> bounded finalization retry using the same evidence (no research tools)

Progress observes both phases; adapter transport policy is independent.
Model context is a bounded projection of evidence, not the authoritative evidence store.
```

- Preserve AMESH's journals, required-tool ledger, permissions, accounting, cancellation,
  tenant boundaries and message-bound protected continuation. The harness projects context;
  it does not gain authority to execute tools or commit session outcomes.
- Introduce a versioned, opt-in interaction protocol. Existing checkpoints keep their pinned
  protocol; never reinterpret an in-flight legacy checkpoint as the new protocol.
- Research uses native tool calls and explicit completion intent. Finalization begins only
  after the required-evidence gate and a durable checkpoint referencing immutable evidence.
  It uses the business schema without research tools. Invalid output cannot commit success.
- Keep provider-specific transport constraints at the adapter boundary. The first slice
  makes the existing progress-stream interface fall back to a unary HTTP request for
  healing-enabled structured OpenRouter calls. It returns the same terminal response event;
  generic accounting, continuation protection and session lifecycle handling remain in place.
  The later explicit transport policy must preserve this compatibility rule.
- Rejection diagnostics retain bounded parse metadata. Assistant excerpts, if enabled, need
  explicit retention/redaction controls; private reasoning is never diagnostic output.
- Keep stable instructions, tool definitions and projection markers before changing data.
  Store complete evidence durably and project only task-relevant content with references.
  VibeStonks owns domain-specific selection; AMESH owns the generic projection contract.
  Do not rewrite retained assistant messages under existing continuation bindings.

## Cache acceptance and tradeoffs

Extend the existing analyzer, not a second report or a response/result cache. Separate
request-positive-read rate from token-weighted reuse. Report uncached input, cache writes,
missing evidence, rejected billed calls, latency and cost per accepted result, grouped by
cold/warm and research/finalization cohorts. Missing evidence is not a miss.

Frozen before/after fixtures must preserve required evidence and stable reusable prefixes
while reducing repeated model-visible input. A controlled provider comparison uses identical
inputs, model, route and settings; success requires lower uncached input per accepted result
without reducing acceptance quality or increasing total cost. Report actual provider cache
rates rather than promise a universal percentage. Never pad prompts to improve a ratio.
Any affinity hint is tenant/session scoped and mapped only by a supporting adapter.

Finalization may require an additional model call and a different schema prefix. Measure that
cost rather than assume separation improves every cache metric. Unary transport gives up
token-level progress on those calls, but preserves task/session lifecycle progress.

## Delivery and verification

Agent Hotel c219 is the primary tracker. GitHub milestones are response handling [#75](https://github.com/samchung95/amesh/issues/75),
phase separation [#76](https://github.com/samchung95/amesh/issues/76), cache/context [#77](https://github.com/samchung95/amesh/issues/77),
and qualification [#78](https://github.com/samchung95/amesh/issues/78).
Tests must exercise actual HTTP transport choice, malformed output and repair, phase-transition
recovery, no duplicate completed tools, continuation bindings, legacy checkpoints and fail-closed
consumer acceptance. The draft PR is not merge-ready until these and local release gates pass.
No deployment, broker actions, provider swap, whole-engine rewrite or unrelated debt is included.

The owner clarified that improvement over baseline alone is insufficient. Closure requires
measured optimization as far as practicable for the pinned scout workload, with both Codex and
Claude Fable 5.1 finding no remaining worthwhile in-scope optimization. Any actionable remaining
finding needs a fix or explicit owner acceptance. Independently, fresh candidate collection must
complete all eight Core Discovery sessions and produce a durable accepted slate through Vibe's
normal consumer path. AMESH success alone is not this gate; no buy signal or broker execution is
part of qualification. These live gates remain pending after implementation-only verification.

The opt-in field is `interactionProtocol: NATIVE_V2` (default `STRUCTURED_V1`). The research
completion call is `amesh_finish_research`; its accepted transition journals `research.completed`,
pins the evidence digest, and prevents further research calls in that attempt. The default
projection removes only proven duplicate JSON text from MCP `content`, retaining all other
evidence and the complete journal result. Existing context budgets still bound model input.
No provider-affinity hint is added without support and measured benefit on the pinned route.

Provider references: [response healing](https://openrouter.ai/docs/guides/features/plugins/response-healing)
and [prompt caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching), checked 2026-09-06.

## Stable native envelope — 2026-09-06

The owner approved the measured #77 follow-up. An explicit `NATIVE_V3` protocol preserves
the same projected tool definitions and business response schema throughout research and
finalization. This is preferable to changing V2 in flight or adding an independent flag with
invalid legacy combinations. Existing V1/V2 requests and checkpoints retain their behavior.

The harness call carries an optional, authority-checked tool choice. V3 research maps to a
tool-call primitive with the business schema also present; finalization maps to a structured
primitive with identical but disabled tool definitions (`toolChoice: none`). Both capabilities
must negotiate before I/O. Original business-schema validation and the required-plan ledger
remain authoritative; unexpected final tool calls fail validation and never dispatch. Research
continues to require exactly one call at the controller. No private continuation is rewritten.

Both phases reserve context overhead for tools AND schema. V3 omits the unsupported
`parallel_tool_calls` provider option in both phases; the controller enforces serial dispatch.
Multiple research calls are rejected before dispatch and use the existing bounded repair
path, including consumed tokens/cost. They do not become accepted continuation messages.
Provider routing and response-healing transport remain adapter-owned. Unsupported combined
capabilities fail explicitly; opt-in does not silently substitute a model/provider or fall back.
Checkpoint protocol identity rejects reinterpretation on recovery. The wire tool definitions
are retained for caching, not as finalization authority; this qualifies the earlier "without
research tools" statement without changing the no-dispatch boundary.

Validation: V2/V3 phase/recovery/repair regressions; original final-schema and no-tool gates;
stable request prefixes and both-phase budget accounting; five paired real-harness runs using
identical frozen research/model/provider settings and protected continuation; fresh Vibe E2E;
Fable review of code and measured results. No guaranteed cache rate or padded/stale production
research. Leave the optimization gate open if the measurements do not justify closure.
