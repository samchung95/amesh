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
    await api.flowMetadata('team/data', 'daily flow')
    await api.flowDataContract('team/data', 'daily flow')
    await api.executeFlow('team/data', 'daily flow', { message: 'hello' })
    await api.execution('run/one')
    await api.executionGraph('run/one')
    await api.executionEvidence('run/one', 'cursor/value')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/health',
      '/api/v1/ui/session',
      '/api/v1/flows/team%2Fdata/daily%20flow/graph',
      '/api/v1/flows/team%2Fdata/daily%20flow/metadata',
      '/api/v1/flows/team%2Fdata/daily%20flow/data-contract',
      '/api/v1/executions',
      '/api/v1/executions/run%2Fone',
      '/api/v1/executions/run%2Fone/graph',
      '/api/v1/executions/run%2Fone/evidence?cursor=cursor%2Fvalue',
    ])
    const executeInit = fetchMock.mock.calls[5]?.[1] as RequestInit
    expect(executeInit.method).toBe('POST')
    expect(JSON.parse(executeInit.body as string)).toEqual({
      namespace: 'team/data',
      flowId: 'daily flow',
      inputs: { message: 'hello' },
      runner: 'local',
    })
  })

  it('uses a deterministic fallback when JSON detail is not text', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 42 }), { status: 500 })))
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await expect(api.flows()).rejects.toMatchObject({ message: 'Request failed with status 500' })
  })

  it('builds workflow control collection and mutation requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.providers()
    await api.triggers('team/data')
    await api.triggers()
    await api.triggerOccurrences('team/data')
    await api.triggerOccurrences()
    await api.checkPolicies('team/data')
    await api.checkEvaluations()
    await api.checkCompliance('team/data')
    await api.setTriggerPaused('team/data', 'daily flow', 'schedule/one', true, 'maintenance')
    await api.replayTriggerOccurrence('occurrence/one', 'operator replay')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/auth/providers',
      '/api/v1/triggers?namespace=team%2Fdata',
      '/api/v1/triggers',
      '/api/v1/trigger-occurrences?limit=200&namespace=team%2Fdata',
      '/api/v1/trigger-occurrences?limit=200',
      '/api/v1/check-policies?limit=200&namespace=team%2Fdata',
      '/api/v1/check-evaluations?limit=200',
      '/api/v1/check-compliance?groupBy=flow&limit=200&namespace=team%2Fdata',
      '/api/v1/triggers/team%2Fdata/daily%20flow/schedule%2Fone/pause',
      '/api/v1/trigger-occurrences/occurrence%2Fone/replay',
    ])
  })

  it('creates a browser session without a bearer token', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ principalId: 'user-1', display: 'User' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: '', tenant: 'default', namespace: '' })

    await api.login('operator', 'correct horse battery staple')

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    const headers = new Headers(init.headers)
    expect(url).toBe('/api/v1/auth/login')
    expect(init.credentials).toBe('same-origin')
    expect(headers.has('authorization')).toBe(false)
    expect(headers.get('content-type')).toBe('application/json')
    expect(JSON.parse(init.body as string)).toEqual({
      provider: 'local',
      identifier: 'operator',
      password: 'correct horse battery staple',
    })
  })

  it('sends the same-origin CSRF cookie on logout', async () => {
    document.cookie = 'amesh_csrf=csrf-proof; path=/'
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: '', tenant: 'default', namespace: '' })

    await api.logout()

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(new Headers(init.headers).get('x-amesh-csrf')).toBe('csrf-proof')
    expect(init.method).toBe('POST')
  })
})
