import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

import type { ReleaseHistoryEntry, ReleaseTarget } from '../src/api/types'

type ReleaseSessionOptions = {
  canManage?: boolean
  canView?: boolean
}

const baseSession = {
  principalId: '00000000-0000-7000-8000-000000000818',
  principalType: 'USER',
  display: 'Release operator',
  tenantId: 'default',
  namespace: null,
  capabilities: {
    'releases.view': true,
    'releases.manage': true,
  },
  telemetryEnabled: false,
  serverVersion: '0.2.0',
}

const initialTarget: ReleaseTarget = {
  tenantId: 'default',
  targetKind: 'WORKFLOW' as const,
  targetKey: 'examples.safe/research',
  activeRevision: 1,
  activeConfigurationDigest: 'sha256:revision-one',
  state: 'ACTIVE' as const,
  version: 1,
  updatedAt: '2026-08-26T00:00:00Z',
}

const initialHistory: ReleaseHistoryEntry[] = [{
  eventId: 'release-event-1', tenantId: 'default', targetKind: 'WORKFLOW' as const,
  targetKey: initialTarget.targetKey, action: 'PROMOTE' as const, fromRevision: null,
  toRevision: 1, toConfigurationDigest: 'sha256:revision-one', gateDigest: 'sha256:gate-one',
  actorId: 'bootstrap', reason: 'initial release', version: 1, occurredAt: '2026-08-26T00:00:00Z',
}]

const passingGate = {
  gateId: 'gate-1', tenantId: 'default', policyId: 'policy-safe', policyDigest: 'sha256:policy',
  targetKind: 'WORKFLOW' as const, targetKey: initialTarget.targetKey, targetRevision: 2,
  configurationDigest: 'sha256:revision-two', evidenceDigests: ['sha256:evidence'], passed: true,
  failures: [], evaluatedAt: '2026-08-26T00:01:00Z',
}

async function prepareReleaseApi(page: Page, options: ReleaseSessionOptions = {}) {
  const canView = options.canView ?? true
  const canManage = options.canManage ?? true
  const session = {
    ...baseSession,
    capabilities: {
      'releases.view': canView,
      'releases.manage': canManage,
    },
  }
  let target: ReleaseTarget = { ...initialTarget }
  let history: ReleaseHistoryEntry[] = [...initialHistory]
  const requests: Array<{ path: string; body: Record<string, unknown> }> = []

  await page.addInitScript(() => {
    localStorage.setItem('amesh.ui.browser-session', '1')
    localStorage.setItem('amesh.ui.settings.v1', JSON.stringify({
      tenant: 'default', namespace: '', locale: 'en', timezone: 'UTC', savedViews: [], authenticationMode: 'session',
    }))
  })
  await page.route('**/ready', (route) => route.fulfill({ json: { status: 'ready', database: 'ready', migrations_applied: 65, migrations_expected: 65 } }))
  await page.route('**/api/v1/auth/providers**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: session }))
  await page.route('**/api/v1/releases/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const body = request.postDataJSON?.() as Record<string, unknown> | null
    if (body) requests.push({ path: url.pathname, body })

    if (request.method() === 'GET' && url.pathname.endsWith('/history')) return route.fulfill({ json: history })
    if (request.method() === 'GET') return route.fulfill({ json: target })
    if (url.pathname.endsWith('/preview')) return route.fulfill({ json: passingGate })
    if (url.pathname.endsWith('/apply')) {
      target = { ...target, activeRevision: 2, activeConfigurationDigest: 'sha256:revision-two', version: 2, updatedAt: '2026-08-26T00:02:00Z' }
      const event = { ...initialHistory[0], eventId: 'release-event-2', action: 'PROMOTE' as const, fromRevision: 1, toRevision: 2, toConfigurationDigest: target.activeConfigurationDigest, gateDigest: passingGate.policyDigest, actorId: baseSession.principalId, reason: String(body?.reason), version: 2, occurredAt: target.updatedAt }
      history = [event, ...history]
      return route.fulfill({ json: { target, event } })
    }
    if (url.pathname.endsWith('/rollback')) {
      target = { ...target, activeRevision: 1, activeConfigurationDigest: 'sha256:revision-one', version: 3, updatedAt: '2026-08-26T00:03:00Z' }
      const event = { ...initialHistory[0], eventId: 'release-event-3', action: 'ROLLBACK' as const, fromRevision: 2, toRevision: 1, toConfigurationDigest: target.activeConfigurationDigest, gateDigest: null, actorId: baseSession.principalId, reason: String(body?.reason), version: 3, occurredAt: target.updatedAt }
      history = [event, ...history]
      return route.fulfill({ json: { target, event } })
    }
    if (url.pathname.endsWith('/kill-switch')) {
      target = { ...target, state: 'KILLED' as const, version: 4, updatedAt: '2026-08-26T00:04:00Z' }
      const event = { ...initialHistory[0], eventId: 'release-event-4', action: 'KILL_SWITCH' as const, fromRevision: 1, toRevision: 1, toConfigurationDigest: target.activeConfigurationDigest, gateDigest: null, actorId: baseSession.principalId, reason: String(body?.reason), version: 4, occurredAt: target.updatedAt }
      history = [event, ...history]
      return route.fulfill({ json: { target, event } })
    }
    return route.fulfill({ status: 404, json: { detail: 'unsupported release route' } })
  })

  return { requests }
}

