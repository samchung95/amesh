import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, createApiClient } from './client'
import type { AssetDraft } from './types'

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
    const fetchMock = vi.fn().mockImplementation((path: string) => Promise.resolve(new Response(
      path.includes('/evidence/stream') ? '{"event_id":"one","nextCursor":"cursor-2"}\n' : '{}',
      { status: 200 },
    )))
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
    const streamed: unknown[] = []
    await api.streamExecutionEvidence('run/one', 'cursor/value', (event) => streamed.push(event), new AbortController().signal)

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/health',
      '/api/v1/ui/session',
      '/api/v1/flows/team%2Fdata/daily%20flow/graph',
      '/api/v1/flows/team%2Fdata/daily%20flow/metadata',
      '/api/v1/flows/team%2Fdata/daily%20flow/data-contract',
      '/api/v1/executions',
      '/api/v1/executions/run%2Fone?taskOffset=0&taskLimit=250',
      '/api/v1/executions/run%2Fone/graph',
      '/api/v1/executions/run%2Fone/evidence?cursor=cursor%2Fvalue',
      '/api/v1/executions/run%2Fone/evidence/stream?cursor=cursor%2Fvalue',
    ])
    expect(streamed).toEqual([{ event_id: 'one', nextCursor: 'cursor-2' }])
    const executeInit = fetchMock.mock.calls[5]?.[1] as RequestInit
    expect(executeInit.method).toBe('POST')
    expect(JSON.parse(executeInit.body as string)).toEqual({
      namespace: 'team/data',
      flowId: 'daily flow',
      inputs: { message: 'hello' },
      runner: 'local',
    })
  })

  it('builds asset catalog list, detail, declaration and export requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(
      new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } }),
    ))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })
    const draft: AssetDraft = {
      assetId: 'asset-one',
      namespace: 'team/data',
      provider: 'postgresql',
      account: 'analytics',
      location: 'warehouse:5432',
      externalKey: 'curated.orders',
      assetType: 'table',
      displayName: 'Curated orders',
      description: '',
      owner: null,
      contacts: [],
      domainGroup: null,
      tags: [],
      customMetadata: {},
      labels: {},
      health: 'UNKNOWN',
      lastMaterializationAt: null,
      source: 'DECLARED',
    }

    await api.assets('team/data')
    await api.assets()
    await api.asset('asset/one')
    await api.registerAsset(draft)
    await api.exportAssetCatalog('team/data')
    await api.exportAssetCatalog()

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/assets?namespace=team%2Fdata',
      '/api/v1/assets',
      '/api/v1/assets/asset%2Fone',
      '/api/v1/assets',
      '/api/v1/assets/export/openlineage?namespace=team%2Fdata',
      '/api/v1/assets/export/openlineage',
    ])
    const declaration = fetchMock.mock.calls[3]?.[1] as RequestInit
    expect(declaration.method).toBe('POST')
    expect(JSON.parse(declaration.body as string)).toEqual(draft)
  })

  it('builds execution debugging, intervention and backfill requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })
    const preview = {
      execution_id: 'run/one', action: 'PAUSE' as const, current_state: 'RUNNING' as const,
      predicted_state: 'PAUSED' as const, current_version: 4, current_epoch: 2,
      checkpoint_task_id: null, impacted_task_ids: [], preserved_task_ids: [],
      invalidates_active_claims: false, destructive: false, force_available_at: null,
      consequences: [],
    }
    const spec = {
      namespace: 'team/data', flowId: 'daily flow', flowRevision: 3,
      selection: { sourceExecutionIds: ['run/one'] }, inputs: {}, labels: {},
      maxConcurrency: 1, ratePerMinute: 60, priority: 0,
    }

    await api.executionSubflows('run/one')
    await api.executionParentSubflow('run/one')
    await api.executionInterventions('run/one')
    await api.executionFiles('run/one')
    await api.downloadExecutionFile('run/one', 'file/one')
    await api.previewExecutionIntervention('run/one', 'PAUSE')
    await api.applyExecutionIntervention('run/one', preview, 'maintenance')
    await api.previewBackfill(spec)
    await api.createBackfill(spec)

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/executions/run%2Fone/subflows',
      '/api/v1/executions/run%2Fone/parent-subflow',
      '/api/v1/executions/run%2Fone/interventions',
      '/api/v1/executions/run%2Fone/files',
      '/api/v1/executions/run%2Fone/files/file%2Fone',
      '/api/v1/executions/run%2Fone/interventions/preview',
      '/api/v1/executions/run%2Fone/interventions',
      '/api/v1/backfills/preview',
      '/api/v1/backfills',
    ])
    const applyInit = fetchMock.mock.calls[6]?.[1] as RequestInit
    expect(JSON.parse(applyInit.body as string)).toMatchObject({ action: 'PAUSE', expectedVersion: 4, expectedEpoch: 2, reason: 'maintenance' })
  })

  it('builds lifecycle policy, hold, preview and resumable purge requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })
    const policy = {
      resourceType: 'EXECUTION' as const,
      scope: 'NAMESPACE' as const,
      namespace: 'team/data',
      labelSelector: {},
      retentionDays: 30,
      batchSize: 100,
      scheduleIntervalMinutes: 60,
      enabled: true,
      reason: 'scheduled retention policy',
    }
    const hold = {
      name: 'case-608', reason: 'preserve investigation evidence',
      resourceType: 'EXECUTION' as const, resourceId: 'run/one',
      namespace: 'team/data', labelSelector: {},
    }

    await api.lifecyclePolicies()
    await api.createLifecyclePolicy(policy)
    await api.lifecycleLegalHolds()
    await api.createLifecycleLegalHold(hold)
    await api.releaseLifecycleLegalHold('hold/one')
    await api.lifecycleJobs()
    await api.previewLifecyclePurge('policy/one', 'manual preview')
    await api.executeLifecycleJob('job/one', 'PURGE 12')
    await api.resumeLifecycleJob('job/one')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/lifecycle/policies',
      '/api/v1/lifecycle/policies',
      '/api/v1/lifecycle/legal-holds',
      '/api/v1/lifecycle/legal-holds',
      '/api/v1/lifecycle/legal-holds/hold%2Fone/release',
      '/api/v1/lifecycle/jobs',
      '/api/v1/lifecycle/previews',
      '/api/v1/lifecycle/jobs/job%2Fone/execute',
      '/api/v1/lifecycle/jobs/job%2Fone/resume',
    ])
    expect(JSON.parse((fetchMock.mock.calls[1]?.[1] as RequestInit).body as string)).toEqual(policy)
    expect(JSON.parse((fetchMock.mock.calls[6]?.[1] as RequestInit).body as string)).toEqual({ policyId: 'policy/one', reason: 'manual preview' })
    expect(JSON.parse((fetchMock.mock.calls[7]?.[1] as RequestInit).body as string)).toEqual({ confirmation: 'PURGE 12' })
  })

  it('builds upgrade reports and exact bounded event-upcast requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.upgradePolicy()
    await api.upgradeReport('preflight', '0.1.0', '0.2.0')
    await api.upgradeReport('postflight', '0.1.0', '0.2.0')
    await api.previewEventUpcast()
    await api.applyEventUpcast('UPCAST 3', 'supported LTS migration', 25)

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/upgrades/policy',
      '/api/v1/upgrades/preflight',
      '/api/v1/upgrades/postflight',
      '/api/v1/upgrades/events/upcast',
      '/api/v1/upgrades/events/upcast',
    ])
    expect(JSON.parse((fetchMock.mock.calls[1]?.[1] as RequestInit).body as string)).toEqual({ fromVersion: '0.1.0', toVersion: '0.2.0' })
    expect(JSON.parse((fetchMock.mock.calls[4]?.[1] as RequestInit).body as string)).toEqual({ confirmation: 'UPCAST 3', reason: 'supported LTS migration', batchSize: 25 })
  })

  it('loads redacted network diagnostics from the operations API', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.networkDiagnostics()

    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/operations/network-diagnostics')
  })

  it('uses a deterministic fallback when JSON detail is not text', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 42 }), { status: 500 })))
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await expect(api.flows()).rejects.toMatchObject({ message: 'Request failed with status 500' })
  })

  it('posts revision-pinned side-effect-free simulation inputs', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.simulateFlow('team/data', 'daily flow', 7, { customer: 'acme' })

    const [path, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(path).toBe('/api/v1/flows/team%2Fdata/daily%20flow/revisions/7/simulate')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toEqual({
      inputs: { customer: 'acme' },
      fixtures: {},
      estimateModels: {},
      signEvidence: true,
    })
  })

  it('builds revision-pinned flow-test and quality-gate requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })
    const draft = {
      testId: 'branch-a', name: 'Branch A', revision: 3, inputs: {}, variables: {},
      fixtures: {}, expected: { state: 'SUCCESS' }, tags: ['ci'],
    }

    await api.flowTests('team/data', 'daily flow', 3)
    await api.saveFlowTest('team/data', 'daily flow', draft)
    await api.runFlowTests('team/data', 'daily flow', 3, ['branch-a'])
    await api.flowTestRuns('team/data', 'daily flow', 3)
    await api.flowTestGate('team/data')
    await api.saveFlowTestGate('team/data', true, 80, ['branch-a'], 2)
    await api.deleteFlowTest('team/data', 'daily flow', 'branch-a', 4)

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/flows/team%2Fdata/daily%20flow/tests?revision=3',
      '/api/v1/flows/team%2Fdata/daily%20flow/tests',
      '/api/v1/flows/team%2Fdata/daily%20flow/tests/runs?revision=3',
      '/api/v1/flows/team%2Fdata/daily%20flow/tests/runs?revision=3',
      '/api/v1/namespaces/team%2Fdata/flow-test-gate',
      '/api/v1/namespaces/team%2Fdata/flow-test-gate',
      '/api/v1/flows/team%2Fdata/daily%20flow/tests/branch-a?expectedVersion=4',
    ])
    const runInit = fetchMock.mock.calls[2]?.[1] as RequestInit
    expect(JSON.parse(runInit.body as string)).toEqual({ testIds: ['branch-a'], failFast: false })
  })

  it('builds workflow control collection and mutation requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.providers()
    await api.routedProviders('ada@example.com', 'tenant-a')
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
      '/api/v1/auth/providers?identifier=ada%40example.com&tenant=tenant-a',
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

  it('builds encoded namespace resource requests without sending secret values', async () => {
    const fetchMock = vi.fn().mockImplementation((path: string, init?: RequestInit) => Promise.resolve(
      path.includes('/files/config/rules.txt') && (!init?.method || init.method === 'GET') && !path.endsWith('/versions')
        ? new Response('rules', { status: 200, headers: { 'Content-Type': 'text/plain' } })
        : new Response('{}', { status: 200 }),
    ))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: 'team/data' })
    const file = new File(['rules'], 'rules.txt', { type: 'text/plain' })

    await api.namespaceFiles('team/data')
    await api.uploadNamespaceFile('team/data', 'config/rules.txt', file)
    await api.downloadNamespaceFile('team/data', 'config/rules.txt', 2)
    await api.namespaceFileVersions('team/data', 'config/rules.txt')
    await api.moveNamespaceFile('team/data', 'config/rules.txt', 'archive/rules.txt', 2)
    await api.putNamespaceKeyValue('team/data', 'release channel', 'STRING', 'stable')
    await api.putNamespaceSecretBinding('team/data', 'API/KEY', 'PRODUCTION_API_KEY')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/namespaces/team%2Fdata/files',
      '/api/v1/namespaces/team%2Fdata/files/config/rules.txt',
      '/api/v1/namespaces/team%2Fdata/files/config/rules.txt?version=2',
      '/api/v1/namespaces/team%2Fdata/files/config/rules.txt/versions',
      '/api/v1/namespaces/team%2Fdata/files/config/rules.txt/move',
      '/api/v1/namespaces/team%2Fdata/key-values/release%20channel',
      '/api/v1/namespaces/team%2Fdata/secret-bindings/API%2FKEY',
    ])
    const secretInit = fetchMock.mock.calls[6]?.[1] as RequestInit
    const secretBody = JSON.parse(secretInit.body as string) as Record<string, unknown>
    expect(secretBody).toEqual({ provider: 'env', providerReference: 'PRODUCTION_API_KEY' })
    expect(JSON.stringify(secretBody)).not.toContain('secretValue')
  })

  it('uses the server-authoritative flow editor and revision endpoints', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(
      new Response('{}', { status: 200 }),
    ))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.flowEditorSchema()
    await api.validateFlow('id: daily')
    await api.formatFlow('id: daily')
    await api.saveFlow('id: daily', 'etag-7')
    await api.flowDocument('team/data', 'daily flow', 3)
    await api.flowRevisions('team/data', 'daily flow')
    await api.diffFlowDraft('team/data', 'daily flow', 2, 'id: daily')
    await api.setFlowLifecycle('team/data', 'daily flow', 3, 'DISABLED', 'maintenance')
    await api.restoreFlowRevision('team/data', 'daily flow', 2, 'rollback')
    await api.previewExpression('{{ inputs.name }}', { inputs: { name: 'Ada' } })

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/flows/editor/schema',
      '/api/v1/flows/validate',
      '/api/v1/flows/format',
      '/api/v1/flows',
      '/api/v1/flows/team%2Fdata/daily%20flow/document?revision=3',
      '/api/v1/flows/team%2Fdata/daily%20flow/revisions',
      '/api/v1/flows/team%2Fdata/daily%20flow/revisions/2/diff-draft',
      '/api/v1/flows/team%2Fdata/daily%20flow/revisions/3/lifecycle',
      '/api/v1/flows/team%2Fdata/daily%20flow/revisions/2/restore',
      '/api/v1/flows/expressions/preview',
    ])
    const saveInit = fetchMock.mock.calls[3]?.[1] as RequestInit
    expect(new Headers(saveInit.headers).get('if-match')).toBe('etag-7')
    expect(saveInit.body).toBe('id: daily')
  })

  it('uses the versioned blueprint catalog and isolated playground endpoints', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(
      new Response('{}', { status: 200 }),
    ))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.blueprints('hello world', 'BUILTIN')
    await api.blueprint('hello-world', '1.0.0')
    await api.instantiateBlueprint('hello-world', '1.0.0', {
      namespace: 'examples.local',
      flow_id: 'hello_draft',
    })
    await api.simulatePlayground(
      '{{ inputs.name }}',
      { inputs: { name: 'Ada' } },
      'id: done\ntype: core.return\nvalue: ok\n',
    )

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/blueprints?q=hello+world&source=BUILTIN',
      '/api/v1/blueprints/hello-world/1.0.0',
      '/api/v1/blueprints/hello-world/1.0.0/instantiate',
      '/api/v1/playground/simulate',
    ])
    const instantiateInit = fetchMock.mock.calls[2]?.[1] as RequestInit
    const instantiateBody = JSON.parse(instantiateInit.body as string) as Record<string, unknown>
    expect(instantiateBody).toEqual({
      parameters: { namespace: 'examples.local', flow_id: 'hello_draft' },
    })
  })

  it('builds typed dashboard query, persistence and export requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })
    const query = {
      source: 'EXECUTIONS' as const, visualization: 'STATUS_BREAKDOWN' as const,
      measure: 'COUNT' as const, aggregation: 'COUNT' as const, groupBy: ['state'],
      filters: { namespace: 'team/data' }, limit: 100, timeoutMs: 1500, sampleRate: 1,
    }
    const spec = {
      title: 'Operations', description: '', visibility: 'TENANT' as const,
      viewerIds: [], editorIds: [], source: 'API' as const,
      widgets: [{ widgetId: 'states', title: 'States', description: '', query }],
    }

    await api.dashboards()
    await api.dashboard('ops/team')
    await api.renderDashboard('ops/team', { namespace: 'team/data' })
    await api.queryDashboard(query)
    await api.saveDashboard('ops/team', spec)
    await api.saveDashboard('ops/team', spec, 2)
    await api.deleteDashboard('ops/team', 3)
    await api.exportDashboard('ops/team', 'json')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/dashboards',
      '/api/v1/dashboards/ops%2Fteam',
      '/api/v1/dashboards/ops%2Fteam/render',
      '/api/v1/dashboard-queries',
      '/api/v1/dashboards/ops%2Fteam',
      '/api/v1/dashboards/ops%2Fteam?expectedVersion=2',
      '/api/v1/dashboards/ops%2Fteam?expectedVersion=3',
      '/api/v1/dashboards/ops%2Fteam/export?format=json',
    ])
    expect((fetchMock.mock.calls[2]?.[1] as RequestInit).method).toBe('POST')
    expect((fetchMock.mock.calls[4]?.[1] as RequestInit).method).toBe('PUT')
    expect((fetchMock.mock.calls[6]?.[1] as RequestInit).method).toBe('DELETE')
  })

  it('builds typed search, status and rebuild requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.search({
      query: 'needle', types: ['FLOW', 'LOG'], namespace: 'team.data',
      labels: { team: 'platform' }, fields: { level: 'ERROR' },
      sort: 'UPDATED_AT', direction: 'DESC', limit: 25,
    })
    await api.searchStatus()
    await api.rebuildSearch('repair projection drift')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/search',
      '/api/v1/search/status',
      '/api/v1/search/rebuild',
    ])
    const searchInit = fetchMock.mock.calls[0]?.[1] as RequestInit
    expect(searchInit.method).toBe('POST')
    expect(JSON.parse(searchInit.body as string)).toMatchObject({ query: 'needle', types: ['FLOW', 'LOG'] })
    const rebuildInit = fetchMock.mock.calls[2]?.[1] as RequestInit
    expect(JSON.parse(rebuildInit.body as string)).toEqual({ reason: 'repair projection drift' })
  })

  it('builds guarded administration control requests', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'tenant-a', namespace: '' })
    const draft = { key: 'KILL_SWITCH' as const, enabled: true, value: null, reason: 'incident containment', expectedVersion: 2 }
    const preview = {
      draft,
      impacts: ['Stop new execution admission.'],
      recovery: 'Disable the switch.',
      confirmation: 'APPLY KILL_SWITCH',
      approval: 'signed-approval',
      expiresAt: '2026-08-23T01:00:00Z',
    }

    await api.administrationControls()
    await api.previewAdministrationControl(draft)
    await api.applyAdministrationControl(preview, preview.confirmation)
    await api.administrationAudit()

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/admin/controls',
      '/api/v1/admin/controls/preview',
      '/api/v1/admin/controls/KILL_SWITCH',
      '/api/v1/admin/audit?limit=200',
    ])
    expect(JSON.parse((fetchMock.mock.calls[1]?.[1] as RequestInit).body as string)).toEqual(draft)
    expect(JSON.parse((fetchMock.mock.calls[2]?.[1] as RequestInit).body as string)).toEqual({
      draft,
      approval: 'signed-approval',
      confirmation: 'APPLY KILL_SWITCH',
    })
  })

  it('uses versioned admission policy and decision endpoints', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: 'team/data' })
    const policy = {
      schemaVersion: 'amesh.policy/v1' as const,
      policyKey: 'security.local',
      name: 'Local security',
      description: 'Local test policy',
      scope: 'NAMESPACE' as const,
      namespace: 'team/data',
      criticality: 'ENFORCING' as const,
      evaluationTimeoutMs: 100,
      enabled: true,
      rules: [{
        id: 'deny-docker',
        stages: ['LAUNCH' as const],
        conditions: [{ path: 'runner.requested', operator: 'EQUALS' as const, value: 'DOCKER' }],
        outcome: 'DENY' as const,
        reason: 'Docker disabled',
        mutations: {},
      }],
    }

    await api.admissionPolicies('team/data')
    await api.admissionPolicyDecisions()
    await api.saveAdmissionPolicy(policy)
    await api.validateFlowPolicy('id: governed')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/policies?namespace=team%2Fdata',
      '/api/v1/policies/decisions?limit=50',
      '/api/v1/policies',
      '/api/v1/policies/flows/validate',
    ])
    const saveInit = fetchMock.mock.calls[2]?.[1] as RequestInit
    expect(saveInit.method).toBe('POST')
    expect(JSON.parse(saveInit.body as string)).toEqual(policy)
  })

  it('builds release preview, promotion and recovery requests with concurrency guards', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 200 })))
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient({ token: 'token', tenant: 'default', namespace: '' })

    await api.previewRelease('policy/one')
    await api.applyRelease('policy/one', 3, 'promote tested revision')
    await api.releaseTarget('WORKFLOW', 'examples/safe/research')
    await api.releaseHistory('WORKFLOW', 'examples/safe/research')
    await api.rollbackRelease('WORKFLOW', 'examples/safe/research', 2, 4, 'restore known good revision')
    await api.killSwitchRelease('WORKFLOW', 'examples/safe/research', 5, 'stop during incident review')

    expect(fetchMock.mock.calls.map((call) => call[0] as string)).toEqual([
      '/api/v1/releases/policies/policy%2Fone/preview',
      '/api/v1/releases/policies/policy%2Fone/apply',
      '/api/v1/releases/WORKFLOW/examples%2Fsafe%2Fresearch',
      '/api/v1/releases/WORKFLOW/examples%2Fsafe%2Fresearch/history',
      '/api/v1/releases/WORKFLOW/examples%2Fsafe%2Fresearch/rollback',
      '/api/v1/releases/WORKFLOW/examples%2Fsafe%2Fresearch/kill-switch',
    ])
    expect(JSON.parse((fetchMock.mock.calls[0]?.[1] as RequestInit).body as string)).toEqual({ approvals: {} })
    expect(JSON.parse((fetchMock.mock.calls[1]?.[1] as RequestInit).body as string)).toEqual({ expectedVersion: 3, reason: 'promote tested revision', approvals: {} })
    expect(JSON.parse((fetchMock.mock.calls[4]?.[1] as RequestInit).body as string)).toEqual({ toRevision: 2, expectedVersion: 4, reason: 'restore known good revision' })
    expect(JSON.parse((fetchMock.mock.calls[5]?.[1] as RequestInit).body as string)).toEqual({ expectedVersion: 5, reason: 'stop during incident review' })
  })
})
