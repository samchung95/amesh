import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useNavigate } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { AgentSessionSummary, ExecutionEvidenceEvent } from '../../api/types'
import { ExecutionDetailPage } from './ExecutionDetailPage'

function evidenceEvent(executionId: string): ExecutionEvidenceEvent & { nextCursor: string } {
  return {
    cursor: executionId === 'execution-a' ? 1 : 2,
    event_id: `${executionId}-event`,
    execution_id: executionId,
    task_run_id: null,
    kind: 'LOG',
    event_type: 'log.info',
    payload: { message: `${executionId} evidence` },
    occurred_at: '2026-08-28T00:00:00Z',
    ingested_at: '2026-08-28T00:00:00Z',
    nextCursor: executionId,
  }
}

function agentSession(overrides: Partial<AgentSessionSummary> = {}): AgentSessionSummary {
  return {
    sessionId: 'session-1',
    tenantId: 'tenant-a',
    namespace: 'examples',
    executionId: 'execution-a',
    taskRunId: 'task-run-1',
    attempt: 1,
    capabilityPinId: 'pin-1',
    envelopeDigest: `sha256:${'a'.repeat(64)}`,
    state: 'SUCCEEDED',
    phase: 'COMPLETE',
    version: 2,
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
    createdAt: '2026-08-28T00:00:00Z',
    updatedAt: '2026-08-28T00:01:00Z',
    completedAt: '2026-08-28T00:01:00Z',
    ...overrides,
  }
}

const api = {
  execution: vi.fn((executionId: string) => Promise.resolve({
    execution: {
      execution_id: executionId,
      tenant_id: 'tenant-a',
      state: 'RUNNING',
      epoch: 1,
      version: 1,
      namespace: 'examples',
      flow_id: executionId,
      flow_revision: 1,
      inputs: {},
      outputs: {},
      labels: {},
      trigger: { type: 'manual' },
      created_by: 'operator',
      created_at: '2026-08-28T00:00:00Z',
      updated_at: '2026-08-28T00:00:00Z',
      timeout_at: null,
      cancel_deadline_at: null,
      lifecycle_evidence: {},
    },
    taskRuns: [],
  })),
  executionGraph: vi.fn().mockResolvedValue({ nodes: [], edges: [] }),
  executionEvidence: vi.fn().mockResolvedValue({ items: [], nextCursor: null }),
  executionFiles: vi.fn().mockResolvedValue([]),
  executionSubflows: vi.fn().mockResolvedValue([]),
  executionParentSubflow: vi.fn().mockResolvedValue(null),
  executionInterventions: vi.fn().mockResolvedValue([]),
  executionAgentSessions: vi.fn().mockResolvedValue([]),
  executionAgentSessionDetail: vi.fn().mockResolvedValue({ session: agentSession(), events: [], nextEventIndex: null }),
  agentSessionProgress: vi.fn().mockResolvedValue({ sessionId: 'session-1', events: [], nextCursor: '' }),
  streamAgentSessionProgress: vi.fn(async (_sessionId: string, _after: string | null, _onItem: unknown, signal: AbortSignal) => {
    await new Promise<void>((resolve) => {
      if (signal.aborted) resolve()
      else signal.addEventListener('abort', () => resolve(), { once: true })
    })
  }),
  streamExecutionEvidence: vi.fn(async (
    executionId: string,
    _cursor: string | null,
    receive: (event: ExecutionEvidenceEvent & { nextCursor: string }) => void,
    signal: AbortSignal,
  ) => {
    receive(evidenceEvent(executionId))
    await new Promise<void>((resolve) => {
      if (signal.aborted) resolve()
      else signal.addEventListener('abort', () => resolve(), { once: true })
    })
  }),
}

vi.mock('../../app/queries', () => ({ useApiClient: () => api }))

vi.mock('../../app/settings', () => ({
  useAppSettings: () => ({ settings: { tenant: 'tenant-a', locale: 'en', timezone: 'UTC' } }),
}))

vi.mock('./ExecutionDebugger', () => ({
  ExecutionDebugger: ({ evidence }: { evidence: ExecutionEvidenceEvent[] }) => (
    <output data-testid="execution-evidence">
      {evidence.map((event) => event.execution_id).join(',')}
    </output>
  ),
}))

function RouteReuseHarness() {
  const navigate = useNavigate()
  return (
    <>
      <button type="button" onClick={() => void navigate('/executions/execution-b')}>Open execution B</button>
      <Routes>
        <Route path="/executions/:executionId" element={<ExecutionDetailPage session={session} />} />
      </Routes>
    </>
  )
}

const session = {
  capabilities: {
    'executions.manage': false,
    'executions.execute': false,
    'humanTasks.view': false,
  },
} as never

beforeEach(() => {
  vi.clearAllMocks()
  api.executionAgentSessions.mockResolvedValue([])
  api.executionAgentSessionDetail.mockResolvedValue({ session: agentSession(), events: [], nextEventIndex: null })
  api.agentSessionProgress.mockResolvedValue({ sessionId: 'session-1', events: [], nextCursor: '' })
})

describe('execution detail route reuse', () => {
  it('does not retain streamed evidence from the previous execution', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const user = userEvent.setup()
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/executions/execution-a']}>
          <RouteReuseHarness />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('execution-evidence')).toHaveTextContent('execution-a'))
    await user.click(screen.getByRole('button', { name: 'Open execution B' }))
    await waitFor(() => expect(screen.getByTestId('execution-evidence')).toHaveTextContent('execution-b'))
    expect(screen.getByTestId('execution-evidence')).not.toHaveTextContent('execution-a')
  })

  it('keeps detailed agent evidence collapsed and labels differing run states', async () => {
    api.executionAgentSessions.mockResolvedValue([agentSession()])
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const user = userEvent.setup()
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/executions/execution-a']}>
          <Routes>
            <Route path="/executions/:executionId" element={<ExecutionDetailPage session={session} />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    const disclosureSummary = await screen.findByText('Detailed agent session evidence')
    const disclosure = disclosureSummary.closest('details')
    expect(disclosure).not.toHaveAttribute('open')
    expect(screen.getAllByText('Agent session: Succeeded · Workflow run: Still running')[0]).toBeVisible()
    expect(screen.getByLabelText('Agent run inspector')).not.toBeVisible()

    await user.click(disclosureSummary)

    expect(disclosure).toHaveAttribute('open')
    expect(screen.getByLabelText('Agent run inspector')).toBeVisible()
  })
})
