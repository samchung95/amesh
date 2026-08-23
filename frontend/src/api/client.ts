import type {
  AdministrationAuditEntry,
  AdministrationControl,
  AdministrationControlDraft,
  AdministrationImpactPreview,
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
  FlowDataContract,
  FlowDocumentExport,
  FlowEditorSchema,
  FlowFormatResponse,
  FlowMetadata,
  AuthenticationProvider,
  ConfigurationSnapshot,
  CredentialMetadata,
  FeatureFlag,
  FlowGraph,
  FlowRevisionDiff,
  FlowRevisionRecord,
  FlowValidationResult,
  HealthResponse,
  LoginResponse,
  ExpressionPreviewResponse,
  NamespaceCheckPolicy,
  NamespaceFile,
  NamespaceFileVersion,
  NamespaceWorkflowMetadataView,
  PluginRegistryIndex,
  KeyValueEntry,
  KeyValueType,
  PersistedExecution,
  PersistedFlow,
  PersistedSubflow,
  PlaygroundSimulationResponse,
  PrincipalDefinition,
  ReadinessResponse,
  RoleBinding,
  RoleDefinition,
  SecretBinding,
  SearchProjectionStatus,
  SearchRequest,
  SearchResponse,
  ServiceTopology,
  TriggerOccurrence,
  TriggerRuntimeState,
  UiSession,
  WorkerInventory,
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
    flowGraph: async (namespace: string, flowId: string) =>
      request<FlowGraph>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/graph`),
    flowDataContract: async (namespace: string, flowId: string) =>
      request<FlowDataContract>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/data-contract`),
    flowMetadata: async (namespace: string, flowId: string) =>
      request<FlowMetadata>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/metadata`),
    executeFlow: async (namespace: string, flowId: string, inputs: Record<string, unknown>) =>
      request<ExecutionDetail>('/api/v1/executions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ namespace, flowId, inputs, runner: 'local' }),
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
    rebuildSearch: async (reason: string) =>
      request<SearchProjectionStatus>('/api/v1/search/rebuild', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
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
    namespaceFiles: async (namespace: string) =>
      request<NamespaceFile[]>(`${namespaceRoot(namespace)}/files`),
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
  }
}
