import { Cable, CheckCircle2, Code2, Package, Search, ShieldCheck, Wrench } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { AgentCapabilityCatalog, AgentCapabilityCatalogItem, AgentCapabilityKind, AgentCapabilityStatus } from '../../api/types'
import { EmptyState, ErrorState, LoadingState, StatusBadge } from '../../shared/ui'
import {
  CAPABILITY_KINDS,
  capabilityCanAttach,
  capabilityExactRef,
  capabilityRevisionLabel,
  capabilityStatusLabel,
  filterCapabilityCatalog,
  type CapabilityCatalogFilters,
} from './capabilityCatalogModel'

interface CapabilityCatalogProps {
  items: AgentCapabilityCatalogItem[]
  sourceAccess?: AgentCapabilityCatalog['sourceAccess']
  pending?: boolean
  error?: string | null
  onRetry?: () => void
  onAttach: (item: AgentCapabilityCatalogItem) => void
}

const STATUSES: Array<AgentCapabilityStatus | 'ALL'> = ['ALL', 'available', 'deprecated', 'incompatible', 'denied', 'unavailable', 'schema-drift', 'yanked']

function iconForKind(kind: AgentCapabilityKind) {
  if (kind === 'plugin') return Package
  if (kind === 'mcp-connection') return Cable
  if (kind === 'mcp-tool') return Wrench
  return Code2
}

function permissionLabels(item: AgentCapabilityCatalogItem): string {
  const permissions = item.permissions
  if (!permissions) return 'None declared'
  return [
    ...(permissions.delegatedCapabilities ?? []),
    ...(permissions.toolAllowlist ?? []),
    ...(permissions.secretScopes ?? []).map((scope) => `secret:${scope}`),
    ...(permissions.networkHosts ?? []).map((host) => `network:${host}`),
    ...(permissions.allowedEgress ?? []),
  ].join(', ') || 'None declared'
}

function schemaEntries(item: AgentCapabilityCatalogItem): Array<[string, unknown]> {
  return Object.entries(item.schemas ?? {})
}

