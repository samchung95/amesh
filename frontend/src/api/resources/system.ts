import type {
  AuthenticationProvider,
  HealthResponse,
  LoginResponse,
  ReadinessResponse,
  UiSession,
} from '../types'
import type { ApiTransport } from '../transport'

export function createSystemResource(transport: ApiTransport) {
  return {
    health: async () => transport.request<HealthResponse>('/health'),
    readiness: async () => transport.request<ReadinessResponse>('/ready'),
    providers: async () => transport.request<AuthenticationProvider[]>('/api/v1/auth/providers'),
    routedProviders: async (identifier?: string, tenant?: string) => {
      const params = new URLSearchParams()
      if (identifier) params.set('identifier', identifier)
      if (tenant) params.set('tenant', tenant)
      const suffix = params.size ? `?${params.toString()}` : ''
      return transport.request<AuthenticationProvider[]>(`/api/v1/auth/providers${suffix}`)
    },
    login: async (identifier: string, password: string, provider = 'local') =>
      transport.request<LoginResponse>('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, identifier, password }),
      }),
    logout: async () => transport.request<void>('/api/v1/auth/logout', { method: 'POST' }),
    session: async () => {
      const params = new URLSearchParams()
      if (transport.connection.namespace) params.set('namespace', transport.connection.namespace)
      const suffix = params.size ? `?${params.toString()}` : ''
      return transport.request<UiSession>(`/api/v1/ui/session${suffix}`)
    },
  }
}
