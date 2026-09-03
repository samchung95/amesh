import { useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Activity, Ban, CheckCircle2, CircleDot, History, Pause, Play, RotateCcw, ShieldCheck } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'

import type { AgentSessionControlEvent, AgentSessionCreateDraft, AgentSessionControlSummary, ImageArtifactRef, UiSession } from '../../api/types'
import { formatDate } from '../../app/format'
import { useApiClient } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { CatalogSelect, EmptyState, ErrorState, LoadingState, StatusBadge } from '../../shared/ui'
import { AgentProgressTimeline } from './AgentProgressTimeline'
import { agentPinnedProfile, agentResourceOptions, currentHarnessAlias, harnessCatalogOptions, mergeSessionSummary, sessionCanCancel, sessionCanPause, sessionCanResume, sessionCanRetry, sessionEventLabel, sessionHarnessLabel, sessionIsLive } from './agentSessionControlModel'
import { progressImagesFromSessionEvents, type AgentProgressImageReference } from './agentProgressModel'

function sessionIdLabel(id: string): string {
  return id.length > 16 ? `${id.slice(0, 8)}…${id.slice(-6)}` : id
}

function counter(value: number | undefined): string {
  return value === undefined ? '—' : value.toLocaleString()
}

function budget(value: unknown, suffix = ''): string {
  return typeof value === 'number' || typeof value === 'string' ? `${String(value)}${suffix}` : '∞'
}

function progressImageReference(image: ImageArtifactRef): AgentProgressImageReference {
  return {
    reference: image.artifact.reference,
    mediaType: image.artifact.mediaType ?? null,
    sizeBytes: image.artifact.sizeBytes,
    checksumSha256: image.artifact.checksumSha256,
    altText: image.display.altText || image.display.filename,
  }
}

