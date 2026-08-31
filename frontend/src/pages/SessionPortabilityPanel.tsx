import { useMemo, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Download, FileJson, ShieldCheck, Upload } from 'lucide-react'

import type { AgentSessionCompatibilityReport, AgentSessionFleetItem, AgentSessionImportResult, AgentSessionProfileCompatibilityReport, AgentSessionProfileImportResult, AgentSessionProfileTransferBundle, AgentSessionTransferBundle, AgentSessionTransferMode } from '../api/types'
import { useApiClient } from '../app/queries'
import { parseTransferBundle, stableCredentialRefs, transferDigest, type TransferBundle, type TransferKind } from '../components/sessionTransferModel'
import { LoadingState } from '../components/AsyncState'

type Plan = AgentSessionProfileCompatibilityReport | AgentSessionCompatibilityReport
type ImportResult = AgentSessionProfileImportResult | AgentSessionImportResult

function downloadJson(bundle: unknown, filename: string) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

function profileAgentKey(agentRef: string | null): string | null {
  if (!agentRef) return null
  const key = agentRef.split('/').at(-1)?.split('@')[0]
  return key || null
}

function asProfileBundle(bundle: TransferBundle): AgentSessionProfileTransferBundle { return bundle as AgentSessionProfileTransferBundle }
function asSessionBundle(bundle: TransferBundle): AgentSessionTransferBundle { return bundle as AgentSessionTransferBundle }

function diagnostics(plan: Plan, bundle: TransferBundle) {
  if ('eligible' in plan) return { source: plan.sourceTenantId, target: plan.targetTenantId, digest: plan.bundleDigest, mode: plan.mode, issues: plan.issues, credentials: plan.credentialRebindingDiagnostics, artifacts: plan.artifactDiagnostics }
  return { source: bundle.sourceTenantId, target: plan.targetTenantId, digest: transferDigest(bundle), mode: 'PROFILE', issues: plan.issues, credentials: ['Not applicable to profile plans'], artifacts: ['Not applicable to profile plans'] }
}

