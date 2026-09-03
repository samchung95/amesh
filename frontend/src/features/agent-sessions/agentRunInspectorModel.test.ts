import { describe, expect, it } from 'vitest'

import type { AgentSessionEvent, AgentSessionSummary } from '../../api/types'
import { buildAgentRunInspectorModel } from './agentRunInspectorModel'

function session(overrides: Partial<AgentSessionSummary> = {}): AgentSessionSummary {
  return {
    sessionId: 'session-1', tenantId: 'tenant-1', namespace: 'examples.agent', executionId: 'execution-1', taskRunId: 'task-1', attempt: 2,
    capabilityPinId: 'pin-1', envelopeDigest: `sha256:${'a'.repeat(64)}`, state: 'RUNNING', phase: 'MODEL', version: 4,
    contextReceipt: {
      algorithm: 'amesh.recent-complete-turns/v1', byteHeadroom: 32, compacted: true,
      completeTurnsPreserved: true, contextBytes: 480, contextDigest: `sha256:${'c'.repeat(64)}`,
      contextEstimatedTokens: 120, contextMessageCount: 4, estimatedTokenHeadroom: 32,
      markerIncluded: true, messageHeadroom: 1, omittedSourceIndexes: [0],
      receiptDigest: `sha256:${'d'.repeat(64)}`, retainedSourceIndexes: [1, 2, 3],
      schemaVersion: 'amesh.agent-context/v1', transcriptBytes: 640,
      transcriptDigest: `sha256:${'e'.repeat(64)}`, transcriptMessageCount: 5, turn: 2,
    },
    counters: {
      billingCertainty: 'exact', cacheReadTokens: 0, cacheWriteTokens: 0, costUsd: '0.004',
      inputTokens: 80, loopIterations: 2, outputTokens: 30, pricedModelInvocations: 1,
      reasoningTokens: 10, repairAttempts: 1, toolCalls: 1, totalTokens: 120, turns: 2,
      unresolvedModelInvocations: 0,
    },
    finalResult: null, error: null, createdAt: '2026-08-26T00:00:00Z', updatedAt: '2026-08-26T00:01:00Z', completedAt: null,
    ...overrides,
  }
}

function event(eventIndex: number, eventType: string, payload: Record<string, unknown>): AgentSessionEvent {
  const occurredAt = `2026-08-26T00:00:${String(eventIndex).padStart(2, '0')}Z`
  return { eventId: `event-${String(eventIndex)}`, sessionId: 'session-1', eventIndex, eventKey: `turn:${String(eventIndex)}`, eventType, payload, occurredAt }
}

describe('buildAgentRunInspectorModel', () => {
  it('orders canonical events and projects bounded run facts without model rationale', () => {
    const model = buildAgentRunInspectorModel({
      session: session({ phase: 'APPROVAL' }),
      events: [
        event(4, 'tool.result', { turn: 2, tool: 'lookup', result: { rows: 2 }, toolCalls: 1 }),
        event(2, 'model.response', { turn: 1, model: 'luna', providerPin: { providerId: 'openrouter', providerRevision: '7' }, usageNormalized: { totalTokens: 120, promptCache: { state: 'reported', hitRatio: 0.5 } }, costNormalized: { amountUsd: '0.004' } }),
        event(3, 'policy.authorized', { turn: 2, tool: 'lookup', impact: 'READ_ONLY', approval: { required: false } }),
        event(5, 'output.accepted', { turn: 2, schemaValid: true, businessAssertionsPassed: 2, result: { answer: 'done' } }),
      ],
    })

    expect(model.displayState).toBe('WAITING_APPROVAL')
    expect(model.turn).toBe(2)
    expect(model.events.map((item) => item.eventIndex)).toEqual([2, 3, 4, 5])
    expect(model.facts.find((group) => group.key === 'model')?.facts).toEqual(expect.arrayContaining([
      { label: 'Model', value: 'luna' },
      { label: 'Provider', value: 'openrouter' },
    ]))
    expect(model.facts.find((group) => group.key === 'tools')?.facts).toEqual(expect.arrayContaining([{ label: 'Tools', value: 'lookup' }]))
    expect(model.facts.find((group) => group.key === 'schema')?.facts).toEqual(expect.arrayContaining([{ label: 'Schema valid', value: 'true' }]))
    expect(model.events.find((item) => item.eventType === 'tool.result')?.payloadText).toContain('rows')
  })

  it('uses enclosing execution state for controls and marks redacted or malformed evidence explicitly', () => {
    const model = buildAgentRunInspectorModel({
      session: session({ state: 'SUCCEEDED', phase: 'COMPLETE' }),
      executionState: 'PAUSED',
      events: [
        event(2, 'model.response', { model: '[REDACTED]' }),
        { ...event(1, 'session.started', {}), eventIndex: 0 },
      ],
    })

    expect(model.displayState).toBe('PAUSED')
    expect(model.status).toBe('malformed')
    expect(model.malformedCount).toBe(1)
    expect(model.events[1]).toMatchObject({ redacted: true, malformed: false, summary: 'Model response' })
    expect(model.events[1].facts).toContainEqual({ label: 'Model', value: 'Redacted by server', redacted: true })
    expect(model.events[1].payloadText).toContain('REDACTED')
  })

  it('returns an explicit empty state when no authorized session summary exists', () => {
    expect(buildAgentRunInspectorModel({ session: null })).toMatchObject({ status: 'empty', events: [], facts: [] })
  })
})
