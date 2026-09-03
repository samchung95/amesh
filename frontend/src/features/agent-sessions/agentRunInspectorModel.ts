import type {
  AgentSessionEvent,
  AgentSessionSummary,
  ExecutionState,
} from '../../api/types'

export interface AgentRunInspectorFact {
  label: string
  value: string
  redacted?: boolean
}

export interface AgentRunInspectorEvent {
  eventId: string
  eventIndex: number | null
  eventKey: string
  eventType: string
  occurredAt: string | null
  summary: string
  facts: AgentRunInspectorFact[]
  payloadText: string | null
  redacted: boolean
  malformed: boolean
}

export interface AgentRunInspectorFactGroup {
  key: string
  label: string
  emptyLabel: string
  facts: AgentRunInspectorFact[]
}

export interface AgentRunInspectorModel {
  status: 'empty' | 'ready' | 'malformed'
  displayState: string
  sessionState: string
  executionState: ExecutionState | null
  phase: string
  turn: number
  attempt: number
  counters: AgentSessionSummary['counters'] | null
  facts: AgentRunInspectorFactGroup[]
  events: AgentRunInspectorEvent[]
  malformedCount: number
}

export interface BuildAgentRunInspectorModelInput {
  session: AgentSessionSummary | null | undefined
  executionState?: ExecutionState | null
  events?: AgentSessionEvent[]
}

const sessionStates = new Set(['RUNNING', 'SUCCEEDED', 'FAILED'])
const sessionPhases = new Set(['READY', 'MODEL', 'POLICY', 'APPROVAL', 'TOOL', 'VALIDATING', 'COMPLETE'])

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {}
}

function scalar(value: unknown): string | null {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value)
  return null
}

function hasRedactedMarker(value: unknown): boolean {
  if (typeof value === 'string') return /redact|\[redacted\]/i.test(value)
  if (Array.isArray(value)) return value.some(hasRedactedMarker)
  if (typeof value === 'object' && value !== null) {
    const object = value as Record<string, unknown>
    return object.redacted === true || Object.entries(object).some(([key, item]) => /redact/i.test(key) || hasRedactedMarker(item))
  }
  return false
}

function fact(label: string, value: unknown): AgentRunInspectorFact | null {
  if (value === null || value === undefined) return null
  const redacted = hasRedactedMarker(value)
  if (redacted) return { label, value: 'Redacted by server', redacted: true }
  const text = scalar(value)
  if (text !== null) return { label, value: text }
  if (Array.isArray(value)) return { label, value: `${String(value.length)} item${value.length === 1 ? '' : 's'}` }
  if (typeof value === 'object') return { label, value: `${String(Object.keys(value).length)} fields` }
  return null
}

function jsonFact(label: string, value: unknown): AgentRunInspectorFact | null {
  if (value === null || value === undefined) return null
  if (hasRedactedMarker(value)) return { label, value: 'Redacted by server', redacted: true }
  return { label, value: JSON.stringify(value, null, 2) }
}

