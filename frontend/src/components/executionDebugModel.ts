import type {
  ExecutionEvidenceEvent,
  ExecutionInterventionAction,
  PersistedExecution,
  PersistedTaskRun,
} from '../api/types'

export const TASK_RUN_PAGE_SIZE = 100
export const EVIDENCE_BUFFER_LIMIT = 5_000
export const LARGE_GRAPH_THRESHOLD = 1_000

export type DebugView = 'topology' | 'gantt' | 'logs' | 'data' | 'history'

export interface LogFilters {
  task: string
  attempt: string
  level: string
  worker: string
  from: string
  to: string
  text: string
}

export interface DebugLog {
  id: string
  taskId: string
  taskRunId: string | null
  attempt: number
  level: string
  worker: string
  occurredAt: string
  text: string
  event: ExecutionEvidenceEvent
}

export interface GanttAttempt {
  id: string
  taskId: string
  taskRunId: string
  attempt: number
  state: string
  queueMs: number
  waitMs: number
  runnerMs: number
  startedAt: string | null
  endedAt: string | null
  worker: string
  leftPercent: number
  widthPercent: number
}

const terminalTaskEvents = new Set([
  'TaskRunSucceeded',
  'TaskRunFailed',
  'TaskRunCancelled',
  'TaskRunDeferred',
  'TaskRunRetryScheduled',
])

function eventName(event: ExecutionEvidenceEvent): string {
  return scalarText(event.payload.eventType, event.event_type.split('.').at(-1) ?? event.event_type)
}

function scalarText(value: unknown, fallback: string): string {
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
    ? String(value)
    : fallback
}

function eventData(event: ExecutionEvidenceEvent): Record<string, unknown> {
  const nested = event.payload.payload
  return typeof nested === 'object' && nested !== null ? nested as Record<string, unknown> : {}
}

function timestamp(value: string): number {
  const parsed = Date.parse(value)
  return Number.isFinite(parsed) ? parsed : 0
}

export function mergeEvidence(
  current: ExecutionEvidenceEvent[],
  incoming: ExecutionEvidenceEvent[],
  limit = EVIDENCE_BUFFER_LIMIT,
): ExecutionEvidenceEvent[] {
  const byCursor = new Map(current.map((event) => [event.cursor, event]))
  incoming.forEach((event) => byCursor.set(event.cursor, event))
  return [...byCursor.values()]
    .sort((left, right) => left.cursor - right.cursor)
    .slice(-limit)
}

export function stateHistory(events: ExecutionEvidenceEvent[]): ExecutionEvidenceEvent[] {
  return events.filter((event) => event.kind === 'STATE' && event.payload.entity === 'execution')
}

export function executionDurationMs(execution: PersistedExecution, now = Date.now()): number {
  const start = timestamp(execution.created_at)
  const terminal = ['SUCCESS', 'FAILED', 'WARNING', 'CANCELLED'].includes(execution.state)
  const end = terminal ? timestamp(execution.updated_at) : now
  return Math.max(0, end - start)
}

export function logsFromEvidence(
  events: ExecutionEvidenceEvent[],
  taskRuns: PersistedTaskRun[],
): DebugLog[] {
  const taskByRun = new Map(taskRuns.map((task) => [task.task_run_id, task.task_id]))
  return events
    .filter((event) => event.kind === 'LOG')
    .map((event) => ({
      id: event.event_id,
      taskId: event.task_run_id ? taskByRun.get(event.task_run_id) ?? event.task_run_id : 'execution',
      taskRunId: event.task_run_id,
      attempt: Number(event.payload.attempt ?? 1),
      level: scalarText(event.payload.level, 'INFO'),
      worker: scalarText(event.payload.workerId, 'unassigned'),
      occurredAt: event.occurred_at,
      text: scalarText(event.payload.message, ''),
      event,
    }))
}

export function filterLogs(logs: DebugLog[], filters: LogFilters): DebugLog[] {
  const from = filters.from ? timestamp(filters.from) : Number.NEGATIVE_INFINITY
  const to = filters.to ? timestamp(filters.to) : Number.POSITIVE_INFINITY
  const text = filters.text.trim().toLocaleLowerCase()
  return logs.filter((log) => {
    const at = timestamp(log.occurredAt)
    return (!filters.task || log.taskId === filters.task)
      && (!filters.attempt || log.attempt === Number(filters.attempt))
      && (!filters.level || log.level === filters.level)
      && (!filters.worker || log.worker === filters.worker)
      && at >= from
      && at <= to
      && (!text || `${log.text} ${JSON.stringify(log.event.payload.fields ?? {})}`.toLocaleLowerCase().includes(text))
  })
}

