import { FileCode2, Plus, Search, Workflow } from 'lucide-react'
import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useSearchParams } from 'react-router-dom'

import type { UiSession } from '../api/types'
import { useFlows } from '../app/queries'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'

export function FlowsPage({ session }: { session: UiSession }) {
  const { t } = useTranslation()
  const [params, setParams] = useSearchParams()
  const flows = useFlows(session.capabilities['flows.view'])
  const query = params.get('q') || ''
  const selectedNamespace = params.get('namespace') || ''
  const visible = useMemo(() => (flows.data || []).filter((flow) => {
    const matchesQuery = `${flow.namespace}.${flow.flow_id}`.toLowerCase().includes(query.toLowerCase())
    return matchesQuery && (!selectedNamespace || flow.namespace === selectedNamespace)
  }), [flows.data, query, selectedNamespace])

  return (
    <div className="page-stack">
      <header className="page-heading"><div><p className="eyebrow">BUILD / CATALOG</p><h1>{t('flows')}</h1><p>Canonical definitions available to this tenant and namespace scope.</p></div>{session.capabilities['flows.create'] ? <button className="button button-primary" type="button" disabled title="Flow editor is delivered by EPIC-405"><Plus size={17} aria-hidden="true" />Create flow</button> : null}</header>
      <section className="toolbar" aria-label="Flow filters">
        <label className="search-field"><Search size={17} aria-hidden="true" /><span className="sr-only">Search flows</span><input value={query} onChange={(event) => { const next = new URLSearchParams(params); if (event.target.value) next.set('q', event.target.value); else next.delete('q'); setParams(next) }} placeholder="Search namespace or flow ID" /></label>
        <span className="result-count">{visible.length} / {flows.data?.length || 0} flows</span>
      </section>
      {flows.isPending ? <LoadingState label="Loading flow catalog" /> : null}
      {flows.error ? <ErrorState message={flows.error.message} retry={() => void flows.refetch()} /> : null}
      {!flows.isPending && !flows.error && !visible.length ? <EmptyState title="No flows in this view" body={query || selectedNamespace ? 'Clear the current filters or change workspace context.' : 'Apply a YAML flow through the API or CLI to see it here.'} /> : null}
      {visible.length ? (
        <section className="table-shell" aria-label="Flows">
          <table><thead><tr><th>Flow</th><th>Namespace</th><th>Revision</th><th>Contract</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{visible.map((flow) => <tr key={flow.resource_id}><td><span className="primary-cell"><Workflow size={17} aria-hidden="true" /><strong>{flow.flow_id}</strong></span></td><td><code>{flow.namespace}</code></td><td>r{flow.revision}</td><td><span className="hash"><FileCode2 size={14} aria-hidden="true" />{flow.semantic_hash.slice(0, 12)}</span></td><td><Link className="button button-quiet" to={`/flows/${encodeURIComponent(flow.namespace)}/${encodeURIComponent(flow.flow_id)}`}>Open graph</Link></td></tr>)}</tbody></table>
        </section>
      ) : null}
    </div>
  )
}
