import { BookmarkPlus, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useSearchParams } from 'react-router-dom'

import type { UiSession } from '../api/types'
import { compactId, formatDate } from '../app/format'
import { useExecutions, useFlows } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'
import { CatalogSelect } from '../components/CatalogSelect'
import { StatusBadge } from '../components/StatusBadge'

export function ExecutionsPage({ session }: { session: UiSession }) {
  const { t } = useTranslation()
  const { settings, saveView } = useAppSettings()
  const [params, setParams] = useSearchParams()
  const [savedNotice, setSavedNotice] = useState(false)
  const executions = useExecutions(session.capabilities['executions.view'])
  const flows = useFlows(session.capabilities['flows.view'])
  const state = params.get('state') || ''
  const namespace = params.get('namespace') || ''
  const flowId = params.get('flow') || ''
  const query = params.get('q') || ''
  const namespaces = useMemo(() => Array.from(new Set((flows.data || []).map((flow) => flow.namespace))).sort(), [flows.data])
  const flowOptions = useMemo(() => (flows.data || []).filter((flow) => !namespace || flow.namespace === namespace), [flows.data, namespace])
  const visible = useMemo(() => (executions.data || []).filter((execution) => (!state || execution.state === state) && (!namespace || execution.namespace === namespace) && (!flowId || execution.flow_id === flowId) && `${execution.namespace}.${execution.flow_id} ${execution.execution_id}`.toLowerCase().includes(query.toLowerCase())), [executions.data, flowId, namespace, query, state])
  const update = (key: string, value: string) => { const next = new URLSearchParams(params); if (value) next.set(key, value); else next.delete(key); setParams(next) }
  const save = () => { const path = `/executions${params.size ? `?${params.toString()}` : ''}`; saveView({ id: `executions:${params.toString() || 'all'}`, label: state ? `Executions · ${state}` : 'Executions · All', path }); setSavedNotice(true); window.setTimeout(() => setSavedNotice(false), 1600) }

  return (
    <div className="page-stack">
      <header className="page-heading"><div><p className="eyebrow">OPERATE / HISTORY</p><h1>{t('executions')}</h1><p>Current and terminal runs in the selected tenant boundary.</p></div><button className="button button-secondary" type="button" onClick={save}><BookmarkPlus size={17} aria-hidden="true" />{t('saveView')}</button></header>
      <div className="sr-live" aria-live="polite">{savedNotice ? t('saved') : ''}</div>
      <section className="toolbar" aria-label="Execution filters">
        <label className="search-field"><Search size={17} aria-hidden="true" /><span className="sr-only">Search executions</span><input value={query} onChange={(event) => update('q', event.target.value)} placeholder="Search flow or execution ID" /></label>
        <CatalogSelect label="Namespace" value={namespace} options={namespaces.map((item) => ({ value: item, label: item }))} onChange={(value) => { const next = new URLSearchParams(params); if (value) next.set('namespace', value); else next.delete('namespace'); next.delete('flow'); setParams(next) }} emptyLabel="All namespaces" loading={flows.isPending} className="filter-select" />
        <CatalogSelect label="Flow" value={flowId} options={flowOptions.map((flow) => ({ value: flow.flow_id, label: `${flow.flow_id} · ${flow.namespace}` }))} onChange={(value) => update('flow', value)} emptyLabel="All flows" loading={flows.isPending} className="filter-select" />
        <CatalogSelect label="State" value={state} options={['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'RESTARTING', 'SUCCESS', 'WARNING', 'FAILED', 'CANCELLED'].map((value) => ({ value, label: value.replaceAll('_', ' ') }))} onChange={(value) => update('state', value)} emptyLabel={t('allStates')} className="filter-select" />
        <span className="result-count">{visible.length} / {executions.data?.length || 0} runs</span>
      </section>
      {executions.isPending ? <LoadingState label="Loading execution history" /> : null}
      {executions.error ? <ErrorState message={executions.error.message} retry={() => void executions.refetch()} /> : null}
      {!executions.isPending && !executions.error && !visible.length ? <EmptyState title="No executions match" body="Clear the filters or run a flow to populate execution history." /> : null}
      {visible.length ? <section className="table-shell" aria-label="Executions"><table><thead><tr><th>Execution</th><th>Flow</th><th>State</th><th>Updated</th><th>Epoch</th></tr></thead><tbody>{visible.map((execution) => <tr key={execution.execution_id}><td><Link className="table-link" to={`/executions/${execution.execution_id}`}><code>{compactId(execution.execution_id)}</code></Link></td><td><strong>{execution.flow_id}</strong><small className="cell-subtitle">{execution.namespace}</small></td><td><StatusBadge state={execution.state} /></td><td><time dateTime={execution.updated_at}>{formatDate(execution.updated_at, settings.locale, settings.timezone)}</time></td><td>e{execution.epoch}</td></tr>)}</tbody></table></section> : null}
    </div>
  )
}
