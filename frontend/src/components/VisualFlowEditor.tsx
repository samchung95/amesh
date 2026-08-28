import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Connection,
  type Edge,
  type Node,
  type NodeProps,
} from '@xyflow/react'
import {
  ArrowDown,
  ArrowUp,
  Braces,
  GitBranch,
  Group,
  Plus,
  ShieldAlert,
  Trash2,
  Unplug,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import type { FlowEditorSchema, JsonSchema } from '../api/types'
import {
  addVisualTask,
  buildVisualFlowGraph,
  connectVisualTasks,
  disconnectVisualTasks,
  GROUP_TASK_TYPES,
  moveVisualTask,
  removeVisualTask,
  reorderVisualTask,
  updateVisualTask,
  validateVisualConnection,
  visualDestinations,
  type VisualFieldChange,
  type VisualFlowGraph,
  type VisualMutation,
  type VisualTaskNode,
} from './visualFlowModel'

type CanvasNodeData = {
  task: VisualTaskNode
}
type CanvasNode = Node<CanvasNodeData, 'task'>

interface VisualFlowEditorProps {
  source: string
  schema: FlowEditorSchema
  onChange: (source: string) => void
  onOpenCode: () => void
}

const TOPOLOGY_SCHEMAS: Record<string, JsonSchema> = {
  description: { type: 'string', title: 'Description' },
  runIf: { type: 'string', title: 'Run condition', description: 'Expression evaluated before this task runs.' },
  condition: { type: 'string', title: 'Branch / loop condition' },
  retry: { type: 'object', title: 'Retry policy' },
  timeoutSeconds: { type: 'number', title: 'Timeout (seconds)' },
  concurrency: { type: 'array', title: 'Concurrency rules' },
  failurePolicy: { type: 'string', title: 'Failure policy', enum: ['FAIL_FAST', 'CONTINUE_ON_ERROR', 'COLLECT_ALL'] },
  maxConcurrency: { type: 'integer', title: 'Maximum concurrency' },
}

const NESTED_FIELDS = new Set(['tasks', 'then', 'else', 'elseIf', 'cases', 'predicateCases', 'errors'])

function topologyFields(task: VisualTaskNode): string[] {
  const fields = ['description', 'runIf', 'retry', 'timeoutSeconds', 'concurrency']
  if (['core.if', 'core.while', 'core.until'].includes(task.taskType)) fields.push('condition')
  if (GROUP_TASK_TYPES.has(task.taskType)) fields.push('failurePolicy', 'maxConcurrency')
  return fields
}

function schemaFields(task: VisualTaskNode): Array<{ key: string; schema: JsonSchema }> {
  const properties = task.resource?.configurationSchema.properties || {}
  const ordered = task.resource?.editor.propertyOrder || []
  const keys = [
    ...ordered,
    ...Object.keys(properties).filter((key) => !ordered.includes(key)),
    ...topologyFields(task),
  ]
  return [...new Set(keys)]
    .filter((key) => !NESTED_FIELDS.has(key))
    .map((key) => ({ key, schema: properties[key] || TOPOLOGY_SCHEMAS[key] || {} }))
}

function fieldType(schema: JsonSchema): string | undefined {
  if (typeof schema.type === 'string') return schema.type
  return schema.type?.find((candidate) => candidate !== 'null')
}

function editorValue(value: unknown, schema: JsonSchema): string {
  if (value === undefined || value === null) return ''
  const type = fieldType(schema)
  if (type === 'object' || type === 'array' || type === undefined) return JSON.stringify(value, null, 2)
  return displayValue(value)
}

function displayValue(value: unknown): string {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value) || ''
}

