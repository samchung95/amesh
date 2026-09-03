import type { FlowEditorSchema, FlowResourceSchema, JsonSchema } from '../../api/types'

export interface WorkflowEditorSchema {
  schemaVersion: string
  flowSchema: JsonSchema
  resourceCatalog: { schemaVersion: string; resources: FlowResourceSchema[] }
  expressionContext: Record<string, string>
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isResourceSchema(value: unknown): value is FlowResourceSchema {
  if (!isRecord(value) || typeof value.type !== 'string' || !['task', 'trigger', 'input'].includes(typeof value.kind === 'string' ? value.kind : '')) return false
  if (!isRecord(value.configurationSchema) || !isRecord(value.editor)) return false
  return typeof value.editor.title === 'string'
    && typeof value.editor.description === 'string'
    && typeof value.editor.category === 'string'
    && Array.isArray(value.editor.propertyOrder)
    && value.editor.propertyOrder.every((item) => typeof item === 'string')
}

export function normalizeWorkflowEditorSchema(value: FlowEditorSchema | undefined): WorkflowEditorSchema | undefined {
  if (!value || !isRecord(value.flowSchema) || !isRecord(value.resourceCatalog)) return undefined
  const resources = value.resourceCatalog.resources
  if (!Array.isArray(resources) || !resources.every(isResourceSchema)) return undefined
  return {
    schemaVersion: value.schemaVersion,
    flowSchema: value.flowSchema,
    resourceCatalog: {
      schemaVersion: typeof value.resourceCatalog.schemaVersion === 'string' ? value.resourceCatalog.schemaVersion : 'amesh.resource-catalog/v1',
      resources,
    },
    expressionContext: value.expressionContext,
  }
}
