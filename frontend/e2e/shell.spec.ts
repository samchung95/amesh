import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

const session = {
  principalId: '00000000-0000-7000-8000-000000000002',
  principalType: 'USER',
  display: 'Operator',
  tenantId: 'default',
  namespace: null,
  capabilities: {
    'assets.view': true,
    'assets.manage': true,
    'flows.view': true,
    'flows.create': true,
    'flows.update': true,
    'executions.view': true,
    'executions.execute': true,
    'executions.manage': true,
    'dashboards.view': true,
    'dashboards.manage': true,
    'search.view': true,
    'search.manage': true,
    'triggers.view': true,
    'triggers.manage': true,
    'checks.view': true,
    'checks.manage': true,
    'namespaces.view': true,
    'namespaceResources.read': true,
    'namespaceResources.write': true,
    'secretBindings.write': true,
    'plugins.view': true,
    'administration.manage': false,
  },
  telemetryEnabled: false,
  serverVersion: '0.2.0',
}

const flows = [
  { resource_id: 'flow-1', tenant_id: 'default', namespace: 'examples.engine', flow_id: 'hello_world', revision: 3, semantic_hash: 'abc1234567890def', etag: 'etag-1' },
  { resource_id: 'flow-2', tenant_id: 'default', namespace: 'examples.agent', flow_id: 'luna_research', revision: 1, semantic_hash: 'def1234567890abc', etag: 'etag-2' },
]

const executions = [
  { execution_id: '00000000-0000-7000-8000-000000000101', tenant_id: 'default', state: 'RUNNING', epoch: 1, version: 2, namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, inputs: { message: 'hello' }, outputs: {}, labels: { environment: 'test' }, trigger: { type: 'manual' }, created_by: 'operator', created_at: '2026-08-21T12:00:00Z', updated_at: '2026-08-21T12:01:00Z', timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {} },
  { execution_id: '00000000-0000-7000-8000-000000000102', tenant_id: 'default', state: 'SUCCESS', epoch: 1, version: 4, namespace: 'examples.agent', flow_id: 'luna_research', flow_revision: 1, inputs: {}, outputs: {}, labels: {}, trigger: { type: 'cron' }, created_by: 'scheduler', created_at: '2026-08-21T11:00:00Z', updated_at: '2026-08-21T11:02:00Z', timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {} },
]

