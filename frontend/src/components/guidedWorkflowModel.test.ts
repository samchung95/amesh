import { describe, expect, it } from 'vitest'
import { parse } from 'yaml'

import type { FlowEditorSchema } from '../api/types'
import {
  addGuidedStep,
  createIntentSource,
  hasRoundTripDocument,
  readGuidedWorkflow,
  updateGuidedIdentity,
  updateGuidedOutput,
  updateGuidedTask,
  updateGuidedTrigger,
} from './guidedWorkflowModel'

const schema: FlowEditorSchema = {
  schemaVersion: 'amesh.flow-editor/v1',
  flowSchema: {},
  resourceCatalog: {
    schemaVersion: 'amesh.resource-catalog/v1',
    resources: [
      { type: 'core.return', kind: 'task', configurationSchema: { type: 'object', properties: { value: {} } }, editor: { title: 'Return value', description: 'Return output.', category: 'Core', propertyOrder: ['value'] } },
      { type: 'core.log', kind: 'task', configurationSchema: { type: 'object', properties: { message: { type: 'string' } }, required: ['message'] }, editor: { title: 'Log message', description: 'Write a log.', category: 'Core', propertyOrder: ['message'] } },
    ],
  },
  expressionContext: {},
}

describe('guided workflow YAML projection', () => {
  it('creates every intent as ordinary canonical YAML', () => {
    for (const intent of ['scheduled', 'webhook', 'pipeline', 'approval', 'agent', 'blank'] as const) {
      const source = createIntentSource(intent, 'examples.guided', '00000000-0000-7000-8000-000000000002')
      const document = parse(source) as Record<string, unknown>
      expect(document).toMatchObject({ namespace: 'examples.guided', revision: 1 })
      expect(Array.isArray(document.tasks)).toBe(true)
      expect(hasRoundTripDocument(source)).toBe(true)
    }
  })

  it('round-trips guided changes without removing comments or code-only fields', () => {
    const source = `# operator note\nid: original\nnamespace: examples\nx-owner: data\ntasks:\n  - id: first\n    type: core.return\n    value: ok\n`
    const renamed = updateGuidedIdentity(source, 'id', 'renamed')
    const withStep = addGuidedStep(renamed, schema)
    const connected = updateGuidedTask(withStep, schema, 1, { dependsOn: 'first' })
    const output = updateGuidedOutput(connected, 'publish')
    expect(output).toContain('# operator note')
    expect(output).toContain('x-owner: data')
    expect(readGuidedWorkflow(output)).toMatchObject({ id: 'renamed', outputTaskId: 'publish', advancedPaths: ['x-owner'] })
  })

  it('uses catalog-derived required defaults when a guided step type changes', () => {
    const source = createIntentSource('blank', 'examples', '00000000-0000-7000-8000-000000000002')
    const updated = updateGuidedTask(source, schema, 0, { type: 'core.log' })
    expect(parse(updated)).toMatchObject({ tasks: [{ id: 'done', type: 'core.log', message: '' }] })
  })

  it('switches trigger types using valid starter configuration', () => {
    const source = createIntentSource('blank', 'examples', '00000000-0000-7000-8000-000000000002')
    const scheduled = parse(updateGuidedTrigger(source, 'core.cron')) as Record<string, unknown>
    expect(scheduled.triggers).toEqual([{ id: 'start', type: 'core.cron', cron: '0 9 * * *', timezone: 'UTC' }])
  })
})
