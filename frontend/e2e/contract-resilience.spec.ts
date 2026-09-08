import { expect, test } from '@playwright/test'
import { readFileSync } from 'node:fs'

const flow = { namespace: 'demo', flow_id: 'safe', revision: 1, etag: 'r1', semantic_hash: 'test' }
const flowSchema: unknown = JSON.parse(readFileSync('../schemas/flow.schema.json', 'utf8'))
const catalog = JSON.parse(readFileSync('../schemas/resource-catalog.json', 'utf8')) as { resources: unknown[] }
const executionId = '00000000-0000-7000-8000-000000000067'
const timestamp = '2026-09-08T00:00:00Z'

test('keeps known workflow schemas editable and exposes every evidence kind in History', async ({ page }, testInfo) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.route('**/api/v1/**', async (route) => {
    const path = new URL(route.request().url()).pathname.slice('/api/v1'.length)
    let json: unknown
    if (path === '/auth/providers') json = []
    else if (path === '/ui/session') json = {
      principalId: 'operator', principalType: 'USER', display: 'Operator', tenantId: 'default', namespace: null,
      capabilities: { 'flows.view': true, 'flows.update': true, 'executions.view': true, 'announcements.view': false },
      telemetryEnabled: false, serverVersion: 'test',
    }
    else if (path === '/flows') json = [flow]
    else if (path === '/flows/editor/schema') json = {
      schemaVersion: 'amesh.flow-editor/v1', flowSchema,
      resourceCatalog: { ...catalog, resources: [...catalog.resources, { type: 'plugin.future', kind: 'future' }] },
      expressionContext: {},
    }
    else if (path === '/flows/demo/safe/document') json = {
      document: { id: 'safe', namespace: 'demo', revision: 1, tasks: [{ id: 'done', type: 'core.return', value: 'ok' }] }, revision: 1,
    }
    else if (path === '/flows/validate') json = { valid: true, irVersion: '1', semantic_hash: null, canonical: null, issues: [] }
    else if (path === '/policies/flows/validate') json = { allowed: true, outcome: 'ALLOW', matchedRules: [], requiredApprovals: [], mutations: [], pinnedPolicies: [], evaluationDurationMs: 0 }
    else if (path === `/executions/${executionId}`) json = {
      execution: {
        execution_id: executionId, tenant_id: 'default', state: 'SUCCESS', epoch: 1, version: 1,
        namespace: 'demo', flow_id: 'safe', flow_revision: 1, inputs: {}, outputs: {}, labels: {},
        trigger: { type: 'manual' }, created_by: 'operator', created_at: timestamp, updated_at: timestamp,
        timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {},
      }, taskRuns: [],
    }
    else if (path === `/executions/${executionId}/graph`) json = { nodes: [], edges: [] }
    else if (path === `/executions/${executionId}/evidence`) json = {
      items: ['DECISION', 'MODEL'].map((kind, index) => ({
        cursor: index + 1, event_id: `event-${index}`, execution_id: executionId, task_run_id: null,
        kind, event_type: `${kind.toLowerCase()}.completed`, payload: { reason: `${kind} evidence fixture` },
        occurred_at: timestamp, ingested_at: timestamp,
      })), nextCursor: null,
    }
    else if (path === `/executions/${executionId}/evidence/stream`) {
      await route.fulfill({ contentType: 'application/x-ndjson', body: '' })
      return
    }
    else if (path === `/executions/${executionId}/parent`) json = null
    else if (path === '/flows/demo/safe/revisions' || path.startsWith('/namespaces/demo/')
      || /^\/executions\/[^/]+\/(files|subflows|interventions|agent-sessions)$/.test(path)) json = []
    else {
      await route.fulfill({ status: 404, json: { detail: `Unexpected fixture request: ${path}` } })
      return
    }
    await route.fulfill({ json })
  })

  await page.goto('/flows/demo/safe/edit')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('fixture-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await expect(page.getByRole('status').filter({ hasText: 'plugin.future' })).toBeVisible()
  await page.getByRole('tab', { name: 'YAML', exact: true }).click()
  const editor = page.getByRole('textbox', { name: 'Flow YAML source' })
  await expect(editor).toContainText('core.return')
  await editor.fill('id: safe\nnamespace: demo\nrevision: 1\ntasks:\n  - id: done\n    type: core.return\n    value: updated\n')
  await expect(page.getByRole('button', { name: 'Save revision', exact: true })).toBeEnabled()
  await page.screenshot({ path: testInfo.outputPath('mixed-plugin-editor.png'), fullPage: true })

  await page.goto(`/executions/${executionId}?view=history`)
  const timeline = page.getByRole('region', { name: 'Live execution timeline' })
  const filter = timeline.getByRole('combobox', { name: 'Event kind' })
  await expect(filter.locator('option')).toHaveCount(14)
  await filter.selectOption('DECISION')
  await expect(timeline.getByText('DECISION evidence fixture', { exact: true })).toBeVisible()
  await expect(timeline.getByText('MODEL evidence fixture', { exact: true })).toHaveCount(0)
  await filter.selectOption('MODEL')
  await expect(timeline.getByText('MODEL evidence fixture', { exact: true })).toBeVisible()
  await expect(timeline.getByText('DECISION evidence fixture', { exact: true })).toHaveCount(0)
  await page.screenshot({ path: testInfo.outputPath('evidence-kind-filter.png'), fullPage: true })
  expect(errors).toEqual([])
})
