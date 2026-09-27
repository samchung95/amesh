import { useQueries } from '@tanstack/react-query'
import { FileCode2, Plus, Search, Workflow } from 'lucide-react'
import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useSearchParams } from 'react-router-dom'

import type { PersistedExecution, PersistedFlow, TriggerRuntimeState, UiSession } from '../../api/types'
import { formatDate } from '../../app/format'
import { useApiClient, useFlows, useTriggerRuntime } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { CatalogSelect, EmptyState, ErrorState, LoadingState, StatusBadge } from '../../shared/ui'

const LAST_RUN_LOOKUP_LIMIT = 50

type LastRunQuery = {
  data?: PersistedExecution[]
  error: Error | null
  isPending: boolean
}

function flowKey(flow: Pick<PersistedFlow, 'namespace' | 'flow_id'>): string {
  return `${flow.namespace}\u0000${flow.flow_id}`
}

function triggerTypeLabel(type: string): string {
  const label = type.replace(/^core\./u, '').replace(/[._-]+/gu, ' ').trim()
  return label ? `${label[0]?.toUpperCase() || ''}${label.slice(1)}` : 'Trigger'
}

function flowLabels(flow: PersistedFlow): Record<string, string> {
  return flow.metadata?.labels ?? {}
}

function matchingTriggers(flow: PersistedFlow, triggers: TriggerRuntimeState[] | undefined): TriggerRuntimeState[] {
  return (triggers || [])
    .filter((trigger) => trigger.namespace === flow.namespace && trigger.flow_id === flow.flow_id)
    .sort((left, right) => Number(right.active) - Number(left.active) || Number(left.paused) - Number(right.paused) || left.trigger_id.localeCompare(right.trigger_id))
}

function lastRunTriggerLabel(lastRun: PersistedExecution | undefined): string | null {
  const type = typeof lastRun?.trigger?.type === 'string' ? lastRun.trigger.type : null
  if (!type || type === 'manual') return null
  return `${triggerTypeLabel(type)} from last run`
}

function triggerSummary(
  flow: PersistedFlow,
  triggers: TriggerRuntimeState[] | undefined,
  lastRun: PersistedExecution | undefined,
  canViewTriggers: boolean,
  triggersPending: boolean,
  triggersError: Error | null,
  locale: string,
  timezone: string,
): string {
  if (!canViewTriggers) return lastRunTriggerLabel(lastRun) || 'Trigger access needed'
  if (triggersPending) return 'Loading triggers'
  if (triggersError) return lastRunTriggerLabel(lastRun) || 'Trigger status unavailable'
  const matches = matchingTriggers(flow, triggers)
  if (!matches.length) return lastRunTriggerLabel(lastRun) || 'Manual or API'
  const active = matches.filter((trigger) => trigger.active && !trigger.paused)
  const selected = active[0] || matches[0]
  const base = matches.length > 1 ? `${String(matches.length)} triggers` : triggerTypeLabel(selected.trigger_type)
  if (selected.paused) return `${base} · paused`
  if (selected.next_evaluation_at) return `${base} · next ${formatDate(selected.next_evaluation_at, locale, timezone)}`
  return base
}

function LastRunCell({ query, canViewExecutions, locale, timezone }: { query?: LastRunQuery; canViewExecutions: boolean; locale: string; timezone: string }) {
  if (!canViewExecutions) return <span className="status status-unknown">Run access needed</span>
  if (!query) return <span className="status status-unknown">Filter to load status</span>
  if (query.isPending) return <span className="status status-unknown">Loading</span>
  if (query.error) return <span className="status status-warning">Status unavailable</span>
  const execution = query.data?.[0]
  if (!execution) return <span className="status status-unknown">Never run</span>
  return <span className="flow-last-run"><StatusBadge state={execution.state} /><time dateTime={execution.updated_at}>{formatDate(execution.updated_at, locale, timezone)}</time></span>
}

function FlowLabelList({ labels }: { labels: Record<string, string> }) {
  const entries = Object.entries(labels)
  if (!entries.length) return <span className="cell-subtitle">No labels</span>
  return <span className="flow-labels">{entries.slice(0, 3).map(([key, value]) => <span key={key}><b>{key}</b>{value}</span>)}{entries.length > 3 ? <span>+{String(entries.length - 3)}</span> : null}</span>
}

