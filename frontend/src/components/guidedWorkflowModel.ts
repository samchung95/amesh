import { isMap, isSeq, parseDocument, stringify, type Document } from 'yaml'

import type { AgentResourceRevision, ArtifactRef, FlowEditorSchema } from '../api/types'
import { DEFAULT_OPENROUTER_MODEL } from './agentDefinitionModel'

export type WorkflowIntent =
  | 'scheduled'
  | 'webhook'
  | 'pipeline'
  | 'approval'
  | 'agent'
  | 'blank'

export interface IntentStarter {
  id: WorkflowIntent
  title: string
  description: string
  outcome: string
}

export interface GuidedTaskState {
  id: string
  type: string
  dependsOn: string[]
  runner: string
  value: unknown
  message: string
  model: string
  prompt: string
  credentialRef: string
  agent: string
  agentRevision: number | null
  input: Record<string, unknown>
  invalidOutputPolicy: 'FAIL' | 'REPAIR'
  maxRepairAttempts: number
  dataHandling: 'DENY_SECRETS' | 'REDACT_SECRETS' | 'ALLOW'
  contextPolicy: {
    maxMessages: number
    maxBytes: number
    maxEstimatedTokens: number
    contextWindowTokens: number | null
    reservedCompletionTokens: number
  }
  artifact: ArtifactRef | null
  source: string
  limits: {
    maxBytes: number
    maxPages: number
    maxTokens: number
    chunkTokens: number
    wallTimeSeconds: number
  }
}

export interface GuidedWorkflowState {
  id: string
  namespace: string
  description: string
  triggerType: string
  inputMode: 'none' | 'text' | 'payload'
  tasks: GuidedTaskState[]
  outputTaskId: string
  advancedPaths: string[]
}

export const INTENT_STARTERS: IntentStarter[] = [
  { id: 'scheduled', title: 'Scheduled task', description: 'Run on a predictable cron schedule.', outcome: 'Prepare and publish a scheduled result.' },
  { id: 'webhook', title: 'Webhook / API', description: 'Start from an authenticated HTTP request.', outcome: 'Accept a payload and return a traceable result.' },
  { id: 'pipeline', title: 'Data pipeline', description: 'Move data through ordered processing steps.', outcome: 'Stage and publish a deterministic data result.' },
  { id: 'approval', title: 'Approval flow', description: 'Pause for an assigned human decision.', outcome: 'Request approval, then record the decision.' },
  { id: 'agent', title: 'AI / model task', description: 'Require schema-valid output from a bounded model call.', outcome: 'Ask Luna for structured JSON, validate it, then publish it.' },
  { id: 'blank', title: 'Blank advanced', description: 'Start small and use visual or YAML editing.', outcome: 'Create one deterministic return step.' },
]

const KNOWN_ROOT_FIELDS = new Set([
  'apiVersion',
  'id',
  'namespace',
  'revision',
  'description',
  'labels',
  'inputs',
  'variables',
  'triggers',
  'tasks',
  'outputs',
])

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function parseSource(source: string): { document: Document.Parsed; data: Record<string, unknown> } {
  const document = parseDocument(source, { keepSourceTokens: true, strict: true })
  if (document.errors.length) throw new Error(document.errors[0]?.message || 'Invalid YAML source')
  const data = document.toJS() as unknown
  if (!isRecord(data)) throw new Error('Flow source must decode to an object')
  return { document, data }
}

function render(document: Document.Parsed): string {
  return document.toString({ lineWidth: 0 })
}

