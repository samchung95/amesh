import { apiOperation } from '../openapi'
import type { ApiTransport } from '../transport'

export function createSystemResource(transport: ApiTransport) {
  return {
    health: async () => transport.request(apiOperation('/health', 'get', '/health')),
    readiness: async () => transport.request(apiOperation('/ready', 'get', '/ready')),
    providers: async () => transport.request(apiOperation('/api/v1/auth/providers', 'get', '/api/v1/auth/providers')),
    routedProviders: async (identifier?: string, tenant?: string) => {
      return transport.request(apiOperation('/api/v1/auth/providers', 'get', `/api/v1/auth/providers`, { identifier: identifier || undefined, tenant: tenant || undefined }))
    },
    login: async (identifier: string, password: string, provider = 'local') =>
      transport.request(apiOperation('/api/v1/auth/login', 'post', '/api/v1/auth/login'), {
        headers: { 'Content-Type': 'application/json' },
        json: { provider, identifier, password },
      }),
    logout: async () => transport.request(apiOperation('/api/v1/auth/logout', 'post', '/api/v1/auth/logout'), { }),
    session: async () => {
      return transport.request(apiOperation('/api/v1/ui/session', 'get', `/api/v1/ui/session`, { namespace: transport.connection.namespace || undefined }))
    },
  }
}
