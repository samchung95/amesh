import '@testing-library/jest-dom/vitest'

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import type { ExecutionDetail } from '../../api/types'
import { ExecutionDebugger } from './ExecutionDebugger'

function detail(): ExecutionDetail {
  return {
    execution: {
      execution_id: 'execution-1',
      tenant_id: 'tenant-a',
      state: 'RUNNING',
      epoch: 2,
      version: 5,
      namespace: 'examples',
      flow_id: 'evidence-flow',
      flow_revision: 7,
      inputs: {},
      outputs: {},
      labels: {},
      trigger: { type: 'manual' },
      created_by: 'operator',
      created_at: '2026-09-26T00:00:00Z',
      updated_at: '2026-09-26T00:00:05Z',
      timeout_at: null,
      cancel_deadline_at: null,
      lifecycle_evidence: {},
    },
    taskRunOffset: 0,
    taskRuns: [],
    taskRunSummary: {
      total: 0,
      waiting: 0,
      running: 0,
      retry_delay: 0,
      succeeded: 0,
      failed: 0,
      cancelled: 0,
    },
  }
}

describe('ExecutionDebugger outcome layout', () => {
  it('leads with outcome, actions and the simple trace before run counts', () => {
    const { container } = render(
      <MemoryRouter>
        <ExecutionDebugger
          detail={detail()}
          graph={undefined}
          graphLoading={false}
          evidence={[]}
          streamState="live"
          artifacts={[]}
          subflows={[]}
          parent={null}
          interventions={[]}
          humanTasks={[]}
          locale="en-US"
          timezone="UTC"
          canManage
          canExecute
          busy={false}
          onPreviewIntervention={vi.fn()}
          onApplyIntervention={vi.fn()}
          onPreviewBackfill={vi.fn()}
          onCreateBackfill={vi.fn()}
          onDownloadArtifact={vi.fn()}
        />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'What happened' })).toBeVisible()
    expect(screen.getAllByText('Run version (epoch / revision)')[0]).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Execution actions' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Simple execution trace' })).toBeVisible()

    const text = container.textContent ?? ''
    expect(text.indexOf('What happened')).toBeLessThan(text.indexOf('Execution actions'))
    expect(text.indexOf('Execution actions')).toBeLessThan(text.indexOf('Simple execution trace'))
    expect(text.indexOf('Simple execution trace')).toBeLessThan(text.indexOf('Total task runs'))
  })
})
