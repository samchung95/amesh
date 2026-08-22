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
    'flows.update': true,
    'executions.view': true,
    'executions.execute': true,
    'executions.manage': true,
    'triggers.view': true,
    'triggers.manage': true,
    'checks.view': true,
    'checks.manage': true,
    'namespaces.view': true,
    'namespaceResources.read': true,
    'namespaceResources.write': true,
    'secretBindings.write': true,
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
  { execution_id: '00000000-0000-7000-8000-000000000101', tenant_id: 'default', state: 'RUNNING', epoch: 1, version: 2, namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, inputs: { message: 'hello' }, outputs: {}, labels: { environment: 'test' }, trigger: { type: 'manual' }, created_by: 'operator', created_at: '2026-08-21T12:00:00Z', updated_at: '2026-08-21T12:01:00Z', timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {} },
  { execution_id: '00000000-0000-7000-8000-000000000102', tenant_id: 'default', state: 'SUCCESS', epoch: 1, version: 4, namespace: 'examples.agent', flow_id: 'luna_research', flow_revision: 1, inputs: {}, outputs: {}, labels: {}, trigger: { type: 'cron' }, created_by: 'scheduler', created_at: '2026-08-21T11:00:00Z', updated_at: '2026-08-21T11:02:00Z', timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {} },
]

const triggers = [
  { trigger_definition_id: '00000000-0000-7000-8000-000000000301', tenant_id: 'default', namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, trigger_id: 'every_minute', trigger_type: 'core.cron', active: true, paused: false, checkpoint: {}, cursor: null, last_evaluated_at: '2026-08-21T12:01:00Z', next_evaluation_at: '2026-08-21T12:02:00Z', last_occurrence_at: '2026-08-21T12:01:00Z', last_success_at: '2026-08-21T12:01:00Z', lag_seconds: 2, pending_count: 1, dead_letter_count: 0, consecutive_failures: 0, last_error: null, last_decision: 'occurrence launched execution', updated_at: '2026-08-21T12:01:00Z' },
]

const triggerOccurrences = [
  { occurrence_id: '00000000-0000-7000-8000-000000000302', tenant_id: 'default', trigger_definition_id: triggers[0].trigger_definition_id, namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, trigger_id: 'every_minute', trigger_type: 'core.cron', occurrence_key: 'core.cron:examples.engine:hello_world:3:every_minute:2026-08-21T12:01:00Z', state: 'SUCCEEDED', attempt: 1, max_attempts: 3, available_at: '2026-08-21T12:01:00Z', payload: {}, metadata: { source: 'schedule' }, evidence: { reason: 'scheduled occurrence created an execution' }, execution_id: executions[1].execution_id, replay_of: null, created_at: '2026-08-21T12:01:00Z', updated_at: '2026-08-21T12:01:01Z', completed_at: '2026-08-21T12:01:01Z' },
]

const checkEvaluations = [
  { evaluation_id: '00000000-0000-7000-8000-000000000401', tenant_id: 'default', check_definition_id: '00000000-0000-7000-8000-000000000402', execution_id: executions[1].execution_id, namespace: 'examples.agent', flow_id: 'luna_research', flow_revision: 1, check_id: 'research-output', check_type: 'OUTPUT', source: 'EXPLICIT', evaluation_point: 'TERMINAL', subject_key: `execution:${executions[1].execution_id}`, outcome: 'PASS', severity: 'FAIL', reason: 'expression evaluated true', evidence: { result: true }, labels: { service: 'research' }, evaluated_at: '2026-08-21T11:02:00Z' },
  { evaluation_id: '00000000-0000-7000-8000-000000000403', tenant_id: 'default', check_definition_id: '00000000-0000-7000-8000-000000000404', execution_id: executions[0].execution_id, namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, check_id: 'start-latency', check_type: 'START_DELAY', source: 'NAMESPACE', evaluation_point: 'STARTED', subject_key: `execution:${executions[0].execution_id}`, outcome: 'WARN', severity: 'WARN', reason: 'execution start delay exceeded the configured threshold', evidence: { delaySeconds: 12 }, labels: { service: 'engine' }, evaluated_at: '2026-08-21T12:00:00Z' },
]

const checkCompliance = [
  { group_key: 'examples.agent.luna_research', total: 1, passed: 1, warned: 0, failed: 0, errors: 0, compliance_rate: 1 },
  { group_key: 'examples.engine.hello_world', total: 1, passed: 0, warned: 1, failed: 0, errors: 0, compliance_rate: 0 },
]

