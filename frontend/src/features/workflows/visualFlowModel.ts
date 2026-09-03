import { isSeq, parseDocument, type Document, type YAMLSeq } from 'yaml'

import type { FlowResourceSchema } from '../../api/types'
import type { WorkflowEditorSchema } from './workflowEditorSchemaModel'

export type VisualPath = Array<string | number>
export type VisualLifecycle = 'MAIN' | 'ERROR' | 'FINALLY' | 'AFTER_EXECUTION'

export interface VisualTaskNode {
  taskId: string
  taskType: string
  title: string
  category: string
  path: VisualPath
  collectionPath: VisualPath
  collectionKey: string
  collectionLabel: string
  index: number
  parentId: string | null
  lifecycle: VisualLifecycle
  dependencies: string[]
  children: string[]
  raw: Record<string, unknown>
  resource: FlowResourceSchema | null
  codeOnlyFields: string[]
}

export interface VisualTaskEdge {
  id: string
  source: string
  target: string
  kind: 'dependsOn' | 'contains' | 'handles'
}

export interface VisualGraphIssue {
  code: 'duplicate_id' | 'missing_reference' | 'incompatible_connection' | 'cycle'
  message: string
  taskId: string | null
}

export interface VisualFlowGraph {
  nodes: VisualTaskNode[]
  edges: VisualTaskEdge[]
  issues: VisualGraphIssue[]
}

export interface VisualMutation {
  source: string
  impact: 'generated' | 'lossy'
  summary: string
  details: string[]
}

export interface VisualDestination {
  id: string
  label: string
  collectionPath: VisualPath
  parentId: string | null
}

export interface VisualFieldChange {
  key: string
  value?: unknown
  remove?: boolean
}

const CHILD_FIELDS = new Set([
  'tasks',
  'then',
  'else',
  'elseIf',
  'cases',
  'predicateCases',
  'errors',
])

const COMMON_TASK_FIELDS = new Set([
  'id',
  'type',
  'description',
  'runLabels',
  'dependsOn',
  'runIf',
  'conditionErrorPolicy',
  'retry',
  'timeoutSeconds',
  'command',
  'stdin',
  'image',
  'environment',
  'resources',
  'taskRunner',
  'runnerCredentials',
  'networkPolicy',
  'securityPolicy',
  'inputFiles',
  'outputFiles',
  'outputManifest',
  'workspaceQuotaBytes',
  'retainDiagnosticsOnFailure',
  'concurrency',
  'priority',
  'workerGroup',
  'failurePolicy',
  'maxConcurrency',
  'contract',
  'taskCache',
  'condition',
  'errorSelector',
  ...CHILD_FIELDS,
])

export const GROUP_TASK_TYPES = new Set([
  'core.sequential',
  'core.parallel',
  'core.dag',
  'core.foreach',
  'core.while',
  'core.until',
  'core.workingDirectory',
])

const ROOT_DESTINATIONS: VisualDestination[] = [
  { id: 'flow:tasks', label: 'Main tasks', collectionPath: ['tasks'], parentId: null },
  { id: 'flow:errors', label: 'Flow error handlers', collectionPath: ['errors'], parentId: null },
  { id: 'flow:finally', label: 'Flow finally handlers', collectionPath: ['finally'], parentId: null },
  {
    id: 'flow:afterExecution',
    label: 'Flow after-execution handlers',
    collectionPath: ['afterExecution'],
    parentId: null,
  },
]

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function collectionKey(path: VisualPath): string {
  return JSON.stringify(path)
}

function pathStartsWith(path: VisualPath, prefix: VisualPath): boolean {
  return prefix.every((part, index) => path[index] === part)
}

function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

function parseSource(source: string): { document: Document.Parsed; data: Record<string, unknown> } {
  const document = parseDocument(source, { keepSourceTokens: true, strict: true })
  if (document.errors.length) throw new Error(document.errors[0]?.message || 'Invalid YAML source')
  const data = document.toJS() as unknown
  if (!isRecord(data)) throw new Error('Flow source must decode to an object')
  return { document, data }
}

function renderDocument(document: Document.Parsed): string {
  return document.toString({ lineWidth: 0 })
}

function taskResources(schema: WorkflowEditorSchema): Map<string, FlowResourceSchema> {
  return new Map(
    schema.resourceCatalog.resources
      .filter((resource) => resource.kind === 'task')
      .map((resource) => [resource.type, resource]),
  )
}

