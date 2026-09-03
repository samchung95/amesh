import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Activity, Pause, Play, RadioTower, RefreshCw, RotateCcw, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import type { TriggerOccurrenceState, TriggerRuntimeState, UiSession } from '../../api/types'
import { compactId, formatDate } from '../../app/format'
import { useApiClient, useTriggerOccurrences, useTriggerRuntime } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { EmptyState, ErrorState, LoadingState, StatusBadge } from '../../shared/ui'

const occurrenceStates: TriggerOccurrenceState[] = [
  'ACCEPTED',
  'DEFERRED',
  'PROCESSING',
  'RETRY_WAIT',
  'SUCCEEDED',
  'DEAD_LETTERED',
]

export function TriggersPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const triggers = useTriggerRuntime(session.capabilities['triggers.view'])
  const occurrences = useTriggerOccurrences(session.capabilities['triggers.view'])
  const [query, setQuery] = useState('')
  const [state, setState] = useState<TriggerOccurrenceState | ''>('')
  const canManage = session.capabilities['triggers.manage']

  const refresh = async () => {
    await Promise.all([triggers.refetch(), occurrences.refetch()])
  }
  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['triggers'] }),
      queryClient.invalidateQueries({ queryKey: ['trigger-occurrences'] }),
    ])
  }
  const pauseMutation = useMutation({
    mutationFn: ({ trigger, paused }: { trigger: TriggerRuntimeState; paused: boolean }) =>
      api.setTriggerPaused(
        trigger.namespace,
        trigger.flow_id,
        trigger.trigger_id,
        paused,
        paused ? 'Paused from trigger monitor' : 'Resumed from trigger monitor',
      ),
    onSuccess: invalidate,
  })
  const replayMutation = useMutation({
    mutationFn: (occurrenceId: string) =>
      api.replayTriggerOccurrence(occurrenceId, 'Replayed from trigger monitor'),
    onSuccess: invalidate,
  })

  const runtimeRows = triggers.data || []
  const occurrenceRows = useMemo(
    () =>
      (occurrences.data || []).filter((item) => {
        const haystack = `${item.namespace}.${item.flow_id} ${item.trigger_id} ${item.occurrence_key}`
          .toLowerCase()
        return (!state || item.state === state) && haystack.includes(query.toLowerCase())
      }),
    [occurrences.data, query, state],
  )
  const totals = runtimeRows.reduce(
    (current, trigger) => ({
      active: current.active + (trigger.active && !trigger.paused ? 1 : 0),
      paused: current.paused + (trigger.paused ? 1 : 0),
      pending: current.pending + trigger.pending_count,
      dead: current.dead + trigger.dead_letter_count,
    }),
    { active: 0, paused: 0, pending: 0, dead: 0 },
  )
  const error = triggers.error || occurrences.error || pauseMutation.error || replayMutation.error
  const pendingAction = pauseMutation.isPending || replayMutation.isPending

  return (
    <div className="page-stack">
      <header className="page-heading trigger-heading">
        <div>
          <p className="eyebrow">OPERATE / OCCURRENCES</p>
          <h1>Trigger runtime</h1>
          <p>Live source health, durable checkpoints, retries, dead letters and replay lineage.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={() => void refresh()} disabled={triggers.isFetching || occurrences.isFetching}>
          <RefreshCw className={triggers.isFetching || occurrences.isFetching ? 'spin' : ''} size={17} aria-hidden="true" />
          Refresh
        </button>
      </header>

      <section className="metric-strip" aria-label="Trigger summary">
        <article><span><RadioTower size={16} aria-hidden="true" />Active</span><strong>{totals.active}</strong><small>accepting occurrences</small></article>
        <article><span><Pause size={16} aria-hidden="true" />Paused</span><strong>{totals.paused}</strong><small>operator or definition hold</small></article>
        <article><span><Activity size={16} aria-hidden="true" />Pending</span><strong>{totals.pending}</strong><small>accepted, deferred or retrying</small></article>
        <article className={totals.dead ? 'metric-alert' : ''}><span><RotateCcw size={16} aria-hidden="true" />Dead letters</span><strong>{totals.dead}</strong><small>eligible for manual replay</small></article>
      </section>

      {triggers.isPending || occurrences.isPending ? <LoadingState label="Loading trigger runtime" /> : null}
      {error ? <ErrorState message={error.message} retry={() => void refresh()} /> : null}

      {!triggers.isPending && !triggers.error ? (
        <section className="data-section" aria-labelledby="trigger-health-heading">
          <div className="section-heading"><div><p className="eyebrow">SOURCE HEALTH</p><h2 id="trigger-health-heading">Active trigger revisions</h2></div><span className="live-indicator"><i className="online" />10s refresh</span></div>
          {!runtimeRows.length ? <EmptyState title="No active triggers" body="Apply a flow with a webhook, schedule, flow-completion or plugin trigger to populate this monitor." /> : null}
          {runtimeRows.length ? (
            <div className="table-shell trigger-table"><table><thead><tr><th>Trigger</th><th>Type / revision</th><th>Health</th><th>Queue</th><th>Latest decision</th><th>Control</th></tr></thead><tbody>
              {runtimeRows.map((trigger) => (
                <tr key={trigger.trigger_definition_id}>
                  <td><strong>{trigger.trigger_id}</strong><small className="cell-subtitle">{trigger.namespace}.{trigger.flow_id}</small></td>
                  <td><code>{trigger.trigger_type}</code><small className="cell-subtitle">revision {trigger.flow_revision}</small></td>
                  <td><StatusBadge state={trigger.paused ? 'PAUSED' : trigger.last_error ? 'FAILED' : 'RUNNING'} /><small className="cell-subtitle">{trigger.consecutive_failures} consecutive failures</small></td>
                  <td><strong>{trigger.pending_count}</strong><small className="cell-subtitle">{trigger.dead_letter_count} dead</small></td>
                  <td className="trigger-decision"><span>{trigger.last_decision}</span>{trigger.last_error ? <small>{trigger.last_error}</small> : null}</td>
                  <td>{canManage ? <button className="button button-compact button-secondary" type="button" disabled={pendingAction} onClick={() => pauseMutation.mutate({ trigger, paused: !trigger.paused })}>{trigger.paused ? <Play size={15} aria-hidden="true" /> : <Pause size={15} aria-hidden="true" />}{trigger.paused ? 'Resume' : 'Pause'}</button> : <span className="hash">view only</span>}</td>
                </tr>
              ))}
            </tbody></table></div>
          ) : null}
        </section>
      ) : null}

      {!occurrences.isPending && !occurrences.error ? (
        <section className="data-section" aria-labelledby="occurrence-ledger-heading">
          <div className="section-heading"><div><p className="eyebrow">DURABLE LEDGER</p><h2 id="occurrence-ledger-heading">Recent occurrences</h2></div></div>
          <div className="toolbar trigger-toolbar" aria-label="Occurrence filters">
            <label className="search-field"><Search size={17} aria-hidden="true" /><span className="sr-only">Search occurrences</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search flow, trigger or occurrence key" /></label>
            <label className="filter-select"><span>State</span><select value={state} onChange={(event) => setState(event.target.value as TriggerOccurrenceState | '')}><option value="">All states</option>{occurrenceStates.map((item) => <option key={item} value={item}>{item.replace('_', ' ')}</option>)}</select></label>
            <span className="result-count">{occurrenceRows.length} / {occurrences.data?.length || 0} occurrences</span>
          </div>
          {!occurrenceRows.length ? <EmptyState title="No occurrences match" body="Clear the filters or send an event to an active trigger." /> : null}
          {occurrenceRows.length ? (
            <div className="table-shell trigger-table"><table><thead><tr><th>Occurrence</th><th>Trigger</th><th>State</th><th>Attempt</th><th>Decision evidence</th><th>Created</th><th>Action</th></tr></thead><tbody>
              {occurrenceRows.map((occurrence) => (
                <tr key={occurrence.occurrence_id}>
                  <td><code title={occurrence.occurrence_key}>{compactId(occurrence.occurrence_id)}</code><small className="cell-subtitle occurrence-key">{occurrence.occurrence_key}</small></td>
                  <td><strong>{occurrence.trigger_id}</strong><small className="cell-subtitle">{occurrence.namespace}.{occurrence.flow_id}</small></td>
                  <td><StatusBadge state={occurrence.state} /></td>
                  <td>{occurrence.attempt} / {occurrence.max_attempts}</td>
                  <td className="trigger-decision"><span>{typeof occurrence.evidence?.reason === 'string' ? occurrence.evidence.reason : 'Occurrence state recorded'}</span>{occurrence.replay_of ? <small>Replay of {compactId(occurrence.replay_of)}</small> : null}</td>
                  <td><time dateTime={occurrence.created_at}>{formatDate(occurrence.created_at, settings.locale, settings.timezone)}</time></td>
                  <td className="trigger-actions">{occurrence.execution_id ? <Link className="button button-compact button-secondary" to={`/executions/${occurrence.execution_id}`}>Execution</Link> : null}{canManage && (occurrence.state === 'SUCCEEDED' || occurrence.state === 'DEAD_LETTERED') ? <button className="button button-compact button-secondary" type="button" disabled={pendingAction} onClick={() => replayMutation.mutate(occurrence.occurrence_id)}><RotateCcw size={15} aria-hidden="true" />Replay</button> : null}</td>
                </tr>
              ))}
            </tbody></table></div>
          ) : null}
        </section>
      ) : null}
    </div>
  )
}
