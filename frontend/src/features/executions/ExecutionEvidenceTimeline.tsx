import { Activity, FileArchive, Gauge, ScrollText, SquareFunction } from 'lucide-react'
import { useMemo, useState } from 'react'

import { formatDate } from '../../app/format'
import type { ExecutionEvidenceEvent, ExecutionEvidenceKind } from '../../api/types'

const kinds: Array<ExecutionEvidenceKind | 'ALL'> = ['ALL', 'STATE', 'LOG', 'METRIC', 'OUTPUT', 'ARTIFACT']

function readableValue(value: unknown, fallback: string): string {
  if (value === null || value === undefined) return fallback
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean' || typeof value === 'bigint') return String(value)
  try {
    return JSON.stringify(value) ?? fallback
  } catch {
    return fallback
  }
}

function eventSummary(event: ExecutionEvidenceEvent): string {
  const payload = event.payload
  if (event.kind === 'LOG') return readableValue(payload.message, event.event_type)
  if (event.kind === 'METRIC') return `${readableValue(payload.name, 'metric')} = ${readableValue(payload.value, '—')}${payload.unit ? ` ${readableValue(payload.unit, '')}` : ''}`
  if (event.kind === 'ARTIFACT') return readableValue(payload.uri, event.event_type)
  if (event.kind === 'OUTPUT') return `${readableValue(payload.sizeBytes, '0')} bytes committed`
  return readableValue(payload.reason ?? payload.eventType, event.event_type)
}

function KindIcon({ kind }: { kind: ExecutionEvidenceKind }) {
  if (kind === 'LOG') return <ScrollText size={16} aria-hidden="true" />
  if (kind === 'METRIC') return <Gauge size={16} aria-hidden="true" />
  if (kind === 'OUTPUT') return <SquareFunction size={16} aria-hidden="true" />
  if (kind === 'ARTIFACT') return <FileArchive size={16} aria-hidden="true" />
  return <Activity size={16} aria-hidden="true" />
}

interface Props {
  events: ExecutionEvidenceEvent[]
  locale: string
  timezone: string
}

export function ExecutionEvidenceTimeline({ events, locale, timezone }: Props) {
  const [kind, setKind] = useState<ExecutionEvidenceKind | 'ALL'>('ALL')
  const visible = useMemo(
    () => events.filter((event) => kind === 'ALL' || event.kind === kind),
    [events, kind],
  )

  return (
    <section className="data-section evidence-section" aria-labelledby="evidence-heading">
      <div className="section-heading evidence-heading">
        <div><p className="eyebrow">DURABLE EVIDENCE</p><h2 id="evidence-heading">Live execution timeline</h2></div>
        <label className="filter-select evidence-filter">
          <span>Event kind</span>
          <select value={kind} onChange={(event) => setKind(event.target.value as ExecutionEvidenceKind | 'ALL')}>
            {kinds.map((value) => <option key={value} value={value}>{value === 'ALL' ? 'All events' : value}</option>)}
          </select>
        </label>
      </div>
      {visible.length === 0 ? <p className="inline-empty">No {kind === 'ALL' ? '' : `${kind.toLowerCase()} `}evidence has arrived yet.</p> : null}
      <ol className="evidence-timeline">
        {visible.map((event) => (
          <li key={event.event_id} className={`evidence-event evidence-${event.kind.toLowerCase()}`}>
            <span className="evidence-icon"><KindIcon kind={event.kind} /></span>
            <div className="evidence-body">
              <div className="evidence-meta"><strong>{event.kind}</strong><code>{event.event_type}</code><span>#{event.cursor}</span></div>
              <p>{eventSummary(event)}</p>
              <small>{formatDate(event.occurred_at, locale, timezone)}{event.task_run_id ? ` · task ${event.task_run_id.slice(0, 8)}` : ''}</small>
              <details><summary>Event payload</summary><pre>{JSON.stringify(event.payload, null, 2)}</pre></details>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
