import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Braces,
  CheckCircle2,
  Copy,
  Download,
  FileDiff,
  FileUp,
  GitBranch,
  Save,
  ShieldOff,
  Sparkles,
  WandSparkles,
} from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { stringify } from 'yaml'

import type {
  AdmissionPolicyDecision,
  FlowValidationResult,
  UiSession,
} from '../api/types'
import { useApiClient, useFlows } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import {
  FlowCodeEditor,
  type FlowCodeEditorHandle,
} from '../components/FlowCodeEditor'
import { VisualFlowEditor } from '../components/VisualFlowEditor'
import { blueprintDraftTransferKey } from '../components/blueprintModel'

const EMPTY_VALIDATION: FlowValidationResult = {
  valid: false,
  irVersion: null,
  semantic_hash: null,
  canonical: null,
  issues: [],
}

function starterFlow(namespace: string): string {
  return `id: new_flow
namespace: ${namespace || 'default'}
revision: 1
tasks:
  - id: done
    type: core.return
    value: ok
`
}

// eslint-disable-next-line react-refresh/only-export-components
export function flowDraftKey(
  tenant: string,
  principalId: string,
  namespace: string,
  flowId: string,
): string {
  return `amesh.flow-draft.v1:${tenant}:${principalId}:${namespace}:${flowId}`
}

// eslint-disable-next-line react-refresh/only-export-components
export function cloneFlowDocument(document: Record<string, unknown>): string {
  const clone = structuredClone(document)
  const sourceId = typeof document.id === 'string' ? document.id : 'flow'
  clone.id = `${sourceId}_copy`
  clone.revision = 1
  return stringify(clone, { lineWidth: 100 })
}