export function AgentSessionsPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  const queryClient = useQueryClient()
  const [params, setParams] = useSearchParams()
  const selectedId = params.get('session')
  const canExecute = session.capabilities['agentSessions.create']
  const canManage = session.capabilities['agentSessions.manage']
  const canViewSessions = session.capabilities['agentSessions.view']
  const [agentRef, setAgentRef] = useState('')
  const [input, setInput] = useState('{}')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [notice, setNotice] = useState('')
  const [uploadingImage, setUploadingImage] = useState(false)
  const [sessionImages, setSessionImages] = useState<Record<string, AgentProgressImageReference[]>>({})

  const resources = useQuery({
    queryKey: ['agent-session-resources', settings.tenant, settings.namespace],
    queryFn: () => api.agentResources(settings.namespace || ''),
    enabled: Boolean(settings.namespace && session.capabilities['agents.view']),
    staleTime: 10_000,
  })
  const harnesses = useQuery({
    queryKey: ['agent-session-harnesses', settings.tenant],
    queryFn: api.agentSessionHarnesses,
    enabled: canViewSessions,
    staleTime: 30_000,
  })
  const sessions = useQuery({
    queryKey: ['agent-sessions', settings.tenant, settings.namespace],
    queryFn: api.agentSessions,
    enabled: canViewSessions,
    refetchInterval: 5_000,
  })
  const selected = sessions.data?.find((item) => item.sessionId === selectedId) || null
  const detail = useQuery({
    queryKey: ['agent-session', settings.tenant, selectedId],
    queryFn: () => api.agentSession(selectedId || ''),
    enabled: Boolean(selectedId),
    refetchInterval: selected && sessionIsLive(selected) ? 3_000 : false,
  })
  const events = useQuery({
    queryKey: ['agent-session-events', settings.tenant, selectedId],
    queryFn: () => api.agentSessionEvents(selectedId || '', 0, 100),
    enabled: Boolean(selectedId),
    refetchInterval: selected && sessionIsLive(selected) ? 3_000 : false,
  })
  const result = useQuery({
    queryKey: ['agent-session-result', settings.tenant, selectedId],
    queryFn: () => api.agentSessionResult(selectedId || ''),
    enabled: Boolean(selectedId && (['SUCCEEDED', 'FAILED', 'CANCELLED'].includes(selected?.state || '') || ['SUCCEEDED', 'FAILED', 'CANCELLED'].includes(detail.data?.state || ''))),
    staleTime: 10_000,
  })
  const agentOptions = useMemo(() => agentResourceOptions(resources.data || [], 'AGENT'), [resources.data])
  const harnessOptions = useMemo(() => harnessCatalogOptions(harnesses.data || {}), [harnesses.data])
  const currentHarness = useMemo(() => currentHarnessAlias(harnesses.data || {}), [harnesses.data])

  const refresh = async (next: AgentSessionControlSummary) => {
    setParams({ session: next.sessionId })
    await queryClient.invalidateQueries({ queryKey: ['agent-sessions', settings.tenant, settings.namespace] })
    await queryClient.invalidateQueries({ queryKey: ['agent-session', settings.tenant, next.sessionId] })
    await queryClient.invalidateQueries({ queryKey: ['agent-session-events', settings.tenant, next.sessionId] })
  }
  const create = useMutation({
    mutationFn: (request: AgentSessionCreateDraft) => api.createAgentSession(request),
    onSuccess: (next) => { setNotice(`Session ${sessionIdLabel(next.sessionId)} started.`); void refresh(next) },
  })
  const lifecycle = useMutation({
    mutationFn: ({ action, id, version, epoch }: { action: 'cancel' | 'pause' | 'retry' | 'resume'; id: string; version?: number; epoch?: number }) => {
      const control = { expectedVersion: version, expectedEpoch: epoch, reason: `Operator requested ${action}.` }
      if (action === 'cancel') return api.cancelAgentSession(id, control)
      if (action === 'pause') return api.pauseAgentSession(id, control)
      if (action === 'retry') return api.retryAgentSession(id, control)
      return api.resumeAgentSession(id, control)
    },
    onSuccess: (next) => { setNotice(`Session ${sessionIdLabel(next.sessionId)} updated.`); void refresh(next) },
  })

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    if (!agentRef) { setFormError('Choose an agent revision from the authorized catalog.'); return }
    try {
      const parsed = JSON.parse(input) as unknown
      if (parsed === null || Array.isArray(parsed) || typeof parsed !== 'object') throw new Error('Input must be a JSON object.')
      const requestInput = parsed as Record<string, unknown>
      let uploadedImage: ImageArtifactRef | null = null
      if (imageFile) {
        if (!settings.namespace) throw new Error('Choose a namespace before attaching an image.')
        setUploadingImage(true)
        try {
          uploadedImage = await api.uploadNamespaceImage(settings.namespace, `session-inputs/${crypto.randomUUID()}-${imageFile.name}`, imageFile)
          requestInput.image = uploadedImage
        } finally {
          setUploadingImage(false)
        }
      }
      create.mutate(
        { agentRef, input: requestInput },
        {
          onSuccess: (next) => {
            if (uploadedImage) {
              setSessionImages((current) => ({
                ...current,
                [next.sessionId]: [progressImageReference(uploadedImage)],
              }))
            }
          },
        },
      )
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Input must be valid JSON.')
    }
  }

  if (sessions.isPending) return <div className="page-stack"><LoadingState label="Loading agent sessions" /></div>
  if (sessions.error) return <div className="page-stack"><ErrorState message={sessions.error.message} retry={() => void sessions.refetch()} /></div>

  const active = selected && detail.data ? mergeSessionSummary(selected, detail.data) : detail.data || selected
  const activeImages = active
    ? Array.from(new Map([
      ...progressImagesFromSessionEvents(events.data?.events || []),
      ...(sessionImages[active.sessionId] || []),
    ].map((image) => [`${image.reference}:${image.checksumSha256}`, image])).values())
    : []
  return (
    <div className="page-stack agent-session-control-room">
      <header className="page-heading"><div><p className="eyebrow">OPERATE / SESSION SERVICE</p><h1>Agent sessions</h1><p>Start, observe, and safely recover bounded agent work. Prompts, credentials, and hidden reasoning never appear here.</p></div><span className="live-indicator"><i />{sessions.data?.filter(sessionIsLive).length || 0} active</span></header>
      {notice ? <p className="permission-note" role="status"><CheckCircle2 size={16} aria-hidden="true" />{notice}</p> : null}
      <div className="session-control-grid">
        <section className="data-section" aria-labelledby="start-session-heading">
          <div className="section-heading"><div><p className="eyebrow">NEW RUN</p><h2 id="start-session-heading">Start an agent session</h2></div><Play size={18} aria-hidden="true" /></div>
          <p className="session-help">Choose immutable catalog revisions. The session service applies the policy boundary and records the resulting provenance.</p>
          <form className="session-start-form" onSubmit={(event) => { void submit(event) }}>
            <CatalogSelect label="Agent revision" value={agentRef} options={agentOptions} onChange={setAgentRef} emptyLabel="Choose an agent" loading={resources.isPending} required helpText="Only authorized revisions are offered." />
            <label className="session-pinned-profile">Model profile <small>The agent definition pins this exact policy revision; it cannot be changed for one session.</small><strong>{agentPinnedProfile(resources.data || [], agentRef)}</strong></label>
            <CatalogSelect label="Harness adapter" value={currentHarness} options={harnessOptions} onChange={() => undefined} disabled helpText={harnesses.error ? 'Harness registry is unavailable; the service will report the persisted pin after start.' : 'Registry-derived service default; the exact pin is immutable after start.'} />
            <label>Task input <small>JSON object passed to the agent boundary; no prompt or secret fields are displayed.</small><textarea value={input} onChange={(event) => setInput(event.target.value)} spellCheck={false} aria-label="Task input JSON" /></label>
            <label className="file-button">Attach an image (optional)<input type="file" accept="image/gif,image/jpeg,image/png,image/webp" onChange={(event) => setImageFile(event.target.files?.[0] || null)} />{imageFile ? `${imageFile.name} · ${Math.ceil(imageFile.size / 1024)} KB` : 'Choose a governed image'}</label>
            {formError ? <p className="form-error" role="alert">{formError}</p> : null}
            {create.error ? <p className="form-error" role="alert">{create.error.message}</p> : null}
            <button className="button button-primary" type="submit" disabled={create.isPending || uploadingImage || !canExecute}><Play size={16} aria-hidden="true" />{uploadingImage ? 'Uploading image…' : create.isPending ? 'Starting…' : 'Start session'}</button>
            {!canExecute ? <small className="permission-note"><ShieldCheck size={15} />Your role can inspect sessions but cannot start them.</small> : null}
          </form>
        </section>
        <section className="data-section" aria-labelledby="session-list-heading">
          <div className="section-heading"><div><p className="eyebrow">DURABLE RUNS</p><h2 id="session-list-heading">Session history</h2></div><span>{sessions.data?.length || 0} sessions</span></div>
          {!sessions.data?.length ? <EmptyState title="No agent sessions yet" body="Start a session to see its state, budget usage, and trace here." /> : <div className="session-list">{sessions.data.map((item) => <button className={`session-list-item${item.sessionId === selectedId ? ' selected' : ''}`} type="button" key={item.sessionId} onClick={() => setParams({ session: item.sessionId })}><span><StatusBadge state={item.state} /><strong>{sessionIdLabel(item.sessionId)}</strong></span><small>{item.agentRef || 'Agent revision unavailable'} · {formatDate(item.updatedAt, settings.locale, settings.timezone)}</small><span className="session-list-phase">{item.phase || 'State recorded'}</span></button>)}</div>}
        </section>
      </div>
      {active ? <SessionDetail api={api} images={activeImages} session={active} result={result.data} events={events.data?.events || []} loading={detail.isPending || events.isPending} error={detail.error?.message || events.error?.message || result.error?.message || null} locale={settings.locale} timezone={settings.timezone} canManage={canManage} onAction={(action) => lifecycle.mutate({ action, id: active.sessionId, version: active.version ?? undefined, epoch: active.executionEpoch ?? undefined })} lifecyclePending={lifecycle.isPending} /> : <section className="data-section session-empty-detail"><History size={24} aria-hidden="true" /><div><h2>Choose a session to inspect</h2><p>The control room keeps run status, trace events, usage, budgets, and structured output in one bounded view.</p></div></section>}
    </div>
  )
}

