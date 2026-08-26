import { CheckCircle2, Cable, FlaskConical, ShieldCheck } from 'lucide-react'
import { useMemo, useState, type FormEvent } from 'react'

import type { AgentMcpConnectionRevision, AgentMcpConnectionSpec, AgentMcpConnectionTestResult, AgentMcpDiscoveryResult, SecretBinding } from '../api/types'
import { CatalogSelect } from './CatalogSelect'

interface ConnectionWizardProps {
  namespace: string
  secrets: SecretBinding[]
  discover: (namespace: string, input: { endpoint: string; credentialRef: string; timeoutSeconds?: number }) => Promise<AgentMcpDiscoveryResult>
  create: (namespace: string, spec: AgentMcpConnectionSpec) => Promise<AgentMcpConnectionRevision>
  test: (namespace: string, key: string, revision: number, timeoutSeconds?: number) => Promise<AgentMcpConnectionTestResult>
  onSaved: (connection: AgentMcpConnectionRevision, test: AgentMcpConnectionTestResult) => void
}

type WizardStatus = 'idle' | 'discovering' | 'discovered' | 'saving' | 'testing' | 'saved' | 'invalid' | 'denied' | 'unavailable' | 'schema-drift'

function statusForError(error: unknown): Exclude<WizardStatus, 'idle' | 'discovering' | 'discovered' | 'saving' | 'testing' | 'saved'> {
  const status = typeof error === 'object' && error !== null && 'status' in error ? Number(error.status) : 0
  if (status === 403 || status === 404) return 'denied'
  if (status === 409) return 'schema-drift'
  if (status === 502 || status === 503) return 'unavailable'
  return 'invalid'
}

