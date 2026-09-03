import { useState, type FormEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Clock3, GitBranch, ShieldAlert } from 'lucide-react'

import type { AdmissionPolicyDocument, AdmissionPolicyOperator, AdmissionPolicyOutcome, AdmissionPolicyStage, UiSession } from '../../api/types'
import { formatDate } from '../../app/format'
import { useAdmissionPolicies, useAdmissionPolicyDecisions, useApiClient } from '../../app/queries'
import { useAppSettings } from '../../app/settings'
import { ErrorState, LoadingState, StatusBadge } from '../../shared/ui'

const STAGES: AdmissionPolicyStage[] = ['VALIDATE', 'SAVE', 'PROMOTE', 'LAUNCH', 'DISPATCH']
const OUTCOMES: AdmissionPolicyOutcome[] = ['ALLOW', 'DENY', 'WARN', 'MUTATE_DEFAULT', 'REQUIRE_APPROVAL']
const OPERATORS: AdmissionPolicyOperator[] = ['EQUALS', 'NOT_EQUALS', 'IN', 'CONTAINS', 'EXISTS', 'MATCHES', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL']

interface PolicyDraft {
  policyKey: string
  name: string
  stage: AdmissionPolicyStage
  path: string
  operator: AdmissionPolicyOperator
  value: string
  outcome: AdmissionPolicyOutcome
  reason: string
  mutationPath: string
  mutationValue: string
  criticality: 'ADVISORY' | 'ENFORCING'
}

export function AdmissionPolicyPanel({ session }: { session: UiSession }) {
  const policies = useAdmissionPolicies()
  const decisions = useAdmissionPolicyDecisions()
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const canManage = session.capabilities['administration.manage']
  const [notice, setNotice] = useState('')
  const [draft, setDraft] = useState<PolicyDraft>({
    policyKey: 'security.local',
    name: 'Local security policy',
    stage: 'LAUNCH',
    path: 'runner.requested',
    operator: 'EQUALS',
    value: 'DOCKER',
    outcome: 'WARN',
    reason: 'Docker launches require review',
    mutationPath: 'resource.inputs.region',
    mutationValue: 'local',
    criticality: 'ENFORCING',
  })
  const save = useMutation({
    mutationFn: api.saveAdmissionPolicy,
    onSuccess: async (revision) => {
      setNotice(`${revision.document.policyKey}@${String(revision.revision)} is active.`)
      await queryClient.invalidateQueries({ queryKey: ['admission-policies'] })
    },
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()
    const conditionValue = parseValue(draft.value)
    const document: AdmissionPolicyDocument = {
      schemaVersion: 'amesh.policy/v1',
      policyKey: draft.policyKey,
      name: draft.name,
      description: `Managed from the AMESH governance UI for ${settings.namespace || 'the tenant'}.`,
      scope: settings.namespace ? 'NAMESPACE' : 'TENANT',
      namespace: settings.namespace || null,
      criticality: draft.criticality,
      evaluationTimeoutMs: 100,
      enabled: true,
      rules: [{
        id: 'ui-rule',
        stages: [draft.stage],
        conditions: draft.path ? [{ path: draft.path, operator: draft.operator, value: conditionValue }] : [],
        outcome: draft.outcome,
        reason: draft.reason,
        mutations: draft.outcome === 'MUTATE_DEFAULT'
          ? { [draft.mutationPath]: parseValue(draft.mutationValue) }
          : {},
      }],
    }
    save.mutate(document)
  }

  return (
    <section className="developer-portal plugin-governance" aria-labelledby="admission-policy-heading">
      <div className="section-heading">
        <div><p className="eyebrow">POLICY AS CODE / ADMISSION</p><h2 id="admission-policy-heading">Workflow admission policies</h2></div>
        <ShieldAlert size={22} aria-hidden="true" />
      </div>
      <p>Versioned declarative rules run at validation, save, promotion, launch and task dispatch. Every decision pins the exact policy digest and records matched evidence.</p>

      {policies.isPending ? <LoadingState label="Loading admission policies" /> : null}
      {policies.error ? <ErrorState message={policies.error.message} retry={() => void policies.refetch()} /> : null}
      {policies.data ? (
        <div className="policy-rule-list" aria-label="Active admission policy revisions">
          {policies.data.length ? policies.data.map((revision) => (
            <article key={`${revision.policyId}:${String(revision.revision)}`}>
              <div><StatusBadge state={revision.document.criticality === 'ENFORCING' ? 'PASS' : 'WARN'} /><strong>{revision.document.name}</strong><code>r{revision.revision}</code></div>
              <p>{revision.document.description || `${String(revision.document.rules.length)} declarative rules`}</p>
              <small>{revision.document.scope}{revision.document.namespace ? ` / ${revision.document.namespace}` : ''} · {revision.digest.slice(0, 22)}… · {revision.document.evaluationTimeoutMs} ms bound</small>
            </article>
          )) : <p className="muted-copy">No admission policies are active. Lifecycle evaluations default to allow and still produce decision evidence.</p>}
        </div>
      ) : null}

      {canManage ? (
        <div className="governance-forms">
          <form onSubmit={submit}>
            <h3>Create the next immutable revision</h3>
            <label>Policy key<input required value={draft.policyKey} onChange={(event) => setDraft({ ...draft, policyKey: event.target.value })} pattern="[a-z][a-z0-9_.-]*" /></label>
            <label>Name<input required value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} /></label>
            <label>Stage<select value={draft.stage} onChange={(event) => setDraft({ ...draft, stage: event.target.value as AdmissionPolicyStage })}>{STAGES.map((stage) => <option key={stage}>{stage}</option>)}</select></label>
            <label>Context path<input required value={draft.path} onChange={(event) => setDraft({ ...draft, path: event.target.value })} placeholder="resource.taskType" /></label>
            <label>Operator<select value={draft.operator} onChange={(event) => setDraft({ ...draft, operator: event.target.value as AdmissionPolicyOperator })}>{OPERATORS.map((operator) => <option key={operator}>{operator}</option>)}</select></label>
            <label>Match value<input value={draft.value} onChange={(event) => setDraft({ ...draft, value: event.target.value })} placeholder="JSON or text" /></label>
            <label>Outcome<select value={draft.outcome} onChange={(event) => setDraft({ ...draft, outcome: event.target.value as AdmissionPolicyOutcome })}>{OUTCOMES.map((outcome) => <option key={outcome}>{outcome}</option>)}</select></label>
            {draft.outcome === 'MUTATE_DEFAULT' ? <><label>Default path<input required value={draft.mutationPath} onChange={(event) => setDraft({ ...draft, mutationPath: event.target.value })} /></label><label>Default value<input required value={draft.mutationValue} onChange={(event) => setDraft({ ...draft, mutationValue: event.target.value })} /></label></> : null}
            <label>Criticality<select value={draft.criticality} onChange={(event) => setDraft({ ...draft, criticality: event.target.value as PolicyDraft['criticality'] })}><option>ENFORCING</option><option>ADVISORY</option></select></label>
            <label>Evidence reason<input required value={draft.reason} onChange={(event) => setDraft({ ...draft, reason: event.target.value })} /></label>
            <button className="button button-primary" type="submit" disabled={save.isPending}>Save policy revision</button>
          </form>
        </div>
      ) : <p className="muted-copy">Policy changes require administration permission.</p>}
      {notice ? <p className="resource-notice" role="status">{notice}</p> : null}
      {save.error ? <p className="resource-failure" role="alert">{save.error.message}</p> : null}

      <div className="section-heading">
        <div><p className="eyebrow">RECENT EVIDENCE</p><h3>Enforcement decisions</h3></div>
        <GitBranch size={19} aria-hidden="true" />
      </div>
      {decisions.isPending ? <LoadingState label="Loading policy decisions" /> : null}
      {decisions.error ? <ErrorState message={decisions.error.message} retry={() => void decisions.refetch()} /> : null}
      {decisions.data ? (
        <div className="policy-rule-list" aria-label="Recent admission policy decisions">
          {decisions.data.slice(0, 12).map((decision) => (
            <article key={decision.id}>
              <div><StatusBadge state={decision.outcome === 'DENY' || decision.outcome === 'REQUIRE_APPROVAL' ? 'FAIL' : decision.outcome === 'WARN' ? 'WARN' : 'PASS'} /><strong>{decision.stage}</strong><code>{decision.outcome}</code></div>
              <p>{decision.matchedRules.map((rule) => rule.reason).join(' · ') || 'No rule matched; default allow.'}</p>
              <small><Clock3 size={13} />{decision.decidedAt ? formatDate(decision.decidedAt, settings.locale, settings.timezone) : 'Time unavailable'} · {decision.flowId}@{decision.flowRevision} · {decision.evaluationDurationMs.toFixed(2)} ms · {decision.pinnedPolicies.length} pins</small>
            </article>
          ))}
          {!decisions.data.length ? <p className="muted-copy">No enforcement decisions have been recorded yet. Validate, save, promote or run a flow to create evidence.</p> : null}
        </div>
      ) : null}
    </section>
  )
}

function parseValue(value: string): unknown {
  try {
    return JSON.parse(value) as unknown
  } catch {
    return value
  }
}