export function buildGanttAttempts(
  execution: PersistedExecution,
  taskRuns: PersistedTaskRun[],
  events: ExecutionEvidenceEvent[],
  now = Date.now(),
): GanttAttempt[] {
  const startBound = timestamp(execution.created_at)
  const endBound = Math.max(startBound + 1, executionDurationMs(execution, now) + startBound)
  const span = endBound - startBound
  const eventsByRun = new Map<string, ExecutionEvidenceEvent[]>()
  events.filter((event) => event.kind === 'STATE' && event.task_run_id).forEach((event) => {
    const bucket = eventsByRun.get(event.task_run_id!) ?? []
    bucket.push(event)
    eventsByRun.set(event.task_run_id!, bucket)
  })
  const rows: GanttAttempt[] = []
  taskRuns.forEach((task) => {
    const taskEvents = (eventsByRun.get(task.task_run_id) ?? [])
      .sort((left, right) => timestamp(left.occurred_at) - timestamp(right.occurred_at))
    const created = taskEvents.find((event) => eventName(event) === 'TaskRunCreated')
    const starts = taskEvents.filter((event) => eventName(event) === 'TaskRunStarted')
    if (starts.length === 0) {
      const queuedAt = timestamp(created?.occurred_at ?? execution.created_at)
      rows.push({
        id: `${task.task_run_id}:queue`, taskId: task.task_id, taskRunId: task.task_run_id,
        attempt: Math.max(task.current_attempt, 0), state: task.state,
        queueMs: Math.max(0, endBound - queuedAt), waitMs: 0, runnerMs: 0,
        startedAt: null, endedAt: null, worker: 'unassigned',
        leftPercent: Math.max(0, (queuedAt - startBound) / span * 100),
        widthPercent: Math.max(.4, (endBound - queuedAt) / span * 100),
      })
      return
    }
    starts.forEach((started, index) => {
      const startedMs = timestamp(started.occurred_at)
      const nextStartedMs = starts[index + 1] ? timestamp(starts[index + 1].occurred_at) : Number.POSITIVE_INFINITY
      const ended = taskEvents.find((event) => {
        const at = timestamp(event.occurred_at)
        return at >= startedMs && at < nextStartedMs && terminalTaskEvents.has(eventName(event))
      })
      const endedMs = ended ? timestamp(ended.occurred_at) : endBound
      const previousRetry = [...taskEvents].reverse().find((event) => (
        timestamp(event.occurred_at) < startedMs && eventName(event) === 'TaskRunRetryScheduled'
      ))
      const queuedAt = index === 0 ? timestamp(created?.occurred_at ?? execution.created_at) : startedMs
      const waitAt = previousRetry ? timestamp(previousRetry.occurred_at) : startedMs
      const nested = eventData(started)
      rows.push({
        id: `${task.task_run_id}:${String(index + 1)}`,
        taskId: task.task_id,
        taskRunId: task.task_run_id,
        attempt: index + 1,
        state: ended ? eventName(ended).replace('TaskRun', '').toUpperCase() : task.state,
        queueMs: index === 0 ? Math.max(0, startedMs - queuedAt) : 0,
        waitMs: Math.max(0, startedMs - waitAt),
        runnerMs: Math.max(0, endedMs - startedMs),
        startedAt: started.occurred_at,
        endedAt: ended?.occurred_at ?? null,
        worker: scalarText(nested.workerGroup, 'unassigned'),
        leftPercent: Math.max(0, (startedMs - startBound) / span * 100),
        widthPercent: Math.max(.4, (endedMs - startedMs) / span * 100),
      })
    })
  })
  return rows
}

export function permittedActions(state: PersistedExecution['state']): Array<{
  label: string
  action: ExecutionInterventionAction
}> {
  if (state === 'RUNNING') return [
    { label: 'Pause', action: 'PAUSE' },
    { label: 'Cancel', action: 'REQUEST_CANCEL' },
  ]
  if (state === 'PAUSED') return [
    { label: 'Resume', action: 'RESUME' },
    { label: 'Cancel', action: 'REQUEST_CANCEL' },
  ]
  if (state === 'CANCELLING') return [{ label: 'Kill', action: 'FORCE_CANCEL' }]
  if (['SUCCESS', 'FAILED', 'WARNING', 'CANCELLED'].includes(state)) {
    return [{ label: 'Restart', action: 'RESTART' }]
  }
  return []
}
