import { ArrowLeft, Braces, Play, ShieldCheck, Workflow } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import type { FlowInputSchemaProperty, UiSession } from '../api/types'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { ErrorState, LoadingState } from '../components/AsyncState'
import { FlowGraphView } from '../components/FlowGraphView'

type FormValues = Record<string, unknown>

function initialValues(properties: Record<string, FlowInputSchemaProperty>): FormValues {
  return Object.fromEntries(Object.entries(properties).flatMap(([id, property]) => {
    const value = property['x-amesh-input']?.prefill ?? property.default
    return value === undefined || value === null ? [] : [[id, value]]
  }))
}

function parseStructuredValue(raw: string, kind: string): unknown {
  if (!raw.trim()) return kind === 'array' ? [] : {}
  return JSON.parse(raw) as unknown
}

function scalarText(value: unknown): string {
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return `${value}`
  return ''
}

function fileValue(file: File): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error(`Unable to read ${file.name}`))
    reader.onload = () => {
      if (typeof reader.result !== 'string') {
        reject(new Error(`Unable to encode ${file.name}`))
        return
      }
      const result = reader.result
      resolve({
        name: file.name,
        contentType: file.type || 'application/octet-stream',
        contentBase64: result.slice(result.indexOf(',') + 1),
      })
    }
    reader.readAsDataURL(file)
  })
}

export function FlowDetailPage({ session }: { session: UiSession }) {
  const { namespace = '', flowId = '' } = useParams()
  const api = useApiClient()
  const navigate = useNavigate()
  const { settings } = useAppSettings()
  const [values, setValues] = useState<FormValues>({})
  const [formError, setFormError] = useState<string | null>(null)
  const graph = useQuery({
    queryKey: ['flow-graph', namespace, flowId, settings.tenant],
    queryFn: () => api.flowGraph(namespace, flowId),
    enabled: Boolean(namespace && flowId),
  })
  const contract = useQuery({
    queryKey: ['flow-data-contract', namespace, flowId, settings.tenant],
    queryFn: () => api.flowDataContract(namespace, flowId),
    enabled: Boolean(namespace && flowId),
  })
  const execute = useMutation({
    mutationFn: (inputs: FormValues) => api.executeFlow(namespace, flowId, inputs),
    onSuccess: (detail) => void navigate(`/executions/${detail.execution.execution_id}`),
    onError: (error) => setFormError(error.message),
  })

  if (graph.isPending || contract.isPending) return <LoadingState label="Loading workflow contract" />
  if (graph.error) return <ErrorState message={graph.error.message} retry={() => void graph.refetch()} />
  if (contract.error) return <ErrorState message={contract.error.message} retry={() => void contract.refetch()} />

  const properties = contract.data.inputSchema.properties
  const required = new Set(contract.data.inputSchema.required)
  const setValue = (id: string, value: unknown) => setValues((current) => ({ ...current, [id]: value }))

  return (
    <div className="page-stack">
      <Link className="back-link" to="/flows"><ArrowLeft size={16} aria-hidden="true" />Flows</Link>
      <header className="page-heading detail-heading">
        <div><p className="eyebrow">FLOW / REVISION {graph.data.revision}</p><h1>{graph.data.flowId}</h1><p>{graph.data.namespace}</p></div>
        <span className="live-indicator"><Workflow size={15} aria-hidden="true" />Definition</span>
      </header>
      {session.capabilities['executions.execute'] ? (
        <section className="data-section flow-run-panel" aria-labelledby="run-flow-heading">
          <div className="section-heading">
            <div><p className="eyebrow">TYPED CONTRACT</p><h2 id="run-flow-heading">Run this flow</h2></div>
            <span><ShieldCheck size={15} aria-hidden="true" />Validated before launch</span>
          </div>
          <form onSubmit={(event) => {
            event.preventDefault()
            setFormError(null)
            execute.mutate({ ...initialValues(properties), ...values })
          }}>
            <div className="flow-input-grid">
              {Object.entries(properties).map(([id, property]) => {
                const metadata = property['x-amesh-input']
                const kind = metadata?.type || (typeof property.type === 'string' ? property.type : 'string')
                const label = property.title || id
                const common = { id: `flow-input-${id}`, required: required.has(id) }
                return (
                  <label className="flow-input-field" key={id} htmlFor={common.id}>
                    <span>{label}{common.required ? <b aria-label="required"> *</b> : null}</span>
                    <small>{property.description || `${kind} input`}{metadata?.sensitive ? ' · redacted after submission' : ''}</small>
                    {kind === 'boolean' ? (
                      <input {...common} type="checkbox" checked={Boolean(values[id] ?? property.default)} onChange={(event) => setValue(id, event.target.checked)} />
                    ) : kind === 'enum' ? (
                      <select {...common} value={scalarText(values[id] ?? property.default)} onChange={(event) => setValue(id, (property.enum || []).find((option) => scalarText(option) === event.target.value) ?? event.target.value)}><option value="">Select…</option>{(property.enum || []).map((option) => <option key={scalarText(option)} value={scalarText(option)}>{scalarText(option)}</option>)}</select>
                    ) : kind === 'array' || kind === 'object' ? (
                      <textarea {...common} defaultValue={JSON.stringify(values[id] ?? property.default ?? (kind === 'array' ? [] : {}), null, 2)} onChange={(event) => { try { setValue(id, parseStructuredValue(event.target.value, kind)); setFormError(null) } catch { setFormError(`${label} must be valid JSON`) } }} />
                    ) : kind === 'file' ? (
                      <input {...common} type="file" onChange={(event) => { const file = event.target.files?.[0]; if (file) void fileValue(file).then((value) => setValue(id, value)).catch((error: Error) => setFormError(error.message)) }} />
                    ) : (
                      <input {...common} type={kind === 'number' || kind === 'integer' ? 'number' : metadata?.sensitive ? 'password' : 'text'} step={kind === 'integer' ? '1' : kind === 'number' ? 'any' : undefined} placeholder={metadata?.placeholder || (kind === 'secret' ? 'secret://namespace/key' : undefined)} value={scalarText(values[id] ?? property.default)} onChange={(event) => setValue(id, kind === 'number' || kind === 'integer' ? (event.target.value ? event.target.valueAsNumber : undefined) : event.target.value)} />
                    )}
                  </label>
                )
              })}
            </div>
            {!Object.keys(properties).length ? <p className="flow-no-inputs"><Braces size={16} aria-hidden="true" />This flow has no declared inputs.</p> : null}
            {formError ? <p className="field-error" role="alert">{formError}</p> : null}
            <button className="button button-primary" type="submit" disabled={execute.isPending || Boolean(formError)}><Play size={16} aria-hidden="true" />{execute.isPending ? 'Starting…' : 'Run flow'}</button>
          </form>
        </section>
      ) : null}
      <FlowGraphView graph={graph.data} />
    </div>
  )
}
