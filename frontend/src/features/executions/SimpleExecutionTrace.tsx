import { Check, Copy, ExternalLink, GitBranch, ListTree, Timer, UserRoundCheck } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import type {
  DeterminismEnvelope,
  ExecutionEvidenceEvent,
  ExecutionInterventionRecord,
  FlowGraph,
  HumanTask,
  PersistedExecution,
  PersistedSubflow,
  PersistedTaskRun,
} from '../../api/types'
import { compactId, formatDate } from '../../app/format'
import { StatusBadge } from '../../shared/ui'
import { buildExecutionTrace } from './executionTraceModel'

interface Props {
  execution: PersistedExecution
  taskRuns: PersistedTaskRun[]
  evidence: ExecutionEvidenceEvent[]
  graph?: FlowGraph
  subflows: PersistedSubflow[]
  humanTasks: HumanTask[]
  interventions: ExecutionInterventionRecord[]
  selectedStep: string
  locale: string
  timezone: string
  nowMs: number
  onSelectStep: (stepId: string) => void
}

function duration(value: number | null): string {
  if (value === null) return 'Timing unavailable'
  if (value < 1_000) return `${String(Math.round(value))} ms`
  if (value < 60_000) return `${(value / 1_000).toFixed(1)} s`
  return `${Math.floor(value / 60_000)}m ${Math.round(value % 60_000 / 1_000)}s`
}

function pinnedPluginEvidence(execution: PersistedExecution): string {
  const envelope = executionDeterminism(execution)
  if (envelope) return envelope.pluginSetHash
  const evidence = execution.lifecycle_evidence ?? {}
  const digest = evidence.pluginSetHash ?? evidence.plugin_set_hash ?? evidence.pluginManifestHash ?? evidence.plugin_manifest_hash
  return typeof digest === 'string' && digest ? digest : 'No pinned plugin digest recorded'
}

function executionDeterminism(execution: PersistedExecution): DeterminismEnvelope | null {
  const value = execution.trigger?._ameshDeterminism
  if (typeof value !== 'object' || value === null) return null
  const envelope = value as Partial<DeterminismEnvelope>
  return typeof envelope.envelopeDigest === 'string' && Array.isArray(envelope.dynamicBounds)
    ? value as DeterminismEnvelope
    : null
}

