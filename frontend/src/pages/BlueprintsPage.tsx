import { useMutation, useQuery } from '@tanstack/react-query'
import {
  BookOpenCheck,
  Braces,
  CheckCircle2,
  CircleDashed,
  FlaskConical,
  LibraryBig,
  Play,
  Search,
  ShieldCheck,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import type {
  BlueprintCatalogSource,
  UiSession,
} from '../api/types'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import {
  blueprintDraftTransferKey,
  onboardingProgressKey,
  onboardingReadiness,
  ONBOARDING_CHECKS,
  readOnboardingProgress,
} from '../components/blueprintModel'

type BlueprintView = 'catalog' | 'playground' | 'setup'

const SOURCES: Array<BlueprintCatalogSource | 'ALL'> = ['ALL', 'BUILTIN', 'ORGANIZATION', 'COMMUNITY']
const DEFAULT_FRAGMENT = `id: done
type: core.return
value:
  message: local preview
`

export function BlueprintsPage({ session }: { session: UiSession }) {
  const [params, setParams] = useSearchParams()
  const view = (params.get('view') as BlueprintView) || 'catalog'
  const selectView = (next: BlueprintView) => setParams(next === 'catalog' ? {} : { view: next })

  return (
    <div className="page-stack blueprint-page">
      <header className="page-heading">
        <div>
          <p className="eyebrow">BUILD / GETTING STARTED</p>
          <h1>Blueprints</h1>
          <p>Start from a reviewed draft, safely try expressions and fragments, or verify your local setup.</p>
        </div>
        <span className="blueprint-local-note"><ShieldCheck size={16} aria-hidden="true" />Local-only. No telemetry.</span>
      </header>
      <div className="admin-tabs blueprint-tabs" role="tablist" aria-label="Blueprint workspace">
        <button className={view === 'catalog' ? 'active' : ''} type="button" role="tab" aria-selected={view === 'catalog'} onClick={() => selectView('catalog')}><LibraryBig size={17} aria-hidden="true" />Catalog</button>
        <button className={view === 'playground' ? 'active' : ''} type="button" role="tab" aria-selected={view === 'playground'} onClick={() => selectView('playground')}><FlaskConical size={17} aria-hidden="true" />Playground</button>
        <button className={view === 'setup' ? 'active' : ''} type="button" role="tab" aria-selected={view === 'setup'} onClick={() => selectView('setup')}><BookOpenCheck size={17} aria-hidden="true" />Setup guide</button>
      </div>
      {view === 'catalog' ? <CatalogView session={session} /> : null}
      {view === 'playground' ? <PlaygroundView /> : null}
      {view === 'setup' ? <SetupView session={session} /> : null}
    </div>
  )
}

function CatalogView({ session }: { session: UiSession }) {
  const api = useApiClient()
  const navigate = useNavigate()
  const { settings } = useAppSettings()
  const [query, setQuery] = useState('')
  const [source, setSource] = useState<BlueprintCatalogSource | 'ALL'>('ALL')
  const [selectedKey, setSelectedKey] = useState('')
  const [values, setValues] = useState<Record<string, string>>({})
  const catalog = useQuery({
    queryKey: ['blueprints', query, source, settings.tenant],
    queryFn: () => api.blueprints(query, source === 'ALL' ? undefined : source),
  })
  const selected = catalog.data?.find(
    (item) => `${item.blueprintId}:${item.version}` === selectedKey,
  ) || catalog.data?.[0] || null
  const preview = useQuery({
    queryKey: ['blueprint', selected?.blueprintId, selected?.version, settings.tenant],
    queryFn: () => api.blueprint(selected?.blueprintId || '', selected?.version || ''),
    enabled: Boolean(selected),
  })
  const parameterValues = Object.fromEntries(
    (preview.data?.parameters || []).map((parameter) => [
      parameter.name,
      values[parameter.name] ?? parameter.default ?? '',
    ]),
  )
  const instantiate = useMutation({
    mutationFn: () => api.instantiateBlueprint(selected?.blueprintId || '', selected?.version || '', parameterValues),
    onSuccess: (draft) => {
      sessionStorage.setItem(
        blueprintDraftTransferKey(settings.tenant, session.principalId, draft.blueprint.blueprintId, draft.blueprint.version),
        draft.document,
      )
      const next = new URLSearchParams({
        blueprint: draft.blueprint.blueprintId,
        blueprintVersion: draft.blueprint.version,
        draftNamespace: parameterValues.namespace || settings.namespace || 'default',
        draftFlowId: parameterValues.flow_id || 'new_flow',
      })
      void navigate(`/flows/new?${next.toString()}`)
    },
  })

  if (catalog.isPending) return <LoadingState label="Loading blueprint catalog" />
  if (catalog.error) return <ErrorState message={catalog.error.message} retry={() => void catalog.refetch()} />

  return (
    <div className="blueprint-catalog-layout">
      <section className="blueprint-library" aria-labelledby="catalog-heading">
        <div className="section-heading"><div><p className="eyebrow">VERSIONED CATALOG</p><h2 id="catalog-heading">Choose a starting point</h2></div><span>{catalog.data.length} found</span></div>
        <div className="blueprint-filters">
          <label><span className="sr-only">Search blueprints</span><Search size={16} aria-hidden="true" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search titles, tags or docs" /></label>
          <select value={source} onChange={(event) => { setSource(event.target.value as typeof source); setSelectedKey(''); setValues({}) }} aria-label="Catalog source">
            {SOURCES.map((value) => <option key={value} value={value}>{value === 'ALL' ? 'All sources' : value.toLowerCase()}</option>)}
          </select>
        </div>
        <ol className="blueprint-list">
          {catalog.data.map((item) => <li key={`${item.blueprintId}:${item.version}`}>
            <button className={selected?.blueprintId === item.blueprintId ? 'selected' : ''} type="button" onClick={() => { setSelectedKey(`${item.blueprintId}:${item.version}`); setValues(Object.fromEntries(item.parameters.map((parameter) => [parameter.name, parameter.default || '']))) }}>
              <span><strong>{item.title}</strong><small>{item.summary}</small></span>
              <span className={`blueprint-source source-${item.source.toLowerCase()}`}>{item.source}</span>
              <code>v{item.version}</code>
            </button>
          </li>)}
        </ol>
        {!catalog.data.length ? <p className="editor-empty">No blueprints match these filters.</p> : null}
      </section>
      <section className="blueprint-preview" aria-labelledby="preview-heading">
        {!selected || preview.isPending ? <LoadingState label="Loading blueprint preview" /> : null}
        {preview.error ? <ErrorState message={preview.error.message} retry={() => void preview.refetch()} /> : null}
        {preview.data ? <>
          <div className="section-heading"><div><p className="eyebrow">{preview.data.source} / {preview.data.license}</p><h2 id="preview-heading">{preview.data.title}</h2></div><LibraryBig size={20} aria-hidden="true" /></div>
          <p>{preview.data.documentation}</p>
          <dl className="blueprint-provenance">
            <div><dt>Publisher</dt><dd>{preview.data.provenance.publisher}</dd></div>
            <div><dt>Revision</dt><dd>{preview.data.provenance.revision}</dd></div>
            <div><dt>Location</dt><dd>{preview.data.provenance.location}</dd></div>
            <div><dt>Digest</dt><dd title={preview.data.provenance.digest}>{preview.data.provenance.digest.slice(0, 22)}…</dd></div>
          </dl>
          <form className="blueprint-parameters" onSubmit={(event) => { event.preventDefault(); instantiate.mutate() }}>
            <h3>Draft parameters</h3>
            {preview.data.parameters.map((parameter) => <label key={parameter.name}>{parameter.title}<small>{parameter.description}</small><input required={parameter.required} value={parameterValues[parameter.name] || ''} onChange={(event) => setValues((current) => ({ ...current, [parameter.name]: event.target.value }))} /></label>)}
            <p className="blueprint-draft-warning"><CircleDashed size={16} aria-hidden="true" />Draft only. Nothing executes until you save it and manually run it.</p>
            <button className="button button-primary" type="submit" disabled={!session.capabilities['flows.create'] || instantiate.isPending}><Play size={16} aria-hidden="true" />{instantiate.isPending ? 'Preparing draft…' : 'Open unsaved draft'}</button>
            {instantiate.error ? <p className="resource-failure" role="alert">{instantiate.error.message}</p> : null}
          </form>
          <details className="blueprint-template"><summary>Template source</summary><pre>{preview.data.template}</pre></details>
        </> : null}
      </section>
    </div>
  )
}

function PlaygroundView() {
  const api = useApiClient()
  const [expression, setExpression] = useState('{{ inputs.name ?? "operator" }}')
  const [context, setContext] = useState('{\n  "inputs": { "name": "Ada", "apiToken": "will-be-redacted" }\n}')
  const [fragment, setFragment] = useState(DEFAULT_FRAGMENT)
  const simulation = useMutation({
    mutationFn: () => api.simulatePlayground(expression, JSON.parse(context) as Record<string, unknown>, fragment),
  })
  return (
    <div className="blueprint-playground-layout">
      <section className="admin-panel playground-form">
        <div className="section-heading"><div><p className="eyebrow">ISOLATED SIMULATOR</p><h2>Try without running</h2></div><FlaskConical size={20} aria-hidden="true" /></div>
        <p>Validates native syntax and previews deterministic core tasks. It cannot use production credentials or runner infrastructure.</p>
        <label>Expression<textarea value={expression} onChange={(event) => setExpression(event.target.value)} /></label>
        <label>Sample context (JSON)<textarea value={context} onChange={(event) => setContext(event.target.value)} /></label>
        <label>Flow or task fragment (YAML)<textarea className="playground-fragment" value={fragment} onChange={(event) => setFragment(event.target.value)} /></label>
        <button className="button button-primary" type="button" disabled={simulation.isPending} onClick={() => simulation.mutate()}><Braces size={16} aria-hidden="true" />{simulation.isPending ? 'Simulating…' : 'Validate and simulate'}</button>
        {simulation.error ? <p className="resource-failure" role="alert">{simulation.error.message}</p> : null}
      </section>
      <section className="admin-panel playground-result" aria-live="polite">
        <div className="section-heading"><div><p className="eyebrow">RESULTS</p><h2>Local evidence</h2></div></div>
        {simulation.data ? <>
          <div className="playground-safety">
            {Object.entries(simulation.data.safety).map(([key, value]) => <article key={key}><CheckCircle2 size={17} aria-hidden="true" /><span>{key.replace(/[A-Z]/g, (letter) => ` ${letter.toLowerCase()}`)}</span><strong>{value ? 'Yes' : 'No'}</strong></article>)}
          </div>
          <dl className="blueprint-provenance"><div><dt>Expression result</dt><dd><code>{JSON.stringify(simulation.data.expressionResult)}</code></dd></div><div><dt>Fragment</dt><dd>{simulation.data.validation?.valid ? 'Valid' : 'Invalid'}</dd></div><div><dt>Compatibility</dt><dd>{simulation.data.compatibilityVersion}</dd></div></dl>
          <h3>Preview steps</h3>
          <ol className="playground-steps">{simulation.data.steps.map((step) => <li key={step.taskId}><span className={step.simulated ? 'ready' : ''}>{step.simulated ? <CheckCircle2 size={16} /> : <CircleDashed size={16} />}</span><div><strong>{step.taskId}</strong><small>{step.taskType} · {step.reason}</small></div></li>)}</ol>
          {simulation.data.validation?.issues.length ? <ul className="editor-issues">{simulation.data.validation.issues.map((issue) => <li key={`${issue.code}:${issue.path}`}><strong>{issue.message}</strong><small>{issue.path}</small></li>)}</ul> : null}
          <details><summary>Redacted context</summary><pre>{JSON.stringify(simulation.data.redactedContext, null, 2)}</pre></details>
        </> : <p className="editor-empty">Run a simulation to see validation and isolation evidence.</p>}
      </section>
    </div>
  )
}

function SetupView({ session }: { session: UiSession }) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  const progressKey = onboardingProgressKey(settings.tenant, session.principalId)
  const [completed, setCompleted] = useState(() => readOnboardingProgress(localStorage, progressKey))
  const readiness = useQuery({ queryKey: ['onboarding', 'readiness'], queryFn: api.readiness })
  const configuration = useQuery({ queryKey: ['onboarding', 'configuration'], queryFn: api.configuration })
  const providers = useQuery({ queryKey: ['onboarding', 'providers'], queryFn: api.providers })
  const topology = useQuery({ queryKey: ['onboarding', 'topology'], queryFn: api.topology })
  const checks = useMemo(
    () => onboardingReadiness(readiness.data, configuration.data, providers.data, topology.data),
    [configuration.data, providers.data, readiness.data, topology.data],
  )
  const toggle = (id: string) => {
    const next = completed.includes(id) ? completed.filter((value) => value !== id) : [...completed, id]
    setCompleted(next)
    localStorage.setItem(progressKey, JSON.stringify(next))
  }
  return (
    <div className="setup-layout">
      <section className="admin-panel">
        <div className="section-heading"><div><p className="eyebrow">LIVE READINESS</p><h2>Local prerequisites</h2></div><span>{checks.filter((check) => check.ready).length} / 4 ready</span></div>
        <div className="setup-readiness">{checks.map((check) => <article key={check.id} className={check.ready ? 'ready' : ''}>{check.ready ? <CheckCircle2 size={19} /> : <CircleDashed size={19} />}<div><strong>{check.title}</strong><small>{check.detail}</small></div></article>)}</div>
        {readiness.error || configuration.error || providers.error || topology.error ? <p className="resource-failure" role="alert">Some readiness facts could not be loaded. Confirm the API permissions for this account.</p> : null}
      </section>
      <section className="admin-panel">
        <div className="section-heading"><div><p className="eyebrow">UNDER 20 MINUTES</p><h2>First successful run</h2></div><span>{completed.length} / {ONBOARDING_CHECKS.length}</span></div>
        <ol className="setup-checklist">{ONBOARDING_CHECKS.map((check, index) => <li key={check.id}><label><input type="checkbox" checked={completed.includes(check.id)} onChange={() => toggle(check.id)} /><span><b>{String(index + 1).padStart(2, '0')}</b><strong>{check.title}</strong><small>{check.detail}</small></span></label></li>)}</ol>
        <p className="blueprint-draft-warning"><ShieldCheck size={16} aria-hidden="true" />Completion is stored only in this browser. No onboarding telemetry is sent.</p>
      </section>
    </div>
  )
}
