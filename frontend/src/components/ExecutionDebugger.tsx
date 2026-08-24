import {
  Activity,
  AlertTriangle,
  BarChart3,
  Box,
  Braces,
  ChevronLeft,
  ChevronRight,
  CircleStop,
  Clock3,
  Download,
  GitBranch,
  History,
  ListFilter,
  ListTree,
  Pause,
  Play,
  RefreshCcw,
  RotateCcw,
  ScrollText,
  Workflow,
  X,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import type {
  BackfillPreview,
  BackfillRecord,
  BackfillSpec,
  ExecutionArtifact,
  ExecutionDetail,
  ExecutionEvidenceEvent,
  ExecutionInterventionAction,
  ExecutionInterventionPreview,
  ExecutionInterventionRecord,
  FlowGraph,
  HumanTask,
  PersistedSubflow,
} from '../api/types'
import { compactId, formatDate, formatNumber } from '../app/format'
import {
  buildGanttAttempts,
  executionDurationMs,
  filterLogs,
  LARGE_GRAPH_THRESHOLD,
  logsFromEvidence,
  permittedActions,
  stateHistory,
  TASK_RUN_PAGE_SIZE,
  type DebugView,
  type LogFilters,
} from './executionDebugModel'
import { FlowGraphView } from './FlowGraphView'
import { SimpleExecutionTrace } from './SimpleExecutionTrace'
import { StatusBadge } from './StatusBadge'

const views: Array<{ id: DebugView; label: string; icon: typeof Workflow }> = [
  { id: 'trace', label: 'Simple trace', icon: ListTree },
  { id: 'topology', label: 'Topology', icon: Workflow },
  { id: 'gantt', label: 'Gantt', icon: BarChart3 },
  { id: 'logs', label: 'Logs', icon: ScrollText },
  { id: 'data', label: 'Data', icon: Braces },
  { id: 'history', label: 'History', icon: History },
]

type Confirmation =
  | { kind: 'intervention'; preview: ExecutionInterventionPreview }
  | { kind: 'backfill'; label: 'Replay' | 'Backfill'; spec: BackfillSpec; preview: BackfillPreview }

interface Props {
  detail: ExecutionDetail
  graph: FlowGraph | undefined
  graphLoading: boolean
  evidence: ExecutionEvidenceEvent[]
  streamState: 'connecting' | 'live' | 'reconnecting' | 'complete'
  artifacts: ExecutionArtifact[]
  subflows: PersistedSubflow[]
  parent: PersistedSubflow | null
  interventions: ExecutionInterventionRecord[]
  humanTasks: HumanTask[]
  locale: string
  timezone: string
  canManage: boolean
  canExecute: boolean
  busy: boolean
  onPreviewIntervention: (action: ExecutionInterventionAction, checkpoint?: string) => Promise<ExecutionInterventionPreview>
  onApplyIntervention: (preview: ExecutionInterventionPreview, reason: string) => Promise<void>
  onPreviewBackfill: (spec: BackfillSpec) => Promise<BackfillPreview>
  onCreateBackfill: (spec: BackfillSpec) => Promise<BackfillRecord>
  onDownloadArtifact: (artifact: ExecutionArtifact) => Promise<void>
}

function duration(value: number): string {
  if (value < 1_000) return `${String(Math.round(value))} ms`
  if (value < 60_000) return `${(value / 1_000).toFixed(1)} s`
  if (value < 3_600_000) return `${Math.floor(value / 60_000)}m ${Math.round(value % 60_000 / 1_000)}s`
  return `${Math.floor(value / 3_600_000)}h ${Math.round(value % 3_600_000 / 60_000)}m`
}

function json(value: unknown): string {
  return JSON.stringify(value ?? null, null, 2)
}

function inputDateTime(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toISOString().slice(0, 16)
}

function eventActor(event: ExecutionEvidenceEvent): string {
  return scalarText(event.payload.actorId, 'actor unavailable for legacy evidence')
}

function scalarText(value: unknown, fallback: string): string {
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
    ? String(value)
    : fallback
}

export function ExecutionDebugger({
  detail,
  graph,
  graphLoading,
  evidence,
  streamState,
  artifacts,
  subflows,
  parent,
  interventions,
  humanTasks,
  locale,
  timezone,
  canManage,
  canExecute,
  busy,
  onPreviewIntervention,
  onApplyIntervention,
  onPreviewBackfill,
  onCreateBackfill,
  onDownloadArtifact,
}: Props) {
  const { execution, taskRuns, taskRunSummary } = detail
  const [searchParams, setSearchParams] = useSearchParams()
  const requestedView = searchParams.get('view') as DebugView | null
  const view = views.some((item) => item.id === requestedView) ? requestedView! : 'trace'
  const selectedTask = searchParams.get('task') || ''
  const selectedStep = searchParams.get('step') || ''
  const offset = Math.max(0, Number(searchParams.get('offset') || detail.taskRunOffset || 0))
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null)
  const [reason, setReason] = useState('Operator requested this execution action')
  const [actionError, setActionError] = useState('')
  const [actionResult, setActionResult] = useState('')
  const [backfillOpen, setBackfillOpen] = useState(false)
  const [backfillStart, setBackfillStart] = useState(inputDateTime(execution.created_at))
  const [backfillEnd, setBackfillEnd] = useState(inputDateTime(execution.updated_at))
  const [backfillInterval, setBackfillInterval] = useState(3_600)

  const updateParams = (changes: Record<string, string | null>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(changes).forEach(([key, value]) => value ? next.set(key, value) : next.delete(key))
    setSearchParams(next)
  }
  const filters: LogFilters = {
    task: searchParams.get('task') || '',
    attempt: searchParams.get('attempt') || '',
    level: searchParams.get('level') || '',
    worker: searchParams.get('worker') || '',
    from: searchParams.get('from') || '',
    to: searchParams.get('to') || '',
    text: searchParams.get('q') || '',
  }
  const logs = useMemo(() => logsFromEvidence(evidence, taskRuns), [evidence, taskRuns])
  const filteredLogs = filterLogs(logs, filters)
  const gantt = useMemo(
    () => buildGanttAttempts(execution, selectedTask ? taskRuns.filter((task) => task.task_id === selectedTask) : taskRuns, evidence),
    [evidence, execution, selectedTask, taskRuns],
  )
  const executionHistory = useMemo(() => stateHistory(evidence), [evidence])
  const taskNames = [...new Set(logs.map((log) => log.taskId))].sort()
  const levels = [...new Set(logs.map((log) => log.level))].sort()
  const workers = [...new Set(logs.map((log) => log.worker))].sort()
  const metrics = evidence.filter((event) => event.kind === 'METRIC')
  const outputs = evidence.filter((event) => event.kind === 'OUTPUT')
  const errors = taskRuns.filter((task) => task.failure_category || task.state === 'FAILED')
  const summary = taskRunSummary ?? {
    total: taskRuns.length,
    waiting: taskRuns.filter((task) => task.state === 'WAITING').length,
    running: taskRuns.filter((task) => task.state === 'RUNNING').length,
    retry_delay: taskRuns.filter((task) => task.state === 'RETRY_DELAY').length,
    succeeded: taskRuns.filter((task) => task.state === 'SUCCESS').length,
    failed: taskRuns.filter((task) => task.state === 'FAILED').length,
    cancelled: taskRuns.filter((task) => task.state === 'CANCELLED').length,
  }

  const baseBackfill = (selection: BackfillSpec['selection']): BackfillSpec => ({
    namespace: execution.namespace,
    flowId: execution.flow_id,
    flowRevision: execution.flow_revision,
    selection,
    inputs: execution.inputs,
    labels: {},
    maxConcurrency: 1,
    ratePerMinute: 60,
    priority: 0,
  })
  const openIntervention = async (action: ExecutionInterventionAction) => {
    setActionError('')
    try {
      setConfirmation({ kind: 'intervention', preview: await onPreviewIntervention(action, action === 'RESTART' ? selectedTask || undefined : undefined) })
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'Unable to preview action')
    }
  }
  const openReplay = async () => {
    setActionError('')
    const spec = baseBackfill({ sourceExecutionIds: [execution.execution_id] })
    try {
      setConfirmation({ kind: 'backfill', label: 'Replay', spec, preview: await onPreviewBackfill(spec) })
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'Unable to preview replay')
    }
  }
  const openBackfill = async () => {
    setActionError('')
    const spec = baseBackfill({
      timeRange: {
        start: new Date(backfillStart).toISOString(),
        end: new Date(backfillEnd).toISOString(),
        intervalSeconds: backfillInterval,
      },
    })
    try {
      setConfirmation({ kind: 'backfill', label: 'Backfill', spec, preview: await onPreviewBackfill(spec) })
      setBackfillOpen(false)
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'Unable to preview backfill')
    }
  }
  const confirmAction = async () => {
    if (!confirmation) return
    setActionError('')
    try {
      if (confirmation.kind === 'intervention') {
        await onApplyIntervention(confirmation.preview, reason)
        setActionResult(`${confirmation.preview.action.replaceAll('_', ' ').toLocaleLowerCase()} accepted`)
      } else {
        const created = await onCreateBackfill(confirmation.spec)
        setActionResult(`${confirmation.label} ${compactId(created.backfillId)} created with ${String(created.total)} item(s)`)
      }
      setConfirmation(null)
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'Action failed')
    }
  }

  return (
    <div className="execution-debugger">
      <section className="execution-summary" aria-label="Execution summary">
        <div className="detail-facts">
          <div><Workflow size={17} aria-hidden="true" /><span><small>Revision</small><strong>{execution.flow_id} · r{execution.flow_revision}</strong></span></div>
          <div><Clock3 size={17} aria-hidden="true" /><span><small>Duration</small><strong>{duration(executionDurationMs(execution))}</strong></span></div>
          <div><Braces size={17} aria-hidden="true" /><span><small>Epoch / version</small><strong>{execution.epoch} / {execution.version}</strong></span></div>
          <div><Activity size={17} aria-hidden="true" /><span><small>Evidence stream</small><strong className={`stream-${streamState}`}>{streamState}</strong></span></div>
        </div>
        <div className="execution-meta-grid">
          <div><small>Created</small><strong>{formatDate(execution.created_at, locale, timezone)}</strong></div>
          <div><small>Created by</small><strong>{execution.created_by}</strong></div>
          <div><small>Trigger</small><code>{scalarText(execution.trigger.type ?? execution.trigger.source, 'manual')}</code></div>
          <div><small>Labels</small><code>{Object.entries(execution.labels).map(([key, value]) => `${key}=${value}`).join(', ') || 'None'}</code></div>
        </div>
        {(parent || subflows.length) ? <div className="relationship-strip" aria-label="Parent and child executions">
          <GitBranch size={16} aria-hidden="true" />
          {parent ? <Link to={`/executions/${parent.parent_execution_id}`}>Parent {compactId(parent.parent_execution_id)}</Link> : <span>No parent</span>}
          {subflows.map((child) => <Link key={child.relationship_id} to={`/executions/${child.child_execution_id}`}>Child {child.child_flow_id} · {child.mode}</Link>)}
        </div> : null}
      </section>

      {(canManage || canExecute) ? <section className="execution-actions" aria-labelledby="execution-actions-title">
        <div><p className="eyebrow">CONTROL PLANE</p><h2 id="execution-actions-title">Execution actions</h2></div>
        <div className="action-buttons">
          {canManage ? permittedActions(execution.state).map(({ label, action }) => {
            const Icon = action === 'PAUSE' ? Pause : action === 'RESUME' ? Play : action === 'RESTART' ? RotateCcw : CircleStop
            return <button key={action} className="button button-secondary" type="button" disabled={busy} onClick={() => void openIntervention(action)}><Icon size={15} aria-hidden="true" />{label}</button>
          }) : null}
          {canExecute ? <button className="button button-secondary" type="button" disabled={busy} onClick={() => void openReplay()}><RefreshCcw size={15} aria-hidden="true" />Replay</button> : null}
          {canExecute ? <button className="button button-secondary" type="button" disabled={busy} onClick={() => setBackfillOpen(true)}><History size={15} aria-hidden="true" />Backfill</button> : null}
        </div>
        {actionError ? <p className="form-error" role="alert">{actionError}</p> : null}
        {actionResult ? <p className="form-success" role="status">{actionResult}</p> : null}
      </section> : null}

      <section className="task-aggregate" aria-label="Task run aggregation">
        <div><small>Total task runs</small><strong>{formatNumber(summary.total, locale)}</strong></div>
        <div><small>Active</small><strong>{formatNumber(summary.running + summary.retry_delay, locale)}</strong></div>
        <div><small>Succeeded</small><strong>{formatNumber(summary.succeeded, locale)}</strong></div>
        <div><small>Failed / cancelled</small><strong>{formatNumber(summary.failed + summary.cancelled, locale)}</strong></div>
      </section>

      <div className="debug-navigation">
        <button className="trace-view-button" type="button" aria-current={view === 'trace' ? 'page' : undefined} onClick={() => updateParams({ view: null })}><ListTree size={16} aria-hidden="true" />Simple trace</button>
        <details className="advanced-evidence" open={view !== 'trace'}>
          <summary>Advanced evidence <small>Topology, timing, raw logs, data and audit history</small></summary>
          <nav className="debug-tabs" aria-label="Advanced execution evidence">
            {views.filter(({ id }) => id !== 'trace').map(({ id, label, icon: Icon }) => <button key={id} type="button" aria-current={view === id ? 'page' : undefined} onClick={() => updateParams({ view: id })}><Icon size={15} aria-hidden="true" />{label}</button>)}
          </nav>
        </details>
      </div>

      {view === 'trace' ? <SimpleExecutionTrace
        execution={execution}
        taskRuns={taskRuns}
        evidence={evidence}
        graph={graph}
        subflows={subflows}
        humanTasks={humanTasks}
        interventions={interventions}
        selectedStep={selectedStep}
        locale={locale}
        timezone={timezone}
        nowMs={Math.max(Date.parse(execution.updated_at), ...evidence.map((event) => Date.parse(event.occurred_at)).filter(Number.isFinite))}
        onSelectStep={(step) => updateParams({ step: step || null })}
      /> : null}

      {view === 'topology' ? <div className="debug-view">
        {summary.total > LARGE_GRAPH_THRESHOLD ? <section className="data-section aggregate-notice"><Box size={20} aria-hidden="true" /><div><h2>Aggregated topology</h2><p>{formatNumber(summary.total, locale)} task runs exceed the {formatNumber(LARGE_GRAPH_THRESHOLD, locale)}-node interactive canvas threshold. Use the bounded task pages and Gantt filters below.</p></div></section> : null}
        {graphLoading ? <p className="inline-empty">Loading interactive topology…</p> : null}
        {graph ? <FlowGraphView graph={graph} selectedTaskId={selectedTask} onSelectTask={(task) => updateParams({ task: task || null })} /> : null}
        <section className="data-section" aria-labelledby="task-runs-title">
          <div className="section-heading"><div><p className="eyebrow">BOUNDED PAGE</p><h2 id="task-runs-title">Task runs</h2></div><span>{offset + 1}–{Math.min(offset + taskRuns.length, summary.total)} of {formatNumber(summary.total, locale)}</span></div>
          <div className="task-run-table" role="list">
            {taskRuns.map((task) => <button key={task.task_run_id} type="button" role="listitem" className={selectedTask === task.task_id ? 'selected' : ''} onClick={() => updateParams({ task: selectedTask === task.task_id ? null : task.task_id })}>
              <span><strong>{task.task_id}</strong><small>{compactId(task.task_run_id)} · attempt {task.current_attempt} · {task.lifecycle_phase.toLocaleLowerCase().replaceAll('_', ' ')}</small></span>
              <StatusBadge state={task.state} />
            </button>)}
          </div>
          <div className="pager" aria-label="Task run pages">
            <button className="button button-secondary" type="button" disabled={offset === 0} onClick={() => updateParams({ offset: String(Math.max(0, offset - TASK_RUN_PAGE_SIZE)), task: null })}><ChevronLeft size={15} aria-hidden="true" />Previous</button>
            <button className="button button-secondary" type="button" disabled={offset + taskRuns.length >= summary.total} onClick={() => updateParams({ offset: String(offset + TASK_RUN_PAGE_SIZE), task: null })}>Next<ChevronRight size={15} aria-hidden="true" /></button>
          </div>
        </section>
      </div> : null}

      {view === 'gantt' ? <section className="data-section gantt-section" aria-labelledby="gantt-title">
        <div className="section-heading"><div><p className="eyebrow">ATTEMPT TIMING</p><h2 id="gantt-title">Queue, wait and runner Gantt</h2></div><span>{gantt.length} attempts on this bounded page</span></div>
        {gantt.length === 0 ? <p className="inline-empty">No task timing evidence is available.</p> : <div className="gantt-table" role="table" aria-label="Task attempt timings">
          <div className="gantt-header" role="row"><span role="columnheader">Task / attempt</span><span role="columnheader">Timeline</span><span role="columnheader">Timing</span></div>
          {gantt.slice(0, 500).map((attempt) => <button key={attempt.id} type="button" role="row" className={selectedTask === attempt.taskId ? 'selected' : ''} onClick={() => updateParams({ task: selectedTask === attempt.taskId ? null : attempt.taskId })}>
            <span role="cell"><strong>{attempt.taskId}</strong><small>attempt {attempt.attempt} · {attempt.worker}</small></span>
            <span role="cell" className="gantt-track"><i style={{ left: `${attempt.leftPercent}%`, width: `${attempt.widthPercent}%` }} /><em>{attempt.state}</em></span>
            <span role="cell"><small>queue {duration(attempt.queueMs)} · wait {duration(attempt.waitMs)} · runner {duration(attempt.runnerMs)}</small></span>
          </button>)}
        </div>}
      </section> : null}

      {view === 'logs' ? <section className="data-section logs-section" aria-labelledby="logs-title">
        <div className="section-heading"><div><p className="eyebrow">LIVE STREAM</p><h2 id="logs-title">Execution logs</h2></div><span>{filteredLogs.length} of {logs.length} buffered · {streamState}</span></div>
        <div className="log-filters">
          <label><span>Task</span><select value={filters.task} onChange={(event) => updateParams({ task: event.target.value || null })}><option value="">All tasks</option>{taskNames.map((task) => <option key={task}>{task}</option>)}</select></label>
          <label><span>Attempt</span><input type="number" min="1" value={filters.attempt} onChange={(event) => updateParams({ attempt: event.target.value || null })} /></label>
          <label><span>Level</span><select value={filters.level} onChange={(event) => updateParams({ level: event.target.value || null })}><option value="">All levels</option>{levels.map((level) => <option key={level}>{level}</option>)}</select></label>
          <label><span>Worker</span><select value={filters.worker} onChange={(event) => updateParams({ worker: event.target.value || null })}><option value="">All workers</option>{workers.map((worker) => <option key={worker}>{worker}</option>)}</select></label>
          <label><span>From</span><input type="datetime-local" value={filters.from} onChange={(event) => updateParams({ from: event.target.value || null })} /></label>
          <label><span>To</span><input type="datetime-local" value={filters.to} onChange={(event) => updateParams({ to: event.target.value || null })} /></label>
          <label className="log-text-filter"><span>Text</span><input type="search" placeholder="Message or structured fields" value={filters.text} onChange={(event) => updateParams({ q: event.target.value || null })} /></label>
          <button className="button button-secondary" type="button" onClick={() => updateParams({ task: null, attempt: null, level: null, worker: null, from: null, to: null, q: null })}><ListFilter size={15} aria-hidden="true" />Clear</button>
        </div>
        {filteredLogs.length === 0 ? <p className="inline-empty">No buffered logs match these filters.</p> : <ol className="log-stream" aria-live="polite">
          {filteredLogs.slice(-300).map((log) => <li key={log.id}><time>{formatDate(log.occurredAt, locale, timezone)}</time><strong className={`log-${log.level.toLocaleLowerCase()}`}>{log.level}</strong><code>{log.taskId}#{log.attempt}</code><span>{log.worker}</span><p>{log.text}</p></li>)}
        </ol>}
      </section> : null}

      {view === 'data' ? <div className="debug-data-grid">
        <section className="data-section"><p className="eyebrow">RENDERED CONTRACT</p><h2>Inputs and flow outputs</h2><p className="redaction-note">Sensitive values are redacted by the server before this view is rendered.</p><h3>Inputs</h3><pre>{json(execution.inputs)}</pre><h3>Outputs</h3><pre>{json(execution.outputs)}</pre></section>
        <section className="data-section"><p className="eyebrow">TASK OUTPUTS</p><h2>Selected results and cache</h2>{taskRuns.filter((task) => !selectedTask || task.task_id === selectedTask).map((task) => <details key={task.task_run_id}><summary>{task.task_id} · attempt {task.current_attempt}</summary><pre>{json(task.result)}</pre>{task.evidence.cache ? <><h3>Cache decision</h3><pre>{json(task.evidence.cache)}</pre></> : null}</details>)}</section>
        <section className="data-section"><p className="eyebrow">METRICS</p><h2>{metrics.length} buffered metrics</h2>{metrics.length ? metrics.map((metric) => <article key={metric.event_id} className="evidence-data-row"><strong>{scalarText(metric.payload.name, metric.event_type)}</strong><span>{scalarText(metric.payload.value, '—')} {scalarText(metric.payload.unit, '')}</span><small>{formatDate(metric.occurred_at, locale, timezone)}</small></article>) : <p className="inline-empty">No metrics recorded.</p>}</section>
        <section className="data-section"><p className="eyebrow">ARTIFACTS</p><h2>{artifacts.length} files</h2>{artifacts.length ? artifacts.map((artifact) => <article key={artifact.artifact_id} className="artifact-row"><span><strong>{artifact.logical_path || artifact.uri}</strong><small>{formatNumber(artifact.size_bytes, locale)} bytes · attempt {artifact.attempt}</small></span><button className="button button-secondary" type="button" onClick={() => void onDownloadArtifact(artifact)}><Download size={14} aria-hidden="true" />Download</button></article>) : <p className="inline-empty">No artifacts recorded.</p>}</section>
        <section className="data-section"><p className="eyebrow">ERRORS</p><h2>{errors.length} failed task runs</h2>{errors.length ? errors.map((task) => <article key={task.task_run_id} className="error-row"><AlertTriangle size={16} aria-hidden="true" /><span><strong>{task.task_id} · {task.failure_category || 'FAILED'}</strong><pre>{json(task.result)}</pre></span></article>) : <p className="inline-empty">No task errors on this page.</p>}</section>
        <section className="data-section"><p className="eyebrow">DURABLE OUTPUT EVIDENCE</p><h2>{outputs.length} committed outputs</h2>{outputs.slice(-100).map((output) => <details key={output.event_id}><summary>{compactId(output.task_run_id || execution.execution_id)} · {formatDate(output.occurred_at, locale, timezone)}</summary><pre>{json(output.payload)}</pre></details>)}</section>
      </div> : null}

      {view === 'history' ? <section className="data-section history-section" aria-labelledby="history-title">
        <div className="section-heading"><div><p className="eyebrow">CAUSE AND ACTOR</p><h2 id="history-title">Execution state history</h2></div><span>{executionHistory.length} transitions</span></div>
        <ol className="state-history">
          {executionHistory.map((event) => <li key={event.event_id}><span className="state-marker" /><div><strong>{scalarText(event.payload.eventType, event.event_type)}</strong><p>{scalarText(event.payload.reason, 'No reason recorded')}</p><small>{formatDate(event.occurred_at, locale, timezone)} · {eventActor(event)}</small>{event.payload.causationId ? <code>caused by {scalarText(event.payload.causationId, 'unknown event')}</code> : null}</div></li>)}
        </ol>
        <h3>Operator interventions</h3>
        {interventions.length ? <ol className="intervention-history">{interventions.map((item) => <li key={item.sequence}><StatusBadge state={item.action} /><span><strong>{item.event_type}</strong><small>{formatDate(item.occurred_at, locale, timezone)} · {item.actor_id} · {item.reason || 'No reason'}</small></span></li>)}</ol> : <p className="inline-empty">No operator interventions recorded.</p>}
      </section> : null}

      {backfillOpen ? <div className="modal-backdrop"><section className="confirmation-dialog" role="dialog" aria-modal="true" aria-labelledby="backfill-dialog-title">
        <button className="icon-button dialog-close" type="button" aria-label="Close backfill form" onClick={() => setBackfillOpen(false)}><X size={17} /></button>
        <p className="eyebrow">BACKFILL WINDOW</p><h2 id="backfill-dialog-title">Choose the execution window</h2>
        <div className="backfill-fields"><label><span>Start</span><input type="datetime-local" value={backfillStart} onChange={(event) => setBackfillStart(event.target.value)} /></label><label><span>End</span><input type="datetime-local" value={backfillEnd} onChange={(event) => setBackfillEnd(event.target.value)} /></label><label><span>Interval seconds</span><input type="number" min="1" value={backfillInterval} onChange={(event) => setBackfillInterval(Number(event.target.value))} /></label></div>
        <p>The server will calculate impact and cost before anything is created.</p>
        <div className="dialog-actions"><button className="button button-secondary" type="button" onClick={() => setBackfillOpen(false)}>Cancel</button><button className="button button-primary" type="button" disabled={!backfillStart || !backfillEnd || busy} onClick={() => void openBackfill()}>Preview impact</button></div>
      </section></div> : null}

      {confirmation ? <div className="modal-backdrop"><section className="confirmation-dialog" role="dialog" aria-modal="true" aria-labelledby="confirmation-dialog-title">
        <button className="icon-button dialog-close" type="button" aria-label="Close confirmation" onClick={() => setConfirmation(null)}><X size={17} /></button>
        <p className="eyebrow">IMPACT CONFIRMATION</p><h2 id="confirmation-dialog-title">Confirm {confirmation.kind === 'intervention' ? confirmation.preview.action.replaceAll('_', ' ').toLocaleLowerCase() : confirmation.label.toLocaleLowerCase()}</h2>
        {confirmation.kind === 'intervention' ? <>
          <p><strong>{confirmation.preview.current_state}</strong> → <strong>{confirmation.preview.predicted_state}</strong></p>
          <dl className="impact-grid"><div><dt>Impacted tasks</dt><dd>{confirmation.preview.impacted_task_ids.length}</dd></div><div><dt>Preserved tasks</dt><dd>{confirmation.preview.preserved_task_ids.length}</dd></div><div><dt>Invalidates claims</dt><dd>{confirmation.preview.invalidates_active_claims ? 'Yes' : 'No'}</dd></div><div><dt>Destructive</dt><dd>{confirmation.preview.destructive ? 'Yes' : 'No'}</dd></div></dl>
          {confirmation.preview.consequences.length ? <ul>{confirmation.preview.consequences.map((item) => <li key={item}>{item}</li>)}</ul> : null}
          <label><span>Reason</span><textarea rows={3} value={reason} onChange={(event) => setReason(event.target.value)} /></label>
        </> : <>
          <dl className="impact-grid"><div><dt>Executions</dt><dd>{confirmation.preview.executionCount}</dd></div><div><dt>Estimated task runs</dt><dd>{confirmation.preview.estimatedTaskRuns}</dd></div><div><dt>Cost units</dt><dd>{confirmation.preview.estimatedCostUnits}</dd></div><div><dt>Selection</dt><dd>{confirmation.preview.selectionKind}</dd></div></dl>
          {confirmation.preview.warnings.length ? <ul>{confirmation.preview.warnings.map((item) => <li key={item}>{item}</li>)}</ul> : null}
        </>}
        {actionError ? <p className="form-error" role="alert">{actionError}</p> : null}
        <div className="dialog-actions"><button className="button button-secondary" type="button" onClick={() => setConfirmation(null)}>Cancel</button><button className="button button-primary" type="button" disabled={busy || (confirmation.kind === 'intervention' && !reason.trim())} onClick={() => void confirmAction()}>Confirm action</button></div>
      </section></div> : null}
    </div>
  )
}
