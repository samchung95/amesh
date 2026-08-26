import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { AgentCapabilityCatalogItem } from '../api/types'
import { CapabilityCatalog } from './CapabilityCatalog'

const item: AgentCapabilityCatalogItem = {
  kind: 'mcp-tool', catalogId: 'mcp-tool:catalog:2:lookup', key: 'lookup', humanLabel: 'Lookup', description: 'Read customer data', revision: 2,
  digest: `sha256:${'a'.repeat(64)}`, status: 'available', schemas: { inputSchema: { type: 'object' }, outputSchema: { type: 'object' } }, impact: 'READ_ONLY',
  permissions: { delegatedCapabilities: [], toolAllowlist: ['lookup'], secretScopes: ['mcp-token'], networkHosts: ['mcp.example.test'], allowedEgress: [], filesystemReadRoots: [], filesystemWriteRoots: [], allowHighImpact: false }, providerCompatibility: ['amesh.agent/v1'], attachment: { target: 'agent-definition', reference: { kind: 'mcp-tool', key: 'lookup', revision: 2, digest: `sha256:${'a'.repeat(64)}`, connectionKey: 'catalog', connectionRevision: 2, toolName: 'lookup' }, constraints: [] }, diagnostics: [],
}

describe('CapabilityCatalog', () => {
  it('filters, details and attaches the exact canonical reference', () => {
    const onAttach = vi.fn()
    render(<CapabilityCatalog items={[item]} onAttach={onAttach} />)
    expect(screen.getAllByText('Lookup')).toHaveLength(2)
    fireEvent.change(screen.getByLabelText('Search capabilities'), { target: { value: 'missing' } })
    expect(screen.getByText('No capabilities match these filters.')).toBeVisible()
    fireEvent.change(screen.getByLabelText('Search capabilities'), { target: { value: 'customer' } })
    fireEvent.click(screen.getByRole('button', { name: /Attach exact reference/i }))
    expect(onAttach).toHaveBeenCalledWith(item)
    expect(screen.getByText('catalog@2:lookup')).toBeVisible()
    expect(screen.getByText(/mcp-token/)).toBeVisible()
  })

  it('explains denied and unavailable source states when the catalog is empty', () => {
    render(<CapabilityCatalog items={[]} sourceAccess={[{ source: 'agents', status: 'denied', diagnostics: ['Ask a namespace administrator for view access.'] }, { source: 'plugins', status: 'unavailable', diagnostics: ['Registry unavailable; retry later.'] }]} onAttach={vi.fn()} />)
    expect(screen.getByText(/Ask a namespace administrator/)).toBeVisible()
    expect(screen.getByText(/Registry unavailable/)).toBeVisible()
    expect(screen.getByText('No visible capabilities')).toBeVisible()
  })
})
