import type {
  DashboardDefinition,
  DashboardFilters,
  DashboardQuery,
  DashboardQueryResult,
  DashboardRender,
  DashboardSpec,
  SearchProjectionStatus,
  SearchProjectionVerification,
  SearchRequest,
  SearchResponse,
} from '../types'
import type { ApiTransport } from '../transport'
import type {
  CheckComplianceSummary,
  CheckEvaluation,
  NamespaceCheckPolicy,
  TriggerOccurrence,
  TriggerRuntimeState,
} from '../types'
import type {
  LifecycleJob,
  LifecycleLegalHold,
  LifecycleLegalHoldDraft,
  LifecyclePolicy,
  LifecyclePolicyDraft,
  PersistedEventMigration,
  UpgradePolicy,
  UpgradeReport,
} from '../types'

export function createOperationsResource(transport: ApiTransport) {
  return {
    dashboards: async () => transport.request<DashboardDefinition[]>('/api/v1/dashboards'),
    dashboard: async (dashboardId: string) =>
      transport.request<DashboardDefinition>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}`),
    renderDashboard: async (dashboardId: string, filters: DashboardFilters) =>
      transport.request<DashboardRender>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
      }),
    queryDashboard: async (query: DashboardQuery) =>
      transport.request<DashboardQueryResult>('/api/v1/dashboard-queries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      }),
    saveDashboard: async (dashboardId: string, spec: DashboardSpec, expectedVersion?: number) =>
      transport.request<DashboardDefinition>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}${expectedVersion ? `?expectedVersion=${String(expectedVersion)}` : ''}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec),
      }),
    deleteDashboard: async (dashboardId: string, expectedVersion: number) =>
      transport.request<void>(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    exportDashboard: async (dashboardId: string, format: 'yaml' | 'json' = 'yaml') =>
      transport.requestBlob(`/api/v1/dashboards/${encodeURIComponent(dashboardId)}/export?format=${format}`),
    search: async (searchRequest: SearchRequest) =>
      transport.request<SearchResponse>('/api/v1/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchRequest),
      }),
    searchStatus: async () => transport.request<SearchProjectionStatus>('/api/v1/search/status'),
    rebuildSearch: async (
      reason: string,
      scope: { types?: string[]; from?: string; to?: string } = {},
    ) =>
      transport.request<SearchProjectionStatus>('/api/v1/search/rebuild', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, ...scope }),
      }),
    verifySearch: async () => transport.request<SearchProjectionVerification>('/api/v1/search/verify'),
    controlSearch: async (enabled: boolean, reason: string) =>
      transport.request<SearchProjectionStatus>('/api/v1/search/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, reason }),
      }),
    triggers: async (namespace?: string) => {
      const suffix = namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''
      return transport.request<TriggerRuntimeState[]>(`/api/v1/triggers${suffix}`)
    },
    triggerOccurrences: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request<TriggerOccurrence[]>(`/api/v1/trigger-occurrences?${params.toString()}`)
    },
    checkPolicies: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request<NamespaceCheckPolicy[]>(`/api/v1/check-policies?${params.toString()}`)
    },
    checkEvaluations: async (namespace?: string) => {
      const params = new URLSearchParams({ limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request<CheckEvaluation[]>(`/api/v1/check-evaluations?${params.toString()}`)
    },
    checkCompliance: async (namespace?: string) => {
      const params = new URLSearchParams({ groupBy: 'flow', limit: '200' })
      if (namespace) params.set('namespace', namespace)
      return transport.request<CheckComplianceSummary[]>(`/api/v1/check-compliance?${params.toString()}`)
    },
    setTriggerPaused: async (namespace: string, flowId: string, triggerId: string, paused: boolean, reason: string) =>
      transport.request<TriggerRuntimeState>(`/api/v1/triggers/${encodeURIComponent(namespace)}/${encodeURIComponent(flowId)}/${encodeURIComponent(triggerId)}/${paused ? 'pause' : 'resume'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }),
    replayTriggerOccurrence: async (occurrenceId: string, reason: string) =>
      transport.request<TriggerOccurrence>(`/api/v1/trigger-occurrences/${encodeURIComponent(occurrenceId)}/replay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }),
    lifecyclePolicies: async () => transport.request<LifecyclePolicy[]>('/api/v1/lifecycle/policies'),
    createLifecyclePolicy: async (draft: LifecyclePolicyDraft) =>
      transport.request<LifecyclePolicy>('/api/v1/lifecycle/policies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    lifecycleLegalHolds: async () =>
      transport.request<LifecycleLegalHold[]>('/api/v1/lifecycle/legal-holds'),
    createLifecycleLegalHold: async (draft: LifecycleLegalHoldDraft) =>
      transport.request<LifecycleLegalHold>('/api/v1/lifecycle/legal-holds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    releaseLifecycleLegalHold: async (holdId: string) =>
      transport.request<LifecycleLegalHold>(`/api/v1/lifecycle/legal-holds/${encodeURIComponent(holdId)}/release`, {
        method: 'POST',
      }),
    lifecycleJobs: async () => transport.request<LifecycleJob[]>('/api/v1/lifecycle/jobs'),
    previewLifecyclePurge: async (policyId: string, reason: string) =>
      transport.request<LifecycleJob>('/api/v1/lifecycle/previews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policyId, reason }),
      }),
    executeLifecycleJob: async (jobId: string, confirmation: string) =>
      transport.request<LifecycleJob>(`/api/v1/lifecycle/jobs/${encodeURIComponent(jobId)}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation }),
      }),
    resumeLifecycleJob: async (jobId: string) =>
      transport.request<LifecycleJob>(`/api/v1/lifecycle/jobs/${encodeURIComponent(jobId)}/resume`, {
        method: 'POST',
      }),
    upgradePolicy: async () => transport.request<UpgradePolicy>('/api/v1/upgrades/policy'),
    upgradeReport: async (phase: 'preflight' | 'postflight', fromVersion: string, toVersion: string) =>
      transport.request<UpgradeReport>(`/api/v1/upgrades/${phase}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fromVersion, toVersion }),
      }),
    previewEventUpcast: async () =>
      transport.request<PersistedEventMigration>('/api/v1/upgrades/events/upcast'),
    applyEventUpcast: async (confirmation: string, reason: string, batchSize: number) =>
      transport.request<PersistedEventMigration>('/api/v1/upgrades/events/upcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation, reason, batchSize }),
      }),
  }
}
