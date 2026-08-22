# Realtime events and outbound webhooks

AMESH projects committed state, log, output, artifact and audit evidence into a tenant-isolated
PostgreSQL cursor. Clients can page that projection or keep a bounded server-sent event connection;
outbound destinations are handled by the optional indexer role and never participate in the core
orchestration transaction.

## Page and stream events

Use the page endpoint when a consumer controls its own polling interval:

```powershell
$headers = @{ Authorization = 'Bearer development-token' }
$page = Invoke-RestMethod `
  -Uri 'http://localhost:8000/api/v1/realtime/events?namespace=demo&limit=100' `
  -Headers $headers
$page.nextCursor
```

Use `GET /api/v1/realtime/stream` for SSE. It accepts the same filters:

- `namespace`, `flowId` and `executionId`;
- repeatable `eventType` and `severity` values;
- `includeAudit` when the caller also has `audit:view`;
- opaque `cursor`, or the standard `Last-Event-ID` request header on reconnect.

Every data frame contains a cursor in its SSE `id`, an exact `event` type and a versioned JSON body:

```text
id: eyJvZmZzZXQiOjQyLCJ2ZXJzaW9uIjoxfQ
event: execution.executionsucceeded
data: {"cursor":42,"eventId":"...","severity":"INFO","payload":{...}}
```

The server emits heartbeat comments while idle. If retention removed the requested cursor, it first
emits an explicit `gap` event containing `oldestAvailable` and `resumeCursor`, then continues from
that boundary. A cursor ahead of the durable projection is rejected.

`bufferEvents` bounds each database batch and is returned as `X-Amesh-Buffer-Limit`. The generator
yields each bounded batch directly to the network, so transport backpressure stops more reads rather
than accumulating an unbounded per-client queue. `maxEvents` and `streamSeconds` apply an explicit
disconnect boundary; reconnect with the last received SSE `id`.

Tenant RLS always applies. Namespace and execution filters are authorized before streaming. Audit
events are excluded when the caller lacks audit permission. Sensitive field names, values declared
sensitive by the flow contract and explicitly sensitive outputs are replaced with `[REDACTED]`
before either SSE or webhook delivery.

## Create and test a subscription

Create a destination with objective filters and a bounded retry count:

```powershell
$body = @{
  name = 'ops.execution-events'
  url = 'https://hooks.example.com/amesh'
  filters = @{
    namespace = 'demo'
    eventTypes = @('execution.executionsucceeded', 'execution.executionfailed')
    severities = @('INFO', 'WARNING', 'ERROR')
    includeAudit = $false
  }
  maxAttempts = 8
} | ConvertTo-Json -Depth 5

$created = Invoke-RestMethod -Method Post `
  -Uri 'http://localhost:8000/api/v1/webhook-subscriptions' `
  -Headers $headers -ContentType 'application/json' -Body $body
$created.signingSecret
```

The signing secret is returned only when the subscription is created or rotated. Store it in the
consumer's secret manager. AMESH derives versioned secrets from the operator-owned
`WEBHOOK_SIGNING_KEY`; it does not persist plaintext destination secrets.

Queue a test delivery, then inspect its attempt history:

```powershell
$id = $created.subscription.id
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/api/v1/webhook-subscriptions/$id/test" -Headers $headers
Invoke-RestMethod `
  -Uri "http://localhost:8000/api/v1/webhook-subscriptions/$id/deliveries" -Headers $headers
```

Rotate with optimistic concurrency:

```powershell
$version = $created.subscription.resourceVersion
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/api/v1/webhook-subscriptions/$id/rotate-secret?expectedVersion=$version" `
  -Headers $headers
```

Replay one selected history item with
`POST /api/v1/webhook-deliveries/{deliveryId}/replay`. A replay receives a new delivery ID and links
to the original. Ordinary retries retain one stable delivery ID so consumers can reject duplicates.

## Verify signatures and replay protection

Each POST includes:

- `X-Amesh-Delivery-Id`: stable across automatic retries;
- `X-Amesh-Event-Id`: immutable source event identity;
- `X-Amesh-Timestamp`: Unix seconds used in the signature;
- `X-Amesh-Signature`: `v1=` plus HMAC-SHA256.

The signed bytes are:

```text
<timestamp>.<delivery-id>.<exact-request-body>
```

The consumer should compute the HMAC over the exact body, compare signatures in constant time,
reject timestamps outside its accepted clock-skew window and store accepted delivery IDs for that
window. A repeated ID is a replay and must not apply the side effect twice.

## Failure isolation and retry history

The indexer claims due rows with `FOR UPDATE SKIP LOCKED`, sends outside the claim transaction and
records every response code, duration and stable error category. Failures retry exponentially up to
five minutes and stop at `maxAttempts`. An indexer crash leaves a 60-second lease; another replica
can reclaim the same delivery ID afterward.

Subscription projection and delivery are additive work owned by `SERVICE_ROLE=indexer`. If the
indexer is stopped, DNS fails, a destination times out or the remote service returns an error,
executions and other orchestration roles continue using their existing PostgreSQL truth. Pending and
retry history remains durable until the indexer or destination recovers.
