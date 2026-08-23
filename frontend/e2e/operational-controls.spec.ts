import { expect, test } from '@playwright/test'

import type { Announcement, OperationalControl } from '../src/api/types'

const session = {
  principalId: '00000000-0000-7000-8000-000000000001',
  principalType: 'USER',
  display: 'Incident commander',
  tenantId: 'default',
  namespace: 'demo.ops',
  capabilities: {
    'announcements.view': true,
    'operationalControls.manage': true,
    'administration.manage': true,
  },
  telemetryEnabled: false,
  serverVersion: '0.2.0',
}

test('publishes an announcement and activates an acknowledged kill switch', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop operations acceptance')
  let announcements: Announcement[] = []
  let controls: OperationalControl[] = []

  await page.route('**/ready', (route) => route.fulfill({ json: { status: 'ready', database: 'ready', migrations_applied: 50, migrations_expected: 50 } }))
  await page.route('**/api/v1/auth/providers**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: session }))
  await page.route('**/api/v1/admin/controls**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/feature-flags**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/announcements**', (route) => {
    if (route.request().method() === 'POST') {
      const draft = route.request().postDataJSON() as Record<string, unknown>
      const created = {
        ...draft,
        id: 'announcement-1',
        tenantId: 'default',
        namespace: null,
        active: true,
        version: 1,
        createdBy: session.principalId,
        createdAt: '2026-08-23T09:00:00Z',
        updatedAt: '2026-08-23T09:00:00Z',
      } as Announcement
      announcements = [created]
      return route.fulfill({ status: 201, json: created })
    }
    return route.fulfill({ json: announcements })
  })
  await page.route('**/api/v1/operational-controls**', (route) => {
    if (route.request().method() === 'POST' && new URL(route.request().url()).pathname === '/api/v1/operational-controls') {
      const draft = route.request().postDataJSON() as Record<string, unknown>
      const created = {
        ...draft,
        id: 'control-1',
        tenantId: 'default',
        namespace: null,
        flowId: null,
        pluginId: null,
        runnerId: null,
        state: 'ACTIVE',
        version: 1,
        reviewAt: null,
        bypassUntil: null,
        bypassReason: null,
        createdBy: session.principalId,
        updatedBy: session.principalId,
        createdAt: '2026-08-23T09:01:00Z',
        updatedAt: '2026-08-23T09:01:00Z',
        acknowledgements: [{ componentId: 'executor-1', componentRole: 'EXECUTOR', controlVersion: 1, acknowledgedAt: '2026-08-23T09:01:01Z' }],
      } as OperationalControl
      controls = [created]
      return route.fulfill({ status: 201, json: created })
    }
    return route.fulfill({ json: controls })
  })

  await page.goto('/')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('test-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await page.getByRole('link', { name: 'Administration' }).click()
  await page.getByRole('button', { name: 'Controls' }).click()

  const announcementPanel = page.locator('.admin-panel').filter({ hasText: 'Announcements' })
  await announcementPanel.getByLabel('Title').fill('Incident maintenance')
  await announcementPanel.getByLabel('Severity').selectOption('CRITICAL')
  await announcementPanel.getByLabel('Message').fill('New launches pause while accepted work drains.')
  await announcementPanel.getByRole('button', { name: 'Publish announcement' }).click()
  await expect(announcementPanel.getByText('Incident maintenance')).toBeVisible()

  const controlPanel = page.locator('.admin-panel').filter({ hasText: 'Maintenance & kill switches' })
  await controlPanel.getByLabel('Kind').selectOption('KILL_SWITCH')
  await controlPanel.getByLabel('Name', { exact: true }).fill('Stop new launches')
  await controlPanel.getByRole('combobox').nth(2).selectOption('CANCEL')
  await controlPanel.getByLabel('Reason', { exact: true }).fill('incident containment')
  await controlPanel.getByLabel('WORKER DISPATCH').check()
  await controlPanel.getByRole('button', { name: 'Activate control' }).click()

  const status = page.locator('.admin-panel').filter({ hasText: 'Control status' })
  await expect(status.getByText('Stop new launches')).toBeVisible()
  await expect(status.getByText('EXECUTOR')).toBeVisible()
  await expect(status.getByText('CANCEL')).toBeVisible()
})