function stringValue(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

function numberValue(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function taskRunner(value: unknown): string {
  return isRecord(value) ? stringValue(value.type) : ''
}

function defaultValue(schema: Record<string, unknown>): unknown {
  if ('default' in schema) return schema.default
  if (Array.isArray(schema.enum) && schema.enum.length) return schema.enum[0]
  if ('const' in schema) return schema.const
  if (schema.type === 'boolean') return false
  if (schema.type === 'integer' || schema.type === 'number') return typeof schema.minimum === 'number' ? schema.minimum : 1
  if (schema.type === 'array') return []
  if (schema.type === 'object') return {}
  return ''
}

function newTask(type: string, id: string, schema: FlowEditorSchema): Record<string, unknown> {
  const resource = schema.resourceCatalog.resources.find((item) => item.kind === 'task' && item.type === type)
  const task: Record<string, unknown> = { id, type }
  const properties = resource?.configurationSchema.properties || {}
  for (const field of resource?.configurationSchema.required || []) {
    const fieldSchema = properties[field]
    if (fieldSchema) task[field] = defaultValue(fieldSchema)
  }
  if (type.startsWith('agent.') && type !== 'agent.session') Object.assign(task, {
    provider: {
      adapter: 'openai-compatible',
      endpoint: 'https://openrouter.ai/api/v1/chat/completions',
      credentialRef: 'openrouter',
    },
    model: DEFAULT_OPENROUTER_MODEL,
    budget: { maxTotalTokens: 256, maxCompletionTokens: 128, maxCostUsd: '0.10' },
    dataHandling: { egress: 'REDACT_SECRETS', promptRetention: 'HASH_ONLY' },
    timeoutSeconds: 60,
  })
  if (type === 'agent.structured') Object.assign(task, {
    prompt: 'Return a short summary of the supplied input.',
    outputSchema: {
      type: 'object',
      properties: { summary: { type: 'string', minLength: 1 } },
      required: ['summary'],
      additionalProperties: false,
    },
  })
  if (type === 'agent.session') Object.assign(task, {
    agent: '',
    agentRevision: 1,
    input: {},
    invalidOutputPolicy: 'FAIL',
    maxRepairAttempts: 0,
    dataHandling: 'DENY_SECRETS',
    contextPolicy: {
      maxMessages: 64,
      maxBytes: 262144,
      maxEstimatedTokens: 65536,
      reservedCompletionTokens: 4096,
    },
  })
  if (type === 'core.document.extract') Object.assign(task, {
    artifact: null,
    source: 'document.pdf',
    limits: { maxBytes: 10_485_760, maxPages: 100, maxTokens: 20_000, chunkTokens: 1_000, wallTimeSeconds: 60 },
    inputFiles: { 'document.pdf': '' },
    outputFiles: ['document-result.json'],
  })
  return task
}

function starterTasks(
  intent: WorkflowIntent,
  principalId: string,
  agentResources: AgentResourceRevision[] = [],
  preferredAgentRef = '',
): Record<string, unknown>[] {
  if (intent === 'approval') return [
    {
      id: 'approve',
      type: 'core.approval',
      title: 'Approve this workflow run',
      description: 'Review the supplied input before the workflow continues.',
      assigneeIds: [principalId],
      deadlineSeconds: 86400,
    },
    { id: 'record_decision', type: 'core.return', dependsOn: ['approve'], value: '{{ outputs.approve }}' },
  ]
  if (intent === 'agent') {
    const compatible = agentResources
      .filter(isGuidedRequestCompatible)
      .sort((left, right) => `${left.key}@${left.revision}`.localeCompare(`${right.key}@${right.revision}`))
    const selected = compatible.find(
      (item) => `${item.key}@${String(item.revision)}` === preferredAgentRef,
    ) ?? compatible[0]
    const secretScopes = selected && 'permissions' in selected.spec ? selected.spec.permissions.secretScopes : []
    return [
      {
        id: 'run_agent',
        type: 'agent.session',
        agent: selected?.key || '',
        agentRevision: selected?.revision || 1,
        input: { request: '{{ inputs.request }}' },
        invalidOutputPolicy: 'FAIL',
        maxRepairAttempts: 0,
        dataHandling: 'DENY_SECRETS',
        contract: { secretScopes },
        contextPolicy: {
          maxMessages: 64,
          maxBytes: 262144,
          maxEstimatedTokens: 65536,
          reservedCompletionTokens: 4096,
        },
      },
      { id: 'publish', type: 'core.return', dependsOn: ['run_agent'], value: '{{ outputs.run_agent.result }}' },
    ]
  }
  if (intent === 'blank') return [{ id: 'done', type: 'core.return', value: 'ok' }]
  const firstId = intent === 'pipeline' ? 'stage' : intent === 'webhook' ? 'accept' : 'prepare'
  return [
    { id: firstId, type: 'core.return', value: intent === 'webhook' ? '{{ trigger.body }}' : 'ready' },
    { id: 'publish', type: 'core.return', dependsOn: [firstId], value: `{{ outputs.${firstId}.value }}` },
  ]
}

export function createIntentSource(
  intent: WorkflowIntent,
  namespace: string,
  principalId: string,
  agentResources: AgentResourceRevision[] = [],
  preferredAgentRef = '',
): string {
  const root: Record<string, unknown> = {
    id: `${intent}_workflow`,
    namespace: namespace || 'default',
    revision: 1,
    description: INTENT_STARTERS.find((item) => item.id === intent)?.outcome || '',
    labels: { team: 'platform', createdWith: 'guided' },
    tasks: starterTasks(intent, principalId, agentResources, preferredAgentRef),
  }
  if (intent === 'scheduled') root.triggers = [{ id: 'schedule', type: 'core.cron', cron: '0 9 * * *', timezone: 'UTC' }]
  if (intent === 'webhook') root.triggers = [{ id: 'webhook', type: 'core.webhook', maxPending: 100, maxAttempts: 3, retryDelay: 'PT5S' }]
  if (intent === 'pipeline') root.inputs = [{ id: 'payload', type: 'JSON', required: false, default: {} }]
  if (intent === 'agent') root.inputs = [{ id: 'request', type: 'STRING', required: false, default: 'Summarize this workflow.' }]
  const outputTask = (root.tasks as Record<string, unknown>[]).at(-1)
  if (outputTask) root.outputs = { result: `{{ outputs.${String(outputTask.id)}.value }}` }
  return render(parseDocument(stringify(root, { lineWidth: 0 })))
}

export function isGuidedRequestCompatible(resource: AgentResourceRevision): boolean {
  if (resource.kind !== 'AGENT' || resource.spec.kind !== 'AGENT') return false
  const required = resource.spec.inputSchema.required
  return !Array.isArray(required) || required.every((field) => field === 'request')
}

export function readGuidedWorkflow(source: string): GuidedWorkflowState {
  const { data } = parseSource(source)
  const tasks = Array.isArray(data.tasks) ? data.tasks.filter(isRecord) : []
  const triggers = Array.isArray(data.triggers) ? data.triggers.filter(isRecord) : []
  const inputs = Array.isArray(data.inputs) ? data.inputs.filter(isRecord) : []
  const outputResult = isRecord(data.outputs) ? stringValue(data.outputs.result) : ''
  const outputTaskId = tasks
    .map((task) => stringValue(task.id))
    .filter(Boolean)
    .sort((left, right) => right.length - left.length)
    .find((taskId) => outputResult.includes(`outputs.${taskId}.`)) || ''
  const advancedPaths = Object.keys(data).filter((key) => !KNOWN_ROOT_FIELDS.has(key))
  if (tasks.length > 2) advancedPaths.push(`tasks[2…${String(tasks.length - 1)}]`)
  if (triggers.length > 1) advancedPaths.push(`triggers[1…${String(triggers.length - 1)}]`)
  return {
    id: stringValue(data.id),
    namespace: stringValue(data.namespace),
    description: stringValue(data.description),
    triggerType: stringValue(triggers[0]?.type),
    inputMode: inputs.length === 0 ? 'none' : inputs[0]?.type === 'JSON' ? 'payload' : 'text',
    tasks: tasks.slice(0, 2).map((task) => ({
      id: stringValue(task.id),
      type: stringValue(task.type),
      dependsOn: stringList(task.dependsOn),
      runner: taskRunner(task.taskRunner),
      value: task.value,
      message: stringValue(task.message),
      model: stringValue(task.model),
      prompt: stringValue(task.prompt),
      credentialRef: isRecord(task.provider) ? stringValue(task.provider.credentialRef) : '',
      agent: stringValue(task.agent),
      agentRevision: typeof task.agentRevision === 'number' ? task.agentRevision : null,
      input: isRecord(task.input) ? task.input : {},
      invalidOutputPolicy: task.invalidOutputPolicy === 'REPAIR' ? 'REPAIR' : 'FAIL',
      maxRepairAttempts: numberValue(task.maxRepairAttempts, 0),
      dataHandling: task.dataHandling === 'ALLOW' || task.dataHandling === 'REDACT_SECRETS' ? task.dataHandling : 'DENY_SECRETS',
      contextPolicy: isRecord(task.contextPolicy) ? {
        maxMessages: numberValue(task.contextPolicy.maxMessages, 64),
        maxBytes: numberValue(task.contextPolicy.maxBytes, 262144),
        maxEstimatedTokens: numberValue(task.contextPolicy.maxEstimatedTokens, 65536),
        contextWindowTokens: typeof task.contextPolicy.contextWindowTokens === 'number'
          ? numberValue(task.contextPolicy.contextWindowTokens, 65536)
          : null,
        reservedCompletionTokens: numberValue(task.contextPolicy.reservedCompletionTokens, 4096),
      } : {
        maxMessages: 64,
        maxBytes: 262144,
        maxEstimatedTokens: 65536,
        contextWindowTokens: null,
        reservedCompletionTokens: 4096,
      },
      artifact: isRecord(task.artifact) && typeof task.artifact.reference === 'string' && isRecord(task.artifact.provenance)
        ? task.artifact as unknown as ArtifactRef
        : null,
      source: stringValue(task.source) || 'document.pdf',
      limits: isRecord(task.limits) ? {
        maxBytes: numberValue(task.limits.maxBytes, 10_485_760),
        maxPages: numberValue(task.limits.maxPages, 100),
        maxTokens: numberValue(task.limits.maxTokens, 20_000),
        chunkTokens: numberValue(task.limits.chunkTokens, 1_000),
        wallTimeSeconds: numberValue(task.limits.wallTimeSeconds, 60),
      } : {
        maxBytes: 10_485_760,
        maxPages: 100,
        maxTokens: 20_000,
        chunkTokens: 1_000,
        wallTimeSeconds: 60,
      },
    })),
    outputTaskId,
    advancedPaths,
  }
}

export function updateGuidedDocumentArtifact(
  source: string,
  index: number,
  artifact: ArtifactRef | null,
  documentSource = 'document.pdf',
): string {
  const { data: original } = parseSource(source)
  const originalTasks = Array.isArray(original.tasks) ? original.tasks.filter(isRecord) : []
  const originalTask = originalTasks[index]
  const previousSource = originalTask ? stringValue(originalTask.source) || 'document.pdf' : 'document.pdf'
  const nextSource = documentSource || 'document.pdf'
  let next = updateGuidedTaskField(source, index, 'artifact', artifact)
  next = updateGuidedTaskField(next, index, 'source', nextSource)
  next = updateGuidedTaskField(next, index, ['inputFiles', nextSource], artifact?.reference || '')
  if (previousSource === nextSource) return next
  const { document } = parseSource(next)
  document.deleteIn(['tasks', index, 'inputFiles', previousSource])
  return render(document)
}

export function updateGuidedIdentity(
  source: string,
  field: 'id' | 'namespace' | 'description',
  value: string,
): string {
  const { document } = parseSource(source)
  if (field === 'description' && !value) document.delete(field)
  else document.set(field, value)
  return render(document)
}

export function updateGuidedInput(
  source: string,
  mode: GuidedWorkflowState['inputMode'],
): string {
  const { document } = parseSource(source)
  if (mode === 'none') document.delete('inputs')
  else if (mode === 'payload') document.set('inputs', [{ id: 'payload', type: 'JSON', required: false, default: {} }])
  else document.set('inputs', [{ id: 'message', type: 'STRING', required: false, default: 'Hello' }])
  return render(document)
}

export function updateGuidedTrigger(source: string, type: string): string {
  const { document } = parseSource(source)
  if (!type) document.delete('triggers')
  else {
    const trigger: Record<string, unknown> = { id: 'start', type }
    if (type === 'core.cron') Object.assign(trigger, { cron: '0 9 * * *', timezone: 'UTC' })
    if (type === 'core.interval') Object.assign(trigger, { interval: 'PT1H', timezone: 'UTC' })
    if (type === 'core.webhook') Object.assign(trigger, { maxPending: 100, maxAttempts: 3, retryDelay: 'PT5S' })
    document.set('triggers', [trigger])
  }
  return render(document)
}

export function updateGuidedTask(
  source: string,
  schema: FlowEditorSchema,
  index: number,
  changes: { id?: string; type?: string; dependsOn?: string; runner?: string; prompt?: string; model?: string; credentialRef?: string },
): string {
  const { document, data } = parseSource(source)
  const tasks = Array.isArray(data.tasks) ? data.tasks.filter(isRecord) : []
  const current = tasks[index]
  if (!current) throw new Error(`Step ${String(index + 1)} does not exist.`)
  if (changes.type && changes.type !== current.type) {
    const replacement = newTask(changes.type, stringValue(current.id) || `step_${String(index + 1)}`, schema)
    if (Array.isArray(current.dependsOn)) replacement.dependsOn = current.dependsOn
    document.setIn(['tasks', index], replacement)
  }
  if (changes.id !== undefined) document.setIn(['tasks', index, 'id'], changes.id)
  if (changes.dependsOn !== undefined) {
    if (changes.dependsOn) document.setIn(['tasks', index, 'dependsOn'], [changes.dependsOn])
    else document.deleteIn(['tasks', index, 'dependsOn'])
  }
  if (changes.runner !== undefined) {
    if (changes.runner) document.setIn(['tasks', index, 'taskRunner'], { type: changes.runner })
    else document.deleteIn(['tasks', index, 'taskRunner'])
  }
  if (changes.prompt !== undefined) document.setIn(['tasks', index, 'prompt'], changes.prompt)
  if (changes.model !== undefined) document.setIn(['tasks', index, 'model'], changes.model)
  if (changes.credentialRef !== undefined) document.setIn(['tasks', index, 'provider', 'credentialRef'], changes.credentialRef)
  return render(document)
}

export function updateGuidedTaskField(
  source: string,
  index: number,
  field: string | string[],
  value: unknown,
): string {
  const { document } = parseSource(source)
  const path = ['tasks', index, ...(Array.isArray(field) ? field : [field])]
  if (value === undefined) document.deleteIn(path)
  else document.setIn(path, value)
  return render(document)
}

export function updateGuidedAgentSelection(
  source: string,
  index: number,
  key: string,
  revision: number,
  secretScopes: string[],
): string {
  let next = updateGuidedTaskField(source, index, 'agent', key)
  next = updateGuidedTaskField(next, index, 'agentRevision', revision)
  return updateGuidedTaskField(next, index, ['contract', 'secretScopes'], secretScopes)
}

export function addGuidedStep(source: string, schema: FlowEditorSchema): string {
  const { document, data } = parseSource(source)
  const tasks = Array.isArray(data.tasks) ? data.tasks.filter(isRecord) : []
  if (tasks.length >= 2) return source
  const previousId = stringValue(tasks[0]?.id)
  const task = newTask('core.return', 'publish', schema)
  task.value = previousId ? `{{ outputs.${previousId}.value }}` : 'ok'
  if (previousId) task.dependsOn = [previousId]
  const sequence = document.get('tasks', true)
  if (!isSeq(sequence)) document.set('tasks', [task])
  else sequence.add(document.createNode(task))
  return render(document)
}

export function updateGuidedOutput(source: string, taskId: string): string {
  const { document } = parseSource(source)
  if (!taskId) document.delete('outputs')
  else document.set('outputs', { result: `{{ outputs.${taskId}.value }}` })
  return render(document)
}

export function taskSupportsRunner(schema: FlowEditorSchema, type: string): boolean {
  const resource = schema.resourceCatalog.resources.find((item) => item.kind === 'task' && item.type === type)
  return Boolean(resource?.configurationSchema.properties?.taskRunner)
}

export function taskSupportsModel(schema: FlowEditorSchema, type: string): boolean {
  const resource = schema.resourceCatalog.resources.find((item) => item.kind === 'task' && item.type === type)
  return Boolean(resource?.configurationSchema.properties?.model)
}

export function hasRoundTripDocument(source: string): boolean {
  const { document } = parseSource(source)
  return isMap(document.contents)
}
