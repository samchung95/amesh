import { describe, expect, it } from 'vitest'

import type { WorkflowEditorSchema } from './workflowEditorSchemaModel'
import { buildFlowCompletions, validationDiagnostics } from './FlowCodeEditor'

const schema: WorkflowEditorSchema = {
  schemaVersion: 'amesh.flow-editor/v1',
  flowSchema: {
    type: 'object',
    properties: { namespace: { type: 'string', description: 'Flow namespace.' } },
  },
  resourceCatalog: {
    schemaVersion: 'amesh.resource-catalog/v1',
    resources: [
      {
        type: 'core.return',
        kind: 'task',
        configurationSchema: { properties: { value: { description: 'Returned value.' } } },
        editor: { title: 'Return', description: 'Return a value.', category: 'Core', propertyOrder: ['value'] },
      },
      {
        type: 'acme.enrich',
        kind: 'task',
        configurationSchema: { properties: { model: { type: 'string', description: 'Installed model.' } } },
        editor: { title: 'Enrich', description: 'Installed plugin task.', category: 'Acme', propertyOrder: ['model'] },
      },
    ],
  },
  expressionContext: {},
}

describe('flow code editor helpers', () => {
  it('offers core and installed plugin types with schema property documentation', () => {
    const completions = buildFlowCompletions(schema)
    expect(completions.resourceTypes.map((option) => option.label)).toEqual([
      'core.return',
      'acme.enrich',
    ])
    expect(completions.properties).toEqual(expect.arrayContaining([
      expect.objectContaining({ label: 'namespace', info: 'Flow namespace.' }),
      expect.objectContaining({ label: 'value', info: 'Returned value.' }),
      expect.objectContaining({ label: 'model', info: 'Installed model.' }),
    ]))
  })

  it('maps server source offsets to exact editor diagnostics', () => {
    expect(validationDiagnostics([{
      code: 'invalid_task',
      message: 'Task type is invalid.',
      path: '/tasks/0/type',
      hint: 'Choose an installed type.',
      sourceRange: {
        start: { line: 5, column: 11, offset: 42 },
        end: { line: 5, column: 20, offset: 51 },
      },
      severity: 'error',
    }], 100)).toEqual([expect.objectContaining({
      from: 42,
      to: 51,
      severity: 'error',
      message: 'Task type is invalid.\nChoose an installed type.',
    })])
  })
})
