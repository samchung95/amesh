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

export interface ApiTransport {
  readonly connection: ApiConnection
  request<T>(path: string, init?: RequestInit): Promise<T>
  requestBlob(path: string): Promise<Blob>
  streamNdjson<T>(path: string, onItem: (item: T) => void, signal: AbortSignal): Promise<void>
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

export function namespaceRoot(namespace: string): string {
  return `/api/v1/namespaces/${encodeURIComponent(namespace)}`
}

export function filePath(namespace: string, path: string): string {
  return `${namespaceRoot(namespace)}/files/${path.split('/').map(encodeURIComponent).join('/')}`
}

export function imagePath(namespace: string, path: string): string {
  return `${namespaceRoot(namespace)}/images/${path.split('/').map(encodeURIComponent).join('/')}`
}

export function createTransport(connection: ApiConnection): ApiTransport {
  const transport: ApiTransport = {
    connection,
    async request<T>(path: string, init?: RequestInit): Promise<T> {
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
    },
    async requestBlob(path: string): Promise<Blob> {
      const headers = new Headers()
      if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
      headers.set('X-Amesh-Tenant', connection.tenant)
      const response = await fetch(path, { credentials: 'same-origin', headers })
      if (!response.ok) throw new ApiError(response.status, await readError(response))
      return response.blob()
    },
    async streamNdjson<T>(
      path: string,
      onItem: (item: T) => void,
      signal: AbortSignal,
    ): Promise<void> {
      const headers = new Headers({ Accept: 'application/x-ndjson' })
      if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
      headers.set('X-Amesh-Tenant', connection.tenant)
      const response = await fetch(path, { credentials: 'same-origin', headers, signal })
      if (!response.ok) throw new ApiError(response.status, await readError(response))
      if (!response.body) throw new ApiError(502, 'Streaming response body is unavailable')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let pending = ''
      while (true) {
        const { done, value } = await reader.read()
        pending += decoder.decode(value, { stream: !done })
        const lines = pending.split('\n')
        pending = lines.pop() || ''
        lines.filter(Boolean).forEach((line) => onItem(JSON.parse(line) as T))
        if (done) break
      }
      if (pending.trim()) onItem(JSON.parse(pending) as T)
    },
  }
  return transport
}
