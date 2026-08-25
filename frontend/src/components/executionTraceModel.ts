import type {
  ExecutionEvidenceEvent,
  ExecutionInterventionRecord,
  FlowGraph,
  HumanTask,
  PersistedSubflow,
  PersistedTaskRun,
} from '../api/types'

export const SIMPLE_TRACE_LIMIT = 500

export interface ExecutionTraceStep {
  id: string
  taskId: string
  label: string
  state: PersistedTaskRun['state']
  attempt: number
  lifecyclePhase: PersistedTaskRun['lifecycle_phase']
  iterationKey: string | null
  startedAt: string | null
  endedAt: string | null
  durationMs: number | null
  worker: string
  outcome: string
  context: string[]
  annotations: string[]
  childExecutions: PersistedSubflow[]
  nonSelected: boolean
}

export interface ExecutionTraceGroup {
  key: string
  label: string
  collapsible: boolean
  steps: ExecutionTraceStep[]
}

export interface ExecutionTraceModel {
  groups: ExecutionTraceGroup[]
  total: number
  hidden: number
  runAnnotations: string[]
}

function eventName(event: ExecutionEvidenceEvent): string {
  const name = event.payload.eventType
  return typeof name === 'string' ? name : event.event_type.split('.').at(-1) ?? event.event_type
}

function nestedPayload(event: ExecutionEvidenceEvent): Record<string, unknown> {
  const nested = event.payload.payload
  return typeof nested === 'object' && nested !== null ? nested as Record<string, unknown> : {}
}

function text(value: unknown): string | null {
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
    ? String(value)
    : null
}

