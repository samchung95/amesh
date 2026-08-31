import { type FormEvent, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Activity, AlertTriangle, CheckCircle2, ChevronRight, CircleDot, Filter, Pause, Play, RotateCcw, ShieldCheck, Square, X } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'

import type { AgentSessionAdminAction, AgentSessionControlEvent, AgentSessionControlSummary, AgentSessionFleetItem, AgentSessionFleetQuery, AgentSessionPolicy, AgentSessionPolicyDraft, AgentSessionPolicyRevision, UiSession } from '../api/types'
import { formatDate } from '../app/format'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { buildFleetQuery, compactId, dependencyLabel, dependencyTone, fleetStatusLabel, fleetStatusTone, formatFleetCost, lifecycleActions, MAX_BULK_SELECTION, selectVisibleFleetRows, toggleFleetSelection } from '../components/sessionOrchestratorModel'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'
import { AgentProgressTimeline } from '../components/AgentProgressTimeline'
import { progressImagesFromSessionEvents } from '../components/agentProgressModel'
import { SessionPortabilityPanel } from './SessionPortabilityPanel'

type Filters = AgentSessionFleetQuery

const states = ['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'CANCELLED', 'SUCCEEDED', 'FAILED', 'WARNING', 'RESTARTING'] as const

function initialFilters(): Filters {
  return { limit: 50 }
}

function metric(value: number | undefined): string {
  return value === undefined ? '—' : value.toLocaleString()
}

function localDateValue(value: string | undefined): string {
  return value ? value.slice(0, 16) : ''
}

export function SessionOrchestratorPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  const queryClient = useQueryClient()
  const [params, setParams] = useSearchParams()
  const selectedId = params.get('session')
  const [draft, setDraft] = useState<Filters>(initialFilters)
  const [filters, setFilters] = useState<Filters>(initialFilters)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [bulkAction, setBulkAction] = useState<AgentSessionAdminAction>('cancel')
  const [bulkConfirm, setBulkConfirm] = useState(false)
  const [notice, setNotice] = useState('')
  const canManage = session.capabilities['agentSessions.manage']
  const canInstanceView = session.capabilities['agentSessionAdministration.instanceView']
  const canViewPolicies = session.capabilities['agentSessionPolicies.view']
  const canManagePolicies = session.capabilities['agentSessionPolicies.manage']
  const canViewMigration = session.capabilities['agentSessionMigration.view']
  const canManageMigration = session.capabilities['agentSessionMigration.manage']
  const query = useMemo(() => buildFleetQuery(filters), [filters])

  const fleet = useQuery({
    queryKey: ['admin-agent-session-fleet', settings.tenant, query],
    queryFn: () => api.agentSessionFleet(query),
    refetchInterval: 10_000,
  })
  const instance = useQuery({
    queryKey: ['admin-agent-session-instance-aggregate'],
    queryFn: api.agentSessionInstanceAggregate,
    enabled: Boolean(canInstanceView),
    staleTime: 30_000,
  })
  const selected = fleet.data?.items.find((item) => item.sessionId === selectedId) || null
  const detail = useQuery({
    queryKey: ['admin-agent-session-detail', settings.tenant, selectedId],
    queryFn: () => api.agentSession(selectedId || ''),
    enabled: Boolean(selectedId),
  })
  const events = useQuery({
    queryKey: ['admin-agent-session-events', settings.tenant, selectedId],
    queryFn: () => api.agentSessionEvents(selectedId || '', 0, 100),
    enabled: Boolean(selectedId),
  })
  const policyNamespaces = useMemo(() => Array.from(new Set([
    ...(fleet.data?.items.map((item) => item.namespace) || []),
    settings.namespace || '',
  ].filter(Boolean))).sort(), [fleet.data?.items, settings.namespace])
  const policies = useQuery({
    queryKey: ['admin-agent-session-policies', settings.tenant],
    queryFn: () => api.agentSessionPolicies(),
    enabled: canViewPolicies,
  })
  const [evaluationNamespace, setEvaluationNamespace] = useState('')
  const [evaluationApplication, setEvaluationApplication] = useState('')
  const effectivePolicies = useQuery({
    queryKey: ['admin-agent-session-policies-effective', settings.tenant, evaluationNamespace, evaluationApplication],
    queryFn: () => api.effectiveAgentSessionPolicies(evaluationNamespace, evaluationApplication || undefined),
    enabled: canViewPolicies && Boolean(evaluationNamespace),
  })
  const lifecycle = useMutation({
    mutationFn: ({ action, item }: { action: AgentSessionAdminAction; item: AgentSessionFleetItem }) => {
      const control = { expectedVersion: item.executionVersion, expectedEpoch: item.executionEpoch, reason: `Administrator requested ${action}.` }
      if (action === 'cancel') return api.cancelAgentSession(item.sessionId, control)
      if (action === 'pause') return api.pauseAgentSession(item.sessionId, control)
      if (action === 'resume') return api.resumeAgentSession(item.sessionId, control)
      return api.retryAgentSession(item.sessionId, control)
    },
    onSuccess: (_, variables) => {
      setNotice(`Session ${compactId(variables.item.sessionId)} updated.`)
      void queryClient.invalidateQueries({ queryKey: ['admin-agent-session-fleet'] })
      void queryClient.invalidateQueries({ queryKey: ['admin-agent-session-detail'] })
    },
  })
  const bulk = useMutation({
    mutationFn: () => {
      const items = selectedIds.map((sessionId) => {
        const item = fleet.data?.items.find((entry) => entry.sessionId === sessionId)
        if (!item) throw new Error(`Session ${sessionId} is no longer in the current fleet view.`)
        return { sessionId, expectedVersion: item.executionVersion, expectedEpoch: item.executionEpoch }
      })
      return api.agentSessionFleetActions({ action: bulkAction, items, reason: `Administrator bulk action: ${bulkAction}.`, confirmation: `${bulkAction.toUpperCase()} ${selectedIds.length} AGENT SESSIONS` })
    },
    onSuccess: (result) => {
      setNotice(`${metric(result.applied)} action${result.applied === 1 ? '' : 's'} applied${result.rejected ? `; ${metric(result.rejected)} rejected` : ''}.`)
      setSelectedIds([])
      setBulkConfirm(false)
      void queryClient.invalidateQueries({ queryKey: ['admin-agent-session-fleet'] })
    },
  })

  const applyFilters = () => { setFilters({ ...draft }); setSelectedIds([]) }
  const clearFilters = () => { const next = initialFilters(); setDraft(next); setFilters(next); setSelectedIds([]) }
  const toggle = (id: string) => setSelectedIds((current) => {
    const result = toggleFleetSelection(current, id)
    if (result.limited) setNotice(`Bulk actions are limited to ${MAX_BULK_SELECTION} sessions.`)
    return result.next
  })
  const allVisibleSelected = Boolean(fleet.data?.items.length && fleet.data.items.every((item) => selectedIds.includes(item.sessionId)))
  const toggleAll = () => setSelectedIds(() => {
    const result = selectVisibleFleetRows(fleet.data?.items.map((item) => item.sessionId) || [], allVisibleSelected)
    if (result.limited) setNotice(`Only the first ${MAX_BULK_SELECTION} sessions were selected; bulk actions are limited to ${MAX_BULK_SELECTION}.`)
    return result.next
  })
  const filterOptions = useMemo(() => {
    const unique = (values: Array<string | null | undefined>) => Array.from(new Set(values.filter((value): value is string => Boolean(value)))).sort()
    return {
      agents: unique([...(fleet.data?.items.map((item) => item.agentRef) || []), filters.agentRef || null, draft.agentRef || null]),
      namespaces: unique([...(fleet.data?.items.map((item) => item.namespace) || []), filters.namespace || null, draft.namespace || null]),
      owners: unique([...(fleet.data?.items.map((item) => item.ownerId) || []), filters.ownerId || null, draft.ownerId || null]),
      harnesses: unique([...(fleet.data?.items.map((item) => item.harness?.adapter) || []), filters.harness || null, draft.harness || null]),
    }
  }, [draft.agentRef, draft.harness, draft.namespace, draft.ownerId, fleet.data?.items, filters.agentRef, filters.harness, filters.namespace, filters.ownerId])
  const loadMore = () => {
    if (!fleet.data?.nextCursor) return
    void api.agentSessionFleet(buildFleetQuery(filters, fleet.data.nextCursor)).then((next) => {
      queryClient.setQueryData(['admin-agent-session-fleet', settings.tenant, query], { ...next, items: [...(fleet.data?.items || []), ...next.items] })
    })
  }

  if (fleet.isPending) return <div className="page-stack"><LoadingState label="Loading session administration fleet" /></div>
  if (fleet.error) return <div className="page-stack"><ErrorState message={fleet.error.message} retry={() => void fleet.refetch()} /></div>
  const aggregates = fleet.data.aggregates

  return (
    <div className="page-stack session-orchestrator">
      <header className="page-heading">
        <div><p className="eyebrow">GOVERN / SESSION ORCHESTRATOR</p><h1>Fleet administration</h1><p>Observe tenant-scoped agent work, trace bounded evidence, and coordinate lifecycle operations.</p></div>
        <span className="live-indicator"><i />Read {formatDate(fleet.data.readAt, settings.locale, settings.timezone)}</span>
      </header>
      {notice ? <p className="permission-note" role="status"><CheckCircle2 size={16} aria-hidden="true" />{notice}</p> : null}
      {bulk.error ? <p className="form-error" role="alert">Bulk action failed: {bulk.error.message}</p> : null}
      <section className="metric-strip session-fleet-metrics" aria-label="Fleet aggregate status and usage">
        <article><span><Activity size={15} aria-hidden="true" />Matched executions</span><strong>{metric(aggregates.matchedExecutions)}</strong><small>{metric(aggregates.active)} active · {metric(aggregates.terminal)} terminal</small></article>
        <article><span><CircleDot size={15} aria-hidden="true" />Usage</span><strong>{metric(aggregates.totalTokens)}</strong><small>tokens · {metric(aggregates.totalTurns)} turns · {metric(aggregates.totalToolCalls)} tools</small></article>
        <article><span><CheckCircle2 size={15} aria-hidden="true" />Cost</span><strong>{formatFleetCost(aggregates.totalCostUsd)}</strong><small>{metric(aggregates.modelInvocations)} model · {metric(aggregates.toolInvocations)} tool invocations</small></article>
        <article className={aggregates.degradedDependencies ? 'metric-alert' : ''}><span><AlertTriangle size={15} aria-hidden="true" />Dependency posture</span><strong>{metric(aggregates.degradedDependencies)}</strong><small>{aggregates.degradedDependencies ? 'degraded sessions' : 'all pinned dependencies healthy'}</small></article>
      </section>
      {canInstanceView ? <section className="session-instance-pulse" aria-label="Instance aggregate posture">
        <div><strong>Instance pulse</strong><span>Metadata-only totals across tenants; no session content is exposed.</span></div>
        <div><strong>{metric(instance.data?.matchedExecutions)}</strong><small>all-tenant executions</small></div>
        <div><strong>{metric(instance.data?.active)}</strong><small>active</small></div>
        <div><strong>{metric(instance.data?.tenants.length)}</strong><small>tenant groups</small></div>
      </section> : null}
      <form className="toolbar session-fleet-filters" onSubmit={(event) => { event.preventDefault(); applyFilters() }} aria-label="Fleet filters">
        <label className="filter-select"><span>Agent</span><select value={draft.agentRef || ''} onChange={(event) => setDraft({ ...draft, agentRef: event.target.value || undefined })}><option value="">Any agent</option>{filterOptions.agents.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
        <label className="filter-select"><span>State</span><select value={draft.state || ''} onChange={(event) => setDraft({ ...draft, state: (event.target.value || undefined) as Filters['state'] })}><option value="">All states</option>{states.map((state) => <option key={state} value={state}>{fleetStatusLabel(state)}</option>)}</select></label>
        <label className="filter-select"><span>Namespace</span><select value={draft.namespace || ''} onChange={(event) => setDraft({ ...draft, namespace: event.target.value || undefined })}><option value="">Any namespace</option>{filterOptions.namespaces.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
        <label className="filter-select"><span>Owner</span><select value={draft.ownerId || ''} onChange={(event) => setDraft({ ...draft, ownerId: event.target.value || undefined })}><option value="">Any owner</option>{filterOptions.owners.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
        <label className="filter-select"><span>Harness</span><select value={draft.harness || ''} onChange={(event) => setDraft({ ...draft, harness: event.target.value || undefined })}><option value="">Any harness</option>{filterOptions.harnesses.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
        <label className="filter-select"><span>Created from</span><input type="datetime-local" value={localDateValue(draft.createdFrom)} onChange={(event) => setDraft({ ...draft, createdFrom: event.target.value ? new Date(event.target.value).toISOString() : undefined })} /></label>
        <label className="filter-select"><span>Created to</span><input type="datetime-local" value={localDateValue(draft.createdTo)} onChange={(event) => setDraft({ ...draft, createdTo: event.target.value ? new Date(event.target.value).toISOString() : undefined })} /></label>
        <button className="button button-primary" type="submit"><Filter size={16} aria-hidden="true" />Apply</button><button className="button button-quiet" type="button" onClick={clearFilters}>Clear</button>
      </form>
      {selectedIds.length ? <section className="bulk-bar" aria-label="Bulk lifecycle controls"><strong>{selectedIds.length} selected</strong><small>Maximum {MAX_BULK_SELECTION} sessions per action.</small><label><span className="sr-only">Bulk action</span><select value={bulkAction} onChange={(event) => setBulkAction(event.target.value as AgentSessionAdminAction)}><option value="cancel">Cancel</option><option value="pause">Pause</option><option value="resume">Resume</option><option value="retry">Retry</option></select></label>{bulkConfirm ? <div className="bulk-confirm" role="alert"><span>Apply {bulkAction} to {selectedIds.length} sessions?</span><button className="button button-danger button-compact" type="button" disabled={bulk.isPending} onClick={() => bulk.mutate()}>Confirm action</button><button className="button button-quiet button-compact" type="button" onClick={() => setBulkConfirm(false)}>Keep selection</button></div> : <button className="button button-secondary button-compact" type="button" disabled={!canManage} onClick={() => setBulkConfirm(true)}><ShieldCheck size={15} aria-hidden="true" />Review action</button>}{!canManage ? <small className="permission-note"><ShieldCheck size={15} />Lifecycle actions require session administrator access.</small> : null}</section> : null}
      <section className="table-shell session-fleet-table" aria-labelledby="fleet-table-heading">
        <div className="section-heading"><div><p className="eyebrow">TENANT-SCOPED PROJECTION</p><h2 id="fleet-table-heading">Agent session fleet</h2></div><span className="result-count">{metric(fleet.data.items.length)} shown · newest first</span></div>
        {!fleet.data.items.length ? <EmptyState title="No sessions match" body="Adjust the filters or clear the current view to inspect another part of the fleet." /> : <table><thead><tr><th><input type="checkbox" checked={allVisibleSelected} onChange={toggleAll} aria-label="Select all visible sessions" /></th><th>Session / execution</th><th>Owner</th><th>Agent</th><th>Namespace</th><th>Harness</th><th>State</th><th>Usage / dependency</th><th>Updated</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{fleet.data.items.map((item) => <FleetRow key={item.sessionId} item={item} selected={item.sessionId === selectedId} checked={selectedIds.includes(item.sessionId)} canManage={canManage} pending={lifecycle.isPending} locale={settings.locale} timezone={settings.timezone} onToggle={() => toggle(item.sessionId)} onSelect={() => setParams({ session: item.sessionId })} onAction={(action) => lifecycle.mutate({ action, item })} />)}</tbody></table>}
      </section>
      {fleet.data.nextCursor ? <button className="button button-secondary session-load-more" type="button" onClick={loadMore}><ChevronRight size={16} aria-hidden="true" />Load more sessions</button> : null}
      {selected ? <SessionTrace api={api} item={selected} detail={detail.data} events={events.data?.events || []} loading={detail.isPending || events.isPending} error={detail.error?.message || events.error?.message || null} locale={settings.locale} timezone={settings.timezone} /> : <section className="data-section session-trace-empty"><HistoryIcon /><div><h2>Select a session to inspect trace</h2><p>Rows open the canonical redacted session detail and event APIs. Inputs, credentials, and hidden reasoning remain outside this workbench.</p></div></section>}
      {canViewPolicies ? <SessionPolicyPanel api={api} policies={policies.data || []} loading={policies.isPending} error={policies.error?.message || null} canManage={canManagePolicies} namespaceOptions={policyNamespaces} evaluationNamespace={evaluationNamespace} evaluationApplication={evaluationApplication} onEvaluationNamespace={setEvaluationNamespace} onEvaluationApplication={setEvaluationApplication} effectivePolicies={effectivePolicies.data || []} effectiveLoading={effectivePolicies.isPending} effectiveError={effectivePolicies.error?.message || null} onSaved={() => { void queryClient.invalidateQueries({ queryKey: ['admin-agent-session-policies'] }); void queryClient.invalidateQueries({ queryKey: ['admin-agent-session-policies-effective'] }); setNotice('Session policy revision saved.') }} /> : null}
      {canViewMigration || canManageMigration ? <SessionPortabilityPanel api={api} selected={selected} namespaceOptions={policyNamespaces} canView={canViewMigration} canManage={canManageMigration} /> : null}
    </div>
  )
}

function FleetRow({ item, selected, checked, canManage, pending, locale, timezone, onToggle, onSelect, onAction }: { item: AgentSessionFleetItem; selected: boolean; checked: boolean; canManage: boolean; pending: boolean; locale: string; timezone: string; onToggle: () => void; onSelect: () => void; onAction: (action: AgentSessionAdminAction) => void }) {
  const actions = lifecycleActions(item.state)
  return <tr className={selected ? 'session-fleet-row-selected' : ''}>
    <td><input type="checkbox" checked={checked} onChange={onToggle} aria-label={`Select session ${compactId(item.sessionId)}`} /></td>
    <td><button className="table-link session-row-link" type="button" onClick={onSelect}><strong>{compactId(item.sessionId)}</strong><small>{compactId(item.executionId)}</small></button></td>
    <td><span className="cell-subtitle">{item.ownerId || 'Unassigned'}</span></td>
    <td><strong>{item.agentRef || 'Unknown agent'}</strong><small className="cell-subtitle">{item.phase || '—'}</small></td>
    <td><code>{item.namespace}</code></td>
    <td>{item.harness ? <><strong>{item.harness.adapter}</strong><small className="cell-subtitle">{item.harness.adapterVersion}</small></> : '—'}</td>
    <td><span className={`status status-${fleetStatusTone(item.state)}`}><span aria-hidden="true">●</span>{fleetStatusLabel(item.state)}</span></td>
    <td><strong>{metric(item.counters.totalTokens)} tokens</strong><small className={`cell-subtitle status-text-${dependencyTone(item.dependencyHealth)}`}>{dependencyLabel(item)}</small></td>
    <td><time dateTime={item.updatedAt}>{formatDate(item.updatedAt, locale, timezone)}</time></td>
    <td><div className="session-row-actions">{canManage ? actions.map((action) => <button className={`button button-quiet button-compact${action === 'cancel' ? ' button-danger' : ''}`} type="button" key={action} disabled={pending} onClick={() => onAction(action)}>{action === 'pause' ? <Pause size={13} aria-hidden="true" /> : action === 'resume' ? <Play size={13} aria-hidden="true" /> : action === 'retry' ? <RotateCcw size={13} aria-hidden="true" /> : <Square size={13} aria-hidden="true" />}{action}</button>) : null}</div></td>
  </tr>
}

function SessionTrace({ api, item, detail, events, loading, error, locale, timezone }: { api: Parameters<typeof AgentProgressTimeline>[0]['api']; item: AgentSessionFleetItem; detail?: AgentSessionControlSummary; events: AgentSessionControlEvent[]; loading: boolean; error: string | null; locale: string; timezone: string }) {
  return <section className="data-section session-trace" aria-labelledby="session-trace-heading"><header className="section-heading"><div><p className="eyebrow">TRACE / CANONICAL SESSION API</p><h2 id="session-trace-heading">{compactId(item.sessionId)}</h2><p>{item.agentRef || 'Agent session'} · {item.namespace} · execution {compactId(item.executionId)}</p></div><span className={`status status-${fleetStatusTone(item.state)}`}>{fleetStatusLabel(item.state)}</span></header>{loading ? <LoadingState label="Loading session trace" /> : null}{error ? <p className="form-error" role="alert">{error}</p> : null}<div className="detail-facts"><div><small>Owner</small><strong>{item.ownerId || 'Unassigned'}</strong></div><div><small>Harness</small><strong>{item.harness?.adapter || 'Not pinned'}</strong></div><div><small>Dependencies</small><strong>{dependencyLabel(item)}</strong></div><div><small>Envelope</small><strong title={item.envelopeDigest || undefined}>{compactId(item.envelopeDigest)}</strong></div><div><small>Turns / tools</small><strong>{metric(item.counters.turns)} / {metric(item.counters.toolCalls)}</strong></div><div><small>Cost</small><strong>{formatFleetCost(item.counters.costUsd)}</strong></div></div><AgentProgressTimeline api={api} sessionId={item.sessionId} isLive={['RUNNING', 'QUEUED', 'CREATED', 'RESTARTING'].includes(item.state)} locale={locale} timezone={timezone} images={progressImagesFromSessionEvents(events)} /><div className="session-trace-layout"><section><div className="section-heading"><div><p className="eyebrow">EVENT LOG</p><h3>Recorded trace</h3></div><Activity size={17} aria-hidden="true" /></div>{events.length ? <ol className="session-event-list">{events.map((event) => <li key={`${event.eventId}:${event.eventIndex}`}><span className="session-event-marker">#{event.eventIndex}</span><div><strong>{event.eventType}</strong><small>{formatDate(event.occurredAt, locale, timezone)}</small></div></li>)}</ol> : <p className="inline-empty">No trace events are available yet.</p>}</section><section><div className="section-heading"><div><p className="eyebrow">CURRENT PROJECTION</p><h3>Redacted session detail</h3></div><ShieldCheck size={17} aria-hidden="true" /></div>{detail ? <dl className="orchestrator-detail-list"><div><dt>Phase</dt><dd>{detail.phase || '—'}</dd></div><div><dt>Version / epoch</dt><dd>{detail.version ?? '—'} / {detail.executionEpoch ?? '—'}</dd></div><div><dt>Updated</dt><dd>{formatDate(detail.updatedAt, locale, timezone)}</dd></div><div><dt>Result</dt><dd>{detail.error || (detail.finalResult ? 'Structured result available' : 'No result yet')}</dd></div></dl> : <p className="inline-empty">Detail not available.</p>}</section></div><p className="session-redaction-note"><ShieldCheck size={15} aria-hidden="true" />Operational metadata only. Payloads, credentials, prompts, and hidden reasoning are intentionally excluded.</p></section>
}

function HistoryIcon() { return <div className="session-trace-empty-icon" aria-hidden="true"><X size={24} /></div> }

const emptyPolicy: AgentSessionPolicyDraft = {
  admissionEnabled: true,
  maxConcurrency: 10,
  maxTotalTokens: 100000,
  maxCostUsd: '10',
  maxDurationSeconds: 3600,
  retentionSeconds: 86400,
  allowedProviderIds: [],
  allowedHarnessIds: [],
  allowedToolIds: [],
  namespace: null,
  applicationId: null,
}

function policyScopeLabel(policy: AgentSessionPolicyRevision): string {
  if (policy.applicationId) return `Application · ${policy.applicationId}`
  if (policy.namespace) return `Namespace · ${policy.namespace}`
  return 'Tenant default'
}

function policyListValue(value: string[]): string {
  return value.length ? value.join(', ') : 'Any'
}

function effectivePolicySpec(policies: AgentSessionPolicyRevision[]): AgentSessionPolicy {
  const specs = policies.map((policy) => policy.spec)
  const intersectAllowlist = (key: 'allowedProviderIds' | 'allowedHarnessIds' | 'allowedToolIds') => {
    const constrained = specs.filter((spec) => spec[key].length).map((spec) => spec[key])
    if (!constrained.length) return []
    return constrained.slice(1).reduce((allowed, current) => allowed.filter((value) => current.includes(value)), constrained[0])
  }
  return {
    admissionEnabled: specs.every((spec) => spec.admissionEnabled),
    maxConcurrency: Math.min(...specs.map((spec) => spec.maxConcurrency)),
    maxTotalTokens: Math.min(...specs.map((spec) => spec.maxTotalTokens)),
    maxCostUsd: specs.reduce((lowest, spec) => Number(spec.maxCostUsd) < Number(lowest) ? spec.maxCostUsd : lowest, specs[0]?.maxCostUsd || '0'),
    maxDurationSeconds: Math.min(...specs.map((spec) => spec.maxDurationSeconds)),
    retentionSeconds: Math.min(...specs.map((spec) => spec.retentionSeconds)),
    allowedProviderIds: intersectAllowlist('allowedProviderIds'),
    allowedHarnessIds: intersectAllowlist('allowedHarnessIds'),
    allowedToolIds: intersectAllowlist('allowedToolIds'),
  }
}

function SessionPolicyPanel({ api, policies, loading, error, canManage, namespaceOptions, evaluationNamespace, evaluationApplication, onEvaluationNamespace, onEvaluationApplication, effectivePolicies, effectiveLoading, effectiveError, onSaved }: { api: ReturnType<typeof useApiClient>; policies: AgentSessionPolicyRevision[]; loading: boolean; error: string | null; canManage: boolean; namespaceOptions: string[]; evaluationNamespace: string; evaluationApplication: string; onEvaluationNamespace: (value: string) => void; onEvaluationApplication: (value: string) => void; effectivePolicies: AgentSessionPolicyRevision[]; effectiveLoading: boolean; effectiveError: string | null; onSaved: () => void }) {
  const [draft, setDraft] = useState<AgentSessionPolicyDraft>(emptyPolicy)
  const [scope, setScope] = useState<'TENANT' | 'NAMESPACE' | 'APPLICATION'>('TENANT')
  const [saveError, setSaveError] = useState('')
  const save = useMutation({
    mutationFn: (input: AgentSessionPolicyDraft) => api.saveAgentSessionPolicy(input),
    onSuccess: () => { setSaveError(''); setDraft(emptyPolicy); setScope('TENANT'); onSaved() },
    onError: (cause) => {
      const status = (cause as { status?: number }).status
      setSaveError(status === 409 ? 'This policy changed while you were editing it. Reload the current revision, then apply your changes again.' : cause.message)
    },
  })
  function updateDraft<K extends keyof AgentSessionPolicyDraft>(key: K, value: AgentSessionPolicyDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }))
  }
  const edit = (policy: AgentSessionPolicyRevision) => {
    setScope(policy.applicationId ? 'APPLICATION' : policy.namespace ? 'NAMESPACE' : 'TENANT')
    setDraft({ ...policy.spec, namespace: policy.namespace, applicationId: policy.applicationId, expectedRevision: policy.revision })
    setSaveError('')
  }
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (scope === 'APPLICATION' && (!draft.namespace || !draft.applicationId)) {
      setSaveError('Choose a namespace and application before saving an application policy.')
      return
    }
    if (scope === 'NAMESPACE' && !draft.namespace) {
      setSaveError('Choose a namespace before saving a namespace policy.')
      return
    }
    save.mutate({ ...draft, namespace: scope === 'TENANT' ? null : draft.namespace, applicationId: scope === 'APPLICATION' ? draft.applicationId : null })
  }
  const scopeChanged = (value: 'TENANT' | 'NAMESPACE' | 'APPLICATION') => {
    setScope(value)
    if (value === 'TENANT') setDraft((current) => ({ ...current, namespace: null, applicationId: null, expectedRevision: undefined }))
    if (value === 'NAMESPACE') setDraft((current) => ({ ...current, applicationId: null, expectedRevision: undefined }))
    if (value === 'APPLICATION') setDraft((current) => ({ ...current, expectedRevision: undefined }))
  }
  return <section className="data-section session-policy-panel" aria-labelledby="session-policy-heading">
    <header className="section-heading"><div><p className="eyebrow">POLICY / ADMISSION BOUNDARY</p><h2 id="session-policy-heading">Session policy administration</h2><p>Review effective tenant and namespace limits before changing the versioned admission boundary.</p></div><span className="result-count">{policies.length} revisions</span></header>
    {error ? <p className="form-error" role="alert">Unable to load session policies: {error}</p> : null}
    {loading ? <LoadingState label="Loading session policies" /> : <div className="session-policy-layout">
      <section className="session-policy-effective" aria-labelledby="effective-policy-heading"><div className="section-heading"><div><p className="eyebrow">EVALUATE EFFECTIVE</p><h3 id="effective-policy-heading">Resolved policy chain</h3></div><ShieldCheck size={17} aria-hidden="true" /></div><div className="policy-evaluation-controls"><label>Namespace<select value={evaluationNamespace} onChange={(event) => onEvaluationNamespace(event.target.value)}><option value="">Choose namespace</option>{namespaceOptions.map((value) => <option key={value} value={value}>{value}</option>)}</select></label><label>Application (optional)<input value={evaluationApplication} onChange={(event) => onEvaluationApplication(event.target.value)} placeholder="application id" /></label></div>{effectiveError ? <p className="form-error" role="alert">Effective evaluation failed: {effectiveError}</p> : null}{effectiveLoading ? <LoadingState label="Evaluating effective session policies" /> : null}{evaluationNamespace && !effectiveLoading && !effectiveError ? <PolicySummary policies={effectivePolicies} empty="No namespace or application policy applies; the tenant default is unconfigured." /> : <p className="inline-empty">Choose a namespace to evaluate the tenant, namespace, and optional application chain.</p>}</section>
      <section className="session-policy-catalog" aria-labelledby="policy-catalog-heading"><div className="section-heading"><div><p className="eyebrow">VERSIONED CATALOG</p><h3 id="policy-catalog-heading">Exact revisions and provenance</h3></div>{canManage ? <button className="button button-secondary button-compact" type="button" onClick={() => { setDraft(emptyPolicy); setScope('TENANT'); setSaveError('') }}>New revision</button> : null}</div>{policies.length ? <div className="policy-revision-list">{policies.map((policy) => <article key={`${policy.policyId}:${String(policy.revision)}`}><header><div><strong>{policyScopeLabel(policy)}</strong><small>Revision {policy.revision} · {policy.createdBy} · {formatDate(policy.createdAt, 'en', 'UTC')}</small></div>{canManage ? <button className="button button-quiet button-compact" type="button" onClick={() => edit(policy)}>Edit</button> : null}</header><code title={policy.digest}>{policy.digest}</code><PolicyLimitGrid policy={policy.spec} /></article>)}</div> : <p className="inline-empty">No session policy revisions are configured.</p>}</section>
    </div>}
    {canManage ? <form className="session-policy-editor" onSubmit={submit} aria-labelledby="policy-editor-heading"><div className="section-heading"><div><p className="eyebrow">MANAGE / EXPECTED REVISION</p><h3 id="policy-editor-heading">Create or update policy</h3></div><span>{draft.expectedRevision ? `Optimistic update · expects r${draft.expectedRevision}` : 'New revision'}</span></div><div className="policy-editor-grid"><label>Scope<select value={scope} onChange={(event) => scopeChanged(event.target.value as typeof scope)}><option value="TENANT">Tenant default</option><option value="NAMESPACE">Namespace</option><option value="APPLICATION">Application</option></select></label>{scope !== 'TENANT' ? <label>Namespace<select required value={draft.namespace || ''} onChange={(event) => updateDraft('namespace', event.target.value || null)}><option value="">Choose namespace</option>{namespaceOptions.map((value) => <option key={value} value={value}>{value}</option>)}</select></label> : null}{scope === 'APPLICATION' ? <label>Application ID<input required value={draft.applicationId || ''} onChange={(event) => updateDraft('applicationId', event.target.value || null)} /></label> : null}<label className="policy-toggle"><span>Admission</span><select value={draft.admissionEnabled ? 'ENABLED' : 'DISABLED'} onChange={(event) => updateDraft('admissionEnabled', event.target.value === 'ENABLED')}><option value="ENABLED">Enabled</option><option value="DISABLED">Disabled</option></select></label><label>Max concurrency<input type="number" min="1" max="1000" value={draft.maxConcurrency} onChange={(event) => updateDraft('maxConcurrency', event.target.valueAsNumber)} /></label><label>Max total tokens<input type="number" min="1" value={draft.maxTotalTokens} onChange={(event) => updateDraft('maxTotalTokens', event.target.valueAsNumber)} /></label><label>Max cost (USD)<input type="number" min="0" step="0.01" value={draft.maxCostUsd} onChange={(event) => updateDraft('maxCostUsd', event.target.value)} /></label><label>Max duration (seconds)<input type="number" min="1" value={draft.maxDurationSeconds} onChange={(event) => updateDraft('maxDurationSeconds', event.target.valueAsNumber)} /></label><label>Retention (seconds)<input type="number" min="0" value={draft.retentionSeconds} onChange={(event) => updateDraft('retentionSeconds', event.target.valueAsNumber)} /></label><label className="span-two">Allowed providers<input value={draft.allowedProviderIds.join(', ')} onChange={(event) => updateDraft('allowedProviderIds', splitPolicyValues(event.target.value))} placeholder="Any provider" /><small>Comma-separated canonical provider IDs; leave empty for any.</small></label><label className="span-two">Allowed harnesses<input value={draft.allowedHarnessIds.join(', ')} onChange={(event) => updateDraft('allowedHarnessIds', splitPolicyValues(event.target.value))} placeholder="Any harness" /><small>Comma-separated canonical harness IDs; leave empty for any.</small></label><label className="span-two">Allowed tools<input value={draft.allowedToolIds.join(', ')} onChange={(event) => updateDraft('allowedToolIds', splitPolicyValues(event.target.value))} placeholder="Any tool" /><small>Comma-separated canonical tool IDs; leave empty for any.</small></label></div>{saveError ? <p className="form-error" role="alert">{saveError}</p> : null}<button className="button button-primary" type="submit" disabled={save.isPending}>{save.isPending ? 'Saving revision…' : draft.expectedRevision ? 'Save new revision' : 'Create revision'}</button></form> : <p className="permission-note"><ShieldCheck size={15} aria-hidden="true" />You can evaluate policies. Policy changes require the session policy manage capability.</p>}
  </section>
}

function splitPolicyValues(value: string): string[] {
  return value.split(',').map((item) => item.trim()).filter(Boolean)
}

function PolicySummary({ policies, empty }: { policies: AgentSessionPolicyRevision[]; empty: string }) {
  if (!policies.length) return <p className="inline-empty">{empty}</p>
  return <div className="effective-policy-summary"><p>{policies.map((policy) => `${policyScopeLabel(policy)} · r${String(policy.revision)}`).join(' + ')}</p><PolicyLimitGrid policy={effectivePolicySpec(policies)} /><small>Effective limits use the tightest value across the chain. Digest provenance: {policies.map((policy) => policy.digest).join(' · ')}</small></div>
}

function PolicyLimitGrid({ policy }: { policy: AgentSessionPolicy }) {
  return <dl className="policy-limit-grid"><div><dt>Admission</dt><dd>{policy.admissionEnabled ? 'Enabled' : 'Disabled'}</dd></div><div><dt>Limits</dt><dd>{policy.maxConcurrency} concurrent · {policy.maxTotalTokens.toLocaleString()} tokens · ${policy.maxCostUsd}</dd></div><div><dt>Duration / retention</dt><dd>{policy.maxDurationSeconds}s · {policy.retentionSeconds}s</dd></div><div><dt>Allowlists</dt><dd>Providers: {policyListValue(policy.allowedProviderIds)} · Harnesses: {policyListValue(policy.allowedHarnessIds)} · Tools: {policyListValue(policy.allowedToolIds)}</dd></div></dl>
}
