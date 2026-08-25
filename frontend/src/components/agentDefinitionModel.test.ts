import { describe, expect, it } from 'vitest'

import type { AgentResourceRevision } from '../api/types'
import {
  buildAgentResourceSpec,
  initialAgentBuilderDraft,
} from './agentDefinitionModel'

const policy: AgentResourceRevision = {
  resourceId: 'policy-1', tenantId: 'default', namespace: 'agents.demo', kind: 'MODEL_POLICY', key: 'luna', revision: 2,
  digest: `sha256:${'a'.repeat(64)}`, createdBy: 'author', createdAt: '2026-08-25T00:00:00Z',
  spec: {
    kind: 'MODEL_POLICY', key: 'luna', namespace: 'agents.demo', title: 'Luna', fallbackMode: 'DISABLED',
    outputNondeterminismDisclosure: 'Outputs vary.',
    routes: [{ routeId: 'primary', provider: { adapter: 'openai-compatible', endpoint: 'https://openrouter.ai/api/v1', embeddingEndpoint: null, credentialRef: 'openrouter-key' }, model: 'openai/gpt-5.6-luna', requiredFeatures: [], parameters: {} }],
  },
}

describe('agent definition model', () => {
  it('derives the effective secret and network boundary from exact catalogs', () => {
    const spec = buildAgentResourceSpec('agents.demo', {
      ...initialAgentBuilderDraft,
      key: 'researcher', title: 'Researcher', instructions: 'Return JSON.', modelPolicyRef: 'luna@2',
      toolRef: 'catalog@3:search',
    }, [policy], [{
      connectionKey: 'catalog', connectionRevision: 3, connectionDigest: `sha256:${'b'.repeat(64)}`,
      credentialRef: 'mcp-key', endpoint: 'https://mcp.example.test/mcp', toolName: 'search',
      description: 'Search', schemaDigest: `sha256:${'c'.repeat(64)}`, impact: 'READ_ONLY',
    }])

    expect(spec.kind).toBe('AGENT')
    if (spec.kind !== 'AGENT') throw new Error('expected agent')
    expect(spec.modelPolicy).toEqual({ key: 'luna', revision: 2 })
    expect(spec.permissions.secretScopes).toEqual(['openrouter-key', 'mcp-key'])
    expect(spec.permissions.networkHosts).toEqual(['openrouter.ai', 'mcp.example.test'])
    expect(spec.tools[0]?.schemaDigest).toBe(`sha256:${'c'.repeat(64)}`)
  })

  it('uses Luna as the default OpenRouter model policy', () => {
    const spec = buildAgentResourceSpec('agents.demo', {
      ...initialAgentBuilderDraft,
      kind: 'MODEL_POLICY', key: 'luna', title: 'Luna',
    }, [], [])
    expect(spec.kind).toBe('MODEL_POLICY')
    if (spec.kind !== 'MODEL_POLICY') throw new Error('expected policy')
    expect(spec.routes[0]?.model).toBe('openai/gpt-5.6-luna')
    expect(spec.fallbackMode).toBe('DISABLED')
  })
})