function at(value: string): number {
  const parsed = Date.parse(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function terminalEvent(name: string): boolean {
  return ['TaskRunSucceeded', 'TaskRunFailed', 'TaskRunCancelled', 'TaskRunDeferred', 'TaskRunRetryScheduled'].includes(name)
}

function readableEvent(event: ExecutionEvidenceEvent): string | null {
  if (event.event_type.startsWith('agent.')) return readableAgentEvent(event)
  const name = eventName(event)
  if (/RetryScheduled/i.test(name)) return `Retry scheduled${text(event.payload.reason) ? `: ${text(event.payload.reason)}` : ''}`
  if (/Paused/i.test(name)) return `Paused${text(event.payload.reason) ? `: ${text(event.payload.reason)}` : ''}`
  if (/Cancel/i.test(name)) return `Cancellation: ${name.replaceAll(/([a-z])([A-Z])/g, '$1 $2')}`
  if (/Approval|HumanTask/i.test(name)) return `Approval: ${name.replaceAll(/([a-z])([A-Z])/g, '$1 $2')}`
  if (/Policy/i.test(name)) return `Policy: ${text(event.payload.reason) ?? name.replaceAll(/([a-z])([A-Z])/g, '$1 $2')}`
  if (/Branch|Condition/i.test(name)) return `Decision: ${text(event.payload.reason) ?? name.replaceAll(/([a-z])([A-Z])/g, '$1 $2')}`
  return null
}

function readableAgentEvent(event: ExecutionEvidenceEvent): string {
  const payload = nestedPayload(event)
  const turn = text(payload.turn)
  const counters = typeof payload.counters === 'object' && payload.counters !== null
    ? payload.counters as Record<string, unknown>
    : {}
  const budget = text(counters.totalTokens)
    ? `${text(counters.totalTokens)} tokens · $${text(counters.costUsd) ?? '0'}`
    : null
  if (event.event_type === 'agent.session.started') {
    const digest = text(payload.envelopeDigest)
    const recalled = Array.isArray(payload.memoryReads) ? payload.memoryReads.length : 0
    return `Agent session started${digest ? ` · envelope ${digest.slice(0, 18)}…` : ''}${recalled ? ` · ${String(recalled)} memory entries recalled` : ''}`
  }
  if (event.event_type === 'agent.model.response') {
    return `Model turn ${turn ?? '?'} · proposed ${text(payload.action) ?? 'action'}${budget ? ` · ${budget}` : ''}`
  }
  if (event.event_type === 'agent.policy.authorized') {
    const approval = typeof payload.approval === 'object' && payload.approval !== null
      ? payload.approval as Record<string, unknown>
      : {}
    const approvalText = approval.required === true ? ` · approval ${text(approval.decision) ?? 'required'}` : ''
    return `Tool authorized: ${text(payload.tool) ?? 'unknown'} · ${text(payload.impact) ?? 'policy checked'}${approvalText}`
  }
  if (event.event_type === 'agent.tool.result') return `Tool completed: ${text(payload.tool) ?? 'unknown'} · call ${text(payload.toolCalls) ?? '?'}`
  if (event.event_type === 'agent.output.rejected') return `Output rejected${payload.repairScheduled === true ? ' · bounded repair scheduled' : ' · session stopped'}`
  if (event.event_type === 'agent.evaluation.completed') {
    const deterministic = typeof payload.deterministic === 'object' && payload.deterministic !== null
      ? payload.deterministic as Record<string, unknown>
      : {}
    const judge = typeof payload.judge === 'object' && payload.judge !== null
      ? payload.judge as Record<string, unknown>
      : null
    return `Evaluation ${text(payload.key) ?? 'unknown'} ${payload.passed === true ? 'passed' : 'failed'} · deterministic score ${text(deterministic.rubricScore) ?? '?'}${judge ? ` · judge ${text(judge.score) ?? '?'} ± ${text(judge.uncertainty) ?? '?'}` : ''}`
  }
  if (event.event_type === 'agent.release.approved') return `Human release approved · ${text(payload.approvalTask) ?? 'approval task'}`
  if (event.event_type === 'agent.memory.written') return `Memory written: ${text(payload.key) ?? 'unknown'} · ${text(payload.scope) ?? 'bounded scope'}`
  if (event.event_type === 'agent.output.accepted') return `Output accepted · schema valid · ${text(payload.businessAssertionsPassed) ?? '0'} business gates`
  if (event.event_type === 'agent.session.failed') return `Agent session failed: ${text(payload.error) ?? 'see task failure'}`
  return `Agent: ${event.event_type.slice('agent.'.length).replaceAll('.', ' ')}`
}

function workerFor(task: PersistedTaskRun, events: ExecutionEvidenceEvent[]): string {
  for (const event of [...events].reverse()) {
    const worker = text(event.payload.workerId) ?? text(nestedPayload(event).workerGroup)
    if (worker) return worker
  }
  return text(task.evidence.workerGroup) ?? text(task.evidence.runner) ?? 'unassigned'
}

function outcomeFor(task: PersistedTaskRun, approvals: HumanTask[]): string {
  if (task.result?.skipped === true) return `Not run: ${text(task.result.reason) ?? 'branch was not selected'}`
  if (task.state === 'FAILED') return task.failure_category ? `Failed: ${task.failure_category}` : 'Failed'
  if (task.state === 'RETRY_DELAY') return task.retry_at ? `Retry at ${task.retry_at}` : 'Waiting to retry'
  if (task.state === 'WAITING') {
    const approval = approvals.find((item) => ['OPEN', 'ESCALATED'].includes(item.state))
    return approval ? `Waiting for approval: ${approval.title}` : 'Waiting for a dependency or claim'
  }
  if (task.state === 'RUNNING') return 'Running now'
  if (task.state === 'CANCELLED') return 'Cancelled'
  const keys = Object.keys(task.result ?? {})
  return keys.length ? `Completed with ${keys.join(', ')}` : 'Completed'
}

function branchContext(task: PersistedTaskRun): { context: string[]; nonSelected: boolean } {
  const control = typeof task.evidence.control === 'object' && task.evidence.control !== null
    ? task.evidence.control as Record<string, unknown>
    : null
  if (!control) return { context: [], nonSelected: false }
  const branch = control.branch
  if (typeof branch === 'object' && branch !== null) {
    const selected = text((branch as Record<string, unknown>).selectedBranch)
    return { context: selected ? [`Selected path ${selected}`] : [], nonSelected: false }
  }
  const selected = text(control.selectedBranch)
  const path = text(branch)
  const nonSelected = task.current_attempt === 0 && Boolean(selected)
  return {
    context: nonSelected ? [`Path ${path ?? 'unknown'} not selected; chose ${selected!}`] : [],
    nonSelected,
  }
}

function taskTiming(events: ExecutionEvidenceEvent[], nowMs: number, active: boolean): {
  startedAt: string | null
  endedAt: string | null
  durationMs: number | null
} {
  const stateEvents = events.filter((event) => event.kind === 'STATE').sort((left, right) => left.cursor - right.cursor)
  const created = stateEvents.find((event) => eventName(event) === 'TaskRunCreated')
  const started = [...stateEvents].reverse().find((event) => eventName(event) === 'TaskRunStarted')
  const ended = [...stateEvents].reverse().find((event) => terminalEvent(eventName(event)))
  const start = started ?? created
  if (!start) return { startedAt: null, endedAt: ended?.occurred_at ?? null, durationMs: null }
  const endMs = ended ? at(ended.occurred_at) : active ? nowMs : at(start.occurred_at)
  return {
    startedAt: start.occurred_at,
    endedAt: ended?.occurred_at ?? null,
    durationMs: Math.max(0, endMs - at(start.occurred_at)),
  }
}

export function buildExecutionTrace({
  taskRuns,
  evidence,
  graph,
  subflows,
  humanTasks,
  interventions,
  nowMs,
  limit = SIMPLE_TRACE_LIMIT,
}: {
  taskRuns: PersistedTaskRun[]
  evidence: ExecutionEvidenceEvent[]
  graph?: FlowGraph
  subflows: PersistedSubflow[]
  humanTasks: HumanTask[]
  interventions: ExecutionInterventionRecord[]
  nowMs: number
  limit?: number
}): ExecutionTraceModel {
  const nodeByTask = new Map((graph?.nodes ?? []).map((node) => [node.taskId, node]))
  const orderByTask = new Map((graph?.nodes ?? []).map((node) => [node.taskId, node.order]))
  const eventsByRun = new Map<string, ExecutionEvidenceEvent[]>()
  evidence.filter((event) => event.task_run_id).forEach((event) => {
    const events = eventsByRun.get(event.task_run_id!) ?? []
    events.push(event)
    eventsByRun.set(event.task_run_id!, events)
  })
  const approvalsByRun = new Map<string, HumanTask[]>()
  humanTasks.forEach((approval) => {
    const approvals = approvalsByRun.get(approval.taskRunId) ?? []
    approvals.push(approval)
    approvalsByRun.set(approval.taskRunId, approvals)
  })
  const childrenByRun = new Map<string, PersistedSubflow[]>()
  subflows.forEach((child) => {
    const children = childrenByRun.get(child.parent_task_run_id) ?? []
    children.push(child)
    childrenByRun.set(child.parent_task_run_id, children)
  })

  const sorted = [...taskRuns].sort((left, right) => {
    const graphOrder = (orderByTask.get(left.task_id) ?? Number.MAX_SAFE_INTEGER) - (orderByTask.get(right.task_id) ?? Number.MAX_SAFE_INTEGER)
    if (graphOrder) return graphOrder
    const taskOrder = left.task_id.localeCompare(right.task_id, undefined, { numeric: true })
    if (taskOrder) return taskOrder
    const iterationOrder = (left.iteration_key ?? '').localeCompare(right.iteration_key ?? '', undefined, { numeric: true })
    if (iterationOrder) return iterationOrder
    return left.task_run_id.localeCompare(right.task_run_id)
  })
  const visible = sorted.slice(0, limit)
  const steps = visible.map((task): ExecutionTraceStep => {
    const taskEvents = (eventsByRun.get(task.task_run_id) ?? []).sort((left, right) => left.cursor - right.cursor)
    const approvals = approvalsByRun.get(task.task_run_id) ?? []
    const node = nodeByTask.get(task.task_id)
    const timing = taskTiming(taskEvents, nowMs, ['RUNNING', 'WAITING', 'RETRY_DELAY'].includes(task.state))
    const context: string[] = []
    const branch = branchContext(task)
    if (node?.dependencies.length) context.push(`After ${node.dependencies.join(', ')}`)
    if (node?.mode) context.push(`${node.mode.toLocaleLowerCase()} control`)
    if (node?.parentId) context.push(`Inside ${node.parentId}`)
    if (task.iteration_key) context.push(`Iteration ${task.iteration_key}`)
    context.push(...branch.context)
    const annotations = taskEvents.map(readableEvent).filter((item): item is string => Boolean(item))
    if (task.current_attempt > 1) annotations.unshift(`${String(task.current_attempt)} attempts`)
    if (task.lifecycle_phase !== 'MAIN') annotations.unshift(`${task.lifecycle_phase.replaceAll('_', ' ').toLocaleLowerCase()} handler`)
    approvals.forEach((approval) => annotations.push(`${approval.title}: ${approval.state.replaceAll('_', ' ').toLocaleLowerCase()}`))
    return {
      id: task.task_run_id,
      taskId: task.task_id,
      label: node?.label || task.task_id,
      state: task.state,
      attempt: task.current_attempt,
      lifecyclePhase: task.lifecycle_phase,
      iterationKey: task.iteration_key,
      ...timing,
      worker: workerFor(task, taskEvents),
      outcome: outcomeFor(task, approvals),
      context: [...new Set(context)],
      annotations: [...new Set(annotations)],
      childExecutions: childrenByRun.get(task.task_run_id) ?? [],
      nonSelected: branch.nonSelected,
    }
  })

  const counts = new Map<string, number>()
  const selectedSteps = steps.filter((step) => !step.nonSelected)
  const nonSelectedSteps = steps.filter((step) => step.nonSelected)
  selectedSteps.forEach((step) => counts.set(step.taskId, (counts.get(step.taskId) ?? 0) + 1))
  const groups: ExecutionTraceGroup[] = []
  selectedSteps.forEach((step) => {
    const node = nodeByTask.get(step.taskId)
    const collapsible = (counts.get(step.taskId) ?? 0) > 1 || ['FOREACH', 'WHILE', 'UNTIL'].includes(node?.mode ?? '')
    const key = collapsible ? `loop:${step.taskId}` : `step:${step.id}`
    const existing = groups.at(-1)
    if (existing?.key === key) existing.steps.push(step)
    else groups.push({ key, label: collapsible ? `${step.label} · ${String(counts.get(step.taskId) ?? 1)} iterations` : step.label, collapsible, steps: [step] })
  })
  if (nonSelectedSteps.length) groups.push({ key: 'branches:not-selected', label: `${String(nonSelectedSteps.length)} non-selected branch step${nonSelectedSteps.length === 1 ? '' : 's'}`, collapsible: true, steps: nonSelectedSteps })
  const runAnnotations = interventions.map((item) => `${item.action.replaceAll('_', ' ').toLocaleLowerCase()} by ${item.actor_id}${item.reason ? `: ${item.reason}` : ''}`)
  return { groups, total: sorted.length, hidden: Math.max(0, sorted.length - visible.length), runAnnotations }
}
