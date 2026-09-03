import { AlertTriangle, CheckCircle2, CircleDot, Image as ImageIcon, LoaderCircle, Wifi, WifiOff } from 'lucide-react'
import { useEffect, useState } from 'react'

import type { AgentProgressEvent, AgentProgressHeartbeat, AgentProgressStreamItem } from '../../api/types'
import { formatDate } from '../../app/format'
import { appendAgentProgress, progressLabel, progressTone, type AgentProgressImageReference } from './agentProgressModel'

export interface AgentProgressApi {
  agentSessionProgress: (sessionId: string, after?: string, limit?: number) => Promise<{ sessionId: string; events: AgentProgressEvent[]; nextCursor: string }>
  streamAgentSessionProgress: (sessionId: string, after: string | null, onItem: (item: AgentProgressStreamItem) => void, signal: AbortSignal) => Promise<void>
}

function isHeartbeat(item: AgentProgressStreamItem): item is AgentProgressHeartbeat {
  return 'type' in item && item.type === 'heartbeat'
}

function safeThumbnailUrl(value: string | null | undefined): string | null {
  if (!value || value.startsWith('data:') || value.startsWith('blob:') || value.startsWith('javascript:')) return null
  if (value.startsWith('/api/')) return value
  return null
}

function formatSize(sizeBytes: number): string {
  if (sizeBytes < 1024) return `${sizeBytes} B`
  if (sizeBytes < 1024 * 1024) return `${Math.round(sizeBytes / 1024)} KB`
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`
}

export function AgentProgressTimeline({
  api,
  sessionId,
  isLive = false,
  locale = 'en',
  timezone = 'UTC',
  images = [],
}: {
  api: AgentProgressApi
  sessionId: string
  isLive?: boolean
  locale?: string
  timezone?: string
  images?: AgentProgressImageReference[]
}) {
  const [events, setEvents] = useState<AgentProgressEvent[]>([])
  const [state, setState] = useState<'loading' | 'connecting' | 'live' | 'reconnecting' | 'complete' | 'error'>('loading')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    let retryTimer: number | null = null
    let retrying = false
    let localCursor: string | null = null
    let terminal = false
    let knownEvents: AgentProgressEvent[] = []

    const receive = (item: AgentProgressStreamItem) => {
      if (isHeartbeat(item)) {
        localCursor = item.cursor
        return
      }
      const next = appendAgentProgress(knownEvents, [item])
      knownEvents = next.events
      localCursor = next.cursor
      terminal = next.isTerminal
      setEvents(next.events)
      setState('live')
    }

    const run = async () => {
      try {
        const page = await api.agentSessionProgress(sessionId, undefined, 100)
        if (controller.signal.aborted) return
        const seeded = appendAgentProgress([], page.events)
        knownEvents = seeded.events
        localCursor = page.nextCursor || seeded.cursor
        terminal = seeded.isTerminal
        setEvents(seeded.events)
        setState(terminal || !isLive ? 'complete' : 'connecting')
        if (terminal || !isLive) return
      } catch (cause) {
        if (controller.signal.aborted) return
        setError(cause instanceof Error ? cause.message : 'Unable to load agent progress.')
        setState('error')
        return
      }

      while (!controller.signal.aborted && !terminal) {
        try {
          setState(retrying ? 'reconnecting' : 'connecting')
          await api.streamAgentSessionProgress(sessionId, localCursor, receive, controller.signal)
          if (terminal || controller.signal.aborted) break
          retrying = true
          setState('reconnecting')
        } catch (cause) {
          if (controller.signal.aborted) break
          retrying = true
          setError(cause instanceof Error ? cause.message : 'Progress stream interrupted.')
          setState('reconnecting')
        }
        if (!controller.signal.aborted && !terminal) {
          await new Promise<void>((resolve) => {
            retryTimer = window.setTimeout(resolve, 1000)
          })
        }
      }
      if (!controller.signal.aborted && terminal) setState('complete')
    }
    void run()
    return () => {
      controller.abort()
      if (retryTimer !== null) window.clearTimeout(retryTimer)
    }
  }, [api, isLive, sessionId])

  return <section className="agent-progress-timeline" aria-labelledby={`agent-progress-heading-${sessionId}`}>
    <header className="section-heading">
      <div><p className="eyebrow">LIVE / SAFE PROGRESS</p><h3 id={`agent-progress-heading-${sessionId}`}>Run timeline</h3></div>
      <span className="agent-progress-connection" role="status" aria-live="polite">
        {state === 'loading' ? <><LoaderCircle size={15} aria-hidden="true" />Loading</> : null}
        {state === 'connecting' ? <><Wifi size={15} aria-hidden="true" />Connecting</> : null}
        {state === 'live' ? <><Wifi size={15} aria-hidden="true" />Live</> : null}
        {state === 'reconnecting' ? <><WifiOff size={15} aria-hidden="true" />Reconnecting</> : null}
        {state === 'complete' ? <><CheckCircle2 size={15} aria-hidden="true" />Complete</> : null}
        {state === 'error' ? <><AlertTriangle size={15} aria-hidden="true" />Unavailable</> : null}
      </span>
    </header>
    {error && state !== 'reconnecting' ? <p className="form-error" role="alert">{error}</p> : null}
    {state === 'reconnecting' && error ? <p className="permission-note" role="status">The live connection was interrupted. Reconnecting from the last durable cursor.</p> : null}
    {!events.length && state === 'loading' ? <p className="inline-empty">Loading chronological progress…</p> : null}
    {!events.length && state !== 'loading' && state !== 'error' ? <p className="inline-empty">No safe progress has been recorded yet.</p> : null}
    {events.length ? <ol className="agent-progress-list" aria-label="Chronological agent progress">
      {events.map((event) => {
        const tone = progressTone(event.frame)
        return <li className={`agent-progress-item agent-progress-${tone}`} key={event.eventId}>
          <span className="agent-progress-marker" aria-hidden="true"><CircleDot size={14} /></span>
          <div className="agent-progress-body">
            <div className="agent-progress-meta"><strong>{event.frame.activity}</strong><span>{event.frame.status}</span><time dateTime={event.frame.occurredAt}>{formatDate(event.frame.occurredAt, locale, timezone)}</time></div>
            <p>{progressLabel(event.frame)}</p>
            {event.frame.turn ? <small>Turn {event.frame.turn}{event.frame.segmentId ? ` · segment ${event.frame.segmentId.slice(0, 8)}…` : ''}</small> : null}
          </div>
        </li>
      })}
    </ol> : null}
    {images.length ? <section className="agent-progress-images" aria-labelledby={`agent-progress-images-heading-${sessionId}`}>
      <div className="section-heading"><div><p className="eyebrow">INPUT / GOVERNED MEDIA</p><h4 id={`agent-progress-images-heading-${sessionId}`}>Attached images</h4></div><ImageIcon size={16} aria-hidden="true" /></div>
      <div className="agent-progress-image-list">{images.map((image) => {
        const thumbnail = safeThumbnailUrl(image.thumbnailUrl)
        return <figure key={`${image.reference}:${image.checksumSha256}`} className="agent-progress-image">
          {thumbnail ? <img src={thumbnail} alt={image.altText || 'Attached image'} loading="lazy" /> : <span className="agent-progress-image-placeholder" aria-hidden="true"><ImageIcon size={22} /></span>}
          <figcaption><strong>{image.altText || image.reference}</strong><small>{image.mediaType || 'image'} · {formatSize(image.sizeBytes)} · {image.checksumSha256.slice(0, 14)}…</small></figcaption>
        </figure>
      })}</div>
    </section> : null}
  </section>
}