function nestedCollections(
  task: Record<string, unknown>,
  path: VisualPath,
  lifecycle: VisualLifecycle,
): Array<{
  tasks: unknown
  path: VisualPath
  lifecycle: VisualLifecycle
  label: string
}> {
  const collections: Array<{
    tasks: unknown
    path: VisualPath
    lifecycle: VisualLifecycle
    label: string
  }> = [
    { tasks: task.tasks, path: [...path, 'tasks'], lifecycle, label: 'children' },
    { tasks: task.then, path: [...path, 'then'], lifecycle, label: 'then branch' },
    { tasks: task.else, path: [...path, 'else'], lifecycle, label: 'else branch' },
    { tasks: task.errors, path: [...path, 'errors'], lifecycle: 'ERROR', label: 'local errors' },
  ]
  if (Array.isArray(task.elseIf)) {
    task.elseIf.forEach((branch, index) => {
      if (isRecord(branch)) collections.push({
        tasks: branch.tasks,
        path: [...path, 'elseIf', index, 'tasks'],
        lifecycle,
        label: `else-if ${typeof branch.id === 'string' ? branch.id : String(index + 1)}`,
      })
    })
  }
  if (isRecord(task.cases)) {
    Object.entries(task.cases).forEach(([name, tasks]) => collections.push({
      tasks,
      path: [...path, 'cases', name],
      lifecycle,
      label: `case ${name}`,
    }))
  }
  if (Array.isArray(task.predicateCases)) {
    task.predicateCases.forEach((branch, index) => {
      if (isRecord(branch)) collections.push({
        tasks: branch.tasks,
        path: [...path, 'predicateCases', index, 'tasks'],
        lifecycle,
        label: `predicate ${typeof branch.id === 'string' ? branch.id : String(index + 1)}`,
      })
    })
  }
  return collections
}

export function buildVisualFlowGraph(source: string, schema: WorkflowEditorSchema): VisualFlowGraph {
  const { data } = parseSource(source)
  const resources = taskResources(schema)
  const nodes: VisualTaskNode[] = []
  const edges: VisualTaskEdge[] = []
  const issues: VisualGraphIssue[] = []
  const ids = new Set<string>()

  const walk = (
    value: unknown,
    path: VisualPath,
    lifecycle: VisualLifecycle,
    parentId: string | null,
    label: string,
  ) => {
    if (!Array.isArray(value)) return
    value.forEach((candidate, index) => {
      if (!isRecord(candidate)) return
      const taskId = typeof candidate.id === 'string' ? candidate.id : `unnamed-${nodes.length + 1}`
      const taskType = typeof candidate.type === 'string' ? candidate.type : 'unknown'
      const resource = resources.get(taskType) || null
      const resourceFields = new Set(Object.keys(resource?.configurationSchema.properties || {}))
      const codeOnlyFields = Object.keys(candidate).filter(
        (key) => !COMMON_TASK_FIELDS.has(key) && !resourceFields.has(key),
      )
      if (!resource) codeOnlyFields.unshift(`unsupported type: ${taskType}`)
      if (ids.has(taskId)) issues.push({
        code: 'duplicate_id',
        message: `Task ID ${taskId} is declared more than once.`,
        taskId,
      })
      ids.add(taskId)
      const taskPath = [...path, index]
      const children: string[] = []
      nestedCollections(candidate, taskPath, lifecycle).forEach((collection) => {
        if (Array.isArray(collection.tasks)) {
          collection.tasks.forEach((child) => {
            if (isRecord(child) && typeof child.id === 'string') children.push(child.id)
          })
        }
      })
      const node: VisualTaskNode = {
        taskId,
        taskType,
        title: resource?.editor.title || taskType,
        category: resource?.editor.category || 'Code only',
        path: taskPath,
        collectionPath: path,
        collectionKey: collectionKey(path),
        collectionLabel: label,
        index,
        parentId,
        lifecycle,
        dependencies: stringList(candidate.dependsOn),
        children,
        raw: candidate,
        resource,
        codeOnlyFields,
      }
      nodes.push(node)
      if (parentId) edges.push({
        id: `contains:${parentId}:${taskId}`,
        source: parentId,
        target: taskId,
        kind: lifecycle === 'ERROR' ? 'handles' : 'contains',
      })
      nestedCollections(candidate, taskPath, lifecycle).forEach((collection) => {
        walk(collection.tasks, collection.path, collection.lifecycle, taskId, collection.label)
      })
    })
  }

  walk(data.tasks, ['tasks'], 'MAIN', null, 'main tasks')
  walk(data.errors, ['errors'], 'ERROR', null, 'flow errors')
  walk(data.finally, ['finally'], 'FINALLY', null, 'flow finally')
  walk(data.afterExecution, ['afterExecution'], 'AFTER_EXECUTION', null, 'after execution')

  const byId = new Map(nodes.map((node) => [node.taskId, node]))
  nodes.forEach((node) => {
    node.dependencies.forEach((dependency) => {
      const sourceNode = byId.get(dependency)
      edges.push({
        id: `dependsOn:${dependency}:${node.taskId}`,
        source: dependency,
        target: node.taskId,
        kind: 'dependsOn',
      })
      if (!sourceNode) issues.push({
        code: 'missing_reference',
        message: `${node.taskId} depends on missing task ${dependency}.`,
        taskId: node.taskId,
      })
      else if (sourceNode.collectionKey !== node.collectionKey) issues.push({
        code: 'incompatible_connection',
        message: `${dependency} and ${node.taskId} are in different task groups.`,
        taskId: node.taskId,
      })
    })
  })

  const adjacency = new Map<string, string[]>()
  edges.filter((edge) => edge.kind === 'dependsOn').forEach((edge) => {
    adjacency.set(edge.source, [...(adjacency.get(edge.source) || []), edge.target])
  })
  const visiting = new Set<string>()
  const visited = new Set<string>()
  const visit = (taskId: string): boolean => {
    if (visiting.has(taskId)) return true
    if (visited.has(taskId)) return false
    visiting.add(taskId)
    const cycle = (adjacency.get(taskId) || []).some(visit)
    visiting.delete(taskId)
    visited.add(taskId)
    return cycle
  }
  if (nodes.some((node) => visit(node.taskId))) issues.push({
    code: 'cycle',
    message: 'The dependency graph contains a cycle.',
    taskId: null,
  })
  return { nodes, edges, issues }
}

