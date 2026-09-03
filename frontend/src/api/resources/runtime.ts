import { apiOperation } from '../openapi'
import type {
  ExecutionEvidenceStreamEvent,
  ExecutionInterventionAction,
  ExecutionInterventionPreview,
} from '../types'
import type { ApiTransport } from '../transport'
import type { BackfillSpec } from '../types'
import type {
  PromotionTargetKind,
} from '../types'

export function createRuntimeResource(transport: ApiTransport) {
  return {
    executions: async () => transport.request(apiOperation('/api/v1/executions', 'get', '/api/v1/executions?limit=200')),
    execution: async (executionId: string, taskOffset = 0, taskLimit = 250) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}?taskOffset=${String(taskOffset)}&taskLimit=${String(taskLimit)}`)),
    executionAgentSessions: async (executionId: string) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}/agent-sessions', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/agent-sessions`)),
    executionAgentSessionDetail: async (
      executionId: string,
      taskRunId: string,
      attempt: number,
      afterEventIndex = 0,
      limit = 100,
    ) => transport.request(
      apiOperation('/api/v1/executions/{execution_id}/agent-sessions/{task_run_id}', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/agent-sessions/${encodeURIComponent(taskRunId)}?attempt=${String(attempt)}&afterEventIndex=${String(afterEventIndex)}&limit=${String(limit)}`),
    ),
    executionGraph: async (executionId: string) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}/graph', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/graph`)),
    executionEvidence: async (executionId: string, cursor?: string) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      return transport.request(apiOperation('/api/v1/executions/{execution_id}/evidence', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/evidence${suffix}`))
    },
    streamExecutionEvidence: async (
      executionId: string,
      cursor: string | null,
      onEvent: (event: ExecutionEvidenceStreamEvent) => void,
      signal: AbortSignal,
    ) => {
      const suffix = cursor ? `?cursor=${encodeURIComponent(cursor)}` : ''
      await transport.streamNdjson(
        apiOperation('/api/v1/executions/{execution_id}/evidence/stream', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/evidence/stream${suffix}`),
        onEvent,
        signal,
      )
    },
    executionSubflows: async (executionId: string) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}/subflows', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/subflows`)),
    executionParentSubflow: async (executionId: string) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}/parent-subflow', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/parent-subflow`)),
    executionInterventions: async (executionId: string) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}/interventions', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/interventions`)),
    executionFiles: async (executionId: string) =>
      transport.request(apiOperation('/api/v1/executions/{execution_id}/files', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/files`)),
    downloadExecutionFile: async (executionId: string, artifactId: string) =>
      transport.requestBlob(apiOperation('/api/v1/executions/{execution_id}/files/{artifact_id}', 'get', `/api/v1/executions/${encodeURIComponent(executionId)}/files/${encodeURIComponent(artifactId)}`)),
    previewExecutionIntervention: async (
      executionId: string,
      action: ExecutionInterventionAction,
      checkpointTaskId?: string,
    ) => transport.request(apiOperation('/api/v1/executions/{execution_id}/interventions/preview', 'post', `/api/v1/executions/${encodeURIComponent(executionId)}/interventions/preview`), {
      headers: { 'Content-Type': 'application/json' },
      json: { action, graceSeconds: 30, ...(checkpointTaskId ? { checkpointTaskId } : {}) },
    }),
    applyExecutionIntervention: async (
      executionId: string,
      preview: ExecutionInterventionPreview,
      reason: string,
    ) => transport.request(apiOperation('/api/v1/executions/{execution_id}/interventions', 'post', `/api/v1/executions/${encodeURIComponent(executionId)}/interventions`), {
      headers: { 'Content-Type': 'application/json' },
      json: {
        action: preview.action,
        checkpointTaskId: preview.checkpoint_task_id,
        expectedVersion: preview.current_version,
        expectedEpoch: preview.current_epoch,
        graceSeconds: 30,
        reason,
      },
    }),
    previewBackfill: async (spec: BackfillSpec) => transport.request(apiOperation('/api/v1/backfills/preview', 'post', '/api/v1/backfills/preview'), {
      headers: { 'Content-Type': 'application/json' },
      json: {
        ...spec,
        replaySources: spec.replaySources ?? [],
        selection: {
          ...spec.selection,
          occurrences: spec.selection.occurrences ?? [],
          partitions: spec.selection.partitions ?? [],
          sourceExecutionIds: spec.selection.sourceExecutionIds ?? [],
        },
      },
    }),
    createBackfill: async (spec: BackfillSpec) => transport.request(apiOperation('/api/v1/backfills', 'post', '/api/v1/backfills'), {
      headers: { 'Content-Type': 'application/json' },
      json: {
        ...spec,
        replaySources: spec.replaySources ?? [],
        selection: {
          ...spec.selection,
          occurrences: spec.selection.occurrences ?? [],
          partitions: spec.selection.partitions ?? [],
          sourceExecutionIds: spec.selection.sourceExecutionIds ?? [],
        },
      },
    }),
    previewRelease: async (policyId: string) =>
      transport.request(apiOperation('/api/v1/releases/policies/{policy_id}/preview', 'post', `/api/v1/releases/policies/${encodeURIComponent(policyId)}/preview`), {
        headers: { 'Content-Type': 'application/json' },
        json: { approvals: {} },
      }),
    applyRelease: async (policyId: string, expectedVersion: number, reason: string) =>
      transport.request(apiOperation('/api/v1/releases/policies/{policy_id}/apply', 'post', `/api/v1/releases/policies/${encodeURIComponent(policyId)}/apply`), {
        headers: { 'Content-Type': 'application/json' },
        json: { expectedVersion, reason, approvals: {} },
      }),
    releaseTarget: async (targetKind: PromotionTargetKind, targetKey: string) =>
      transport.request(apiOperation('/api/v1/releases/{target_kind}/{target_key}', 'get', `/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}`)),
    releaseHistory: async (targetKind: PromotionTargetKind, targetKey: string) =>
      transport.request(apiOperation('/api/v1/releases/{target_kind}/{target_key}/history', 'get', `/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/history`)),
    rollbackRelease: async (
      targetKind: PromotionTargetKind,
      targetKey: string,
      toRevision: number,
      expectedVersion: number,
      reason: string,
    ) => transport.request(apiOperation('/api/v1/releases/{target_kind}/{target_key}/rollback', 'post', `/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/rollback`), {
      headers: { 'Content-Type': 'application/json' },
      json: { toRevision, expectedVersion, reason },
    }),
    killSwitchRelease: async (
      targetKind: PromotionTargetKind,
      targetKey: string,
      expectedVersion: number,
      reason: string,
    ) => transport.request(apiOperation('/api/v1/releases/{target_kind}/{target_key}/kill-switch', 'post', `/api/v1/releases/${targetKind}/${encodeURIComponent(targetKey)}/kill-switch`), {
      headers: { 'Content-Type': 'application/json' },
      json: { expectedVersion, reason },
    }),
  }
}