test('release.view opens the release route and preserves denied authorization', async ({ page }) => {
  await prepareReleaseApi(page, { canView: true, canManage: false })
  await page.goto('/releases')
  await expect(page.getByRole('heading', { name: 'Releases' })).toBeVisible()
  await expect(page.getByText('Preview only')).toBeVisible()

  await page.reload()
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: { ...baseSession, capabilities: { 'releases.view': false, 'releases.manage': false } } }))
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Permission required' })).toBeVisible()
})

test('preview-only release access can preview but cannot mutate', async ({ page }) => {
  const { requests } = await prepareReleaseApi(page, { canView: true, canManage: false })
  await page.goto('/releases')
  await page.getByLabel('Policy ID').fill('policy-safe')
  await page.getByRole('button', { name: 'Preview evidence' }).click()
  await expect(page.getByText('Gate passed', { exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Preview-only access' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Apply promotion' })).toHaveCount(0)
  expect(requests.map((request) => request.path)).toEqual([
    '/api/v1/releases/policies/policy-safe/preview',
  ])
})

test('release manager applies, rolls back, kills, updates history, and passes axe', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop release-control acceptance')
  const { requests } = await prepareReleaseApi(page)
  await page.goto('/releases')
  await page.getByLabel('Target type').selectOption('WORKFLOW')
  await page.getByLabel('Stable target key').fill(initialTarget.targetKey)
  await page.getByRole('button', { name: 'Inspect target' }).click()
  await expect(page.getByText('Concurrency version')).toBeVisible()

  await page.getByLabel('Policy ID').fill('policy-safe')
  await page.getByRole('button', { name: 'Preview evidence' }).click()
  await expect(page.getByText('Gate passed', { exact: true })).toBeVisible()
  await page.getByLabel('Change reason').fill('promote tested revision')
  await page.getByRole('button', { name: 'Apply promotion' }).click()
  await expect(page.getByText('Revision 2 is active at version 2.')).toBeVisible()
  await expect(page.getByText('2 events')).toBeVisible()

  await page.getByLabel('Prior revision').selectOption('1')
  await page.getByLabel('Recovery reason').fill('restore known good revision')
  await page.getByRole('button', { name: 'Rollback revision' }).click()
  await expect(page.getByRole('dialog')).toContainText('Confirm rollback to revision 1')
  await page.getByRole('button', { name: 'Confirm rollback' }).click()
  await expect(page.getByText('Rolled back to exact revision 1.')).toBeVisible()

  await page.getByLabel('Recovery reason').fill('stop during incident review')
  await page.getByRole('button', { name: 'Activate kill switch' }).click()
  await expect(page.getByRole('dialog')).toContainText('Confirm kill switch')
  await page.getByRole('button', { name: 'Confirm kill switch' }).click()
  await expect(page.getByText('Kill switch activated; this target is no longer active.')).toBeVisible()
  await expect(page.getByText('4 events')).toBeVisible()
  await expect(page.getByText('KILLED', { exact: true })).toBeVisible()
  await expect(page.getByText('Killed', { exact: true })).toBeVisible()

  expect(requests).toEqual(expect.arrayContaining([
    { path: '/api/v1/releases/policies/policy-safe/apply', body: { expectedVersion: 1, reason: 'promote tested revision', approvals: {} } },
    { path: `/api/v1/releases/WORKFLOW/${encodeURIComponent(initialTarget.targetKey)}/rollback`, body: { toRevision: 1, expectedVersion: 2, reason: 'restore known good revision' } },
    { path: `/api/v1/releases/WORKFLOW/${encodeURIComponent(initialTarget.targetKey)}/kill-switch`, body: { expectedVersion: 3, reason: 'stop during incident review' } },
  ]))

  const findings = await new AxeBuilder({ page }).analyze()
  expect(findings.violations.filter((violation) => violation.impact === 'critical' || violation.impact === 'serious')).toEqual([])
  const outputDirectory = resolve(process.cwd(), '..', 'docs', 'product', 'ui-audit', 'screenshots', 'after')
  await mkdir(outputDirectory, { recursive: true })
  await page.evaluate(() => {
    window.scrollTo(0, 0)
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur()
  })
  await page.screenshot({ path: resolve(outputDirectory, 'desktop-release-controls.png'), fullPage: true, animations: 'disabled' })
})
