# EPIC-814 — Unified MCP and plugin ToolProvider contract

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `plugins`
- **Primary persona:** Plugin developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let MCP servers and installable plugins supply tools through one pinned policy, schema, invocation and recovery boundary without embedding domain integrations in core.

## In scope

- [x] A neutral ToolProvider port defines identity, input/output schemas, impact, secrets, egress, filesystem and invocation semantics.
- [x] The existing MCP adapter implements the port without changing its external semantics.
- [x] Plugin tool entry points execute through isolated RPC, policy checks and the durable invocation journal.
- [x] Agent definitions pin provider kind, key, revision, tool name and schema digest; existing MCP-only references migrate compatibly.
- [x] Discovery, allowlisting, high-impact approval, schema validation, timeout, cancellation, restart reuse and ambiguous-outcome rules are identical across providers.
- [x] A neutral example plugin tool and certification suite prove extensibility without adding a domain connector to core.

## Implementation completion evidence

- 2026-08-26 — EPIC-814 is complete. MCP connections and isolated installable plugins now implement one pinned `ToolProvider` discovery, JSON-schema, policy, redaction, timeout, cancellation and restart-recovery contract. Migration 0062 supplies a tenant-RLS durable invocation journal with stable ownership and explicit ambiguous external-outcome handling; certification docs and a neutral example plugin show how clients add domain tools without changing core. The shared conformance suite passed both actual adapters locally and against PostgreSQL, including discovery identity, schema denial, secret redaction, accepted-result reuse and restart ambiguity; Ruff and strict mypy passed. Evidence: [`TESTLOG.md`](../../docs/reviews/TESTLOG.md), [`tool-provider.md`](../../docs/reference/tool-provider.md), [`implement-tool-provider.md`](../../docs/how-to/implement-tool-provider.md), [`neutral-tool-provider.py`](../../examples/plugin-sdk/neutral-tool-provider.py), and [`test_tool_provider_conformance.py`](../../tests/conformance/test_tool_provider_conformance.py).

## Explicit non-goals

- Shipping news, market-data, broker or other use-case-specific tools
- Allowing in-process plugin code to bypass isolation

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-301
- EPIC-312
- EPIC-807
- EPIC-808

## Architecture impact

- Primary bounded area: `plugins`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- ToolProvider contract and MCP compatibility tests.
- Plugin isolated-RPC discovery and invocation integration tests.
- Policy, schema, timeout, cancellation, restart and ambiguous-outcome conformance tests.
- Neutral example plugin certification test.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] MCP and plugin tools pass one provider-neutral certification suite.
- [x] Existing MCP agent definitions have a documented compatibility path.
- [x] Plugin authors can implement and test a tool without modifying AMESH core.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- A plugin tool path can accidentally bypass the policy and invocation journal used by MCP.
- Provider-specific identity can make exact agent capability pins non-portable.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
