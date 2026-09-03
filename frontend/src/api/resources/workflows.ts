import { apiOperation, type ApiJsonRequestBody } from '../openapi'
import type { BlueprintCatalogSource } from '../types'
import type { ApiTransport } from '../transport'
import type {
  ExecutionRunner,
} from '../types'
import { namespaceRoot } from '../transport'
import type {
  AdmissionPolicyDocument,
  PluginPolicyRuleDraft,
  PluginQuarantineDraft,
} from '../types'

export function createWorkflowsResource(transport: ApiTransport) {
  return {
    blueprints: async (query = '', source?: BlueprintCatalogSource) => {
      const params = new URLSearchParams()
      if (query.trim()) params.set('q', query.trim())
      if (source) params.set('source', source)
      return transport.request(apiOperation('/api/v1/blueprints', 'get', `/api/v1/blueprints${params.size ? `?${params.toString()}` : ''}`))
    },
    blueprint: async (blueprintId: string, version: string) =>
      transport.request(apiOperation('/api/v1/blueprints/{blueprint_id}/{version}', 'get', `/api/v1/blueprints/${encodeURIComponent(blueprintId)}/${encodeURIComponent(version)}`)),
    instantiateBlueprint: async (blueprintId: string, version: string, parameters: Record<string, string>) =>
      transport.request(apiOperation('/api/v1/blueprints/{blueprint_id}/{version}/instantiate', 'post', `/api/v1/blueprints/${encodeURIComponent(blueprintId)}/${encodeURIComponent(version)}/instantiate`), {
        headers: { 'Content-Type': 'application/json' },
        json: { parameters },
      }),
    simulatePlayground: async (expression: string, context: Record<string, unknown>, fragment: string) =>
      transport.request(apiOperation('/api/v1/playground/simulate', 'post', '/api/v1/playground/simulate'), {
        headers: { 'Content-Type': 'application/json' },
        json: { expression, context, fragment },
      }),
    flows: async () => transport.request(apiOperation('/api/v1/flows', 'get', '/api/v1/flows')),
    flowEditorSchema: async () => transport.request(apiOperation('/api/v1/flows/editor/schema', 'get', '/api/v1/flows/editor/schema')),
    validateFlow: async (document: string) =>
      transport.request(apiOperation('/api/v1/flows/validate', 'post', '/api/v1/flows/validate'), {
        headers: { 'Content-Type': 'application/yaml' },
        rawBody: document,
      }),
    validateFlowPolicy: async (document: string) =>
      transport.request(apiOperation('/api/v1/policies/flows/validate', 'post', '/api/v1/policies/flows/validate'), {
        headers: { 'Content-Type': 'application/yaml' },
        rawBody: document,
      }),
    formatFlow: async (document: string) =>
      transport.request(apiOperation('/api/v1/flows/format', 'post', '/api/v1/flows/format'), {
        headers: { 'Content-Type': 'application/yaml' },
        rawBody: document,
      }),
    saveFlow: async (document: string, etag?: string) =>
      transport.request(apiOperation('/api/v1/flows', 'put', '/api/v1/flows'), {
        headers: {
          'Content-Type': 'application/yaml',
          ...(etag ? { 'If-Match': etag } : {}),
        },
        rawBody: document,
      }),
    flowDocument: async (namespace: string, flowId: string, revision?: number) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/document', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/document${revision ? `?revision=${String(revision)}` : ''}`)),
    flowRevisions: async (namespace: string, flowId: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/revisions', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions`)),
    flowTests: async (namespace: string, flowId: string, revision: number) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/tests', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests?revision=${String(revision)}`)),
    saveFlowTest: async (
      namespace: string,
      flowId: string,
      draft: ApiJsonRequestBody<'/api/v1/flows/{namespace}/{flow_id}/tests', 'put'>,
    ) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/tests', 'put', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests`), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    deleteFlowTest: async (namespace: string, flowId: string, testId: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/tests/{test_id}', 'delete', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/${encodeURIComponent(testId)}?expectedVersion=${String(expectedVersion)}`), { }),
    flowTestRuns: async (namespace: string, flowId: string, revision: number) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/tests/runs', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/runs?revision=${String(revision)}`)),
    runFlowTests: async (namespace: string, flowId: string, revision: number, testIds: string[] = []) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/tests/runs', 'post', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/tests/runs?revision=${String(revision)}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { testIds, failFast: false },
      }),
    flowTestGate: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/flow-test-gate', 'get', `${namespaceRoot(namespace)}/flow-test-gate`)),
    saveFlowTestGate: async (namespace: string, enabled: boolean, minimumCoverage: number, requiredTestIds: string[], expectedVersion?: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/flow-test-gate', 'put', `${namespaceRoot(namespace)}/flow-test-gate`), {
        headers: { 'Content-Type': 'application/json' },
        json: { enabled, minimumCoverage, requiredTestIds, expectedVersion },
      }),
    diffFlowDraft: async (namespace: string, flowId: string, revision: number, document: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft', 'post', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/diff-draft`), {
        headers: { 'Content-Type': 'application/yaml' },
        rawBody: document,
      }),
    setFlowLifecycle: async (namespace: string, flowId: string, revision: number, lifecycle: 'DRAFT' | 'ACTIVE' | 'DISABLED' | 'ARCHIVED', reason: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle', 'put', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/lifecycle`), {
        headers: { 'Content-Type': 'application/json' },
        json: { lifecycle, reason },
      }),
    restoreFlowRevision: async (namespace: string, flowId: string, revision: number, reason: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore', 'post', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/restore`), {
        headers: { 'Content-Type': 'application/json' },
        json: { reason },
      }),
    previewExpression: async (expression: string, context: Record<string, unknown>) =>
      transport.request(apiOperation('/api/v1/flows/expressions/preview', 'post', '/api/v1/flows/expressions/preview'), {
        headers: { 'Content-Type': 'application/json' },
        json: { expression, context },
      }),
    flowGraph: async (namespace: string, flowId: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/graph', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/graph`)),
    flowDataContract: async (namespace: string, flowId: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/data-contract', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/data-contract`)),
    flowMetadata: async (namespace: string, flowId: string) =>
      transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/metadata', 'get', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/metadata`)),
    simulateFlow: async (
      namespace: string,
      flowId: string,
      revision: number,
      inputs: Record<string, unknown>,
    ) => transport.request(apiOperation('/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate', 'post', `/api/v1/flows/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/revisions/${String(revision)}/simulate`), {
      headers: { 'Content-Type': 'application/json' },
      json: { inputs, defaultRunner: 'kubernetes', fixtures: {}, estimateModels: {}, signEvidence: true },
    }),
    executeFlow: async (
      namespace: string,
      flowId: string,
      inputs: Record<string, unknown>,
      runner: ExecutionRunner = 'local',
    ) =>
      transport.request(apiOperation('/api/v1/executions', 'post', '/api/v1/executions'), {
        headers: { 'Content-Type': 'application/json' },
        json: { namespace, flowId, inputs, runner, cacheMode: 'USE' },
      }),
    pluginRegistry: async () => transport.request(apiOperation('/api/v1/plugin-registry/index', 'get', '/api/v1/plugin-registry/index')),
    pluginPolicy: async (namespace?: string) =>
      transport.request(apiOperation('/api/v1/plugin-policy/effective', 'get', `/api/v1/plugin-policy/effective${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`)),
    admissionPolicies: async (namespace?: string) => {
      const params = new URLSearchParams({ namespace: namespace || 'default' })
      return transport.request(apiOperation('/api/v1/policies', 'get', `/api/v1/policies?${params.toString()}`))
    },
    admissionPolicyDecisions: async () =>
      transport.request(apiOperation('/api/v1/policies/decisions', 'get', '/api/v1/policies/decisions?limit=50')),
    saveAdmissionPolicy: async (document: AdmissionPolicyDocument) =>
      transport.request(apiOperation('/api/v1/policies', 'post', '/api/v1/policies'), {
        headers: { 'Content-Type': 'application/json' },
        json: document,
      }),
    createPluginPolicyRule: async (draft: PluginPolicyRuleDraft) =>
      transport.request(apiOperation('/api/v1/plugin-policy/rules', 'post', '/api/v1/plugin-policy/rules'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    deletePluginPolicyRule: async (ruleId: string) =>
      transport.request(apiOperation('/api/v1/plugin-policy/rules/{rule_id}', 'delete', `/api/v1/plugin-policy/rules/${encodeURIComponent(ruleId)}`), { }),
    previewPluginQuarantine: async (draft: PluginQuarantineDraft) =>
      transport.request(apiOperation('/api/v1/plugin-policy/quarantines/preview', 'post', '/api/v1/plugin-policy/quarantines/preview'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    createPluginQuarantine: async (draft: PluginQuarantineDraft) =>
      transport.request(apiOperation('/api/v1/plugin-policy/quarantines', 'post', '/api/v1/plugin-policy/quarantines'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
  }
}
