import type { AgentSessionFleetItem, AgentSessionFleetQuery } from '../../api/types'

export const MAX_BULK_SELECTION = 25

export type FleetStatusTone = 'running' | 'success' | 'failed' | 'warning' | 'waiting' | 'unknown'

export function fleetStatusTone(state: string): FleetStatusTone {
  if (['RUNNING'].includes(state)) return 'running'
  if (['SUCCEEDED'].includes(state)) return 'success'
  if (['FAILED', 'CANCELLED'].includes(state)) return 'failed'
  if (['WARNING'].includes(state)) return 'warning'
  if (['CREATED', 'QUEUED', 'PAUSED', 'CANCELLING', 'RESTARTING'].includes(state)) return 'waiting'
  return 'unknown'
}

export function fleetStatusLabel(state: string): string {
  return state.replaceAll('_', ' ')
}

export function dependencyTone(health: string): FleetStatusTone {
  return health === 'HEALTHY' ? 'success' : health === 'DEGRADED' || health === 'FAILED' ? 'failed' : 'warning'
}

export function dependencyLabel(item: Pick<AgentSessionFleetItem, 'dependencyHealth' | 'dependencyKeys'>): string {
  if (!item.dependencyKeys.length) return 'No dependencies'
  return `${item.dependencyHealth} · ${item.dependencyKeys.length} pinned`
}

export function formatFleetCost(value: string | number | undefined): string {
  const amount = Number(value)
  if (!Number.isFinite(amount)) return '$—'
  return `$${amount.toFixed(amount > 0 && amount < 0.01 ? 4 : 2)}`
}

export function compactId(value: string | null | undefined): string {
  if (!value) return '—'
  return value.length > 16 ? `${value.slice(0, 8)}…${value.slice(-6)}` : value
}

export function buildFleetQuery(filters: AgentSessionFleetQuery, cursor?: string): AgentSessionFleetQuery {
  return {
    limit: filters.limit || 50,
    ...(cursor ? { cursor } : {}),
    ...(filters.state ? { state: filters.state } : {}),
    ...(filters.namespace?.trim() ? { namespace: filters.namespace.trim() } : {}),
    ...(filters.agentRef?.trim() ? { agentRef: filters.agentRef.trim() } : {}),
    ...(filters.ownerId?.trim() ? { ownerId: filters.ownerId.trim() } : {}),
    ...(filters.harness?.trim() ? { harness: filters.harness.trim() } : {}),
    ...(filters.createdFrom ? { createdFrom: filters.createdFrom } : {}),
    ...(filters.createdTo ? { createdTo: filters.createdTo } : {}),
  }
}

export function lifecycleActions(state: string): Array<'cancel' | 'pause' | 'resume' | 'retry'> {
  if (['CREATED', 'QUEUED', 'RUNNING', 'RESTARTING'].includes(state)) return ['pause', 'cancel']
  if (state === 'PAUSED') return ['resume', 'cancel']
  if (['FAILED', 'CANCELLED', 'WARNING'].includes(state)) return ['retry']
  return []
}

export function toggleFleetSelection(selected: string[], id: string): { next: string[]; limited: boolean } {
  if (selected.includes(id)) return { next: selected.filter((value) => value !== id), limited: false }
  if (selected.length >= MAX_BULK_SELECTION) return { next: selected, limited: true }
  return { next: [...selected, id], limited: false }
}

export function selectVisibleFleetRows(ids: string[], allSelected: boolean): { next: string[]; limited: boolean } {
  if (allSelected) return { next: [], limited: false }
  return { next: ids.slice(0, MAX_BULK_SELECTION), limited: ids.length > MAX_BULK_SELECTION }
}
