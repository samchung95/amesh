# ADR-050: Reuse HTTPX, jsonschema and the official MCP SDK for agent primitives

- **Status:** Accepted
- **Date:** 2026-08-25
- **Epic:** EPIC-312

## Context

EPIC-312 needs bounded HTTP model calls, Draft 2020-12 output validation and authenticated MCP client
and server behavior. AMESH already locks HTTPX, jsonschema and MCP v2 for those jobs.

## Decision

Keep provider behavior behind AMESH model-adapter contracts, but reuse HTTPX for OpenAI-compatible
transport, `Draft202012Validator` for schemas and the official MCP v2 client/server for protocol and
authentication behavior. Declare the MCP SDK's existing `httpx2` transport as a direct dependency so
AMESH owns the API it imports; this adds no newly installed package to the lock. AMESH owns connection
policy, budget enforcement, redaction, invocation journaling and orchestration integration because
those are product semantics.

## Consequences

- Protocol and schema edge cases remain with maintained libraries already present in `uv.lock`.
- Provider and MCP implementations remain replaceable behind AMESH contracts.
- A dependency decision is revisited only if an existing library cannot implement a required public
  contract or its maintenance/security posture becomes unacceptable.