const searchDocuments = [
  { documentType: 'FLOW', documentId: 'flow-1', namespace: 'examples.engine', title: 'examples.engine.hello_world', summary: 'Searchable hello workflow', state: 'ACTIVE', labels: { team: 'platform' }, fields: { flowId: 'hello_world' }, occurredAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T12:00:00Z', sourceVersion: 3, relevance: 1.2 },
  { documentType: 'LOG', documentId: 'log-1', namespace: 'examples.engine', title: 'ERROR · task.return', summary: 'diagnostic needle appeared', state: 'ERROR', labels: {}, fields: { flowId: 'hello_world', executionId: executions[0].execution_id, level: 'ERROR', logger: 'task.return' }, occurredAt: '2026-08-21T12:00:03Z', updatedAt: '2026-08-21T12:00:03Z', sourceVersion: 0, relevance: 0.9 },
]

const dashboardDefinitions = [
  {
    dashboardId: 'builtin.instance', tenantId: 'default', title: 'Instance overview', description: 'Execution, log and worker posture across the selected tenant.', visibility: 'TENANT', viewerIds: [], editorIds: [], source: 'BUILTIN', version: 1, ownerId: 'system', builtin: true, createdAt: '2026-01-01T00:00:00Z', updatedAt: '2026-01-01T00:00:00Z',
    widgets: [
      { widgetId: 'executions', title: 'Executions', description: '', query: { source: 'EXECUTIONS', visualization: 'COUNTER', measure: 'COUNT', aggregation: 'COUNT', groupBy: [], filters: {}, limit: 100, timeoutMs: 1500, sampleRate: 1 } },
      { widgetId: 'states', title: 'Execution states', description: '', query: { source: 'EXECUTIONS', visualization: 'STATUS_BREAKDOWN', measure: 'COUNT', aggregation: 'COUNT', groupBy: [], filters: {}, limit: 100, timeoutMs: 1500, sampleRate: 1 } },
      { widgetId: 'activity', title: 'Execution activity', description: '', query: { source: 'EXECUTIONS', visualization: 'TIME_SERIES', measure: 'COUNT', aggregation: 'COUNT', groupBy: ['state'], filters: {}, limit: 100, timeoutMs: 1500, sampleRate: 1 } },
      { widgetId: 'log_levels', title: 'Log levels', description: '', query: { source: 'LOGS', visualization: 'RANKED_LIST', measure: 'COUNT', aggregation: 'COUNT', groupBy: ['level'], filters: {}, limit: 8, timeoutMs: 1500, sampleRate: 0.25 } },
    ],
  },
  ...['tenant', 'namespace', 'flow', 'workers', 'sla'].map((id) => ({ dashboardId: `builtin.${id}`, tenantId: 'default', title: `${id[0].toUpperCase()}${id.slice(1)} dashboard`, description: `${id} operational view`, visibility: 'TENANT', viewerIds: [], editorIds: [], source: 'BUILTIN', version: 1, ownerId: 'system', builtin: true, createdAt: '2026-01-01T00:00:00Z', updatedAt: '2026-01-01T00:00:00Z', widgets: [] })),
]

const triggers = [
  { trigger_definition_id: '00000000-0000-7000-8000-000000000301', tenant_id: 'default', namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, trigger_id: 'every_minute', trigger_type: 'core.cron', active: true, paused: false, checkpoint: {}, cursor: null, last_evaluated_at: '2026-08-21T12:01:00Z', next_evaluation_at: '2026-08-21T12:02:00Z', last_occurrence_at: '2026-08-21T12:01:00Z', last_success_at: '2026-08-21T12:01:00Z', lag_seconds: 2, pending_count: 1, dead_letter_count: 0, consecutive_failures: 0, last_error: null, last_decision: 'occurrence launched execution', updated_at: '2026-08-21T12:01:00Z' },
]

const triggerOccurrences = [
  { occurrence_id: '00000000-0000-7000-8000-000000000302', tenant_id: 'default', trigger_definition_id: triggers[0].trigger_definition_id, namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, trigger_id: 'every_minute', trigger_type: 'core.cron', occurrence_key: 'core.cron:examples.engine:hello_world:3:every_minute:2026-08-21T12:01:00Z', state: 'SUCCEEDED', attempt: 1, max_attempts: 3, available_at: '2026-08-21T12:01:00Z', payload: {}, metadata: { source: 'schedule' }, evidence: { reason: 'scheduled occurrence created an execution' }, execution_id: executions[1].execution_id, replay_of: null, created_at: '2026-08-21T12:01:00Z', updated_at: '2026-08-21T12:01:01Z', completed_at: '2026-08-21T12:01:01Z' },
]

const checkEvaluations = [
  { evaluation_id: '00000000-0000-7000-8000-000000000401', tenant_id: 'default', check_definition_id: '00000000-0000-7000-8000-000000000402', execution_id: executions[1].execution_id, namespace: 'examples.agent', flow_id: 'luna_research', flow_revision: 1, check_id: 'research-output', check_type: 'OUTPUT', source: 'EXPLICIT', evaluation_point: 'TERMINAL', subject_key: `execution:${executions[1].execution_id}`, outcome: 'PASS', severity: 'FAIL', reason: 'expression evaluated true', evidence: { result: true }, labels: { service: 'research' }, evaluated_at: '2026-08-21T11:02:00Z' },
  { evaluation_id: '00000000-0000-7000-8000-000000000403', tenant_id: 'default', check_definition_id: '00000000-0000-7000-8000-000000000404', execution_id: executions[0].execution_id, namespace: 'examples.engine', flow_id: 'hello_world', flow_revision: 3, check_id: 'start-latency', check_type: 'START_DELAY', source: 'NAMESPACE', evaluation_point: 'STARTED', subject_key: `execution:${executions[0].execution_id}`, outcome: 'WARN', severity: 'WARN', reason: 'execution start delay exceeded the configured threshold', evidence: { delaySeconds: 12 }, labels: { service: 'engine' }, evaluated_at: '2026-08-21T12:00:00Z' },
]

const checkCompliance = [
  { group_key: 'examples.agent.luna_research', total: 1, passed: 1, warned: 0, failed: 0, errors: 0, compliance_rate: 1 },
  { group_key: 'examples.engine.hello_world', total: 1, passed: 0, warned: 1, failed: 0, errors: 0, compliance_rate: 0 },
]

const checkPolicies = [
  { policy_id: '00000000-0000-7000-8000-000000000405', tenant_id: 'default', namespace: 'examples.engine', policy_key: 'interactive-start', source: 'NAMESPACE', task_type: null, definition: { id: 'start-latency', type: 'START_DELAY', severity: 'WARN', threshold: 'PT10S', enabled: true, actions: [] }, enabled: true, created_at: '2026-08-21T10:00:00Z', updated_at: '2026-08-21T10:00:00Z' },
]

const namespaceFiles = [
  { namespace: 'team.data', path: 'config/rules.json', version: 2, resourceVersion: 2, sizeBytes: 128, checksumSha256: 'a'.repeat(64), contentType: 'application/json', metadata: {}, originNamespace: 'team.data', inherited: false, createdAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T11:00:00Z' },
]

const namespaceKeyValues = [
  { namespace: 'team.data', key: 'release.channel', type: 'STRING', value: 'stable', expiresAt: null, metadata: {}, resourceVersion: 1, createdAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T10:00:00Z' },
]

const namespaceSecrets = [
  { namespace: 'team.data', key: 'API_KEY', provider: 'env', providerReference: 'PRODUCTION_API_KEY', metadata: {}, resourceVersion: 1, inherited: false, originNamespace: 'team.data', createdAt: '2026-08-21T10:00:00Z', updatedAt: '2026-08-21T10:00:00Z' },
]

const catalogAssets = [
  { assetId: '00000000-0000-7000-8000-000000000601', tenantId: 'default', namespace: 'team.data', provider: 'postgresql', account: 'analytics', location: 'warehouse.internal:5432', externalKey: 'raw.orders', assetType: 'table', displayName: 'Raw orders', description: 'Unmodified order intake.', owner: 'data-platform', contacts: ['data@example.test'], domainGroup: 'commerce', tags: ['qualified', 'raw'], customMetadata: { classification: 'internal' }, labels: {}, health: 'UNKNOWN', lastMaterializationAt: null, source: 'PLUGIN_EVENT', resourceVersion: 2, createdBy: 'plugin:warehouse', updatedBy: 'plugin:warehouse', createdAt: '2026-08-23T09:00:00Z', updatedAt: '2026-08-23T09:01:00Z' },
  { assetId: '00000000-0000-7000-8000-000000000602', tenantId: 'default', namespace: 'team.data', provider: 'postgresql', account: 'analytics', location: 'warehouse.internal:5432', externalKey: 'curated.orders', assetType: 'table', displayName: 'Curated orders', description: 'Validated order facts.', owner: 'analytics', contacts: ['analytics@example.test'], domainGroup: 'commerce', tags: ['qualified', 'gold'], customMetadata: { classification: 'internal' }, labels: {}, health: 'HEALTHY', lastMaterializationAt: '2026-08-23T09:02:00Z', source: 'DECLARED', resourceVersion: 3, createdBy: session.principalId, updatedBy: 'plugin:warehouse', createdAt: '2026-08-23T08:00:00Z', updatedAt: '2026-08-23T09:02:00Z' },
]

const blueprints = [
  {
    blueprintId: 'hello-world', version: '1.0.0', source: 'BUILTIN', title: 'Hello, workflow', summary: 'A local log-and-return flow with one optional input.', tags: ['getting-started', 'local', 'core'], documentation: 'Start here. The draft uses only deterministic core tasks and runs in Compose.', license: 'Apache-2.0', localOnly: true,
    parameters: [{ name: 'namespace', title: 'Namespace', description: 'Draft namespace in dotted AMESH form.', kind: 'NAMESPACE', required: true, default: 'examples.getting_started' }, { name: 'flow_id', title: 'Flow ID', description: 'Natural identifier for the unsaved draft.', kind: 'FLOW_ID', required: true, default: 'hello_blueprint' }, { name: 'greeting', title: 'Greeting', description: 'Text emitted before the supplied name.', kind: 'STRING', required: true, default: 'Hello' }],
    provenance: { publisher: 'AMESH project', location: 'repository://amesh/examples/hello-world.yaml', revision: '0.2.0', digest: `sha256:${'a'.repeat(64)}` },
    template: 'apiVersion: amesh.flow/v1\nid: ${flow_id}\nnamespace: ${namespace}\ntasks:\n- id: done\n  type: core.return\n  value: ${greeting}\n',
  },
  {
    blueprintId: 'organization-readiness', version: '1.0.0', source: 'ORGANIZATION', title: 'Organization readiness marker', summary: 'A policy-neutral local marker.', tags: ['organization'], documentation: 'Organization example.', license: 'Apache-2.0', localOnly: true, parameters: [], provenance: { publisher: 'Example organization', location: 'organization://default', revision: '1', digest: `sha256:${'b'.repeat(64)}` }, template: 'tasks: []\n',
  },
  {
    blueprintId: 'community-batch', version: '1.0.0', source: 'COMMUNITY', title: 'Community batch loop', summary: 'A bounded foreach example.', tags: ['community', 'foreach'], documentation: 'Community example.', license: 'MIT', localOnly: true, parameters: [], provenance: { publisher: 'AMESH community', location: 'community://amesh/examples', revision: '1', digest: `sha256:${'c'.repeat(64)}` }, template: 'tasks: []\n',
  },
]

async function mockApi(page: Page, overrides = session) {
  let customDashboard: Record<string, unknown> | null = null
  let assetRecords = [...catalogAssets]
  let adminControls: Array<{ key: string; flagKey: string; enabled: boolean; value: unknown; version: number | null; updatedBy: string | null; updatedAt: string | null }> = [
    { key: 'RETENTION', flagKey: 'admin-retention-executions', enabled: false, value: 30, version: null, updatedBy: null, updatedAt: null },
    { key: 'ANNOUNCEMENT', flagKey: 'admin-announcement-banner', enabled: false, value: '', version: null, updatedBy: null, updatedAt: null },
    { key: 'MAINTENANCE', flagKey: 'admin-maintenance-mode', enabled: false, value: null, version: null, updatedBy: null, updatedAt: null },
    { key: 'KILL_SWITCH', flagKey: 'admin-execution-kill-switch', enabled: false, value: null, version: null, updatedBy: null, updatedAt: null },
  ]
  const adminAudit: Array<Record<string, unknown>> = []
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: overrides }))
  await page.route('**/ready', (route) => route.fulfill({ json: { status: 'ready', version: '0.2.0', database: 'ready', migrations_applied: 44, migrations_expected: 44, latest_migration: '0044_search_projection.sql', error: null } }))
  await page.route('**/api/v1/auth/providers**', (route) => route.fulfill({ json: [
    { id: 'local', kind: 'local', display_name: 'Local account', interactive: true, login_mode: 'password', domains: [], tenants: [] },
    { id: 'corporate-oidc', kind: 'oidc', display_name: 'Corporate OIDC', interactive: true, login_mode: 'redirect', domains: ['example.com'], tenants: ['default'] },
    { id: 'directory', kind: 'ldap', display_name: 'Corporate directory', interactive: true, login_mode: 'password', domains: ['example.com'], tenants: ['default'] },
  ] }))
  await page.route('**/api/v1/admin/controls**', (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path.endsWith('/preview')) {
      const draft = request.postDataJSON() as Record<string, unknown>
      return route.fulfill({ json: { draft, impacts: ['Stop new execution admission for this tenant.'], recovery: 'Disable the switch and verify capacity.', confirmation: `APPLY ${String(draft.key)}`, approval: 'signed-administration-approval', expiresAt: '2026-08-23T10:00:00Z' } })
    }
    if (request.method() === 'PUT') {
      const body = request.postDataJSON() as { draft: { key: string; enabled: boolean; value: unknown; reason: string } }
      adminControls = adminControls.map((control) => control.key === body.draft.key ? { ...control, enabled: body.draft.enabled, value: body.draft.value, version: 1, updatedBy: session.principalId, updatedAt: '2026-08-23T09:00:00Z' } : control)
      const changed = adminControls.find((control) => control.key === body.draft.key)
      adminAudit.unshift({ eventId: 'admin-event-1', actorId: session.principalId, action: 'APPLY_CONTROL', resourceId: body.draft.key, outcome: 'SUCCESS', reason: body.draft.reason, evidence: { enabled: body.draft.enabled }, occurredAt: '2026-08-23T09:00:00Z' })
      return route.fulfill({ json: changed })
    }
    return route.fulfill({ json: adminControls })
  })
  await page.route('**/api/v1/admin/audit**', (route) => route.fulfill({ json: adminAudit }))
  await page.route('**/api/v1/announcements**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/operational-controls**', (route) => route.fulfill({ json: [] }))
  await page.route('**/api/v1/feature-flags**', (route) => route.fulfill({ json: [{ id: 'flag-1', key: 'editor-v2', scope: 'TENANT', enabled: true, tenant_id: 'default', namespace: null, description: 'New editor rollout', version: 2, updated_by: session.principalId, updated_at: '2026-08-23T08:00:00Z' }] }))
  await page.route('**/api/v1/configuration**', (route) => route.fulfill({ json: { schema_version: 1, version: 7, fingerprint: 'abcdef0123456789abcdef0123456789', loaded_at: '2026-08-23T08:00:00Z', precedence: ['defaults', 'environment'], entries: [{ name: 'database.url', value: 'postgresql://amesh', source: 'environment', reloadable: false, secret: false }, { name: 'object_storage_backend', value: 's3', source: 'environment', reloadable: false, secret: false }, { name: 'execution_runner_mode', value: 'local', source: 'environment', reloadable: false, secret: false }, { name: 'amesh.token_pepper', value: 'server-redacted', source: 'environment', reloadable: false, secret: true }], warnings: [] } }))
  await page.route('**/api/v1/operations/topology', (route) => route.fulfill({ json: { observedAt: '2026-08-23T09:00:00Z', currentVersion: '0.2.0', versionSkew: false, coordination: 'postgresql-leases', quorumDependencies: { objectStorage: 'ready' }, roles: [{ role: 'api', totalInstances: 1, liveInstances: 1, readyInstances: 1, drainingInstances: 0, staleInstances: 0, versions: ['0.2.0'], failoverStatus: 'READY' }, { role: 'executor', totalInstances: 1, liveInstances: 1, readyInstances: 1, drainingInstances: 0, staleInstances: 0, versions: ['0.2.0'], failoverStatus: 'READY' }], instances: [] } }))
  await page.route('**/api/v1/workers', (route) => route.fulfill({ json: [{ worker_id: 'worker-1', worker_group: 'local', instance_name: 'executor-1', version: '0.2.0', status: 'ACTIVE', liveness: 'LIVE', compatibility: 'COMPATIBLE', capacity: 4, claimed_work: 1, utilization: 0.25, last_heartbeat_at: '2026-08-23T09:00:00Z' }] }))
  await page.route('**/api/v1/admissions/diagnostics', (route) => route.fulfill({ json: { active_reservations: 1, queued_requests: 0, oldest_queue_age_seconds: 0, pressure_by_policy: {} } }))
  await page.route('**/api/v1/assets**', (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path.endsWith('/export/openlineage')) return route.fulfill({ body: JSON.stringify({ format: 'openlineage', generatedAt: '2026-08-23T09:03:00Z', producer: 'https://github.com/amesh-workflows/amesh', events: [] }), contentType: 'application/json' })
    if (path === '/api/v1/assets' && request.method() === 'POST') {
      const draft = request.postDataJSON() as Record<string, unknown>
      const created = { ...draft, tenantId: 'default', resourceVersion: 1, createdBy: session.principalId, updatedBy: session.principalId, createdAt: '2026-08-23T09:04:00Z', updatedAt: '2026-08-23T09:04:00Z' }
      assetRecords = [...assetRecords, created as typeof catalogAssets[number]]
      return route.fulfill({ status: 201, json: created })
    }
    if (path === '/api/v1/assets') return route.fulfill({ json: assetRecords })
    const assetId = path.split('/').at(-1)
    const asset = assetRecords.find((item) => item.assetId === assetId) || assetRecords[0]
    const source = assetRecords[0]
    const target = assetRecords[1]
    const isTarget = asset.assetId === target.assetId
    return route.fulfill({ json: {
      asset,
      upstream: isTarget ? [source] : [],
      downstream: asset.assetId === source.assetId ? [target] : [],
      observations: asset.assetId === source.assetId
        ? [{ observationId: '00000000-0000-7000-8000-000000000603', assetId: source.assetId, tenantId: 'default', namespace: 'team.data', accessMode: 'READ', evidenceKind: 'OBSERVED', confidence: 0.9, flowId: 'warehouse', executionId: executions[1].execution_id, taskRunId: null, artifactId: null, metadata: {}, observedAt: '2026-08-23T09:01:00Z', createdBy: 'plugin:warehouse' }]
        : isTarget ? [{ observationId: '00000000-0000-7000-8000-000000000604', assetId: target.assetId, tenantId: 'default', namespace: 'team.data', accessMode: 'WRITE', evidenceKind: 'OBSERVED', confidence: 1, flowId: 'warehouse', executionId: executions[1].execution_id, taskRunId: null, artifactId: '00000000-0000-7000-8000-000000000605', metadata: {}, observedAt: '2026-08-23T09:02:00Z', createdBy: 'plugin:warehouse' }] : [],
      edges: isTarget || asset.assetId === source.assetId ? [{ edgeId: '00000000-0000-7000-8000-000000000606', tenantId: 'default', namespace: 'team.data', upstreamAssetId: source.assetId, downstreamAssetId: target.assetId, evidenceKind: 'INFERRED', confidence: 0.8, flowId: 'warehouse', executionId: executions[1].execution_id, taskRunId: null, artifactId: null, metadata: {}, observedAt: '2026-08-23T09:02:00Z', createdBy: 'plugin:warehouse' }] : [],
    } })
  })
  await page.route('**/api/v1/dashboards', (route) => route.fulfill({ json: customDashboard ? [...dashboardDefinitions, customDashboard] : dashboardDefinitions }))
  await page.route('**/api/v1/dashboards/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const dashboardId = decodeURIComponent(path.split('/')[4] || 'builtin.instance')
    if (path.endsWith('/render')) {
      const dashboard = customDashboard && customDashboard.dashboardId === dashboardId ? customDashboard : dashboardDefinitions.find((item) => item.dashboardId === dashboardId) || dashboardDefinitions[0]
      const widgets = (dashboard.widgets as Array<{ widgetId: string }>).map((widget) => ({ widgetId: widget.widgetId, result: widget.widgetId === 'executions'
        ? { columns: ['value'], rows: [{ value: 2 }], freshAt: '2026-08-21T12:01:00Z', partial: false, sampled: false, redacted: false, scannedRows: 2, limit: 100 }
        : widget.widgetId === 'states'
          ? { columns: ['state', 'value'], rows: [{ state: 'RUNNING', value: 1 }, { state: 'SUCCESS', value: 1 }], freshAt: '2026-08-21T12:01:00Z', partial: false, sampled: false, redacted: false, scannedRows: 2, limit: 100 }
          : widget.widgetId === 'activity'
            ? { columns: ['bucketStart', 'state', 'value'], rows: [{ bucketStart: '2026-08-21T11:00:00Z', state: 'SUCCESS', value: 1 }, { bucketStart: '2026-08-21T12:00:00Z', state: 'RUNNING', value: 1 }], freshAt: '2026-08-21T12:01:00Z', partial: false, sampled: false, redacted: false, scannedRows: 2, limit: 100 }
            : { columns: ['level', 'value'], rows: [{ level: 'INFO', value: 8 }, { level: 'ERROR', value: 1 }], freshAt: '2026-08-21T12:01:00Z', partial: true, sampled: true, redacted: false, scannedRows: 9, limit: 8 } }))
      return route.fulfill({ json: { dashboard, widgets, renderedAt: '2026-08-21T12:01:00Z' } })
    }
    if (path.endsWith('/export')) return route.fulfill({ body: `dashboardId: ${dashboardId}\n`, contentType: 'application/yaml' })
    if (request.method() === 'PUT') {
      const spec = request.postDataJSON() as Record<string, unknown>
      customDashboard = { dashboardId, tenantId: 'default', ...spec, version: 1, ownerId: session.principalId, builtin: false, createdAt: '2026-08-21T12:01:00Z', updatedAt: '2026-08-21T12:01:00Z' }
      return route.fulfill({ json: customDashboard })
    }
    if (request.method() === 'DELETE') { customDashboard = null; return route.fulfill({ status: 204 }) }
    return route.fulfill({ json: customDashboard || dashboardDefinitions[0] })
  })
  await page.route('**/api/v1/search**', (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path.endsWith('/status')) return route.fulfill({ json: { projectionVersion: 4, condition: 'READY', documentsIndexed: 42, sourceDocuments: 42, progress: 1, lastProjectedAt: '2026-08-21T12:01:00Z', latestSourceAt: '2026-08-21T12:01:00Z', lagSeconds: 0, rebuildStartedAt: null, rebuildCompletedAt: '2026-08-21T12:00:00Z', failures: 0, lastError: null } })
    if (path.endsWith('/rebuild')) return route.fulfill({ status: 202, json: { projectionVersion: 5, condition: 'REBUILDING', documentsIndexed: 0, sourceDocuments: 42, progress: 0, lastProjectedAt: '2026-08-21T12:01:00Z', latestSourceAt: '2026-08-21T12:01:00Z', lagSeconds: 0, rebuildStartedAt: '2026-08-21T12:02:00Z', rebuildCompletedAt: null, failures: 0, lastError: null } })
    const body = request.postDataJSON() as { cursor?: string; types?: string[] }
    if (body.types?.includes('AUDIT')) return route.fulfill({ json: { items: adminAudit.map((event) => ({ documentType: 'AUDIT', documentId: event.eventId, namespace: null, title: String(event.action), summary: String(event.reason), state: String(event.outcome), labels: {}, fields: { action: event.action, resourceType: 'administration_control', outcome: event.outcome }, occurredAt: event.occurredAt, updatedAt: event.occurredAt, sourceVersion: 1, relevance: 1 })), nextCursor: null, deniedTypes: [], projectionVersion: 4, projectionCondition: 'READY' } })
    if (body.cursor) return route.fulfill({ json: { items: [searchDocuments[1]], nextCursor: null, deniedTypes: ['AUDIT'], projectionVersion: 4, projectionCondition: 'READY' } })
    return route.fulfill({ json: { items: searchDocuments, nextCursor: 'search-page-2', deniedTypes: ['AUDIT'], projectionVersion: 4, projectionCondition: 'READY' } })
  })
  await page.route('**/api/v1/blueprints**', (route) => {
    const request = route.request()
    const url = new URL(request.url())
    if (url.pathname.endsWith('/instantiate')) {
      const body = request.postDataJSON() as { parameters: Record<string, string> }
      const document = `apiVersion: amesh.flow/v1\nid: ${body.parameters.flow_id}\nnamespace: ${body.parameters.namespace}\ndescription: Created from the built-in hello-world blueprint.\ntasks:\n- id: done\n  type: core.return\n  value: ${body.parameters.greeting}\n`
      return route.fulfill({ json: { blueprint: blueprints[0], document, validation: { valid: true, irVersion: 'amesh.flow/v1', semantic_hash: 'blueprint-hash', canonical: {}, issues: [] } } })
    }
    const parts = url.pathname.split('/').filter(Boolean)
    if (parts.length > 3) {
      const item = blueprints.find((blueprint) => blueprint.blueprintId === parts[3]) || blueprints[0]
      return route.fulfill({ json: item })
    }
    const source = url.searchParams.get('source')
    const query = (url.searchParams.get('q') || '').toLowerCase()
    return route.fulfill({ json: blueprints.filter((item) => (!source || item.source === source) && (!query || `${item.title} ${item.summary} ${item.tags.join(' ')}`.toLowerCase().includes(query))) })
  })
  await page.route('**/api/v1/playground/simulate', (route) => route.fulfill({ json: { expressionResult: 'Ada', redactedContext: { inputs: { name: 'Ada', apiToken: '[REDACTED]' } }, validation: { valid: true, irVersion: 'amesh.flow/v1', semantic_hash: 'playground-hash', canonical: {}, issues: [] }, steps: [{ taskId: 'done', taskType: 'core.return', dependencies: [], simulated: true, reason: 'deterministic local preview' }], safety: { persisted: false, executed: false, credentialAccess: false, infrastructureAccess: false }, compatibilityVersion: 'amesh.expr/v1' } }))
  await page.route('**/api/v1/flows', (route) => route.fulfill({ json: flows }))
  await page.route('**/api/v1/flows/editor/schema', (route) => route.fulfill({ json: {
    schemaVersion: 'amesh.flow-editor/v1',
    flowSchema: { type: 'object', properties: { id: { type: 'string' }, namespace: { type: 'string' }, tasks: { type: 'array' } } },
    resourceCatalog: { schemaVersion: 'amesh.resource-catalog/v1', resources: [{ type: 'core.return', kind: 'task', configurationSchema: { type: 'object', properties: { value: {} } }, editor: { title: 'Return', description: 'Return a value.', category: 'Core', propertyOrder: ['value'] } }] },
    expressionContext: { inputs: 'Validated flow inputs.' },
  } }))
  await page.route('**/api/v1/flows/validate', (route) => route.fulfill({ json: { valid: true, irVersion: 'amesh.flow/v1', semantic_hash: 'editor-hash', canonical: {}, issues: [] } }))
  await page.route('**/api/v1/executions?limit=200', (route) => route.fulfill({ json: executions }))
  await page.route('**/api/v1/triggers', (route) => route.fulfill({ json: triggers }))
  await page.route('**/api/v1/trigger-occurrences?limit=200', (route) => route.fulfill({ json: triggerOccurrences }))
  await page.route('**/api/v1/check-evaluations?*', (route) => route.fulfill({ json: checkEvaluations }))
  await page.route('**/api/v1/check-compliance?*', (route) => route.fulfill({ json: checkCompliance }))
  await page.route('**/api/v1/check-policies?*', (route) => route.fulfill({ json: checkPolicies }))
  await page.route('**/api/v1/plugin-registry/index', (route) => route.fulfill({ json: { schemaVersion: 'amesh.plugin-registry/v1', generatedAt: '2026-08-23T09:00:00Z', packages: [], signature: null } }))
  await page.route('**/api/v1/plugin-policy/effective**', (route) => route.fulfill({ json: { tenantId: 'default', namespace: null, defaultEffect: 'DENY', rules: [{ id: '00000000-0000-7000-8000-000000000505', tenantId: 'default', scope: 'TENANT', namespace: null, effect: 'ALLOW', stages: ['AUTHORING', 'VALIDATION', 'EXECUTION'], selector: { package: 'acme.reviewed', versionRange: '>=1.0.0,<2.0.0', vendor: 'Acme *', pluginTypes: [], capabilities: [] }, priority: 100, reason: 'Security review SEC-142', enabled: true, createdBy: session.principalId, createdAt: '2026-08-23T09:00:00Z', updatedBy: session.principalId, updatedAt: '2026-08-23T09:00:00Z' }], quarantines: [] } }))
  await page.route('**/api/v1/plugin-policy/quarantines/preview', (route) => route.fulfill({ json: { package: 'acme.reviewed', version: '1.4.0', affectedFlows: [{ namespace: 'team.data', flow_key: 'warehouse' }], runningExecutions: [] } }))
  await page.route('**/api/v1/namespaces/team.data/files', (route) => route.fulfill({ json: namespaceFiles }))
  await page.route('**/api/v1/namespaces/team.data/key-values', (route) => route.fulfill({ json: namespaceKeyValues }))
  await page.route('**/api/v1/namespaces/team.data/secret-bindings', (route) => route.fulfill({ json: namespaceSecrets }))
  const taskRun = { task_run_id: '00000000-0000-7000-8000-000000000201', execution_id: executions[0].execution_id, task_id: 'return', state: 'SUCCESS', current_attempt: 1, version: 2, retry_at: null, result: { value: 'cached' }, iteration_key: null, labels: {}, failure_category: null, lifecycle_phase: 'MAIN', evidence: { cache: { decision: 'HIT', reason: 'reused a matching result', keyHash: 'abc123', sourceExecutionId: executions[1].execution_id, sourceTaskRunId: '00000000-0000-7000-8000-000000000202', sourceAttempt: 1, expiresAt: '2026-08-21T13:00:00Z' } } }
  const evidence = [
    { cursor: 1, event_id: 'evidence-1', execution_id: executions[0].execution_id, task_run_id: null, kind: 'STATE', event_type: 'execution.executioncreated', payload: { entity: 'execution', eventType: 'ExecutionCreated', actorId: 'operator', reason: 'manual launch' }, occurred_at: '2026-08-21T12:00:00Z', ingested_at: '2026-08-21T12:00:00Z' },
    { cursor: 2, event_id: 'evidence-2', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'STATE', event_type: 'task.taskruncreated', payload: { entity: 'task', eventType: 'TaskRunCreated', actorId: 'executor', payload: {} }, occurred_at: '2026-08-21T12:00:01Z', ingested_at: '2026-08-21T12:00:01Z' },
    { cursor: 3, event_id: 'evidence-3', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'STATE', event_type: 'task.taskrunstarted', payload: { entity: 'task', eventType: 'TaskRunStarted', actorId: 'executor', payload: { workerGroup: 'local' } }, occurred_at: '2026-08-21T12:00:02Z', ingested_at: '2026-08-21T12:00:02Z' },
    { cursor: 4, event_id: 'evidence-4', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'LOG', event_type: 'log.info', payload: { level: 'INFO', attempt: 1, workerId: 'worker-local', message: 'returned cached value', fields: { cache: 'hit' } }, occurred_at: '2026-08-21T12:00:03Z', ingested_at: '2026-08-21T12:00:03Z' },
    { cursor: 5, event_id: 'evidence-5', execution_id: executions[0].execution_id, task_run_id: taskRun.task_run_id, kind: 'STATE', event_type: 'task.taskrunsucceeded', payload: { entity: 'task', eventType: 'TaskRunSucceeded', actorId: 'executor', payload: {} }, occurred_at: '2026-08-21T12:00:04Z', ingested_at: '2026-08-21T12:00:04Z' },
  ]
  await page.route('**/api/v1/executions/**', (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path.endsWith('/graph')) return route.fulfill({ json: { namespace: 'examples.engine', flowId: 'hello_world', revision: 3, nodes: [{ taskId: 'return', label: 'return', taskType: 'core.return', order: 0, depth: 0, parentId: null, dependencies: [], children: [], mode: null, failurePolicy: 'FAIL_FAST', maxConcurrency: null, state: 'SUCCESS', result: { value: 'cached' }, iterationCount: null, lifecyclePhase: 'MAIN', handlerOwnerId: null }], edges: [] } })
    if (path.endsWith('/evidence')) return route.fulfill({ json: { items: evidence, nextCursor: 'cursor-5' } })
    if (path.endsWith('/evidence/stream')) return route.fulfill({ body: '', contentType: 'application/x-ndjson' })
    if (path.endsWith('/files')) return route.fulfill({ json: [] })
    if (path.endsWith('/subflows')) return route.fulfill({ json: [] })
    if (path.endsWith('/parent-subflow')) return route.fulfill({ json: null })
    if (path.endsWith('/interventions/preview')) return route.fulfill({ json: { execution_id: executions[0].execution_id, action: 'PAUSE', current_state: 'RUNNING', predicted_state: 'PAUSED', current_version: 2, current_epoch: 1, checkpoint_task_id: null, impacted_task_ids: ['return'], preserved_task_ids: [], invalidates_active_claims: false, destructive: false, force_available_at: null, consequences: ['new task claims stop'] } })
    if (path.endsWith('/interventions')) return route.fulfill({ json: request.method() === 'GET' ? [] : { execution: executions[0], taskRuns: [taskRun], taskRunSummary: { total: 1, waiting: 0, running: 0, retry_delay: 0, succeeded: 1, failed: 0, cancelled: 0 }, taskRunOffset: 0 } })
    return route.fulfill({ json: { execution: executions[0], taskRuns: [taskRun], taskRunSummary: { total: 1, waiting: 0, running: 0, retry_delay: 0, succeeded: 1, failed: 0, cancelled: 0 }, taskRunOffset: 0 } })
  })
  await page.route('**/api/v1/backfills/preview', (route) => route.fulfill({ json: { selectionKind: 'REPLAY', executionCount: 1, estimatedTaskRuns: 1, estimatedCostUnits: 1, idempotencyKeyTemplate: 'replay:{sourceExecutionId}', warnings: [] } }))
  await page.route('**/api/v1/backfills', (route) => route.fulfill({ json: { backfillId: 'backfill-1', state: 'RUNNING', total: 1 } }))
}