export function ConnectionWizard({ namespace, secrets, discover, create, test, onSaved }: ConnectionWizardProps) {
  const [key, setKey] = useState('')
  const [endpoint, setEndpoint] = useState('')
  const [credentialRef, setCredentialRef] = useState('')
  const [timeoutSeconds, setTimeoutSeconds] = useState(30)
  const [discovery, setDiscovery] = useState<AgentMcpDiscoveryResult | null>(null)
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [impacts, setImpacts] = useState<Record<string, AgentMcpConnectionSpec['tools'][number]['impact']>>({})
  const [status, setStatus] = useState<WizardStatus>('idle')
  const [failure, setFailure] = useState('')
  const [saved, setSaved] = useState<AgentMcpConnectionRevision | null>(null)
  const selectedPins = useMemo(() => (discovery?.tools || []).filter((tool) => selectedTools.includes(tool.name)).map((tool) => ({ ...tool, impact: impacts[tool.name] || tool.impact })), [discovery?.tools, impacts, selectedTools])

  const runDiscovery = async () => {
    setFailure('')
    try {
      const parsed = new URL(endpoint)
      if (!['http:', 'https:'].includes(parsed.protocol) || parsed.username || parsed.password || parsed.hash) throw new Error('Endpoint must be an absolute HTTP(S) URL without credentials or a fragment.')
      if (!credentialRef) throw new Error('Choose an authorized secret binding before discovering the server.')
      setStatus('discovering')
      const result = await discover(namespace, { endpoint, credentialRef, timeoutSeconds })
      setDiscovery(result)
      setSelectedTools(result.tools.map((tool) => tool.name))
      setImpacts(Object.fromEntries(result.tools.map((tool) => [tool.name, tool.impact])))
      setStatus('discovered')
    } catch (error) {
      setStatus(statusForError(error))
      setFailure(error instanceof Error ? error.message : 'MCP discovery failed.')
    }
  }

  const saveConnection = async (event: FormEvent) => {
    event.preventDefault()
    setFailure('')
    if (!discovery || !selectedPins.length) {
      setStatus('invalid')
      setFailure('Discover the server and select at least one tool before saving.')
      return
    }
    try {
      setStatus('saving')
      const connection = await create(namespace, { key, namespace, endpoint, credentialRef, toolAllowlist: selectedPins.map((tool) => tool.name), tools: selectedPins })
      setSaved(connection)
      setStatus('testing')
      const testResult = await test(namespace, connection.spec.key, connection.revision, timeoutSeconds)
      setStatus(testResult.status === 'PASSED' ? 'saved' : testResult.status === 'SCHEMA_DRIFT' ? 'schema-drift' : 'unavailable')
      if (testResult.status !== 'PASSED') setFailure(testResult.diagnostic || `Connection test ${testResult.status.toLowerCase()}.`)
      onSaved(connection, testResult)
    } catch (error) {
      setStatus(statusForError(error))
      setFailure(error instanceof Error ? error.message : 'The connection could not be saved.')
    }
  }

  const handleSubmit = (event: FormEvent) => {
    void saveConnection(event)
  }

  return (
    <section className="connection-wizard" aria-labelledby="connection-wizard-heading">
      <div className="section-heading"><div><p className="eyebrow">GOVERNED MCP CONNECTION</p><h2 id="connection-wizard-heading">Connect a server</h2></div><Cable size={21} aria-hidden="true" /></div>
      <p>Discover live schemas with an authorized secret binding, review the allowlist, then save an immutable connection revision. Secret values never enter this form.</p>
      <form className="connection-wizard-form" onSubmit={handleSubmit}>
        <label>Connection key<input aria-label="Connection key" required pattern="[a-zA-Z0-9][a-zA-Z0-9._-]*" value={key} onChange={(event) => setKey(event.target.value)} placeholder="catalog" /></label>
        <label>Endpoint<input aria-label="Endpoint" required type="url" value={endpoint} onChange={(event) => setEndpoint(event.target.value)} placeholder="https://mcp.example.test/mcp" /><small>Absolute HTTP(S) URL; credentials and fragments are rejected.</small></label>
        <CatalogSelect label="Secret binding" value={credentialRef} options={secrets.map((secret) => ({ value: secret.key, label: secret.key, description: `Inherited from ${secret.originNamespace}` }))} onChange={setCredentialRef} emptyLabel="Choose an authorized binding" loading={false} required />
        <label>Discovery timeout (seconds)<input type="number" min="1" max="300" value={timeoutSeconds} onChange={(event) => setTimeoutSeconds(event.target.valueAsNumber)} /></label>
        <div className="button-row"><button className="button button-secondary" type="button" onClick={() => void runDiscovery()} disabled={status === 'discovering' || !endpoint || !credentialRef}><FlaskConical size={16} aria-hidden="true" />{status === 'discovering' ? 'Discovering…' : 'Discover schemas'}</button><span className="permission-note">Namespace · {namespace}</span></div>
        {discovery ? <section className="connection-discovery" aria-label="Discovered MCP tools"><div className="section-heading"><div><p className="eyebrow">{discovery.serverName} {discovery.serverVersion}</p><h3>Review tool access</h3></div><code>{discovery.digest.slice(0, 18)}…</code></div>{discovery.tools.map((tool) => <label className="connection-tool" key={tool.name}><input type="checkbox" checked={selectedTools.includes(tool.name)} onChange={() => setSelectedTools((current) => current.includes(tool.name) ? current.filter((name) => name !== tool.name) : [...current, tool.name])} /><span><strong>{tool.name}</strong><small>{tool.description || 'No description supplied.'} · input/output schemas available</small></span><select aria-label={`Impact for ${tool.name}`} value={impacts[tool.name] || tool.impact} onChange={(event) => setImpacts((current) => ({ ...current, [tool.name]: event.target.value as AgentMcpConnectionSpec['tools'][number]['impact'] }))}><option value="READ_ONLY">Read-only</option><option value="IDEMPOTENT_WRITE">Idempotent write</option><option value="HIGH_IMPACT">High impact</option></select></label>)}{!discovery.tools.length ? <p className="editor-empty">The server returned no attachable tools.</p> : null}</section> : null}
        <button className="button button-primary" type="submit" disabled={!discovery || !selectedPins.length || !key || status === 'saving' || status === 'testing'}><CheckCircle2 size={16} aria-hidden="true" />{status === 'saving' ? 'Saving revision…' : status === 'testing' ? 'Testing saved revision…' : 'Save and test exact revision'}</button>
      </form>
      {saved && status === 'saved' ? <p className="resource-notice" role="status"><ShieldCheck size={16} aria-hidden="true" />Saved and tested {saved.spec.key}@{String(saved.revision)}.</p> : null}
      {failure ? <p className={`resource-failure connection-wizard-${status}`} role="alert">{failure}</p> : null}
    </section>
  )
}
