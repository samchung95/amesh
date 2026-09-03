import type {
  ApiJsonResponse,
  ApiNdjsonItem,
  ApiOperation,
  ApiRequestArguments,
  BlobApiOperation,
  BlobOpenApiPath,
  NdjsonApiOperation,
  NdjsonOpenApiPath,
  OpenApiMethod,
  OpenApiPath,
} from './openapi'

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
  request<Path extends OpenApiPath, Method extends OpenApiMethod<Path>>(
    operation: ApiOperation<Path, Method>,
    ...args: ApiRequestArguments<Path, Method>
  ): Promise<ApiJsonResponse<Path, Method>>
  requestBlob<Path extends BlobOpenApiPath>(
    operation: BlobApiOperation<Path>,
  ): Promise<Blob>
  streamNdjson<Path extends NdjsonOpenApiPath>(
    operation: NdjsonApiOperation<Path>,
    onItem: (item: ApiNdjsonItem<Path>) => void,
    signal: AbortSignal,
  ): Promise<void>
}

function decodeNdjsonItem<Path extends NdjsonOpenApiPath>(
  operation: NdjsonApiOperation<Path>,
  line: string,
): ApiNdjsonItem<Path> {
  void operation
  return JSON.parse(line) as ApiNdjsonItem<Path>
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

function decodeGeneratedJson<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
>(
  response: Response,
  operation: ApiOperation<Path, Method>,
): Promise<ApiJsonResponse<Path, Method>> {
  void operation
  return response.json() as Promise<ApiJsonResponse<Path, Method>>
}

function decodeGeneratedNoContent<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
>(operation: ApiOperation<Path, Method>): ApiJsonResponse<Path, Method> {
  void operation
  return undefined as ApiJsonResponse<Path, Method>
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
    async request(operation, ...args) {
      const options = args[0]
      const { json, rawBody, ...init } = (options ?? {}) as RequestInit & {
        json?: unknown
        rawBody?: BodyInit | null
      }
      const headers = new Headers(init.headers)
      if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
      headers.set('X-Amesh-Tenant', connection.tenant)
      headers.set('Accept', 'application/json')
      const method = operation.method.toUpperCase()
      if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
        const csrf = csrfToken()
        if (csrf) headers.set('X-Amesh-CSRF', csrf)
      }
      let body = rawBody
      if (json !== undefined) {
        if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
        body = JSON.stringify(json)
      }
      const response = await fetch(operation.url, {
        ...init,
        body,
        credentials: 'same-origin',
        headers,
        method,
      })
      if (!response.ok) throw new ApiError(response.status, await readError(response))
      if (response.status === 204) return decodeGeneratedNoContent(operation)
      return decodeGeneratedJson(response, operation)
    },
    async requestBlob(operation) {
      const headers = new Headers()
      if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
      headers.set('X-Amesh-Tenant', connection.tenant)
      const response = await fetch(operation.url, {
        credentials: 'same-origin',
        headers,
        method: operation.method.toUpperCase(),
      })
      if (!response.ok) throw new ApiError(response.status, await readError(response))
      return response.blob()
    },
    async streamNdjson(
      operation,
      onItem,
      signal: AbortSignal,
    ): Promise<void> {
      const headers = new Headers({ Accept: 'application/x-ndjson' })
      if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
      headers.set('X-Amesh-Tenant', connection.tenant)
      const response = await fetch(operation.url, {
        credentials: 'same-origin',
        headers,
        method: operation.method.toUpperCase(),
        signal,
      })
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
        lines.filter(Boolean).forEach((line) => onItem(decodeNdjsonItem(operation, line)))
        if (done) break
      }
      if (pending.trim()) onItem(decodeNdjsonItem(operation, pending))
    },
  }
  return transport
}