async function connect(page: Page) {
  await page.goto('/')
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill('test-token')
  await page.getByRole('button', { name: 'Open control room' }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
}

test.beforeEach(async ({ page }) => {
  await mockApi(page)
})

test('routes local, redirect and directory identity providers before login', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop identity routing acceptance')
  await page.goto('/')
  const providers = page.locator('.identity-provider-list')
  await expect(providers.getByRole('button', { name: 'Local account', exact: true })).toBeVisible()
  await expect(providers.getByRole('button', { name: 'Continue with Corporate OIDC' })).toBeVisible()
  await expect(providers.getByRole('button', { name: 'Corporate directory' })).toBeVisible()
  await page.getByLabel('User handle').fill('ada@example.com')
  await providers.getByRole('button', { name: 'Corporate directory' }).click()
  await expect(providers.getByRole('button', { name: 'Corporate directory' })).toHaveAttribute('aria-pressed', 'true')
})

test('connects, navigates resources, preserves deep links and opens the command palette', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop interaction acceptance')
  await connect(page)
  await expect(page.getByText('2', { exact: true }).first()).toBeVisible()
  await page.getByRole('link', { name: 'Executions' }).click()
  await expect(page).toHaveURL(/\/executions$/)
  await page.getByRole('link', { name: '…0101' }).click()
  await expect(page.getByRole('heading', { name: 'hello_world' })).toBeVisible()

  await page.reload()
  await expect(page.getByRole('heading', { name: 'Task runs' })).toBeVisible()
  await page.getByRole('button', { name: 'Data' }).click()
  await expect(page.getByText('Selected results and cache')).toBeVisible()
  await page.getByText('return · attempt 1').click()
  await expect(page.getByText('reused a matching result')).toBeVisible()
  await page.getByRole('button', { name: 'Logs' }).click()
  await expect(page.getByText('returned cached value')).toBeVisible()
  await page.getByLabel('Level').selectOption('INFO')
  await expect(page).toHaveURL(/view=logs.*level=INFO|level=INFO.*view=logs/)
  await page.getByRole('button', { name: 'Gantt' }).click()
  await expect(page.getByRole('heading', { name: 'Queue, wait and runner Gantt' })).toBeVisible()
  await page.getByRole('button', { name: 'History' }).click()
  await expect(page.getByText('ExecutionCreated')).toBeVisible()
  await page.getByRole('button', { name: 'Pause' }).click()
  await expect(page.getByRole('dialog', { name: /Confirm pause/ })).toBeVisible()
  await expect(page.getByText('new task claims stop')).toBeVisible()
  await page.getByRole('dialog', { name: /Confirm pause/ }).getByRole('button', { name: 'Cancel' }).click()
  await page.keyboard.press('Control+K')
  await expect(page.getByRole('dialog', { name: 'Global command menu' })).toBeVisible()
  await page.locator('[cmdk-input]').fill('Flows')
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(/\/flows$/)

  if (testInfo.project.name === 'chromium') {
    await page.screenshot({ path: 'test-results/dashboard-shell.png', fullPage: true })
  }
})

