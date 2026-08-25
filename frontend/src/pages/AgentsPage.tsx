import { useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bot, Braces, CheckCircle2, GitCompareArrows, Plus, Save, ShieldCheck, Sparkles } from 'lucide-react'

import type {
  AgentEnvelopePreview,
  AgentResourceKind,
  AgentResourceRevision,
  AgentRevisionComparison,
  UiSession,
} from '../api/types'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import {
  agentKinds,
  buildAgentResourceSpec,
  initialAgentBuilderDraft,
  openRouterModels,
  revisionRef,
  schemaPresets,
  type AgentBuilderDraft,
} from '../components/agentDefinitionModel'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'

const kindLabels: Record<AgentResourceKind, string> = {
  PROMPT: 'Prompt',
  SKILL: 'Skill',
  MODEL_POLICY: 'Model policy',
  EVALUATION: 'Evaluation',
  AGENT: 'Agent',
}

function resourceDescription(resource: AgentResourceRevision): string {
  if (resource.spec.kind === 'PROMPT') return `${resource.spec.content.slice(0, 90)}${resource.spec.content.length > 90 ? '…' : ''}`
  if (resource.spec.kind === 'SKILL') return resource.spec.description || resource.spec.instructions.slice(0, 90)
  if (resource.spec.kind === 'MODEL_POLICY') return resource.spec.routes.map((route) => route.model).join(' → ')
  if (resource.spec.kind === 'EVALUATION') return `${resource.spec.assertions.length} assertions · ${resource.spec.rubric.length} rubric criteria · ${resource.spec.fixtures.length} fixtures`
  return resource.spec.description || `${resource.spec.prompts.length} prompts · ${resource.spec.skills.length} skills · ${resource.spec.tools.length} tools`
}

