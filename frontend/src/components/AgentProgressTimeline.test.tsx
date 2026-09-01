import { render, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { AgentProgressEvent, AgentProgressStreamItem } from '../api/types'
import { AgentProgressTimeline, type AgentProgressApi } from './AgentProgressTimeline'
import { progressImagesFromSessionEvents } from './agentProgressModel'

function event(index: number, activity: AgentProgressEvent['frame']['activity'], status: AgentProgressEvent['frame']['status'], segmentId: string | null = null): AgentProgressEvent {
  return {
    schemaVersion: 'amesh.agent-progress-event/v1', serviceSessionId: 'session-1', eventId: `event-${index}`, eventIndex: index, cursor: `cursor-${index}`, acceptedAt: `2026-08-31T00:00:0${index}Z`,
    frame: { schemaVersion: 'amesh.agent-progress/v1', attemptSessionId: 'attempt-1', attempt: 1, turn: 1, activity, status, activityId: `activity-${index}`, segmentId, sourceId: 'source', sourceSequence: index, occurredAt: `2026-08-31T00:00:0${index}Z`, detail: { kind: 'STATUS', code: 'progress', label: `${activity} ${status}` } },
  }
}

function apiFor(pageEvents: AgentProgressEvent[], streamItems: AgentProgressStreamItem[] = []): AgentProgressApi {
  const stream: AgentProgressApi['streamAgentSessionProgress'] = (_sessionId, _after, onItem) => {
    streamItems.forEach((item) => onItem(item))
    return Promise.resolve()
  }
  return {
    agentSessionProgress: vi.fn(() => Promise.resolve({ sessionId: 'session-1', events: pageEvents, nextCursor: pageEvents.at(-1)?.cursor || 'cursor-0' })),
    streamAgentSessionProgress: vi.fn(stream),
  }
}

describe('AgentProgressTimeline', () => {
  it('projects only validated durable image metadata and deduplicates retries', () => {
    const image = { schemaVersion: 'amesh.image-display/v1', reference: `sha256:${'a'.repeat(64)}`, mediaType: 'image/png', sizeBytes: 2048, checksumSha256: 'a'.repeat(64) }
    expect(progressImagesFromSessionEvents([
      { payload: { inputImages: [image, image, { ...image, checksumSha256: 'invalid' }] } },
      { payload: { inputImages: 'not-an-array' } },
    ])).toEqual([{ reference: image.reference, mediaType: 'image/png', sizeBytes: 2048, checksumSha256: 'a'.repeat(64) }])
  })

  it('renders the accessible chronological live timeline', async () => {
    const api = apiFor([event(1, 'THINKING', 'STARTED', 'thinking-1')], [event(2, 'TOOL', 'COMPLETED'), event(3, 'THINKING', 'STARTED', 'thinking-2'), event(4, 'TERMINAL', 'COMPLETED')])
    render(<AgentProgressTimeline api={api} sessionId="session-1" isLive />)

    await waitFor(() => expect(screen.getByRole('list', { name: 'Chronological agent progress' })).toBeInTheDocument())
    expect(screen.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      expect.stringContaining('THINKING STARTED'),
      expect.stringContaining('TOOL COMPLETED'),
      expect.stringContaining('THINKING STARTED'),
      expect.stringContaining('TERMINAL COMPLETED'),
    ])
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('does not render raw image bytes and exposes metadata-only fallback', async () => {
    const api = apiFor([])
    render(<AgentProgressTimeline api={api} sessionId="session-1" images={[{ reference: 'artifact://image/one', mediaType: 'image/png', sizeBytes: 2048, checksumSha256: 'abcdef1234567890', altText: 'Research chart', thumbnailUrl: 'data:image/png;base64,raw-bytes' }]} />)

    await waitFor(() => expect(screen.getByText('Research chart')).toBeInTheDocument())
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
    expect(screen.queryByText(/raw-bytes/)).not.toBeInTheDocument()
    expect(screen.getByText(/image\/png · 2 KB/)).toBeInTheDocument()
  })

  it('renders explicit loading, empty, and initial failure states', async () => {
    const pending = new Promise<{ sessionId: string; events: AgentProgressEvent[]; nextCursor: string }>(() => undefined)
    const loadingApi: AgentProgressApi = { agentSessionProgress: vi.fn(() => pending), streamAgentSessionProgress: vi.fn() }
    const loading = render(<AgentProgressTimeline api={loadingApi} sessionId="loading" />)
    expect(screen.getByText('Loading chronological progress…')).toBeInTheDocument()
    loading.unmount()

    const empty = render(<AgentProgressTimeline api={apiFor([])} sessionId="empty" />)
    await waitFor(() => expect(screen.getByText('No safe progress has been recorded yet.')).toBeInTheDocument())
    empty.unmount()

    const failedApi: AgentProgressApi = {
      agentSessionProgress: vi.fn(() => Promise.reject(new Error('journal unavailable'))),
      streamAgentSessionProgress: vi.fn(),
    }
    const failed = render(<AgentProgressTimeline api={failedApi} sessionId="failed" />)
    await waitFor(() => expect(within(failed.container).getByRole('alert')).toHaveTextContent('journal unavailable'))
    expect(within(failed.container).getByText('Unavailable', { selector: '.agent-progress-connection' })).toBeInTheDocument()
  })

  it('shows reconnecting state after a live stream interruption', async () => {
    const api = apiFor([event(1, 'THINKING', 'STARTED', 'thinking-1')])
    api.streamAgentSessionProgress = vi.fn(() => Promise.reject(new Error('connection lost')))
    const rendered = render(<AgentProgressTimeline api={api} sessionId="session-1" isLive />)

    await waitFor(() => expect(within(rendered.container).getByText(/Reconnecting from the last durable cursor/)).toBeInTheDocument())
    expect(within(rendered.container).getByText('Reconnecting', { selector: '.agent-progress-connection' })).toBeInTheDocument()
  })
})