function parseEditorValue(value: string, schema: JsonSchema, required: boolean): unknown {
  if (!value.trim() && !required) return undefined
  const type = fieldType(schema)
  if (type === 'integer') {
    const parsed = Number(value)
    if (!Number.isInteger(parsed)) throw new Error('Enter a whole number.')
    return parsed
  }
  if (type === 'number') {
    const parsed = Number(value)
    if (!Number.isFinite(parsed)) throw new Error('Enter a number.')
    return parsed
  }
  if (type === 'boolean') return value === 'true'
  if (type === 'object' || type === 'array' || type === undefined) {
    try {
      return JSON.parse(value) as unknown
    } catch {
      throw new Error('Enter valid JSON for this structured field.')
    }
  }
  return value
}

function taskBadges(task: VisualTaskNode): string[] {
  const badges: string[] = []
  if (task.lifecycle !== 'MAIN') badges.push(task.lifecycle.replace('_', ' '))
  if (task.raw.runIf || task.raw.condition) badges.push('CONDITION')
  if (task.raw.retry) badges.push('RETRY')
  if (typeof task.raw.timeoutSeconds === 'number' || typeof task.raw.timeoutSeconds === 'string') badges.push(`${task.raw.timeoutSeconds}S TIMEOUT`)
  if (task.raw.concurrency || task.raw.maxConcurrency) badges.push('CONCURRENCY')
  if (task.taskType === 'core.subflow') badges.push('SUBFLOW')
  if (task.codeOnlyFields.length) badges.push('CODE ONLY')
  return badges
}

