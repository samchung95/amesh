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

import type { FlowEditorSchema, SecretBinding } from '../api/types'
import { CatalogSelect } from './CatalogSelect'
import {
  INTENT_STARTERS,
  addGuidedStep,
  createIntentSource,
  readGuidedWorkflow,
  taskSupportsModel,
  taskSupportsRunner,
  updateGuidedIdentity,
  updateGuidedInput,
  updateGuidedOutput,
  updateGuidedTask,
  updateGuidedTaskField,
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
            return <button key={starter.id} type="button" aria-pressed={intent === starter.id} onClick={() => { setIntent(starter.id); onChange(createIntentSource(starter.id, workflow.namespace, principalId)); setMutationError(null) }}>
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
              {taskSupportsModel(schema, task.type) ? <details className="guided-step-advanced" open><summary>Model boundary</summary><div className="guided-form-grid"><CatalogSelect label="Model" required value={task.model} options={[{ value: 'openai/gpt-5.6-luna', label: 'OpenAI GPT-5.6 Luna', description: 'Project base model through OpenRouter.' }]} onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { model: value }))} /><CatalogSelect label="Credential" required value={task.credentialRef} options={secretBindings.map((binding) => ({ value: binding.key, label: binding.key, description: `Inherited from ${binding.originNamespace}` }))} allowCustom customLabel="Reference another approved binding" onChange={(value) => mutate(() => updateGuidedTask(source, schema, index, { credentialRef: value }))} /><label className="span-two">Prompt<small>The output must match the schema declared in YAML.</small><textarea value={task.prompt} onChange={(event) => mutate(() => updateGuidedTask(source, schema, index, { prompt: event.target.value }))} /></label></div></details> : null}
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