export function SessionPortabilityPanel({ api, selected, namespaceOptions, canView, canManage }: { api: ReturnType<typeof useApiClient>; selected: AgentSessionFleetItem | null; namespaceOptions: string[]; canView: boolean; canManage: boolean }) {
  const [mode, setMode] = useState<AgentSessionTransferMode>('CLEAN_CHECKPOINT')
  const [targetNamespace, setTargetNamespace] = useState('')
  const [imported, setImported] = useState<{ kind: TransferKind; bundle: TransferBundle } | null>(null)
  const [plan, setPlan] = useState<Plan | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [credentialMappings, setCredentialMappings] = useState<Record<string, string>>({})
  const [error, setError] = useState('')
  const [exportError, setExportError] = useState('')
  const refs = useMemo(() => imported ? stableCredentialRefs(imported.bundle) : [], [imported])
  const destinationNamespaces = useMemo(() => Array.from(new Set([...namespaceOptions, ...(imported?.kind === 'profile' ? [asProfileBundle(imported.bundle).namespace] : [])].filter(Boolean))).sort(), [imported, namespaceOptions])

  const profilePlan = useMutation({ mutationFn: (bundle: AgentSessionProfileTransferBundle) => api.planAgentSessionProfileTransfer(bundle, targetNamespace || undefined), onSuccess: (value) => { setPlan(value); setError(''); setResult(null) }, onError: (cause) => setError(cause.message) })
  const sessionPlan = useMutation({ mutationFn: (bundle: AgentSessionTransferBundle) => api.planAgentSessionTransfer(bundle, credentialMappings), onSuccess: (value) => { setPlan(value); setError(''); setResult(null) }, onError: (cause) => setError(cause.message) })
  const profileImport = useMutation({ mutationFn: (bundle: AgentSessionProfileTransferBundle) => api.importAgentSessionProfile(bundle, targetNamespace || undefined), onSuccess: (value) => { setResult(value); setError('') }, onError: (cause) => setError(cause.message) })
  const sessionImport = useMutation({ mutationFn: (bundle: AgentSessionTransferBundle) => api.importAgentSessionTransfer(bundle, credentialMappings), onSuccess: (value) => { setResult(value); setError('') }, onError: (cause) => setError(cause.message) })

  const exportProfile = async () => {
    const agentKey = profileAgentKey(selected?.agentRef || null)
    if (!selected || !agentKey) { setExportError('Select a fleet row with an agent reference before exporting a profile.'); return }
    try { setExportError(''); downloadJson(await api.exportAgentSessionProfile(selected.namespace, agentKey), `${agentKey}-profile.json`) } catch (cause) { setExportError(cause instanceof Error ? cause.message : 'Profile export failed.') }
  }
  const exportSession = async () => {
    if (!selected) { setExportError('Select a fleet row before exporting a session.'); return }
    try { setExportError(''); downloadJson(await api.exportAgentSessionTransfer(selected.sessionId, mode), `${selected.sessionId}-${mode.toLowerCase()}.json`) } catch (cause) { setExportError(cause instanceof Error ? cause.message : 'Session export failed.') }
  }
  const readBundle = async (file: File) => {
    try {
      const parsed = parseTransferBundle(JSON.parse(await file.text()))
      setImported(parsed); setPlan(null); setResult(null); setError(''); setTargetNamespace(parsed.kind === 'profile' ? asProfileBundle(parsed.bundle).namespace : '')
      const nextRefs = stableCredentialRefs(parsed.bundle)
      setCredentialMappings(Object.fromEntries(nextRefs.map((ref) => [ref, ref])))
    } catch (cause) { setImported(null); setPlan(null); setResult(null); setError(cause instanceof Error ? cause.message : 'Transfer bundle could not be read.') }
  }
  const preview = () => {
    if (!canView || !imported) return
    if (imported.kind === 'profile') profilePlan.mutate(asProfileBundle(imported.bundle))
    else sessionPlan.mutate(asSessionBundle(imported.bundle))
  }
  const importBundle = () => {
    if (!canManage || !imported || !plan || !('compatible' in plan ? plan.compatible : plan.eligible)) return
    if (imported.kind === 'profile') profileImport.mutate(asProfileBundle(imported.bundle))
    else sessionImport.mutate(asSessionBundle(imported.bundle))
  }
  const pending = profilePlan.isPending || sessionPlan.isPending || profileImport.isPending || sessionImport.isPending
  const planDetails = plan && imported ? diagnostics(plan, imported.bundle) : null
  return <section className="data-section session-portability" aria-labelledby="session-portability-heading">
    <header className="section-heading"><div><p className="eyebrow">PORTABILITY / VERIFIED BUNDLES</p><h2 id="session-portability-heading">Profile and session transfer</h2><p>Export immutable references or import a JSON bundle only after a target compatibility plan passes.</p></div><span className="result-count">{canView ? 'Read and plan enabled' : 'Read and plan restricted'}</span></header>
    <div className="portability-export-grid"><article><div><FileJson size={18} aria-hidden="true" /><strong>Export agent profile</strong></div><p>Package the selected agent revision, dependencies, and stable credential references without secret values.</p><button className="button button-secondary" type="button" disabled={!canView} onClick={() => void exportProfile()}><Download size={16} aria-hidden="true" />Download profile</button></article><article><div><FileJson size={18} aria-hidden="true" /><strong>Export session</strong></div><p>Choose a portable terminal history or clean checkpoint bundle from the selected canonical session.</p><label>Transfer mode<select value={mode} onChange={(event) => setMode(event.target.value as AgentSessionTransferMode)}><option value="CLEAN_CHECKPOINT">Clean checkpoint</option><option value="TERMINAL_HISTORY">Terminal history</option></select></label><button className="button button-secondary" type="button" disabled={!canView} onClick={() => void exportSession()}><Download size={16} aria-hidden="true" />Download session</button></article></div>
    {exportError ? <p className="form-error" role="alert">{exportError}</p> : null}
    <section className="portability-import" aria-labelledby="portability-import-heading"><div className="section-heading"><div><p className="eyebrow">IMPORT / PLAN FIRST</p><h3 id="portability-import-heading">Verify a bundle before import</h3></div><ShieldCheck size={17} aria-hidden="true" /></div><label className="file-button"><Upload size={16} aria-hidden="true" />Choose JSON bundle<input type="file" accept="application/json,.json" onChange={(event) => { const file = event.target.files?.[0]; if (file) void readBundle(file) }} /></label>{!canManage ? <p className="permission-note">Import requires the session migration manage capability.</p> : null}{!canView ? <p className="permission-note">Compatibility planning requires the session migration view capability.</p> : null}{imported ? <div className="transfer-bundle-facts"><strong>{imported.kind === 'profile' ? `${String(asProfileBundle(imported.bundle).agentKey)}@${String(asProfileBundle(imported.bundle).agentRevision)}` : 'Agent session bundle'}</strong><span>Source tenant: {String(imported.bundle.sourceTenantId)}</span><span>Digest: {transferDigest(imported.bundle)}</span><span>Mode: {imported.kind === 'profile' ? 'PROFILE' : String(asSessionBundle(imported.bundle).mode)}</span></div> : <p className="inline-empty">No bundle selected. JSON file upload keeps the bundle auditable and avoids unbounded paste input.</p>}{imported?.kind === 'profile' ? <label>Target namespace<select value={targetNamespace} onChange={(event) => { setTargetNamespace(event.target.value); setPlan(null); setResult(null) }}>{destinationNamespaces.map((value) => <option key={value} value={value}>{value}</option>)}</select></label> : null}{refs.length ? <div className="credential-map-list"><strong>Stable credential mappings</strong>{refs.map((ref) => <label key={ref}>{ref}<select value={credentialMappings[ref] || ''} onChange={(event) => { setCredentialMappings((current) => ({ ...current, [ref]: event.target.value })); setPlan(null); setResult(null) }}><option value="">Do not acknowledge</option><option value={ref}>{ref}</option></select></label>)}</div> : null}<div className="button-row"><button className="button button-secondary" type="button" disabled={!canView || !imported || pending} onClick={preview}>{pending && !plan ? 'Planning…' : 'Preview compatibility'}</button><button className="button button-primary" type="button" disabled={!canManage || !plan || Boolean(plan && ('compatible' in plan ? !plan.compatible : !plan.eligible)) || pending} onClick={importBundle}>{pending && plan ? 'Importing…' : 'Import verified bundle'}</button></div>{error ? <p className="form-error" role="alert">{error}</p> : null}{pending && plan ? <LoadingState label="Importing verified transfer bundle" /> : null}{planDetails ? <TransferPlanDetails details={planDetails} /> : null}{result ? <TransferResult result={result} /> : null}</section>
  </section>
}

