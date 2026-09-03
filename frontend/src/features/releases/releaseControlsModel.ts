import type {
  PromotionGate,
  PromotionTargetKind,
  ReleaseHistoryEntry,
  ReleaseTarget,
} from '../../api/types'

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isTargetKind(value: unknown): value is PromotionTargetKind {
  return value === 'WORKFLOW' || value === 'AGENT'
}

function isNullableNumber(value: unknown): value is number | null {
  return value === null || typeof value === 'number'
}

function isNullableString(value: unknown): value is string | null {
  return value === null || typeof value === 'string'
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

export function isReleaseTarget(value: unknown): value is ReleaseTarget {
  return isRecord(value)
    && typeof value.tenantId === 'string'
    && isTargetKind(value.targetKind)
    && typeof value.targetKey === 'string'
    && isNullableNumber(value.activeRevision)
    && isNullableString(value.activeConfigurationDigest)
    && (value.state === 'ACTIVE' || value.state === 'KILLED')
    && typeof value.version === 'number'
    && typeof value.updatedAt === 'string'
}

export function isReleaseHistoryEntry(value: unknown): value is ReleaseHistoryEntry {
  return isRecord(value)
    && typeof value.eventId === 'string'
    && typeof value.tenantId === 'string'
    && isTargetKind(value.targetKind)
    && typeof value.targetKey === 'string'
    && (value.action === 'PROMOTE' || value.action === 'ROLLBACK' || value.action === 'KILL_SWITCH')
    && isNullableNumber(value.fromRevision)
    && isNullableNumber(value.toRevision)
    && isNullableString(value.toConfigurationDigest)
    && isNullableString(value.gateDigest)
    && typeof value.actorId === 'string'
    && typeof value.reason === 'string'
    && typeof value.version === 'number'
    && typeof value.occurredAt === 'string'
}

export function isReleaseHistory(value: unknown): value is ReleaseHistoryEntry[] {
  return Array.isArray(value) && value.every(isReleaseHistoryEntry)
}

export function isPromotionGate(value: unknown): value is PromotionGate {
  return isRecord(value)
    && typeof value.gateId === 'string'
    && typeof value.tenantId === 'string'
    && typeof value.policyId === 'string'
    && typeof value.policyDigest === 'string'
    && isTargetKind(value.targetKind)
    && typeof value.targetKey === 'string'
    && typeof value.targetRevision === 'number'
    && typeof value.configurationDigest === 'string'
    && isStringArray(value.evidenceDigests)
    && typeof value.passed === 'boolean'
    && isStringArray(value.failures)
    && typeof value.evaluatedAt === 'string'
}

export function isReleaseAction(value: unknown): value is { target: ReleaseTarget; event: ReleaseHistoryEntry } {
  return isRecord(value) && isReleaseTarget(value.target) && isReleaseHistoryEntry(value.event)
}
