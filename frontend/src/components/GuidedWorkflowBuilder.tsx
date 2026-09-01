import {
  Bot,
  CalendarClock,
  CheckCircle2,
  CircleDot,
  DatabaseZap,
  GitPullRequestArrow,
  Plus,
  SlidersHorizontal,
  Sparkles,
  Webhook,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import type { AgentEnvelopePreview, AgentResourceRevision, ArtifactRef, FlowEditorSchema, FlowTestRunResult, SecretBinding } from '../api/types'
import { openRouterModels } from './agentDefinitionModel'
import { CatalogSelect } from './CatalogSelect'
import {
  INTENT_STARTERS,
  addGuidedStep,
  createIntentSource,
  readGuidedWorkflow,
  taskSupportsModel,
  taskSupportsRunner,
  isGuidedRequestCompatible,
  updateGuidedIdentity,
  updateGuidedInput,
  updateGuidedOutput,
  updateGuidedTask,
  updateGuidedAgentSelection,
  updateGuidedTaskField,
  updateGuidedDocumentArtifact,
  updateGuidedTrigger,
  type WorkflowIntent,
} from './guidedWorkflowModel'

const INTENT_ICONS = {
  scheduled: CalendarClock,
  webhook: Webhook,
  pipeline: DatabaseZap,
  approval: GitPullRequestArrow,
  agent: Bot,
  blank: SlidersHorizontal,
}

interface GuidedWorkflowBuilderProps {
  source: string
  schema: FlowEditorSchema
  principalId: string
  namespaceOptions: string[]
  secretBindings: SecretBinding[]
  agentResources: AgentResourceRevision[]
  artifacts: ArtifactRef[]
  agentPreview: AgentEnvelopePreview | null
  agentPreviewPending: boolean
  agentPreviewError: string | null
  onPreviewAgent: (key: string, revision: number) => void
  canTestNode: boolean
  nodeTestPending: boolean
  nodeTestOutcome: FlowTestRunResult['outcome'] | null
  onTestNode: () => void
  onChange: (source: string) => void
  onOpenVisual: () => void
  onOpenCode: () => void
}

export function GuidedWorkflowBuilder({
  source,
  schema,
  principalId,
  namespaceOptions,
  secretBindings,
  agentResources,
  artifacts,
  agentPreview,
  agentPreviewPending,
  agentPreviewError,
  onPreviewAgent,
  canTestNode,
  nodeTestPending,
  nodeTestOutcome,
  onTestNode,
  onChange,
  onOpenVisual,
  onOpenCode,
}: GuidedWorkflowBuilderProps) {
  const [intent, setIntent] = useState<WorkflowIntent>('blank')
  const [mutationError, setMutationError] = useState<string | null>(null)
  const state = useMemo(() => {
    try {
      return { value: readGuidedWorkflow(source), error: null }
    } catch (error) {
      return { value: null, error: error instanceof Error ? error.message : 'The YAML cannot be shown in the guide.' }
    }
  }, [source])

  const mutate = (operation: () => string) => {
    try {
      onChange(operation())
      setMutationError(null)
    } catch (error) {
      setMutationError(error instanceof Error ? error.message : 'The guided change could not be applied.')
    }
  }

  if (!state.value) return (
    <div className="guided-fallback" role="alert">
      <CircleDot aria-hidden="true" />
      <div><strong>The guide needs valid YAML.</strong><p>{state.error}</p></div>
      <button className="button button-secondary" type="button" onClick={onOpenCode}>Fix in YAML</button>
    </div>
  )

  const workflow = state.value
  const taskOptions = schema.resourceCatalog.resources
    .filter((resource) => resource.kind === 'task')
    .map((resource) => ({ value: resource.type, label: resource.editor.title, description: resource.editor.description }))
  const triggerOptions = schema.resourceCatalog.resources
    .filter((resource) => resource.kind === 'trigger')
    .map((resource) => ({ value: resource.type, label: resource.editor.title, description: resource.editor.description }))
  const taskIds = workflow.tasks.filter((task) => task.id).map((task) => ({ value: task.id, label: task.id }))
  const agentOptions = agentResources.filter(isGuidedRequestCompatible).map((resource) => ({
    value: `${resource.key}@${String(resource.revision)}`,
    label: `${resource.spec.title} · ${resource.key}@${String(resource.revision)}`,
    description: 'description' in resource.spec ? resource.spec.description : `Immutable ${resource.kind.toLowerCase()} revision`,
  }))
  const pdfArtifacts = artifacts.filter((artifact) => artifact.mediaType === 'application/pdf' || artifact.path.toLocaleLowerCase().endsWith('.pdf'))
  const stepReady = workflow.tasks.length > 0 && workflow.tasks.every((task) => Boolean(task.id && task.type))
  const rail = [
    ['1', 'Intent', true],
    ['2', 'Identity', Boolean(workflow.id && workflow.namespace)],
    ['3', 'Start', true],
    ['4', 'Inputs', true],
    ['5', 'Steps', stepReady],
    ['6', 'Output', Boolean(workflow.outputTaskId) || intent === 'blank'],
  ] as const

  return (
    <div className="guided-builder">
      <nav className="guided-rail" aria-label="Workflow creation progress">
        <p className="eyebrow">GUIDED BUILD</p>
        <ol>{rail.map(([number, label, complete]) => <li key={number} className={complete ? 'complete' : ''}><span>{complete ? <CheckCircle2 aria-hidden="true" /> : number}</span>{label}</li>)}</ol>
        <div className="guided-advanced-links">
          <strong>Need full control?</strong>
          <button type="button" onClick={onOpenVisual}>Open visual graph</button>
          <button type="button" onClick={onOpenCode}>Open YAML</button>
        </div>
      </nav>

      <div className="guided-surface">
        <section aria-labelledby="guided-intent-heading">
          <div className="section-heading"><div><p className="eyebrow">1 / CHOOSE AN OUTCOME</p><h2 id="guided-intent-heading">What should this workflow do?</h2></div><Sparkles aria-hidden="true" /></div>
          <div className="intent-grid">{INTENT_STARTERS.map((starter) => {
            const Icon = INTENT_ICONS[starter.id]
            return <button key={starter.id} type="button" aria-pressed={intent === starter.id} onClick={() => { setIntent(starter.id); onChange(createIntentSource(starter.id, workflow.namespace, principalId, agentResources)); setMutationError(null) }}>
              <Icon aria-hidden="true" /><span><strong>{starter.title}</strong><small>{starter.description}</small></span>
            </button>
          })}</div>
          <p className="guided-impact">Choosing a starter replaces this new draft with a documented starting point. Nothing is saved or run until you say so.</p>
        </section>

        <section aria-labelledby="guided-identity-heading">
          <div className="section-heading"><div><p className="eyebrow">2 / NAME IT</p><h2 id="guided-identity-heading">Workflow identity</h2></div></div>
          <div className="guided-form-grid">
            <CatalogSelect label="Namespace" required value={workflow.namespace} options={namespaceOptions.map((value) => ({ value, label: value }))} allowCustom customLabel="Create in another namespace" helpText="Controls ownership, policy, secrets, and visibility." onChange={(value) => mutate(() => updateGuidedIdentity(source, 'namespace', value))} />
            <label>Workflow name<small>Letters, numbers, dots, underscores, or hyphens.</small><input required value={workflow.id} onChange={(event) => mutate(() => updateGuidedIdentity(source, 'id', event.target.value))} /></label>
            <label className="span-two">Purpose<small>Tell operators what success means.</small><input value={workflow.description} onChange={(event) => mutate(() => updateGuidedIdentity(source, 'description', event.target.value))} /></label>
          </div>
        </section>

        <section aria-labelledby="guided-start-heading">
          <div className="section-heading"><div><p className="eyebrow">3 / START CONDITION</p><h2 id="guided-start-heading">How does it begin?</h2></div></div>
          <CatalogSelect label="Trigger" value={workflow.triggerType} options={triggerOptions} emptyLabel="Manual — Run now or API" helpText="Only installed trigger types are shown. Manual runs need no trigger block." onChange={(value) => mutate(() => updateGuidedTrigger(source, value))} />
        </section>

        <section aria-labelledby="guided-input-heading">
          <div className="section-heading"><div><p className="eyebrow">4 / INPUT BOUNDARY</p><h2 id="guided-input-heading">What may a run receive?</h2></div></div>
          <CatalogSelect label="Starter input" value={workflow.inputMode} options={[
            { value: 'none', label: 'No input', description: 'The workflow is self-contained.' },
            { value: 'text', label: 'Optional text', description: 'A message string with a safe default.' },
            { value: 'payload', label: 'Optional JSON payload', description: 'A structured object with an empty default.' },
          ]} onChange={(value) => mutate(() => updateGuidedInput(source, value as 'none' | 'text' | 'payload'))} />
        </section>

        <section aria-labelledby="guided-steps-heading">
          <div className="section-heading"><div><p className="eyebrow">5 / ORDERED WORK</p><h2 id="guided-steps-heading">Configure the steps</h2></div>{workflow.tasks.length < 2 ? <button className="button button-secondary" type="button" onClick={() => mutate(() => addGuidedStep(source, schema))}><Plus aria-hidden="true" />Add second step</button> : null}</div>
          <div className="guided-step-list">{workflow.tasks.map((task, index) => {
            const resource = schema.resourceCatalog.resources.find((item) => item.kind === 'task' && item.type === task.type)
            const simpleField = task.type === 'core.log' ? 'message' : task.type === 'core.return' ? 'value' : ''
            return <article key={`${String(index)}-${task.id}`}>
              <header><span>{String(index + 1).padStart(2, '0')}</span><div><strong>{task.id || `Step ${String(index + 1)}`}</strong><small>{resource?.editor.description || 'Choose an installed task type.'}</small></div></header>
              <div className="guided-form-grid">
                <label>Step ID<input required value={task.id} onChange={(event) => mutate(() => updateGuidedTask(source, schema, index, { id: event.target.value }))} /></label>
                <CatalogSelect label="Task / plugin" required value={task.type} options={taskOptions} emptyLabel="Choose an installed task" onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { type: value }))} />
                {index > 0 ? <CatalogSelect label="Run after" value={task.dependsOn[0] || ''} options={taskIds.filter((option) => option.value !== task.id)} emptyLabel="No upstream dependency" helpText="Select an upstream output producer; the guide prevents free-form references." onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { dependsOn: value }))} /> : null}
                {simpleField ? <label>{simpleField === 'message' ? 'Message' : 'Returned value'}<small>Expressions may reference validated inputs and upstream outputs.</small><input value={simpleField === 'message' ? task.message : typeof task.value === 'string' ? task.value : JSON.stringify(task.value ?? '')} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, simpleField, event.target.value))} /></label> : null}
              </div>
              {task.type === 'agent.session' ? <details className="guided-step-advanced" open>
                <summary>Agent session boundary</summary>
                <div className="guided-form-grid">
                  <CatalogSelect
                    label="Agent definition revision"
                    required
                    value={task.agent ? `${task.agent}@${String(task.agentRevision || 1)}` : ''}
                    options={agentOptions}
                    emptyLabel="Choose an authorized agent revision"
                    helpText="Only tenant-authorized immutable definitions are available."
                    onChange={(value) => {
                      const separator = value.lastIndexOf('@')
                      const key = separator >= 0 ? value.slice(0, separator) : value
                      const revision = separator >= 0 ? Number(value.slice(separator + 1)) : 1
                      const selected = agentResources.find((resource) => resource.key === key && resource.revision === revision && isGuidedRequestCompatible(resource))
                      mutate(() => updateGuidedAgentSelection(source, index, key, revision, selected && 'permissions' in selected.spec ? selected.spec.permissions.secretScopes : []))
                    }}
                  />
                  <label>Invalid output policy<small>Repair consumes additional bounded session turns.</small><select value={task.invalidOutputPolicy} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, 'invalidOutputPolicy', event.target.value))}><option value="FAIL">Fail on invalid output</option><option value="REPAIR">Repair within session limits</option></select></label>
                  <label>Max repair attempts<small>Additional output-validation attempts, 0–20.</small><input type="number" min="0" max="20" value={task.maxRepairAttempts} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, 'maxRepairAttempts', Number(event.target.value)))} /></label>
                  <CatalogSelect label="Data handling" required value={task.dataHandling} options={[{ value: 'DENY_SECRETS', label: 'Deny secrets', description: 'Reject secret egress.' }, { value: 'REDACT_SECRETS', label: 'Redact secrets', description: 'Remove known secrets before model egress.' }, { value: 'ALLOW', label: 'Allow declared egress', description: 'Requires the pinned policy and approval boundary.' }]} onChange={(value) => mutate(() => updateGuidedTaskField(source, index, 'dataHandling', value))} />
                  <div className="guided-form-grid span-two">
                    <div><strong>Context policy</strong><small>Bounds the derived model context; the canonical transcript remains unchanged.</small></div>
                    <label>Max messages<input type="number" min="3" max="10000" value={task.contextPolicy.maxMessages} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['contextPolicy', 'maxMessages'], Number(event.target.value)))} /></label>
                    <label>Max bytes<input type="number" min="256" max="100000000" value={task.contextPolicy.maxBytes} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['contextPolicy', 'maxBytes'], Number(event.target.value)))} /></label>
                    <label>Estimated token ceiling<input type="number" min="64" max="10000000" value={task.contextPolicy.maxEstimatedTokens} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['contextPolicy', 'maxEstimatedTokens'], Number(event.target.value)))} /></label>
                    <label>Model context window<small>Optional. Leave blank to derive the window from the input ceiling and completion reserve.</small><input type="number" min="65" max="10000000" value={task.contextPolicy.contextWindowTokens ?? ''} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['contextPolicy', 'contextWindowTokens'], event.target.value === '' ? undefined : Number(event.target.value)))} /></label>
                    <label>Reserved completion tokens<small>Completion headroom kept outside the model input budget.</small><input type="number" min="1" max="1000000" value={task.contextPolicy.reservedCompletionTokens} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['contextPolicy', 'reservedCompletionTokens'], Number(event.target.value)))} /></label>
                  </div>
                  {agentPreview ? <section className="simulation-summary span-two" aria-label="Resolved agent capability envelope">
                    <strong>Resolved capability envelope · {agentPreview.envelopeDigest.slice(0, 18)}…</strong>
                    <p><CheckCircle2 aria-hidden="true" />Side-effect-free preview. External model, tool, memory and approval calls were suppressed.</p>
                    <div className="guided-envelope-grid"><div><strong>Immutable resources</strong><ul>{agentPreview.envelope.resources.map((item) => <li key={`${item.kind}:${item.key}:${item.revision}`}><code>{item.kind}</code> {item.key}@{String(item.revision)} <small>{item.digest.slice(0, 12)}…</small></li>)}</ul></div><div><strong>Model routes</strong><ul>{agentPreview.envelope.modelRoutes.map((route) => <li key={route.routeId}>{route.routeId} · {route.model}<small>{route.provider.adapter}</small></li>)}</ul></div><div><strong>MCP tools</strong><ul>{agentPreview.envelope.tools.length ? agentPreview.envelope.tools.map((tool, toolIndex) => <li key={`${String(tool.connectionKey)}:${String(tool.toolName)}:${String(toolIndex)}`}>{String(tool.connectionKey)}@{String(tool.connectionRevision)} · {String(tool.toolName)}</li>) : <li>None attached</li>}</ul></div></div>
                    <dl><div><dt>Hard token ceiling</dt><dd>{agentPreview.envelope.hardLimits.maxTotalTokens.toLocaleString()}</dd></div><div><dt>Hard cost ceiling</dt><dd>${agentPreview.envelope.hardLimits.maxCostUsd}</dd></div><div><dt>Duration ceiling</dt><dd>{agentPreview.envelope.hardLimits.maxDurationSeconds}s</dd></div><div><dt>Turn / tool ceiling</dt><dd>{agentPreview.envelope.hardLimits.maxTurns} / {agentPreview.envelope.hardLimits.maxToolCalls}</dd></div><div><dt>Memory</dt><dd>{agentPreview.envelope.memoryPolicy.scope} · {agentPreview.envelope.memoryPolicy.maxBytes.toLocaleString()} bytes</dd></div><div><dt>Permissions</dt><dd>{agentPreview.envelope.permissions.delegatedCapabilities.length} capabilities · {agentPreview.envelope.permissions.secretScopes.length} secret scopes</dd></div></dl>
                    <details><summary>Output schema</summary><pre className="editor-preview">{JSON.stringify(agentPreview.envelope.outputSchema, null, 2)}</pre></details>
                    <small>{agentPreview.envelope.outputNondeterminismDisclosure}</small>
                  </section> : null}
                  <div className="button-row span-two"><button className="button button-secondary" type="button" disabled={!task.agent || !task.agentRevision || agentPreviewPending} onClick={() => onPreviewAgent(task.agent, task.agentRevision || 1)}>{agentPreviewPending ? 'Resolving envelope…' : 'Preview resolved envelope'}</button><button className="button button-secondary" type="button" disabled={!task.agent || !canTestNode || nodeTestPending} onClick={onTestNode}>{nodeTestPending ? 'Testing agent node…' : nodeTestOutcome ? `Agent node test: ${nodeTestOutcome}` : 'Test agent node (isolated)'}</button>{!agentOptions.length ? <p className="permission-note" role="status">No compatible authorized agent revisions are available. Definitions requiring other input fields remain available in YAML and Agents.</p> : null}{!canTestNode && agentOptions.length ? <p className="permission-note">Save the flow and ensure isolated flow-test permissions are available before testing this node.</p> : null}{agentPreviewError ? <p className="field-error" role="alert">{agentPreviewError}</p> : null}</div>
                </div>
              </details> : null}
              {task.type === 'core.document.extract' ? <details className="guided-step-advanced guided-document-step" open>
                <summary>Document extraction boundary</summary>
                <div className="guided-form-grid">
                  <CatalogSelect
                    label="Input PDF artifact"
                    required
                    value={task.artifact?.reference || ''}
                    options={pdfArtifacts.map((artifact) => ({ value: artifact.reference, label: `${artifact.path} · v${artifact.version}`, description: `${artifact.sizeBytes.toLocaleString()} bytes · ${artifact.checksumSha256.slice(0, 12)}…` }))}
                    emptyLabel="Choose a typed PDF artifact"
                    helpText="Only tenant-scoped, content-addressed artifacts are selectable."
                    onChange={(value) => mutate(() => updateGuidedDocumentArtifact(source, index, pdfArtifacts.find((artifact) => artifact.reference === value) || null, task.source))}
                  />
                  <label>Source name<small>Logical filename exposed to the extractor.</small><input value={task.source} onChange={(event) => mutate(() => updateGuidedDocumentArtifact(source, index, task.artifact, event.target.value))} /></label>
                  <label>Maximum bytes<input type="number" min="1" value={task.limits.maxBytes} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['limits', 'maxBytes'], Number(event.target.value)))} /></label>
                  <label>Maximum pages<input type="number" min="1" value={task.limits.maxPages} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['limits', 'maxPages'], Number(event.target.value)))} /></label>
                  <label>Maximum tokens<input type="number" min="1" value={task.limits.maxTokens} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['limits', 'maxTokens'], Number(event.target.value)))} /></label>
                  <label>Chunk tokens<input type="number" min="1" value={task.limits.chunkTokens} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['limits', 'chunkTokens'], Number(event.target.value)))} /></label>
                  <label>Wall time seconds<input type="number" min="1" value={task.limits.wallTimeSeconds} onChange={(event) => mutate(() => updateGuidedTaskField(source, index, ['limits', 'wallTimeSeconds'], Number(event.target.value)))} /></label>
                  {task.artifact ? <section className="artifact-selection-summary" aria-label="Selected document artifact"><strong>Selected artifact</strong><code>{task.artifact.reference}</code><small>{task.artifact.contentAddress} · {task.artifact.provenance.source} · {task.artifact.provenance.createdBy}</small></section> : <p className="permission-note" role="status">Upload a PDF in Namespace resources before selecting an artifact.</p>}
                </div>
              </details> : null}
              {taskSupportsModel(schema, task.type) ? <details className="guided-step-advanced" open><summary>Model boundary</summary><div className="guided-form-grid"><CatalogSelect label="Model" required value={task.model} options={openRouterModels} onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { model: value }))} /><CatalogSelect label="Credential" required value={task.credentialRef} options={secretBindings.map((binding) => ({ value: binding.key, label: binding.key, description: `Inherited from ${binding.originNamespace}` }))} allowCustom customLabel="Reference another approved binding" onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { credentialRef: value }))} /><label className="span-two">Prompt<small>The output must match the schema declared in YAML.</small><textarea value={task.prompt} onChange={(event) => mutate(() => updateGuidedTask(source, schema, index, { prompt: event.target.value }))} /></label></div></details> : null}
              {taskSupportsRunner(schema, task.type) ? <details className="guided-step-advanced"><summary>Runner and environment</summary><CatalogSelect label="Runner" value={task.runner} options={[{ value: 'local', label: 'Local process', description: 'Runs in the configured local worker boundary.' }, { value: 'docker', label: 'Docker', description: 'Runs in an isolated container.' }, { value: 'kubernetes', label: 'Kubernetes Job', description: 'Runs in a fenced cluster Job.' }]} emptyLabel="Use platform default" onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { runner: value }))} /></details> : null}
            </article>
          })}</div>
        </section>

        <section aria-labelledby="guided-output-heading">
          <div className="section-heading"><div><p className="eyebrow">6 / OUTPUT CONTRACT</p><h2 id="guided-output-heading">What result should callers receive?</h2></div></div>
          <CatalogSelect label="Publish output from" value={workflow.outputTaskId} options={taskIds} emptyLabel="No declared flow output" helpText="Select a step instead of typing an output expression." onChange={(value) => mutate(() => updateGuidedOutput(source, value))} />
          {workflow.advancedPaths.length ? <p className="guided-code-only"><CircleDot aria-hidden="true" /><span><strong>Advanced YAML is preserved.</strong> The guide does not edit {workflow.advancedPaths.join(', ')}.</span><button type="button" onClick={onOpenCode}>Inspect</button></p> : null}
        </section>
        {mutationError ? <p className="field-error" role="alert">{mutationError}</p> : null}
      </div>
    </div>
  )
}