function downloadYaml(filename: string, source: string) {
  const url = URL.createObjectURL(new Blob([source], { type: 'application/yaml' }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export function FlowEditorPage({ session }: { session: UiSession }) {
  const { namespace = '', flowId = '' } = useParams()
  const [searchParams] = useSearchParams()
  const cloneNamespace = searchParams.get('cloneNamespace') || ''
  const cloneFlowId = searchParams.get('cloneFlowId') || ''
  const blueprintId = searchParams.get('blueprint') || ''
  const blueprintVersion = searchParams.get('blueprintVersion') || ''
  const draftNamespace = searchParams.get('draftNamespace') || ''
  const draftFlowId = searchParams.get('draftFlowId') || ''
  const existing = Boolean(namespace && flowId)
  const api = useApiClient()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const editor = useRef<FlowCodeEditorHandle>(null)
  const importInput = useRef<HTMLInputElement>(null)
  const initialized = useRef(false)
  const [source, setSource] = useState(() => starterFlow(settings.namespace))
  const [savedSource, setSavedSource] = useState('')
  const [validation, setValidation] = useState(EMPTY_VALIDATION)
  const [policyDecision, setPolicyDecision] = useState<AdmissionPolicyDecision | null>(null)
  const [recovered, setRecovered] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [selectedRevision, setSelectedRevision] = useState<number | null>(null)
  const [diff, setDiff] = useState('')
  const [etag, setEtag] = useState<string | undefined>()
  const [expression, setExpression] = useState('{{ inputs.name ?? "operator" }}')
  const [sampleContext, setSampleContext] = useState('{\n  "inputs": { "name": "Ada" }\n}')
  const [preview, setPreview] = useState<unknown>(null)
  const [expressionError, setExpressionError] = useState<string | null>(null)
  const [view, setView] = useState<'visual' | 'code'>('visual')

  const schema = useQuery({
    queryKey: ['flow-editor-schema', settings.tenant],
    queryFn: api.flowEditorSchema,
  })
  const document = useQuery({
    queryKey: ['flow-document', namespace, flowId, settings.tenant],
    queryFn: () => api.flowDocument(namespace, flowId),
    enabled: existing,
  })
  const cloneDocument = useQuery({
    queryKey: ['flow-document', cloneNamespace, cloneFlowId, settings.tenant],
    queryFn: () => api.flowDocument(cloneNamespace, cloneFlowId),
    enabled: !existing && Boolean(cloneNamespace && cloneFlowId),
  })
  const revisions = useQuery({
    queryKey: ['flow-revisions', namespace, flowId, settings.tenant],
    queryFn: () => api.flowRevisions(namespace, flowId),
    enabled: existing,
  })
  const flows = useFlows(existing)
  const persisted = useMemo(
    () => flows.data?.find((flow) => flow.namespace === namespace && flow.flow_id === flowId),
    [flowId, flows.data, namespace],
  )
  const targetNamespace = existing ? namespace : draftNamespace || cloneNamespace || settings.namespace || 'default'
  const targetFlowId = existing ? flowId : draftFlowId || (cloneFlowId ? `${cloneFlowId}_copy` : 'new_flow')
  const draftKey = flowDraftKey(settings.tenant, session.principalId, targetNamespace, targetFlowId)
  const blueprintKey = blueprintDraftTransferKey(settings.tenant, session.principalId, blueprintId, blueprintVersion)
  const dirty = Boolean(savedSource) && source !== savedSource
  const effectiveRevision = selectedRevision ?? revisions.data?.[0]?.revision ?? null
  const saveEtag = etag || persisted?.etag

  useEffect(() => {
    if (initialized.current) return
    let initial: string | null = null
    if (existing && document.data) initial = stringify(document.data.document, { lineWidth: 100 })
    if (!existing && cloneDocument.data) initial = cloneFlowDocument(cloneDocument.data.document)
    if (!existing && !cloneNamespace && !cloneFlowId) initial = starterFlow(targetNamespace)
    if (initial === null) return
    const blueprintDraft = blueprintId && blueprintVersion ? sessionStorage.getItem(blueprintKey) : null
    const localDraft = localStorage.getItem(draftKey)
    setSavedSource(initial)
    setSource(blueprintDraft || localDraft || initial)
    setRecovered(Boolean(!blueprintDraft && localDraft && localDraft !== initial))
    if (blueprintDraft) {
      sessionStorage.removeItem(blueprintKey)
      setNotice(`Blueprint ${blueprintId} v${blueprintVersion} loaded as an unsaved draft. Nothing has run.`)
    }
    initialized.current = true
  }, [blueprintId, blueprintKey, blueprintVersion, cloneDocument.data, cloneFlowId, cloneNamespace, document.data, draftKey, existing, targetNamespace])

  useEffect(() => {
    if (!initialized.current || !savedSource) return
    if (source === savedSource) localStorage.removeItem(draftKey)
    else localStorage.setItem(draftKey, source)
  }, [draftKey, savedSource, source])

  useEffect(() => {
    if (!dirty) return
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault()
      event.returnValue = ''
    }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [dirty])

  useEffect(() => {
    if (!initialized.current) return
    let active = true
    const timer = window.setTimeout(() => {
      void api.validateFlow(source).then((result) => {
        if (active) setValidation(result)
      }).catch((error: Error) => {
        if (active) setValidation({ ...EMPTY_VALIDATION, issues: [{
          code: 'validation_request_failed',
          message: error.message,
          path: '',
          hint: 'Correct the YAML syntax or retry validation.',
          sourceRange: null,
          severity: 'error',
        }] })
      })
    }, 450)
    return () => {
      active = false
      window.clearTimeout(timer)
    }
  }, [api, source])

  const save = useMutation({
    mutationFn: async () => {
      const decision = await api.validateFlowPolicy(source)
      setPolicyDecision(decision)
      if (!decision.allowed) {
        const reasons = decision.matchedRules.map((rule) => rule.reason).join('; ')
        throw new Error(`Policy ${decision.outcome.toLowerCase()}: ${reasons || 'save is not allowed'}`)
      }
      return api.saveFlow(source, existing ? saveEtag : undefined)
    },
    onSuccess: (flow) => {
      localStorage.removeItem(draftKey)
      setSavedSource(source)
      setRecovered(false)
      setEtag(flow.etag)
      setNotice(`Saved ${flow.namespace}.${flow.flow_id} revision ${String(flow.revision)}.`)
      void queryClient.invalidateQueries({ queryKey: ['flows'] })
      void queryClient.invalidateQueries({ queryKey: ['flow-revisions'] })
      if (!existing) void navigate(`/flows/${encodeURIComponent(flow.namespace)}/${encodeURIComponent(flow.flow_id)}/edit`, { replace: true })
    },
  })
  const format = useMutation({
    mutationFn: () => api.formatFlow(source),
    onSuccess: (result) => {
      setValidation(result.validation)
      if (result.document) setSource(result.document)
    },
  })
  const compare = useMutation({
    mutationFn: () => api.diffFlowDraft(namespace, flowId, effectiveRevision || 1, source),
    onSuccess: (result) => setDiff(result.human || 'No changes from this revision.'),
  })
  const lifecycle = useMutation({
    mutationFn: () => api.setFlowLifecycle(namespace, flowId, document.data?.revision || 1, 'DISABLED', 'disabled in flow editor'),
    onSuccess: () => setNotice('The current revision is disabled.'),
  })
  const restore = useMutation({
    mutationFn: () => api.restoreFlowRevision(namespace, flowId, effectiveRevision || 1, 'restored in flow editor'),
    onSuccess: async () => {
      setNotice(`Revision ${String(effectiveRevision)} restored as active.`)
      const refreshed = await document.refetch()
      if (refreshed.data) {
        const restoredSource = stringify(refreshed.data.document, { lineWidth: 100 })
        setSource(restoredSource)
        setSavedSource(restoredSource)
        localStorage.removeItem(draftKey)
      }
      void revisions.refetch()
    },
  })
  const expressionPreview = useMutation({
    mutationFn: () => {
      const parsed = JSON.parse(sampleContext) as Record<string, unknown>
      return api.previewExpression(expression, parsed)
    },
    onMutate: () => setExpressionError(null),
    onSuccess: (result) => setPreview(result),
    onError: (error) => setExpressionError(error.message),
  })

  const initialPending = schema.isPending || (existing && document.isPending) || (!existing && Boolean(cloneNamespace && cloneFlowId) && cloneDocument.isPending)
  const initialError = schema.error || document.error || cloneDocument.error
  if (initialPending) return <LoadingState label="Opening flow editor" />
  if (initialError) return <ErrorState message={initialError.message} retry={() => { void schema.refetch(); void document.refetch(); void cloneDocument.refetch() }} />

  const confirmLeave = (event: React.MouseEvent<HTMLAnchorElement>) => {
    if (dirty && !window.confirm('Discard unsaved changes? Your local draft will remain available.')) event.preventDefault()
  }

  return (
    <div className="page-stack flow-editor-page">
      <Link className="back-link" to={existing ? `/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}` : blueprintId ? '/blueprints' : '/flows'} onClick={confirmLeave}><ArrowLeft size={16} aria-hidden="true" />{existing ? 'Flow details' : blueprintId ? 'Blueprints' : 'Flows'}</Link>
      <header className="page-heading flow-editor-heading">
        <div><p className="eyebrow">BUILD / VISUAL + YAML</p><h1>{existing ? flowId : cloneFlowId ? `Clone ${cloneFlowId}` : blueprintId ? `Draft ${draftFlowId || blueprintId}` : 'Create flow'}</h1><p>Visual topology and schema forms backed by one server-validated YAML definition.</p></div>
        <div className="flow-editor-actions">
          <button className="button button-secondary" type="button" onClick={() => importInput.current?.click()}><FileUp size={16} aria-hidden="true" />Import</button>
          <input ref={importInput} className="sr-only" type="file" accept=".yaml,.yml,application/yaml,text/yaml" aria-label="Import flow YAML" onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) void file.text().then(setSource)
            event.target.value = ''
          }} />
          <button className="button button-secondary" type="button" onClick={() => downloadYaml(`${flowId || targetFlowId}.yaml`, source)}><Download size={16} aria-hidden="true" />Export</button>
          <button className="button button-secondary" type="button" disabled={format.isPending} onClick={() => format.mutate()}><WandSparkles size={16} aria-hidden="true" />Format</button>
          <button className="button button-primary" type="button" disabled={!validation.valid || save.isPending || !dirty} onClick={() => save.mutate()}><Save size={16} aria-hidden="true" />{save.isPending ? 'Saving…' : 'Save'}</button>
        </div>
      </header>
      {recovered ? <p className="editor-notice" role="status">Recovered your local unsaved draft. Server content remains available by discarding this draft.</p> : null}
      {notice ? <p className="editor-notice" role="status"><CheckCircle2 size={16} aria-hidden="true" />{notice}</p> : null}
      {save.error || format.error ? <p className="resource-failure" role="alert">{(save.error || format.error)?.message}</p> : null}
      <div className="flow-editor-workspace">
        <section className="editor-source-panel" aria-labelledby="source-heading">
          <div className="section-heading"><div><p className="eyebrow">{view === 'visual' ? 'TOPOLOGY' : 'SOURCE'}</p><h2 id="source-heading">Flow definition</h2></div><div className="editor-heading-actions"><div className="editor-view-toggle" role="tablist" aria-label="Flow editing view"><button role="tab" aria-selected={view === 'visual'} type="button" onClick={() => setView('visual')}><GitBranch size={15} aria-hidden="true" />Visual</button><button role="tab" aria-selected={view === 'code'} type="button" onClick={() => setView('code')}><Braces size={15} aria-hidden="true" />YAML</button></div><span className={validation.valid ? 'editor-valid' : 'editor-invalid'}>{validation.valid ? 'Valid' : `${String(validation.issues.length)} issues`}</span></div></div>
          {view === 'visual' ? <VisualFlowEditor source={source} schema={schema.data} onChange={setSource} onOpenCode={() => setView('code')} /> : <FlowCodeEditor ref={editor} value={source} schema={schema.data} issues={validation.issues} onChange={setSource} />}
        </section>
        <aside className="editor-inspector" aria-label="Flow editor inspector">
          <section aria-labelledby="validation-heading">
            <div className="section-heading"><div><p className="eyebrow">DIAGNOSTICS</p><h2 id="validation-heading">Validation</h2></div></div>
            {validation.issues.length ? <ol className="editor-issues">{validation.issues.map((issue, index) => <li key={`${issue.code}-${String(index)}`}><button type="button" onClick={() => { setView('code'); window.requestAnimationFrame(() => editor.current?.focusRange(issue.sourceRange?.start.offset || 0, issue.sourceRange?.end.offset || 0)) }}><strong>{issue.message}</strong><span>{issue.path || 'document'}{issue.sourceRange ? ` · ${String(issue.sourceRange.start.line)}:${String(issue.sourceRange.start.column)}` : ''}</span><small>{issue.hint}</small></button></li>)}</ol> : <p className="editor-empty"><CheckCircle2 size={16} aria-hidden="true" />No validation issues.</p>}
          </section>
          {policyDecision ? <section aria-labelledby="policy-validation-heading"><div className="section-heading"><div><p className="eyebrow">ADMISSION EVIDENCE</p><h2 id="policy-validation-heading">Policy validation</h2></div></div><p className={policyDecision.allowed ? 'editor-empty' : 'field-error'}>{policyDecision.outcome} · {policyDecision.matchedRules.map((rule) => rule.reason).join(' · ') || 'Default allow'}</p><small>{policyDecision.pinnedPolicies.length} policy revisions pinned · {policyDecision.evaluationDurationMs.toFixed(2)} ms</small></section> : null}
          <section aria-labelledby="expression-heading">
            <div className="section-heading"><div><p className="eyebrow">SAFE PREVIEW</p><h2 id="expression-heading">Expression</h2></div><Sparkles size={17} aria-hidden="true" /></div>
            <label className="editor-field">Expression<textarea value={expression} onChange={(event) => setExpression(event.target.value)} /></label>
            <label className="editor-field">Sample context<textarea value={sampleContext} onChange={(event) => setSampleContext(event.target.value)} /></label>
            <button className="button button-secondary" type="button" disabled={expressionPreview.isPending} onClick={() => expressionPreview.mutate()}><Braces size={16} aria-hidden="true" />Preview</button>
            {expressionError ? <p className="field-error" role="alert">{expressionError}</p> : null}
            {preview !== null ? <pre className="editor-preview" aria-live="polite">{JSON.stringify(preview, null, 2)}</pre> : null}
          </section>
          {existing ? <section aria-labelledby="revision-heading">
            <div className="section-heading"><div><p className="eyebrow">HISTORY</p><h2 id="revision-heading">Revisions</h2></div></div>
            <label className="editor-field">Compare or restore<select value={effectiveRevision || ''} onChange={(event) => setSelectedRevision(Number(event.target.value))}>{revisions.data?.map((revision) => <option key={revision.revision} value={revision.revision}>Revision {revision.revision} · {new Date(revision.created_at).toLocaleString()}</option>)}</select></label>
            <div className="revision-actions">
              <button className="button button-secondary" type="button" onClick={() => compare.mutate()}><FileDiff size={16} aria-hidden="true" />Diff draft</button>
              <button className="button button-secondary" type="button" onClick={() => { if (window.confirm(`Restore revision ${String(effectiveRevision)}?`)) restore.mutate() }}><Copy size={16} aria-hidden="true" />Restore</button>
              <Link className="button button-secondary" to={`/flows/new?cloneNamespace=${encodeURIComponent(namespace)}&cloneFlowId=${encodeURIComponent(flowId)}`} onClick={confirmLeave}><Copy size={16} aria-hidden="true" />Clone</Link>
              <button className="button button-danger" type="button" onClick={() => { if (window.confirm('Disable the current revision?')) lifecycle.mutate() }}><ShieldOff size={16} aria-hidden="true" />Disable</button>
            </div>
            {diff ? <pre className="editor-diff">{diff}</pre> : null}
          </section> : null}
        </aside>
      </div>
    </div>
  )
}
