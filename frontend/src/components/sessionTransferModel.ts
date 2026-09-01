import type { AgentSessionProfileTransferBundle, AgentSessionTransferBundle } from '../api/types'

export type TransferBundle = AgentSessionProfileTransferBundle | AgentSessionTransferBundle
export type TransferKind = 'profile' | 'session'

export function parseTransferBundle(value: unknown): { kind: TransferKind; bundle: TransferBundle } {
  if (!isRecord(value) || typeof value.schemaVersion !== 'string') {
    throw new Error('The selected file is not a JSON transfer bundle.')
  }
  if (value.schemaVersion === 'amesh.profile/v1' && typeof value.sourceTenantId === 'string' && typeof value.namespace === 'string' && typeof value.agentKey === 'string') {
    return { kind: 'profile', bundle: value as unknown as AgentSessionProfileTransferBundle }
  }
  if (value.schemaVersion === 'amesh.session-transfer/v1' && typeof value.sourceTenantId === 'string' && typeof value.mode === 'string' && isRecord(value.session)) {
    return { kind: 'session', bundle: value as unknown as AgentSessionTransferBundle }
  }
  throw new Error('Choose an AMESH profile or session transfer JSON bundle.')
}

export function stableCredentialRefs(bundle: TransferBundle): string[] {
  const refs = new Set<string>()
  const visit = (value: unknown, key = '') => {
    if (typeof value === 'string' && key === 'credentialRef') refs.add(value)
    if (Array.isArray(value)) {
      value.forEach((item) => visit(item, key))
      return
    }
    if (!isRecord(value)) return
    Object.entries(value).forEach(([childKey, childValue]) => {
      if ((childKey === 'secretScopes' || childKey === 'secret_scopes' || childKey === 'credentialRefs' || childKey === 'credential_refs') && Array.isArray(childValue)) {
        childValue.filter((item): item is string => typeof item === 'string').forEach((item) => refs.add(item))
      }
      visit(childValue, childKey)
    })
  }
  visit(bundle)
  return Array.from(refs).sort()
}

export function transferDigest(bundle: TransferBundle): string {
  return bundle.checksumSha256
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}