export function visualDestinations(graph: VisualFlowGraph): VisualDestination[] {
  return [
    ...ROOT_DESTINATIONS,
    ...graph.nodes
      .filter((node) => GROUP_TASK_TYPES.has(node.taskType))
      .map((node) => ({
        id: `task:${node.taskId}`,
        label: `Inside ${node.taskId}`,
        collectionPath: [...node.path, 'tasks'],
        parentId: node.taskId,
      })),
  ]
}

export function validateVisualConnection(
  graph: VisualFlowGraph,
  sourceId: string,
  targetId: string,
): string | null {
  const source = graph.nodes.find((node) => node.taskId === sourceId)
  const target = graph.nodes.find((node) => node.taskId === targetId)
  if (!source || !target) return 'Both connection endpoints must be existing tasks.'
  if (sourceId === targetId) return 'A task cannot depend on itself.'
  if (source.collectionKey !== target.collectionKey) return 'Dependencies must stay inside one task group.'
  if (target.dependencies.includes(sourceId)) return 'That dependency already exists.'
  const adjacency = new Map<string, string[]>()
  graph.edges.filter((edge) => edge.kind === 'dependsOn').forEach((edge) => {
    adjacency.set(edge.source, [...(adjacency.get(edge.source) || []), edge.target])
  })
  adjacency.set(sourceId, [...(adjacency.get(sourceId) || []), targetId])
  const pending = [targetId]
  const seen = new Set<string>()
  while (pending.length) {
    const current = pending.pop()
    if (!current || seen.has(current)) continue
    if (current === sourceId) return 'That connection would create a cycle.'
    seen.add(current)
    pending.push(...(adjacency.get(current) || []))
  }
  return null
}

function sequenceAt(document: Document.Parsed, path: VisualPath): YAMLSeq<unknown> {
  const node = document.getIn(path, true)
  if (!isSeq(node)) throw new Error(`Task group ${collectionKey(path)} is not a sequence`)
  return node
}

