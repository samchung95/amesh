import { FileCode2, Plus, Search, Workflow } from 'lucide-react'
import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useSearchParams } from 'react-router-dom'

import type { UiSession } from '../../api/types'
import { useFlows } from '../../app/queries'
import { CatalogSelect, EmptyState, ErrorState, LoadingState } from '../../shared/ui'

export function FlowsPage({ session }: { session: UiSession }) {
  const { t } = useTranslation()
  const [params, setParams] = useSearchParams()
  const flows = useFlows(session.capabilities['flows.view'])
  const query = params.get('q') || ''
  const selectedNamespace = params.get('namespace') || ''
  const namespaces = useMemo(() => Array.from(new Set((flows.data || []).map((flow) => flow.namespace))).sort(), [flows.data])
  const visible = useMemo(() => (flows.data || []).filter((flow) => {
    const matchesQuery = `${flow.namespace}.${flow.flow_id}`.toLowerCase().includes(query.toLowerCase())
    return matchesQuery && (!selectedNamespace || flow.namespace === selectedNamespace)
  }), [flows.data, query, selectedNamespace])

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
      {visible.length ? (
        <section className="table-shell" aria-label="Workflows">
          <table><thead><tr><th>Workflow</th><th>Namespace</th><th>Revision</th><th>Contract</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{visible.map((flow) => <tr key={flow.resource_id}><td><span className="primary-cell"><Workflow size={17} aria-hidden="true" /><strong>{flow.flow_id}</strong></span></td><td><code>{flow.namespace}</code></td><td>r{flow.revision}</td><td><span className="hash"><FileCode2 size={14} aria-hidden="true" />{flow.semantic_hash.slice(0, 12)}</span></td><td><Link className="button button-quiet" to={`/flows/${encodeURIComponent(flow.namespace)}/${encodeURIComponent(flow.flow_id)}`}>Open workflow</Link></td></tr>)}</tbody></table>
        </section>
      ) : null}
    </div>
  )
}
