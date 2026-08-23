import { expect, test } from '@playwright/test'

const session = {
  principalId: '00000000-0000-7000-8000-000000000001',
  principalType: 'USER',
  display: 'Flow author',
  tenantId: 'default',
  namespace: 'examples.tests',
  capabilities: {
    'flows.view': true,
    'flowTests.view': true,
    'flowTests.manage': true,
    'flowTests.execute': true,
  },
  telemetryEnabled: false,
  serverVersion: '0.2.0',
}

test('defines and runs an isolated revision-pinned flow test', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop flow-test authoring acceptance')
  let definitions: Array<Record<string, unknown>> = []
  let runs: Array<Record<string, unknown>> = []

  await page.route('**/ready', (route) => route.fulfill({ json: { status: 'ready', database: 'ready', migrations_applied: 51, migrations_expected: 51 } }))
  await page.route('**/api/v1/auth/providers**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: session }))
  await page.route('**/api/v1/flows/examples.tests/approval/document', (route) => route.fulfill({ json: { namespace: 'examples.tests', flowId: 'approval', revision: 3, semanticHash: 'semantic-v3', document: {} } }))
  await page.route('**/api/v1/namespaces/examples.tests/flow-test-gate', (route) => route.fulfill({ json: null }))
  await page.route('**/api/v1/flows/examples.tests/approval/tests/runs**', (route) => {
    if (route.request().method() === 'GET') return route.fulfill({ json: runs })
    const result = {
      schemaVersion: 'amesh.flow-test-result/v1', runId: 'run-1', tenantId: 'default', namespace: 'examples.tests', flowId: 'approval', revision: 3,
      flowSemanticHash: 'semantic-v3', pluginSetHash: 'plugins-v3', simulatorVersion: 'amesh.flow-test/v1', outcome: 'PASSED',
      cases: [{ testId: 'happy-path', outcome: 'PASSED', state: 'SUCCESS', assertions: [{ path: 'state', passed: true, expected: 'SUCCESS', actual: 'SUCCESS' }], error: null }],
      coverage: { tasksTotal: 2, tasksCovered: 2, branchesTotal: 0, branchesCovered: 0, handlersTotal: 0, handlersCovered: 0, conditionsTotal: 0, conditionsCovered: 0, percentage: 100, disclaimer: 'Coverage is observed simulator execution, not proof of full workflow semantics.' },
      isolated: true, productionExecutionsCreated: 0, artifactsCreated: 0, secretLookups: 0, requestedBy: session.principalId, createdAt: '2026-08-23T10:00:00Z',
    }
    runs = [result]
    return route.fulfill({ json: result })
  })
  await page.route('**/api/v1/flows/examples.tests/approval/tests**', (route) => {
    if (new URL(route.request().url()).pathname.endsWith('/runs')) return route.fallback()
    if (route.request().method() === 'GET') return route.fulfill({ json: definitions })
    const draft = route.request().postDataJSON() as Record<string, unknown>
    const definition = {
      ...draft, id: 'definition-1', tenantId: 'default', namespace: 'examples.tests', flowId: 'approval',
      flowSemanticHash: 'semantic-v3', pluginSetHash: 'plugins-v3', version: 1, createdBy: session.principalId,
      updatedBy: session.principalId, createdAt: '2026-08-23T09:00:00Z', updatedAt: '2026-08-23T09:00:00Z',
    }
    definitions = [definition]
    return route.fulfill({ json: definition })
  })

  await page.goto('/')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('test-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await page.goto('/flows/examples.tests/approval/tests')

  await expect(page.getByRole('heading', { name: 'Define a test' })).toBeVisible()
  await page.getByRole('button', { name: 'Save test' }).click()
  await expect(page.getByText('Happy path', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Run all tests' }).click()
  await expect(page.getByText('PASSED', { exact: true })).toBeVisible()
  await expect(page.getByText('Isolated · 0 executions · 0 artifacts · 0 secret lookups')).toBeVisible()
  await expect(page.getByText('happy-path · state')).toBeVisible()
})
