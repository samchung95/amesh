import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowDownToLine, ArrowUpFromLine, DatabaseZap, Download, Network, Plus, RefreshCw, Search } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'

import type { AssetDraft, UiSession } from '../../api/types'
import { formatDate } from '../../app/format'
import { useApiClient, useAsset, useAssets } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../../shared/ui'

const emptyDraft = (namespace: string): AssetDraft => ({
  assetId: crypto.randomUUID(),
  namespace: namespace || 'default',
  provider: '',
  account: 'default',
  location: 'global',
  externalKey: '',
  assetType: 'dataset',
  displayName: '',
  description: '',
  owner: null,
  contacts: [],
  domainGroup: null,
  tags: [],
  customMetadata: {},
  labels: {},
  health: 'UNKNOWN',
  lastMaterializationAt: null,
  source: 'DECLARED',
})

export function AssetsPage({ session }: { session: UiSession }) {
  const assets = useAssets()
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const [params, setParams] = useSearchParams()
  const selectedId = params.get('asset')
  const selected = useAsset(selectedId)
  const [query, setQuery] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [draft, setDraft] = useState<AssetDraft>(() => emptyDraft(settings.namespace))
  const [tags, setTags] = useState('')
  const [contacts, setContacts] = useState('')
  const [customMetadata, setCustomMetadata] = useState('{}')
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')
  const canManage = session.capabilities['assets.manage']

  useEffect(() => {
    if (!selectedId && assets.data?.length) setParams({ asset: assets.data[0].assetId }, { replace: true })
  }, [assets.data, selectedId, setParams])

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (!needle) return assets.data || []
    return (assets.data || []).filter((asset) => [
      asset.displayName,
      asset.externalKey,
      asset.provider,
      asset.assetType,
      asset.owner || '',
      asset.domainGroup || '',
      ...asset.tags,
    ].some((value) => value.toLowerCase().includes(needle)))
  }, [assets.data, query])

  const register = useMutation({
    mutationFn: api.registerAsset,
    onSuccess: async (asset) => {
      await queryClient.invalidateQueries({ queryKey: ['assets'] })
      setParams({ asset: asset.assetId })
      setDraft(emptyDraft(settings.namespace))
      setTags('')
      setContacts('')
      setCustomMetadata('{}')
      setShowCreate(false)
      setNotice('Asset declaration saved.')
    },
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()
    setFailure('')
    try {
      const metadata = JSON.parse(customMetadata) as unknown
      if (!metadata || Array.isArray(metadata) || typeof metadata !== 'object') throw new Error('Custom metadata must be a JSON object.')
      register.mutate({
        ...draft,
        tags: tags.split(',').map((item) => item.trim()).filter(Boolean),
        contacts: contacts.split(',').map((item) => item.trim()).filter(Boolean),
        customMetadata: metadata as Record<string, unknown>,
      })
    } catch (error) {
      setFailure(error instanceof Error ? error.message : 'Custom metadata is invalid.')
    }
  }

  const download = async () => {
    const blob = await api.exportAssetCatalog(settings.namespace || undefined)
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `amesh-openlineage-${settings.tenant}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  const healthy = (assets.data || []).filter((asset) => asset.health === 'HEALTHY').length
  const domains = new Set((assets.data || []).map((asset) => asset.domainGroup).filter(Boolean)).size

  return (
    <div className="page-stack">
      <header className="page-heading">
        <div>
          <p className="eyebrow">GOVERN / DISCOVER</p>
          <h1>Asset catalog</h1>
          <p>Declared and observed datasets, infrastructure resources, execution links and lineage evidence.</p>
        </div>
        <div className="asset-heading-actions">
          <button className="button button-secondary" type="button" onClick={() => void download()}><Download size={17} aria-hidden="true" />OpenLineage</button>
          <button className="button button-secondary" type="button" onClick={() => void assets.refetch()} disabled={assets.isFetching}><RefreshCw className={assets.isFetching ? 'spin' : ''} size={17} aria-hidden="true" />Refresh</button>
          {canManage ? <button className="button button-primary" type="button" onClick={() => setShowCreate((value) => !value)}><Plus size={17} aria-hidden="true" />Declare asset</button> : null}
        </div>
      </header>

      <section className="metric-strip" aria-label="Asset catalog summary">
        <article><span><DatabaseZap size={16} aria-hidden="true" />Catalogued</span><strong>{assets.data?.length || 0}</strong><small>visible assets</small></article>
        <article><span><ArrowUpFromLine size={16} aria-hidden="true" />Materialized</span><strong>{healthy}</strong><small>healthy outputs</small></article>
        <article><span><Network size={16} aria-hidden="true" />Domains</span><strong>{domains}</strong><small>governance groups</small></article>
        <article><span><ArrowDownToLine size={16} aria-hidden="true" />Evidence</span><strong>{selected.data?.observations.length || 0}</strong><small>selected timeline</small></article>
      </section>

      {showCreate ? (
        <form className="asset-declaration panel" onSubmit={submit}>
          <div className="section-heading"><div><p className="eyebrow">EXPLICIT DECLARATION</p><h2>Register an asset</h2></div></div>
          <label>Namespace<input required value={draft.namespace} onChange={(event) => setDraft({ ...draft, namespace: event.target.value })} /></label>
          <label>Provider<input required value={draft.provider} onChange={(event) => setDraft({ ...draft, provider: event.target.value })} placeholder="postgres" /></label>
          <label>Account<input required value={draft.account} onChange={(event) => setDraft({ ...draft, account: event.target.value })} /></label>
          <label>Location<input required value={draft.location} onChange={(event) => setDraft({ ...draft, location: event.target.value })} placeholder="warehouse.example:5432/db" /></label>
          <label>Type<input required value={draft.assetType} onChange={(event) => setDraft({ ...draft, assetType: event.target.value })} /></label>
          <label>Stable external key<input required value={draft.externalKey} onChange={(event) => setDraft({ ...draft, externalKey: event.target.value })} placeholder="analytics.orders" /></label>
          <label>Display name<input required value={draft.displayName} onChange={(event) => setDraft({ ...draft, displayName: event.target.value })} /></label>
          <label>Owner<input value={draft.owner || ''} onChange={(event) => setDraft({ ...draft, owner: event.target.value || null })} /></label>
          <label>Domain<input value={draft.domainGroup || ''} onChange={(event) => setDraft({ ...draft, domainGroup: event.target.value || null })} /></label>
          <label>Tags<input value={tags} onChange={(event) => setTags(event.target.value)} placeholder="pii, finance" /></label>
          <label>Contacts<input value={contacts} onChange={(event) => setContacts(event.target.value)} placeholder="data@example.com" /></label>
          <label className="span-two">Description<textarea value={draft.description} onChange={(event) => setDraft({ ...draft, description: event.target.value })} /></label>
          <label className="span-two">Custom metadata<textarea value={customMetadata} onChange={(event) => setCustomMetadata(event.target.value)} spellCheck={false} /></label>
          <div className="span-two asset-form-actions"><button className="button button-primary" type="submit" disabled={register.isPending}>Save declaration</button><button className="button button-ghost" type="button" onClick={() => setShowCreate(false)}>Cancel</button></div>
          {failure || register.error ? <p className="resource-failure span-two" role="alert">{failure || register.error?.message}</p> : null}
        </form>
      ) : null}
      {notice ? <p className="resource-notice" role="status">{notice}</p> : null}

      {assets.isPending ? <LoadingState label="Loading asset catalog" /> : null}
      {assets.error ? <ErrorState message={assets.error.message} retry={() => void assets.refetch()} /> : null}
      {!assets.isPending && !assets.error && !assets.data?.length ? <EmptyState title="No visible assets" body="Declare an asset here or run a plugin that emits an amesh.asset READ or WRITE event." /> : null}

      {assets.data?.length ? (
        <section className="asset-layout">
          <div className="asset-library panel">
            <label className="asset-search"><Search size={16} aria-hidden="true" /><span className="sr-only">Filter assets</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter provider, key, owner or tag" /></label>
            <div className="asset-list" role="list">
              {visible.map((asset) => <button type="button" role="listitem" className={selectedId === asset.assetId ? 'asset-list-item selected' : 'asset-list-item'} key={asset.assetId} onClick={() => setParams({ asset: asset.assetId })}><span><strong>{asset.displayName}</strong><small>{asset.provider} · {asset.assetType}</small></span><em data-health={asset.health}>{asset.health}</em></button>)}
            </div>
          </div>

          <div className="asset-detail panel">
            {selected.isPending ? <LoadingState label="Loading lineage" /> : null}
            {selected.error ? <ErrorState message={selected.error.message} retry={() => void selected.refetch()} /> : null}
            {selected.data ? <>
              <header><div><p className="eyebrow">{selected.data.asset.namespace} / {selected.data.asset.domainGroup || 'UNGROUPED'}</p><h2>{selected.data.asset.displayName}</h2><code>{selected.data.asset.provider}://{selected.data.asset.account}/{selected.data.asset.location}/{selected.data.asset.externalKey}</code></div><span className="asset-health" data-health={selected.data.asset.health}>{selected.data.asset.health}</span></header>
              <p>{selected.data.asset.description || 'No description supplied.'}</p>
              <dl className="asset-facts"><div><dt>Owner</dt><dd>{selected.data.asset.owner || 'Unassigned'}</dd></div><div><dt>Source</dt><dd>{selected.data.asset.source.replace('_', ' ')}</dd></div><div><dt>Last materialization</dt><dd>{selected.data.asset.lastMaterializationAt ? formatDate(selected.data.asset.lastMaterializationAt, settings.locale, settings.timezone) : 'Not observed'}</dd></div><div><dt>Contacts</dt><dd>{selected.data.asset.contacts.join(', ') || 'None'}</dd></div></dl>
              <div className="asset-tags">{selected.data.asset.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
              <div className="asset-lineage-columns"><section><h3><ArrowDownToLine size={16} aria-hidden="true" />Upstream</h3>{selected.data.upstream.length ? selected.data.upstream.map((asset) => <button type="button" key={asset.assetId} onClick={() => setParams({ asset: asset.assetId })}>{asset.displayName}<small>{asset.provider}</small></button>) : <p>No visible upstream assets.</p>}</section><section><h3><ArrowUpFromLine size={16} aria-hidden="true" />Downstream</h3>{selected.data.downstream.length ? selected.data.downstream.map((asset) => <button type="button" key={asset.assetId} onClick={() => setParams({ asset: asset.assetId })}>{asset.displayName}<small>{asset.provider}</small></button>) : <p>No visible downstream assets.</p>}</section></div>
              <section className="asset-observations"><h3>Execution and artifact evidence</h3>{selected.data.observations.length ? selected.data.observations.map((item) => <article key={item.observationId}><span data-access={item.accessMode}>{item.accessMode}</span><div><strong>{item.flowId || 'Explicit declaration'}</strong><small>{item.evidenceKind.toLowerCase()} · confidence {item.confidence.toFixed(2)}{item.artifactId ? ' · artifact linked' : ''}</small></div><time>{formatDate(item.observedAt, settings.locale, settings.timezone)}</time></article>) : <p>No execution observations yet.</p>}</section>
            </> : null}
          </div>
        </section>
      ) : null}
    </div>
  )
}
