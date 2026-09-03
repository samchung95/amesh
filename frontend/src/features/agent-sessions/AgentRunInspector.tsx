import { Activity, AlertTriangle, Braces, Clock3, ShieldCheck, Wrench } from 'lucide-react'

import type { AgentSessionEvent, AgentSessionSummary, ExecutionState } from '../../api/types'
import { formatDate } from '../../app/format'
import { LoadingState, StatusBadge } from '../../shared/ui'
import {
  buildAgentRunInspectorModel,
  type AgentRunInspectorFactGroup,
} from './agentRunInspectorModel'
import { AgentProgressTimeline, type AgentProgressApi } from './AgentProgressTimeline'
import { progressImagesFromSessionEvents } from './agentProgressModel'

export interface AgentRunInspectorProps {
  session: AgentSessionSummary | null | undefined
  executionState?: ExecutionState | null
  events?: AgentSessionEvent[]
  pending?: boolean
  error?: string | null
  locale?: string
  timezone?: string
  progressApi?: AgentProgressApi
}

function badgeState(state: string): string {
  return state === 'WAITING_APPROVAL' ? 'WAITING' : state
}

function factIcon(group: AgentRunInspectorFactGroup) {
  if (group.key === 'tools') return <Wrench size={16} aria-hidden="true" />
  if (group.key === 'approvals') return <ShieldCheck size={16} aria-hidden="true" />
  if (group.key === 'schema' || group.key === 'final') return <Braces size={16} aria-hidden="true" />
  return <Activity size={16} aria-hidden="true" />
}

export function AgentRunInspector({
  session,
  executionState = null,
  events = [],
  pending = false,
  error = null,
  locale = 'en',
  timezone = 'UTC',
  progressApi,
}: AgentRunInspectorProps) {
  if (pending) return <LoadingState label="Loading agent run evidence" />
  if (error) {
    return <section className="agent-run-inspector state-panel state-error" role="alert" aria-label="Agent run evidence error">
      <AlertTriangle size={24} aria-hidden="true" />
      <div><h2>Agent evidence unavailable</h2><p>{error}</p></div>
    </section>
  }

  const model = buildAgentRunInspectorModel({ session, executionState, events })
  if (model.status === 'empty') {
    return <section className="agent-run-inspector state-panel state-empty" aria-label="Agent run inspector empty state">
      <Activity size={28} aria-hidden="true" />
      <div><h2>No agent session selected</h2><p>Agent session summaries and canonical events will appear here when this execution includes an agent task.</p></div>
    </section>
  }

  const redactedCount = model.events.filter((event) => event.redacted).length
  return <section className="agent-run-inspector" aria-label="Agent run inspector">
    <header className="agent-run-inspector-heading">
      <div><p className="eyebrow">AGENT RUN / CANONICAL EVIDENCE</p><h2>Agent session</h2><p><code>{session?.sessionId}</code> · attempt {model.attempt}</p></div>
      <div className="agent-run-inspector-state"><StatusBadge state={badgeState(model.displayState)} /><span>{model.displayState.replaceAll('_', ' ')}</span></div>
    </header>

    {model.status === 'malformed' ? <p className="agent-run-inspector-warning" role="alert"><AlertTriangle size={16} aria-hidden="true" />{String(model.malformedCount)} canonical record{model.malformedCount === 1 ? '' : 's'} could not be validated; affected details are withheld.</p> : null}
    {redactedCount ? <p className="agent-run-inspector-redaction" role="status"><ShieldCheck size={16} aria-hidden="true" />{String(redactedCount)} event{redactedCount === 1 ? '' : 's'} include server-redacted fields. Hidden rationale and secrets are never rendered.</p> : null}

    <section className="agent-run-summary" aria-label="Agent session summary">
      <div><small>Current state</small><strong>{model.displayState.replaceAll('_', ' ')}</strong></div>
      <div><small>Session phase</small><strong>{model.phase}</strong></div>
      <div><small>Current turn</small><strong>{model.turn || 'Not started'}</strong></div>
      <div><small>Execution state</small><strong>{model.executionState || 'Not supplied'}</strong></div>
    </section>

    <div className="agent-run-facts" aria-label="Agent run facts">
      {model.facts.map((group) => <details className="agent-run-fact-group" key={group.key} open={group.facts.length > 0}>
        <summary>{factIcon(group)}<strong>{group.label}</strong><span>{group.facts.length ? `${String(group.facts.length)} recorded` : 'Empty'}</span></summary>
        {group.facts.length ? <dl>{group.facts.map((item) => <div key={`${item.label}:${item.value}`}><dt>{item.label}</dt><dd className={item.redacted ? 'agent-run-fact-redacted' : undefined}>{group.key === 'final' && !item.redacted ? <pre>{item.value}</pre> : item.value}</dd></div>)}</dl> : <p className="inline-empty">{group.emptyLabel}</p>}
      </details>)}
    </div>

    <section className="agent-run-events" aria-labelledby="agent-run-events-heading">
      <div className="section-heading"><div><p className="eyebrow">DURABLE SESSION JOURNAL</p><h3 id="agent-run-events-heading">Chronological canonical events</h3></div><span>{model.events.length} event{model.events.length === 1 ? '' : 's'}</span></div>
      {model.events.length ? <ol className="agent-run-event-list">
        {model.events.map((event) => <li className={`agent-run-event${event.malformed ? ' agent-run-event-malformed' : ''}`} key={`${event.eventId}:${String(event.eventIndex)}`}>
          <div className="agent-run-event-marker"><span>{event.eventIndex === null ? '?' : `#${String(event.eventIndex)}`}</span></div>
          <div className="agent-run-event-body">
            <div className="agent-run-event-meta"><code>{event.eventType}</code>{event.occurredAt ? <time dateTime={event.occurredAt}>{formatDate(event.occurredAt, locale, timezone)}</time> : <span>Timestamp unavailable</span>}</div>
            <strong>{event.summary}</strong>
            {event.redacted ? <span className="agent-run-fact-redacted">Redacted fields</span> : null}
            {event.malformed ? <p className="form-error">Malformed evidence; payload withheld until the canonical record is repaired.</p> : <details><summary>Event evidence details</summary><dl className="agent-run-event-details"><div><dt>Event key</dt><dd><code>{event.eventKey}</code></dd></div><div><dt>Event ID</dt><dd><code>{event.eventId}</code></dd></div>{event.facts.map((item) => <div key={`${item.label}:${item.value}`}><dt>{item.label}</dt><dd className={item.redacted ? 'agent-run-fact-redacted' : undefined}>{item.value}</dd></div>)}{event.payloadText ? <div className="agent-run-event-payload"><dt>Sanitized payload</dt><dd><pre>{event.payloadText}</pre></dd></div> : null}</dl></details>}
          </div>
        </li>)}
      </ol> : <p className="inline-empty">No canonical session events are available yet. The summary above remains the only authorized evidence.</p>}
    </section>
    {progressApi && session?.sessionId ? <AgentProgressTimeline api={progressApi} sessionId={session.sessionId} isLive={['RUNNING', 'QUEUED', 'CREATED', 'RESTARTING'].includes(String(executionState || session.state))} locale={locale} timezone={timezone} images={progressImagesFromSessionEvents(events)} /> : null}

    <footer className="agent-run-inspector-footnote"><Clock3 size={15} aria-hidden="true" /><span>Events are ordered by canonical event index. Evidence is redacted at the server boundary; this view does not infer hidden model rationale.</span></footer>
  </section>
}
