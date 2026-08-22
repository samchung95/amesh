import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

const session = {
  principalId: '00000000-0000-7000-8000-000000000002',
  principalType: 'USER',
  display: 'Operator',
  tenantId: 'default',
  namespace: null,
  capabilities: {
    'flows.view': true,
    'flows.create': true,
    'executions.view': true,
    'executions.execute': true,
    'namespaces.view': true,
    'plugins.view': true,
    'administration.manage': false,
  },
  telemetryEnabled: false,
  serverVersion: '0.2.0',
}

const flows = [
  { resource_id: 'flow-1', tenant_id: 'default', namespace: 'examples.engine', flow_id: 'hello_world', revision: 3, semantic_hash: 'abc1234567890def', etag: 'etag-1' },
  { resource_id: 'flow-2', tenant_id: 'default', namespace: 'examples.agent', flow_id: 'luna_research', revision: 1, semantic_hash: 'def1234567890abc', etag: 'etag-2' },
]

const executions = [
  { execution_id: '00000000-0000-7000-8000-000000000101', tenant_id: 'default', state: 'RUNNING', epoch: 1, version: 2, namespace: 'examples.engine', flow_id: 'hello_world', inputs: {}, trigger: { type: 'manual' }, created_at: '2026-08-21T12:00:00Z', updated_at: '2026-08-21T12:01:00Z' },
  { execution_id: '00000000-0000-7000-8000-000000000102', tenant_id: 'default', state: 'SUCCESS', epoch: 1, version: 4, namespace: 'examples.agent', flow_id: 'luna_research', inputs: {}, trigger: { type: 'cron' }, created_at: '2026-08-21T11:00:00Z', updated_at: '2026-08-21T11:02:00Z' },
]

async function mockApi(page: Page, overrides = session) {
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: overrides }))
  await page.route('**/api/v1/flows', (route) => route.fulfill({ json: flows }))
  await page.route('**/api/v1/executions?limit=200', (route) => route.fulfill({ json: executions }))
  await page.route('**/api/v1/executions/*', (route) => route.fulfill({ json: { execution: executions[0], taskRuns: [{ task_run_id: '00000000-0000-7000-8000-000000000201', execution_id: executions[0].execution_id, task_id: 'return', state: 'SUCCESS', current_attempt: 1, version: 2, retry_at: null, result: { value: 'cached' }, evidence: { cache: { decision: 'HIT', reason: 'reused a matching result', keyHash: 'abc123', sourceExecutionId: executions[1].execution_id, sourceTaskRunId: '00000000-0000-7000-8000-000000000202', sourceAttempt: 1, expiresAt: '2026-08-21T13:00:00Z' } } }] } }))
}

async function connect(page: Page) {
  await page.goto('/')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('test-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
}

test.beforeEach(async ({ page }) => {
  await mockApi(page)
})

test('connects, navigates resources, preserves deep links and opens the command palette', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop interaction acceptance')
  await connect(page)
  await expect(page.getByText('2', { exact: true }).first()).toBeVisible()
  await page.getByRole('link', { name: 'Executions' }).click()
  await expect(page).toHaveURL(/\/executions$/)
  await page.getByRole('link', { name: '…0101' }).click()
  await expect(page.getByRole('heading', { name: 'hello_world' })).toBeVisible()

  await page.reload()
  await expect(page.getByText('Task runs')).toBeVisible()
  await expect(page.getByText(/Cache hit · reused a matching result/)).toBeVisible()
  await page.keyboard.press('Control+K')
  await expect(page.getByRole('dialog', { name: 'Global command menu' })).toBeVisible()
  await page.locator('[cmdk-input]').fill('Flows')
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(/\/flows$/)

  if (testInfo.project.name === 'chromium') {
    await page.screenshot({ path: 'test-results/dashboard-shell.png', fullPage: true })
  }
})

test('uses server permissions for navigation and direct routes', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop policy acceptance')
  await connect(page)
  const administration = page.locator('.rail-link-disabled').filter({ hasText: 'Administration' })
  await expect(administration).toHaveAttribute('aria-disabled', 'true')
  await page.goto('/administration')
  await expect(page.getByRole('heading', { name: 'Permission required' })).toBeVisible()
})

test('switches locale and has no critical or serious automated accessibility findings', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop accessibility acceptance')
  await connect(page)
  await page.getByLabel('Language').selectOption('zh-CN')
  await expect(page.getByRole('heading', { name: '仪表板' })).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN')
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
  await page.keyboard.press('Tab')
  await expect(page.getByRole('link', { name: '跳至主要内容' })).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('main')).toBeFocused()
  await expect(page.getByRole('navigation')).toBeAttached()
  await expect(page.getByRole('complementary', { name: 'Primary' })).toBeAttached()

  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()
  expect(results.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))).toEqual([])
})

test('recovers a failed data view and makes no external requests', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop recovery acceptance')
  const origins = new Set<string>()
  page.on('request', (request) => origins.add(new URL(request.url()).origin))
  let attempts = 0
  await page.unroute('**/api/v1/flows')
  await page.route('**/api/v1/flows', (route) => {
    attempts += 1
    if (attempts <= 2) void route.fulfill({ status: 503, json: { detail: 'control plane unavailable' } })
    else void route.fulfill({ json: flows })
  })
  await connect(page)
  await page.getByRole('link', { name: 'Flows' }).click()
  await expect(page.getByRole('heading', { name: 'Unable to load this view' })).toBeVisible()
  await page.getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByText('hello_world')).toBeVisible()
  expect([...origins]).toEqual(['http://127.0.0.1:4173'])
})

test('uses the accessible compact navigation rail on tablet', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'tablet', 'tablet-only responsive acceptance')
  await connect(page)
  const rail = page.getByRole('complementary', { name: 'Primary' })
  await expect(rail).toBeVisible()
  expect((await rail.boundingBox())?.width).toBe(76)
  await page.getByRole('link', { name: 'Flows' }).click()
  await expect(page).toHaveURL(/\/flows$/)
})
