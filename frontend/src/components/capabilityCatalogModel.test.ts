import { describe, expect, it } from 'vitest'

import type { AgentCapabilityCatalogItem } from '../api/types'
import { capabilityCanAttach, capabilityRevisionLabel, filterCapabilityCatalog } from './capabilityCatalogModel'

const item = (overrides: Partial<AgentCapabilityCatalogItem>): AgentCapabilityCatalogItem => ({
  kind: 'mcp-tool', catalogId: 'mcp-tool:catalog:2:lookup', key: 'lookup', humanLabel: 'Lookup', description: 'Read a customer record',
  revision: 2, digest: `sha256:${'a'.repeat(64)}`, status: 'available', schemas: { inputSchema: { type: 'object' }, outputSchema: null }, impact: 'READ_ONLY',
  permissions: { delegatedCapabilities: [], toolAllowlist: ['lookup'], secretScopes: ['mcp-token'], networkHosts: ['mcp.example.test'], allowedEgress: [], filesystemReadRoots: [], filesystemWriteRoots: [], allowHighImpact: false }, providerCompatibility: ['amesh.agent/v1'], attachment: { target: 'agent-definition', reference: { kind: 'mcp-tool', key: 'lookup', revision: 2, digest: `sha256:${'a'.repeat(64)}`, connectionKey: 'catalog', connectionRevision: 2, toolName: 'lookup' }, constraints: [] }, diagnostics: [], ...overrides,
})

describe('capability catalog model', () => {
  it('filters by exact kind, status and searchable evidence', () => {
    const items = [item({}), item({ kind: 'plugin', key: 'acme.reviewed', catalogId: 'plugin:acme.reviewed:1.4.0', humanLabel: 'Reviewed plugin', revision: '1.4.0', attachment: { target: 'none', reference: { kind: 'plugin', key: 'acme.reviewed', revision: '1.4.0', digest: `sha256:${'b'.repeat(64)}` }, constraints: ['managed'] } })]
    expect(filterCapabilityCatalog(items, { query: 'customer', kind: 'mcp-tool', status: 'available' })).toHaveLength(1)
    expect(filterCapabilityCatalog(items, { query: '', kind: 'plugin', status: 'ALL' })[0]?.catalogId).toBe('plugin:acme.reviewed:1.4.0')
  })

  it('does not offer denied, drifted or unattached capabilities for attachment', () => {
    expect(capabilityCanAttach(item({ status: 'denied' }))).toBe(false)
    expect(capabilityCanAttach(item({ attachment: { target: 'none', reference: item({}).attachment.reference, constraints: ['Use a plugin task entry point'] } }))).toBe(false)
    expect(capabilityCanAttach(item({ attachment: { target: 'agent-definition', reference: item({}).attachment.reference, constraints: ['Requires approval at execution'] } }))).toBe(true)
    expect(capabilityCanAttach(item({}))).toBe(true)
  })

  it('labels numeric revisions and plugin versions without inventing a revision', () => {
    expect(capabilityRevisionLabel(item({}))).toBe('r2')
    expect(capabilityRevisionLabel(item({ revision: '1.4.0' }))).toBe('1.4.0')
  })
})