test('filters, creates, permissions and exports typed dashboards', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop dashboard authoring acceptance')
  await connect(page)
  await expect(page.getByRole('heading', { name: 'Instance overview' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Execution states' })).toBeVisible()
  await expect(page.getByText('Partial · limit 8')).toBeVisible()
  await expect(page.getByText('Sampled 25%')).toBeVisible()

  const renderRequest = page.waitForRequest((request) => request.url().includes('/builtin.instance/render') && request.method() === 'POST' && request.postData()?.includes('examples.engine') === true)
  await page.getByRole('textbox', { name: 'Namespace' }).fill('examples.engine')
  await page.getByRole('button', { name: 'Apply' }).click()
  await renderRequest

  await page.getByRole('button', { name: 'Create dashboard' }).click()
  const editor = page.getByRole('dialog', { name: 'Create dashboard' })
  await editor.getByLabel('Dashboard ID').fill('ops.team')
  await editor.getByLabel('Title', { exact: true }).fill('Team operations')
  await editor.getByLabel('Visibility').selectOption('TENANT')
  await editor.getByLabel('Viewer IDs').fill('viewer-a')
  await editor.getByLabel('Editor IDs').fill('editor-a')
  await editor.getByRole('button', { name: 'Save dashboard' }).click()
  await expect(page).toHaveURL(/dashboard=ops.team/)
  await expect(page.getByRole('heading', { name: 'Team operations' })).toBeVisible()
  const download = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export' }).click()
  expect((await download).suggestedFilename()).toBe('ops.team.yaml')
})

test('searches, filters, paginates and rebuilds the tenant projection', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop structured-search acceptance')
  await connect(page)
  await page.keyboard.press('Control+K')
  await page.locator('[cmdk-input]').fill('diagnostic')
  await expect(page.getByText('ERROR · task.return')).toBeVisible()
  await page.getByText('View all indexed results').click()
  await expect(page).toHaveURL(/\/search\?q=diagnostic/)
  await expect(page.getByRole('heading', { name: 'Search' })).toBeVisible()
  await expect(page.getByText('READY · projection v4')).toBeVisible()
  await expect(page.getByText('examples.engine.hello_world')).toBeVisible()

  const filtered = page.waitForRequest((request) => request.url().endsWith('/api/v1/search') && request.method() === 'POST' && request.postData()?.includes('examples.engine') === true && request.postData()?.includes('team') === true)
  await page.getByRole('textbox', { name: 'Namespace' }).fill('examples.engine')
  await page.getByLabel('Labels').fill('team=platform')
  await page.getByLabel('Field', { exact: true }).selectOption('level')
  await page.getByLabel('Field value', { exact: true }).fill('ERROR')
  await page.getByRole('button', { name: 'Search projection' }).click()
  await filtered
  await expect(page.getByText(/Not searched: Audit/)).toBeVisible()

  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByText('diagnostic needle appeared')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Previous' })).toBeEnabled()

  page.once('dialog', (dialog) => void dialog.accept())
  await page.getByRole('button', { name: 'Rebuild index' }).click()
  await expect(page.getByText(/Rebuild accepted/)).toBeVisible()
})

test('uses server permissions for navigation and direct routes', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop policy acceptance')
  await connect(page)
  const administration = page.locator('.rail-link-disabled').filter({ hasText: 'Administration' })
  await expect(administration).toHaveAttribute('aria-disabled', 'true')
  await page.goto('/administration')
  await expect(page.getByRole('heading', { name: 'Permission required' })).toBeVisible()
})

