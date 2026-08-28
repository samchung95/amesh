import type {
  AgentResourceRevision,
  AgentSessionControlEvent,
  AgentSessionControlSummary,
  AgentSessionHarnessCatalog,
} from '../api/types'

export function sessionStateLabel(state: string): string {
  return state.replaceAll('_', ' ')
}

export function sessionCanCancel(session: AgentSessionControlSummary): boolean {
  return ['QUEUED', 'RUNNING', 'PAUSED'].includes(session.state)
}

export function sessionCanPause(session: AgentSessionControlSummary): boolean {
  return session.state === 'RUNNING'
}

export function sessionCanResume(session: AgentSessionControlSummary): boolean {
  return session.state === 'PAUSED'
}

export function sessionCanRetry(session: AgentSessionControlSummary): boolean {
  return session.state === 'FAILED'
}

export function sessionIsLive(session: AgentSessionControlSummary): boolean {
  return ['CREATED', 'QUEUED', 'RUNNING', 'PAUSED', 'CANCELLING', 'RESTARTING'].includes(session.state)
}

export function sessionEventLabel(event: AgentSessionControlEvent): string {
  return event.eventType.replaceAll('.', ' ')
}

export function agentResourceOptions(resources: AgentResourceRevision[], kind: 'AGENT' | 'MODEL_POLICY') {
  return resources
    .filter((resource) => resource.kind === kind)
    .map((resource) => ({
      value: `${resource.namespace}/${resource.key}@${String(resource.revision)}`,
      label: `${resource.spec.title} · ${resource.namespace}/${resource.key}@${String(resource.revision)}`,
      description: resource.digest,
    }))
    .sort((left, right) => left.label.localeCompare(right.label))
}

export function agentPinnedProfile(resources: AgentResourceRevision[], agentRef: string): string {
  const agent = resources.find((resource) => resource.kind === 'AGENT' && `${resource.namespace}/${resource.key}@${String(resource.revision)}` === agentRef)
  if (!agent || agent.kind !== 'AGENT' || agent.spec.kind !== 'AGENT') return 'Select an agent to see its pinned model profile'
  return `${agent.spec.modelPolicy.key}@${String(agent.spec.modelPolicy.revision)}`
}

export function harnessCatalogOptions(catalog: AgentSessionHarnessCatalog) {
  return Object.entries(catalog)
    .map(([alias, entry]) => ({
      value: alias,
      label: `${alias} · ${entry.adapter}`,
      description: `${entry.adapterVersion} · ${entry.protocol}`,
    }))
    .sort((left, right) => left.label.localeCompare(right.label))
}

export function currentHarnessAlias(catalog: AgentSessionHarnessCatalog, session?: AgentSessionControlSummary | null): string {
  const entries = Object.entries(catalog).sort(([left], [right]) => left.localeCompare(right))
  const adapter = session?.harness?.adapter
  const matching = adapter ? entries.find(([, entry]) => entry.adapter === adapter) : undefined
  return matching?.[0] || (entries.length === 1 ? entries[0][0] : '')
}

export function mergeSessionSummary(base: AgentSessionControlSummary, detail: AgentSessionControlSummary): AgentSessionControlSummary {
  return {
    ...base,
    ...detail,
    sessionId: detail.sessionId || base.sessionId,
    executionId: detail.executionId === undefined ? base.executionId : detail.executionId,
    taskRunId: detail.taskRunId === undefined ? base.taskRunId : detail.taskRunId,
    attempt: detail.attempt === undefined ? base.attempt : detail.attempt,
    capabilityPinId: detail.capabilityPinId === undefined ? base.capabilityPinId : detail.capabilityPinId,
    envelopeDigest: detail.envelopeDigest === undefined ? base.envelopeDigest : detail.envelopeDigest,
    agentRef: detail.agentRef === undefined ? base.agentRef : detail.agentRef,
    modelProfile: detail.modelProfile === undefined ? base.modelProfile : detail.modelProfile,
    harness: detail.harness === undefined ? base.harness : detail.harness,
    version: detail.version === undefined ? base.version : detail.version,
    executionEpoch: detail.executionEpoch === undefined ? base.executionEpoch : detail.executionEpoch,
    counters: detail.counters === undefined ? base.counters : detail.counters,
    budgets: detail.budgets === undefined ? base.budgets : detail.budgets,
    result: detail.result === undefined ? base.result : detail.result,
    finalResult: detail.finalResult === undefined ? base.finalResult : detail.finalResult,
    error: detail.error === undefined ? base.error : detail.error,
  }
}

export function sessionHarnessLabel(session: AgentSessionControlSummary): string {
  const pin = session.harness
  if (!pin) return 'Harness provenance unavailable'
  return `${pin.adapter} · ${pin.adapterVersion}`
}
