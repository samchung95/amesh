import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { webcrypto } from 'node:crypto';

const require = createRequire(import.meta.url);
const { ExecutionClient, verifyWebhook } = require('../../sdks/api/typescript/dist/index.js');
globalThis.crypto ??= webcrypto;

const detail = {
  execution: {
    execution_id: '0198cafe-0000-7000-8000-000000000001',
    tenant_id: 'default',
    state: 'SUCCESS',
    epoch: 1,
    version: 2,
    namespace: 'examples.mvp',
    flow_id: 'hello_world',
    created_at: '2026-08-23T00:00:00Z',
    updated_at: '2026-08-23T00:00:01Z',
  },
  taskRuns: [],
};
const requests = [];
const responses = [
  new Response('{}', { status: 503, headers: { 'retry-after': '0' } }),
  new Response(JSON.stringify(detail), { status: 200 }),
];
const client = new ExecutionClient({
  endpoint: 'https://amesh.test',
  token: 'test-token',
  fetchApi: async (url, init) => {
    requests.push({ url, init });
    return responses.shift();
  },
  retryPolicy: { maxAttempts: 2, initialDelayMs: 0 },
  sleep: async () => {},
});
const launched = await client.launch(
  'examples.mvp',
  'hello_world',
  { name: 'SDK' },
  'local',
  'stable-key',
);
assert.equal(launched.execution.state, 'SUCCESS');
assert.equal(requests.length, 2);
assert.equal(requests[0].init.headers['Idempotency-Key'], 'stable-key');
assert.equal(requests[0].init.headers.Authorization, 'Bearer test-token');
assert.equal(requests[0].init.body, requests[1].init.body);

const timestamp = 1_800_000_000;
const deliveryId = '0198cafe-0000-7000-8000-000000000002';
const body = new TextEncoder().encode('{"event":"execution.completed"}');
const key = await crypto.subtle.importKey(
  'raw',
  new TextEncoder().encode('webhook-secret'),
  { name: 'HMAC', hash: 'SHA-256' },
  false,
  ['sign'],
);
const prefix = new TextEncoder().encode(`${timestamp}.${deliveryId}.`);
const signed = new Uint8Array(prefix.length + body.length);
signed.set(prefix);
signed.set(body, prefix.length);
const digest = new Uint8Array(await crypto.subtle.sign('HMAC', key, signed));
const signature = `v1=${Array.from(digest, (value) => value.toString(16).padStart(2, '0')).join('')}`;
assert.equal(
  await verifyWebhook('webhook-secret', timestamp, deliveryId, body, signature, timestamp + 30),
  true,
);
assert.equal(
  await verifyWebhook('webhook-secret', timestamp, deliveryId, body, signature, timestamp + 301),
  false,
);

if (process.env.AMESH_SDK_LIVE_ENDPOINT) {
  const liveClient = new ExecutionClient({
    endpoint: process.env.AMESH_SDK_LIVE_ENDPOINT,
    token: process.env.AMESH_SDK_LIVE_TOKEN,
    tenant: process.env.AMESH_SDK_LIVE_TENANT ?? 'default',
  });
  const liveLaunch = await liveClient.launch(
    process.env.AMESH_SDK_LIVE_NAMESPACE ?? 'examples.getting_started',
    process.env.AMESH_SDK_LIVE_FLOW ?? 'hello_world',
    { name: 'TypeScript SDK' },
  );
  const liveId = liveLaunch.execution.executionId;
  const completed = await liveClient.waitForTerminal(liveId, 90000, 250);
  assert.equal(completed.execution.state, 'SUCCESS');
  assert.equal((await liveClient.get(liveId)).execution.executionId, liveId);
  assert.ok(Array.isArray(await liveClient.logs(liveId)));
  assert.ok(Array.isArray(await liveClient.artifacts(liveId)));
}