test('discovers lineage evidence, declares assets and exports OpenLineage', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop asset-catalog acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Assets' }).click()
  await expect(page.getByRole('heading', { name: 'Asset catalog' })).toBeVisible()
  await expect(page.getByText('Raw orders', { exact: true }).first()).toBeVisible()
  await page.getByPlaceholder('Filter provider, key, owner or tag').fill('gold')
  await page.getByText('Curated orders', { exact: true }).first().click()
  await expect(page.getByRole('heading', { name: 'Curated orders' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Upstream' }).locator('..').getByText('Raw orders')).toBeVisible()
  await expect(page.getByText('observed · confidence 1.00 · artifact linked')).toBeVisible()

  await page.getByRole('button', { name: 'Declare asset' }).click()
  await expect(page.getByRole('heading', { name: 'Register an asset' })).toBeVisible()
  await page.getByLabel('Provider').fill('s3')
  await page.getByLabel('Location').fill('minio:9000/amesh')
  await page.getByLabel('Stable external key').fill('reports/orders.parquet')
  await page.getByLabel('Display name').fill('Orders report')
  await page.getByRole('button', { name: 'Save declaration' }).click()
  await expect(page.getByText('Asset declaration saved.')).toBeVisible()

  const download = page.waitForEvent('download')
  await page.getByRole('button', { name: 'OpenLineage' }).click()
  expect((await download).suggestedFilename()).toBe('amesh-openlineage-default.json')
})

test('explains plugin policy and previews emergency disable before mutation', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop plugin-governance acceptance')
  await page.unroute('**/api/v1/ui/session**')
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: { ...session, capabilities: { ...session.capabilities, 'administration.manage': true } } }))
  await connect(page)
  await page.getByRole('link', { name: 'Plugins' }).click()
  await expect(page.getByRole('heading', { name: 'Effective plugin policy' })).toBeVisible()
  await expect(page.getByText('Security review SEC-142')).toBeVisible()
  await expect(page.locator('.policy-summary strong')).toHaveText('DENY')
  const emergency = page.getByRole('heading', { name: 'Emergency version disable' }).locator('..')
  await emergency.getByLabel('Package').fill('acme.reviewed')
  await emergency.getByLabel('Exact version').fill('1.4.0')
  await emergency.getByLabel('Reason').fill('security incident')
  await emergency.getByRole('button', { name: 'Preview impact' }).click()
  await expect(emergency.getByText('1 flow revisions')).toBeVisible()
  await expect(emergency.getByRole('button', { name: 'Confirm disable' })).toBeVisible()
})

