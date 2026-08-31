# Integrate an application

All resource-bearing requests require a bearer token and an explicit tenant. Use a stable
`Idempotency-Key` when creating work so a client retry converges on the same accepted operation.

## Pick a client surface

| Surface | Best fit | Reference |
| --- | --- | --- |
| REST + OpenAPI | Any language or generated client | [API contracts](../api/README.md) |
| CLI | Operators, scripts and local automation | [CLI guide](../cli/README.md) |
| Generated SDKs | Typed Python, TypeScript, Java and Go clients | [Public SDKs](../api/sdks.md) |
| OpenAI-compatible subset | Existing chat clients targeting a pinned AMESH agent | [Session-service compatibility route](../how-to/use-agent-session-service.md#use-an-openai-compatible-client) |
| External orchestration profile | Client-neutral launches, correlation, events and webhooks | [External orchestration](../api/external-orchestration.md) |

The interactive API explorer is served at `/docs` by a running AMESH instance. The checked-in
[OpenAPI document](../api/openapi.json) is generated and verified locally.

## Common protocol rules

- Send `Authorization: Bearer <token>` and `X-Amesh-Tenant: <tenant>`.
- Keep credentials in the client application's secret store; do not embed them in workflows.
- Use exact flow or agent revisions when repeatability matters.
- Follow `Location` after an asynchronous `202` response.
- Treat `application/problem+json` as the canonical error shape and use its stable code and
  retryability instead of parsing prose.
- Follow opaque page or event cursors exactly; do not construct them.
- Reconnect SSE, NDJSON or agent-progress streams from the last acknowledged cursor.

See [Authentication](../operations/authentication.md), [API conventions](../api/README.md#v1-conventions)
and [Realtime delivery](../api/realtime.md) for the complete contracts.

## Agent-session integration

Use the canonical session API when the client needs AMESH-owned continuation, progress and controls.
Use the OpenAI-compatible route when compatibility with an existing request-scoped chat client is more
important. The browser or mobile application remains responsible for its privileged local actions;
AMESH sees only the high-level, registered tool contract and its governed result.

The [agent session service API](../api/agent-session-service.md) documents start, later turns,
idempotency, polling, chronological progress, results and redacted errors.