function SessionDetail({ api, images, session, result, events, loading, error, locale, timezone, canManage, onAction, lifecyclePending }: { api: Parameters<typeof AgentProgressTimeline>[0]['api']; images: AgentProgressImageReference[]; session: AgentSessionControlSummary; result?: { result?: Record<string, unknown> | null; error?: string | null }; events: AgentSessionControlEvent[]; loading: boolean; error: string | null; locale: string; timezone: string; canManage: boolean; onAction: (action: 'cancel' | 'pause' | 'retry' | 'resume') => void; lifecyclePending: boolean }) {
  const current = session
  return <section className="data-section session-detail" aria-labelledby="session-detail-heading">
    <header className="section-heading"><div><p className="eyebrow">SESSION / {sessionIdLabel(current.sessionId)}</p><h2 id="session-detail-heading">{current.agentRef || 'Agent session'}</h2><p className="session-provenance" title={current.envelopeDigest || undefined}><CircleDot size={14} aria-hidden="true" />{sessionHarnessLabel(current)} · {current.envelopeDigest ? `envelope ${current.envelopeDigest.slice(0, 19)}…` : 'capability pin pending'} · exact pins are immutable after start</p></div><StatusBadge state={current.state} /></header>
    {loading ? <LoadingState label="Refreshing session evidence" /> : null}
    {error ? <p className="form-error" role="alert">{error}</p> : null}
    <div className="session-facts" aria-label="Session status and usage"><div><small>Phase</small><strong>{current.phase || 'Not reported'}</strong></div><div><small>Turns</small><strong>{counter(current.counters?.turns)}</strong></div><div><small>Tool calls</small><strong>{counter(current.counters?.toolCalls)}</strong></div><div><small>Total tokens</small><strong>{counter(current.counters?.totalTokens)}</strong></div><div><small>Cost</small><strong>{current.counters?.costUsd ? `$${current.counters.costUsd}` : '—'}</strong></div><div><small>Updated</small><strong>{formatDate(current.updatedAt, locale, timezone)}</strong></div></div>
    {current.budgets ? <div className="session-budget"><strong>Declared ceilings</strong><span>{budget(current.budgets.maxTurns)} turns · {budget(current.budgets.maxToolCalls)} tools · {budget(current.budgets.maxTotalTokens)} tokens · {budget(current.budgets.maxCostUsd, ' USD')}</span></div> : null}
    <AgentProgressTimeline api={api} sessionId={current.sessionId} isLive={sessionIsLive(current)} locale={locale} timezone={timezone} images={images} />
    <div className="session-detail-grid"><section><div className="section-heading"><div><p className="eyebrow">TRACE</p><h3>Recorded events</h3></div><Activity size={17} aria-hidden="true" /></div>{events.length ? <ol className="session-event-list">{events.map((event) => <li key={`${event.eventId}:${event.eventIndex}`}><span className="session-event-marker">#{event.eventIndex}</span><div><strong>{sessionEventLabel(event)}</strong><small>{event.eventType} · {formatDate(event.occurredAt, locale, timezone)}</small></div></li>)}</ol> : <p className="inline-empty">No trace events are available yet.</p>}</section><section><div className="section-heading"><div><p className="eyebrow">OUTPUT</p><h3>Result or error</h3></div><CheckCircle2 size={17} aria-hidden="true" /></div>{current.error || result?.error ? <p className="form-error">{current.error || result?.error}</p> : current.result || current.finalResult || result?.result ? <pre className="session-result">{JSON.stringify(current.result || current.finalResult || result?.result, null, 2)}</pre> : <p className="inline-empty">No structured result yet.</p>}</section></div>
    <div className="session-actions"><div className="button-row">{canManage && sessionCanPause(current) ? <button className="button button-secondary" type="button" disabled={lifecyclePending} onClick={() => onAction('pause')}><Pause size={16} />Pause</button> : null}{canManage && sessionCanCancel(current) ? <button className="button button-danger" type="button" disabled={lifecyclePending} onClick={() => onAction('cancel')}><Ban size={16} />Cancel</button> : null}{canManage && sessionCanResume(current) ? <button className="button button-secondary" type="button" disabled={lifecyclePending} onClick={() => onAction('resume')}><RotateCcw size={16} />Resume</button> : null}{canManage && sessionCanRetry(current) ? <button className="button button-secondary" type="button" disabled={lifecyclePending} onClick={() => onAction('retry')}><RotateCcw size={16} />Retry</button> : null}</div>{!canManage ? <small className="permission-note"><ShieldCheck size={15} />Lifecycle actions require session operator access.</small> : null}</div>
  </section>
}
