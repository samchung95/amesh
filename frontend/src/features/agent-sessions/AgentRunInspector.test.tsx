import '@testing-library/jest-dom/vitest'

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { AgentSessionSummary } from '../../api/types'
import { AgentRunInspector } from './AgentRunInspector'

function session(overrides: Partial<AgentSessionSummary> = {}): AgentSessionSummary {
  return {
    sessionId: 'session-1',
    tenantId: 'tenant-a',
    namespace: 'examples',
    executionId: 'execution-1',
    taskRunId: 'task-run-1',
    attempt: 1,
    capabilityPinId: 'pin-1',
    envelopeDigest: `sha256:${'a'.repeat(64)}`,
    state: 'SUCCEEDED',
    phase: 'COMPLETE',
    version: 3,
    contextReceipt: null,
    counters: {
      billingCertainty: 'exact',
      cacheReadTokens: 0,
      cacheWriteTokens: 0,
      costUsd: '0',
      inputTokens: 0,
      loopIterations: 0,
      outputTokens: 0,
      pricedModelInvocations: 0,
      reasoningTokens: 0,
      repairAttempts: 0,
      toolCalls: 0,
      totalTokens: 0,
      turns: 1,
      unresolvedModelInvocations: 0,
    },
    finalResult: null,
    error: null,
    createdAt: '2026-09-26T00:00:00Z',
    updatedAt: '2026-09-26T00:01:00Z',
    completedAt: '2026-09-26T00:01:00Z',
    ...overrides,
  }
}

describe('AgentRunInspector', () => {
  it('labels agent and workflow states explicitly when they differ', () => {
    render(<AgentRunInspector session={session()} executionState="RUNNING" events={[]} />)

    expect(screen.getByText('Agent session: Succeeded · Workflow run: Still running')).toBeVisible()
    expect(screen.getByText('Workflow run')).toBeVisible()
    expect(screen.getByText('Still running')).toBeVisible()
  })
})
