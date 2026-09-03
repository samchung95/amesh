import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, ArrowLeft, ArrowRight, Database, RefreshCw, Search } from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import type { SearchDocumentType, SearchRequest, SearchSortDirection, SearchSortField, UiSession } from '../../api/types'
import { formatDate, formatNumber } from '../../app/format'
import { useApiClient, useFlows } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { CatalogSelect, EmptyState, ErrorState, LoadingState } from '../../shared/ui'
import { parseSearchPairs, SEARCH_TYPES, searchResultPath, searchTypeLabel } from './searchModel'

const FIELD_OPTIONS = [
  ['flowId', 'Flow ID'], ['executionId', 'Execution ID'], ['taskRunId', 'Task run ID'],
  ['level', 'Log level'], ['logger', 'Logger'], ['provider', 'Asset provider'],
  ['assetType', 'Asset type'], ['resourceType', 'Audit resource'], ['action', 'Audit action'],
  ['outcome', 'Audit outcome'], ['actorId', 'Actor ID'],
] as const

const SEARCH_STATES = ['RUNNING', 'QUEUED', 'PAUSED', 'RESTARTING', 'SUCCESS', 'WARNING', 'FAILED', 'CANCELLED', 'OPEN', 'ACTIVE', 'DISABLED']

function iso(value: string): string | undefined {
  return value ? new Date(value).toISOString() : undefined
}

