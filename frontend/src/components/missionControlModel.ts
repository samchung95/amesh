import type { AdmissionDiagnostics, ExecutionDetail, ExecutionState, HumanTask, PersistedExecution, PersistedTaskRun, WorkerInventory } from '../api/types'

export interface MissionControlFilters {
  namespace: string
  flowId: string
  states: ExecutionState[]
}

export interface MissionRunRow {
  execution: PersistedExecution
  currentTask: PersistedTaskRun | null
  progress: number | null
  workerGroup: string | null
  explanation: string
  elapsedMs: number
  attention: boolean
  attentionKind: 'failed' | 'retrying' | 'paused' | 'overdue' | 'approval' | null
}

export interface MissionAttentionItem {
  key: string
  executionId: string | null
  state: string
  title: string
  explanation: string
  taskRunId: string | null
}

export interface MissionControlModel {
  counts: {
    running: number
    queued: number
    retrying: number
    paused: number
    waitingApproval: number
    failedRecently: number
    completedRecently: number
  }
  running: MissionRunRow[]
  attention: MissionAttentionItem[]
}

const ACTIVE_STATES: ExecutionState[] = ['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'RESTARTING']
const COMPLETED_STATES: ExecutionState[] = ['SUCCESS', 'WARNING', 'CANCELLED']

function currentTask(detail: ExecutionDetail | undefined): PersistedTaskRun | null {
  if (!detail?.taskRuns.length) return null
  const priorities: PersistedTaskRun['state'][] = ['FAILED', 'RETRY_DELAY', 'RUNNING', 'WAITING', 'CANCELLED', 'SUCCESS']
  return [...detail.taskRuns].sort((left, right) => priorities.indexOf(left.state) - priorities.indexOf(right.state))[0] || null
}

function workerGroup(task: PersistedTaskRun | null): string | null {
  if (!task) return null
  const direct = task.evidence.workerGroup
  if (typeof direct === 'string') return direct
  const runner = task.evidence.runner
  if (runner && typeof runner === 'object') {
    const candidate = (runner as Record<string, unknown>).workerGroup
    if (typeof candidate === 'string') return candidate
  }
  return null
}

function taskExplanation(execution: PersistedExecution, task: PersistedTaskRun | null): string {
  if (execution.state === 'QUEUED' || execution.state === 'CREATED') return 'Waiting for available capacity and admission checks.'
  if (execution.state === 'PAUSED') return 'Paused; resume or inspect the recorded intervention before work continues.'
  if (execution.state === 'RESTARTING' || task?.state === 'RETRY_DELAY') return task?.retry_at ? `${task.task_id} will retry at ${task.retry_at}.` : `${task?.task_id || 'The current step'} is waiting to retry.`
  if (execution.state === 'FAILED' || task?.state === 'FAILED') return task?.failure_category ? `${task.task_id} failed: ${task.failure_category}.` : `${task?.task_id || 'The run'} failed. Open the trace for recorded evidence.`
  if (task?.state === 'RUNNING') return `${task.task_id} is running${workerGroup(task) ? ` on ${workerGroup(task)}` : ''}.`
  if (task?.state === 'WAITING') return `${task.task_id} is waiting for its prerequisite or external decision.`
  return `${execution.flow_id} is ${execution.state.toLowerCase().replaceAll('_', ' ')}.`
}

function rowFor(execution: PersistedExecution, detail: ExecutionDetail | undefined, nowMs: number): MissionRunRow {
  const task = currentTask(detail)
  const summary = detail?.taskRunSummary
  const completed = summary ? summary.succeeded + summary.failed + summary.cancelled : 0
  const overdue = Boolean(execution.timeout_at && new Date(execution.timeout_at).getTime() < nowMs)
  const attentionKind = execution.state === 'FAILED' || task?.state === 'FAILED'
    ? 'failed'
    : execution.state === 'RESTARTING' || task?.state === 'RETRY_DELAY'
      ? 'retrying'
      : execution.state === 'PAUSED'
        ? 'paused'
        : overdue
          ? 'overdue'
          : null
  const terminal = ['SUCCESS', 'WARNING', 'FAILED', 'CANCELLED'].includes(execution.state)
  return {
    execution,
    currentTask: task,
    progress: summary?.total ? completed / summary.total : null,
    workerGroup: workerGroup(task),
    explanation: overdue ? `The configured deadline passed at ${execution.timeout_at!}.` : taskExplanation(execution, task),
    elapsedMs: Math.max(0, (terminal ? new Date(execution.updated_at).getTime() : nowMs) - new Date(execution.created_at).getTime()),
    attention: attentionKind !== null,
    attentionKind,
  }
}

function matches(execution: PersistedExecution, filters: MissionControlFilters): boolean {
  return (!filters.namespace || execution.namespace === filters.namespace)
    && (!filters.flowId || execution.flow_id === filters.flowId)
    && (!filters.states.length || filters.states.includes(execution.state))
}

function attentionRank(item: MissionAttentionItem): number {
  if (item.key.startsWith('approval:')) return 0
  if (['RETRY_DELAY', 'RESTARTING', 'OVERDUE'].includes(item.state)) return 1
  if (item.state === 'FAILED') return 2
  if (item.state === 'PAUSED') return 3
  if (item.state === 'DEGRADED') return 4
  return 5
}

export function missionControlModel({
  executions,
  details,
  humanTasks,
  workers,
  admission,
  filters,
  nowMs,
}: {
  executions: PersistedExecution[]
  details: Record<string, ExecutionDetail | undefined>
  humanTasks: HumanTask[]
  workers: WorkerInventory[]
  admission?: AdmissionDiagnostics
  filters: MissionControlFilters
  nowMs: number
}): MissionControlModel {
  const visible = executions.filter((execution) => matches(execution, filters))
  const openHumanTasks = humanTasks.filter((task) => ['OPEN', 'ESCALATED'].includes(task.state) && visible.some((execution) => execution.execution_id === task.executionId))
  const rows = visible.map((execution) => rowFor(execution, details[execution.execution_id], nowMs))
  const running = rows.filter((row) => ACTIVE_STATES.includes(row.execution.state))
  const attention: MissionAttentionItem[] = rows.filter((row) => row.attention).map((row) => ({
    key: `${row.attentionKind}:${row.execution.execution_id}`,
    executionId: row.execution.execution_id,
    state: row.attentionKind === 'overdue' ? 'OVERDUE' : row.execution.state,
    title: `${row.execution.flow_id} · ${row.currentTask?.task_id || 'run'}`,
    explanation: row.explanation,
    taskRunId: row.currentTask?.task_run_id || null,
  }))
  for (const task of openHumanTasks) {
    attention.push({ key: `approval:${task.humanTaskId}`, executionId: task.executionId, state: 'WAITING', title: task.title, explanation: `Approval or input is required before ${task.taskRunId} can continue.`, taskRunId: task.taskRunId })
  }
  for (const worker of workers.filter((item) => item.liveness !== 'LIVE' || item.compatibility !== 'COMPATIBLE')) {
    attention.push({ key: `worker:${worker.worker_id}`, executionId: null, state: 'DEGRADED', title: `${worker.instance_name} · ${worker.worker_group}`, explanation: `Worker is ${worker.liveness.toLowerCase()} and ${worker.compatibility.toLowerCase()}.`, taskRunId: null })
  }
  if (admission?.queued_requests) {
    attention.push({ key: 'admission:queue', executionId: null, state: 'QUEUED', title: `${String(admission.queued_requests)} admission requests queued`, explanation: `The oldest request has waited ${admission.oldest_queue_age_seconds.toFixed(1)} seconds.`, taskRunId: null })
  }
  attention.sort((left, right) => attentionRank(left) - attentionRank(right))
  return {
    counts: {
      running: visible.filter((item) => item.state === 'RUNNING').length,
      queued: visible.filter((item) => ['CREATED', 'QUEUED'].includes(item.state)).length,
      retrying: rows.filter((row) => row.execution.state === 'RESTARTING' || row.currentTask?.state === 'RETRY_DELAY').length,
      paused: visible.filter((item) => item.state === 'PAUSED').length,
      waitingApproval: openHumanTasks.length,
      failedRecently: visible.filter((item) => item.state === 'FAILED').length,
      completedRecently: visible.filter((item) => COMPLETED_STATES.includes(item.state)).length,
    },
    running,
    attention,
  }
}