export function SimpleExecutionTrace({
  execution,
  taskRuns,
  evidence,
  graph,
  subflows,
  humanTasks,
  interventions,
  selectedStep,
  locale,
  timezone,
  nowMs,
  onSelectStep,
}: Props) {
  const [copied, setCopied] = useState('')
  const determinism = executionDeterminism(execution)
  const model = useMemo(() => buildExecutionTrace({ taskRuns, evidence, graph, subflows, humanTasks, interventions, nowMs }), [evidence, graph, humanTasks, interventions, nowMs, subflows, taskRuns])
  const selected = model.groups.flatMap((group) => group.steps).find((step) => step.id === selectedStep)

  useEffect(() => {
    if (!selectedStep) return
    const element = document.getElementById(`trace-step-${selectedStep}`)
    element?.focus({ preventScroll: true })
    element?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, [selectedStep])

  const copy = async (label: string, value: string) => {
    try {
      await navigator.clipboard.writeText(value)
    } catch {
      const field = document.createElement('textarea')
      field.value = value
      field.style.position = 'fixed'
      field.style.opacity = '0'
      document.body.append(field)
      field.select()
      document.execCommand('copy')
      field.remove()
    }
    setCopied(label)
  }
  const selectedUrl = () => {
    const url = new URL(window.location.href)
    if (selected?.id) url.searchParams.set('step', selected.id)
    url.searchParams.delete('view')
    return url.toString()
  }
  const supportSummary = () => [
    `Execution: ${execution.execution_id}`,
    `Flow: ${execution.namespace}/${execution.flow_id}@${String(execution.flow_revision)}`,
    `State: ${execution.state}`,
    `Epoch/version: ${String(execution.epoch)}/${String(execution.version)}`,
    `Selected step: ${selected ? `${selected.taskId} (${selected.id})` : 'none'}`,
    `Step state: ${selected?.state ?? 'n/a'}`,
    `Outcome: ${selected?.outcome ?? 'n/a'}`,
    `Plugin evidence: ${pinnedPluginEvidence(execution)}`,
    `Determinism envelope: ${determinism?.envelopeDigest ?? 'not recorded'}`,
    `URL: ${selectedUrl()}`,
  ].join('\n')

  return <section className="simple-trace" aria-labelledby="simple-trace-title">
    <header className="simple-trace-heading">
      <div><p className="eyebrow">RUN STORY</p><h2 id="simple-trace-title">Simple execution trace</h2><p>Read from top to bottom. Active, waiting, and failed steps stay visually dominant.</p></div>
      <div className="trace-copy-actions" aria-label="Copy run evidence">
        <button className="button button-secondary" type="button" onClick={() => void copy('id', execution.execution_id)}><Copy size={14} aria-hidden="true" />Copy ID</button>
        <button className="button button-secondary" type="button" onClick={() => void copy('url', selectedUrl())}><ExternalLink size={14} aria-hidden="true" />Copy URL</button>
        <button className="button button-secondary" type="button" onClick={() => void copy('summary', supportSummary())}><ListTree size={14} aria-hidden="true" />Copy support summary</button>
      </div>
    </header>
    {copied ? <p className="trace-copy-status" role="status"><Check size={14} aria-hidden="true" />{copied === 'id' ? 'Execution ID' : copied === 'url' ? 'Trace URL' : 'Support summary'} copied</p> : null}
    <dl className="trace-pins" aria-label="Immutable run context">
      <div><dt>Flow revision</dt><dd>{execution.namespace}/{execution.flow_id}@{execution.flow_revision}</dd></div>
      <div><dt>Plugin set</dt><dd>{pinnedPluginEvidence(execution)}</dd></div>
      <div><dt>Semantic hash</dt><dd>{determinism?.semanticHash ?? 'Not recorded'}</dd></div>
      <div><dt>Envelope</dt><dd>{determinism?.envelopeDigest ?? 'Not recorded'}</dd></div>
      <div><dt>Epoch / version</dt><dd>{execution.epoch} / {execution.version}</dd></div>
      <div><dt>Policy pins</dt><dd>{determinism?.policyPins.length ?? 0}</dd></div>
    </dl>
    {determinism ? <aside className="trace-run-events" aria-label="Deterministic runtime bounds"><strong>Deterministic runtime bounds</strong><span>Worst case {determinism.worstCaseTaskRuns} task runs · nesting {determinism.configuredTaskNestingDepth}/{determinism.maximumTaskNestingDepth}</span>{determinism.dynamicBounds.map((bound) => <span key={bound.taskId}>{bound.taskId} · {bound.kind} · ≤ {bound.worstCaseTaskRuns} runs{bound.maxIterations === null ? '' : ` · ${String(bound.maxIterations)} iterations`}{bound.maxConcurrency === null ? '' : ` · ${String(bound.maxConcurrency)} concurrent`}{bound.iterationKeyPattern ? ` · ${bound.iterationKeyPattern}` : ''}</span>)}{determinism.nondeterministicOperations.length ? <span>External outputs require pinned metadata or recorded fixtures; identical provider output is not claimed.</span> : null}</aside> : null}
    {model.runAnnotations.length ? <aside className="trace-run-events" aria-label="Operator interventions"><strong>Run controls</strong>{model.runAnnotations.map((item) => <span key={item}>{item}</span>)}</aside> : null}
    {model.total === 0 ? <p className="inline-empty">No task runs have been created yet.</p> : <ol className="trace-list">
      {model.groups.map((group) => group.collapsible ? <li key={group.key}><details className="trace-loop" open={group.steps.some((step) => step.id === selectedStep)}>
          <summary><GitBranch size={16} aria-hidden="true" /><span><strong>{group.label}</strong><small>Expand ordered iterations</small></span></summary>
          <ol>{group.steps.map((step) => <TraceStep key={step.id} step={step} selected={step.id === selectedStep} locale={locale} timezone={timezone} onSelect={onSelectStep} />)}</ol>
        </details></li> : <TraceStep key={group.key} step={group.steps[0]} selected={group.steps[0].id === selectedStep} locale={locale} timezone={timezone} onSelect={onSelectStep} />)}
    </ol>}
    {model.hidden ? <p className="aggregate-notice">Showing the first 500 stable, ordered task runs. Use bounded advanced views for the remaining {model.hidden}.</p> : null}
  </section>
}

function TraceStep({ step, selected, locale, timezone, onSelect }: {
  step: ReturnType<typeof buildExecutionTrace>['groups'][number]['steps'][number]
  selected: boolean
  locale: string
  timezone: string
  onSelect: (stepId: string) => void
}) {
  return <li>
    <article id={`trace-step-${step.id}`} tabIndex={-1} className={`trace-step trace-step-${step.state.toLocaleLowerCase()}${selected ? ' selected' : ''}`} aria-label={`${step.label}, ${step.state}`}>
      <button className="trace-step-main" type="button" aria-pressed={selected} onClick={() => onSelect(selected ? '' : step.id)}>
        <span className="trace-marker" aria-hidden="true" />
        <span className="trace-step-name"><strong>{step.label}</strong><small>{compactId(step.id)} · attempt {step.attempt}</small></span>
        <StatusBadge state={step.state} />
        <span className="trace-timing"><Timer size={14} aria-hidden="true" />{duration(step.durationMs)}{step.startedAt ? <small>{formatDate(step.startedAt, locale, timezone)}</small> : null}</span>
        <span className="trace-runner"><UserRoundCheck size={14} aria-hidden="true" />{step.worker}</span>
        <span className="trace-outcome">{step.outcome}</span>
      </button>
      {(step.context.length || step.annotations.length || step.childExecutions.length) ? <div className="trace-context">
        {[...step.context, ...step.annotations].map((item) => <span key={item}>{item}</span>)}
        {step.childExecutions.map((child) => <Link key={child.relationship_id} to={`/executions/${child.child_execution_id}`}><GitBranch size={13} aria-hidden="true" />Subflow {child.child_flow_id} · {child.mode.toLocaleLowerCase()} · {child.child_state.toLocaleLowerCase()}</Link>)}
      </div> : null}
    </article>
  </li>
}
