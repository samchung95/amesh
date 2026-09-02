import type {
  AgentSessionDetailPage,
  AgentSessionSummary,
  ExecutionArtifact,
  ExecutionDetail,
  ExecutionEvidencePage,
  ExecutionEvidenceStreamEvent,
  ExecutionInterventionAction,
  ExecutionInterventionPreview,
  ExecutionInterventionRecord,
  FlowGraph,
  PersistedExecution,
  PersistedSubflow,
} from '../types'
import type { ApiTransport } from '../transport'
import type {
  BackfillPreview,
  BackfillRecord,
  BackfillSpec,
} from '../types'
import type {
  PromotionGate,
  PromotionTargetKind,
  ReleaseActionResult,
  ReleaseHistoryEntry,
  ReleaseTarget,
} from '../types'

export function createRuntimeResource(transport: ApiTransport) {
  return {
    executions: async () => transport.request<PersistedExecution[]>('/api/v1/executions?limit=200'),
    execution: async (executionId: string, taskOffset = 0, taskLimit = 250) =>
      transport.request<ExecutionDetail>(`/api/v1/executions/${encodeURIComponent(executionId)}?taskOffset=${String(taskOffset)}&taskLimit=${String(taskLimit)}`),
    executionAgentSessions: async (executionId: string) =>
      transport.request<AgentSessionSummary[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/agent-sessions`),
    executionAgentSessionDetail: async (
      executionId: string,
      taskRunId: string,
      attempt: number,
      afterEventIndex = 0,
      limit = 100,
    ) => transport.request<AgentSessionDetailPage>(
      `/api/v1/executions/${encodeURIComponent(executionId)}/agent-sessions/${encodeURIComponent(taskRunId)}?attempt=${String(attempt)}&afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`,
    ),
    executionGraph: async (executionId: string) =>
      transport.request<FlowGraph>(`/api/v1/executions/${encodeURIComponent(executionId)}/graph`),
    executionEvidence: async (executionId: string, cursor?: string) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      return transport.request<ExecutionEvidencePage>(`/api/v1/executions/${encodeURIComponent(executionId)}/evidence${suffix}`)
    },
    streamExecutionEvidence: async (
      executionId: string,
      cursor: string | null,
      onEvent: (event: ExecutionEvidenceStreamEvent) => void,
      signal: AbortSignal,
    ) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      await transport.streamNdjson<ExecutionEvidenceStreamEvent>(
        `/api/v1/executions/${encodeURIComponent(executionId)}/evidence/stream${suffix}`,
        onEvent,
        signal,
      )
    },
    executionSubflows: async (executionId: string) =>
      transport.request<PersistedSubflow[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/subflows`),
    executionParentSubflow: async (executionId: string) =>
      transport.request<PersistedSubflow | null>(`/api/v1/executions/${encodeURIComponent(executionId)}/parent-subflow`),
    executionInterventions: async (executionId: string) =>
      transport.request<ExecutionInterventionRecord[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/interventions`),
    executionFiles: async (executionId: string) =>
      transport.request<ExecutionArtifact[]>(`/api/v1/executions/${encodeURIComponent(executionId)}/files`),
    downloadExecutionFile: async (executionId: string, artifactId: string) =>
      transport.requestBlob(`/api/v1/executions/${encodeURIComponent(executionId)}/files/${encodeURIComponent(artifactId)}`),
    previewExecutionIntervention: async (
      executionId: string,
      action: ExecutionInterventionAction,
      checkpointTaskId?: string,
    ) => transport.request<ExecutionInterventionPreview>(`/api/v1/executions/${encodeURIComponent(executionId)}/interventions/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, ...(checkpointTaskId ? { checkpointTaskId } : {}) }),
    }),
    applyExecutionIntervention: async (
      executionId: string,
      preview: ExecutionInterventionPreview,
      reason: string,
    ) => transport.request<ExecutionDetail>(`/api/v1/executions/${encodeURIComponent(executionId)}/interventions`, {
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
    previewBackfill: async (spec: BackfillSpec) => transport.request<BackfillPreview>('/api/v1/backfills/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec),
    }),
    createBackfill: async (spec: BackfillSpec) => transport.request<BackfillRecord>('/api/v1/backfills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec),
    }),
    previewRelease: async (policyId: string) =>
      transport.request<PromotionGate>(`/api/v1/releases/policies/${encodeURIComponent(policyId)}/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approvals: {} }),
      }),
    applyRelease: async (policyId: string, expectedVersion: number, reason: string) =>
      transport.request<ReleaseActionResult>(`/api/v1/releases/policies/${encodeURIComponent(policyId)}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expectedVersion, reason, approvals: {} }),
      }),
    releaseTarget: async (targetKind: PromotionTargetKind, targetKey: string) =>
      transport.request<ReleaseTarget>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}`),
    releaseHistory: async (targetKind: PromotionTargetKind, targetKey: string) =>
      transport.request<ReleaseHistoryEntry[]>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/history`),
    rollbackRelease: async (
      targetKind: PromotionTargetKind,
      targetKey: string,
      toRevision: number,
      expectedVersion: number,
      reason: string,
    ) => transport.request<ReleaseActionResult>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/rollback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toRevision, expectedVersion, reason }),
    }),
    killSwitchRelease: async (
      targetKind: PromotionTargetKind,
      targetKey: string,
      expectedVersion: number,
      reason: string,
    ) => transport.request<ReleaseActionResult>(`/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/kill-switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expectedVersion, reason }),
    }),
  }
}
