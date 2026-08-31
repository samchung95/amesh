import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const agent = {
  resourceId: 'agent-1', tenantId: 'default', namespace: 'demo', kind: 'AGENT', key: 'researcher', revision: 1, digest: 'sha256:agent', createdBy: 'operator', createdAt: '2026-08-29T00:00:00Z',
  spec: { kind: 'AGENT', key: 'researcher', namespace: 'demo', title: 'Researcher', description: 'Safe research agent', modelPolicy: { key: 'safe', revision: 1 } },
}

const summary = (state: string) => ({ sessionId: '00000000-0000-7000-8000-000000000801', tenantId: 'default', namespace: 'demo', agentRef: 'demo/researcher@1', modelProfile: 'demo/safe@1', executionId: '00000000-0000-7000-8000-000000000901', taskRunId: '00000000-0000-7000-8000-000000000902', attempt: 1, capabilityPinId: '00000000-0000-7000-8000-000000000903', envelopeDigest: 'sha256:envelope', state, phase: state === 'SUCCEEDED' ? 'COMPLETE' : 'MODEL', version: 2, executionEpoch: 1, counters: { turns: 2, loopIterations: 1, toolCalls: 1, totalTokens: 256, costUsd: '0.001', repairAttempts: 0 }, harness: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' }, finalResult: state === 'SUCCEEDED' ? { decision: 'ready', evidence: ['source-1'] } : null, result: state === 'SUCCEEDED' ? { decision: 'ready', evidence: ['source-1'] } : null, budgets: { maxTurns: 5, maxToolCalls: 10, maxTotalTokens: 2000, maxCostUsd: '0.05' }, error: null, createdAt: '2026-08-29T00:00:00Z', updatedAt: '2026-08-29T00:01:00Z', completedAt: state === 'SUCCEEDED' ? '2026-08-29T00:01:00Z' : null })

const progressEvent = (index: number, activity: string, status: string, segmentId: string | null) => ({
  schemaVersion: 'amesh.agent-progress-event/v1', serviceSessionId: summary('RUNNING').sessionId, eventId: `00000000-0000-7000-8000-00000000081${index}`, eventIndex: index, cursor: `cursor-${index}`, acceptedAt: `2026-08-29T00:00:0${index}Z`,
  frame: { schemaVersion: 'amesh.agent-progress/v1', attemptSessionId: summary('RUNNING').sessionId, attempt: 1, turn: 1, activity, status, activityId: `activity:${index}`, segmentId, sourceId: 'pi:test', sourceSequence: index, occurredAt: `2026-08-29T00:00:0${index}Z`, detail: { kind: 'STATUS', code: `${activity.toLowerCase()}.${status.toLowerCase()}`, label: `${activity} ${status}` } },
})

const progressEvents = [
  progressEvent(1, 'THINKING', 'STARTED', '00000000-0000-7000-8000-000000000821'),
  progressEvent(2, 'TOOL', 'COMPLETED', null),
  progressEvent(3, 'THINKING', 'STARTED', '00000000-0000-7000-8000-000000000823'),
  progressEvent(4, 'TERMINAL', 'COMPLETED', null),
]

const uploadedImage = {
  schemaVersion: 'amesh.image-ref/v1',
  artifact: { reference: `nsfile:///session-inputs/chart.png?version=1&sha256=${'a'.repeat(64)}`, contentAddress: `sha256:${'a'.repeat(64)}`, tenantId: 'default', namespace: 'demo', path: 'session-inputs/chart.png', version: 1, mediaType: 'image/png', sizeBytes: 68, checksumSha256: 'a'.repeat(64), provenance: {}, retention: {} },
  display: { filename: 'chart.png', altText: 'Test chart', widthPixels: 1, heightPixels: 1 },
}

const safeImageMetadata = {
  schemaVersion: 'amesh.image-display/v1', reference: `sha256:${'a'.repeat(64)}`, mediaType: 'image/png', sizeBytes: 68, checksumSha256: 'a'.repeat(64), widthPixels: 1, heightPixels: 1,
}

test('runs the session control-room journey and captures an accessible result view', async ({ page }, testInfo) => {
  let created = false
  let state = 'RUNNING'
  let detailReads = 0
  let progressStreamReads = 0
  let createBody: Record<string, unknown> | null = null
  await page.route('**/api/v1/auth/providers*', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/ui/session*', (route) => route.fulfill({ json: { principalId: 'operator', principalType: 'USER', display: 'Operator', tenantId: 'default', namespace: null, capabilities: { 'dashboards.view': true, 'flows.view': true, 'agents.view': true, 'executions.view': true, 'executions.manage': true, 'executions.execute': true, 'agentSessions.view': true, 'agentSessions.create': true, 'agentSessions.list': true, 'agentSessions.manage': true, 'announcements.view': false }, telemetryEnabled: false, serverVersion: '0.2.0' } }))
  await page.route('**/api/v1/flows*', (route) => route.fulfill({ json: [{ namespace: 'demo', flow_id: 'sample', resource_id: 'flow-1', revision: 1, semantic_hash: 'hash', etag: 'etag' }] }))
  await page.route('**/api/v1/announcements*', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/namespaces/demo/images/**', (route) => route.fulfill({ json: uploadedImage }))
  await page.route('**/api/v1/namespaces/demo/agent/resources*', (route) => route.fulfill({ json: [agent] }))
  await page.route('**/api/v1/agent-sessions', async (route) => {
    if (route.request().method() === 'POST') {
      created = true
      createBody = route.request().postDataJSON() as Record<string, unknown>
      return route.fulfill({ status: 201, json: { sessionId: summary('RUNNING').sessionId, executionId: summary('RUNNING').executionId, taskRunId: summary('RUNNING').taskRunId, attempt: 1, executionState: 'RUNNING', session: summary('RUNNING') } })
    }
    return route.fulfill({ json: created ? [{ sessionId: summary(state).sessionId, attemptSessionId: summary(state).sessionId, session: summary(state) }] : [] })
  })
  await page.route('**/api/v1/agent-sessions/**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/harnesses')) return route.fulfill({ json: { pi: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' } } })
    if (url.pathname.endsWith('/progress/stream')) {
      progressStreamReads += 1
      const items = progressStreamReads === 1
        ? [{ type: 'heartbeat', sessionId: summary('RUNNING').sessionId, cursor: 'cursor-1' }, progressEvents[1]]
        : [progressEvents[1], progressEvents[2], progressEvents[3]]
      return route.fulfill({ body: `${items.map((item) => JSON.stringify(item)).join('\n')}\n`, contentType: 'application/x-ndjson' })
    }
    if (url.pathname.endsWith('/progress')) {
      const events = state === 'SUCCEEDED' ? progressEvents : [progressEvents[0]]
      return route.fulfill({ json: { sessionId: summary(state).sessionId, events, nextCursor: events.at(-1)?.cursor ?? null } })
    }
    if (url.pathname.endsWith('/result')) return route.fulfill({ json: { sessionId: summary('SUCCEEDED').sessionId, state: 'SUCCEEDED', result: summary('SUCCEEDED').finalResult, error: null } })
    if (url.pathname.endsWith('/events')) return route.fulfill({ json: { session: summary(state), events: [{ eventId: 'event-1', sessionId: summary(state).sessionId, eventIndex: 1, eventKey: 'session.started', eventType: 'session.started', payload: { inputImages: [safeImageMetadata] }, occurredAt: '2026-08-29T00:00:01Z' }], nextEventIndex: null } })
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
  await page.getByLabel('Attach an image (optional)').setInputFiles({ name: 'chart.png', mimeType: 'image/png', buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=', 'base64') })
  await page.getByRole('button', { name: 'Start session' }).click()
  await expect.poll(() => createBody).toMatchObject({ input: { image: uploadedImage } })
  await expect(page.getByText('1 active')).toBeVisible()
  const progress = page.getByRole('list', { name: 'Chronological agent progress' })
  await expect(progress.locator('li')).toHaveCount(4, { timeout: 10_000 })
  await expect(progress.locator('li').nth(0)).toContainText('THINKING')
  await expect(progress.locator('li').nth(1)).toContainText('TOOL')
  await expect(progress.locator('li').nth(2)).toContainText('THINKING')
  await expect(page.getByRole('heading', { name: 'Attached images' })).toBeVisible()
  await expect(page.getByText('Test chart')).toBeVisible()
  expect(await page.locator('body').innerText()).not.toContain('data:image/png')
  await expect(page.getByRole('heading', { name: 'Recorded events' })).toBeVisible()
  await expect(page.getByText('SUCCEEDED')).toBeVisible({ timeout: 10_000 })
  await expect(progress.locator('li')).toHaveCount(4)
  await expect(page.getByRole('heading', { name: 'Result or error' })).toBeVisible()
  await expect(page.getByText(/"decision": "ready"/)).toBeVisible()
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Attached images' })).toBeVisible()
  await expect(page.getByText(new RegExp(`sha256:${'a'.repeat(14)}`))).toBeVisible()
  await page.emulateMedia({ reducedMotion: 'reduce' })
  const reducedDurationMs = await page.locator('.agent-progress-item').first().evaluate((element) => {
    const value = getComputedStyle(element).animationDuration
    return Number.parseFloat(value) * (value.endsWith('ms') ? 1 : 1000)
  })
  expect(reducedDurationMs).toBeLessThanOrEqual(0.01)
  await expect(page.getByRole('alert')).toHaveCount(0)
  const violations = await new AxeBuilder({ page }).analyze()
  expect(violations.violations).toEqual([])
  const directory = resolve(process.cwd(), '..', 'docs', 'product', 'ui-audit', 'screenshots', 'agent-sessions')
  await mkdir(directory, { recursive: true })
  await page.screenshot({ path: resolve(directory, `${testInfo.project.name}-control-room.png`), fullPage: true, animations: 'disabled' })
})