function ensureSequence(document: Document.Parsed, path: VisualPath): YAMLSeq<unknown> {
  let node = document.getIn(path, true)
  if (node === undefined) {
    document.setIn(path, [])
    node = document.getIn(path, true)
  }
  if (!isSeq(node)) throw new Error(`Task group ${collectionKey(path)} is not a sequence`)
  return node
}

function defaultForSchema(schema: Record<string, unknown>): unknown {
  if ('default' in schema) return schema.default
  if (Array.isArray(schema.enum) && schema.enum.length) return schema.enum[0]
  if ('const' in schema) return schema.const
  if (schema.type === 'boolean') return false
  if (schema.type === 'integer' || schema.type === 'number') {
    if (typeof schema.minimum === 'number') return schema.minimum
    if (typeof schema.exclusiveMinimum === 'number') return schema.exclusiveMinimum + 1
    return 1
  }
  if (schema.type === 'array') return []
  if (schema.type === 'object') return {}
  return ''
}

export function addVisualTask(
  source: string,
  schema: WorkflowEditorSchema,
  taskId: string,
  taskType: string,
  destination: VisualDestination,
): VisualMutation {
  const { document } = parseSource(source)
  const resource = schema.resourceCatalog.resources.find(
    (candidate) => candidate.kind === 'task' && candidate.type === taskType,
  )
  if (!resource) throw new Error(`Task type ${taskType} is not installed.`)
  const graph = buildVisualFlowGraph(source, schema)
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(taskId)) throw new Error('Use a non-empty task ID containing letters, numbers, dots, underscores or hyphens.')
  if (graph.nodes.some((node) => node.taskId === taskId)) throw new Error(`Task ID ${taskId} already exists.`)
  const task: Record<string, unknown> = { id: taskId, type: taskType }
  const properties = resource.configurationSchema.properties || {}
  for (const key of resource.configurationSchema.required || []) {
    const fieldSchema = properties[key]
    if (fieldSchema) task[key] = defaultForSchema(fieldSchema)
  }
  const sequence = ensureSequence(document, destination.collectionPath)
  sequence.add(document.createNode(task))
  return {
    source: renderDocument(document),
    impact: 'generated',
    summary: `Add ${taskId} to ${destination.label}`,
    details: ['A schema-derived task block will be generated in YAML.', 'Configure required values before saving.'],
  }
}

export function updateVisualTask(
  source: string,
  node: VisualTaskNode,
  changes: VisualFieldChange[],
): VisualMutation {
  const { document } = parseSource(source)
  changes.forEach((change) => {
    const path = [...node.path, change.key]
    if (change.remove) document.deleteIn(path)
    else document.setIn(path, change.value)
  })
  return {
    source: renderDocument(document),
    impact: 'generated',
    summary: `Configure ${node.taskId}`,
    details: changes.map((change) => `${change.remove ? 'Remove' : 'Set'} ${change.key}`),
  }
}

export function connectVisualTasks(
  source: string,
  schema: WorkflowEditorSchema,
  sourceId: string,
  targetId: string,
): VisualMutation {
  const graph = buildVisualFlowGraph(source, schema)
  const problem = validateVisualConnection(graph, sourceId, targetId)
  if (problem) throw new Error(problem)
  const target = graph.nodes.find((node) => node.taskId === targetId)
  if (!target) throw new Error(`Task ${targetId} was not found.`)
  const { document } = parseSource(source)
  document.setIn([...target.path, 'dependsOn'], [...target.dependencies, sourceId])
  return {
    source: renderDocument(document),
    impact: 'generated',
    summary: `Connect ${sourceId} to ${targetId}`,
    details: [`${targetId} will depend on ${sourceId}.`],
  }
}

export function disconnectVisualTasks(
  source: string,
  schema: WorkflowEditorSchema,
  sourceId: string,
  targetId: string,
): VisualMutation {
  const graph = buildVisualFlowGraph(source, schema)
  const target = graph.nodes.find((node) => node.taskId === targetId)
  if (!target || !target.dependencies.includes(sourceId)) throw new Error('Dependency was not found.')
  const dependencies = target.dependencies.filter((dependency) => dependency !== sourceId)
  const { document } = parseSource(source)
  if (dependencies.length) document.setIn([...target.path, 'dependsOn'], dependencies)
  else document.deleteIn([...target.path, 'dependsOn'])
  return {
    source: renderDocument(document),
    impact: 'generated',
    summary: `Disconnect ${sourceId} from ${targetId}`,
    details: [`The explicit dependency on ${sourceId} will be removed.`],
  }
}

