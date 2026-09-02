import type {
  BlueprintCatalogSource,
  BlueprintDefinition,
  BlueprintDraftResponse,
  BlueprintSummary,
  PlaygroundSimulationResponse,
} from '../types'
import type { ApiTransport } from '../transport'
import type {
  AdmissionPolicyDecision,
  ExecutionDetail,
  ExecutionRunner,
  FlowDataContract,
  FlowDocumentExport,
  FlowEditorSchema,
  FlowFormatResponse,
  FlowMetadata,
  FlowGraph,
  FlowRevisionDiff,
  FlowRevisionRecord,
  FlowTestDefinition,
  FlowTestDefinitionDraft,
  FlowTestQualityGate,
  FlowTestRunResult,
  FlowValidationResult,
  ExpressionPreviewResponse,
  PersistedFlow,
  SimulationPlan,
} from '../types'
import { namespaceRoot } from '../transport'
import type {
  AdmissionPolicyDocument,
  AdmissionPolicyRevision,
  EffectivePluginPolicy,
  PluginPolicyImpactPreview,
  PluginPolicyRule,
  PluginPolicyRuleDraft,
  PluginQuarantine,
  PluginQuarantineDraft,
  PluginRegistryIndex,
} from '../types'

export function createWorkflowsResource(transport: ApiTransport) {
  return {
    blueprints: async (query = '', source?: BlueprintCatalogSource) => {
      const params = new URLSearchParams()
      if (query.trim()) params.set('q', query.trim())
      if (source) params.set('source', source)
      return transport.request<BlueprintSummary[]>(`/api/v1/blueprints${params.size ? `?${params.toString()}` : ''}`)
    },
    blueprint: async (blueprintId: string, version: string) =>
      transport.request<BlueprintDefinition>(`/api/v1/blueprints/${encodeURIComponent(blueprintId)}/${encodeURIComponent(version)}`),
    instantiateBlueprint: async (blueprintId: string, version: string, parameters: Record<string, string>) =>
      transport.request<BlueprintDraftResponse>(`/api/v1/blueprints/${encodeURIComponent(blueprintId)}/${encodeURIComponent(version)}/instantiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parameters }),
      }),
    simulatePlayground: async (expression: string, context: Record<string, unknown>, fragment: string) =>
      transport.request<PlaygroundSimulationResponse>('/api/v1/playground/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression, context, fragment }),
      }),
    flows: async () => transport.request<PersistedFlow[]>('/api/v1/flows'),
    flowEditorSchema: async () => transport.request<FlowEditorSchema>('/api/v1/flows/editor/schema'),
    validateFlow: async (document: string) =>
      transport.request<FlowValidationResult>('/api/v1/flows/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    validateFlowPolicy: async (document: string) =>
      transport.request<AdmissionPolicyDecision>('/api/v1/policies/flows/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    formatFlow: async (document: string) =>
      transport.request<FlowFormatResponse>('/api/v1/flows/format', {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    saveFlow: async (document: string, etag?: string) =>
      transport.request<PersistedFlow>('/api/v1/flows', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/yaml',
          ...(etag ? { 'If-Match': etag } : {}),
        },
        body: document,
      }),
    flowDocument: async (namespace: string, flowId: string, revision?: number) =>
      transport.request<FlowDocumentExport>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/document${revision ? `?revision=${String(revision)}` : ''}`),
    flowRevisions: async (namespace: string, flowId: string) =>
      transport.request<FlowRevisionRecord[]>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions`),
    flowTests: async (namespace: string, flowId: string, revision: number) =>
      transport.request<FlowTestDefinition[]>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests?revision=${String(revision)}`),
    saveFlowTest: async (namespace: string, flowId: string, draft: FlowTestDefinitionDraft) =>
      transport.request<FlowTestDefinition>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    deleteFlowTest: async (namespace: string, flowId: string, testId: string, expectedVersion: number) =>
      transport.request<void>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/${encodeURIComponent(testId)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    flowTestRuns: async (namespace: string, flowId: string, revision: number) =>
      transport.request<FlowTestRunResult[]>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/runs?revision=${String(revision)}`),
    runFlowTests: async (namespace: string, flowId: string, revision: number, testIds: string[] = []) =>
      transport.request<FlowTestRunResult>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/runs?revision=${String(revision)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ testIds, failFast: false }),
      }),
    flowTestGate: async (namespace: string) =>
      transport.request<FlowTestQualityGate | null>(`${namespaceRoot(namespace)}/flow-test-gate`),
    saveFlowTestGate: async (namespace: string, enabled: boolean, minimumCoverage: number, requiredTestIds: string[], expectedVersion?: number) =>
      transport.request<FlowTestQualityGate>(`${namespaceRoot(namespace)}/flow-test-gate`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, minimumCoverage, requiredTestIds, expectedVersion }),
      }),
    diffFlowDraft: async (namespace: string, flowId: string, revision: number, document: string) =>
      transport.request<FlowRevisionDiff>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/diff-draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/yaml' },
        body: document,
      }),
    setFlowLifecycle: async (namespace: string, flowId: string, revision: number, lifecycle: 'DRAFT' | 'ACTIVE' | 'DISABLED' | 'ARCHIVED', reason: string) =>
      transport.request<PersistedFlow>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/lifecycle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lifecycle, reason }),
      }),
    restoreFlowRevision: async (namespace: string, flowId: string, revision: number, reason: string) =>
      transport.request<PersistedFlow>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }),
    previewExpression: async (expression: string, context: Record<string, unknown>) =>
      transport.request<ExpressionPreviewResponse>('/api/v1/flows/expressions/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression, context }),
      }),
    flowGraph: async (namespace: string, flowId: string) =>
      transport.request<FlowGraph>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/graph`),
    flowDataContract: async (namespace: string, flowId: string) =>
      transport.request<FlowDataContract>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/data-contract`),
    flowMetadata: async (namespace: string, flowId: string) =>
      transport.request<FlowMetadata>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/metadata`),
    simulateFlow: async (
      namespace: string,
      flowId: string,
      revision: number,
      inputs: Record<string, unknown>,
    ) => transport.request<SimulationPlan>(`/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/simulate`, {
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
      transport.request<ExecutionDetail>('/api/v1/executions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ namespace, flowId, inputs, runner }),
      }),
    pluginRegistry: async () => transport.request<PluginRegistryIndex>('/api/v1/plugin-registry/index'),
    pluginPolicy: async (namespace?: string) =>
      transport.request<EffectivePluginPolicy>(`/api/v1/plugin-policy/effective${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    admissionPolicies: async (namespace?: string) => {
      const params = new URLSearchParams({ namespace: namespace || 'default' })
      return transport.request<AdmissionPolicyRevision[]>(`/api/v1/policies?${params.toString()}`)
    },
    admissionPolicyDecisions: async () =>
      transport.request<AdmissionPolicyDecision[]>('/api/v1/policies/decisions?limit=50'),
    saveAdmissionPolicy: async (document: AdmissionPolicyDocument) =>
      transport.request<AdmissionPolicyRevision>('/api/v1/policies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(document),
      }),
    createPluginPolicyRule: async (draft: PluginPolicyRuleDraft) =>
      transport.request<PluginPolicyRule>('/api/v1/plugin-policy/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    deletePluginPolicyRule: async (ruleId: string) =>
      transport.request<void>(`/api/v1/plugin-policy/rules/${encodeURIComponent(ruleId)}`, { method: 'DELETE' }),
    previewPluginQuarantine: async (draft: PluginQuarantineDraft) =>
      transport.request<PluginPolicyImpactPreview>('/api/v1/plugin-policy/quarantines/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    createPluginQuarantine: async (draft: PluginQuarantineDraft) =>
      transport.request<PluginQuarantine>('/api/v1/plugin-policy/quarantines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
  }
}
