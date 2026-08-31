import { describe, expect, it } from 'vitest'

import { buildFleetQuery, dependencyLabel, fleetStatusTone, lifecycleActions, MAX_BULK_SELECTION, selectVisibleFleetRows, toggleFleetSelection } from './sessionOrchestratorModel'

describe('sessionOrchestratorModel', () => {
  it('builds bounded filters and preserves keyset cursors', () => {
    expect(buildFleetQuery({ limit: 20, namespace: ' data ', agentRef: 'agent@2', ownerId: 'owner', state: 'RUNNING' }, 'cursor/one')).toEqual({
      limit: 20, cursor: 'cursor/one', namespace: 'data', agentRef: 'agent@2', ownerId: 'owner', state: 'RUNNING',
    })
  })

  it('maps fleet state and dependency posture to accessible status tones', () => {
    expect(fleetStatusTone('RUNNING')).toBe('running')
    expect(fleetStatusTone('FAILED')).toBe('failed')
    expect(dependencyLabel({ dependencyHealth: 'DEGRADED', dependencyKeys: ['catalog'] })).toBe('DEGRADED · 1 pinned')
    expect(lifecycleActions('PAUSED')).toEqual(['resume', 'cancel'])
  })

  it('caps bulk selection at the backend limit', () => {
    const ids = Array.from({ length: MAX_BULK_SELECTION + 2 }, (_, index) => `session-${index}`)
    expect(selectVisibleFleetRows(ids, false)).toMatchObject({ limited: true, next: ids.slice(0, MAX_BULK_SELECTION) })
    expect(toggleFleetSelection(ids.slice(0, MAX_BULK_SELECTION), 'overflow')).toEqual({ limited: true, next: ids.slice(0, MAX_BULK_SELECTION) })
  })
})