const checkPolicies = [
  { policy_id: '00000000-0000-7000-8000-000000000405', tenant_id: 'default', namespace: 'examples.engine', policy_key: 'interactive-start', source: 'NAMESPACE', task_type: null, definition: { id: 'start-latency', type: 'START_DELAY', severity: 'WARN', threshold: 'PT10S', enabled: true, actions: [] }, enabled: true, created_at: '2026-08-21T10:00:00Z', updated_at: '2026-08-21T10:00:00Z' },
]

const namespaceFiles = [
  { namespace: 'team.data', path: 'config/rules.json', version: 2, resourceVersion: 2, sizeBytes: 128, checksumSha256: 'a'.repeat(64), contentType: 'application/json', metadata: {}, originNamespace: 'team.data', inherited: false, createdAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T11:00:00Z' },
]

const namespaceKeyValues = [
  { namespace: 'team.data', key: 'release.channel', type: 'STRING', value: 'stable', expiresAt: null, metadata: {}, resourceVersion: 1, createdAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T10:00:00Z' },
]

const namespaceSecrets = [
  { namespace: 'team.data', key: 'API_KEY', provider: 'env', providerReference: 'PRODUCTION_API_KEY', metadata: {}, resourceVersion: 1, inherited: false, originNamespace: 'team.data', createdAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T10:00:00Z' },
]

async function mockApi(page: Page, overrides = session) {
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: overrides }))
  await page.route('**/api/v1/flows', (route) => route.fulfill({ json: flows }))
  await page.route('**/api/v1/flows/editor/schema', (route) => route.fulfill({ json: {
    schemaVersion: 'amesh.flow-editor/v1',
    flowSchema: { type: 'object', properties: { id: { type: 'string' }, namespace: { type: 'string' }, tasks: { type: 'array' } } },
    resourceCatalog: { schemaVersion: 'amesh.resource-catalog/v1', resources: [{ type: 'core.return', kind: 'task', configurationSchema: { type: 'object', properties: { value: {} } }, editor: { title: 'Return', description: 'Return a value.', category: 'Core', propertyOrder: ['value'] } }] },
    expressionContext: { inputs: 'Validated flow inputs.' },
  } }))
  await page.route('**/api/v1/flows/validate', (route) => route.fulfill({ json: { valid: true, irVersion: 'amesh.flow/v1', semantic_hash: 'editor-hash', canonical: {}, issues: [] } }))
  await page.route('**/api/v1/executions?limit=200', (route) => route.fulfill({ json: executions }))
  await page.route('**/api/v1/triggers', (route) => route.fulfill({ json: triggers }))
  await page.route('**/api/v1/trigger-occurrences?limit=200', (route) => route.fulfill({ json: triggerOccurrences }))
  await page.route('**/api/v1/check-evaluations?*', (route) => route.fulfill({ json: checkEvaluations }))
  await page.route('**/api/v1/check-compliance?*', (route) => route.fulfill({ json: checkCompliance }))
  await page.route('**/api/v1/check-policies?*', (route) => route.fulfill({ json: checkPolicies }))
  await page.route('**/api/v1/namespaces/team.data/files', (route) => route.fulfill({ json: namespaceFiles }))
  await page.route('**/api/v1/namespaces/team.data/key-values', (route) => route.fulfill({ json: namespaceKeyValues }))
  await page.route('**/api/v1/namespaces/team.data/secret-bindings', (route) => route.fulfill({ json: namespaceSecrets }))
  const taskRun = { task_run_id: '00000000-0000-7000-8000-000000000201', execution_id: executions[0].execution_id, task_id: 'return', state: 'SUCCESS', current_attempt: 1, version: 2, retry_at: null, result: { value: 'cached' }, iteration_key: null, labels: {}, failure_category: null, lifecycle_phase: 'MAIN', evidence: { cache: { decision: 'HIT', reason: 'reused a matching result', keyHash: 'abc123', sourceExecutionId: executions[1].execution_id, sourceTaskRunId: '00000000-0000-7000-8000-000000000202', sourceAttempt: 1, expiresAt: '2026-08-21T13:00:00Z' } } }
  const evidence = [
    { cursor: 1, event_id: 'evidence-1', execution_id: executions[0].execution_id, task_run_id: null, kind: 'STATE', event_type: 'execution.executioncreated', payload: { entity: 'execution', eventType: 'ExecutionCreated', actorId: 'operator', reason: 'manual launch' }, occurred_at: '2026-08-21T12:00:00Z', ingested_at: '2026-08-21T12:00:00Z' },
    { cursor: 2, event_id: 'evidence-2', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'STATE', event_type: 'task.taskruncreated', payload: { entity: 'task', eventType: 'TaskRunCreated', actorId: 'executor', payload: {} }, occurred_at: '2026-08-21T12:00:01Z', ingested_at: '2026-08-21T12:00:01Z' },
    { cursor: 3, event_id: 'evidence-3', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'STATE', event_type: 'task.taskrunstarted', payload: { entity: 'task', eventType: 'TaskRunStarted', actorId: 'executor', payload: { workerGroup: 'local' } }, occurred_at: '2026-08-21T12:00:02Z', ingested_at: '2026-08-21T12:00:02Z' },
    { cursor: 4, event_id: 'evidence-4', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'LOG', event_type: 'log.info', payload: { level: 'INFO', attempt: 1, workerId: 'worker-local', message: 'returned cached value', fields: { cache: 'hit' } }, occurred_at: '2026-08-21T12:00:03Z', ingested_at: '2026-08-21T12:00:03Z' },
    { cursor: 5, event_id: 'evidence-5', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'STATE', event_type: 'task.taskrunsucceeded', payload: { entity: 'task', eventType: 'TaskRunSucceeded', actorId: 'executor', payload: {} }, occurred_at: '2026-08-21T12:00:04Z', ingested_at: '2026-08-21T12:00:04Z' },
  ]
  await page.route('**/api/v1/executions/**', (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path.endsWith('/graph')) return route.fulfill({ json: { namespace: 'examples.engine', flowId: 'hello_world', revision: 3, nodes: [{ taskId: 'return', label: 'return', taskType: 'core.return', order: 0, depth: 0, parentId: null, dependencies: [], children: [], mode: null, failurePolicy: 'FAIL_FAST', maxConcurrency: null, state: 'SUCCESS', result: { value: 'cached' }, iterationCount: null, lifecyclePhase: 'MAIN', handlerOwnerId: null }], edges: [] } })
    if (path.endsWith('/evidence')) return route.fulfill({ json: { items: evidence, nextCursor: 'cursor-5' } })
    if (path.endsWith('/evidence/stream')) return route.fulfill({ body: '', contentType: 'application/x-ndjson' })
    if (path.endsWith('/files')) return route.fulfill({ json: [] })
    if (path.endsWith('/subflows')) return route.fulfill({ json: [] })
    if (path.endsWith('/parent-subflow')) return route.fulfill({ json: null })
    if (path.endsWith('/interventions/preview')) return route.fulfill({ json: { execution_id: executions[0].execution_id, action: 'PAUSE', current_state: 'RUNNING', predicted_state: 'PAUSED', current_version: 2, current_epoch: 1, checkpoint_task_id: null, impacted_task_ids: ['return'], preserved_task_ids: [], invalidates_active_claims: false, destructive: false, force_available_at: null, consequences: ['new task claims stop'] } })
    if (path.endsWith('/interventions')) return route.fulfill({ json: request.method() === 'GET' ? [] : { execution: executions[0], taskRuns: [taskRun], taskRunSummary: { total: 1, waiting: 0, running: 0, retry_delay: 0, succeeded: 1, failed: 0, cancelled: 0 }, taskRunOffset: 0 } })
    return route.fulfill({ json: { execution: executions[0], taskRuns: [taskRun], taskRunSummary: { total: 1, waiting: 0, running: 0, retry_delay: 0, succeeded: 1, failed: 0, cancelled: 0 }, taskRunOffset: 0 } })
  })
  await page.route('**/api/v1/backfills/preview', (route) => route.fulfill({ json: { selectionKind: 'REPLAY', executionCount: 1, estimatedTaskRuns: 1, estimatedCostUnits: 1, idempotencyKeyTemplate: 'replay:{sourceExecutionId}', warnings: [] } }))
  await page.route('**/api/v1/backfills', (route) => route.fulfill({ json: { backfillId: 'backfill-1', state: 'RUNNING', total: 1 } }))
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
  await expect(page.getByRole('heading', { name: 'Task runs' })).toBeVisible()
  await page.getByRole('button', { name: 'Data' }).click()
  await expect(page.getByText('Selected results and cache')).toBeVisible()
  await page.getByText('return · attempt 1').click()
  await expect(page.getByText('reused a matching result')).toBeVisible()
  await page.getByRole('button', { name: 'Logs' }).click()
  await expect(page.getByText('returned cached value')).toBeVisible()
  await page.getByLabel('Level').selectOption('INFO')
  await expect(page).toHaveURL(/view=logs.*level=INFO|level=INFO.*view=logs/)
  await page.getByRole('button', { name: 'Gantt' }).click()
  await expect(page.getByRole('heading', { name: 'Queue, wait and runner Gantt' })).toBeVisible()
  await page.getByRole('button', { name: 'History' }).click()
  await expect(page.getByText('ExecutionCreated')).toBeVisible()
  await page.getByRole('button', { name: 'Pause' }).click()
  await expect(page.getByRole('dialog', { name: /Confirm pause/ })).toBeVisible()
  await expect(page.getByText('new task claims stop')).toBeVisible()
  await page.getByRole('dialog', { name: /Confirm pause/ }).getByRole('button', { name: 'Cancel' }).click()
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

