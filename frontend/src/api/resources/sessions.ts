import type {
  AgentSessionSummary,
  AgentSessionControlEventPage,
  AgentSessionControlSummary,
  AgentSessionControlRequest,
  AgentSessionAdminActionRequest,
  AgentSessionAdminActionResult,
  AgentSessionCompatibilityReport,
  AgentSessionFleetPage,
  AgentSessionFleetQuery,
  AgentSessionImportResult,
  AgentSessionProfileCompatibilityReport,
  AgentSessionProfileImportResult,
  AgentSessionProfileTransferBundle,
  AgentSessionPolicyDraft,
  AgentSessionPolicyRevision,
  AgentSessionTransferBundle,
  AgentSessionTransferMode,
  AgentSessionInstanceAggregate,
  AgentSessionCreateRequest,
  AgentSessionHarnessCatalog,
  AgentSessionLaunchResponse,
  AgentSessionServiceDetailPage,
  AgentSessionServiceItem,
  AgentSessionResult,
  AgentSessionLifecycleState,
  AgentProgressPage,
  AgentProgressStreamItem,
} from '../types'

import type { ApiTransport } from '../transport'

export function createSessionsResource(transport: ApiTransport) {
  type AgentSessionControlPayload = Partial<AgentSessionControlRequest> & { reason: string }

  const normalizeSessionState = (state: string): AgentSessionLifecycleState => {
    if (state === 'SUCCESS') return 'SUCCEEDED'
    if (state === 'ERROR' || state === 'FAILURE') return 'FAILED'
    return state as AgentSessionLifecycleState
  }

  const controlSummary = (summary: AgentSessionSummary | AgentSessionControlSummary, serviceSessionId?: string): AgentSessionControlSummary => ({
    ...summary,
    sessionId: serviceSessionId || summary.sessionId,
    state: normalizeSessionState(summary.state),
    harness: summary.harness || null,
  })

  const launchSummary = (launch: AgentSessionLaunchResponse): AgentSessionControlSummary => {
    if (launch.session) return controlSummary(launch.session, launch.sessionId)
    const now = new Date().toISOString()
    return { sessionId: launch.sessionId, state: normalizeSessionState(launch.executionState), createdAt: now, updatedAt: now }
  }

  const postAgentSessionControl = (
    sessionId: string,
    action: 'cancel' | 'pause' | 'retry' | 'resume',
    defaultReason: string,
    control?: Partial<AgentSessionControlRequest>,
  ) => transport.request<AgentSessionLaunchResponse>(
    `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/${action}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...control, reason: control?.reason || defaultReason } satisfies AgentSessionControlPayload),
    },
  ).then(launchSummary)

  const agentSessionControlReason = (action: 'cancellation' | 'pause' | 'retry' | 'resume') => `Operator requested ${action}.`

  const agentSessionControlDetail = (sessionId: string, suffix: string) =>
    transport.request<AgentSessionServiceDetailPage>(`/api/v1/agent-sessions/${encodeURIComponent(sessionId)}${suffix}`)
  return {
    agentSessionHarnesses: async () => transport.request<AgentSessionHarnessCatalog>('/api/v1/agent-sessions/harnesses'),
    agentSessions: async () => {
      const items = await transport.request<AgentSessionServiceItem[]>('/api/v1/agent-sessions')
      return items.map((item) => controlSummary(item.session, item.sessionId))
    },
    createAgentSession: async (input: AgentSessionCreateRequest) => {
      const launch = await transport.request<AgentSessionLaunchResponse>('/api/v1/agent-sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentRef: input.agentRef, input: input.input || {} }),
      })
      return launchSummary(launch)
    },
    agentSession: async (sessionId: string) =>
      agentSessionControlDetail(sessionId, '').then((page) => controlSummary(page.session, sessionId)),
    agentSessionEvents: async (sessionId: string, afterEventIndex = 0, limit = 100) => {
      const page = await agentSessionControlDetail(sessionId, `/events?afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`)
      return { events: page.events, nextEventIndex: page.nextEventIndex } as AgentSessionControlEventPage
    },
    agentSessionProgress: async (sessionId: string, after?: string, limit = 100) => {
      const params = new URLSearchParams({ limit: String(limit) })
      if (after) params.set('after', after)
      return transport.request<AgentProgressPage>(`/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/progress?${params.toString()}`)
    },
    streamAgentSessionProgress: async (
      sessionId: string,
      after: string | null,
      onItem: (item: AgentProgressStreamItem) => void,
      signal: AbortSignal,
    ) => {
      const suffix = after ? `?after=${encodeURIComponent(after)}` : ''
      await transport.streamNdjson<AgentProgressStreamItem>(
        `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/progress/stream${suffix}`,
        onItem,
        signal,
      )
    },
    agentSessionMessages: async (sessionId: string, afterEventIndex = 0, limit = 100) =>
      agentSessionControlDetail(sessionId, `/messages?afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`),
    cancelAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'cancel', agentSessionControlReason('cancellation'), control),
    pauseAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'pause', agentSessionControlReason('pause'), control),
    retryAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'retry', agentSessionControlReason('retry'), control),
    resumeAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'resume', agentSessionControlReason('resume'), control),
    agentSessionResult: async (sessionId: string) =>
      transport.request<AgentSessionResult>(`/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/result`),
    agentSessionFleet: async (query: AgentSessionFleetQuery = {}) => {
      const params = new URLSearchParams()
      if (query.limit !== undefined) params.set('limit', String(query.limit))
      if (query.cursor) params.set('cursor', query.cursor)
      if (query.state) params.set('state', query.state)
      if (query.namespace) params.set('namespace', query.namespace)
      if (query.agentRef) params.set('agentRef', query.agentRef)
      if (query.ownerId) params.set('ownerId', query.ownerId)
      if (query.harness) params.set('harness', query.harness)
      if (query.createdFrom) params.set('createdFrom', query.createdFrom)
      if (query.createdTo) params.set('createdTo', query.createdTo)
      const suffix = params.size ? `?${params.toString()}` : ''
      return transport.request<AgentSessionFleetPage>(`/api/v1/admin/agent-sessions${suffix}`)
    },
    agentSessionInstanceAggregate: async () =>
      transport.request<AgentSessionInstanceAggregate>('/api/v1/admin/agent-sessions/aggregate'),
    agentSessionPolicies: async (namespace?: string, applicationId?: string) => {
      const params = new URLSearchParams()
      if (namespace) params.set('namespace', namespace)
      if (applicationId) params.set('applicationId', applicationId)
      params.set('limit', '100')
      return transport.request<AgentSessionPolicyRevision[]>(`/api/v1/admin/agent-session-policies?${params.toString()}`)
    },
    effectiveAgentSessionPolicies: async (namespace: string, applicationId?: string) => {
      const params = new URLSearchParams({ namespace })
      if (applicationId) params.set('applicationId', applicationId)
      return transport.request<AgentSessionPolicyRevision[]>(`/api/v1/admin/agent-session-policies/effective?${params.toString()}`)
    },
    saveAgentSessionPolicy: async (input: AgentSessionPolicyDraft) =>
      transport.request<AgentSessionPolicyRevision>('/api/v1/admin/agent-session-policies', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admissionEnabled: input.admissionEnabled,
          maxConcurrency: input.maxConcurrency,
          maxTotalTokens: input.maxTotalTokens,
          maxCostUsd: input.maxCostUsd,
          maxDurationSeconds: input.maxDurationSeconds,
          retentionSeconds: input.retentionSeconds,
          allowedProviderIds: input.allowedProviderIds,
          allowedHarnessIds: input.allowedHarnessIds,
          allowedToolIds: input.allowedToolIds,
          namespace: input.namespace,
          applicationId: input.applicationId,
          expectedRevision: input.expectedRevision,
      }),
      }),
    exportAgentSessionProfile: async (namespace: string, agentKey: string) =>
      transport.request<AgentSessionProfileTransferBundle>(`/api/v1/admin/agent-session-transfers/profiles/${encodeURIComponent(namespace)}/${encodeURIComponent(agentKey)}/export`),
    planAgentSessionProfileTransfer: async (bundle: AgentSessionProfileTransferBundle, targetNamespace?: string) =>
      transport.request<AgentSessionProfileCompatibilityReport>('/api/v1/admin/agent-session-transfers/profiles/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bundle, targetNamespace }),
      }),
    importAgentSessionProfile: async (bundle: AgentSessionProfileTransferBundle, targetNamespace?: string) =>
      transport.request<AgentSessionProfileImportResult>('/api/v1/admin/agent-session-transfers/profiles/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bundle, targetNamespace }),
      }),
    exportAgentSessionTransfer: async (sessionId: string, mode: AgentSessionTransferMode, artifactDestinationRefs: Record<string, string> = {}) =>
      transport.request<AgentSessionTransferBundle>(`/api/v1/admin/agent-session-transfers/sessions/${encodeURIComponent(sessionId)}/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, artifactDestinationRefs }),
      }),
    planAgentSessionTransfer: async (bundle: AgentSessionTransferBundle, credentialRebindings: Record<string, string> = {}) =>
      transport.request<AgentSessionCompatibilityReport>('/api/v1/admin/agent-session-transfers/sessions/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bundle, credentialRebindings }),
      }),
    importAgentSessionTransfer: async (bundle: AgentSessionTransferBundle, credentialRebindings: Record<string, string> = {}) =>
      transport.request<AgentSessionImportResult>('/api/v1/admin/agent-session-transfers/sessions/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bundle, credentialRebindings }),
      }),
    agentSessionFleetActions: async (input: AgentSessionAdminActionRequest) =>
      transport.request<AgentSessionAdminActionResult>('/api/v1/admin/agent-sessions/actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      }),
  }
}
