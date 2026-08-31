import { describe, expect, it } from 'vitest'

import type { AgentProgressEvent } from '../api/types'
import { appendAgentProgress, progressLabel, progressTone } from './agentProgressModel'

function event(eventIndex: number, activity: AgentProgressEvent['frame']['activity'], status: AgentProgressEvent['frame']['status'], segmentId: string | null): AgentProgressEvent {
  return {
    schemaVersion: 'amesh.agent-progress-event/v1',
    serviceSessionId: 'session-1',
    eventId: `event-${eventIndex}`,
    eventIndex,
    cursor: `opaque-${eventIndex}`,
    acceptedAt: `2026-08-31T00:00:0${eventIndex}Z`,
    frame: {
      schemaVersion: 'amesh.agent-progress/v1',
      attemptSessionId: 'attempt-1',
      attempt: 1,
      turn: 1,
      activity,
      status,
      activityId: `activity-${eventIndex}`,
      segmentId,
      sourceId: 'source-1',
      sourceSequence: eventIndex,
      occurredAt: `2026-08-31T00:00:0${eventIndex}Z`,
      detail: { kind: 'STATUS', code: `${activity.toLowerCase()}.${status.toLowerCase()}`, label: `${activity} ${status}` },
    },
  }
}

describe('agent progress model', () => {
  it('keeps separate thinking segments around tool work in canonical order', () => {
    const first = event(1, 'THINKING', 'STARTED', 'thinking-1')
    const tool = event(2, 'TOOL', 'COMPLETED', null)
    const second = event(3, 'THINKING', 'STARTED', 'thinking-2')
    const result = appendAgentProgress([], [first, tool, second])

    expect(result.events.map((item) => item.frame.activity)).toEqual(['THINKING', 'TOOL', 'THINKING'])
    expect(result.events.map((item) => item.frame.segmentId)).toEqual(['thinking-1', null, 'thinking-2'])
  })

  it('deduplicates reconnect pages by either opaque cursor or event id', () => {
    const first = event(1, 'MODEL', 'STARTED', null)
    const duplicateCursor = { ...first, eventId: 'different-id' }
    const duplicateId = { ...event(2, 'TOOL', 'STARTED', null), cursor: first.cursor }
    const next = event(3, 'TERMINAL', 'COMPLETED', null)
    const result = appendAgentProgress([first], [duplicateCursor, duplicateId, next])

    expect(result.events.map((item) => item.eventId)).toEqual(['event-1', 'event-3'])
    expect(result.isTerminal).toBe(true)
  })

  it('preserves server order when a retry resets the attempt-local event index', () => {
    const priorTerminal = event(4, 'TERMINAL', 'FAILED', null)
    const retryStarted = {
      ...event(1, 'THINKING', 'STARTED', 'thinking-retry'),
      eventId: 'retry-event-1',
      cursor: 'opaque-attempt-2-event-1',
      frame: {
        ...event(1, 'THINKING', 'STARTED', 'thinking-retry').frame,
        attemptSessionId: 'attempt-2',
        attempt: 2,
      },
    }

    const result = appendAgentProgress([priorTerminal], [retryStarted])

    expect(result.events.map((item) => item.frame.attempt)).toEqual([1, 2])
    expect(result.isTerminal).toBe(false)
    expect(result.cursor).toBe('opaque-attempt-2-event-1')
  })

  it('uses safe public status labels and tones', () => {
    const frame = event(1, 'THINKING', 'STARTED', 'thinking-1').frame
    expect(progressLabel(frame)).toBe('THINKING STARTED')
    expect(progressTone(frame)).toBe('live')
    expect(progressTone({ ...frame, activity: 'TERMINAL', status: 'COMPLETED' })).toBe('success')
  })
})
