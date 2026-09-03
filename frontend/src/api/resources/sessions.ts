import { apiOperation, type ApiJsonRequestBody } from '../openapi'
import type {
  AgentSessionSummary,
  AgentSessionControlEventPage,
  AgentSessionControlSummary,
  AgentSessionControlRequest,
  AgentSessionAdminActionRequest,
  AgentSessionFleetQuery,
  AgentSessionPolicyDraft,
  AgentSessionTransferMode,
  AgentSessionCreateDraft,
  AgentSessionLaunchResponse,
  AgentSessionLifecycleState,
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
  ) => transport.request(
    apiOperation('/api/v1/agent-sessions/{service_session_id}/{action}', 'post', `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/${action}`),
    {
      headers: { 'Content-Type': 'application/json' },
      json: {
        graceSeconds: 30,
        ...control,
        reason: control?.reason || defaultReason,
      } satisfies AgentSessionControlPayload,
    },
  ).then(launchSummary)

  const agentSessionControlReason = (action: 'cancellation' | 'pause' | 'retry' | 'resume') => `Operator requested ${action}.`

  type AgentSessionDetailPath =
    | '/api/v1/agent-sessions/{service_session_id}'
    | '/api/v1/agent-sessions/{service_session_id}/events'
    | '/api/v1/agent-sessions/{service_session_id}/messages'

  const agentSessionControlDetail = (
    template: AgentSessionDetailPath,
    sessionId: string,
    suffix: string,
  ) => transport.request(
    apiOperation(template, 'get', `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}${suffix}`),
  )
  return {
    agentSessionHarnesses: async () => transport.request(apiOperation('/api/v1/agent-sessions/harnesses', 'get', '/api/v1/agent-sessions/harnesses')),
    agentSessions: async () => {
      const items = await transport.request(apiOperation('/api/v1/agent-sessions', 'get', '/api/v1/agent-sessions'))
      return items.map((item) => controlSummary(item.session, item.sessionId))
    },
    createAgentSession: async (input: AgentSessionCreateDraft) => {
      const launch = await transport.request(apiOperation('/api/v1/agent-sessions', 'post', '/api/v1/agent-sessions'), {
        headers: { 'Content-Type': 'application/json' },
        json: {
          ...input,
          agentRef: input.agentRef,
          businessAssertions: input.businessAssertions ?? [],
          dataHandling: input.dataHandling ?? 'DENY_SECRETS',
          input: input.input ?? {},
          invalidOutputPolicy: input.invalidOutputPolicy ?? 'FAIL',
          maxRepairAttempts: input.maxRepairAttempts ?? 0,
          memoryReadKeys: input.memoryReadKeys ?? [],
          runner: input.runner ?? 'local',
          timeoutMode: input.timeoutMode ?? 'BOUNDED',
        },
      })
      return launchSummary(launch)
    },
    agentSession: async (sessionId: string) =>
      agentSessionControlDetail(
        '/api/v1/agent-sessions/{service_session_id}',
        sessionId,
        '',
      ).then((page) => controlSummary(page.session, sessionId)),
    agentSessionEvents: async (sessionId: string, afterEventIndex = 0, limit = 100) => {
      const page = await agentSessionControlDetail(
        '/api/v1/agent-sessions/{service_session_id}/events',
        sessionId,
        `/events?afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`,
      )
      return { events: page.events, nextEventIndex: page.nextEventIndex } as AgentSessionControlEventPage
    },
    agentSessionProgress: async (sessionId: string, after?: string, limit = 100) => {
      const params = new URLSearchParams({ limit: String(limit) })
      if (after) params.set('after', after)
      return transport.request(apiOperation('/api/v1/agent-sessions/{service_session_id}/progress', 'get', `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/progress?${params.toString()}`))
    },
    streamAgentSessionProgress: async (
      sessionId: string,
      after: string | null,
      onItem: (item: AgentProgressStreamItem) => void,
      signal: AbortSignal,
    ) => {
      const suffix = after ? `?after=${encodeURIComponent(after)}` : ''
      await transport.streamNdjson(
        apiOperation('/api/v1/agent-sessions/{service_session_id}/progress/stream', 'get', `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/progress/stream${suffix}`),
        onItem,
        signal,
      )
    },
    agentSessionMessages: async (sessionId: string, afterEventIndex = 0, limit = 100) =>
      agentSessionControlDetail(
        '/api/v1/agent-sessions/{service_session_id}/messages',
        sessionId,
        `/messages?afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`,
      ),
    cancelAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'cancel', agentSessionControlReason('cancellation'), control),
    pauseAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'pause', agentSessionControlReason('pause'), control),
    retryAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'retry', agentSessionControlReason('retry'), control),
    resumeAgentSession: async (sessionId: string, control?: Partial<AgentSessionControlRequest>) =>
      postAgentSessionControl(sessionId, 'resume', agentSessionControlReason('resume'), control),
    agentSessionResult: async (sessionId: string) =>
      transport.request(apiOperation('/api/v1/agent-sessions/{service_session_id}/result', 'get', `/api/v1/agent-sessions/${encodeURIComponent(sessionId)}/result`)),
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
      return transport.request(apiOperation('/api/v1/admin/agent-sessions', 'get', `/api/v1/admin/agent-sessions${suffix}`))
    },
    agentSessionInstanceAggregate: async () =>
      transport.request(apiOperation('/api/v1/admin/agent-sessions/aggregate', 'get', '/api/v1/admin/agent-sessions/aggregate')),
    agentSessionPolicies: async (namespace?: string, applicationId?: string) => {
      const params = new URLSearchParams()
      if (namespace) params.set('namespace', namespace)
      if (applicationId) params.set('applicationId', applicationId)
      params.set('limit', '100')
      return transport.request(apiOperation('/api/v1/admin/agent-session-policies', 'get', `/api/v1/admin/agent-session-policies?${params.toString()}`))
    },
    effectiveAgentSessionPolicies: async (namespace: string, applicationId?: string) => {
      const params = new URLSearchParams({ namespace })
      if (applicationId) params.set('applicationId', applicationId)
      return transport.request(apiOperation('/api/v1/admin/agent-session-policies/effective', 'get', `/api/v1/admin/agent-session-policies/effective?${params.toString()}`))
    },
    saveAgentSessionPolicy: async (input: AgentSessionPolicyDraft) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-policies', 'put', '/api/v1/admin/agent-session-policies'), {
        headers: { 'Content-Type': 'application/json' },
        json: {
          admissionEnabled: input.admissionEnabled,
          ceilingMode: input.ceilingMode ?? 'BOUNDED',
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
      },
      }),
    exportAgentSessionProfile: async (namespace: string, agentKey: string) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export', 'get', `/api/v1/admin/agent-session-transfers/profiles/${encodeURIComponent(namespace)}/${encodeURIComponent(agentKey)}/export`)),
    planAgentSessionProfileTransfer: async (
      bundle: ApiJsonRequestBody<'/api/v1/admin/agent-session-transfers/profiles/plan', 'post'>['bundle'],
      targetNamespace?: string,
    ) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-transfers/profiles/plan', 'post', '/api/v1/admin/agent-session-transfers/profiles/plan'), {
        headers: { 'Content-Type': 'application/json' },
        json: { bundle, targetNamespace },
      }),
    importAgentSessionProfile: async (
      bundle: ApiJsonRequestBody<'/api/v1/admin/agent-session-transfers/profiles/import', 'post'>['bundle'],
      targetNamespace?: string,
    ) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-transfers/profiles/import', 'post', '/api/v1/admin/agent-session-transfers/profiles/import'), {
        headers: { 'Content-Type': 'application/json' },
        json: { bundle, targetNamespace },
      }),
    exportAgentSessionTransfer: async (sessionId: string, mode: AgentSessionTransferMode, artifactDestinationRefs: Record<string, string> = {}) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-transfers/sessions/{session_id}/export', 'post', `/api/v1/admin/agent-session-transfers/sessions/${encodeURIComponent(sessionId)}/export`), {
        headers: { 'Content-Type': 'application/json' },
        json: { mode, artifactDestinationRefs },
      }),
    planAgentSessionTransfer: async (
      bundle: ApiJsonRequestBody<'/api/v1/admin/agent-session-transfers/sessions/plan', 'post'>['bundle'],
      credentialRebindings: Record<string, string> = {},
    ) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-transfers/sessions/plan', 'post', '/api/v1/admin/agent-session-transfers/sessions/plan'), {
        headers: { 'Content-Type': 'application/json' },
        json: { bundle, credentialRebindings },
      }),
    importAgentSessionTransfer: async (
      bundle: ApiJsonRequestBody<'/api/v1/admin/agent-session-transfers/sessions/import', 'post'>['bundle'],
      credentialRebindings: Record<string, string> = {},
    ) =>
      transport.request(apiOperation('/api/v1/admin/agent-session-transfers/sessions/import', 'post', '/api/v1/admin/agent-session-transfers/sessions/import'), {
        headers: { 'Content-Type': 'application/json' },
        json: { bundle, credentialRebindings },
      }),
    agentSessionFleetActions: async (input: AgentSessionAdminActionRequest) =>
      transport.request(apiOperation('/api/v1/admin/agent-sessions/actions', 'post', '/api/v1/admin/agent-sessions/actions'), {
        headers: { 'Content-Type': 'application/json' },
        json: input,
      }),
  }
}