export function reorderVisualTask(
  source: string,
  node: VisualTaskNode,
  direction: -1 | 1,
): VisualMutation {
  const { document } = parseSource(source)
  const sequence = sequenceAt(document, node.collectionPath)
  const nextIndex = node.index + direction
  if (nextIndex < 0 || nextIndex >= sequence.items.length) throw new Error('Task is already at the edge of its group.')
  const current = sequence.items[node.index]
  const next = sequence.items[nextIndex]
  if (!current || !next) throw new Error('Task ordering changed; refresh the visual model.')
  sequence.items[node.index] = next
  sequence.items[nextIndex] = current
  return {
    source: renderDocument(document),
    impact: 'generated',
    summary: `Move ${node.taskId} ${direction < 0 ? 'up' : 'down'}`,
    details: ['Only task sequence order changes; dependencies are preserved.'],
  }
}

export function removeVisualTask(
  source: string,
  schema: WorkflowEditorSchema,
  node: VisualTaskNode,
): VisualMutation {
  const graph = buildVisualFlowGraph(source, schema)
  const dependents = graph.nodes.filter((candidate) => candidate.dependencies.includes(node.taskId))
  const { document } = parseSource(source)
  dependents.forEach((dependent) => {
    const dependencies = dependent.dependencies.filter((dependency) => dependency !== node.taskId)
    if (dependencies.length) document.setIn([...dependent.path, 'dependsOn'], dependencies)
    else document.deleteIn([...dependent.path, 'dependsOn'])
  })
  sequenceAt(document, node.collectionPath).items.splice(node.index, 1)
  return {
    source: renderDocument(document),
    impact: 'lossy',
    summary: `Remove ${node.taskId}`,
    details: [
      `The task and its ${node.children.length} nested task(s) will be removed.`,
      `${dependents.length} incoming dependency reference(s) will be removed.`,
    ],
  }
}

export function moveVisualTask(
  source: string,
  schema: WorkflowEditorSchema,
  node: VisualTaskNode,
  destination: VisualDestination,
): VisualMutation {
  if (collectionKey(destination.collectionPath) === node.collectionKey) throw new Error('Task is already in that group.')
  if (pathStartsWith(destination.collectionPath, node.path)) {
    throw new Error('A task cannot be moved inside itself or one of its descendants.')
  }
  const graph = buildVisualFlowGraph(source, schema)
  const destinationIds = new Set(
    graph.nodes
      .filter((candidate) => candidate.collectionKey === collectionKey(destination.collectionPath))
      .map((candidate) => candidate.taskId),
  )
  const dependents = graph.nodes.filter(
    (candidate) => candidate.collectionKey === node.collectionKey && candidate.dependencies.includes(node.taskId),
  )
  const removedOwnDependencies = node.dependencies.filter((dependency) => !destinationIds.has(dependency))
  const { document } = parseSource(source)
  dependents.forEach((dependent) => {
    const dependencies = dependent.dependencies.filter((dependency) => dependency !== node.taskId)
    if (dependencies.length) document.setIn([...dependent.path, 'dependsOn'], dependencies)
    else document.deleteIn([...dependent.path, 'dependsOn'])
  })
  const sourceSequence = sequenceAt(document, node.collectionPath)
  const destinationSequence = ensureSequence(document, destination.collectionPath)
  const item = sourceSequence.items[node.index]
  if (!item) throw new Error('Task changed; refresh the visual model.')
  if (removedOwnDependencies.length) {
    const retained = node.dependencies.filter((dependency) => destinationIds.has(dependency))
    document.setIn([...node.path, 'dependsOn'], retained)
  }
  sourceSequence.items.splice(node.index, 1)
  destinationSequence.items.push(item)
  return {
    source: renderDocument(document),
    impact: dependents.length || removedOwnDependencies.length ? 'lossy' : 'generated',
    summary: `Move ${node.taskId} to ${destination.label}`,
    details: [
      `${dependents.length} dependency reference(s) in the old group will be removed.`,
      `${removedOwnDependencies.length} dependency reference(s) on the moved task will be removed.`,
    ],
  }
}
