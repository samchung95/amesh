import { describe, expect, it } from 'vitest'

import {
  isPromotionGate,
  isReleaseAction,
  isReleaseHistory,
  isReleaseTarget,
} from './releaseControlsModel'

const target = {
  tenantId: 'tenant-a',
  targetKind: 'WORKFLOW',
  targetKey: 'team.research',
  activeRevision: 3,
  activeConfigurationDigest: 'sha256:configuration',
  state: 'ACTIVE',
  version: 4,
  updatedAt: '2026-09-04T00:00:00Z',
}

const historyEntry = {
  eventId: 'event-1',
  tenantId: 'tenant-a',
  targetKind: 'WORKFLOW',
  targetKey: 'team.research',
  action: 'PROMOTE',
  fromRevision: 2,
  toRevision: 3,
  toConfigurationDigest: 'sha256:configuration',
  gateDigest: 'sha256:gate',
  actorId: 'user-a',
  reason: 'Approved release',
  version: 4,
  occurredAt: '2026-09-04T00:00:00Z',
}

const gate = {
  gateId: 'gate-1',
  tenantId: 'tenant-a',
  policyId: 'policy-1',
  policyDigest: 'sha256:policy',
  targetKind: 'WORKFLOW',
  targetKey: 'team.research',
  targetRevision: 3,
  configurationDigest: 'sha256:configuration',
  evidenceDigests: ['sha256:evidence'],
  passed: true,
  failures: [],
  evaluatedAt: '2026-09-04T00:00:00Z',
}

function withoutField(value: Record<string, unknown>, field: string): Record<string, unknown> {
  return Object.fromEntries(Object.entries(value).filter(([key]) => key !== field))
}

describe('release response guards', () => {
  it('accepts complete release responses', () => {
    expect(isReleaseTarget(target)).toBe(true)
    expect(isReleaseHistory([historyEntry])).toBe(true)
    expect(isPromotionGate(gate)).toBe(true)
    expect(isReleaseAction({ target, event: historyEntry })).toBe(true)
  })

  it('rejects history entries without an event ID even when the destination revision is null', () => {
    const missingEventId = withoutField({ ...historyEntry, toRevision: null }, 'eventId')
    expect(isReleaseHistory([missingEventId])).toBe(false)
  })

  it('rejects gates without evidence and failure arrays', () => {
    const missingEvidence = withoutField(gate, 'evidenceDigests')
    const missingFailures = withoutField(gate, 'failures')
    expect(isPromotionGate(missingEvidence)).toBe(false)
    expect(isPromotionGate(missingFailures)).toBe(false)
  })

  it('rejects incomplete targets and action events', () => {
    const missingUpdatedAt = withoutField(target, 'updatedAt')
    const missingOccurredAt = withoutField(historyEntry, 'occurredAt')
    expect(isReleaseTarget(missingUpdatedAt)).toBe(false)
    expect(isReleaseAction({ target, event: missingOccurredAt })).toBe(false)
  })
})
