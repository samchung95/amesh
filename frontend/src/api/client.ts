import type {
  CheckComplianceSummary,
  CheckEvaluation,
  ExecutionDetail,
  ExecutionEvidencePage,
  AuthenticationProvider,
  FlowGraph,
  HealthResponse,
  LoginResponse,
  NamespaceCheckPolicy,
  PersistedExecution,
  PersistedFlow,
  TriggerOccurrence,
  TriggerRuntimeState,
  UiSession,
} from './types'

export interface ApiConnection {
  token: string
  tenant: string
  namespace: string
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown }
    if (typeof payload.detail === 'string') return payload.detail
  } catch {
    // The status text remains the deterministic fallback for non-JSON proxy failures.
  }
  return response.statusText || `Request failed with status ${String(response.status)}`
}

function csrfToken(): string | null {
  const cookie = document.cookie
    .split(';')
    .map((value) => value.trim())
    .find((value) => value.startsWith('amesh_csrf=') || value.startsWith('__Host-amesh_csrf='))
  return cookie ? decodeURIComponent(cookie.slice(cookie.indexOf('=') + 1)) : null
}

export function createApiClient(connection: ApiConnection) {
  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const headers = new Headers(init?.headers)
    if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
    headers.set('X-Amesh-Tenant', connection.tenant)
    headers.set('Accept', 'application/json')
    const method = (init?.method || 'GET').toUpperCase()
    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
      const csrf = csrfToken()
      if (csrf) headers.set('X-Amesh-CSRF', csrf)
    }
    const response = await fetch(path, { ...init, credentials: 'same-origin', headers })
    if (!response.ok) throw new ApiError(response.status, await readError(response))
    if (response.status === 204) return undefined as T
    return (await response.json()) as T
  }

  return {
    health: async () => request<HealthResponse>('/health'),
    providers: async () => request<AuthenticationProvider[]>('/api/v1/auth/providers'),
    login: async (identifier: string, password: string, provider = 'local') =>
      request<LoginResponse>('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, identifier, password }),
      }),
    logout: async () => request<void>('/api/v1/auth/logout', { method: 'POST' }),
    session: async () => {
      const params = new URLSearchParams()
      if (connection.namespace) params.set('namespace', connection.namespace)
      const suffix = params.size ? `?${params.toString()}` : ''
      return request<UiSession>(`/api/v1/ui/session${suffix}`)
    },
    flows: async () => request<PersistedFlow[]>('/api/v1/flows'),
    flowGraph: async (namespace: string, flowId: string) =>
      request<FlowGraph>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/graph`),
    executions: async () => request<PersistedExecution[]>('/api/v1/executions?limit=200'),
    triggers: async (namespace?: string) => {
      const suffix = namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''
      return request<TriggerRuntimeState[]>(`/api/v1/triggers${suffix}`)
    },
    triggerOccurrences: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return request<TriggerOccurrence[]>(`/api/v1/trigger-occurrences?${params.toString()}`)
    },
    checkPolicies: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return request<NamespaceCheckPolicy[]>(`/api/v1/check-policies?${params.toString()}`)
    },
    checkEvaluations: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return request<CheckEvaluation[]>(`/api/v1/check-evaluations?${params.toString()}`)
    },
    checkCompliance: async (namespace?: string) => {
      const params = new URLSearchParams({ groupBy: 'flow', limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return request<CheckComplianceSummary[]>(`/api/v1/check-compliance?${params.toString()}`)
    },
    setTriggerPaused: async (namespace: string, flowId: string, triggerId: string, paused: boolean, reason: string) =>
      request<TriggerRuntimeState>(`/api/v1/triggers/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/${encodeURIComponent(triggerId)}/${paused ? 'pause' : 'resume'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }),
    replayTriggerOccurrence: async (occurrenceId: string, reason: string) =>
      request<TriggerOccurrence>(`/api/v1/trigger-occurrences/${encodeURIComponent(occurrenceId)}/replay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }),
    execution: async (executionId: string) =>
      request<ExecutionDetail>(`/api/v1/executions/${encodeURIComponent(executionId)}`),
    executionGraph: async (executionId: string) =>
      request<FlowGraph>(`/api/v1/executions/${encodeURIComponent(executionId)}/graph`),
    executionEvidence: async (executionId: string, cursor?: string) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      return request<ExecutionEvidencePage>(`/api/v1/executions/${encodeURIComponent(executionId)}/evidence${suffix}`)
    },
  }
}
