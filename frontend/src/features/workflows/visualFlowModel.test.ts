import { describe, expect, it } from 'vitest'
import { parse } from 'yaml'

import type { WorkflowEditorSchema } from './workflowEditorSchemaModel'
import {
  addVisualTask,
  buildVisualFlowGraph,
  connectVisualTasks,
  disconnectVisualTasks,
  moveVisualTask,
  removeVisualTask,
  reorderVisualTask,
  updateVisualTask,
  validateVisualConnection,
  visualDestinations,
  type VisualFlowGraph,
  type VisualTaskNode,
} from './visualFlowModel'

interface TestTask {
  id: string
  type: string
  dependsOn?: string[]
  tasks?: TestTask[]
  [key: string]: unknown
}

interface TestFlow {
  extension: { untouched: boolean }
  tasks: TestTask[]
}

function decode(value: string): TestFlow {
  const parsed: unknown = parse(value)
  return parsed as TestFlow
}

function task(graph: VisualFlowGraph, taskId: string): VisualTaskNode {
  const found = graph.nodes.find((node) => node.taskId === taskId)
  if (!found) throw new Error(`Missing test task ${taskId}`)
  return found
}

const schema: WorkflowEditorSchema = {
  schemaVersion: 'amesh.flow-editor/v1',
  flowSchema: { type: 'object' },
  resourceCatalog: {
    schemaVersion: 'amesh.resource-catalog/v1',
    resources: [
      {
        type: 'core.return',
        kind: 'task',
        configurationSchema: {
          type: 'object',
          properties: { value: {}, timeoutSeconds: { type: 'number' } },
        },
        editor: { title: 'Return value', description: 'Return a value.', category: 'Core', propertyOrder: ['value'] },
      },
      {
        type: 'core.log',
        kind: 'task',
        configurationSchema: {
          type: 'object',
          properties: { message: { type: 'string' } },
          required: ['message'],
        },
        editor: { title: 'Log message', description: 'Write a log.', category: 'Core', propertyOrder: ['message'] },
      },
      {
        type: 'core.parallel',
        kind: 'task',
        configurationSchema: {
          type: 'object',
          properties: { tasks: { type: 'array' }, maxConcurrency: { type: 'integer' } },
        },
        editor: { title: 'Parallel group', description: 'Run children.', category: 'Flow control', propertyOrder: ['maxConcurrency'] },
      },
      {
        type: 'core.subflow',
        kind: 'task',
        configurationSchema: {
          type: 'object',
          properties: { namespace: { type: 'string' }, flowId: { type: 'string' } },
          required: ['namespace', 'flowId'],
        },
        editor: { title: 'Invoke subflow', description: 'Invoke a flow.', category: 'Flow control', propertyOrder: ['namespace', 'flowId'] },
      },
    ],
  },
  expressionContext: {},
}

const source = `# flow comment
id: visual
namespace: tests
extension:
  untouched: true
tasks:
  - id: prepare # keep task comment
    type: core.return
    value: ready
  - id: group
    type: core.parallel
    maxConcurrency: 2
    tasks:
      - id: child
        type: core.return
        runIf: "{{ inputs.ready }}"
        retry: {type: constant, maxAttempts: 2}
        timeoutSeconds: 30
        value: nested
  - id: invoke
    type: core.subflow
    dependsOn: [prepare]
    namespace: examples
    flowId: child_flow
errors:
  - id: recover
    type: core.log
    message: failed
`

