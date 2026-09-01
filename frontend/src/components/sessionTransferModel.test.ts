import { describe, expect, it } from 'vitest'

import { parseTransferBundle, stableCredentialRefs } from './sessionTransferModel'

describe('session transfer model', () => {
  it('accepts only supported profile and session bundle envelopes', () => {
    expect(parseTransferBundle({ schemaVersion: 'amesh.profile/v1', sourceTenantId: 'source', namespace: 'platform', agentKey: 'researcher' }).kind).toBe('profile')
    expect(parseTransferBundle({ schemaVersion: 'amesh.session-transfer/v1', sourceTenantId: 'source', mode: 'CLEAN_CHECKPOINT', session: {} }).kind).toBe('session')
    expect(() => parseTransferBundle({ schemaVersion: 'other/v1' })).toThrow('AMESH profile or session')
  })

  it('extracts only stable credential references from a bundle', () => {
    const { bundle } = parseTransferBundle({ schemaVersion: 'amesh.profile/v1', sourceTenantId: 'source', namespace: 'platform', agentKey: 'researcher', resources: [{ spec: { routes: [{ provider: { credentialRef: 'provider-main' } }], permissions: { secretScopes: ['provider-main', 'mcp-catalog'] } } }] })
    expect(stableCredentialRefs(bundle)).toEqual(['mcp-catalog', 'provider-main'])
  })
})
