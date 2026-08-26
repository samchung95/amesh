import type { AgentCapabilityCatalogItem, AgentCapabilityKind, AgentCapabilityStatus } from '../api/types'

export const CAPABILITY_KINDS: AgentCapabilityKind[] = [
  'prompt', 'skill', 'model-policy', 'evaluation', 'agent', 'plugin', 'mcp-connection', 'mcp-tool',
]

export interface CapabilityCatalogFilters {
  query: string
  kind: AgentCapabilityKind | 'ALL'
  status: AgentCapabilityStatus | 'ALL'
}

function searchableText(item: AgentCapabilityCatalogItem): string {
  return [
    item.kind,
    item.key,
    item.catalogId,
    item.humanLabel,
    item.description,
    ...item.providerCompatibility,
    ...item.attachment.constraints,
  ].join(' ').toLocaleLowerCase()
}

export function filterCapabilityCatalog(items: AgentCapabilityCatalogItem[], filters: CapabilityCatalogFilters): AgentCapabilityCatalogItem[] {
  const query = filters.query.trim().toLocaleLowerCase()
  return items.filter((item) => {
    if (filters.kind !== 'ALL' && item.kind !== filters.kind) return false
    if (filters.status !== 'ALL' && item.status !== filters.status) return false
    return !query || searchableText(item).includes(query)
  })
}

export function capabilityStatusLabel(status: AgentCapabilityStatus): string {
  return status.replace('-', ' ')
}

export function capabilityRevisionLabel(item: AgentCapabilityCatalogItem): string {
  return typeof item.revision === 'number' ? `r${String(item.revision)}` : String(item.revision)
}

export function capabilityCanAttach(item: AgentCapabilityCatalogItem): boolean {
  return item.status === 'available' && item.attachment.target !== 'none' && item.attachment.reference !== null
}

export function capabilityExactRef(item: AgentCapabilityCatalogItem): string {
  const reference = item.attachment.reference
  if (reference?.kind === 'mcp-tool' && reference.connectionKey && reference.connectionRevision && reference.toolName) {
    return `${reference.connectionKey}@${String(reference.connectionRevision)}:${reference.toolName}`
  }
  if (reference) return `${reference.key}@${String(reference.revision)}`
  return `${item.key}@${String(item.revision)}`
}
