# ADR-074: Isolate subscription-backed model engines behind the provider port

- **Status:** Accepted
- **Date:** 2026-09-02
- **Epic:** EPIC-836

## Context

AMESH currently invokes model providers through an OpenAI-compatible HTTP adapter and authorizes
each route with an HTTP endpoint plus a secret reference. A ChatGPT subscription exposed through
Codex App Server and a GitHub Copilot subscription exposed through Copilot CLI are not API keys or
HTTP provider endpoints. Both runtimes own an interactive login, a local account store and a
programmatic process protocol. Pretending either runtime is an HTTP endpoint or passing its local
credential files as workflow secrets would leak engine-specific behavior into workflows and could
share one operator identity across tenants.

The official Codex App Server interface is JSON-RPC over JSONL. It provides initialization,
account login/read/logout, model discovery, thread/turn execution, streaming notifications,
interruption and usage or rate-limit signals. The official Copilot CLI supports browser or device
OAuth, isolated `COPILOT_HOME` state and a JSONL programmatic invocation mode. No additional SDK is
needed for the first implementation: AMESH already has bounded asynchronous subprocess and JSONL
supervision patterns, and the documented process contracts are the narrowest dependencies.

For the optional Docker deployment, use the official npm distributions instead of reimplementing
either protocol or running mutable installer scripts when a container starts. Keep exact direct and
transitive package resolutions in a dedicated lock file, build them into an opt-in runtime target,
and keep self-updates disabled while the image serves AMESH work.

GitHub Copilot CLI normally persists its OAuth credential in an operating-system keyring. A
headless local container has no such keyring, so its official login flow can finish provider
approval but still fail before saving the credential. Plaintext fallback therefore remains
disabled by default. The checked-in local model-engine overlay explicitly opts in because the
credential is confined to the binding-specific home on the protected persistent volume; other
deployments must make that decision themselves.

## Decision

Extend the provider-neutral model route with one optional `engineRef`. Direct HTTP routes retain
their existing endpoint and credential reference byte-for-byte. An engine route supplies
`adapter` plus `engineRef` and omits endpoint and credential fields. The two forms are mutually
exclusive. Agent and task capability envelopes gain `engineScopes`; the exact engine reference
must be delegated before process I/O. Engine-specific login fields, home paths and commands never
enter a workflow, agent profile, session checkpoint or transfer bundle.

Keep the existing `ModelProvider` invocation boundary and add a private typed access value that is
either a secret credential or an engine reference. The provider registry resolves the adapter
selected by the immutable route; it must not silently substitute the HTTP adapter for an unknown
engine. Direct HTTP remains the default and compatibility path. Codex App Server and Copilot CLI
adapters translate their documented process events into the existing OpenAI-shaped internal model
response and safe chronological progress contracts, while AMESH remains authoritative for durable
invocation identity, retries, context selection, budgets, cancellation, tool approval and final
JSON-schema validation.

Engine account state lives below a configured server-owned root in a path derived from the tenant,
namespace, adapter and engine reference. Clients cannot supply a filesystem path. Each subprocess
receives only its derived `CODEX_HOME` or `COPILOT_HOME`, a minimal environment and the pinned
command. Native engine tools and MCP servers are disabled; an engine may only produce content or
an AMESH-validated tool proposal. Image artifacts are resolved through the existing tenant-aware
artifact boundary into an invocation-scoped temporary file and removed after the process exits.

Expose a provider-neutral account-manager port and authorized namespace API for engine catalog,
status, login start and logout. Login start may return only a safe browser URL and, for device
authorization, a user code plus expiry. The runtime owns refresh tokens; AMESH never returns,
logs, exports or copies them. Login, logout and status authorization decisions are audited, while
responses report readiness, account/plan labels and quota or rate-limit signals only when the
runtime supplies them. The API must represent `ACTION_REQUIRED` rather than pretending that a
human browser/device approval was automated.

Subscription quota is not API dollar cost. Engine responses normalize reported token usage where
available and mark monetary cost unavailable or quota-backed unless the runtime explicitly reports
a billable amount. Capabilities are declared per pinned adapter revision. A runtime that cannot
honor an exact requested feature, including embedding, native message-bound opaque continuation or
priced-cost enforcement, fails capability negotiation before starting external work. Functional
multi-turn execution remains available by sending the harness-selected transcript; AMESH does not
claim native continuation when an engine cannot bind it to exact retained messages.

Provider-bounded sessions additionally require an exact model physical-limit profile. The initial
Codex and Copilot revisions publish `gpt-5.6-luna` with a 1,050,000-token context window and
128,000-token output limit, matching the pinned base-model profile. Other engine model identifiers
remain unavailable to provider-bounded sessions until a revision publishes their exact limits.

## Consequences

- Existing HTTP workflows, secrets, route digests and egress checks retain their current behavior.
- Operators can add or replace documented process adapters without changing session or workflow
  result contracts.
- Subscription login requires one unavoidable user approval when the provider demands it; AMESH
  can initiate and monitor that flow but cannot bypass the account owner.
- Per-binding homes must be placed on encrypted or equivalently protected persistent storage when
  durable login across restarts is required. Runtime-native keyring behavior remains preferred.
- Copilot plaintext token storage is a default-off deployment choice. The local overlay enables it
  only inside the protected model-engine volume so the headless official CLI can persist login.
- Codex and Copilot protocol/version drift is isolated to their adapters and caught by provider-free
  conformance fixtures plus opt-in live qualification.
- An engine that lacks priced cost, embeddings or exact opaque continuation is rejected only when a
  route requests that capability; AMESH does not fabricate parity.

## Rejected alternatives

- Treat subscription credentials as API keys: subscriptions do not grant API-key semantics and
  doing so would rely on undocumented tokens.
- Encode a fake local HTTP endpoint and secret reference: this defeats route validation and exposes
  process implementation details to clients.
- Share the operator's default Codex or Copilot home: this crosses tenant and user identity
  boundaries and makes logout or migration ambiguous.
- Add an unofficial wrapper SDK: the official process contracts already provide the required
  boundary and an extra dependency would not remove process supervision or authentication work.
- Enable engine-native tools: those tools bypass AMESH capability envelopes, durable journals and
  approval policy.
