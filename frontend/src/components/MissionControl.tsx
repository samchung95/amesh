import { AlertTriangle, CheckCircle2, Clock3, ListChecks, PauseCircle, PlayCircle, RefreshCw, RotateCcw, Timer, UserRoundCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { ExecutionState } from '../api/types'
import { compactId, formatDate } from '../app/format'
import { CatalogMultiSelect, CatalogSelect, type CatalogOption } from './CatalogSelect'
import { EmptyState, ErrorState, LoadingState } from './AsyncState'
import type { MissionControlFilters, MissionControlModel } from './missionControlModel'
import { StatusBadge } from './StatusBadge'

function elapsed(value: number): string {
  const seconds = Math.floor(value / 1_000)
  if (seconds < 60) return `${String(seconds)}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${String(minutes)}m ${String(seconds % 60)}s`
  const hours = Math.floor(minutes / 60)
  return `${String(hours)}h ${String(minutes % 60)}m`
}

const cards: Array<{ key: keyof MissionControlModel['counts']; label: string; detail: string; icon: typeof PlayCircle; states: ExecutionState[] }> = [
  { key: 'running', label: 'Running', detail: 'Working now', icon: PlayCircle, states: ['RUNNING'] },
  { key: 'queued', label: 'Queued', detail: 'Waiting to start', icon: Timer, states: ['CREATED', 'QUEUED'] },
  { key: 'retrying', label: 'Retrying', detail: 'Waiting to retry', icon: RotateCcw, states: ['RESTARTING'] },
  { key: 'paused', label: 'Paused', detail: 'Stopped intentionally', icon: PauseCircle, states: ['PAUSED'] },
  { key: 'waitingApproval', label: 'Waiting approval', detail: 'Human decision needed', icon: UserRoundCheck, states: [] },
  { key: 'failedRecently', label: 'Failed recently', detail: 'Needs diagnosis', icon: AlertTriangle, states: ['FAILED'] },
  { key: 'completedRecently', label: 'Completed recently', detail: 'Terminal outcomes', icon: CheckCircle2, states: ['SUCCESS', 'WARNING', 'CANCELLED'] },
]

export function MissionControl({
  model,
  filters,
  namespaceOptions,
  flowOptions,
  loading,
  error,
  partial,
  fetching,
  locale,
  timezone,
  tenant,
  onFiltersChange,
  onRefresh,
}: {
  model: MissionControlModel
  filters: MissionControlFilters
  namespaceOptions: CatalogOption[]
  flowOptions: CatalogOption[]
  loading: boolean
  error: string | null
  partial: boolean
  fetching: boolean
  locale: string
  timezone: string
  tenant: string
  onFiltersChange: (filters: MissionControlFilters) => void
  onRefresh: () => void
}) {
  const stateOptions = ['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'RESTARTING', 'SUCCESS', 'WARNING', 'FAILED', 'CANCELLED'].map((value) => ({ value, label: value.replaceAll('_', ' ') }))
  const visibleAttention = model.attention.slice(0, 12)
  return (
    <section className="mission-control" aria-labelledby="mission-control-heading">
      <header className="mission-heading">
        <div><p className="eyebrow">LIVE OPERATIONS</p><h2 id="mission-control-heading">What needs your attention</h2><p>{tenant} · {filters.namespace || 'all authorized namespaces'} · persisted execution evidence</p></div>
        <button className="button button-secondary" type="button" onClick={onRefresh} disabled={fetching}><RefreshCw className={fetching ? 'spin' : ''} size={16} aria-hidden="true" />{fetching ? 'Refreshing…' : 'Refresh now'}</button>
      </header>

      <div className="mission-status-grid" aria-label="Execution state summary">
        {cards.map(({ key, label, detail, icon: Icon, states }) => <button key={key} type="button" className={filters.states.length && filters.states.every((state) => states.includes(state)) ? 'selected' : ''} onClick={() => onFiltersChange({ ...filters, states })}><Icon size={17} aria-hidden="true" /><span><strong>{model.counts[key]}</strong><b>{label}</b><small>{detail}</small></span></button>)}
      </div>

      <form className="mission-filters" aria-label="Mission Control filters" onSubmit={(event) => event.preventDefault()}>
        <CatalogSelect label="Namespace" value={filters.namespace} options={namespaceOptions} onChange={(namespace) => onFiltersChange({ ...filters, namespace, flowId: '' })} emptyLabel="All namespaces" loading={loading} />
        <CatalogSelect label="Flow" value={filters.flowId} options={flowOptions} onChange={(flowId) => onFiltersChange({ ...filters, flowId })} emptyLabel="All flows" loading={loading} />
        <CatalogMultiSelect label="States" values={filters.states} options={stateOptions} onChange={(states) => onFiltersChange({ ...filters, states: states as ExecutionState[] })} />
        <button className="button button-quiet" type="button" onClick={() => onFiltersChange({ namespace: '', flowId: '', states: [] })}>Clear filters</button>
      </form>

      {loading ? <LoadingState label="Loading current work" /> : null}
      {error ? <ErrorState message={error} retry={onRefresh} /> : null}
      {partial ? <p className="mission-partial" role="status"><AlertTriangle size={15} aria-hidden="true" />Some step details are unavailable. Run state and links remain current.</p> : null}

      {!loading && !error ? <div className="mission-columns">
        <section className="mission-list" aria-labelledby="running-now-heading">
          <div className="section-heading"><div><p className="eyebrow">ACTIVE</p><h3 id="running-now-heading">Running now</h3></div><span>{model.running.length}</span></div>
          {model.running.length ? <ol>{model.running.map((row) => {
            const taskId = row.currentTask?.task_run_id
            const path = `/executions/${row.execution.execution_id}${taskId ? `?step=${encodeURIComponent(taskId)}` : ''}`
            return <li key={row.execution.execution_id}><Link to={path}><div className="mission-row-heading"><span><StatusBadge state={row.execution.state} /><strong>{row.execution.flow_id}</strong></span><code>{compactId(row.execution.execution_id)}</code></div><p>{row.explanation}</p><dl><div><dt>Namespace</dt><dd>{row.execution.namespace}</dd></div><div><dt>Current step</dt><dd>{row.currentTask?.task_id || 'Preparing run'}</dd></div><div><dt>Trigger</dt><dd>{row.trigger}</dd></div><div><dt>Elapsed</dt><dd>{elapsed(row.elapsedMs)}</dd></div><div><dt>Progress</dt><dd>{row.progress === null ? 'Collecting' : `${String(Math.round(row.progress * 100))}%`}</dd></div><div><dt>Runner</dt><dd>{row.workerGroup || 'Not assigned'}</dd></div><div><dt>Last change</dt><dd>{formatDate(row.execution.updated_at, locale, timezone)}</dd></div></dl><span className="mission-open">Open simple trace →</span></Link></li>
          })}</ol> : <EmptyState title="Nothing is running in this view" body="Clear filters or start a workflow. Failed and waiting work remains visible under Needs attention." />}
        </section>

        <section className="mission-list mission-attention" aria-labelledby="needs-attention-heading">
          <div className="section-heading"><div><p className="eyebrow">TRIAGE</p><h3 id="needs-attention-heading">Needs attention</h3></div><span>{model.attention.length}</span></div>
          {model.attention.length ? <><ol>{visibleAttention.map((item) => <li key={item.key}>
            {item.executionId ? <Link to={`/executions/${item.executionId}${item.taskRunId ? `?step=${encodeURIComponent(item.taskRunId)}` : ''}`}><div className="mission-row-heading"><span><StatusBadge state={item.state} /><strong>{item.title}</strong></span></div><p>{item.explanation}</p><span className="mission-open">Inspect the recorded cause →</span></Link> : <article><div className="mission-row-heading"><span><StatusBadge state={item.state} /><strong>{item.title}</strong></span></div><p>{item.explanation}</p></article>}
          </li>)}</ol>{model.attention.length > visibleAttention.length ? <p className="mission-more">Showing the {visibleAttention.length} highest-priority items of {model.attention.length}. <Link to="/executions">Open full execution history</Link></p> : null}</> : <EmptyState title="No items need attention" body="There are no failed, paused, retrying, overdue, approval-blocked or degraded items in this view." />}
        </section>
      </div> : null}
      <footer className="mission-footnote"><Clock3 size={14} aria-hidden="true" /><span>Counts reflect the current authorized execution page. Streaming evidence and the 15-second refresh keep persisted state current.</span><Link to="/executions">Open full execution history</Link><ListChecks size={14} aria-hidden="true" /></footer>
    </section>
  )
}
