import type {
  ExecutionDetail,
  FlowGraph,
  HealthResponse,
  PersistedExecution,
  PersistedFlow,
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

export function createApiClient(connection: ApiConnection) {
  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const headers = new Headers(init?.headers)
    headers.set('Authorization', `Bearer ${connection.token}`)
    headers.set('X-Amesh-Tenant', connection.tenant)
    headers.set('Accept', 'application/json')
    const response = await fetch(path, { ...init, headers })
    if (!response.ok) throw new ApiError(response.status, await readError(response))
    return (await response.json()) as T
  }

  return {
    health: async () => request<HealthResponse>('/health'),
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
    execution: async (executionId: string) =>
      request<ExecutionDetail>(`/api/v1/executions/${encodeURIComponent(executionId)}`),
    executionGraph: async (executionId: string) =>
      request<FlowGraph>(`/api/v1/executions/${encodeURIComponent(executionId)}/graph`),
  }
}
