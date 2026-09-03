import { afterEach, describe, expect, it, vi } from 'vitest'

import { apiOperation } from './openapi'
import type { ApiOperation, OpenApiMethod, OpenApiPath } from './openapi'
import { createTransport } from './transport'

describe('generated OpenAPI transport contracts', () => {
  afterEach(() => {
    document.cookie = 'amesh_csrf=; Max-Age=0; Path=/'
    vi.unstubAllGlobals()
  })

  it('derives the HTTP method, serializes JSON, and applies auth and CSRF headers', async () => {
    document.cookie = 'amesh_csrf=csrf%20token; Path=/'
    const fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const transport = createTransport({ token: 'secret', tenant: 'tenant-a', namespace: '' })

    await transport.request(apiOperation('/api/v1/auth/login', 'post'), {
      json: { identifier: 'operator', password: 'password', provider: 'local' },
    })

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    const headers = new Headers(init.headers)
    expect(url).toBe('/api/v1/auth/login')
    expect(init.method).toBe('POST')
    expect(init.body).toBe(JSON.stringify({ identifier: 'operator', password: 'password', provider: 'local' }))
    expect(headers.get('content-type')).toBe('application/json')
    expect(headers.get('authorization')).toBe('Bearer secret')
    expect(headers.get('x-amesh-tenant')).toBe('tenant-a')
    expect(headers.get('x-amesh-csrf')).toBe('csrf token')
  })

  it('decodes an explicitly declared blob response override', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('archive')))
    const transport = createTransport({ token: '', tenant: 'default', namespace: '' })

    const result = await transport.requestBlob(
      apiOperation('/api/v1/assets/export/openlineage', 'get'),
    )

    expect(await result.text()).toBe('archive')
  })

  it('decodes chronological NDJSON chunks including the final unterminated item', async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(encoder.encode('{"type":"heartbeat","sessionId":"s-1","cursor":"one"}\n{"type":"heartbeat","sessionId":"s-1","cursor"'))
        controller.enqueue(encoder.encode(':"two"}'))
        controller.close()
      },
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(stream)))
    const transport = createTransport({ token: '', tenant: 'default', namespace: '' })
    const items: unknown[] = []

    await transport.streamNdjson(
      apiOperation('/api/v1/agent-sessions/{service_session_id}/progress/stream', 'get', '/api/v1/agent-sessions/session-1/progress/stream'),
      (item) => items.push(item),
      new AbortController().signal,
    )

    expect(items).toEqual([
      { type: 'heartbeat', sessionId: 's-1', cursor: 'one' },
      { type: 'heartbeat', sessionId: 's-1', cursor: 'two' },
    ])
  })

  it('rejects runtime paths that do not match their canonical template', () => {
    expect(() => apiOperation('/health', 'get', '/ready')).toThrow(
      'Runtime API pathname "/ready" does not match canonical template "/health"',
    )
    expect(() => apiOperation('/api/v1/assets/export/openlineage', 'get', '/health')).toThrow(
      'does not match canonical template',
    )
    expect(() => apiOperation(
      '/api/v1/namespaces/{namespace}/files/{path}/move',
      'post',
      '/api/v1/namespaces/team%2Fdata/files/reports/2026/result.pdf/move?dryRun=false',
    )).not.toThrow()
    expect(() => apiOperation('/health', 'get', '/health?verbose=true')).not.toThrow()
  })

  it('rejects absolute, protocol-relative, and backslash cross-origin runtime URLs', () => {
    expect(() => apiOperation('/health', 'get', 'https://evil.example/health')).toThrow(
      'Runtime API URL must be same-origin and relative',
    )
    expect(() => apiOperation('/health', 'get', '//evil.example/health')).toThrow(
      'Runtime API URL must be same-origin and relative',
    )
    expect(() => apiOperation('/health', 'get', '/\\evil.example/health')).toThrow(
      'Runtime API URL must be same-origin and relative',
    )
    expect(() => apiOperation('/health', 'get', 'http://amesh.local/health')).toThrow(
      'Runtime API URL must be same-origin and relative',
    )
  })

  it('rejects invalid generated paths, methods, and JSON payloads at compile time', () => {
    const compileOnly = () => {
      // @ts-expect-error /health has no POST operation in the generated contract.
      apiOperation('/health', 'post')
      // @ts-expect-error arbitrary URLs cannot be used as canonical generated paths.
      apiOperation('/not-in-openapi', 'get')

      const narrowOperation = apiOperation('/health', 'get')
      type CatchAllOperation = ApiOperation<OpenApiPath, OpenApiMethod<OpenApiPath>>
      // @ts-expect-error the private invariant brand prevents widening a narrow operation.
      const widenedOperation: CatchAllOperation = narrowOperation
      void widenedOperation
      // @ts-expect-error the module-private brand prevents structural operation forgery.
      const forgedOperation: ApiOperation<'/health', 'get'> = { template: '/health', method: 'get', url: '/health' }
      void forgedOperation

      const transport = createTransport({ token: '', tenant: 'default', namespace: '' })
      // @ts-expect-error login JSON is derived from the generated request body.
      void transport.request(apiOperation('/api/v1/auth/login', 'post'), { json: { identifier: 'missing-fields' } })
      // @ts-expect-error generated-required JSON request bodies cannot omit request options.
      void transport.request(apiOperation('/api/v1/auth/login', 'post'))
      // @ts-expect-error authorized YAML operations require their raw request body.
      void transport.request(apiOperation('/api/v1/flows/validate', 'post'))
      // @ts-expect-error authorized file operations require their raw request body.
      void transport.request(apiOperation('/api/v1/namespaces/{namespace}/files/{path}', 'put'))
      // @ts-expect-error raw bodies are limited to the explicitly authorized YAML/file operations.
      void transport.request(apiOperation('/health', 'get'), { rawBody: 'not-authorized' })
      // @ts-expect-error blob transport is restricted to four generated GET operations.
      void transport.requestBlob(apiOperation('/health', 'get'))
      // @ts-expect-error blob transport does not accept caller-defined codecs.
      void transport.requestBlob(apiOperation('/api/v1/assets/export/openlineage', 'get'), { decode: () => Promise.resolve({}) })
      // @ts-expect-error NDJSON transport is restricted to two generated GET operations.
      void transport.streamNdjson(apiOperation('/health', 'get'), () => undefined, new AbortController().signal)
      // @ts-expect-error NDJSON item types are fixed by the generated path mapping.
      void transport.streamNdjson(apiOperation('/api/v1/executions/{execution_id}/evidence/stream', 'get'), (item: { invented: true }) => void item, new AbortController().signal)
    }

    expect(compileOnly).toBeTypeOf('function')
  })
})
