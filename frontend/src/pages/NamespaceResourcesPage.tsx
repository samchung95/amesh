import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Database,
  Download,
  FileClock,
  FolderOpen,
  KeyRound,
  MoveRight,
  PackageOpen,
  RefreshCw,
  ShieldCheck,
  Trash2,
  Upload,
} from 'lucide-react'
import { type FormEvent, useState } from 'react'

import type { KeyValueType, NamespaceFileVersion, UiSession } from '../api/types'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'

const keyValueTypes: KeyValueType[] = [
  'STRING',
  'NUMBER',
  'BOOLEAN',
  'DATETIME',
  'DATE',
  'DURATION',
  'JSON',
]

function parseKeyValue(type: KeyValueType, value: string): unknown {
  if (type === 'STRING' || type === 'DATETIME' || type === 'DATE' || type === 'DURATION') return value
  if (type === 'BOOLEAN') {
    if (value !== 'true' && value !== 'false') throw new Error('BOOLEAN values must be true or false')
    return value === 'true'
  }
  const parsed: unknown = JSON.parse(value)
  if (type === 'NUMBER' && typeof parsed !== 'number') throw new Error('NUMBER values must be numeric')
  return parsed
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export function NamespaceResourcesPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  const namespace = settings.namespace
  const canRead = session.capabilities['namespaceResources.read']
  const canWrite = session.capabilities['namespaceResources.write']
  const canWriteSecrets = session.capabilities['secretBindings.write']
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [remotePath, setRemotePath] = useState('')
  const [moveSource, setMoveSource] = useState('')
  const [moveDestination, setMoveDestination] = useState('')
  const [versions, setVersions] = useState<Record<string, NamespaceFileVersion[]>>({})
  const [kvKey, setKvKey] = useState('')
  const [kvType, setKvType] = useState<KeyValueType>('STRING')
  const [kvValue, setKvValue] = useState('')
  const [kvExpiresAt, setKvExpiresAt] = useState('')
  const [secretKey, setSecretKey] = useState('')
  const [environmentName, setEnvironmentName] = useState('')

  const files = useQuery({
    queryKey: ['namespace-files', settings.tenant, namespace],
    queryFn: () => api.namespaceFiles(namespace),
    enabled: Boolean(namespace && canRead),
  })
  const keyValues = useQuery({
    queryKey: ['namespace-key-values', settings.tenant, namespace],
    queryFn: () => api.namespaceKeyValues(namespace),
    enabled: Boolean(namespace && canRead),
  })
  const secrets = useQuery({
    queryKey: ['namespace-secret-bindings', settings.tenant, namespace],
    queryFn: () => api.namespaceSecretBindings(namespace),
    enabled: Boolean(namespace && canRead),
  })
  const mutation = useMutation({
    mutationFn: async (operation: () => Promise<unknown>) => operation(),
    onSuccess: async () => {
      setFailure('')
      await Promise.all([files.refetch(), keyValues.refetch(), secrets.refetch()])
    },
    onError: (error) => setFailure(error.message),
  })

  const refresh = async () => {
    await Promise.all([files.refetch(), keyValues.refetch(), secrets.refetch()])
  }
  const uploadFile = (event: FormEvent) => {
    event.preventDefault()
    if (!selectedFile || !remotePath.trim()) return
    mutation.mutate(async () => {
      await api.uploadNamespaceFile(namespace, remotePath.trim(), selectedFile)
      setSelectedFile(null)
      setRemotePath('')
      setNotice(`Uploaded ${remotePath.trim()}`)
    })
  }
  const moveFile = (event: FormEvent) => {
    event.preventDefault()
    const source = files.data?.find((item) => item.path === moveSource)
    if (!source || !moveDestination.trim()) return
    mutation.mutate(async () => {
      await api.moveNamespaceFile(namespace, source.path, moveDestination.trim(), source.resourceVersion)
      setMoveSource('')
      setMoveDestination('')
      setNotice(`Moved ${source.path}`)
    })
  }
  const saveKeyValue = (event: FormEvent) => {
    event.preventDefault()
    try {
      const value = parseKeyValue(kvType, kvValue)
      mutation.mutate(async () => {
        await api.putNamespaceKeyValue(
          namespace,
          kvKey.trim(),
          kvType,
          value,
          kvExpiresAt ? new Date(kvExpiresAt).toISOString() : undefined,
        )
        setKvKey('')
        setKvValue('')
        setKvExpiresAt('')
        setNotice('Key-value saved')
      })
    } catch (error) {
      setFailure(error instanceof Error ? error.message : 'Invalid key-value')
    }
  }
  const bindSecret = (event: FormEvent) => {
    event.preventDefault()
    mutation.mutate(async () => {
      await api.putNamespaceSecretBinding(namespace, secretKey.trim(), environmentName.trim())
      setSecretKey('')
      setEnvironmentName('')
      setNotice('Secret reference saved; no secret value was stored')
    })
  }
  const exportBundle = () => {
    mutation.mutate(async () => {
      const bundle = await api.exportNamespaceResources(namespace)
      downloadBlob(new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' }), `${namespace}-resources.json`)
      setNotice('Resource bundle exported')
    })
  }
  const importBundle = async (file: File) => {
    try {
      const bundle = JSON.parse(await file.text()) as Record<string, unknown>
      mutation.mutate(async () => {
        await api.importNamespaceResources(namespace, bundle)
        setNotice('Resource bundle imported')
      })
    } catch {
      setFailure('Resource bundle must be valid JSON')
    }
  }

  if (!namespace) {
    return (
      <div className="page-stack">
        <header className="page-heading"><div><p className="eyebrow">BUILD / SHARED RESOURCES</p><h1>Namespace resources</h1></div></header>
        <EmptyState title="Select a namespace" body="Use the tenant and namespace selector in the top bar to open files, key-values and secret references." />
      </div>
    )
  }
  if (!canRead) {
    return <ErrorState message="You do not have list permission for namespace resources." retry={() => window.location.reload()} />
  }

  const pending = files.isPending || keyValues.isPending || secrets.isPending
  const error = files.error || keyValues.error || secrets.error
  return (
    <div className="page-stack">
      <header className="page-heading resource-heading">
        <div><p className="eyebrow">BUILD / SHARED RESOURCES</p><h1>{namespace}</h1><p>Versioned files, typed automation values, and runtime-only secret references.</p></div>
        <div className="resource-heading-actions">
          <button className="button button-secondary" type="button" onClick={() => void refresh()}><RefreshCw size={17} aria-hidden="true" />Refresh</button>
          <button className="button button-secondary" type="button" onClick={exportBundle}><PackageOpen size={17} aria-hidden="true" />Export</button>
          {canWrite ? <label className="button button-secondary file-button"><Upload size={17} aria-hidden="true" />Import<input type="file" accept="application/json,.json" onChange={(event) => { const file = event.target.files?.[0]; if (file) void importBundle(file) }} /></label> : null}
        </div>
      </header>
      {notice ? <p className="resource-notice" role="status">{notice}</p> : null}
      {failure ? <p className="resource-failure" role="alert">{failure}</p> : null}
      {pending ? <LoadingState label="Loading namespace resources" /> : null}
      {error ? <ErrorState message={error.message} retry={() => void refresh()} /> : null}

      {!pending && !error ? (
        <>
          <section className="data-section" aria-labelledby="files-heading">
            <div className="section-heading"><div><p className="eyebrow">OBJECT STORAGE</p><h2 id="files-heading"><FolderOpen size={17} aria-hidden="true" /> Namespace files</h2></div><span className="result-count">{files.data?.length || 0} files</span></div>
            {canWrite ? (
              <div className="resource-form-row">
                <form onSubmit={uploadFile}>
                  <label><span>Remote path</span><input value={remotePath} onChange={(event) => setRemotePath(event.target.value)} placeholder="config/rules.json" required /></label>
                  <label className="file-picker"><span>Local file</span><input type="file" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} required /></label>
                  <button className="button button-primary" type="submit" disabled={mutation.isPending}><Upload size={16} aria-hidden="true" />Upload</button>
                </form>
                <form onSubmit={moveFile}>
                  <label><span>Move file</span><select value={moveSource} onChange={(event) => setMoveSource(event.target.value)} required><option value="">Select a file</option>{files.data?.filter((item) => !item.inherited).map((item) => <option key={item.path} value={item.path}>{item.path}</option>)}</select></label>
                  <label><span>Destination</span><input value={moveDestination} onChange={(event) => setMoveDestination(event.target.value)} placeholder="archive/rules.json" required /></label>
                  <button className="button button-secondary" type="submit" disabled={mutation.isPending}><MoveRight size={16} aria-hidden="true" />Move</button>
                </form>
              </div>
            ) : null}
            {!files.data?.length ? <EmptyState title="No namespace files" body="Upload a file here or with the AMESH CLI." /> : (
              <div className="table-shell"><table><thead><tr><th>Path</th><th>Origin</th><th>Version</th><th>Size</th><th>Type</th><th>Actions</th></tr></thead><tbody>{files.data.map((item) => (
                <tr key={`${item.originNamespace}:${item.path}`}><td><strong>{item.path}</strong><small className="cell-subtitle hash">{item.checksumSha256.slice(0, 12)}</small>{versions[item.path]?.map((version) => <small className="cell-subtitle" key={version.version}>v{version.version} · {version.sizeBytes} bytes · {version.createdBy}</small>)}</td><td>{item.originNamespace}{item.inherited ? <small className="cell-subtitle">inherited</small> : null}</td><td>v{item.version}</td><td>{item.sizeBytes} B</td><td>{item.contentType || 'binary'}</td><td><div className="resource-actions"><button className="button button-quiet" type="button" onClick={() => void api.downloadNamespaceFile(namespace, item.path).then((blob) => downloadBlob(blob, item.path.split('/').at(-1) || 'download'))}><Download size={15} aria-hidden="true" />Download</button><button className="button button-quiet" type="button" onClick={() => void api.namespaceFileVersions(namespace, item.path).then((items) => setVersions((current) => ({ ...current, [item.path]: items })))}><FileClock size={15} aria-hidden="true" />Versions</button>{canWrite && !item.inherited ? <button className="button button-quiet resource-delete" type="button" onClick={() => mutation.mutate(() => api.deleteNamespaceFile(namespace, item.path, item.resourceVersion))}><Trash2 size={15} aria-hidden="true" />Delete</button> : null}</div></td></tr>
              ))}</tbody></table></div>
            )}
          </section>

          <section className="data-section" aria-labelledby="kv-heading">
            <div className="section-heading"><div><p className="eyebrow">AUTOMATION CONTEXT</p><h2 id="kv-heading"><Database size={17} aria-hidden="true" /> Typed key-values</h2></div><span className="result-count">{keyValues.data?.length || 0} keys</span></div>
            {canWrite ? <form className="resource-form resource-kv-form" onSubmit={saveKeyValue}><label><span>Key</span><input value={kvKey} onChange={(event) => setKvKey(event.target.value)} placeholder="release.channel" required /></label><label><span>Type</span><select value={kvType} onChange={(event) => setKvType(event.target.value as KeyValueType)}>{keyValueTypes.map((item) => <option key={item}>{item}</option>)}</select></label><label className="resource-value"><span>Value</span><input value={kvValue} onChange={(event) => setKvValue(event.target.value)} placeholder={kvType === 'JSON' ? '{"enabled":true}' : 'value'} required /></label><label><span>Expires at</span><input type="datetime-local" value={kvExpiresAt} onChange={(event) => setKvExpiresAt(event.target.value)} /></label><button className="button button-primary" type="submit" disabled={mutation.isPending}>Save key</button></form> : null}
            {!keyValues.data?.length ? <EmptyState title="No key-values" body="Add a typed value for use through kv() in task expressions." /> : <div className="table-shell"><table><thead><tr><th>Key</th><th>Type</th><th>Value</th><th>Version</th><th>Expiry</th><th>Action</th></tr></thead><tbody>{keyValues.data.map((item) => <tr key={item.key}><td><strong>{item.key}</strong></td><td><code>{item.type}</code></td><td><code>{JSON.stringify(item.value)}</code></td><td>{item.resourceVersion}</td><td>{item.expiresAt || 'Never'}</td><td>{canWrite ? <button className="button button-quiet resource-delete" type="button" onClick={() => mutation.mutate(() => api.deleteNamespaceKeyValue(namespace, item.key, item.resourceVersion))}><Trash2 size={15} aria-hidden="true" />Delete</button> : null}</td></tr>)}</tbody></table></div>}
          </section>

          <section className="data-section" aria-labelledby="secrets-heading">
            <div className="section-heading"><div><p className="eyebrow">RUNTIME RESOLUTION</p><h2 id="secrets-heading"><KeyRound size={17} aria-hidden="true" /> Secret bindings</h2></div><span className="live-indicator"><ShieldCheck size={14} aria-hidden="true" />References only</span></div>
            {canWriteSecrets ? <form className="resource-form" onSubmit={bindSecret}><label><span>Secret key</span><input value={secretKey} onChange={(event) => setSecretKey(event.target.value)} placeholder="API_KEY" required /></label><label className="resource-value"><span>Environment variable</span><input value={environmentName} onChange={(event) => setEnvironmentName(event.target.value)} placeholder="PRODUCTION_API_KEY" required /></label><button className="button button-primary" type="submit" disabled={mutation.isPending}>Bind reference</button></form> : null}
            {!secrets.data?.length ? <EmptyState title="No secret bindings" body="Bind a logical key to an environment variable. Secret values never enter revisions, APIs, bundles or audit events." /> : <div className="table-shell"><table><thead><tr><th>Key</th><th>Provider</th><th>Reference</th><th>Origin</th><th>Version</th><th>Action</th></tr></thead><tbody>{secrets.data.map((item) => <tr key={`${item.originNamespace}:${item.key}`}><td><strong>{item.key}</strong></td><td><code>{item.provider}</code></td><td><code>{item.providerReference}</code></td><td>{item.originNamespace}{item.inherited ? <small className="cell-subtitle">inherited</small> : null}</td><td>{item.resourceVersion}</td><td>{canWriteSecrets && !item.inherited ? <button className="button button-quiet resource-delete" type="button" onClick={() => mutation.mutate(() => api.deleteNamespaceSecretBinding(namespace, item.key, item.resourceVersion))}><Trash2 size={15} aria-hidden="true" />Delete</button> : null}</td></tr>)}</tbody></table></div>}
          </section>
        </>
      ) : null}
    </div>
  )
}