test('administers tenant controls with preview, redaction and audit evidence', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop administration acceptance')
  await page.unroute('**/api/v1/ui/session**')
  await page.route('**/api/v1/ui/session**', (route) => route.fulfill({ json: { ...session, capabilities: { ...session.capabilities, 'administration.manage': true } } }))
  await connect(page)

  await page.getByRole('link', { name: 'Administration' }).click()
  await expect(page.getByRole('heading', { name: 'Administration' })).toBeVisible()
  await page.getByRole('button', { name: 'Operations' }).click()
  await expect(page.getByText('PostgreSQL', { exact: true })).toBeVisible()
  await expect(page.getByText('44/44 migrations')).toBeVisible()

  await page.getByRole('button', { name: 'Controls' }).click()
  const killSwitch = page.locator('.admin-control-grid article').filter({ hasText: 'Execution kill switch' })
  await killSwitch.getByRole('button', { name: 'Preview change' }).click()
  const draft = page.locator('.admin-panel').filter({ hasText: 'DRAFT' })
  await draft.getByRole('checkbox').check()
  await draft.getByLabel('Reason').fill('incident containment exercise')
  await draft.getByRole('button', { name: 'Generate impact preview' }).click()
  const dialog = page.getByRole('dialog', { name: 'Confirm Execution kill switch' })
  await expect(dialog.getByText('Stop new execution admission for this tenant.')).toBeVisible()
  await dialog.getByLabel(/Type APPLY KILL_SWITCH/).fill('APPLY KILL_SWITCH')
  await dialog.getByRole('button', { name: 'Apply guarded change' }).click()
  await expect(page.getByText('Administrative control applied and audited')).toBeVisible()

  await page.getByRole('button', { name: 'Configuration' }).click()
  await expect(page.getByText('Configuration version 7')).toBeVisible()
  await expect(page.getByText('[REDACTED]')).toBeVisible()
  await expect(page.getByText('server-redacted', { exact: true })).toHaveCount(0)

  await page.getByRole('button', { name: 'Audit' }).click()
  await expect(page.getByText('incident containment exercise').first()).toBeVisible()
  await expect(page.getByText('SUCCESS').first()).toBeVisible()
  const findings = await new AxeBuilder({ page }).analyze()
  expect(findings.violations.filter((item) => ['critical', 'serious'].includes(item.impact || ''))).toEqual([])
})