function uniqueFacts(values: Array<AgentRunInspectorFact | null>): AgentRunInspectorFact[] {
  const seen = new Set<string>()
  return values.filter((item): item is AgentRunInspectorFact => {
    if (!item) return false
    const key = `${item.label}:${item.value}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function eventIsValid(event: AgentSessionEvent): boolean {
  return Boolean(event.eventId && event.eventKey && event.eventType)
    && Number.isInteger(event.eventIndex)
    && event.eventIndex > 0
    && typeof event.occurredAt === 'string'
    && Number.isFinite(Date.parse(event.occurredAt))
    && typeof event.payload === 'object'
    && event.payload !== null
}

function eventFacts(event: AgentSessionEvent): AgentRunInspectorFact[] {
  const payload = asRecord(event.payload)
  const approval = asRecord(payload.approval)
  const counters = asRecord(payload.counters)
  const usage = asRecord(payload.usageNormalized)
  const cache = asRecord(payload.promptCache ?? usage.promptCache)
  const providerPin = asRecord(payload.providerPin)
  return uniqueFacts([
    fact('Turn', payload.turn),
    fact('Model', payload.model),
    fact('Provider', providerPin.providerId),
    fact('Provider revision', providerPin.providerRevision),
    fact('Action', payload.action),
    fact('Tool', payload.tool),
    fact('Impact', payload.impact),
    fact('Approval', approval.decision ?? approval.required),
    fact('Tool calls', payload.toolCalls ?? counters.toolCalls),
    fact('Tokens', payload.totalTokens ?? usage.totalTokens ?? counters.totalTokens),
    fact('Cost (USD)', payload.costUsd ?? asRecord(payload.costNormalized).amountUsd ?? counters.costUsd),
    fact('Cache', cache.state ?? cache.hitRatio),
    fact('Schema', payload.schemaValid),
    fact('Repair scheduled', payload.repairScheduled),
    fact('Error', payload.error),
    fact('Evaluation', payload.passed),
    fact('Memory scope', payload.scope),
    fact('Release', payload.decision),
  ])
}

function boundedPayloadText(payload: Record<string, unknown>): string | null {
  try {
    const serialized = JSON.stringify(payload, null, 2)
    return serialized.length > 12_000 ? `${serialized.slice(0, 12_000)}\n… payload truncated by inspector` : serialized
  } catch {
    return null
  }
}

function eventSummary(event: AgentSessionEvent): string {
  const payload = asRecord(event.payload)
  const turn = scalar(payload.turn)
  const tool = scalar(payload.tool)
  const evaluationKey = scalar(payload.key)
  const suffix = turn ? ` · turn ${turn}` : ''
  switch (event.eventType) {
    case 'session.started': return `Session started${suffix}`
    case 'context.projected': return `Context projected${suffix}`
    case 'context.compacted': return `Context compacted${suffix}`
    case 'model.response': return `Model response${suffix}`
    case 'policy.authorized': return `Tool policy authorized${tool ? ` · ${tool}` : ''}`
    case 'tool.result': return `Tool result${tool ? ` · ${tool}` : ''}`
    case 'evaluation.completed': return `Evaluation completed${evaluationKey ? ` · ${evaluationKey}` : ''}`
    case 'release.approved': return 'Human release approved'
    case 'memory.written': return 'Memory write recorded'
    case 'output.accepted': return 'Structured output accepted'
    case 'output.rejected': return 'Structured output rejected'
    case 'session.failed': return 'Session failed'
    default: return event.eventType || 'Unknown canonical event'
  }
}

function latest(events: AgentSessionEvent[], eventType: string): AgentSessionEvent | undefined {
  return [...events].reverse().find((event) => event.eventType === eventType)
}

function stateFor(session: AgentSessionSummary, executionState: ExecutionState | null): string {
  if (executionState === 'PAUSED' || executionState === 'CANCELLING' || executionState === 'CANCELLED' || executionState === 'RESTARTING') return executionState
  if (session.phase === 'APPROVAL' && session.state === 'RUNNING') return 'WAITING_APPROVAL'
  return session.state
}

function summaryFacts(session: AgentSessionSummary, events: AgentSessionEvent[]): AgentRunInspectorFactGroup[] {
  const modelEvent = latest(events, 'model.response')
  const contextEvent = latest(events, 'context.compacted') ?? latest(events, 'context.projected')
  const accepted = latest(events, 'output.accepted')
  const rejected = events.filter((event) => event.eventType === 'output.rejected')
  const toolEvents = events.filter((event) => event.eventType === 'tool.result' || event.eventType === 'policy.authorized')
  const approvalEvents = events.filter((event) => event.eventType === 'policy.authorized' || event.eventType === 'release.approved')
  const context = asRecord(contextEvent?.payload ?? asRecord(modelEvent?.payload).contextReceipt ?? session.contextReceipt)
  const modelPayload = asRecord(modelEvent?.payload)
  const usage = asRecord(modelPayload.usageNormalized)
  const cache = asRecord(modelPayload.promptCache ?? usage.promptCache)
  const schemaPayload = asRecord(accepted?.payload ?? latest(events, 'output.rejected')?.payload)
  const finalResult = session.finalResult ?? asRecord(accepted?.payload).result
  const toolNames = [...new Set(toolEvents.map((event) => scalar(asRecord(event.payload).tool)).filter((name): name is string => Boolean(name)))]
  const approvals = approvalEvents.map((event) => {
    const payload = asRecord(event.payload)
    const approval = asRecord(payload.approval)
    return scalar(approval.decision ?? payload.decision ?? approval.required)
  }).filter((value): value is string => Boolean(value))

  return [
    {
      key: 'model', label: 'Model', emptyLabel: 'No model attempt has been recorded.', facts: uniqueFacts([
        fact('Model', modelPayload.model),
        fact('Provider', asRecord(modelPayload.providerPin).providerId),
        fact('Provider revision', asRecord(modelPayload.providerPin).providerRevision),
      ]),
    },
    {
      key: 'tools', label: 'Tools', emptyLabel: 'No tool proposal or result has been recorded.', facts: uniqueFacts([
        fact('Tools', toolNames.length ? toolNames.join(', ') : null),
        fact('Tool events', toolEvents.length || null),
      ]),
    },
    {
      key: 'approvals', label: 'Approvals', emptyLabel: 'No approval decision has been recorded.', facts: uniqueFacts([
        fact('Decisions', approvals.length ? approvals.join(', ') : null),
        fact('Approval events', approvalEvents.length || null),
      ]),
    },
    {
      key: 'retry', label: 'Retry / repair', emptyLabel: 'No retry or repair evidence has been recorded.', facts: uniqueFacts([
        fact('Attempt', session.attempt),
        fact('Repair attempts', session.counters.repairAttempts),
        fact('Rejected outputs', rejected.length || null),
      ]),
    },
    {
      key: 'context', label: 'Context', emptyLabel: 'No context projection receipt has been recorded.', facts: uniqueFacts([
        fact('Turn', context.turn),
        fact('Messages', context.contextMessageCount),
        fact('Bytes', context.contextBytes),
        fact('Estimated tokens', context.contextEstimatedTokens),
        fact('Compacted', context.compacted),
      ]),
    },
    {
      key: 'usage', label: 'Tokens / cost / cache', emptyLabel: 'No model usage or cache evidence has been recorded.', facts: uniqueFacts([
        fact('Total tokens', session.counters.totalTokens || usage.totalTokens),
        fact('Cost (USD)', session.counters.costUsd || asRecord(modelPayload.costNormalized).amountUsd),
        fact('Cache state', cache.state),
        fact('Cache hit ratio', cache.hitRatio),
      ]),
    },
    {
      key: 'schema', label: 'Schema decisions', emptyLabel: 'No structured-output schema decision has been recorded.', facts: uniqueFacts([
        fact('Schema valid', schemaPayload.schemaValid),
        fact('Business assertions', schemaPayload.businessAssertionsPassed),
        fact('Repair scheduled', schemaPayload.repairScheduled),
      ]),
    },
    {
      key: 'final', label: 'Final result', emptyLabel: 'No final structured result has been recorded.', facts: [jsonFact('Structured result', finalResult)].filter((item): item is AgentRunInspectorFact => Boolean(item)),
    },
    {
      key: 'failure', label: 'Failure', emptyLabel: 'No failure evidence has been recorded.', facts: uniqueFacts([
        fact('Session error', session.error),
        fact('Recorded failures', events.filter((event) => event.eventType === 'session.failed').length || null),
      ]),
    },
  ]
}

export function buildAgentRunInspectorModel({ session, executionState = null, events = [] }: BuildAgentRunInspectorModelInput): AgentRunInspectorModel {
  if (!session) {
    return {
      status: 'empty', displayState: 'UNKNOWN', sessionState: 'UNKNOWN', executionState, phase: 'UNKNOWN', turn: 0, attempt: 0,
      counters: null, facts: [], events: [], malformedCount: 0,
    }
  }

  const malformedSummary = !session.sessionId || !session.executionId || !session.taskRunId || !sessionStates.has(session.state) || !sessionPhases.has(session.phase)
  const projectedEvents = events.map((event): AgentRunInspectorEvent => {
    const valid = eventIsValid(event)
    return {
      eventId: event.eventId || 'malformed-event',
      eventIndex: Number.isInteger(event.eventIndex) ? event.eventIndex : null,
      eventKey: event.eventKey || 'unknown-event',
      eventType: event.eventType || 'unknown',
      occurredAt: typeof event.occurredAt === 'string' && Number.isFinite(Date.parse(event.occurredAt)) ? event.occurredAt : null,
      summary: valid ? eventSummary(event) : 'Malformed canonical event; details withheld.',
      facts: valid ? eventFacts(event) : [],
      payloadText: valid ? boundedPayloadText(event.payload ?? {}) : null,
      redacted: valid && hasRedactedMarker(event.payload ?? {}),
      malformed: !valid,
    }
  }).sort((left, right) => {
    const indexOrder = (left.eventIndex ?? Number.MAX_SAFE_INTEGER) - (right.eventIndex ?? Number.MAX_SAFE_INTEGER)
    if (indexOrder) return indexOrder
    return (left.occurredAt ? Date.parse(left.occurredAt) : Number.MAX_SAFE_INTEGER) - (right.occurredAt ? Date.parse(right.occurredAt) : Number.MAX_SAFE_INTEGER)
  })
  const validEvents = events.filter(eventIsValid)
  const latestTurn = [...validEvents].reverse().map((event) => asRecord(event.payload).turn).find((value): value is number => typeof value === 'number' && Number.isInteger(value))
  const malformedCount = projectedEvents.filter((event) => event.malformed).length + (malformedSummary ? 1 : 0)
  return {
    status: malformedCount ? 'malformed' : 'ready',
    displayState: stateFor(session, executionState),
    sessionState: session.state,
    executionState,
    phase: session.phase,
    turn: latestTurn ?? session.counters.turns,
    attempt: session.attempt,
    counters: session.counters,
    facts: summaryFacts(session, validEvents),
    events: projectedEvents,
    malformedCount,
  }
}
