import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const id = '00000000-0000-7000-8000-000000000827'
const executionId = '00000000-0000-7000-8000-000000000828'
const item = {
  sessionId: id, attemptSessionId: id, tenantId: 'default', namespace: 'platform', agentRef: 'platform/researcher@2', ownerId: 'owner-1', executionId, taskRunId: '00000000-0000-7000-8000-000000000829', attempt: 1,
  state: 'RUNNING', phase: 'TOOL', version: 4, executionVersion: 7, executionEpoch: 1, capabilityPinId: id, envelopeDigest: 'sha256:envelope',
  harness: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' },
  counters: { turns: 4, loopIterations: 2, toolCalls: 3, totalTokens: 2048, costUsd: '0.0125', repairAttempts: 0 },
  modelInvocationCount: 4, toolInvocationCount: 3, failedInvocationCount: 0, dependencyKeys: ['catalog'], dependencyHealth: 'HEALTHY',
  createdAt: '2026-08-30T01:00:00Z', updatedAt: '2026-08-30T01:05:00Z', completedAt: null,
}
const page = {
  items: [item], nextCursor: null, readAt: '2026-08-30T01:06:00Z',
  aggregates: { matchedExecutions: 1, active: 1, terminal: 0, byState: { RUNNING: 1 }, totalTurns: 4, totalToolCalls: 3, totalTokens: 2048, totalCostUsd: '0.0125', modelInvocations: 4, toolInvocations: 3, failedInvocations: 0, degradedDependencies: 0 },
}
const policy = {
  policyId: '00000000-0000-7000-8000-000000000830', tenantId: 'default', namespace: 'platform', applicationId: null, revision: 4,
  spec: { admissionEnabled: true, maxConcurrency: 3, maxTotalTokens: 50000, maxCostUsd: '4.50', maxDurationSeconds: 900, retentionSeconds: 86400, allowedProviderIds: ['provider/openai'], allowedHarnessIds: ['pi-agent-core'], allowedToolIds: ['search'] },
  digest: 'sha256:policy', createdBy: 'operator', createdAt: '2026-08-30T01:00:00Z',
}
const sessionBundle = {
  schemaVersion: 'amesh.session-transfer/v1', mode: 'CLEAN_CHECKPOINT', sourceTenantId: 'source-tenant',
  session: { sessionId: 'source-session', credentialRef: 'provider-main' }, checksumSha256: 'sha256:session',
}
const progressEvents = [
  { schemaVersion: 'amesh.agent-progress-event/v1', serviceSessionId: id, eventId: '00000000-0000-7000-8000-000000000841', eventIndex: 1, cursor: 'orchestrator-cursor-1', acceptedAt: page.readAt, frame: { schemaVersion: 'amesh.agent-progress/v1', attemptSessionId: id, attempt: 1, turn: 1, activity: 'THINKING', status: 'STARTED', activityId: 'thinking:1', segmentId: '00000000-0000-7000-8000-000000000851', sourceId: 'pi:test', sourceSequence: 1, occurredAt: page.readAt, detail: { kind: 'STATUS', code: 'thinking.started', label: 'Thinking started' } } },
  { schemaVersion: 'amesh.agent-progress-event/v1', serviceSessionId: id, eventId: '00000000-0000-7000-8000-000000000842', eventIndex: 2, cursor: 'orchestrator-cursor-2', acceptedAt: page.readAt, frame: { schemaVersion: 'amesh.agent-progress/v1', attemptSessionId: id, attempt: 1, turn: 1, activity: 'TOOL', status: 'COMPLETED', activityId: 'tool:1', segmentId: null, sourceId: 'pi:test', sourceSequence: 2, occurredAt: page.readAt, detail: { kind: 'STATUS', code: 'tool.completed', label: 'Tool work completed' } } },
  { schemaVersion: 'amesh.agent-progress-event/v1', serviceSessionId: id, eventId: '00000000-0000-7000-8000-000000000843', eventIndex: 3, cursor: 'orchestrator-cursor-3', acceptedAt: page.readAt, frame: { schemaVersion: 'amesh.agent-progress/v1', attemptSessionId: id, attempt: 1, turn: 1, activity: 'THINKING', status: 'STARTED', activityId: 'thinking:2', segmentId: '00000000-0000-7000-8000-000000000853', sourceId: 'pi:test', sourceSequence: 3, occurredAt: page.readAt, detail: { kind: 'STATUS', code: 'thinking.resumed', label: 'Thinking resumed' } } },
  { schemaVersion: 'amesh.agent-progress-event/v1', serviceSessionId: id, eventId: '00000000-0000-7000-8000-000000000844', eventIndex: 4, cursor: 'orchestrator-cursor-4', acceptedAt: page.readAt, frame: { schemaVersion: 'amesh.agent-progress/v1', attemptSessionId: id, attempt: 1, turn: 1, activity: 'TERMINAL', status: 'COMPLETED', activityId: 'terminal:1', segmentId: null, sourceId: 'pi:test', sourceSequence: 4, occurredAt: page.readAt, detail: { kind: 'STATUS', code: 'session.succeeded', label: 'Agent session succeeded' } } },
]
const safeImageMetadata = { schemaVersion: 'amesh.image-display/v1', reference: `sha256:${'b'.repeat(64)}`, mediaType: 'image/png', sizeBytes: 2048, checksumSha256: 'b'.repeat(64), widthPixels: 640, heightPixels: 480 }

