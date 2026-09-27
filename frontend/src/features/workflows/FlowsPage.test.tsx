import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { FlowsPage } from './FlowsPage'

const api = {
  flowExecutions: vi.fn((namespace: string, flowId: string) => Promise.resolve(flowId === 'daily_report'
    ? [{
      execution_id: 'run-1',
      tenant_id: 'default',
      state: 'RUNNING',
      epoch: 1,
      version: 2,
      namespace,
      flow_id: flowId,
      flow_revision: 7,
      inputs: {},
      outputs: {},
      labels: {},
      trigger: { type: 'cron' },
      created_by: 'scheduler',
      created_at: '2026-09-27T08:00:00Z',
      updated_at: '2026-09-27T08:05:00Z',
      timeout_at: null,
      cancel_deadline_at: null,
      lifecycle_evidence: {},
    }]
    : [])),
}

const flows = [
  {
    resource_id: 'flow-1',
    tenant_id: 'default',
    namespace: 'team.data',
    flow_id: 'daily_report',
    revision: 7,
    semantic_hash: 'abc1234567890def',
    etag: 'etag-1',
    lifecycle: 'ACTIVE',
    metadata: { labels: { team: 'analytics', priority: 'high' }, lifecycle: 'ACTIVE', resource_version: 1, created_by: 'operator', updated_by: 'operator' },
  },
  {
    resource_id: 'flow-2',
    tenant_id: 'default',
    namespace: 'team.ops',
    flow_id: 'manual_cleanup',
    revision: 2,
    semantic_hash: 'def1234567890abc',
    etag: 'etag-2',
    lifecycle: 'ACTIVE',
    metadata: { labels: {}, lifecycle: 'ACTIVE', resource_version: 1, created_by: 'operator', updated_by: 'operator' },
  },
]

const session = {
  principalId: 'operator',
  principalType: 'USER',
  display: 'Operator',
  tenantId: 'default',
  namespace: null,
  capabilities: {
    'flows.view': true,
    'flows.create': true,
    'executions.view': true,
    'triggers.view': true,
  },
  telemetryEnabled: false,
  serverVersion: 'test',
} as never

vi.mock('../../app/queries', () => ({
  useApiClient: () => api,
  useFlows: () => ({ data: flows, isPending: false, error: null, refetch: vi.fn() }),
  useTriggerRuntime: () => ({
    data: [{
      trigger_definition_id: 'trigger-1',
      tenant_id: 'default',
      namespace: 'team.data',
      flow_id: 'daily_report',
      flow_revision: 7,
      trigger_id: 'daily',
      trigger_type: 'core.cron',
      active: true,
      paused: false,
      checkpoint: {},
      cursor: null,
      last_evaluated_at: '2026-09-27T08:00:00Z',
      next_evaluation_at: '2026-09-28T08:00:00Z',
      last_occurrence_at: '2026-09-27T08:00:00Z',
      last_success_at: '2026-09-27T08:00:00Z',
      lag_seconds: 0,
      pending_count: 0,
      dead_letter_count: 0,
      consecutive_failures: 0,
      last_error: null,
      last_decision: 'scheduled run',
      updated_at: '2026-09-27T08:00:00Z',
    }],
    isPending: false,
    error: null,
  }),
}))

vi.mock('../../app/settings', () => ({
  useAppSettings: () => ({ settings: { tenant: 'default', namespace: '', token: 'token', locale: 'en', timezone: 'UTC' } }),
}))

afterEach(() => {
  cleanup()
  api.flowExecutions.mockClear()
})

describe('FlowsPage', () => {
  it('shows last run, trigger summary, labels and contract details', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <FlowsPage session={session} />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByRole('columnheader', { name: 'Last run' })).toBeVisible()
    expect(screen.getByRole('columnheader', { name: 'Trigger' })).toBeVisible()
    expect(screen.getByRole('columnheader', { name: 'Labels' })).toBeVisible()
    expect(screen.queryByRole('columnheader', { name: 'Contract' })).not.toBeInTheDocument()
    await waitFor(() => expect(screen.getByText('Running')).toBeVisible())
    expect(screen.getByText(/Sep 27, 2026/u)).toBeVisible()
    expect(screen.getByText(/Cron · next/u)).toBeVisible()
    expect(screen.getByText('team')).toBeVisible()
    expect(screen.getByText('analytics')).toBeVisible()
    expect(screen.getByText('No labels')).toBeVisible()
    expect(screen.getByText('Never run')).toBeVisible()

    screen.getByText('r7 details').click()
    expect(screen.getAllByText('Contract hash')[0]).toBeVisible()
    expect(screen.getByText('abc123456789')).toBeVisible()
    expect(api.flowExecutions).toHaveBeenCalledWith('team.data', 'daily_report', 1)
    expect(api.flowExecutions).toHaveBeenCalledWith('team.ops', 'manual_cleanup', 1)
  })
})
