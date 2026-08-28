import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { Clock3, Download, Plus, RefreshCw, Save, Share2, ShieldAlert, Trash2, X } from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'react-router-dom'

import type { DashboardDefinition, DashboardFilters, DashboardQueryResult, DashboardVisualization, ExecutionState, UiSession } from '../api/types'
import { formatDate, formatNumber } from '../app/format'
import { useApiClient, useExecutions, useFlows, useHumanTasks } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { CatalogMultiSelect, CatalogSelect, type CatalogOption } from '../components/CatalogSelect'
import { MissionControl } from '../components/MissionControl'
import { missionControlModel, type MissionControlFilters } from '../components/missionControlModel'
import {
  DASHBOARD_AGGREGATIONS,
  DASHBOARD_SOURCES,
  DASHBOARD_VISUALIZATIONS,
  buildDashboardSpec,
  dashboardFilters,
  displayValue,
  normalizedChartValues,
  rowLabel,
  type DashboardEditorDraft,
  type DashboardFilterDraft,
} from '../components/dashboardModel'

const INITIAL_EDITOR: DashboardEditorDraft = {
  dashboardId: 'ops.custom', title: 'Custom operations', description: '', visibility: 'PRIVATE',
  viewerIds: '', editorIds: '', widgetTitle: 'Execution states', source: 'EXECUTIONS',
  visualization: 'STATUS_BREAKDOWN', measure: 'COUNT', aggregation: 'COUNT', groupBy: 'state',
  limit: 100, timeoutMs: 1500, sampleRate: 1,
}