test('opens the session orchestrator, traces a row, and guards bulk lifecycle actions', async ({ page: browserPage }, testInfo) => {
  let bulkRequestBody: Record<string, unknown> | null = null
  await browserPage.route('**/api/v1/auth/providers*', (route) => route.fulfill({ json: [] }))
  await browserPage.route('**/api/v1/ui/session*', (route) => route.fulfill({ json: { principalId: 'operator', principalType: 'USER', display: 'Operator', tenantId: 'default', namespace: null, capabilities: { 'dashboards.view': true, 'flows.view': true, 'executions.view': true, 'agentSessionAdministration.view': true, 'agentSessionAdministration.instanceView': true, 'agentSessionMigration.view': true, 'agentSessionMigration.manage': true, 'agentSessions.manage': true, 'agentSessionPolicies.view': true, 'agentSessionPolicies.manage': true, 'announcements.view': false }, telemetryEnabled: false, serverVersion: '0.2.0' } }))
  await browserPage.route('**/api/v1/flows*', (route) => route.fulfill({ json: [] }))
  await browserPage.route('**/api/v1/announcements*', (route) => route.fulfill({ json: [] }))
  await browserPage.route('**/api/v1/admin/agent-sessions/aggregate', (route) => route.fulfill({ json: { tenants: [{ tenantId: id, tenantSlug: 'default', matchedExecutions: 1, active: 1, terminal: 0, byState: { RUNNING: 1 } }], matchedExecutions: 1, active: 1, terminal: 0, readAt: page.readAt } }))
  await browserPage.route('**/api/v1/admin/agent-session-policies/effective*', (route) => route.fulfill({ json: [policy] }))
  await browserPage.route('**/api/v1/admin/agent-session-policies*', (route) => route.fulfill({ json: [policy] }))
  await browserPage.route(`**/api/v1/admin/agent-session-transfers/sessions/${id}/export`, (route) => route.fulfill({ json: { ...sessionBundle, session: { ...sessionBundle.session, sessionId: id } } }))
  await browserPage.route('**/api/v1/admin/agent-session-transfers/sessions/plan', (route) => route.fulfill({ json: { schemaVersion: 'amesh.session-transfer/v1', eligible: true, mode: 'CLEAN_CHECKPOINT', sourceTenantId: 'source-tenant', targetTenantId: 'default', bundleDigest: 'sha256:session', flowCompatible: true, capabilityPinCompatible: true, harnessCompatible: true, credentialRebindingDiagnostics: ['provider-main → provider-main'], artifactDiagnostics: ['No artifact remapping required'], issues: [] } }))
  await browserPage.route('**/api/v1/admin/agent-session-transfers/sessions/import', (route) => route.fulfill({ json: { importId: 'import-1', bundleDigest: 'sha256:session', mode: 'CLEAN_CHECKPOINT', targetTenantId: 'default', sessionId: id, alreadyPresent: false, idMapping: {}, credentialRebindingDiagnostics: [] } }))
  await browserPage.route('**/api/v1/admin/agent-sessions/actions', (route) => { bulkRequestBody = route.request().postDataJSON() as Record<string, unknown>; return route.fulfill({ json: { action: 'cancel', total: 1, applied: 1, rejected: 0, results: [{ sessionId: id, status: 'applied' }] } }) })
  await browserPage.route('**/api/v1/admin/agent-sessions*', (route) => route.fulfill({ json: page }))
  await browserPage.route(`**/api/v1/agent-sessions/${id}/progress*`, (route) => route.fulfill({ json: { sessionId: id, events: progressEvents, nextCursor: 'orchestrator-cursor-4' } }))
  await browserPage.route(`**/api/v1/agent-sessions/${id}/events*`, (route) => route.fulfill({ json: { session: { ...item, finalResult: null, error: null }, events: [{ eventId: 'event-1', sessionId: id, eventIndex: 1, eventKey: 'session.started', eventType: 'session.started', payload: { inputImages: [safeImageMetadata] }, occurredAt: page.readAt }], nextEventIndex: null } }))
  await browserPage.route(`**/api/v1/agent-sessions/${id}`, (route) => route.fulfill({ json: { session: { ...item, finalResult: null, error: null }, events: [], nextEventIndex: null } }))

  await browserPage.goto('/')
  await browserPage.getByRole('button', { name: 'API token' }).click()
  await browserPage.getByLabel('API token').fill('test-token')
  await browserPage.getByRole('button', { name: 'Open control room' }).click()
  await browserPage.getByRole('link', { name: 'Session orchestrator' }).click()
  await expect(browserPage.getByRole('heading', { name: 'Fleet administration' })).toBeVisible()
  await expect(browserPage.getByRole('cell', { name: 'owner-1' })).toBeVisible()
  await expect(browserPage.getByRole('cell', { name: /pi-agent-core/ })).toBeVisible()
  await expect(browserPage.getByRole('heading', { name: 'Session policy administration' })).toBeVisible()
  await browserPage
    .getByRole('region', { name: 'Resolved policy chain' })
    .getByRole('combobox', { name: 'Namespace' })
    .selectOption('platform')
  await expect(browserPage.getByText(/Namespace · platform · r4/)).toBeVisible()
  await browserPage.getByRole('button', { name: /00000000…000827/ }).click()
  await expect(browserPage.getByRole('heading', { name: /00000000…000827/ })).toBeVisible()
  await expect(browserPage.getByText('session.started')).toBeVisible()
  const liveTimeline = browserPage.getByRole('list', { name: 'Chronological agent progress' })
  await expect(liveTimeline.locator('li')).toHaveCount(4)
  await expect(liveTimeline.locator('li').nth(0)).toContainText('THINKING')
  await expect(liveTimeline.locator('li').nth(1)).toContainText('TOOL')
  await expect(liveTimeline.locator('li').nth(2)).toContainText('THINKING')
  await expect(browserPage.getByRole('heading', { name: 'Attached images' })).toBeVisible()
  await expect(browserPage.getByText(/image\/png · 2 KB/)).toBeVisible()
  await browserPage.getByRole('checkbox', { name: /Select session/ }).check()
  await browserPage.getByRole('button', { name: 'Review action' }).click()
  await expect(browserPage.getByRole('alert')).toContainText('Apply cancel to 1 sessions?')
  await browserPage.getByRole('button', { name: 'Confirm action' }).click()
  await expect.poll(() => bulkRequestBody).toMatchObject({ action: 'cancel', confirmation: 'CANCEL 1 AGENT SESSIONS', items: [{ sessionId: id, expectedVersion: 7, expectedEpoch: 1 }] })
  await expect(browserPage.getByRole('heading', { name: 'Profile and session transfer' })).toBeVisible()
  await browserPage.getByLabel('Choose JSON bundle').setInputFiles({ name: 'session.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(sessionBundle)) })
  await expect(browserPage.getByText('source-tenant')).toBeVisible()
  await browserPage.getByRole('button', { name: 'Preview compatibility' }).click()
  await expect(browserPage.getByText('Compatible')).toBeVisible()
  await browserPage.getByRole('button', { name: 'Import verified bundle' }).click()
  await expect(browserPage.getByText('Session imported')).toBeVisible()
  await browserPage.screenshot({ path: testInfo.outputPath('session-orchestrator-workbench.png'), fullPage: true })
  const durableDirectory = resolve(process.cwd(), '..', 'docs', 'product', 'ui-audit', 'screenshots', 'session-orchestrator')
  await mkdir(durableDirectory, { recursive: true })
  await browserPage.evaluate(() => window.scrollTo(0, 0))
  await expect.poll(() => browserPage.evaluate(() => window.scrollY)).toBe(0)
  await browserPage.waitForTimeout(100)
  await browserPage.screenshot({ path: resolve(durableDirectory, `${testInfo.project.name}-workbench.png`), fullPage: true, animations: 'disabled' })
  const results = await new AxeBuilder({ page: browserPage }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()
  expect(results.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))).toEqual([])
})