test('previews blueprints, opens an unsaved draft and isolates playground work', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop blueprint workbench acceptance')
  const executionRequests: string[] = []
  page.on('request', (request) => {
    if (request.method() === 'POST' && new URL(request.url()).pathname === '/api/v1/executions') {
      executionRequests.push(request.url())
    }
  })
  await connect(page)

  await page.locator('.app-rail').getByRole('link', { name: 'Blueprints' }).click()
  await expect(page.getByRole('heading', { name: 'Blueprints' })).toBeVisible()
  await expect(page.getByText('Hello, workflow', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('Organization readiness marker', { exact: true })).toBeVisible()
  await expect(page.getByText('Community batch loop', { exact: true })).toBeVisible()
  await page.getByLabel('Catalog source').selectOption('COMMUNITY')
  await expect(page.getByText('Community batch loop', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('Hello, workflow', { exact: true })).toHaveCount(0)
  await page.getByLabel('Catalog source').selectOption('ALL')
  await page.getByText('Hello, workflow', { exact: true }).first().click()
  await page.getByRole('button', { name: 'Open unsaved draft' }).click()

  await expect(page).toHaveURL(/\/flows\/new\?.*blueprint=hello-world/)
  await expect(page.getByRole('heading', { name: 'Draft hello_blueprint' })).toBeVisible()
  await expect(page.getByText(/loaded as an unsaved draft\. Nothing has run/)).toBeVisible()
  await page.getByRole('tab', { name: 'YAML' }).click()
  await expect(page.getByText('Created from the built-in hello-world blueprint.')).toBeVisible()
  expect(executionRequests).toEqual([])

  page.once('dialog', (dialog) => void dialog.accept())
  await page.locator('#main-content').getByRole('link', { name: 'Blueprints' }).click()
  await page.getByRole('tab', { name: 'Playground' }).click()
  await page.getByRole('button', { name: 'Validate and simulate' }).click()
  await expect(page.locator('.playground-safety article').filter({ hasText: 'persisted' })).toContainText('No')
  await expect(page.locator('.playground-safety article').filter({ hasText: 'credential access' })).toContainText('No')
  await expect(page.getByText('deterministic local preview')).toBeVisible()

  await page.getByRole('tab', { name: 'Setup guide' }).click()
  await expect(page.getByText('4 / 4 ready')).toBeVisible()
  await page.getByText('Start the local stack').click()
  await expect(page.getByText('1 / 4', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByText('1 / 4', { exact: true })).toBeVisible()
  const findings = await new AxeBuilder({ page }).analyze()
  expect(findings.violations.filter((item) => ['critical', 'serious'].includes(item.impact || ''))).toEqual([])
})

test('shows live trigger health and durable occurrence evidence', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop trigger monitor acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Triggers' }).click()
  await expect(page.getByRole('heading', { name: 'Trigger runtime' })).toBeVisible()
  await expect(page.getByText('every_minute').first()).toBeVisible()
  await expect(page.getByText('occurrence launched execution')).toBeVisible()
  await expect(page.getByText('scheduled occurrence created an execution')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Execution', exact: true })).toBeVisible()
})

test('shows check compliance, evaluation evidence and reusable policies', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop check monitor acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Checks' }).click()
  await expect(page.getByRole('heading', { name: 'Execution checks' })).toBeVisible()
  await expect(page.getByText('examples.agent.luna_research', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('research-output')).toBeVisible()
  await expect(page.getByText('expression evaluated true')).toBeVisible()
  await expect(page.getByText('interactive-start')).toBeVisible()
})

test('renders namespace files, typed values and secret references', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop namespace-resource acceptance')
  await page.addInitScript(() => localStorage.setItem('amesh.ui.settings.v1', JSON.stringify({ tenant: 'default', namespace: 'team.data', locale: 'en', timezone: 'UTC', savedViews: [], authenticationMode: 'token' })))
  await connect(page)
  await page.getByRole('link', { name: 'Namespaces' }).click()
  await expect(page.getByRole('heading', { name: 'team.data' })).toBeVisible()
  await expect(page.getByRole('row', { name: 'config/rules.json' })).toBeVisible()
  await expect(page.getByText('release.channel')).toBeVisible()
  await expect(page.getByText('PRODUCTION_API_KEY')).toBeVisible()
  await expect(page.getByText('References only')).toBeVisible()
})

test('switches locale and has no critical or serious automated accessibility findings', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop accessibility acceptance')
  await connect(page)
  await page.getByLabel('Language').selectOption('zh-CN')
  await expect(page.getByRole('heading', { name: '仪表板' })).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN')
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
  await page.keyboard.press('Tab')
  await expect(page.getByRole('link', { name: '跳至主要内容' })).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('main')).toBeFocused()
  await expect(page.getByRole('navigation')).toBeAttached()
  await expect(page.getByRole('complementary', { name: 'Primary' })).toBeAttached()

  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()
  expect(results.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))).toEqual([])
})