export function CapabilityCatalog({ items, sourceAccess = [], pending = false, error = null, onRetry, onAttach }: CapabilityCatalogProps) {
  const [filters, setFilters] = useState<CapabilityCatalogFilters>({ query: '', kind: 'ALL', status: 'ALL' })
  const [selectedRef, setSelectedRef] = useState('')
  const visible = useMemo(() => filterCapabilityCatalog(items, filters), [filters, items])
  const selected = visible.find((item) => item.catalogId === selectedRef) || visible[0] || null
  const updateFilters = (next: Partial<CapabilityCatalogFilters>) => {
    setFilters((current) => ({ ...current, ...next }))
    setSelectedRef('')
  }

  if (pending) return <LoadingState label="Loading capability catalog" />
  if (error) return <ErrorState message={error} retry={onRetry || (() => undefined)} />
  const unavailableSources = sourceAccess.filter((entry) => entry.status !== 'allowed')
  const sourceNotices = unavailableSources.length ? <div className="capability-source-access" aria-label="Capability source access">{unavailableSources.map((entry) => <p key={entry.source} className={`capability-source-${entry.status}`} role="status"><strong>{entry.source}</strong>: {entry.diagnostics.join(' ') || (entry.status === 'denied' ? 'Not authorized for the current principal.' : 'Temporarily unavailable.')}</p>)}</div> : null
  if (!items.length) return <section className="capability-catalog" aria-label="Capability catalog">{sourceNotices}<div className="capability-empty"><EmptyState title="No visible capabilities" body={unavailableSources.length ? 'Resolve the source access messages above, or create an authorized capability revision.' : 'Create a prompt, skill, model policy, agent, plugin or connection to populate this catalog.'} /></div></section>

  return (
    <section className="capability-catalog" aria-label="Capability catalog">
      {sourceNotices}
      <div className="capability-library">
        <div className="section-heading"><div><p className="eyebrow">AUTHORIZED PROJECTION</p><h2>Find a capability</h2></div><span>{visible.length} found</span></div>
        <div className="capability-filters">
          <label><Search size={16} aria-hidden="true" /><span className="sr-only">Search capabilities</span><input value={filters.query} onChange={(event) => updateFilters({ query: event.target.value })} placeholder="Search labels, keys or schemas" /></label>
          <label><span className="sr-only">Capability kind</span><select aria-label="Capability kind" value={filters.kind} onChange={(event) => updateFilters({ kind: event.target.value as CapabilityCatalogFilters['kind'] })}><option value="ALL">All kinds</option>{CAPABILITY_KINDS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}</select></label>
          <label><span className="sr-only">Capability status</span><select aria-label="Capability status" value={filters.status} onChange={(event) => updateFilters({ status: event.target.value as CapabilityCatalogFilters['status'] })}>{STATUSES.map((status) => <option key={status} value={status}>{status === 'ALL' ? 'All statuses' : capabilityStatusLabel(status)}</option>)}</select></label>
        </div>
        <div className="capability-list" role="list">
          {visible.map((item) => {
            const Icon = iconForKind(item.kind)
            const exactRef = capabilityExactRef(item)
            return <button type="button" role="listitem" key={item.catalogId} className={selected?.catalogId === item.catalogId ? 'capability-list-item selected' : 'capability-list-item'} onClick={() => setSelectedRef(item.catalogId)}>
              <span className="capability-kind-icon"><Icon size={17} aria-hidden="true" /></span>
              <span><strong>{item.humanLabel}</strong><small>{item.kind} · {exactRef}</small></span>
              <StatusBadge state={item.status === 'available' ? 'PASS' : item.status === 'yanked' ? 'PAUSED' : 'WARN'} />
            </button>
          })}
        </div>
        {!visible.length ? <p className="editor-empty">No capabilities match these filters.</p> : null}
      </div>
      <div className="capability-detail">
        {selected ? <>
          <header><div><p className="eyebrow">{selected.kind} / EXACT REFERENCE</p><h2>{selected.humanLabel}</h2><code>{capabilityExactRef(selected)}</code></div><StatusBadge state={selected.status === 'available' ? 'PASS' : selected.status === 'yanked' ? 'PAUSED' : 'WARN'} /></header>
          <p>{selected.description || 'No description supplied.'}</p>
          <dl className="capability-facts"><div><dt>Status</dt><dd>{capabilityStatusLabel(selected.status)}</dd></div><div><dt>Revision / version</dt><dd>{capabilityRevisionLabel(selected)}</dd></div><div><dt>Digest</dt><dd><code>{selected.digest}</code></dd></div><div><dt>Impact</dt><dd>{selected.impact}</dd></div><div><dt>Provider compatibility</dt><dd>{selected.providerCompatibility.join(', ') || 'Not declared'}</dd></div><div><dt>Permissions</dt><dd>{permissionLabels(selected)}</dd></div></dl>
          <div className="capability-schemas">{schemaEntries(selected).length ? schemaEntries(selected).map(([name, schema]) => <section key={name}><h3>{name}</h3><pre>{JSON.stringify(schema, null, 2)}</pre></section>) : <p className="editor-empty">No schemas supplied.</p>}</div>
          {selected.diagnostics.length ? <p className="resource-failure" role="status">{selected.diagnostics.join(' ')}</p> : null}
          {selected.attachment.constraints.length ? <p className="capability-constraint" role="status"><ShieldCheck size={16} aria-hidden="true" />Attachment constraint: {selected.attachment.constraints.join('; ')}</p> : null}
          <div className="button-row"><button className="button button-primary" type="button" disabled={!capabilityCanAttach(selected)} onClick={() => onAttach(selected)}><CheckCircle2 size={16} aria-hidden="true" />Attach exact reference</button><small className="permission-note">The builder receives only the canonical reference; this catalog never edits resource bodies.</small></div>
        </> : <EmptyState title="Choose a capability" body="Select an authorized item to inspect its exact revision, schemas and attachment boundary." />}
      </div>
    </section>
  )
}
