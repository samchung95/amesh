# ADR-077: Execution-scoped MCP grant exchange

Status: accepted for issue #83; deployment remains owner-gated.

## Context

One MCP connection can serve independently authorized consumer sessions. Model arguments and MCP
transport session IDs cannot establish consumer authority. Existing connection credentials remain
the compatibility path; AMESH must preserve tool pins, policy and durable invocation receipts.

## Decision

Add an optional `executionGrant` policy to an immutable MCP connection revision. Its
`exchangeEndpoint` shares the MCP endpoint's origin (HTTPS in production). Canonical session creation accepts
`toolGrants`, a bounded connection-key to opaque consumer grant-reference mapping. These references
are identifiers, never bearer credentials. Admission rejects references outside the pinned tools;
the accepted mapping lives in execution metadata, is copied unchanged to follow-up turns, and is
omitted from public execution projections. No grant update is allowed through model arguments or
follow-up input.

Before a governed call, AMESH builds a versioned context from its execution metadata: tenant,
namespace, authenticated launching actor, logical session, execution, task run, stable logical
invocation ID, attempt ID/ordinal, exact connection revision/digest and selected tool. It sends that
context and grant reference to the configured exchange endpoint using the connection credential.
The gateway authenticates the AMESH instance and validates the grant's consumer scope, actor,
audience, tools, expiry and revocation. A newly issued grant can be atomically bound to the first
logical AMESH session; subsequent exchanges must reject a different session. AURA owns issuance,
this binding transaction, browser authorization and durable command receipts.

The exchange returns a short-lived bearer token, exact MCP audience, expiry and digest of the
requested context. AMESH checks those fields and uses the token only for that MCP invocation.
The gateway binds the token to the context and validates it when serving `tools/call`. Live
discovery still uses the connection credential and verifies pinned schemas. Tokens and grant
references are absent from model input, public progress and ordinary invocation diagnostics;
echoed tokens are redacted before journaling. Exchange failures never fall back to the connection
credential for a scoped invocation. Retries/recovery preserve the stored grant and invocation
identity; existing ambiguous-outcome handling prevents silently repeating external effects.

## Alternatives and consequences

Connection-per-scope credentials remain sufficient for a single-user MVP. Self-issued AMESH JWTs
would add key distribution and revocation machinery; opaque online exchange reuses the existing
HTTP client and consumer authority without a new dependency, secret store or database migration.
This is a versioned application grant-exchange contract, not a claim to implement the complete
OAuth authorization/discovery protocol. Its transport follows MCP's destination-bound access-token
rule ([MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization));
no AMESH API credential is forwarded. OAuth token exchange is a future interoperable alternative
([RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html)) if consumer deployments require it.
An unavailable gateway fails closed. Revocation is checked on every new exchange and by the gateway
on invocation; token correlation does not create exactly-once browser effects.
