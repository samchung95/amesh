import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'
import { mkdir, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

test('smokes the authenticated live Compose control room', async ({ page }) => {
  const liveBaseUrl = process.env.AMESH_LIVE_BASE_URL
  const liveToken = process.env.AMESH_LIVE_API_TOKEN
  test.skip(!liveBaseUrl || !liveToken, 'set AMESH_LIVE_BASE_URL and AMESH_LIVE_API_TOKEN for the live deployment gate')

  const consoleErrors: string[] = []
  const failedRequests: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  page.on('response', (response) => {
    if (response.status() >= 400 && response.url().includes('/api/')) {
      failedRequests.push(`${String(response.status())} ${new URL(response.url()).pathname}`)
    }
  })

  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto(liveBaseUrl!)
  await expect(page.getByRole('heading', { name: 'Sign in to AMESH' })).toBeVisible()
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill(liveToken!)
  await page.getByRole('button', { name: 'Open control room' }).click()
  await expect(page.getByRole('heading', { name: /Dashboard|Mission Control/ })).toBeVisible()
  await expect(page.getByText('Loading current work')).toBeHidden({ timeout: 60_000 })

  const stateSummary = page.getByLabel('Execution state summary')
  const running = stateSummary.getByRole('button', { name: /^[1-9]\d* Running/ })
  const failed = stateSummary.getByRole('button', { name: /^[1-9]\d* Failed recently/ })
  const completed = stateSummary.getByRole('button', { name: /^[1-9]\d* Completed recently/ })
  await expect(running).toBeVisible()
  await expect(failed).toBeVisible()
  await expect(completed).toBeVisible()
  const stateEvidence = {
    running: await running.getAttribute('aria-label') ?? await running.innerText(),
    failedRecently: await failed.getAttribute('aria-label') ?? await failed.innerText(),
    completedRecently: await completed.getAttribute('aria-label') ?? await completed.innerText(),
  }

  const missionResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
    .analyze()
  const missionSevere = missionResults.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))
  const outputDirectory = resolve(process.cwd(), '..', 'docs', 'product', 'ui-audit', 'screenshots', 'live')
  await mkdir(outputDirectory, { recursive: true })
  await page.screenshot({ path: resolve(outputDirectory, 'compose-control-room.png'), fullPage: true, animations: 'disabled' })

  await page.getByRole('region', { name: 'Running now' }).getByRole('link').first().click()
  await expect(page.getByRole('heading', { name: 'Simple execution trace' })).toBeVisible()
  await expect(page.locator('.trace-step-running')).toBeVisible()
  await page.locator('summary').filter({ hasText: 'Advanced evidence' }).click()
  await expect(page.getByRole('button', { name: 'Topology' })).toBeVisible()
  const traceResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
    .analyze()
  const traceSevere = traceResults.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))
  await page.screenshot({ path: resolve(outputDirectory, 'compose-execution-trace.png'), fullPage: true, animations: 'disabled' })
  await writeFile(resolve(outputDirectory, 'manifest.json'), `${JSON.stringify({
    schemaVersion: 'amesh.ui-audit/v1',
    capturedAt: process.env.AMESH_UI_AUDIT_CAPTURED_AT || '2026-08-24T00:00:00.000Z',
    source: liveBaseUrl,
    authenticated: true,
    stateEvidence,
    simpleTraceVerified: true,
    advancedEvidenceReachable: true,
    criticalOrSeriousAxeFindings: missionSevere.length + traceSevere.length,
    consoleErrors,
    failedRequests,
  }, null, 2)}\n`, 'utf8')

  expect(missionSevere).toEqual([])
  expect(traceSevere).toEqual([])
  expect(consoleErrors).toEqual([])
  expect(failedRequests).toEqual([])
})
