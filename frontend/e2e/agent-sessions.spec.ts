import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const agent = {
  resourceId: 'agent-1', tenantId: 'default', namespace: 'demo', kind: 'AGENT', key: 'researcher', revision: 1, digest: 'sha256:agent', createdBy: 'operator', createdAt: '2026-08-29T00:00:00Z',
  spec: { kind: 'AGENT', key: 'researcher', namespace: 'demo', title: 'Researcher', description: 'Safe research agent', modelPolicy: { key: 'safe', revision: 1 } },
}

const summary = (state: string) => ({ sessionId: '00000000-0000-7000-8000-000000000801', tenantId: 'default', namespace: 'demo', agentRef: 'demo/researcher@1', modelProfile: 'demo/safe@1', executionId: '00000000-0000-7000-8000-000000000901', taskRunId: '00000000-0000-7000-8000-000000000902', attempt: 1, capabilityPinId: '00000000-0000-7000-8000-000000000903', envelopeDigest: 'sha256:envelope', state, phase: state === 'SUCCEEDED' ? 'COMPLETE' : 'MODEL', version: 2, executionEpoch: 1, counters: { turns: 2, loopIterations: 1, toolCalls: 1, totalTokens: 256, costUsd: '0.001', repairAttempts: 0 }, harness: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' }, finalResult: state === 'SUCCEEDED' ? { decision: 'ready', evidence: ['source-1'] } : null, result: state === 'SUCCEEDED' ? { decision: 'ready', evidence: ['source-1'] } : null, budgets: { maxTurns: 5, maxToolCalls: 10, maxTotalTokens: 2000, maxCostUsd: '0.05' }, error: null, createdAt: '2026-08-29T00:00:00Z', updatedAt: '2026-08-29T00:01:00Z', completedAt: state === 'SUCCEEDED' ? '2026-08-29T00:01:00Z' : null })

test('runs the session control-room journey and captures an accessible result view', async ({ page }, testInfo) => {
  let created = false
  let state = 'RUNNING'
  let detailReads = 0
  await page.route('**/api/v1/auth/providers*', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/ui/session*', (route) => route.fulfill({ json: { principalId: 'operator', principalType: 'USER', display: 'Operator', tenantId: 'default', namespace: null, capabilities: { 'dashboards.view': true, 'flows.view': true, 'agents.view': true, 'executions.view': true, 'executions.manage': true, 'executions.execute': true, 'announcements.view': false }, telemetryEnabled: false, serverVersion: '0.2.0' } }))
  await page.route('**/api/v1/flows*', (route) => route.fulfill({ json: [{ namespace: 'demo', flow_id: 'sample', resource_id: 'flow-1', revision: 1, semantic_hash: 'hash', etag: 'etag' }] }))
  await page.route('**/api/v1/announcements*', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/namespaces/demo/agent/resources*', (route) => route.fulfill({ json: [agent] }))
  await page.route('**/api/v1/agent-sessions', async (route) => {
    if (route.request().method() === 'POST') {
      created = true
      return route.fulfill({ status: 201, json: { sessionId: summary('RUNNING').sessionId, executionId: summary('RUNNING').executionId, taskRunId: summary('RUNNING').taskRunId, attempt: 1, executionState: 'RUNNING', session: summary('RUNNING') } })
    }
    return route.fulfill({ json: created ? [{ sessionId: summary(state).sessionId, attemptSessionId: summary(state).sessionId, session: summary(state) }] : [] })
  })
  await page.route('**/api/v1/agent-sessions/**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/harnesses')) return route.fulfill({ json: { pi: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' } } })
    if (url.pathname.endsWith('/result')) return route.fulfill({ json: { sessionId: summary('SUCCEEDED').sessionId, state: 'SUCCEEDED', result: summary('SUCCEEDED').finalResult, error: null } })
    if (url.pathname.endsWith('/events')) return route.fulfill({ json: { session: summary(state), events: [{ eventId: 'event-1', sessionId: summary(state).sessionId, eventIndex: 1, eventKey: 'session.started', eventType: 'session.started', payload: {}, occurredAt: '2026-08-29T00:00:01Z' }], nextEventIndex: null } })
    if (url.pathname.endsWith('/cancel')) {
      state = 'SUCCEEDED'
      return route.fulfill({ json: { sessionId: summary(state).sessionId, executionId: summary(state).executionId, taskRunId: summary(state).taskRunId, attempt: 1, executionState: 'SUCCESS', session: summary(state) } })
    }
    detailReads += 1
    if (detailReads > 1) state = 'SUCCEEDED'
    return route.fulfill({ json: { session: summary(state), events: [], nextEventIndex: null } })
  })

  await page.goto('/')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('test-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await expect(page.getByRole('heading', { name: 'Mission Control' })).toBeVisible()
  await page.getByRole('button', { name: /Tenant default/ }).click()
  await page.getByLabel('Namespace filter').selectOption('demo')
  await page.getByRole('button', { name: 'Apply context' }).click()
  await page.getByRole('link', { name: 'Agent sessions' }).click()
  await expect(page.getByRole('heading', { name: 'Agent sessions', exact: true })).toBeVisible()
  await expect(page.getByLabel('Harness adapter')).toHaveValue('pi')
  await expect(page.getByText('No agent sessions yet')).toBeVisible()
  await page.getByLabel('Agent revision').selectOption('demo/researcher@1')
  await page.getByRole('button', { name: 'Start session' }).click()
  await expect(page.getByText('1 active')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Recorded events' })).toBeVisible()
  await expect(page.getByText('SUCCEEDED')).toBeVisible({ timeout: 10_000 })
  await expect(page.getByRole('heading', { name: 'Result or error' })).toBeVisible()
  await expect(page.getByText(/"decision": "ready"/)).toBeVisible()
  await expect(page.getByRole('alert')).toHaveCount(0)
  const violations = await new AxeBuilder({ page }).analyze()
  expect(violations.violations).toEqual([])
  const directory = resolve(process.cwd(), '..', 'docs', 'product', 'ui-audit', 'screenshots', 'agent-sessions')
  await mkdir(directory, { recursive: true })
  await page.screenshot({ path: resolve(directory, `${testInfo.project.name}-control-room.png`), fullPage: true, animations: 'disabled' })
})
