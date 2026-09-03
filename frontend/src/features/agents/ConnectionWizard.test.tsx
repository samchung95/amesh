import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ConnectionWizard } from './ConnectionWizard'

const tool = { name: 'lookup', description: 'Read customer data', inputSchema: { type: 'object' }, outputSchema: { type: 'object' }, impact: 'READ_ONLY' as const }

describe('ConnectionWizard', () => {
  it('discovers, saves and tests an exact revision without exposing secret values', async () => {
    const discover = vi.fn().mockResolvedValue({ serverName: 'Catalog', serverVersion: '1.0.0', tools: [tool], digest: `sha256:${'a'.repeat(64)}` })
    const create = vi.fn().mockResolvedValue({ connectionId: 'connection-1', tenantId: 'default', revision: 3, digest: `sha256:${'b'.repeat(64)}`, spec: { key: 'catalog', namespace: 'agents.demo', endpoint: 'https://mcp.example.test/mcp', credentialRef: 'mcp-token', toolAllowlist: ['lookup'], tools: [tool] }, createdBy: 'operator', createdAt: '2026-08-26T00:00:00Z' })
    const test = vi.fn().mockResolvedValue({ status: 'PASSED', evidenceId: 'evidence-1', connectionPin: { key: 'catalog', revision: 3, digest: `sha256:${'b'.repeat(64)}` }, observedDigest: `sha256:${'a'.repeat(64)}`, checkedToolCount: 1, diagnostic: null, redacted: true, effectBoundary: 'DISCOVERY_ONLY' as const })
    const onSaved = vi.fn()
    render(<ConnectionWizard namespace="agents.demo" secrets={[{ namespace: 'agents.demo', key: 'mcp-token', provider: 'env', providerReference: 'AMESH_TEST_MCP_TOKEN', metadata: {}, resourceVersion: 1, inherited: false, originNamespace: 'agents.demo', createdAt: '2026-08-26T00:00:00Z', updatedAt: '2026-08-26T00:00:00Z' }]} discover={discover} create={create} test={test} onSaved={onSaved} />)

    fireEvent.input(screen.getByLabelText('Connection key'), { target: { value: 'catalog' } })
    fireEvent.input(screen.getByLabelText('Endpoint'), { target: { value: 'https://mcp.example.test/mcp' } })
    fireEvent.change(screen.getByLabelText('Secret binding'), { target: { value: 'mcp-token' } })
    fireEvent.click(screen.getByRole('button', { name: 'Discover schemas' }))
    await screen.findByText('Catalog 1.0.0')
    fireEvent.click(screen.getByRole('button', { name: 'Save and test exact revision' }))

    await waitFor(() => expect(test).toHaveBeenCalledWith('agents.demo', 'catalog', 3, 30))
    expect(create).toHaveBeenCalledWith('agents.demo', expect.objectContaining({ credentialRef: 'mcp-token', toolAllowlist: ['lookup'] }))
    expect(onSaved).toHaveBeenCalled()
    expect(screen.queryByText('AMESH_TEST_MCP_TOKEN')).not.toBeInTheDocument()
  })
})
