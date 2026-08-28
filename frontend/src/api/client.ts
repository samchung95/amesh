import type {
  AdmissionPolicyDecision,
  AdmissionPolicyDocument,
  AdmissionPolicyRevision,
  AdministrationAuditEntry,
  AssetCatalogEntry,
  AssetDraft,
  AssetRecord,
  AdministrationControl,
  AdministrationControlDraft,
  AdministrationImpactPreview,
  AgentCapabilityPin,
  AgentCapabilityCatalog,
  AgentEnvelopePreview,
  AgentMcpConnectionSpec,
  AgentMcpConnectionTestResult,
  AgentMcpDiscoveryResult,
  AgentMcpConnectionRevision,
  AgentMcpToolCatalogEntry,
  AgentResourceKind,
  AgentResourceRevision,
  AgentResourceSpec,
  AgentRevisionComparison,
  AgentSessionDetailPage,
  AgentSessionSummary,
  ArtifactRef,
  Announcement,
  AnnouncementDraft,
  AdmissionDiagnostics,
  CheckComplianceSummary,
  DashboardDefinition,
  DashboardFilters,
  DashboardQuery,
  DashboardQueryResult,
  DashboardRender,
  DashboardSpec,
  CheckEvaluation,
  BackfillPreview,
  BackfillRecord,
  BackfillSpec,
  BlueprintCatalogSource,
  BlueprintDefinition,
  BlueprintDraftResponse,
  BlueprintSummary,
  ExecutionArtifact,
  ExecutionDetail,
  ExecutionEvidencePage,
  ExecutionEvidenceStreamEvent,
  ExecutionInterventionAction,
  ExecutionInterventionPreview,
  ExecutionInterventionRecord,
  ExecutionRunner,
  FlowDataContract,
  FlowDocumentExport,
  FlowEditorSchema,
  FlowFormatResponse,
  FlowMetadata,
  HumanTask,
  HumanTaskActionKind,
  HumanTaskNotification,
  AuthenticationProvider,
  ConfigurationSnapshot,
  CredentialMetadata,
  FeatureFlag,
  FlowGraph,
  FlowRevisionDiff,
  FlowRevisionRecord,
  FlowTestDefinition,
  FlowTestDefinitionDraft,
  FlowTestQualityGate,
  FlowTestRunResult,
  FlowValidationResult,
  HealthResponse,
  LoginResponse,
  ExpressionPreviewResponse,
  NamespaceCheckPolicy,
  OperationalControl,
  OperationalControlAction,
  OperationalControlDraft,
  OperationalControlEvent,
  NamespaceFile,
  NamespaceFileVersion,
  NamespaceWorkflowMetadataView,
  NetworkDiagnosticBundle,
  EffectivePluginPolicy,
  PluginPolicyImpactPreview,
  PluginPolicyRule,
  PluginPolicyRuleDraft,
  PluginQuarantine,
  PluginQuarantineDraft,
  PluginRegistryIndex,
  KeyValueEntry,
  KeyValueType,
  LifecycleJob,
  LifecycleLegalHold,
  LifecycleLegalHoldDraft,
  LifecyclePolicy,
  LifecyclePolicyDraft,
  PersistedEventMigration,
  PersistedExecution,
  PersistedFlow,
  PersistedSubflow,
  PlaygroundSimulationResponse,
  PrincipalDefinition,
  ReadinessResponse,
  PromotionGate,
  PromotionTargetKind,
  ReleaseActionResult,
  ReleaseHistoryEntry,
  ReleaseTarget,
  RoleBinding,
  RoleDefinition,
  SecretBinding,
  SearchProjectionStatus,
  SearchProjectionVerification,
  SearchRequest,
  SearchResponse,
  ServiceTopology,
  SimulationPlan,
  TriggerOccurrence,
  TriggerRuntimeState,
  UiSession,
  UpgradePolicy,
  UpgradeReport,
  WorkerInventory,
  WorkflowApp,
  IssuedCredential,
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

  async function requestBlob(path: string): Promise<Blob> {
    const headers = new Headers()
    if (connection.token) headers.set('Authorization', `Bearer ${connection.token}`)
    headers.set('X-Amesh-Tenant', connection.tenant)
    const response = await fetch(path, { credentials: 'same-origin', headers })
    if (!response.ok) throw new ApiError(response.status, await readError(response))
    return response.blob()
  }

  async function streamNdjson<T>(
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
  }

  const namespaceRoot = (namespace: string) =>
    `/api/v1/namespaces/${encodeURIComponent(namespace)}`
  const filePath = (namespace: string, path: string) =>
    `${namespaceRoot(namespace)}/files/${path.split('/').map(encodeURIComponent).join('/')}`

  return {
    health: async () => request<HealthResponse>('/health'),
    readiness: async () => request<ReadinessResponse>('/ready'),
    providers: async () => request<AuthenticationProvider[]>('/api/v1/auth/providers'),
    routedProviders: async (identifier?: string, tenant?: string) => {
      const params = new URLSearchParams()
      if (identifier) params.set('identifier', identifier)
      if (tenant) params.set('tenant', tenant)
      const suffix = params.size ? `?${params.toString()}` : ''
      return request<AuthenticationProvider[]>(`/api/v1/auth/providers${suffix}`)
    },
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
    apps: async (namespace?: string) =>
      request<WorkflowApp[]>(`/api/v1/apps${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    app: async (namespace: string, appId: string) =>
      request<WorkflowApp>(`/api/v1/apps/${encodeURIComponent(namespace)}/${encodeURIComponent(appId)}`),
    launchApp: async (namespace: string, appId: string, inputs: Record<string, unknown>) =>
      request<ExecutionDetail>(`/api/v1/apps/${encodeURIComponent(namespace)}/${encodeURIComponent(appId)}/launch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputs, idempotencyKey: crypto.randomUUID() }),
      }),
    humanTasks: async (namespace?: string, includeClosed = false) => {
      const params = new URLSearchParams({ includeClosed: String(includeClosed) })
      if (namespace) params.set('namespace', namespace)
      return request<HumanTask[]>(`/api/v1/human-tasks?${params.toString()}`)
    },
    actOnHumanTask: async (
      humanTaskId: string,
      action: HumanTaskActionKind,
      payload: { reason?: string; formValues?: Record<string, unknown>; comment?: string; artifactUri?: string },
    ) => request<HumanTask>(`/api/v1/human-tasks/${encodeURIComponent(humanTaskId)}/actions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, idempotencyKey: crypto.randomUUID(), ...payload }),
    }),
    humanTaskNotifications: async () =>
      request<HumanTaskNotification[]>('/api/v1/human-task-notifications'),
    assets: async (namespace?: string) =>
      request<AssetRecord[]>(`/api/v1/assets${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    asset: async (assetId: string) =>
      request<AssetCatalogEntry>(`/api/v1/assets/${encodeURIComponent(assetId)}`),
    registerAsset: async (draft: AssetDraft) =>
      request<AssetRecord>('/api/v1/assets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    exportAssetCatalog: async (namespace?: string) =>
      requestBlob(`/api/v1/assets/export/openlineage${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    principals: async () => request<PrincipalDefinition[]>('/api/v1/admin/principals'),
    createPrincipal: async (principalType: PrincipalDefinition['principal_type'], handle: string, displayName: string) =>
      request<PrincipalDefinition>('/api/v1/admin/principals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ principal_type: principalType, handle, display_name: displayName }),
      }),
    addGroupMember: async (groupId: string, memberId: string) =>
      request<void>(`/api/v1/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(memberId)}`, { method: 'PUT' }),
    removeGroupMember: async (groupId: string, memberId: string) =>
      request<void>(`/api/v1/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(memberId)}`, { method: 'DELETE' }),
    roles: async () => request<RoleDefinition[]>('/api/v1/admin/roles'),
    saveRole: async (name: string, displayName: string, description: string, permissions: RoleDefinition['permissions']) =>
      request<RoleDefinition>(`/api/v1/admin/roles/${encodeURIComponent(name)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, display_name: displayName, description, permissions }),
      }),
    bindings: async () => request<RoleBinding[]>('/api/v1/admin/bindings'),
    createBinding: async (binding: Omit<RoleBinding, 'id'>) =>
      request<RoleBinding>('/api/v1/admin/bindings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(binding),
      }),
    principalCredentials: async (principalId: string) =>
      request<CredentialMetadata[]>(`/api/v1/admin/principals/${encodeURIComponent(principalId)}/credentials`),
    createCredential: async (principalId: string, name: string, scopes: string[], expiresAt: string) =>
      request<IssuedCredential>(`/api/v1/admin/principals/${encodeURIComponent(principalId)}/credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, scopes, expiresAt, audience: 'amesh-api', rateLimitPerMinute: 600 }),
      }),
    topology: async () => request<ServiceTopology>('/api/v1/operations/topology'),
    workers: async () => request<WorkerInventory[]>('/api/v1/workers'),
    admissionDiagnostics: async () => request<AdmissionDiagnostics>('/api/v1/admissions/diagnostics'),
    networkDiagnostics: async () => request<NetworkDiagnosticBundle>('/api/v1/operations/network-diagnostics'),
    configuration: async () => request<ConfigurationSnapshot>('/api/v1/configuration'),
    reloadConfiguration: async () => request<ConfigurationSnapshot>('/api/v1/configuration/reload', { method: 'POST' }),
    featureFlags: async () => {
      const suffix = connection.namespace ? `?namespace=${encodeURIComponent(connection.namespace)}` : ''
      return request<FeatureFlag[]>(`/api/v1/feature-flags${suffix}`)
    },
    saveFeatureFlag: async (key: string, enabled: boolean, description: string, expectedVersion?: number) =>
      request<FeatureFlag>(`/api/v1/feature-flags/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scope: connection.namespace ? 'NAMESPACE' : 'TENANT',
          enabled,
          tenantId: connection.tenant,
          namespace: connection.namespace || null,
          description,
          expectedVersion: expectedVersion || null,
        }),
      }),
    administrationControls: async () => request<AdministrationControl[]>('/api/v1/admin/controls'),
    previewAdministrationControl: async (draft: AdministrationControlDraft) =>
      request<AdministrationImpactPreview>('/api/v1/admin/controls/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    applyAdministrationControl: async (preview: AdministrationImpactPreview, confirmation: string) =>
      request<AdministrationControl>(`/api/v1/admin/controls/${preview.draft.key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft: preview.draft, approval: preview.approval, confirmation }),
      }),
    administrationAudit: async () => request<AdministrationAuditEntry[]>('/api/v1/admin/audit?limit=200'),
    announcements: async (namespace?: string, includeInactive = false) => {
      const params = new URLSearchParams()
      if (namespace) params.set('namespace', namespace)
      if (includeInactive) params.set('includeInactive', 'true')
      return request<Announcement[]>(`/api/v1/announcements${params.size ? `?${params.toString()}` : ''}`)
    },
    publishAnnouncement: async (draft: AnnouncementDraft) =>
      request<Announcement>('/api/v1/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    deactivateAnnouncement: async (announcementId: string, expectedVersion: number) =>
      request<Announcement>(`/api/v1/announcements/${encodeURIComponent(announcementId)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    operationalControls: async () => request<OperationalControl[]>('/api/v1/operational-controls'),
    activateOperationalControl: async (draft: OperationalControlDraft) =>
      request<OperationalControl>('/api/v1/operational-controls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    changeOperationalControl: async (controlId: string, action: OperationalControlAction) =>
      request<OperationalControl>(`/api/v1/operational-controls/${encodeURIComponent(controlId)}/actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      }),
    operationalControlEvents: async () => request<OperationalControlEvent[]>('/api/v1/operational-control-events?limit=200'),
    blueprints: async (query = '', source?: BlueprintCatalogSource) => {
      const params = new URLSearchParams()
      if (query.trim()) params.set('q', query.trim())
      if (source) params.set('source', source)
      return request<BlueprintSummary[]>(`/api/v1/blueprints${params.size ? `?${params.toString()}` : ''}`)
    },
    blueprint: async (blueprintId: string, version: string) =>
      request<BlueprintDefinition>(`/api/v1/blueprints/${encodeURIComponent(blueprintId)}/${encodeURIComponent(version)}`),
    instantiateBlueprint: async (blueprintId: string, version: string, parameters: Record<string, string>) =>
      request<BlueprintDraftResponse>(`/api/v1/blueprints/${encodeURIComponent(blueprintId)}/${encodeURIComponent(version)}/instantiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parameters }),
      }),
    simulatePlayground: async (expression: string, context: Record<string, unknown>, fragment: string) =>
      request<PlaygroundSimulationResponse>('/api/v1/playground/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression, context, fragment }),
      }),
    flows: async () => request<PersistedFlow[]>('/api/v1/flows'),
    flowEditorSchema: async () => request<FlowEditorSchema>('/api/v1/flows/editor/schema'),
    validateFlow: async (document: string) =>
      request<FlowValidationResult>('/api/v1/flows/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    validateFlowPolicy: async (document: string) =>
      request<AdmissionPolicyDecision>('/api/v1/policies/flows/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    formatFlow: async (document: string) =>
      request<FlowFormatResponse>('/api/v1/flows/format', {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    saveFlow: async (document: string, etag?: string) =>
      request<PersistedFlow>('/api/v1/flows', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/yaml',
          ...(etag ? { 'If-Match': etag } : {}),
        },
        body: document,
      }),
    flowDocument: async (namespace: string, flowId: string, revision?: number) =>
      request<FlowDocumentExport>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/document${revision ? `?revision=${String(revision)}` : ''}`),
    flowRevisions: async (namespace: string, flowId: string) =>
      request<FlowRevisionRecord[]>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions`),
    flowTests: async (namespace: string, flowId: string, revision: number) =>
      request<FlowTestDefinition[]>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests?revision=${String(revision)}`),
    saveFlowTest: async (namespace: string, flowId: string, draft: FlowTestDefinitionDraft) =>
      request<FlowTestDefinition>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    deleteFlowTest: async (namespace: string, flowId: string, testId: string, expectedVersion: number) =>
      request<void>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/${encodeURIComponent(testId)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    flowTestRuns: async (namespace: string, flowId: string, revision: number) =>
      request<FlowTestRunResult[]>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/runs?revision=${String(revision)}`),
    runFlowTests: async (namespace: string, flowId: string, revision: number, testIds: string[] = []) =>
      request<FlowTestRunResult>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/runs?revision=${String(revision)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ testIds, failFast: false }),
      }),
    flowTestGate: async (namespace: string) =>
      request<FlowTestQualityGate | null>(`${namespaceRoot(namespace)}/flow-test-gate`),
    saveFlowTestGate: async (namespace: string, enabled: boolean, minimumCoverage: number, requiredTestIds: string[], expectedVersion?: number) =>
      request<FlowTestQualityGate>(`${namespaceRoot(namespace)}/flow-test-gate`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, minimumCoverage, requiredTestIds, expectedVersion }),
      }),
    diffFlowDraft: async (namespace: string, flowId: string, revision: number, document: string) =>
      request<FlowRevisionDiff>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/diff-draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    setFlowLifecycle: async (namespace: string, flowId: string, revision: number, lifecycle: 'DRAFT' | 'ACTIVE' | 'DISABLED' | 'ARCHIVED', reason: string) =>
      request<PersistedFlow>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/lifecycle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lifecycle, reason }),
      }),
    restoreFlowRevision: async (namespace: string, flowId: string, revision: number, reason: string) =>
      request<PersistedFlow>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }),
    previewExpression: async (expression: string, context: Record<string, unknown>) =>
      request<ExpressionPreviewResponse>('/api/v1/flows/expressions/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression, context }),
      }),
    pluginRegistry: async () => request<PluginRegistryIndex>('/api/v1/plugin-registry/index'),
    pluginPolicy: async (namespace?: string) =>
      request<EffectivePluginPolicy>(`/api/v1/plugin-policy/effective${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    admissionPolicies: async (namespace?: string) => {
      const params = new URLSearchParams({ namespace: namespace || 'default' })
      return request<AdmissionPolicyRevision[]>(`/api/v1/policies?${params.toString()}`)
    },
    admissionPolicyDecisions: async () =>
      request<AdmissionPolicyDecision[]>('/api/v1/policies/decisions?limit=50'),
    saveAdmissionPolicy: async (document: AdmissionPolicyDocument) =>
      request<AdmissionPolicyRevision>('/api/v1/policies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(document),
      }),
    createPluginPolicyRule: async (draft: PluginPolicyRuleDraft) =>
      request<PluginPolicyRule>('/api/v1/plugin-policy/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    deletePluginPolicyRule: async (ruleId: string) =>
      request<void>(`/api/v1/plugin-policy/rules/${encodeURIComponent(ruleId)}`, { method: 'DELETE' }),
    previewPluginQuarantine: async (draft: PluginQuarantineDraft) =>
      request<PluginPolicyImpactPreview>('/api/v1/plugin-policy/quarantines/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    createPluginQuarantine: async (draft: PluginQuarantineDraft) =>
      request<PluginQuarantine>('/api/v1/plugin-policy/quarantines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    flowGraph: async (namespace: string, flowId: string) =>
      request<FlowGraph>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/graph`),
    flowDataContract: async (namespace: string, flowId: string) =>
      request<FlowDataContract>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/data-contract`),
    flowMetadata: async (namespace: string, flowId: string) =>
      request<FlowMetadata>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/metadata`),
    simulateFlow: async (
      namespace: string,
      flowId: string,
      revision: number,
      inputs: Record<string, unknown>,
    ) => request<SimulationPlan>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ inputs, fixtures: {}, estimateModels: {}, signEvidence: true }),
    }),
    executeFlow: async (
      namespace: string,
      flowId: string,
      inputs: Record<string, unknown>,
      runner: ExecutionRunner = 'local',
    ) =>
      request<ExecutionDetail>('/api/v1/executions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ namespace, flowId, inputs, runner }),
      }),
    executions: async () => request<PersistedExecution[]>('/api/v1/executions?limit=200'),
    dashboards: async () => request<DashboardDefinition[]>('/api/v1/dashboards'),
    dashboard: async (dashboardId: string) =>
      request<DashboardDefinition>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}`),
    renderDashboard: async (dashboardId: string, filters: DashboardFilters) =>
      request<DashboardRender>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
      }),
    queryDashboard: async (query: DashboardQuery) =>
      request<DashboardQueryResult>('/api/v1/dashboard-queries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      }),
    saveDashboard: async (dashboardId: string, spec: DashboardSpec, expectedVersion?: number) =>
      request<DashboardDefinition>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}${expectedVersion ? `?expectedVersion=${String(expectedVersion)}` : ''}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec),
      }),
    deleteDashboard: async (dashboardId: string, expectedVersion: number) =>
      request<void>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    exportDashboard: async (dashboardId: string, format: 'yaml' | 'json' = 'yaml') =>
      requestBlob(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}/export?format=${format}`),
    search: async (searchRequest: SearchRequest) =>
      request<SearchResponse>('/api/v1/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchRequest),
      }),
    searchStatus: async () => request<SearchProjectionStatus>('/api/v1/search/status'),
    rebuildSearch: async (
      reason: string,
      scope: { types?: string[]; from?: string; to?: string } = {},
    ) =>
      request<SearchProjectionStatus>('/api/v1/search/rebuild', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, ...scope }),
      }),
    verifySearch: async () => request<SearchProjectionVerification>('/api/v1/search/verify'),
    controlSearch: async (enabled: boolean, reason: string) =>
      request<SearchProjectionStatus>('/api/v1/search/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, reason }),
      }),
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
    lifecyclePolicies: async () => request<LifecyclePolicy[]>('/api/v1/lifecycle/policies'),
    createLifecyclePolicy: async (draft: LifecyclePolicyDraft) =>
      request<LifecyclePolicy>('/api/v1/lifecycle/policies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    lifecycleLegalHolds: async () =>
      request<LifecycleLegalHold[]>('/api/v1/lifecycle/legal-holds'),
    createLifecycleLegalHold: async (draft: LifecycleLegalHoldDraft) =>
      request<LifecycleLegalHold>('/api/v1/lifecycle/legal-holds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    releaseLifecycleLegalHold: async (holdId: string) =>
      request<LifecycleLegalHold>(`/api/v1/lifecycle/legal-holds/${encodeURIComponent(holdId)}/release`, {
        method: 'POST',
      }),
    lifecycleJobs: async () => request<LifecycleJob[]>('/api/v1/lifecycle/jobs'),
    previewLifecyclePurge: async (policyId: string, reason: string) =>
      request<LifecycleJob>('/api/v1/lifecycle/previews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policyId, reason }),
      }),
    executeLifecycleJob: async (jobId: string, confirmation: string) =>
      request<LifecycleJob>(`/api/v1/lifecycle/jobs/${encodeURIComponent(jobId)}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation }),
      }),
    resumeLifecycleJob: async (jobId: string) =>
      request<LifecycleJob>(`/api/v1/lifecycle/jobs/${encodeURIComponent(jobId)}/resume`, {
        method: 'POST',
      }),
    upgradePolicy: async () => request<UpgradePolicy>('/api/v1/upgrades/policy'),
    upgradeReport: async (phase: 'preflight' | 'postflight', fromVersion: string, toVersion: string) =>
      request<UpgradeReport>(`/api/v1/upgrades/${phase}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fromVersion, toVersion }),
      }),
    previewEventUpcast: async () =>
      request<PersistedEventMigration>('/api/v1/upgrades/events/upcast'),
    applyEventUpcast: async (confirmation: string, reason: string, batchSize: number) =>
      request<PersistedEventMigration>('/api/v1/upgrades/events/upcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation, reason, batchSize }),
      }),
    namespaceFiles: async (namespace: string) =>
      request<NamespaceFile[]>(`${namespaceRoot(namespace)}/files`),
    namespaceArtifacts: async (namespace: string) =>
      request<ArtifactRef[]>(`${namespaceRoot(namespace)}/artifacts`),
    namespaceWorkflowMetadata: async (namespace: string) =>
      request<NamespaceWorkflowMetadataView>(`${namespaceRoot(namespace)}/workflow-metadata`),
    uploadNamespaceFile: async (namespace: string, path: string, file: File) =>
      request<NamespaceFile>(filePath(namespace, path), {
        method: 'PUT',
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
        body: file,
      }),
    downloadNamespaceFile: async (namespace: string, path: string, version?: number) =>
      requestBlob(`${filePath(namespace, path)}${version ? `?version=${String(version)}` : ''}`),
    namespaceFileVersions: async (namespace: string, path: string) =>
      request<NamespaceFileVersion[]>(`${filePath(namespace, path)}/versions`),
    moveNamespaceFile: async (namespace: string, path: string, destinationPath: string, expectedVersion: number) =>
      request<NamespaceFile>(`${filePath(namespace, path)}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destinationPath, expectedVersion }),
      }),
    deleteNamespaceFile: async (namespace: string, path: string, expectedVersion: number) =>
      request<void>(`${filePath(namespace, path)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    namespaceKeyValues: async (namespace: string) =>
      request<KeyValueEntry[]>(`${namespaceRoot(namespace)}/key-values`),
    putNamespaceKeyValue: async (namespace: string, key: string, type: KeyValueType, value: unknown, expiresAt?: string) =>
      request<KeyValueEntry>(`${namespaceRoot(namespace)}/key-values/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, value, expiresAt: expiresAt || null }),
      }),
    deleteNamespaceKeyValue: async (namespace: string, key: string, expectedVersion: number) =>
      request<void>(`${namespaceRoot(namespace)}/key-values/${encodeURIComponent(key)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    namespaceSecretBindings: async (namespace: string) =>
      request<SecretBinding[]>(`${namespaceRoot(namespace)}/secret-bindings`),
    agentResources: async (namespace: string, kind?: AgentResourceKind) => {
      const suffix = kind ? `?kind=${encodeURIComponent(kind)}` : ''
      return request<AgentResourceRevision[]>(`${namespaceRoot(namespace)}/agent/resources${suffix}`)
    },
    agentMcpConnections: async (namespace: string) =>
      request<AgentMcpConnectionRevision[]>(`${namespaceRoot(namespace)}/agent/mcp-connections`),
    agentCapabilityCatalog: async (namespace: string) =>
      request<AgentCapabilityCatalog>(`${namespaceRoot(namespace)}/agent/capabilities/catalog`),
    discoverAgentMcpConnection: async (namespace: string, input: { endpoint: string; credentialRef: string; timeoutSeconds?: number }) =>
      request<AgentMcpDiscoveryResult>(`${namespaceRoot(namespace)}/agent/mcp-connections/discover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      }),
    createAgentMcpConnection: async (namespace: string, spec: AgentMcpConnectionSpec) =>
      request<AgentMcpConnectionRevision>(`${namespaceRoot(namespace)}/agent/mcp-connections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec),
      }),
    testAgentMcpConnection: async (namespace: string, key: string, revision: number, timeoutSeconds?: number) =>
      request<AgentMcpConnectionTestResult>(`${namespaceRoot(namespace)}/agent/mcp-connections/${encodeURIComponent(key)}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ revision, ...(timeoutSeconds === undefined ? {} : { timeoutSeconds }) }),
      }),
    agentMcpTools: async (namespace: string, key: string, revision: number) =>
      request<AgentMcpToolCatalogEntry[]>(`${namespaceRoot(namespace)}/agent/mcp-connections/${encodeURIComponent(key)}/tools?revision=${String(revision)}`),
    createAgentResource: async (namespace: string, spec: AgentResourceSpec) =>
      request<AgentResourceRevision>(`${namespaceRoot(namespace)}/agent/resources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec),
      }),
    agentResource: async (namespace: string, kind: AgentResourceKind, key: string, revision?: number) => {
      const suffix = revision ? `?revision=${String(revision)}` : ''
      return request<AgentResourceRevision>(`${namespaceRoot(namespace)}/agent/resources/${kind}/${encodeURIComponent(key)}${suffix}`)
    },
    resolveAgent: async (namespace: string, key: string, revision: number, subjectRef: string) =>
      request<AgentCapabilityPin>(`${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentRevision: revision, subjectRef }),
      }),
    previewAgent: async (namespace: string, key: string, revision: number) =>
      request<AgentEnvelopePreview>(`${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/preview?agentRevision=${String(revision)}`),
    compareAgent: async (namespace: string, key: string, fromRevision: number, toRevision: number) =>
      request<AgentRevisionComparison>(`${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/compare?fromRevision=${String(fromRevision)}&toRevision=${String(toRevision)}`),
    putNamespaceSecretBinding: async (namespace: string, key: string, providerReference: string) =>
      request<SecretBinding>(`${namespaceRoot(namespace)}/secret-bindings/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'env', providerReference }),
      }),
    deleteNamespaceSecretBinding: async (namespace: string, key: string, expectedVersion: number) =>
      request<void>(`${namespaceRoot(namespace)}/secret-bindings/${encodeURIComponent(key)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    exportNamespaceResources: async (namespace: string) =>
      request<Record<string, unknown>>(`${namespaceRoot(namespace)}/resource-bundle`),
    importNamespaceResources: async (namespace: string, bundle: Record<string, unknown>) =>
      request<Record<string, number>>(`${namespaceRoot(namespace)}/resource-bundle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bundle),
      }),
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
    execution: async (executionId: string, taskOffset = 0, taskLimit = 250) =>
      request<ExecutionDetail>(`/api/v1/executions/${encodeURIComponent(executionId)}?taskOffset=${String(taskOffset)}&taskLimit=${String(taskLimit)}`),
    executionAgentSessions: async (executionId: string) =>
      request<AgentSessionSummary[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/agent-sessions`),
    executionAgentSessionDetail: async (
      executionId: string,
      taskRunId: string,
      attempt: number,
      afterEventIndex = 0,
      limit = 100,
    ) => request<AgentSessionDetailPage>(
      `/api/v1/executions/${encodeURIComponent(executionId)}/agent-sessions/${encodeURIComponent(taskRunId)}?attempt=${String(attempt)}&afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`,
    ),
    executionGraph: async (executionId: string) =>
      request<FlowGraph>(`/api/v1/executions/${encodeURIComponent(executionId)}/graph`),
    executionEvidence: async (executionId: string, cursor?: string) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      return request<ExecutionEvidencePage>(`/api/v1/executions/${encodeURIComponent(executionId)}/evidence${suffix}`)
    },
    streamExecutionEvidence: async (
      executionId: string,
      cursor: string | null,
      onEvent: (event: ExecutionEvidenceStreamEvent) => void,
      signal: AbortSignal,
    ) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      await streamNdjson<ExecutionEvidenceStreamEvent>(
        `/api/v1/executions/${encodeURIComponent(executionId)}/evidence/stream${suffix}`,
        onEvent,
        signal,
      )
    },
    executionSubflows: async (executionId: string) =>
      request<PersistedSubflow[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/subflows`),
    executionParentSubflow: async (executionId: string) =>
      request<PersistedSubflow | null>(`/api/v1/executions/${encodeURIComponent(executionId)}/parent-subflow`),
    executionInterventions: async (executionId: string) =>
      request<ExecutionInterventionRecord[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/interventions`),
    executionFiles: async (executionId: string) =>
      request<ExecutionArtifact[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/files`),
    downloadExecutionFile: async (executionId: string, artifactId: string) =>
      requestBlob(`/api/v1/executions/${encodeURIComponent(executionId)}/files/${encodeURIComponent(artifactId)}`),
    previewExecutionIntervention: async (
      executionId: string,
      action: ExecutionInterventionAction,
      checkpointTaskId?: string,
    ) => request<ExecutionInterventionPreview>(`/api/v1/executions/${encodeURIComponent(executionId)}/interventions/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, ...(checkpointTaskId ? { checkpointTaskId } : {}) }),
    }),
    applyExecutionIntervention: async (
      executionId: string,
      preview: ExecutionInterventionPreview,
      reason: string,
    ) => request<ExecutionDetail>(`/api/v1/executions/${encodeURIComponent(executionId)}/interventions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: preview.action,
        checkpointTaskId: preview.checkpoint_task_id,
        expectedVersion: preview.current_version,
        expectedEpoch: preview.current_epoch,
        reason,
      }),
    }),
    previewBackfill: async (spec: BackfillSpec) => request<BackfillPreview>('/api/v1/backfills/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec),
    }),
    createBackfill: async (spec: BackfillSpec) => request<BackfillRecord>('/api/v1/backfills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec),
    }),
    previewRelease: async (policyId: string) =>
      request<PromotionGate>(`/api/v1/releases/policies/${encodeURIComponent(policyId)}/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approvals: {} }),
      }),
    applyRelease: async (policyId: string, expectedVersion: number, reason: string) =>
      request<ReleaseActionResult>(`/api/v1/releases/policies/${encodeURIComponent(policyId)}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expectedVersion, reason, approvals: {} }),
      }),
    releaseTarget: async (targetKind: PromotionTargetKind, targetKey: string) =>
      request<ReleaseTarget>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}`),
    releaseHistory: async (targetKind: PromotionTargetKind, targetKey: string) =>
      request<ReleaseHistoryEntry[]>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/history`),
    rollbackRelease: async (
      targetKind: PromotionTargetKind,
      targetKey: string,
      toRevision: number,
      expectedVersion: number,
      reason: string,
    ) => request<ReleaseActionResult>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/rollback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toRevision, expectedVersion, reason }),
    }),
    killSwitchRelease: async (
      targetKind: PromotionTargetKind,
      targetKey: string,
      expectedVersion: number,
      reason: string,
    ) => request<ReleaseActionResult>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/kill-switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expectedVersion, reason }),
    }),
  }
}