function TaskCanvasNode({ data, selected }: NodeProps<CanvasNode>) {
  const { task } = data
  const subflow = task.taskType === 'core.subflow'
    ? [task.raw.namespace, task.raw.flowId].filter((part) => typeof part === 'string').join('.')
    : null
  return (
    <article className={`visual-task-node${selected ? ' visual-task-node-selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      <div className="visual-task-node-heading">
        <span>{task.category}</span>
        <code>{task.taskType}</code>
      </div>
      <strong>{task.taskId}</strong>
      <small>{task.title}{subflow ? ` · ${subflow}` : ''}</small>
      <div className="visual-task-badges">
        {taskBadges(task).map((badge) => <span key={badge}>{badge}</span>)}
      </div>
      <Handle type="source" position={Position.Right} />
    </article>
  )
}

const nodeTypes = { task: TaskCanvasNode }

function rankNodes(graph: VisualFlowGraph): Map<string, number> {
  const ranks = new Map<string, number>()
  const visiting = new Set<string>()
  const byId = new Map(graph.nodes.map((node) => [node.taskId, node]))
  const rank = (taskId: string): number => {
    const known = ranks.get(taskId)
    if (known !== undefined) return known
    if (visiting.has(taskId)) return 0
    visiting.add(taskId)
    const task = byId.get(taskId)
    const value = task?.dependencies.length
      ? 1 + Math.max(...task.dependencies.map((dependency) => rank(dependency)))
      : 0
    visiting.delete(taskId)
    ranks.set(taskId, value)
    return value
  }
  graph.nodes.forEach((node) => rank(node.taskId))
  return ranks
}

function canvasElements(graph: VisualFlowGraph): { nodes: CanvasNode[]; edges: Edge[] } {
  const ranks = rankNodes(graph)
  const groupRows = new Map<string, number>()
  let nextGroupRow = 0
  const nodes = graph.nodes.map((task, index): CanvasNode => {
    if (!groupRows.has(task.collectionKey)) groupRows.set(task.collectionKey, nextGroupRow++)
    const row = groupRows.get(task.collectionKey) || 0
    return {
      id: task.taskId,
      type: 'task',
      data: { task },
      position: {
        x: (ranks.get(task.taskId) || 0) * 310 + (task.parentId ? 36 : 0),
        y: row * 50 + index * 145,
      },
      ariaLabel: `${task.taskId}, ${task.taskType}, ${task.collectionLabel}`,
    }
  })
  const edges = graph.edges
    .filter((edge) => graph.nodes.some((node) => node.taskId === edge.source))
    .map((edge): Edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.kind === 'dependsOn' ? undefined : edge.kind,
      deletable: edge.kind === 'dependsOn',
      selectable: edge.kind === 'dependsOn',
      animated: edge.kind === 'dependsOn',
      markerEnd: edge.kind === 'dependsOn' ? { type: MarkerType.ArrowClosed } : undefined,
      className: `visual-edge-${edge.kind.toLowerCase()}`,
    }))
  return { nodes, edges }
}

function TaskConfigurationForm({
  task,
  onStage,
  onOpenCode,
}: {
  task: VisualTaskNode
  onStage: (changes: VisualFieldChange[]) => void
  onOpenCode: () => void
}) {
  const fields = useMemo(() => schemaFields(task), [task])
  const required = new Set(task.resource?.configurationSchema.required || [])
  const [draft, setDraft] = useState<Record<string, string>>(() => Object.fromEntries(
    fields.map((field) => [field.key, editorValue(task.raw[field.key], field.schema)]),
  ))
  const [error, setError] = useState<string | null>(null)

  const apply = () => {
    try {
      const changes: VisualFieldChange[] = []
      fields.forEach((field) => {
        const value = parseEditorValue(draft[field.key] || '', field.schema, required.has(field.key))
        if (value === undefined && task.raw[field.key] !== undefined) changes.push({ key: field.key, remove: true })
        else if (value !== undefined && JSON.stringify(value) !== JSON.stringify(task.raw[field.key])) {
          changes.push({ key: field.key, value })
        }
      })
      if (!changes.length) throw new Error('No configuration fields changed.')
      onStage(changes)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Configuration could not be staged.')
    }
  }

  return (
    <form className="visual-config-form" onSubmit={(event) => { event.preventDefault(); apply() }}>
      <div className="visual-inspector-heading">
        <div><span>SELECTED TASK</span><strong>{task.taskId}</strong></div>
        <code>{task.taskType}</code>
      </div>
      {task.codeOnlyFields.length ? (
        <div className="visual-code-fallback" role="note">
          <ShieldAlert size={16} aria-hidden="true" />
          <p><strong>Code editing required</strong><span>{task.codeOnlyFields.join(', ')}</span></p>
          <button className="button button-quiet" type="button" onClick={onOpenCode}>Open YAML</button>
        </div>
      ) : null}
      <div className="visual-schema-fields">
        {fields.map(({ key, schema }) => {
          const type = fieldType(schema)
          const value = draft[key] || ''
          const label = schema.title || key
          const fieldId = `visual-field-${task.taskId}-${key}`
          return (
            <label className="editor-field" key={key} htmlFor={fieldId}>
              {label}{required.has(key) ? ' *' : ''}
              {schema.enum ? (
                <select id={fieldId} value={value} onChange={(event) => setDraft((current) => ({ ...current, [key]: event.target.value }))}>
                  {!required.has(key) ? <option value="">Not set</option> : null}
                  {schema.enum.map((option) => <option key={displayValue(option)} value={displayValue(option)}>{displayValue(option)}</option>)}
                </select>
              ) : type === 'boolean' ? (
                <select id={fieldId} value={value} onChange={(event) => setDraft((current) => ({ ...current, [key]: event.target.value }))}>
                  <option value="">Not set</option><option value="true">True</option><option value="false">False</option>
                </select>
              ) : type === 'object' || type === 'array' || type === undefined ? (
                <textarea id={fieldId} value={value} placeholder={type === 'array' ? '[]' : '{}'} onChange={(event) => setDraft((current) => ({ ...current, [key]: event.target.value }))} />
              ) : (
                <input id={fieldId} type={type === 'number' || type === 'integer' ? 'number' : 'text'} value={value} onChange={(event) => setDraft((current) => ({ ...current, [key]: event.target.value }))} />
              )}
              {schema.description ? <small>{schema.description}</small> : null}
            </label>
          )
        })}
      </div>
      {error ? <p className="field-error" role="alert">{error}</p> : null}
      <button className="button button-primary button-wide" type="submit"><Braces size={16} aria-hidden="true" />Stage configuration</button>
    </form>
  )
}

export function VisualFlowEditor({ source, schema, onChange, onOpenCode }: VisualFlowEditorProps) {
  const parsed = useMemo(() => {
    try {
      return { graph: buildVisualFlowGraph(source, schema), error: null }
    } catch (cause) {
      return { graph: null, error: cause instanceof Error ? cause.message : 'The YAML cannot be shown visually.' }
    }
  }, [schema, source])
  const graph = parsed.graph
  const canvas = useMemo(() => graph ? canvasElements(graph) : { nodes: [], edges: [] }, [graph])
  const destinations = useMemo(() => graph ? visualDestinations(graph) : [], [graph])
  const resources = useMemo(
    () => schema.resourceCatalog.resources.filter((resource) => resource.kind === 'task'),
    [schema],
  )
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [pending, setPending] = useState<VisualMutation | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [taskId, setTaskId] = useState('new_task')
  const [taskType, setTaskType] = useState(resources[0]?.type || '')
  const [destinationId, setDestinationId] = useState('flow:tasks')
  const [moveDestinationId, setMoveDestinationId] = useState('flow:tasks')
  const selected = graph?.nodes.find((node) => node.taskId === selectedId) || null

  const stage = (factory: (currentSource: string) => VisualMutation) => {
    try {
      setPending(factory(source))
      setError(null)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'The visual edit could not be staged.')
    }
  }
  if (!graph) return (
    <div className="visual-fallback" role="alert">
      <ShieldAlert size={28} aria-hidden="true" />
      <div><strong>Visual model unavailable</strong><p>{parsed.error}</p></div>
      <button className="button button-primary" type="button" onClick={onOpenCode}>Fix in YAML</button>
    </div>
  )

  const onConnect = (connection: Connection) => {
    if (!connection.source || !connection.target) return
    stage((current) => connectVisualTasks(current, schema, connection.source, connection.target))
  }
  const destination = destinations.find((item) => item.id === destinationId) || destinations[0]
  const moveDestination = destinations.find((item) => item.id === moveDestinationId) || destinations[0]

  return (
    <div className="visual-editor-shell">
      <div className="visual-editor-toolbar">
        <label>Task ID<input value={taskId} onChange={(event) => setTaskId(event.target.value)} /></label>
        <label>Task type<select value={taskType} onChange={(event) => setTaskType(event.target.value)}>{resources.map((resource) => <option key={resource.type} value={resource.type}>{resource.editor.title} · {resource.type}</option>)}</select></label>
        <label>Group<select value={destinationId} onChange={(event) => setDestinationId(event.target.value)}>{destinations.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label>
        <button className="button button-primary" type="button" disabled={!destination || Boolean(pending)} onClick={() => destination && stage((current) => addVisualTask(current, schema, taskId, taskType, destination))}><Plus size={16} aria-hidden="true" />Add task</button>
      </div>
      {graph.issues.length ? <div className="visual-graph-issues" role="alert"><ShieldAlert size={16} aria-hidden="true" /><span>{graph.issues.map((issue) => issue.message).join(' ')}</span><button className="button button-quiet" type="button" onClick={onOpenCode}>Open YAML</button></div> : null}
      {error ? <p className="resource-failure" role="alert">{error}</p> : null}
      {pending ? (
        <section className={`visual-change-review visual-change-${pending.impact}`} aria-label="Generated YAML change review">
          <div><span>{pending.impact === 'lossy' ? 'LOSSY TRANSFORMATION' : 'GENERATED YAML'}</span><strong>{pending.summary}</strong>{pending.details.map((detail) => <small key={detail}>{detail}</small>)}</div>
          <details><summary>Review YAML</summary><pre>{pending.source}</pre></details>
          <div className="visual-review-actions"><button className="button button-secondary" type="button" onClick={() => setPending(null)}>Cancel</button><button className="button button-primary" type="button" onClick={() => { onChange(pending.source); setPending(null) }}>Accept change</button></div>
        </section>
      ) : null}
      <div className="visual-editor-layout">
        <section className="visual-canvas" aria-label="Interactive workflow topology">
          <ReactFlow<CanvasNode, Edge>
            key={source}
            defaultNodes={canvas.nodes}
            defaultEdges={canvas.edges}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.15}
            maxZoom={2}
            nodesFocusable
            edgesFocusable
            autoPanOnNodeFocus
            deleteKeyCode={pending ? null : ['Backspace', 'Delete']}
            isValidConnection={(connection) => Boolean(connection.source && connection.target && !validateVisualConnection(graph, connection.source, connection.target))}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedId(node.id)}
            onPaneClick={() => setSelectedId(null)}
            onBeforeDelete={({ nodes, edges }) => {
              const task = nodes[0]?.data.task
              if (task) stage((current) => removeVisualTask(current, schema, task))
              else {
                const edge = edges.find((candidate) => candidate.id.startsWith('dependsOn:'))
                if (edge) stage((current) => disconnectVisualTasks(current, schema, edge.source, edge.target))
              }
              return Promise.resolve(false)
            }}
            aria-label="Workflow task and dependency graph"
          >
            <MiniMap pannable zoomable ariaLabel="Workflow mini map" />
            <Controls />
            <Background variant={BackgroundVariant.Dots} gap={18} size={1} />
          </ReactFlow>
        </section>
        <aside className="visual-inspector" aria-label="Visual task inspector">
          {selected ? (
            <>
              <TaskConfigurationForm key={`${selected.taskId}:${JSON.stringify(selected.raw)}`} task={selected} onStage={(changes) => stage((current) => updateVisualTask(current, selected, changes))} onOpenCode={onOpenCode} />
              <section className="visual-structure-actions" aria-labelledby="structure-heading">
                <div className="visual-inspector-heading"><div><span>STRUCTURE</span><strong id="structure-heading">Position and group</strong></div><GitBranch size={17} aria-hidden="true" /></div>
                <div className="visual-inline-actions">
                  <button className="button button-secondary" type="button" disabled={selected.index === 0 || Boolean(pending)} onClick={() => stage((current) => reorderVisualTask(current, selected, -1))}><ArrowUp size={15} aria-hidden="true" />Up</button>
                  <button className="button button-secondary" type="button" disabled={Boolean(pending)} onClick={() => stage((current) => reorderVisualTask(current, selected, 1))}><ArrowDown size={15} aria-hidden="true" />Down</button>
                </div>
                <label className="editor-field">Move to group<select value={moveDestinationId} onChange={(event) => setMoveDestinationId(event.target.value)}>{destinations.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label>
                <button className="button button-secondary button-wide" type="button" disabled={!moveDestination || Boolean(pending)} onClick={() => moveDestination && stage((current) => moveVisualTask(current, schema, selected, moveDestination))}><Group size={15} aria-hidden="true" />Stage move</button>
                <button className="button button-danger button-wide" type="button" disabled={Boolean(pending)} onClick={() => stage((current) => removeVisualTask(current, schema, selected))}><Trash2 size={15} aria-hidden="true" />Stage removal</button>
                {selected.dependencies.map((dependency) => <button className="button button-quiet button-wide" key={dependency} type="button" disabled={Boolean(pending)} onClick={() => stage((current) => disconnectVisualTasks(current, schema, dependency, selected.taskId))}><Unplug size={14} aria-hidden="true" />Disconnect {dependency}</button>)}
              </section>
            </>
          ) : <div className="visual-empty-inspector"><GitBranch size={28} aria-hidden="true" /><strong>Select a task</strong><p>Configure it, move it, or drag between handles to add a dependency.</p></div>}
        </aside>
      </div>
      <p className="visual-keyboard-help">Keyboard: Tab through nodes and edges, Enter to select, arrows to move, Delete to stage removal. Use controls or the mini map to navigate large graphs.</p>
    </div>
  )
}
