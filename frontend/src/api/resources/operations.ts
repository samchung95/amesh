import { apiOperation, type ApiJsonRequestBody } from '../openapi'
import type {
  DashboardFilters,
  DashboardQuery,
  DashboardSpec,
  SearchRequest,
  SearchDocumentType,
} from '../types'
import type { ApiTransport } from '../transport'
import type {
  LifecycleLegalHoldDraft,
  LifecyclePolicyDraft,
} from '../types'

export function createOperationsResource(transport: ApiTransport) {
  type DashboardFiltersRequest = ApiJsonRequestBody<'/api/v1/dashboards/{dashboard_id}/render', 'post'>
  type DashboardQueryRequest = ApiJsonRequestBody<'/api/v1/dashboard-queries', 'post'>
  type DashboardSpecRequest = ApiJsonRequestBody<'/api/v1/dashboards/{dashboard_id}', 'put'>

  const dashboardFiltersRequest = (filters: DashboardFilters): DashboardFiltersRequest => ({
    ...filters,
    states: filters.states ?? [],
    workerGroups: filters.workerGroups ?? [],
  })
  const dashboardQueryRequest = (query: DashboardQuery): DashboardQueryRequest => {
    const { filters, ...fields } = query
    return {
      ...fields,
      ...(filters ? { filters: dashboardFiltersRequest(filters) } : {}),
    }
  }
  const dashboardSpecRequest = (spec: DashboardSpec): DashboardSpecRequest => ({
    ...spec,
    widgets: spec.widgets.map((widget) => ({
      ...widget,
      query: dashboardQueryRequest(widget.query),
    })),
  })

  return {
    dashboards: async () => transport.request(apiOperation('/api/v1/dashboards', 'get', '/api/v1/dashboards')),
    dashboard: async (dashboardId: string) =>
      transport.request(apiOperation('/api/v1/dashboards/{dashboard_id}', 'get', `/api/v1/dashboards/${encodeURIComponent(dashboardId)}`)),
    renderDashboard: async (dashboardId: string, filters: DashboardFilters) =>
      transport.request(apiOperation('/api/v1/dashboards/{dashboard_id}/render', 'post', `/api/v1/dashboards/${encodeURIComponent(dashboardId)}/render`), {
        headers: { 'Content-Type': 'application/json' },
        json: dashboardFiltersRequest(filters),
      }),
    queryDashboard: async (query: DashboardQuery) =>
      transport.request(apiOperation('/api/v1/dashboard-queries', 'post', '/api/v1/dashboard-queries'), {
        headers: { 'Content-Type': 'application/json' },
        json: dashboardQueryRequest(query),
      }),
    saveDashboard: async (dashboardId: string, spec: DashboardSpec, expectedVersion?: number) =>
      transport.request(apiOperation('/api/v1/dashboards/{dashboard_id}', 'put', `/api/v1/dashboards/${encodeURIComponent(dashboardId)}${expectedVersion ? `?expectedVersion=${String(expectedVersion)}` : ''}`), {
        headers: { 'Content-Type': 'application/json' },
        json: dashboardSpecRequest(spec),
      }),
    deleteDashboard: async (dashboardId: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/dashboards/{dashboard_id}', 'delete', `/api/v1/dashboards/${encodeURIComponent(dashboardId)}?expectedVersion=${String(expectedVersion)}`), { }),
    exportDashboard: async (dashboardId: string, format: 'yaml' | 'json' = 'yaml') =>
      transport.requestBlob(apiOperation('/api/v1/dashboards/{dashboard_id}/export', 'get', `/api/v1/dashboards/${encodeURIComponent(dashboardId)}/export?format=${format}`)),
    search: async (searchRequest: SearchRequest) =>
      transport.request(apiOperation('/api/v1/search', 'post', '/api/v1/search'), {
        headers: { 'Content-Type': 'application/json' },
        json: {
          ...searchRequest,
          direction: searchRequest.direction ?? 'DESC',
          limit: searchRequest.limit ?? 50,
          query: searchRequest.query ?? '',
          ranges: searchRequest.ranges ?? [],
          sort: searchRequest.sort ?? 'RELEVANCE',
          states: searchRequest.states ?? [],
          types: searchRequest.types ?? [],
        },
      }),
    searchStatus: async () => transport.request(apiOperation('/api/v1/search/status', 'get', '/api/v1/search/status')),
    rebuildSearch: async (
      reason: string,
      scope: { types?: SearchDocumentType[]; from?: string; to?: string } = {},
    ) =>
      transport.request(apiOperation('/api/v1/search/rebuild', 'post', '/api/v1/search/rebuild'), {
        headers: { 'Content-Type': 'application/json' },
        json: { reason, types: [], ...scope },
      }),
    verifySearch: async () => transport.request(apiOperation('/api/v1/search/verify', 'get', '/api/v1/search/verify')),
    controlSearch: async (enabled: boolean, reason: string) =>
      transport.request(apiOperation('/api/v1/search/control', 'post', '/api/v1/search/control'), {
        headers: { 'Content-Type': 'application/json' },
        json: { enabled, reason },
      }),
    triggers: async (namespace?: string) => {
      const suffix = namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''
      return transport.request(apiOperation('/api/v1/triggers', 'get', `/api/v1/triggers${suffix}`))
    },
    triggerOccurrences: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request(apiOperation('/api/v1/trigger-occurrences', 'get', `/api/v1/trigger-occurrences?${params.toString()}`))
    },
    checkPolicies: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request(apiOperation('/api/v1/check-policies', 'get', `/api/v1/check-policies?${params.toString()}`))
    },
    checkEvaluations: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request(apiOperation('/api/v1/check-evaluations', 'get', `/api/v1/check-evaluations?${params.toString()}`))
    },
    checkCompliance: async (namespace?: string) => {
      const params = new URLSearchParams({ groupBy: 'flow', limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request(apiOperation('/api/v1/check-compliance', 'get', `/api/v1/check-compliance?${params.toString()}`))
    },
    setTriggerPaused: async (namespace: string, flowId: string, triggerId: string, paused: boolean, reason: string) =>
      transport.request(apiOperation(paused ? '/api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause' : '/api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume', 'post', `/api/v1/triggers/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/${encodeURIComponent(triggerId)}/${paused ? 'pause' : 'resume'}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { reason },
      }),
    replayTriggerOccurrence: async (occurrenceId: string, reason: string) =>
      transport.request(apiOperation('/api/v1/trigger-occurrences/{occurrence_id}/replay', 'post', `/api/v1/trigger-occurrences/${encodeURIComponent(occurrenceId)}/replay`), {
        headers: { 'Content-Type': 'application/json' },
        json: { reason },
      }),
    lifecyclePolicies: async () => transport.request(apiOperation('/api/v1/lifecycle/policies', 'get', '/api/v1/lifecycle/policies')),
    createLifecyclePolicy: async (draft: LifecyclePolicyDraft) =>
      transport.request(apiOperation('/api/v1/lifecycle/policies', 'post', '/api/v1/lifecycle/policies'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    lifecycleLegalHolds: async () =>
      transport.request(apiOperation('/api/v1/lifecycle/legal-holds', 'get', '/api/v1/lifecycle/legal-holds')),
    createLifecycleLegalHold: async (draft: LifecycleLegalHoldDraft) =>
      transport.request(apiOperation('/api/v1/lifecycle/legal-holds', 'post', '/api/v1/lifecycle/legal-holds'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    releaseLifecycleLegalHold: async (holdId: string) =>
      transport.request(apiOperation('/api/v1/lifecycle/legal-holds/{hold_id}/release', 'post', `/api/v1/lifecycle/legal-holds/${encodeURIComponent(holdId)}/release`)),
    lifecycleJobs: async () => transport.request(apiOperation('/api/v1/lifecycle/jobs', 'get', '/api/v1/lifecycle/jobs')),
    previewLifecyclePurge: async (policyId: string, reason: string) =>
      transport.request(apiOperation('/api/v1/lifecycle/previews', 'post', '/api/v1/lifecycle/previews'), {
        headers: { 'Content-Type': 'application/json' },
        json: { policyId, reason },
      }),
    executeLifecycleJob: async (jobId: string, confirmation: string) =>
      transport.request(apiOperation('/api/v1/lifecycle/jobs/{job_id}/execute', 'post', `/api/v1/lifecycle/jobs/${encodeURIComponent(jobId)}/execute`), {
        headers: { 'Content-Type': 'application/json' },
        json: { confirmation },
      }),
    resumeLifecycleJob: async (jobId: string) =>
      transport.request(apiOperation('/api/v1/lifecycle/jobs/{job_id}/resume', 'post', `/api/v1/lifecycle/jobs/${encodeURIComponent(jobId)}/resume`)),
    upgradePolicy: async () => transport.request(apiOperation('/api/v1/upgrades/policy', 'get', '/api/v1/upgrades/policy')),
    upgradeReport: async (phase: 'preflight' | 'postflight', fromVersion: string, toVersion: string) =>
      transport.request(apiOperation(phase === 'preflight' ? '/api/v1/upgrades/preflight' : '/api/v1/upgrades/postflight', 'post', `/api/v1/upgrades/${phase}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { fromVersion, toVersion },
      }),
    previewEventUpcast: async () =>
      transport.request(apiOperation('/api/v1/upgrades/events/upcast', 'get', '/api/v1/upgrades/events/upcast')),
    applyEventUpcast: async (confirmation: string, reason: string, batchSize: number) =>
      transport.request(apiOperation('/api/v1/upgrades/events/upcast', 'post', '/api/v1/upgrades/events/upcast'), {
        headers: { 'Content-Type': 'application/json' },
        json: { confirmation, reason, batchSize },
      }),
  }
}
