# Client-neutral external orchestration

Use the versioned profile at `GET /api/v1/orchestration/profile` to discover the
stable AMESH operations for an external workflow client. The profile is metadata-only;
clients retain their domain validation, calendars and workflow semantics.

## Request identity

Send `X-Amesh-Tenant` with a credential that is authorized for the requested namespace.
Send one stable `X-Correlation-ID` for an end-to-end client attempt. For launch and
other state-changing requests, also send `Idempotency-Key`; retries must reuse both
values. AMESH returns the correlation value in `X-Correlation-ID` and resolves a
repeated launch key to the same logical execution.

Apply and control operations use `If-Match` or the operation's `expectedVersion` and
`expectedEpoch` fields. A stale optimistic-concurrency value returns a conflict or
precondition problem; do not retry it without reading the current resource first.

## Operations

The profile maps these client-neutral operations to the existing `/api/v1` contract:

- Validate a YAML or JSON workflow with `POST /flows/validate`.
- Apply an immutable revision with `PUT /flows`, optionally using `If-Match`.
- Read an exact revision with `GET /flows/{namespace}/{flow_id}/document?revision=N`.
- Launch idempotently with `POST /executions`; use `Prefer: respond-async` for `202`. Include
  `flowRevision: N` in the JSON body when the client must run one exact immutable revision;
  omitting it selects the active revision, and an unknown revision is rejected before launch.
- Inspect with `GET /executions/{execution_id}`.
- Preview a control with `POST /executions/{execution_id}/interventions/preview`, then
  apply it with `POST /executions/{execution_id}/interventions`. The preview is
  side-effect free; applying requires the previewed execution epoch and version.

All resource-bearing operations authenticate and authorize server-side and scope reads
and writes to the authenticated tenant. Responses use `application/problem+json` with
stable `code` values and an `X-Amesh-Error-Category` response header. Treat
`409`/`412` as `conflict`, `408`/`429`/`5xx` transport
outcomes as `retryable`, and ambiguous external outcomes as `ambiguous`: inspect the
logical execution before deciding whether to retry.

## Realtime and webhooks

Connect to `GET /realtime/stream` with `Last-Event-ID` set to the last acknowledged SSE
`id` (or use the equivalent opaque `cursor` query parameter). Advance the cursor only
after durable handling. A `gap` event includes `oldestAvailable` and `resumeCursor`;
the client must record the gap rather than silently treating it as a complete stream.

Outbound webhook delivery is signed with `X-Amesh-Timestamp`,
`X-Amesh-Delivery-Id` and `X-Amesh-Signature`. Delivery is at least once, so consumers
deduplicate by delivery id before applying effects. Verify the signature over the exact
request bytes and enforce a timestamp window; signing-secret rotation changes the
signing version without changing delivery identity.

## Runnable uv example

After installing the generated Python client archive, run the neutral launch/inspect
example from a clean checkout:

```console
AMESH_ENDPOINT=http://localhost:8000 \
AMESH_TOKEN=... \
AMESH_NAMESPACE=examples.getting_started \
AMESH_FLOW=hello_world \
uv run python examples/sdk/neutral-client.py
```

The harness verifies every live profile operation against the live OpenAPI document,
launches twice with one correlation and idempotency key, asserts one logical execution,
and then polls it to completion through the generated Python client. Set
`AMESH_CORRELATION_ID` and `AMESH_IDEMPOTENCY_KEY` to repeat the same probe across an
API restart. It does not contain client-specific domain adapters.
