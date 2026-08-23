import { ArrowLeft, Beaker, CheckCircle2, Pencil, Play, Save, ShieldCheck, Trash2, XCircle } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import type { FlowTestDefinition, FlowTestDefinitionDraft, UiSession } from '../api/types'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'

const DEFAULT_EXPECTED = JSON.stringify({ state: 'SUCCESS', outputs: null, taskStates: {}, taskOutputs: {} }, null, 2)
type GateDraft = { enabled: boolean; minimumCoverage: number; requiredTestIds: string }

function parseObject(label: string, value: string): Record<string, unknown> {
  const parsed = JSON.parse(value) as unknown
  if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') throw new Error(`${label} must be a JSON object`)
  return parsed as Record<string, unknown>
}

export function FlowTestsPage({ session }: { session: UiSession }) {
  const { namespace = '', flowId = '' } = useParams()
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const [editing, setEditing] = useState<FlowTestDefinition | null>(null)
  const [testId, setTestId] = useState('happy-path')
  const [name, setName] = useState('Happy path')
  const [inputs, setInputs] = useState('{}')
  const [variables, setVariables] = useState('{}')
  const [fixtures, setFixtures] = useState('{}')
  const [expected, setExpected] = useState(DEFAULT_EXPECTED)
  const [tags, setTags] = useState('ci')
  const [formError, setFormError] = useState<string | null>(null)
  const [gateDraft, setGateDraft] = useState<GateDraft | null>(null)

  const document = useQuery({
    queryKey: ['flow-document', settings.tenant, namespace, flowId],
    queryFn: () => api.flowDocument(namespace, flowId),
    enabled: Boolean(namespace && flowId),
  })
  const revision = document.data?.revision || 0
  const definitions = useQuery({
    queryKey: ['flow-tests', settings.tenant, namespace, flowId, revision],
    queryFn: () => api.flowTests(namespace, flowId, revision),
    enabled: Boolean(revision && session.capabilities['flowTests.view']),
  })
  const runs = useQuery({
    queryKey: ['flow-test-runs', settings.tenant, namespace, flowId, revision],
    queryFn: () => api.flowTestRuns(namespace, flowId, revision),
    enabled: Boolean(revision && session.capabilities['flowTests.view']),
  })
  const gate = useQuery({
    queryKey: ['flow-test-gate', settings.tenant, namespace],
    queryFn: () => api.flowTestGate(namespace),
    enabled: Boolean(namespace && session.capabilities['flowTests.view']),
  })
  const currentGate: GateDraft = gateDraft || {
    enabled: gate.data?.enabled || false,
    minimumCoverage: gate.data?.minimumCoverage || 0,
    requiredTestIds: gate.data?.requiredTestIds.join(', ') || '',
  }

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['flow-tests', settings.tenant, namespace, flowId] }),
      queryClient.invalidateQueries({ queryKey: ['flow-test-runs', settings.tenant, namespace, flowId] }),
      queryClient.invalidateQueries({ queryKey: ['flow-test-gate', settings.tenant, namespace] }),
    ])
  }
  const save = useMutation({
    mutationFn: (draft: FlowTestDefinitionDraft) => api.saveFlowTest(namespace, flowId, draft),
    onSuccess: () => { setEditing(null); setFormError(null); void invalidate() },
    onError: (error) => setFormError(error.message),
  })
  const remove = useMutation({
    mutationFn: (definition: FlowTestDefinition) => api.deleteFlowTest(namespace, flowId, definition.testId, definition.version),
    onSuccess: () => void invalidate(),
  })
  const run = useMutation({
    mutationFn: (testIds: string[]) => api.runFlowTests(namespace, flowId, revision, testIds),
    onSuccess: () => void invalidate(),
  })
  const saveGate = useMutation({
    mutationFn: () => api.saveFlowTestGate(
      namespace,
      currentGate.enabled,
      currentGate.minimumCoverage,
      currentGate.requiredTestIds.split(',').map((value) => value.trim()).filter(Boolean),
      gate.data?.version,
    ),
    onSuccess: () => { setGateDraft(null); void invalidate() },
  })

  const edit = (definition: FlowTestDefinition) => {
    setEditing(definition)
    setTestId(definition.testId)
    setName(definition.name)
    setInputs(JSON.stringify(definition.inputs, null, 2))
    setVariables(JSON.stringify(definition.variables, null, 2))
    setFixtures(JSON.stringify(definition.fixtures, null, 2))
    setExpected(JSON.stringify(definition.expected, null, 2))
    setTags(definition.tags.join(', '))
    setFormError(null)
  }
  const submit = (event: FormEvent) => {
    event.preventDefault()
    try {
      save.mutate({
        testId,
        name,
        revision,
        inputs: parseObject('Inputs', inputs),
        variables: parseObject('Variables', variables),
        fixtures: parseObject('Fixtures', fixtures),
        expected: parseObject('Expected result', expected),
        tags: tags.split(',').map((value) => value.trim()).filter(Boolean),
        expectedVersion: editing?.version,
      })
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Invalid test definition')
    }
  }
  if (document.isPending) return <LoadingState label="Loading flow-test workspace" />
  if (document.error) return <ErrorState message={document.error.message} retry={() => void document.refetch()} />

  const latest = runs.data?.[0]
  return (
    <div className="page-stack flow-tests-page">
      <Link className="back-link" to={`/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}`}><ArrowLeft size={16} aria-hidden="true" />Flow graph</Link>
      <header className="page-heading detail-heading"><div><p className="eyebrow">FLOW / REVISION {revision} / UNIT TESTS</p><h1>{flowId}</h1><p>Simulate branches, retries, handlers, and generated tasks without production side effects.</p></div>{session.capabilities['flowTests.execute'] ? <button className="button button-primary" type="button" disabled={!definitions.data?.length || run.isPending} onClick={() => run.mutate([])}><Play size={16} />{run.isPending ? 'Running…' : 'Run all tests'}</button> : null}</header>

      {latest ? <section className={`flow-test-summary ${latest.outcome.toLowerCase()}`} aria-live="polite"><div>{latest.outcome === 'PASSED' ? <CheckCircle2 /> : <XCircle />}<span><b>{latest.outcome}</b><small>{latest.cases.length} cases · {latest.coverage.percentage.toFixed(2)}% observed coverage</small></span></div><div className="flow-test-isolation"><ShieldCheck size={16} />Isolated · {latest.productionExecutionsCreated} executions · {latest.artifactsCreated} artifacts · {latest.secretLookups} secret lookups</div></section> : null}

      <div className="flow-test-layout">
        <section className="data-section" aria-labelledby="defined-tests-heading"><div className="section-heading"><div><p className="eyebrow">REVISION-PINNED</p><h2 id="defined-tests-heading">Defined tests</h2></div><span>{definitions.data?.length || 0} cases</span></div>{definitions.isPending ? <LoadingState label="Loading definitions" /> : null}{definitions.error ? <ErrorState message={definitions.error.message} retry={() => void definitions.refetch()} /> : null}<div className="flow-test-list">{definitions.data?.map((definition) => <article key={definition.id}><div><strong>{definition.name}</strong><code>{definition.testId}</code><small>r{definition.revision} · v{definition.version} · {definition.tags.join(', ') || 'untagged'}</small></div><div>{session.capabilities['flowTests.execute'] ? <button className="icon-button" type="button" aria-label={`Run ${definition.name}`} onClick={() => run.mutate([definition.testId])}><Play /></button> : null}{session.capabilities['flowTests.manage'] ? <button className="icon-button" type="button" aria-label={`Edit ${definition.name}`} onClick={() => edit(definition)}><Pencil /></button> : null}{session.capabilities['flowTests.manage'] ? <button className="icon-button danger" type="button" aria-label={`Delete ${definition.name}`} onClick={() => remove.mutate(definition)}><Trash2 /></button> : null}</div></article>)}</div>{!definitions.isPending && !definitions.data?.length ? <p className="flow-no-inputs"><Beaker size={16} />No tests are defined for revision {revision}.</p> : null}</section>

        {session.capabilities['flowTests.manage'] ? <form className="data-section flow-test-editor" onSubmit={submit}><div className="section-heading"><div><p className="eyebrow">{editing ? `EDIT VERSION ${editing.version}` : 'NEW DEFINITION'}</p><h2>{editing ? 'Update test' : 'Define a test'}</h2></div></div><div className="flow-test-fields"><label>Test ID<input required value={testId} disabled={Boolean(editing)} onChange={(event) => setTestId(event.target.value)} /></label><label>Name<input required value={name} onChange={(event) => setName(event.target.value)} /></label><label>Tags<input value={tags} onChange={(event) => setTags(event.target.value)} placeholder="ci, regression" /></label><label>Inputs<textarea value={inputs} onChange={(event) => setInputs(event.target.value)} spellCheck={false} /></label><label>Variables<textarea value={variables} onChange={(event) => setVariables(event.target.value)} spellCheck={false} /></label><label>Fixtures<textarea value={fixtures} onChange={(event) => setFixtures(event.target.value)} spellCheck={false} /></label><label className="span-two">Expected result<textarea value={expected} onChange={(event) => setExpected(event.target.value)} spellCheck={false} /></label></div>{formError ? <p className="field-error" role="alert">{formError}</p> : null}<div className="button-row"><button className="button button-primary" type="submit" disabled={save.isPending}><Save size={16} />{save.isPending ? 'Saving…' : 'Save test'}</button>{editing ? <button className="button button-secondary" type="button" onClick={() => setEditing(null)}>Cancel edit</button> : null}</div></form> : null}
      </div>

      <section className="data-section flow-test-gate"><div className="section-heading"><div><p className="eyebrow">PROMOTION POLICY</p><h2>Namespace quality gate</h2></div><span>{gate.data?.enabled ? 'ENFORCED' : 'OPTIONAL'}</span></div>{gate.isPending ? <LoadingState label="Loading quality gate" /> : null}<form onSubmit={(event) => { event.preventDefault(); saveGate.mutate() }}><label><input type="checkbox" checked={currentGate.enabled} onChange={(event) => setGateDraft({ ...currentGate, enabled: event.target.checked })} />Require passing revision-pinned tests before ACTIVE promotion</label><label>Minimum observed coverage<input type="number" min="0" max="100" step="0.01" value={currentGate.minimumCoverage} onChange={(event) => setGateDraft({ ...currentGate, minimumCoverage: event.target.valueAsNumber })} /></label><label>Required test IDs<input value={currentGate.requiredTestIds} onChange={(event) => setGateDraft({ ...currentGate, requiredTestIds: event.target.value })} placeholder="happy-path, compensation" /></label>{session.capabilities['flowTests.manage'] ? <button className="button button-secondary" type="submit" disabled={saveGate.isPending}><Save size={16} />Save gate</button> : null}</form><small>Coverage reports observed simulator execution only; it is not proof of full workflow semantics.</small></section>

      {latest ? <section className="data-section"><div className="section-heading"><div><p className="eyebrow">LATEST RESULT</p><h2>Assertions</h2></div><code>{latest.simulatorVersion}</code></div><div className="flow-test-assertions">{latest.cases.flatMap((testCase) => testCase.assertions.map((assertion) => <article key={`${testCase.testId}:${assertion.path}`} className={assertion.passed ? 'passed' : 'failed'}><span>{assertion.passed ? <CheckCircle2 /> : <XCircle />}</span><div><strong>{testCase.testId} · {assertion.path}</strong><small>Expected {JSON.stringify(assertion.expected)} · actual {JSON.stringify(assertion.actual)}</small></div></article>))}</div></section> : null}
    </div>
  )
}