const EXECUTION_STATES: ExecutionState[] = ['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'RESTARTING', 'SUCCESS', 'WARNING', 'FAILED', 'CANCELLED']
const ACTIVE_STATES_FOR_DETAIL: ExecutionState[] = ['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'RESTARTING']
const DASHBOARD_DIMENSIONS: CatalogOption[] = [
  'state', 'namespace', 'flowId', 'workerGroup', 'level', 'logger', 'resourceType', 'outcome',
].map((value) => ({ value, label: value.replace(/([A-Z])/g, ' $1').replace(/^./, (letter) => letter.toUpperCase()) }))

function csvValues(value: string): string[] {
  return value.split(',').map((item) => item.trim()).filter(Boolean)
}

function WidgetVisual({ visualization, result, locale }: { visualization: DashboardVisualization; result: DashboardQueryResult; locale: string }) {
  if (result.redacted) return <div className="dashboard-redacted"><ShieldAlert size={20} aria-hidden="true" /><strong>Permission redacted</strong><span>You can view this dashboard definition, but not its underlying data.</span></div>
  if (!result.rows.length) return <p className="inline-empty">No data in this window.</p>
  if (visualization === 'COUNTER') return <strong className="dashboard-counter">{formatNumber(Number(result.rows[0].value || 0), locale)}</strong>
  if (visualization === 'TABLE') {
    return (
      <div className="table-scroll"><table className="data-table dashboard-table"><thead><tr>{result.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{result.rows.map((row, index) => <tr key={index}>{result.columns.map((column) => <td key={column}>{displayValue(row[column])}</td>)}</tr>)}</tbody></table></div>
    )
  }
  if (visualization === 'TIME_SERIES') {
    const values = normalizedChartValues(result.rows)
    const points = values.map((value, index) => `${values.length === 1 ? 50 : (index / (values.length - 1)) * 100},${92 - value * 82}`).join(' ')
    return (
      <div className="dashboard-series">
        <svg viewBox="0 0 100 100" role="img" aria-label="Time series chart"><polyline points={points} fill="none" vectorEffect="non-scaling-stroke" /></svg>
        <ol className="sr-only">{result.rows.map((row, index) => <li key={index}>{rowLabel(row)}: {String(row.value)}</li>)}</ol>
      </div>
    )
  }
  const values = normalizedChartValues(result.rows)
  return (
    <ol className="dashboard-bars">
      {result.rows.map((row, index) => <li key={index}><span>{rowLabel(row)}</span><i><b style={{ width: `${String(values[index] * 100)}%` }} /></i><strong>{formatNumber(Number(row.value || 0), locale)}</strong></li>)}
    </ol>
  )
}

function DashboardEditor({ initialFilters, principals, onClose, onSave, pending }: { initialFilters: DashboardFilters; principals: CatalogOption[]; onClose: () => void; onSave: (draft: DashboardEditorDraft) => void; pending: boolean }) {
  const [draft, setDraft] = useState(INITIAL_EDITOR)
  const [error, setError] = useState('')
  const update = <K extends keyof DashboardEditorDraft>(key: K, value: DashboardEditorDraft[K]) => setDraft((current) => ({ ...current, [key]: value }))
  const submit = (event: FormEvent) => {
    event.preventDefault()
    try {
      buildDashboardSpec(draft, initialFilters)
      setError('')
      onSave(draft)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Invalid dashboard definition')
    }
  }
  return (
    <div className="modal-backdrop" role="presentation">
      <form className="dashboard-editor" role="dialog" aria-modal="true" aria-labelledby="dashboard-editor-title" onSubmit={submit}>
        <header><div><p className="eyebrow">TYPED QUERY</p><h2 id="dashboard-editor-title">Create dashboard</h2></div><button className="icon-button" type="button" aria-label="Close dashboard editor" onClick={onClose}><X aria-hidden="true" /></button></header>
        {error ? <p className="form-error" role="alert">{error}</p> : null}
        <div className="dashboard-form-grid">
          <label>Dashboard ID<input value={draft.dashboardId} onChange={(event) => update('dashboardId', event.target.value)} /></label>
          <label>Title<input value={draft.title} onChange={(event) => update('title', event.target.value)} /></label>
          <label className="span-two">Description<textarea value={draft.description} onChange={(event) => update('description', event.target.value)} /></label>
          <label>Visibility<select value={draft.visibility} onChange={(event) => update('visibility', event.target.value as 'PRIVATE' | 'TENANT')}><option value="PRIVATE">Private</option><option value="TENANT">Tenant</option></select></label>
          <label>Widget title<input value={draft.widgetTitle} onChange={(event) => update('widgetTitle', event.target.value)} /></label>
          <label>Data source<select value={draft.source} onChange={(event) => update('source', event.target.value as DashboardEditorDraft['source'])}>{DASHBOARD_SOURCES.map((source) => <option key={source}>{source}</option>)}</select></label>
          <label>Visualization<select value={draft.visualization} onChange={(event) => update('visualization', event.target.value as DashboardEditorDraft['visualization'])}>{DASHBOARD_VISUALIZATIONS.map((item) => <option key={item}>{item}</option>)}</select></label>
          <label>Measure<select value={draft.measure} onChange={(event) => update('measure', event.target.value as DashboardEditorDraft['measure'])}><option>COUNT</option><option>DURATION_MS</option><option>VALUE</option></select></label>
          <label>Aggregation<select value={draft.aggregation} onChange={(event) => update('aggregation', event.target.value as DashboardEditorDraft['aggregation'])}>{DASHBOARD_AGGREGATIONS.map((item) => <option key={item}>{item}</option>)}</select></label>
          <CatalogMultiSelect label="Group dimensions" values={csvValues(draft.groupBy)} options={DASHBOARD_DIMENSIONS} onChange={(values) => update('groupBy', values.join(','))} className="catalog-multiselect span-two" />
          <label>Row limit<input type="number" min="1" max="500" value={draft.limit} onChange={(event) => update('limit', Number(event.target.value))} /></label>
          <label>Timeout (ms)<input type="number" min="100" max="5000" value={draft.timeoutMs} onChange={(event) => update('timeoutMs', Number(event.target.value))} /></label>
          <label>Sample rate<input type="number" min="0.01" max="1" step="0.01" value={draft.sampleRate} onChange={(event) => update('sampleRate', Number(event.target.value))} /></label>
          <CatalogMultiSelect label="Viewers" values={csvValues(draft.viewerIds)} options={principals} onChange={(values) => update('viewerIds', values.join(','))} />
          <CatalogMultiSelect label="Editors" values={csvValues(draft.editorIds)} options={principals} onChange={(values) => update('editorIds', values.join(','))} className="catalog-multiselect span-two" />
        </div>
        <footer><button className="button button-secondary" type="button" onClick={onClose}>Cancel</button><button className="button button-primary" type="submit" disabled={pending}><Save size={16} aria-hidden="true" />{pending ? 'Saving…' : 'Save dashboard'}</button></footer>
      </form>
    </div>
  )
}

export function DashboardPage({ session }: { session: UiSession }) {
  const { t } = useTranslation()
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedId = searchParams.get('dashboard') || 'builtin.instance'
  const initialDraft = useMemo<DashboardFilterDraft>(() => ({ hours: 24, namespace: settings.namespace || '', flowId: '', states: '', workerGroups: '', labels: '', dimensions: '' }), [settings.namespace])
  const [filterDraft, setFilterDraft] = useState(initialDraft)
  const [filters, setFilters] = useState<DashboardFilters>(() => dashboardFilters(initialDraft))
  const [showEditor, setShowEditor] = useState(false)
  const [notice, setNotice] = useState('')
  const executions = useExecutions(session.capabilities['executions.view'])
  const humanTasks = useHumanTasks(Boolean(session.capabilities['humanTasks.view']))
  const flows = useFlows(session.capabilities['flows.view'])
  const workers = useQuery({ queryKey: ['dashboard-workers', settings.tenant], queryFn: api.workers, enabled: session.capabilities['dashboards.view'], staleTime: 15_000 })
  const admission = useQuery({ queryKey: ['dashboard-admission', settings.tenant], queryFn: api.admissionDiagnostics, enabled: session.capabilities['dashboards.view'], refetchInterval: 15_000 })
  const principals = useQuery({ queryKey: ['dashboard-principals', settings.tenant], queryFn: api.principals, enabled: showEditor && session.capabilities['administration.manage'], staleTime: 15_000 })
  const definitions = useQuery({ queryKey: ['dashboards', settings.tenant], queryFn: api.dashboards, enabled: session.capabilities['dashboards.view'], staleTime: 15_000 })
  const rendered = useQuery({ queryKey: ['dashboard-render', settings.tenant, selectedId, filters], queryFn: () => api.renderDashboard(selectedId, filters), enabled: session.capabilities['dashboards.view'], refetchInterval: 15_000 })
  const selected = rendered.data?.dashboard || definitions.data?.find((item) => item.dashboardId === selectedId)
  const missionFilters: MissionControlFilters = {
    namespace: searchParams.get('mcNamespace') || '',
    flowId: searchParams.get('mcFlow') || '',
    states: (searchParams.get('mcState') || '').split(',').filter((state): state is ExecutionState => EXECUTION_STATES.includes(state as ExecutionState)),
  }
  const detailCandidates = (executions.data || []).filter((execution) => ACTIVE_STATES_FOR_DETAIL.includes(execution.state) || execution.state === 'FAILED').slice(0, 25)
  const detailQueries = useQueries({ queries: detailCandidates.map((execution) => ({
    queryKey: ['mission-execution', settings.tenant, execution.execution_id],
    queryFn: () => api.execution(execution.execution_id),
    refetchInterval: 15_000,
  })) })
  const missionDetails = Object.fromEntries(detailCandidates.map((execution, index) => [execution.execution_id, detailQueries[index]?.data]))
  const mission = missionControlModel({
    executions: executions.data || [],
    details: missionDetails,
    humanTasks: humanTasks.data || [],
    workers: workers.data || [],
    admission: admission.data,
    filters: missionFilters,
    nowMs: executions.dataUpdatedAt,
  })
  const namespaceOptions = Array.from(new Set((flows.data || []).map((flow) => flow.namespace))).sort().map((namespace) => ({ value: namespace, label: namespace }))
  const flowOptions = (flows.data || []).filter((flow) => !filterDraft.namespace || flow.namespace === filterDraft.namespace).map((flow) => ({ value: flow.flow_id, label: `${flow.flow_id} · ${flow.namespace}` }))
  const missionFlowOptions = (flows.data || []).filter((flow) => !missionFilters.namespace || flow.namespace === missionFilters.namespace).map((flow) => ({ value: flow.flow_id, label: `${flow.flow_id} · ${flow.namespace}` }))
  const workerGroupOptions = Array.from(new Set((workers.data || []).map((worker) => worker.worker_group))).sort().map((group) => ({ value: group, label: group }))
  const principalOptions = Array.from(new Map([
    [session.principalId, { value: session.principalId, label: `${session.display} · ${session.principalId.slice(0, 8)}` }],
    ...(principals.data || []).map((principal) => [principal.id, { value: principal.id, label: `${principal.display_name} · ${principal.handle}` }] as const),
  ]).values())
  const save = useMutation({
    mutationFn: (draft: DashboardEditorDraft) => api.saveDashboard(draft.dashboardId, buildDashboardSpec(draft, filters)),
    onSuccess: async (definition) => { await queryClient.invalidateQueries({ queryKey: ['dashboards'] }); setSearchParams({ dashboard: definition.dashboardId }); setShowEditor(false); setNotice('Dashboard saved.') },
  })
  const remove = useMutation({
    mutationFn: (definition: DashboardDefinition) => api.deleteDashboard(definition.dashboardId, definition.version),
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['dashboards'] }); setSearchParams({ dashboard: 'builtin.instance' }); setNotice('Dashboard deleted.') },
  })
  const applyFilters = (event: FormEvent) => {
    event.preventDefault()
    try { setFilters(dashboardFilters(filterDraft)); setNotice('Filters applied.') } catch (caught) { setNotice(caught instanceof Error ? caught.message : 'Invalid filters') }
  }
  const share = async () => {
    const url = new URL(window.location.href)
    url.searchParams.set('dashboard', selectedId)
    await navigator.clipboard.writeText(url.toString())
    setNotice('Share link copied.')
  }
  const exportDefinition = async () => {
    const blob = await api.exportDashboard(selectedId)
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url; anchor.download = `${selectedId}.yaml`; anchor.click(); URL.revokeObjectURL(url)
    setNotice('Dashboard YAML exported.')
  }
  const updateMissionFilters = (nextFilters: MissionControlFilters) => {
    const next = new URLSearchParams(searchParams)
    if (nextFilters.namespace) next.set('mcNamespace', nextFilters.namespace); else next.delete('mcNamespace')
    if (nextFilters.flowId) next.set('mcFlow', nextFilters.flowId); else next.delete('mcFlow')
    if (nextFilters.states.length) next.set('mcState', nextFilters.states.join(',')); else next.delete('mcState')
    setSearchParams(next, { replace: true })
  }
  const refreshMission = () => {
    void Promise.all([
      executions.refetch(),
      flows.refetch(),
      workers.refetch(),
      admission.refetch(),
      ...(session.capabilities['humanTasks.view'] ? [humanTasks.refetch()] : []),
      ...detailQueries.map((query) => query.refetch()),
    ])
  }

  if (!session.capabilities['dashboards.view']) return <ErrorState message="Dashboard access is not available for this workspace." retry={() => undefined} />
  return (
    <div className="page-stack dashboard-workbench">
      <header className="page-heading dashboard-heading">
        <div><p className="eyebrow">OPERATE / LIVE</p><h1>{t('missionControl')}</h1><p>See what is running, what needs attention, and why—before opening expert evidence.</p></div>
        <span className="live-indicator"><i />Refresh · 15s</span>
      </header>
      {notice ? <p className="inline-notice" role="status">{notice}</p> : null}
      <MissionControl model={mission} filters={missionFilters} namespaceOptions={namespaceOptions} flowOptions={missionFlowOptions} loading={executions.isPending || flows.isPending || workers.isPending || admission.isPending} error={(executions.error || flows.error || workers.error || admission.error)?.message || null} partial={detailQueries.some((query) => Boolean(query.error))} fetching={executions.isFetching || flows.isFetching || workers.isFetching || admission.isFetching || detailQueries.some((query) => query.isFetching)} locale={settings.locale} timezone={settings.timezone} tenant={settings.tenant} onFiltersChange={updateMissionFilters} onRefresh={refreshMission} />
      <details className="dashboard-analytics">
        <summary><span><strong>Analytics and saved dashboards</strong><small>Explore charts, saved views and dashboard definitions.</small></span><span>{definitions.data?.length || 0} views</span></summary>
        <div className="dashboard-layout">
        <aside className="dashboard-library" aria-label="Dashboard library">
          <div className="section-heading"><div><p className="eyebrow">LIBRARY</p><h2>Views</h2></div>{session.capabilities['dashboards.manage'] ? <button className="icon-button" type="button" aria-label="Create dashboard" onClick={() => setShowEditor(true)}><Plus aria-hidden="true" /></button> : null}</div>
          {definitions.isPending ? <LoadingState /> : null}
          {definitions.error ? <ErrorState message={definitions.error.message} retry={() => void definitions.refetch()} /> : null}
          <div className="dashboard-library-list">{definitions.data?.map((definition) => <button className={definition.dashboardId === selectedId ? 'selected' : ''} key={definition.dashboardId} type="button" onClick={() => setSearchParams({ dashboard: definition.dashboardId })}><strong>{definition.title}</strong><span>{definition.builtin ? 'Built-in' : `${definition.visibility.toLowerCase()} · v${String(definition.version)}`}</span></button>)}</div>
        </aside>
        <section className="dashboard-canvas" id="dashboard-canvas" aria-label="Dashboard canvas">
          <form className="dashboard-filterbar" onSubmit={applyFilters}>
            <label>Window<select value={filterDraft.hours} onChange={(event) => setFilterDraft((current) => ({ ...current, hours: Number(event.target.value) }))}><option value="1">1 hour</option><option value="24">24 hours</option><option value="168">7 days</option><option value="720">30 days</option></select></label>
            <CatalogSelect label="Namespace" value={filterDraft.namespace} options={namespaceOptions} onChange={(value) => setFilterDraft((current) => ({ ...current, namespace: value, flowId: '' }))} emptyLabel="All namespaces" loading={flows.isPending} />
            <CatalogSelect label="Flow" value={filterDraft.flowId} options={flowOptions} onChange={(value) => setFilterDraft((current) => ({ ...current, flowId: value }))} emptyLabel="All flows" loading={flows.isPending} />
            <CatalogMultiSelect label="States" values={csvValues(filterDraft.states)} options={EXECUTION_STATES.map((state) => ({ value: state, label: state.replaceAll('_', ' ') }))} onChange={(values) => setFilterDraft((current) => ({ ...current, states: values.join(',') }))} />
            <details><summary>More filters</summary><div><CatalogMultiSelect label="Worker groups" values={csvValues(filterDraft.workerGroups)} options={workerGroupOptions} onChange={(values) => setFilterDraft((current) => ({ ...current, workerGroups: values.join(',') }))} /><label>Labels<input value={filterDraft.labels} onChange={(event) => setFilterDraft((current) => ({ ...current, labels: event.target.value }))} placeholder="team=platform" /></label><label>Dimensions<input value={filterDraft.dimensions} onChange={(event) => setFilterDraft((current) => ({ ...current, dimensions: event.target.value }))} placeholder="region=apac" /></label></div></details>
            <button className="button button-secondary" type="submit"><RefreshCw size={15} aria-hidden="true" />Apply</button>
          </form>
          {rendered.isPending ? <LoadingState /> : null}
          {rendered.error ? <ErrorState message={rendered.error.message} retry={() => void rendered.refetch()} /> : null}
          {selected ? <section className="dashboard-titlebar"><div><p className="eyebrow">{selected.source} · {selected.visibility}</p><h2>{selected.title}</h2><p>{selected.description}</p></div><div className="button-row"><button className="button button-secondary" type="button" onClick={() => void share()}><Share2 size={15} aria-hidden="true" />Share</button><button className="button button-secondary" type="button" onClick={() => void exportDefinition()}><Download size={15} aria-hidden="true" />Export</button>{session.capabilities['dashboards.manage'] && !selected.builtin ? <button className="button button-danger" type="button" onClick={() => remove.mutate(selected)}><Trash2 size={15} aria-hidden="true" />Delete</button> : null}</div></section> : null}
          {rendered.data ? <div className="dashboard-widgets">{rendered.data.dashboard.widgets.map((widget) => {
            const result = rendered.data.widgets.find((item) => item.widgetId === widget.widgetId)?.result
            return <article className={`dashboard-widget widget-${widget.query.visualization.toLowerCase()}`} key={widget.widgetId}><header><div><p className="eyebrow">{widget.query.source} / {widget.query.visualization.replaceAll('_', ' ')}</p><h3>{widget.title}</h3></div>{result ? <span title={`Scanned ${String(result.scannedRows)} rows`}><Clock3 size={14} aria-hidden="true" />{formatDate(result.freshAt, settings.locale, settings.timezone)}</span> : null}</header>{result ? <><div className="dashboard-indicators">{result.partial ? <b>Partial · limit {String(result.limit)}</b> : <span>Complete</span>}{result.sampled ? <b>Sampled {String(widget.query.sampleRate * 100)}%</b> : <span>Unsampled</span>}{result.redacted ? <b>Redacted</b> : <span>Authorized</span>}</div><WidgetVisual visualization={widget.query.visualization} result={result} locale={settings.locale} /></> : <LoadingState />}</article>
          })}</div> : null}
        </section>
        </div>
      </details>
      {showEditor ? <DashboardEditor initialFilters={filters} principals={principalOptions} onClose={() => setShowEditor(false)} onSave={(draft) => save.mutate(draft)} pending={save.isPending} /> : null}
    </div>
  )
}