function TransferPlanDetails({ details }: { details: { source: string; target: string; digest: string; mode: string; issues: string[]; credentials: string[]; artifacts: string[] } }) {
  return <div className="transfer-plan-details" aria-label="Compatibility plan diagnostics"><div><strong>Compatibility plan</strong><span className={details.issues.length ? 'status status-warning' : 'status status-success'}>{details.issues.length ? 'Issues found' : 'Compatible'}</span></div><dl><div><dt>Source → target</dt><dd>{details.source} → {details.target}</dd></div><div><dt>Digest / mode</dt><dd>{details.digest} · {details.mode}</dd></div><div><dt>Credential diagnostics</dt><dd>{details.credentials.join(' · ') || 'None'}</dd></div><div><dt>Artifact diagnostics</dt><dd>{details.artifacts.join(' · ') || 'None'}</dd></div><div><dt>Issues</dt><dd>{details.issues.join(' · ') || 'None'}</dd></div></dl></div>
}

function TransferResult({ result }: { result: ImportResult }) {
  if ('agentKey' in result) return <div className="transfer-result" role="status"><strong>{result.alreadyPresent ? 'Profile already present' : 'Profile imported'}</strong><span>{result.agentKey}@{String(result.agentRevision)} → {result.targetNamespace}</span><small>{result.bundleDigest} · {result.resourcesImported} resources imported · {result.mcpConnectionsImported} connections imported</small></div>
  return <div className="transfer-result" role="status"><strong>{result.alreadyPresent ? 'Session already present' : 'Session imported'}</strong><span>{result.sessionId} · {result.mode} → {result.targetTenantId}</span><small>{result.bundleDigest} · {result.credentialRebindingDiagnostics.join(' · ') || 'No credential diagnostics'}</small></div>
}
