import { describe, expect, it } from 'vitest'

import { createApiClient } from './client'

describe('resource client compatibility facade', () => {
  it('preserves every flat method while composing bounded resources', () => {
    const client = createApiClient({ token: 'token', tenant: 'tenant', namespace: 'namespace' })
    const methods = Object.entries(client)

    expect(methods).toHaveLength(192)
    expect(methods.every(([, value]) => typeof value === 'function')).toBe(true)
    expect(Object.keys(client)).toEqual(expect.arrayContaining([
      'health',
      'login',
      'apps',
      'assets',
      'administrationControls',
      'blueprints',
      'flows',
      'pluginRegistry',
      'dashboards',
      'triggers',
      'lifecyclePolicies',
      'namespaceFiles',
      'agentResources',
      'agentSessions',
      'executions',
      'previewBackfill',
      'previewRelease',
    ]))
  })
})