test('shows live trigger health and durable occurrence evidence', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop trigger monitor acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Triggers' }).click()
  await expect(page.getByRole('heading', { name: 'Trigger runtime' })).toBeVisible()
  await expect(page.getByText('every_minute').first()).toBeVisible()
  await expect(page.getByText('occurrence launched execution')).toBeVisible()
  await expect(page.getByText('scheduled occurrence created an execution')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Execution', exact: true })).toBeVisible()
})

test('shows check compliance, evaluation evidence and reusable policies', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop check monitor acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Checks' }).click()
  await expect(page.getByRole('heading', { name: 'Execution checks' })).toBeVisible()
  await expect(page.getByText('examples.agent.luna_research', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('research-output')).toBeVisible()
  await expect(page.getByText('expression evaluated true')).toBeVisible()
  await expect(page.getByText('interactive-start')).toBeVisible()
})

test('renders namespace files, typed values and secret references', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop namespace-resource acceptance')
  await page.addInitScript(() => localStorage.setItem('amesh.ui.settings.v1', JSON.stringify({ tenant: 'default', namespace: 'team.data', locale: 'en', timezone: 'UTC', savedViews: [], authenticationMode: 'token' })))
  await connect(page)
  await page.getByRole('link', { name: 'Namespaces' }).click()
  await expect(page.getByRole('heading', { name: 'team.data' })).toBeVisible()
  await expect(page.getByRole('row', { name: 'config/rules.json' })).toBeVisible()
  await expect(page.getByText('release.channel')).toBeVisible()
  await expect(page.getByText('PRODUCTION_API_KEY')).toBeVisible()
  await expect(page.getByText('References only')).toBeVisible()
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

test('authors a flow visually and falls back to the accessible YAML workbench', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop editor acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Flows' }).click()
  await page.getByRole('link', { name: 'Create flow' }).click()
  await expect(page.getByRole('heading', { name: 'Create flow' })).toBeVisible()
  await expect(page.getByLabel('Interactive workflow topology')).toBeVisible()
  await expect(page.getByLabel('Workflow mini map')).toBeVisible()
  await expect(page.locator('.visual-task-node').filter({ hasText: 'done' })).toBeVisible()
  await page.getByLabel('Task ID').fill('follow_up')
  await page.getByRole('button', { name: 'Add task' }).click()
  await expect(page.getByLabel('Generated YAML change review')).toContainText('GENERATED YAML')
  await page.getByRole('button', { name: 'Accept change' }).click()
  const followUp = page.locator('.visual-task-node').filter({ hasText: 'follow_up' })
  await expect(followUp).toBeVisible()
  await followUp.click()
  const visualInspector = page.getByRole('complementary', { name: 'Visual task inspector' })
  await visualInspector.getByLabel('value', { exact: true }).fill('"configured"')
  await visualInspector.getByRole('button', { name: 'Stage configuration' }).click()
  await page.getByRole('button', { name: 'Accept change' }).click()
  await visualInspector.getByRole('button', { name: 'Stage removal' }).click()
  await expect(page.getByLabel('Generated YAML change review')).toContainText('LOSSY TRANSFORMATION')
  await page.getByRole('button', { name: 'Cancel' }).click()
  await page.getByRole('tab', { name: 'YAML' }).click()
  const source = page.getByLabel('Flow YAML source')
  await expect(source).toBeVisible()
  await expect(page.getByRole('button', { name: 'Format' })).toBeEnabled()
  await source.click()
  await page.keyboard.press('Control+End')
  await page.keyboard.type('\ndescription: browser acceptance')
  await expect(page.getByRole('button', { name: 'Save' })).toBeEnabled()
  await expect.poll(() => page.evaluate(() => Object.keys(localStorage).some((key) => key.startsWith('amesh.flow-draft.v1:')))).toBe(true)
  page.once('dialog', async (dialog) => {
    expect(dialog.message()).toContain('Discard unsaved changes')
    await dialog.dismiss()
  })
  await page.locator('.back-link').click()
  await expect(page.getByRole('heading', { name: 'Create flow' })).toBeVisible()
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
    .analyze()
  expect(results.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))).toEqual([])
})