describe('visual flow model', () => {
  it('renders nested, lifecycle and dependency topology from canonical YAML', () => {
    const graph = buildVisualFlowGraph(source, schema)
    expect(graph.nodes.map((node) => node.taskId)).toEqual(['prepare', 'group', 'child', 'invoke', 'recover'])
    expect(graph.nodes.find((node) => node.taskId === 'child')).toMatchObject({
      parentId: 'group',
      collectionLabel: 'children',
      lifecycle: 'MAIN',
    })
    expect(graph.nodes.find((node) => node.taskId === 'recover')?.lifecycle).toBe('ERROR')
    expect(graph.edges).toEqual(expect.arrayContaining([
      expect.objectContaining({ source: 'prepare', target: 'invoke', kind: 'dependsOn' }),
      expect.objectContaining({ source: 'group', target: 'child', kind: 'contains' }),
    ]))
    expect(graph.issues).toEqual([])
  })

  it('prevents cycles, missing references and cross-group connections before mutation', () => {
    const graph = buildVisualFlowGraph(source, schema)
    expect(validateVisualConnection(graph, 'invoke', 'prepare')).toContain('cycle')
    expect(validateVisualConnection(graph, 'prepare', 'child')).toContain('one task group')
    expect(validateVisualConnection(graph, 'missing', 'prepare')).toContain('existing tasks')
    const invalid = buildVisualFlowGraph(source.replace('dependsOn: [prepare]', 'dependsOn: [missing]'), schema)
    expect(invalid.issues[0]?.code).toBe('missing_reference')
  })

  it('stages generated edits while preserving comments and unrelated semantic content', () => {
    const graph = buildVisualFlowGraph(source, schema)
    const connected = connectVisualTasks(source, schema, 'group', 'invoke')
    expect(connected.impact).toBe('generated')
    expect(connected.source).toContain('# flow comment')
    expect(connected.source).toContain('# keep task comment')
    expect(decode(connected.source).extension).toEqual({ untouched: true })
    expect(decode(connected.source).tasks[2]?.dependsOn).toEqual(['prepare', 'group'])

    const disconnected = disconnectVisualTasks(connected.source, schema, 'prepare', 'invoke')
    expect(decode(disconnected.source).tasks[2]?.dependsOn).toEqual(['group'])
    const configured = updateVisualTask(disconnected.source, task(graph, 'prepare'), [
      { key: 'value', value: 'changed' },
      { key: 'timeoutSeconds', value: 10 },
    ])
    expect(decode(configured.source).tasks[0]).toMatchObject({ value: 'changed', timeoutSeconds: 10 })
    expect(decode(configured.source).extension).toEqual({ untouched: true })
  })

  it('adds, reorders, groups and removes tasks with declared impact', () => {
    const destination = visualDestinations(buildVisualFlowGraph(source, schema))[0]
    const added = addVisualTask(source, schema, 'notify', 'core.log', destination)
    expect(added.impact).toBe('generated')
    expect(decode(added.source).tasks[3]).toMatchObject({ id: 'notify', type: 'core.log', message: '' })

    let graph = buildVisualFlowGraph(added.source, schema)
    const reordered = reorderVisualTask(added.source, task(graph, 'notify'), -1)
    expect(decode(reordered.source).tasks[2]?.id).toBe('notify')

    graph = buildVisualFlowGraph(reordered.source, schema)
    const groupDestination = visualDestinations(graph).find((item) => item.id === 'task:group')!
    const moved = moveVisualTask(reordered.source, schema, task(graph, 'notify'), groupDestination)
    expect(decode(moved.source).tasks[1]?.tasks?.at(-1)?.id).toBe('notify')

    graph = buildVisualFlowGraph(moved.source, schema)
    const removed = removeVisualTask(moved.source, schema, task(graph, 'prepare'))
    expect(removed.impact).toBe('lossy')
    expect(decode(removed.source).tasks.find((item) => item.id === 'invoke')?.dependsOn).toBeUndefined()
  })

  it('builds a 500-task graph within the local large-graph budget', () => {
    const tasks = Array.from({ length: 500 }, (_, index) => ({
      id: `task_${String(index)}`,
      type: 'core.return',
      ...(index ? { dependsOn: [`task_${String(index - 1)}`] } : {}),
      value: index,
    }))
    const largeSource = `id: large\nnamespace: tests\ntasks:\n${tasks.map((task) => `  - id: ${task.id}\n    type: ${task.type}\n${task.dependsOn ? `    dependsOn: [${task.dependsOn[0]}]\n` : ''}    value: ${String(task.value)}`).join('\n')}\n`
    const started = performance.now()
    const graph = buildVisualFlowGraph(largeSource, schema)
    expect(graph.nodes).toHaveLength(500)
    expect(graph.edges).toHaveLength(499)
    expect(performance.now() - started).toBeLessThan(1000)
  })
})