export function SearchPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const flows = useFlows(session.capabilities['flows.view'])
  const { settings } = useAppSettings()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') || '')
  const [namespace, setNamespace] = useState(params.get('namespace') || settings.namespace || '')
  const [state, setState] = useState(params.get('state') || '')
  const [labels, setLabels] = useState(params.get('labels') || '')
  const [field, setField] = useState(params.get('field') || '')
  const [fieldValue, setFieldValue] = useState(params.get('fieldValue') || '')
  const [from, setFrom] = useState(params.get('from') || '')
  const [to, setTo] = useState(params.get('to') || '')
  const [types, setTypes] = useState<SearchDocumentType[]>(() => {
    const selected = (params.get('types') || '').split(',').filter(Boolean) as SearchDocumentType[]
    return selected.length ? selected : SEARCH_TYPES
  })
  const [sort, setSort] = useState<SearchSortField>((params.get('sort') as SearchSortField) || 'RELEVANCE')
  const [direction, setDirection] = useState<SearchSortDirection>((params.get('direction') as SearchSortDirection) || 'DESC')
  const [cursorHistory, setCursorHistory] = useState<string[]>([])
  const [rebuildNotice, setRebuildNotice] = useState('')
  const cursor = params.get('cursor') || undefined
  const namespaces = useMemo(() => Array.from(new Set([
    ...(settings.namespace ? [settings.namespace] : []),
    ...(flows.data || []).map((flow) => flow.namespace),
  ])).sort(), [flows.data, settings.namespace])

  const request = useMemo<SearchRequest>(() => {
    const selectedField = params.get('field')
    const selectedValue = params.get('fieldValue')
    return {
      query: params.get('q') || '',
      namespace: params.get('namespace') || undefined,
      states: params.get('state') ? [params.get('state') as string] : [],
      labels: parseSearchPairs(params.get('labels') || ''),
      fields: selectedField && selectedValue ? { [selectedField]: selectedValue } : {},
      from: iso(params.get('from') || ''),
      to: iso(params.get('to') || ''),
      ranges: [],
      types: ((params.get('types') || '').split(',').filter(Boolean) as SearchDocumentType[]),
      sort: (params.get('sort') as SearchSortField) || 'RELEVANCE',
      direction: (params.get('direction') as SearchSortDirection) || 'DESC',
      limit: 25,
      cursor,
    }
  }, [cursor, params])
  const results = useQuery({
    queryKey: ['search-page', settings.tenant, request],
    queryFn: () => api.search(request),
    enabled: session.capabilities['search.view'],
    placeholderData: (previous) => previous,
  })
  const status = useQuery({
    queryKey: ['search-status', settings.tenant],
    queryFn: api.searchStatus,
    enabled: session.capabilities['search.view'],
    refetchInterval: 5_000,
  })

  const apply = (event: FormEvent) => {
    event.preventDefault()
    const next = new URLSearchParams()
    if (query) next.set('q', query)
    if (namespace) next.set('namespace', namespace)
    if (state) next.set('state', state)
    if (labels) next.set('labels', labels)
    if (field && fieldValue) { next.set('field', field); next.set('fieldValue', fieldValue) }
    if (from) next.set('from', from)
    if (to) next.set('to', to)
    if (types.length !== SEARCH_TYPES.length) next.set('types', types.join(','))
    next.set('sort', sort)
    next.set('direction', direction)
    setCursorHistory([])
    setParams(next)
  }
  const toggleType = (type: SearchDocumentType) => {
    setTypes((current) => current.includes(type) ? current.filter((item) => item !== type) : [...current, type])
  }
  const nextPage = () => {
    if (!results.data?.nextCursor) return
    setCursorHistory((current) => [...current, cursor || ''])
    const next = new URLSearchParams(params)
    next.set('cursor', results.data.nextCursor)
    setParams(next)
  }
  const previousPage = () => {
    const previous = cursorHistory.at(-1)
    if (previous === undefined) return
    const next = new URLSearchParams(params)
    if (previous) next.set('cursor', previous); else next.delete('cursor')
    setCursorHistory((current) => current.slice(0, -1))
    setParams(next)
  }
  const rebuild = async () => {
    if (!window.confirm('Build and atomically activate a new tenant search projection generation?')) return
    try {
      await api.rebuildSearch('operator requested an authoritative projection rebuild', {
        types: types.length === SEARCH_TYPES.length ? undefined : types,
        from: iso(from),
        to: iso(to),
      })
      setRebuildNotice('Blue-green rebuild accepted. The active generation remains queryable until verification passes.')
      await status.refetch()
      await results.refetch()
    } catch (caught) {
      setRebuildNotice(caught instanceof Error ? caught.message : 'Search rebuild failed')
    }
  }
  const verify = async () => {
    try {
      const result = await api.verifySearch()
      setRebuildNotice(result.verified ? `Projection verified: ${result.checksum.slice(0, 12)}` : 'Projection drift detected. Review per-type checksums through the API.')
      await status.refetch()
    } catch (caught) {
      setRebuildNotice(caught instanceof Error ? caught.message : 'Search verification failed')
    }
  }
  const toggleProjection = async () => {
    const enabled = !(status.data?.enabled ?? true)
    try {
      await api.controlSearch(enabled, enabled ? 'operator resumed projected search' : 'operator selected bounded authoritative fallback')
      setRebuildNotice(enabled ? 'Projected search enabled.' : 'Projection disabled. Flow and execution searches use bounded authoritative fallback.')
      await status.refetch()
      await results.refetch()
    } catch (caught) {
      setRebuildNotice(caught instanceof Error ? caught.message : 'Search control failed')
    }
  }

  return (
    <div className="page-stack search-workbench">
      <header className="page-heading">
        <div><p className="eyebrow">DISCOVER / PROJECTION</p><h1>Search</h1><p>Authorized full-text and structured retrieval across rebuildable tenant data.</p></div>
        {session.capabilities['search.manage'] ? <div className="resource-heading-actions"><button className="button button-secondary" type="button" onClick={() => void verify()}>Verify</button><button className="button button-secondary" type="button" onClick={() => void toggleProjection()}>{status.data?.enabled === false ? 'Enable projection' : 'Use fallback'}</button><button className="button button-secondary" type="button" onClick={() => void rebuild()}><RefreshCw size={17} aria-hidden="true" />Rebuild index</button></div> : null}
      </header>
      <section className={`search-health search-health-${(status.data?.condition || 'ready').toLowerCase()}`} aria-label="Search projection status">
        <Database size={20} aria-hidden="true" />
        <div><strong>{status.data?.condition || 'Loading'} · schema v{status.data?.schemaVersion || '—'} · projection v{status.data?.projectionVersion || '—'}{status.data?.buildingVersion ? ` → v${status.data.buildingVersion}` : ''}</strong><span>{status.data ? `${formatNumber(status.data.documentsIndexed, settings.locale)} / ${formatNumber(status.data.sourceDocuments, settings.locale)} documents · ${Math.round(status.data.progress * 100)}% · ${status.data.checkpointsVerified ? 'checksums verified' : 'verification pending'} · lag ${status.data.lagSeconds === null ? 'unknown' : `${status.data.lagSeconds.toFixed(1)}s`}` : 'Reading projection health…'}</span></div>
        {status.data?.failures ? <span className="search-failures"><AlertTriangle size={15} aria-hidden="true" />{status.data.failures} failures</span> : null}
      </section>
      {rebuildNotice ? <p className="inline-notice" role="status">{rebuildNotice}</p> : null}
      <form className="search-filters" onSubmit={apply} aria-label="Search filters">
        <label className="search-query"><span>Full text</span><span><Search size={17} aria-hidden="true" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Flow, execution, log message, asset or audit record" /></span></label>
        <CatalogSelect label="Namespace" value={namespace} options={namespaces.map((item) => ({ value: item, label: item }))} onChange={setNamespace} emptyLabel="All namespaces" loading={flows.isPending} />
        <CatalogSelect label="State" value={state} options={SEARCH_STATES.map((item) => ({ value: item, label: item.replaceAll('_', ' ') }))} onChange={setState} emptyLabel="Any state" allowCustom customLabel="Search another state…" />
        <label><span>Labels</span><input value={labels} onChange={(event) => setLabels(event.target.value)} placeholder="team=platform, env=prod" /></label>
        <label><span>Field</span><select aria-label="Field" value={field} onChange={(event) => setField(event.target.value)}><option value="">No field filter</option>{FIELD_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <label><span>Field value</span><input aria-label="Field value" value={fieldValue} onChange={(event) => setFieldValue(event.target.value)} disabled={!field} /></label>
        <label><span>From</span><input type="datetime-local" value={from} onChange={(event) => setFrom(event.target.value)} /></label>
        <label><span>To</span><input type="datetime-local" value={to} onChange={(event) => setTo(event.target.value)} /></label>
        <label><span>Sort</span><select value={sort} onChange={(event) => setSort(event.target.value as SearchSortField)}><option value="RELEVANCE">Relevance</option><option value="UPDATED_AT">Updated</option><option value="OCCURRED_AT">Occurred</option><option value="TITLE">Title</option><option value="TYPE">Type</option><option value="STATE">State</option></select></label>
        <label><span>Direction</span><select value={direction} onChange={(event) => setDirection(event.target.value as SearchSortDirection)}><option value="DESC">Descending</option><option value="ASC">Ascending</option></select></label>
        <fieldset><legend>Resource types</legend>{SEARCH_TYPES.map((type) => <label key={type}><input type="checkbox" checked={types.includes(type)} onChange={() => toggleType(type)} />{searchTypeLabel(type)}</label>)}</fieldset>
        <button className="button button-primary" type="submit" disabled={!types.length}><Search size={17} aria-hidden="true" />Search projection</button>
      </form>
      {results.isPending ? <LoadingState label="Searching tenant projection" /> : null}
      {results.error ? <ErrorState message={results.error.message} retry={() => void results.refetch()} /> : null}
      {results.data?.deniedTypes.length ? <p className="permission-note"><AlertTriangle size={16} aria-hidden="true" />Not searched: {results.data.deniedTypes.map(searchTypeLabel).join(', ')}. Underlying resource permissions still apply.</p> : null}
      {results.data && !results.data.items.length ? <EmptyState title="No authorized results" body="Change the text or structured filters. Rebuilding projections may be temporarily incomplete." /> : null}
      {results.data?.items.length ? (
        <section className="search-results" aria-label="Search results">
          <header><strong>{results.data.items.length} results on this page</strong><span>{results.data.authoritativeFallback ? 'AUTHORITATIVE FALLBACK' : results.data.projectionCondition} · v{results.data.projectionVersion}</span></header>
          <ol>{results.data.items.map((item) => <li key={`${item.documentType}:${item.documentId}`}><Link to={searchResultPath(item)}><span className={`search-type search-type-${item.documentType.toLowerCase()}`}>{searchTypeLabel(item.documentType)}</span><div><strong>{item.title}</strong><p>{item.summary || 'No indexed summary'}</p><small>{item.namespace || 'Tenant-wide'}{item.state ? ` · ${item.state}` : ''} · updated {formatDate(item.updatedAt, settings.locale, settings.timezone)}</small></div><span className="search-score">{item.relevance.toFixed(2)}</span></Link></li>)}</ol>
          <footer><button className="button button-secondary" type="button" disabled={!cursorHistory.length} onClick={previousPage}><ArrowLeft size={16} aria-hidden="true" />Previous</button><button className="button button-secondary" type="button" disabled={!results.data.nextCursor} onClick={nextPage}>Next<ArrowRight size={16} aria-hidden="true" /></button></footer>
        </section>
      ) : null}
    </div>
  )
}