export function FlowsPage({ session }: { session: UiSession }) {
  const { t } = useTranslation()
  const api = useApiClient()
  const { settings } = useAppSettings()
  const [params, setParams] = useSearchParams()
  const flows = useFlows(session.capabilities['flows.view'])
  const triggers = useTriggerRuntime(session.capabilities['triggers.view'])
  const query = params.get('q') || ''
  const selectedNamespace = params.get('namespace') || ''
  const namespaces = useMemo(() => Array.from(new Set((flows.data || []).map((flow) => flow.namespace))).sort(), [flows.data])
  const visible = useMemo(() => (flows.data || []).filter((flow) => {
    const matchesQuery = `${flow.namespace}.${flow.flow_id}`.toLowerCase().includes(query.toLowerCase())
    return matchesQuery && (!selectedNamespace || flow.namespace === selectedNamespace)
  }), [flows.data, query, selectedNamespace])
  const statusLookupFlows = useMemo(() => visible.slice(0, LAST_RUN_LOOKUP_LIMIT), [visible])
  const lastRunQueries = useQueries({
    queries: statusLookupFlows.map((flow) => ({
      queryKey: ['flow-last-run', settings.tenant, flow.namespace, flow.flow_id],
      queryFn: () => api.flowExecutions(flow.namespace, flow.flow_id, 1),
      enabled: session.capabilities['executions.view'],
      staleTime: 15_000,
    })),
  })
  const lastRunByFlow = new Map(statusLookupFlows.map((flow, index) => [flowKey(flow), lastRunQueries[index] as LastRunQuery | undefined]))

  return (
    <div className="page-stack">
      <header className="page-heading"><div><p className="eyebrow">BUILD / CATALOG</p><h1>{t('flows')}</h1><p>Canonical workflow definitions available to this tenant and namespace scope.</p></div>{session.capabilities['flows.create'] ? <Link className="button button-primary" to="/flows/new"><Plus size={17} aria-hidden="true" />Create workflow</Link> : null}</header>
      <section className="toolbar" aria-label="Workflow filters">
        <label className="search-field"><Search size={17} aria-hidden="true" /><span className="sr-only">Search workflows</span><input value={query} onChange={(event) => { const next = new URLSearchParams(params); if (event.target.value) next.set('q', event.target.value); else next.delete('q'); setParams(next) }} placeholder="Search namespace or workflow ID" /></label>
        <CatalogSelect label="Namespace" value={selectedNamespace} options={namespaces.map((namespace) => ({ value: namespace, label: namespace }))} onChange={(value) => { const next = new URLSearchParams(params); if (value) next.set('namespace', value); else next.delete('namespace'); setParams(next) }} emptyLabel="All namespaces" loading={flows.isPending} className="filter-select" />
        <span className="result-count">{visible.length} / {flows.data?.length || 0} workflows</span>
      </section>
      {flows.isPending ? <LoadingState label="Loading flow catalog" /> : null}
      {flows.error ? <ErrorState message={flows.error.message} retry={() => void flows.refetch()} /> : null}
      {!flows.isPending && !flows.error && !visible.length ? <EmptyState title="No workflows in this view" body={query || selectedNamespace ? 'Clear the current filters or change workspace context.' : 'Create a workflow here or apply YAML through the API or CLI.'} /> : null}
      {visible.length > LAST_RUN_LOOKUP_LIMIT ? <p className="resource-notice" role="status">Showing last-run details for the first {String(LAST_RUN_LOOKUP_LIMIT)} workflows. Filter the list to inspect a specific workflow.</p> : null}
      {visible.length ? (
        <section className="table-shell" aria-label="Workflows">
          <table><thead><tr><th>Workflow</th><th>Last run</th><th>Trigger</th><th>Labels</th><th>Revision details</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{visible.map((flow) => {
            const lastRunQuery = lastRunByFlow.get(flowKey(flow))
            const lastRun = lastRunQuery?.data?.[0]
            return (
              <tr key={flow.resource_id}>
                <td><span className="primary-cell"><Workflow size={17} aria-hidden="true" /><span><strong>{flow.flow_id}</strong><small className="cell-subtitle">{flow.namespace}</small></span></span></td>
                <td><LastRunCell query={lastRunQuery} canViewExecutions={session.capabilities['executions.view']} locale={settings.locale} timezone={settings.timezone} /></td>
                <td><span className="cell-subtitle">{triggerSummary(flow, triggers.data, lastRun, session.capabilities['triggers.view'], triggers.isPending, triggers.error, settings.locale, settings.timezone)}</span></td>
                <td><FlowLabelList labels={flowLabels(flow)} /></td>
                <td><details className="flow-row-details"><summary>r{flow.revision} details</summary><dl><div><dt>Lifecycle</dt><dd>{flow.lifecycle ? flow.lifecycle.toLowerCase() : 'active'}</dd></div><div><dt>Contract hash</dt><dd><span className="hash"><FileCode2 size={14} aria-hidden="true" />{flow.semantic_hash.slice(0, 12)}</span></dd></div></dl></details></td>
                <td><Link className="button button-quiet" to={`/flows/${encodeURIComponent(flow.namespace)}/${encodeURIComponent(flow.flow_id)}`}>Open workflow</Link></td>
              </tr>
            )
          })}</tbody></table>
        </section>
      ) : null}
    </div>
  )
}
