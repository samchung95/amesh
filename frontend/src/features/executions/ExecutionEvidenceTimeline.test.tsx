import '@testing-library/jest-dom/vitest'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import type { ExecutionEvidenceEvent } from '../../api/types'
import { ExecutionEvidenceTimeline } from './ExecutionEvidenceTimeline'

function event(kind: ExecutionEvidenceEvent['kind'], payload: Record<string, unknown>): ExecutionEvidenceEvent {
  return {
    cursor: 1,
    event_id: `event-${kind}`,
    execution_id: 'execution-1',
    task_run_id: null,
    kind,
    event_type: `${kind.toLowerCase()}_event`,
    payload,
    occurred_at: '2026-09-02T00:00:00Z',
    ingested_at: '2026-09-02T00:00:00Z',
  }
}

describe('ExecutionEvidenceTimeline', () => {
  it('filters model, tool and decision evidence using every supported kind', async () => {
    const user = userEvent.setup()
    render(<ExecutionEvidenceTimeline events={[event('TOOL', { reason: 'Tool invoked' }), event('DECISION', { reason: 'Decision recorded' })]} locale="en-US" timezone="UTC" />)
    const select = screen.getByRole('combobox', { name: 'Event kind' })
    expect(screen.getAllByRole('option')).toHaveLength(14)
    await user.selectOptions(select, 'DECISION')
    expect(screen.getByText('Decision recorded')).toBeVisible()
    expect(screen.queryByText('Tool invoked')).not.toBeInTheDocument()
    await user.selectOptions(select, 'MODEL')
    expect(screen.getByText('No model evidence has arrived yet.')).toBeVisible()
  })

  it('renders unknown summary values as readable JSON', () => {
    render(
      <ExecutionEvidenceTimeline
        events={[
          event('LOG', { message: { detail: 'logged' } }),
          event('METRIC', { name: { key: 'latency' }, value: { amount: 42 }, unit: { name: 'ms' } }),
          event('ARTIFACT', { uri: { path: '/tmp/result' } }),
          event('OUTPUT', { sizeBytes: { bytes: 128 } }),
          event('STATE', { reason: { code: 'complete' } }),
        ]}
        locale="en-US"
        timezone="UTC"
      />,
    )

    expect(screen.getByText('{"detail":"logged"}')).toBeInTheDocument()
    expect(screen.getByText('{"key":"latency"} = {"amount":42} {"name":"ms"}')).toBeInTheDocument()
    expect(screen.getByText('{"path":"/tmp/result"}')).toBeInTheDocument()
    expect(screen.getByText('{"bytes":128} bytes committed')).toBeInTheDocument()
    expect(screen.getByText('{"code":"complete"}')).toBeInTheDocument()
    expect(screen.queryByText('[object Object]')).not.toBeInTheDocument()
  })
})