export function AgentsPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const namespace = settings.namespace
  const [draft, setDraft] = useState<AgentBuilderDraft>(initialAgentBuilderDraft)
  const [showBuilder, setShowBuilder] = useState(false)
  const [selected, setSelected] = useState<AgentResourceRevision | null>(null)
  const [comparison, setComparison] = useState<AgentRevisionComparison | null>(null)
  const [envelope, setEnvelope] = useState<AgentEnvelopePreview | null>(null)
  const [notice, setNotice] = useState('')

  const resources = useQuery({
    queryKey: ['agent-resources', settings.tenant, namespace],
    queryFn: () => api.agentResources(namespace),
    enabled: Boolean(namespace && session.capabilities['agents.view']),
    staleTime: 5_000,
  })
  const connections = useQuery({
    queryKey: ['agent-mcp-connections', settings.tenant, namespace],
    queryFn: () => api.agentMcpConnections(namespace),
    enabled: Boolean(namespace && session.capabilities['agents.view']),
    staleTime: 10_000,
  })
  const tools = useQuery({
    queryKey: ['agent-mcp-tools', settings.tenant, namespace, connections.data?.map((item) => `${item.spec.key}@${String(item.revision)}`).join(',')],
    queryFn: async () => (await Promise.all((connections.data || []).map((connection) => api.agentMcpTools(namespace, connection.spec.key, connection.revision)))).flat(),
    enabled: Boolean(namespace && connections.data?.length),
    staleTime: 10_000,
  })
  const secrets = useQuery({
    queryKey: ['agent-secret-catalog', settings.tenant, namespace],
    queryFn: () => api.namespaceSecretBindings(namespace),
    enabled: Boolean(namespace && session.capabilities['namespaceResources.read']),
    staleTime: 10_000,
  })

  const catalog = useMemo(() => resources.data || [], [resources.data])
  const grouped = useMemo(() => Object.fromEntries(agentKinds.map(({ value }) => [value, catalog.filter((item) => item.kind === value)])) as Record<AgentResourceKind, AgentResourceRevision[]>, [catalog])

  const save = useMutation({
    mutationFn: () => api.createAgentResource(namespace, buildAgentResourceSpec(namespace, draft, catalog, tools.data || [])),
    onSuccess: async (resource) => {
      setSelected(resource)
      setShowBuilder(false)
      setNotice(`${kindLabels[resource.kind]} ${resource.key} revision ${String(resource.revision)} saved.`)
      setDraft({ ...initialAgentBuilderDraft, kind: draft.kind })
      await queryClient.invalidateQueries({ queryKey: ['agent-resources', settings.tenant, namespace] })
    },
  })
  const resolve = useMutation({
    mutationFn: (resource: AgentResourceRevision) => api.previewAgent(namespace, resource.key, resource.revision),
    onSuccess: (pin) => { setEnvelope(pin); setComparison(null) },
  })
  const compare = useMutation({
    mutationFn: (resource: AgentResourceRevision) => api.compareAgent(namespace, resource.key, resource.revision - 1, resource.revision),
    onSuccess: (result) => { setComparison(result); setEnvelope(null) },
  })

  function update<Key extends keyof AgentBuilderDraft>(key: Key, value: AgentBuilderDraft[Key]) {
    setDraft((current) => ({ ...current, [key]: value }))
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    setNotice('')
    save.mutate()
  }

  if (!namespace) return <EmptyState title="Choose a namespace" body="Agent definitions are namespace-scoped. Set a namespace in the workspace connection first." />

  return (
    <div className="page agents-page">
      <header className="page-heading agent-heading">
        <div><p className="eyebrow">BUILD / AGENT BOUNDARIES</p><h1>Agents</h1><p>Compose exact prompt, skill, model, and tool revisions into a deterministic capability envelope before execution.</p></div>
        {session.capabilities['agents.manage'] ? <button className="button button-primary" type="button" onClick={() => setShowBuilder((value) => !value)}><Plus size={17} />{showBuilder ? 'Close builder' : 'New resource'}</button> : null}
      </header>

      <section className="agent-boundary-strip" aria-label="Agent resolution stages">
        <span><Braces size={17} />Typed input</span><i aria-hidden="true">→</i>
        <span><Sparkles size={17} />Pinned context</span><i aria-hidden="true">→</i>
        <span><ShieldCheck size={17} />Capability limits</span><i aria-hidden="true">→</i>
        <span><CheckCircle2 size={17} />Validated output</span>
      </section>

      {showBuilder ? (
        <form className="agent-builder" onSubmit={submit}>
          <div className="section-heading"><div><p className="eyebrow">GUIDED COMPOSITION</p><h2>Create a revision</h2></div><span>Namespace · {namespace}</span></div>
          <fieldset className="agent-kind-picker"><legend>What are you defining?</legend>{agentKinds.map((kind) => <label key={kind.value} className={draft.kind === kind.value ? 'selected' : ''}><input type="radio" name="agent-kind" value={kind.value} checked={draft.kind === kind.value} onChange={() => update('kind', kind.value)} /><strong>{kind.label}</strong><small>{kind.description}</small></label>)}</fieldset>
          <div className="agent-form-grid">
            <label>Resource key<input required pattern="[a-zA-Z0-9][a-zA-Z0-9._-]*" value={draft.key} onChange={(event) => update('key', event.target.value)} placeholder="researcher" /><small>Use the same key to create the next immutable revision.</small></label>
            <label>Display name<input required value={draft.title} onChange={(event) => update('title', event.target.value)} placeholder="Evidence researcher" /></label>
            {draft.kind !== 'PROMPT' && draft.kind !== 'MODEL_POLICY' ? <label className="span-two">Description<input value={draft.description} onChange={(event) => update('description', event.target.value)} placeholder="What this resource is for" /></label> : null}
            {draft.kind === 'MODEL_POLICY' ? <><label>Provider<select value="openrouter" disabled><option value="openrouter">OpenRouter</option></select></label><label>Model<select value={draft.model} onChange={(event) => update('model', event.target.value)}>{openRouterModels.map((model) => <option key={model.value} value={model.value}>{model.label}</option>)}</select></label><label>Credential reference<select value={draft.credentialRef} onChange={(event) => update('credentialRef', event.target.value)}>{[draft.credentialRef, ...(secrets.data || []).map((item) => item.key)].filter((value, index, values) => values.indexOf(value) === index).map((key) => <option key={key}>{key}</option>)}</select></label><label>Fallback<select value="DISABLED" disabled><option>DISABLED</option></select><small>Provider substitution requires a new revision.</small></label></> : null}
            {draft.kind === 'SKILL' ? <label>Requested capability<select value={draft.requestedCapability} onChange={(event) => update('requestedCapability', event.target.value)}><option value="cite">Cite evidence</option><option value="summarize">Summarize</option><option value="read-data">Read data</option><option value="">No extra capability</option></select></label> : null}
            {draft.kind === 'EVALUATION' ? <><label>Assertion preset<select value={draft.outputPreset} onChange={(event) => update('outputPreset', event.target.value as AgentBuilderDraft['outputPreset'])}>{Object.keys(schemaPresets).map((preset) => <option key={preset} value={preset}>{preset}</option>)}</select></label><label>Optional judge model<select value={draft.modelPolicyRef} onChange={(event) => update('modelPolicyRef', event.target.value)}><option value="">Deterministic checks only</option>{grouped.MODEL_POLICY.map((item) => <option key={item.resourceId} value={revisionRef(item)}>{item.spec.title} · r{item.revision}</option>)}</select></label></> : null}
            {draft.kind === 'AGENT' ? <><label>Model policy revision<select required value={draft.modelPolicyRef} onChange={(event) => update('modelPolicyRef', event.target.value)}><option value="">Choose exact revision…</option>{grouped.MODEL_POLICY.map((item) => <option key={item.resourceId} value={revisionRef(item)}>{item.spec.title} · r{item.revision}</option>)}</select></label><label>Prompt revision<select value={draft.promptRef} onChange={(event) => update('promptRef', event.target.value)}><option value="">No prompt</option>{grouped.PROMPT.map((item) => <option key={item.resourceId} value={revisionRef(item)}>{item.spec.title} · r{item.revision}</option>)}</select></label><label>Skill revision<select value={draft.skillRef} onChange={(event) => update('skillRef', event.target.value)}><option value="">No skill</option>{grouped.SKILL.map((item) => <option key={item.resourceId} value={revisionRef(item)}>{item.spec.title} · r{item.revision}</option>)}</select></label><label>Evaluation revision<select value={draft.evaluationRef} onChange={(event) => update('evaluationRef', event.target.value)}><option value="">Schema gate only</option>{grouped.EVALUATION.map((item) => <option key={item.resourceId} value={revisionRef(item)}>{item.spec.title} · r{item.revision}</option>)}</select></label><label>MCP tool schema<select value={draft.toolRef} onChange={(event) => update('toolRef', event.target.value)}><option value="">No tool</option>{(tools.data || []).map((tool) => { const value = `${tool.connectionKey}@${String(tool.connectionRevision)}:${tool.toolName}`; return <option key={value} value={value}>{tool.toolName} · {tool.connectionKey} r{tool.connectionRevision} · {tool.impact}</option> })}</select></label><label>Input contract<select value={draft.inputPreset} onChange={(event) => update('inputPreset', event.target.value as AgentBuilderDraft['inputPreset'])}>{Object.keys(schemaPresets).map((preset) => <option key={preset} value={preset}>{preset}</option>)}</select></label><label>Output contract<select value={draft.outputPreset} onChange={(event) => update('outputPreset', event.target.value as AgentBuilderDraft['outputPreset'])}>{Object.keys(schemaPresets).map((preset) => <option key={preset} value={preset}>{preset}</option>)}</select></label><label>Memory scope<select value={draft.memoryScope} onChange={(event) => update('memoryScope', event.target.value as AgentBuilderDraft['memoryScope'])}><option>NONE</option><option>EXECUTION</option><option>PRIVATE</option><option>SHARED</option></select></label>{draft.memoryScope === 'SHARED' ? <label>Shared memory namespace<input required value={draft.sharedScope} onChange={(event) => update('sharedScope', event.target.value)} placeholder="research-team" /></label> : null}<label>Human release gate<select value={draft.requireHumanRelease ? 'REQUIRED' : 'NOT_REQUIRED'} onChange={(event) => update('requireHumanRelease', event.target.value === 'REQUIRED')}><option value="NOT_REQUIRED">Not required</option><option value="REQUIRED">Require approval task</option></select></label><label>Maximum turns<select value={draft.maxTurns} onChange={(event) => update('maxTurns', Number(event.target.value))}><option value="1">1</option><option value="3">3</option><option value="5">5</option><option value="10">10</option></select></label><label>Token ceiling<input type="number" min="1" value={draft.maxTotalTokens} onChange={(event) => update('maxTotalTokens', event.target.valueAsNumber)} /></label><label>Cost ceiling (USD)<input type="number" min="0" step="0.01" value={draft.maxCostUsd} onChange={(event) => update('maxCostUsd', event.target.value)} /></label><label>Duration ceiling<select value={draft.maxDurationSeconds} onChange={(event) => update('maxDurationSeconds', Number(event.target.value))}><option value="30">30 seconds</option><option value="120">2 minutes</option><option value="300">5 minutes</option></select></label></> : null}
            {draft.kind !== 'MODEL_POLICY' && draft.kind !== 'EVALUATION' ? <label className="span-two">{draft.kind === 'PROMPT' ? 'Prompt content' : draft.kind === 'SKILL' ? 'Skill instructions' : 'Agent instructions'}<textarea required value={draft.instructions} onChange={(event) => update('instructions', event.target.value)} placeholder="Describe the behavior that belongs inside this boundary." /></label> : null}
          </div>
          {save.error ? <p className="form-error" role="alert">{save.error.message}</p> : null}
          <div className="button-row"><button className="button button-primary" type="submit" disabled={save.isPending}><Save size={16} />{save.isPending ? 'Saving…' : 'Save immutable revision'}</button><span className="permission-note">Schemas, references, budgets, and permissions are validated server-side.</span></div>
        </form>
      ) : null}

      {notice ? <p className="resource-notice" role="status">{notice}</p> : null}
      {resources.isPending ? <LoadingState label="Loading agent catalogs" /> : null}
      {resources.error ? <ErrorState message={resources.error.message} retry={() => void resources.refetch()} /> : null}
      {!resources.isPending && !resources.error && !catalog.length ? <EmptyState title="No agent resources yet" body="Start with a model policy, then add prompts or skills, and finally compose an agent definition." /> : null}

      {catalog.length ? <div className="agent-catalog">{agentKinds.map((kind) => <section key={kind.value}><div className="section-heading"><div><p className="eyebrow">{kind.value}</p><h2>{kind.label}s</h2></div><span>{grouped[kind.value].length}</span></div><div className="agent-card-list">{grouped[kind.value].map((resource) => <button type="button" key={resource.resourceId} className={`agent-resource-card${selected?.resourceId === resource.resourceId ? ' selected' : ''}`} onClick={() => { setSelected(resource); setEnvelope(null); setComparison(null) }}><span className="agent-resource-icon"><Bot size={18} /></span><span><strong>{resource.spec.title}</strong><code>{resource.key} · r{resource.revision}</code><small>{resourceDescription(resource)}</small></span><em title={resource.digest}>{resource.digest.slice(7, 15)}</em></button>)}</div></section>)}</div> : null}

      {selected ? <section className="agent-inspector"><div className="section-heading"><div><p className="eyebrow">EXACT REVISION</p><h2>{selected.spec.title}</h2></div><code>{selected.key}@{selected.revision}</code></div><div className="agent-inspector-actions">{selected.kind === 'AGENT' && session.capabilities['agents.view'] ? <button className="button button-primary" type="button" disabled={resolve.isPending} onClick={() => resolve.mutate(selected)}><ShieldCheck size={16} />{resolve.isPending ? 'Previewing…' : 'Preview effective envelope'}</button> : null}{selected.kind === 'AGENT' && selected.revision > 1 ? <button className="button button-secondary" type="button" disabled={compare.isPending} onClick={() => compare.mutate(selected)}><GitCompareArrows size={16} />Compare with r{selected.revision - 1}</button> : null}</div>{resolve.error || compare.error ? <p className="form-error" role="alert">{(resolve.error || compare.error)?.message}</p> : null}<dl className="agent-revision-facts"><div><dt>Kind</dt><dd>{kindLabels[selected.kind]}</dd></div><div><dt>Digest</dt><dd><code>{selected.digest}</code></dd></div><div><dt>Created by</dt><dd>{selected.createdBy}</dd></div></dl><details><summary>Inspect canonical definition</summary><pre><code>{JSON.stringify(selected.spec, null, 2)}</code></pre></details></section> : null}

      {envelope ? <section className="agent-envelope"><div className="section-heading"><div><p className="eyebrow">SIDE-EFFECT-FREE PREVIEW</p><h2>Effective capability envelope</h2></div><code>{envelope.envelopeDigest.slice(0, 22)}…</code></div><div className="agent-envelope-grid"><article><strong>{envelope.envelope.resources.length + 1}</strong><span>immutable resource pins</span></article><article><strong>{envelope.envelope.tools.length}</strong><span>allowed tools</span></article><article><strong>{envelope.envelope.hardLimits.maxTotalTokens}</strong><span>token ceiling</span></article><article><strong>${envelope.envelope.hardLimits.maxCostUsd}</strong><span>cost ceiling</span></article></div><ol className="agent-instruction-stack">{envelope.envelope.instructions.map((item) => <li key={`${item.sourceKind}:${item.sourceKey}`}><span>{item.order}</span><strong>{item.sourceKind}</strong><code>{item.sourceKey}</code></li>)}</ol><p className="permission-note">No model, tool, memory, or approval side effects ran. Model behavior remains unknown. {envelope.envelope.outputNondeterminismDisclosure}</p></section> : null}
      {comparison ? <section className="agent-envelope"><div className="section-heading"><div><p className="eyebrow">REVISION DIFF</p><h2>r{comparison.fromRevision} → r{comparison.toRevision}</h2></div><span>{comparison.modelPolicyChanged ? 'Model policy changed' : 'Model policy unchanged'}</span></div><div className="agent-diff-grid"><article><strong>Added</strong><p>{[...comparison.addedPrompts, ...comparison.addedSkills, ...comparison.addedTools, ...comparison.addedEvaluations].join(', ') || 'Nothing'}</p></article><article><strong>Removed</strong><p>{[...comparison.removedPrompts, ...comparison.removedSkills, ...comparison.removedTools, ...comparison.removedEvaluations].join(', ') || 'Nothing'}</p></article></div><p className="permission-note">{comparison.nondeterminismDisclosure}</p></section> : null}
    </div>
  )
}
