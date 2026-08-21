import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, createApiClient } from './client'

describe('API client', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('sends bearer and tenant context on UI session requests', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ display: 'operator' }), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'secret-token', tenant: 'tenant-a', namespace: 'team.data' })

    await api.session()

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    const headers = new Headers(init.headers)
    expect(url).toBe('/api/v1/ui/session?namespace=team.data')
    expect(headers.get('authorization')).toBe('Bearer secret-token')
    expect(headers.get('x-amesh-tenant')).toBe('tenant-a')
    expect(headers.get('accept')).toBe('application/json')
  })

  it('surfaces the server detail and status for recoverable errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'tenant unavailable' }), { status: 404 })))
    const api = createApiClient({ token: 'bad', tenant: 'private', namespace: '' })

    await expect(api.flows()).rejects.toEqual(new ApiError(404, 'tenant unavailable'))
  })

  it('falls back to status text when an upstream error is not JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('offline', { status: 503, statusText: 'Unavailable' })))
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await expect(api.executions()).rejects.toMatchObject({ status: 503, message: 'Unavailable' })
  })

  it('uses stable health, session and encoded execution paths', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.health()
    await api.session()
    await api.flowGraph('team/data', 'daily flow')
    await api.execution('run/one')
    await api.executionGraph('run/one')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/health',
      '/api/v1/ui/session',
      '/api/v1/flows/team%2Fdata/daily%20flow/graph',
      '/api/v1/executions/run%2Fone',
      '/api/v1/executions/run%2Fone/graph',
    ])
  })

  it('uses a deterministic fallback when JSON detail is not text', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 42 }), { status: 500 })))
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await expect(api.flows()).rejects.toMatchObject({ message: 'Request failed with status 500' })
  })
})