test('recovers a failed data view and makes no external requests', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop recovery acceptance')
  const origins = new Set<string>()
  page.on('request', (request) => origins.add(new URL(request.url()).origin))
  let attempts = 0
  await page.unroute('**/api/v1/flows')
  await page.route('**/api/v1/flows', (route) => {
    attempts += 1
    if (attempts <= 2) void route.fulfill({ status: 503, json: { detail: 'control plane unavailable' } })
    else void route.fulfill({ json: flows })
  })
  await connect(page)
  await page.getByRole('link', { name: 'Flows' }).click()
  await expect(page.getByRole('heading', { name: 'Unable to load this view' })).toBeVisible()
  await page.getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByText('hello_world')).toBeVisible()
  expect([...origins]).toEqual(['http://127.0.0.1:4173'])
})

test('uses the accessible compact navigation rail on tablet', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'tablet', 'tablet-only responsive acceptance')
  await connect(page)
  const rail = page.getByRole('complementary', { name: 'Primary' })
  await expect(rail).toBeVisible()
  expect((await rail.boundingBox())?.width).toBe(76)
  await page.getByRole('link', { name: 'Flows' }).click()
  await expect(page).toHaveURL(/\/flows$/)
})

test('authors a flow visually and falls back to the accessible YAML workbench', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'tablet', 'desktop editor acceptance')
  await connect(page)
  await page.getByRole('link', { name: 'Flows' }).click()
  await page.getByRole('link', { name: 'Create flow' }).click()
  await expect(page.getByRole('heading', { name: 'Create flow' })).toBeVisible()
  await expect(page.getByLabel('Interactive workflow topology')).toBeVisible()
  await expect(page.getByLabel('Workflow mini map')).toBeVisible()
  await expect(page.locator('.visual-task-node').filter({ hasText: 'done' })).toBeVisible()
  await page.getByLabel('Task ID').fill('follow_up')
  await page.getByRole('button', { name: 'Add task' }).click()
  await expect(page.getByLabel('Generated YAML change review')).toContainText('GENERATED YAML')
  await page.getByRole('button', { name: 'Accept change' }).click()
  const followUp = page.locator('.visual-task-node').filter({ hasText: 'follow_up' })
  await expect(followUp).toBeVisible()
  await followUp.click()
  const visualInspector = page.getByRole('complementary', { name: 'Visual task inspector' })
  await visualInspector.getByLabel('value', { exact: true }).fill('"configured"')
  await visualInspector.getByRole('button', { name: 'Stage configuration' }).click()
  await page.getByRole('button', { name: 'Accept change' }).click()
  await visualInspector.getByRole('button', { name: 'Stage removal' }).click()
  await expect(page.getByLabel('Generated YAML change review')).toContainText('LOSSY TRANSFORMATION')
  await page.getByRole('button', { name: 'Cancel' }).click()
  await page.getByRole('tab', { name: 'YAML' }).click()
  const source = page.getByLabel('Flow YAML source')
  await expect(source).toBeVisible()
  await expect(page.getByRole('button', { name: 'Format' })).toBeEnabled()
  await source.click()
  await page.keyboard.press('Control+End')
  await page.keyboard.type('\ndescription: browser acceptance')
  await expect(page.getByRole('button', { name: 'Save' })).toBeEnabled()
  await expect.poll(() => page.evaluate(() => Object.keys(localStorage).some((key) => key.startsWith('amesh.flow-draft.v1:')))).toBe(true)
  page.once('dialog', async (dialog) => {
    expect(dialog.message()).toContain('Discard unsaved changes')
    await dialog.dismiss()
  })
  await page.locator('.back-link').click()
  await expect(page.getByRole('heading', { name: 'Create flow' })).toBeVisible()
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
    .analyze()
  expect(results.violations.filter((violation) => ['critical', 'serious'].includes(violation.impact || ''))).toEqual([])
})
