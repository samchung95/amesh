# ADR-070: Harness-owned context projection under AMESH budgets

- **Status:** Accepted
- **Date:** 2026-08-31
- **Epic:** EPIC-832 / board card `c163`

## Context

AMESH currently projects and compacts an `agent.session` transcript before invoking the replaceable
harness. The harness therefore receives an already-selected model call and cannot apply its native
context-management behavior. This makes the harness replaceable in name while keeping an important
session responsibility in the workflow task. It also leaves standalone session launches unable to
set the same context policy as workflow nodes and does not reserve model-output headroom explicitly.

Workflow ordering is a separate boundary. Successful dependency outputs are available to explicit
expressions, but dependency order does not insert those values or another node's private transcript
into a model prompt. Changing global expression visibility would be a breaking workflow change and
is unnecessary to preserve an explicit A-to-B-to-C final-result contract.

Pi 0.84.3 already exposes `transformContext` immediately before its LLM conversion step. Reusing
that locked seam is smaller and more portable than adding another context library or maintaining the
projection as a session-task concern.

## Decision

Move successful model-context projection behind the versioned `AgentSessionHarness` port. AMESH
passes the append-only canonical messages and a calculated `AgentHarnessContextBudget` containing
the configured model context window, maximum model input, reserved completion, compaction trigger,
message and canonical-byte limits. Legacy `maxEstimatedTokens` remains the operator's input ceiling;
an optional context window and completion reserve calculate a stricter effective ceiling.

Pi applies its locked `transformContext` hook to retain pinned instructions and the newest complete
assistant/result groups. It sends the selected messages and a content-addressed, privacy-safe receipt
with its model request. The receipt identifies the harness algorithm and version, source and selected
digests, retained and omitted indexes, measured limits and headroom; it contains no prompt text,
reasoning or tool arguments. Existing AMESH v1/v2 receipts remain readable.

The AMESH model gateway remains authoritative. It allows the harness to replace only the model-visible
messages and their derived modalities. Before provider I/O it verifies the immutable provider,
model, output schema, parameters, token/cost/time limits, credential scopes, continuation and
invocation identity, then rejects context exceeding any calculated message, byte or estimated-token
limit. It records the accepted receipt and verifies that the harness returns the exact gateway model
result. A harness still receives no credentials, repository, checkpoint writer or direct tool
authority.

The session task retains and checkpoints the complete transcript. It no longer selects the
successful turn's message subset. Workflow and canonical standalone session requests expose the same
`contextPolicy`; omitted new fields preserve existing effective defaults. A harness failure,
malformed receipt, minimum safe context that cannot fit, or gateway overflow fails the turn before
unapproved external work.

Workflow nodes remain isolated sessions. An agent's pinned input schema validates only the task's
explicitly rendered input, and its pinned output schema validates the final result. Downstream nodes
receive that result only through an explicit input expression or typed `agent.handoff`. Transitive
outputs remain expression-visible for compatibility, but no upstream transcript or output is
implicitly appended to downstream model context.

DeepSeek qualification uses the same provider, model-policy, image, progress, tool, budget, cache and
structured-output contracts as Luna. `deepseek/deepseek-v4-flash-vision-exp` is data in a model route,
not a new core provider type. AMESH validation and bounded repair remain authoritative when an
OpenRouter route cannot enforce JSON Schema itself. Exact model capability profiles also pin the
completion-limit wire dialect: callers always configure the semantic `maxCompletionTokens` limit,
the negotiated profile resolves its default plus any immutable provider-route override to either
`max_completion_tokens` or `max_tokens`, and the OpenRouter adapter preserves that field while
applying provider compatibility filtering. This prevents `require_parameters=true` from excluding a
compatible pinned route solely because AMESH renamed its supported completion-limit parameter.

## Consequences

- Harnesses can use provider-appropriate compaction while AMESH still enforces hard admission,
  credentials, tools, budgets, durability and evidence.
- Context configuration reserves completion capacity instead of treating the provider window as an
  all-input allowance.
- Pi worker protocol and conformance fixtures must version the context budget, selected messages and
  receipt boundary.
- Provider-independent deterministic fixtures remain the default gate; paid DeepSeek qualification
  stays explicit and secret-gated.
- Global workflow expression semantics and existing explicit transitive references do not change.

## Rejected alternatives

- Keep projection in the session task: this prevents third-party harnesses from owning the context
  strategy the port is meant to replace.
- Give the harness direct provider or tool credentials: this bypasses AMESH policy, invocation and
  evidence authorities.
- Pass only a single context-window number: this can consume all capacity with input and leave no
  completion headroom.
- Restrict every workflow task to direct-dependency outputs: this is a broad breaking change and is
  not required to prevent implicit agent-context propagation.
