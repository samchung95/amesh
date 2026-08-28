import { expect, test } from '@playwright/test'

import type { HumanTask } from '../src/api/types'

const session = {
  principalId: '00000000-0000-7000-8000-000000000001',
  principalType: 'USER',
  display: 'App participant',
  tenantId: 'default',
  namespace: null,
  capabilities: {
    'apps.view': true,
    'apps.manage': true,
    'apps.execute': true,
    'humanTasks.view': true,
    'humanTasks.update': true,
    'dashboards.view': false,
  },
  telemetryEnabled: false,
  serverVersion: '0.2.0',
}

const workflowApp = {
  namespace: 'demo.apps',
  appId: 'expense-review',
  title: 'Expense review',
  description: 'Submit an expense for review.',
  flowId: 'expense_review_demo',
  flowRevision: 1,
  form: {
    fields: [
      { id: 'requester', type: 'text', label: 'Requester', helpText: 'Person requesting reimbursement.', required: true, sensitive: false, placeholder: 'Ada Lovelace', default: null, options: [], validation: {}, schema: {} },
      { id: 'amount', type: 'number', label: 'Amount', helpText: 'Requested reimbursement amount.', required: true, sensitive: false, placeholder: null, default: null, options: [], validation: { minimum: 0 }, schema: {} },
      { id: 'purpose', type: 'text', label: 'Business purpose', helpText: '', required: true, sensitive: false, placeholder: null, default: null, options: [], validation: {}, schema: {} },
    ],
    layout: [{ title: 'Inputs', helpText: '', columns: 1, fields: ['requester', 'amount', 'purpose'] }],
  },
  embedEnabled: true,
  launchLabel: 'Submit for approval',
  revision: 1,
  resourceVersion: 1,
  createdBy: session.principalId,
  createdAt: '2026-08-23T09:00:00Z',
}

const openTask: HumanTask = {
  humanTaskId: '00000000-0000-7000-8000-000000000501',
  namespace: 'demo.apps',
  executionId: '00000000-0000-7000-8000-000000000502',
  taskRunId: '00000000-0000-7000-8000-000000000503',
  attempt: 1,
  title: 'Review expense request',
  description: 'Confirm the amount and business purpose.',
  form: {
    fields: [{ id: 'accountingCode', type: 'text', label: 'Accounting code', helpText: 'Cost center for this expense.', required: true, sensitive: false, placeholder: null, default: null, options: [], validation: {}, schema: {} }],
    layout: [{ title: 'Approval details', helpText: '', columns: 1, fields: ['accountingCode'] }],
  },
  assigneeIds: [session.principalId],
  groupIds: [],
  deadlineAt: '2026-08-24T09:00:00Z',
  state: 'OPEN',
  version: 1,
  createdAt: '2026-08-23T09:00:00Z',
  decidedBy: null,
  decidedAt: null,
  reason: '',
  formValues: {},
  actions: [],
}

test('launches a linkable app and records a human approval', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop app acceptance')
  let task = { ...openTask }
  await page.route('**/ready', (route) => route.fulfill({ json: { status: 'ready', database: 'ready', migrations_applied: 49, migrations_expected: 49 } }))
  await page.route('**/api/v1/auth/providers**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: session }))
  await page.route('**/api/v1/apps', (route) => route.fulfill({ json: [workflowApp] }))
  await page.route('**/api/v1/apps/demo.apps/expense-review', (route) => route.fulfill({ json: workflowApp }))
  await page.route('**/api/v1/apps/demo.apps/expense-review/launch', (route) => route.fulfill({ json: { execution: { execution_id: openTask.executionId }, taskRuns: [], taskRunSummary: null, taskRunOffset: 0 } }))
  await page.route('**/api/v1/human-tasks?**', (route) => route.fulfill({ json: [task] }))
  await page.route('**/api/v1/human-tasks/*/actions', (route) => {
    task = { ...task, state: 'APPROVED', reason: 'Budget confirmed', formValues: { accountingCode: 'PLATFORM' }, decidedBy: session.principalId, decidedAt: '2026-08-23T09:05:00Z' }
    return route.fulfill({ json: task })
  })

  await page.goto('/')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('test-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await page.getByRole('link', { name: 'Apps' }).click()
  await expect(page.getByRole('heading', { name: 'Apps & approvals' })).toBeVisible()
  await page.getByRole('link', { name: /Expense review/ }).click()
  await page.getByLabel('Requester').fill('Ada Lovelace')
  await page.getByLabel('Amount').fill('125.50')
  await page.getByLabel('Business purpose').fill('Customer workshop')
  await page.getByRole('button', { name: 'Submit for approval' }).click()
  await expect(page.getByText('Execution accepted.')).toBeVisible()

  await page.getByRole('link', { name: 'All apps' }).click()
  await page.getByLabel('Accounting code').fill('PLATFORM')
  await page.getByLabel('Decision reason').fill('Budget confirmed')
  await page.getByRole('button', { name: 'Approve' }).click()
  await expect(page.getByText('APPROVED', { exact: true }).first()).toBeVisible()

  await page.goto('/embed/apps/demo.apps/expense-review')
  await expect(page.getByRole('heading', { name: 'Expense review' })).toBeVisible()
  await expect(page.locator('.app-embed')).toBeVisible()
})
