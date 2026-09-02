import type {
  ExecutionDetail,
  HumanTask,
  HumanTaskActionKind,
  HumanTaskNotification,
  WorkflowApp,
} from '../types'
import type { ApiTransport } from '../transport'
import type {
  AssetCatalogEntry,
  AssetDraft,
  AssetRecord,
} from '../types'

export function createGeneralResource(transport: ApiTransport) {
  return {
    apps: async (namespace?: string) =>
      transport.request<WorkflowApp[]>(`/api/v1/apps${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    app: async (namespace: string, appId: string) =>
      transport.request<WorkflowApp>(`/api/v1/apps/${encodeURIComponent(namespace)}/${encodeURIComponent(appId)}`),
    launchApp: async (namespace: string, appId: string, inputs: Record<string, unknown>) =>
      transport.request<ExecutionDetail>(`/api/v1/apps/${encodeURIComponent(namespace)}/${encodeURIComponent(appId)}/launch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputs, idempotencyKey: crypto.randomUUID() }),
      }),
    humanTasks: async (namespace?: string, includeClosed = false) => {
      const params = new URLSearchParams({ includeClosed: String(includeClosed) })
      if (namespace) params.set('namespace', namespace)
      return transport.request<HumanTask[]>(`/api/v1/human-tasks?${params.toString()}`)
    },
    actOnHumanTask: async (
      humanTaskId: string,
      action: HumanTaskActionKind,
      payload: { reason?: string; formValues?: Record<string, unknown>; comment?: string; artifactUri?: string },
    ) => transport.request<HumanTask>(`/api/v1/human-tasks/${encodeURIComponent(humanTaskId)}/actions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, idempotencyKey: crypto.randomUUID(), ...payload }),
    }),
    humanTaskNotifications: async () =>
      transport.request<HumanTaskNotification[]>('/api/v1/human-task-notifications'),
    assets: async (namespace?: string) =>
      transport.request<AssetRecord[]>(`/api/v1/assets${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
    asset: async (assetId: string) =>
      transport.request<AssetCatalogEntry>(`/api/v1/assets/${encodeURIComponent(assetId)}`),
    registerAsset: async (draft: AssetDraft) =>
      transport.request<AssetRecord>('/api/v1/assets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    exportAssetCatalog: async (namespace?: string) =>
      transport.requestBlob(`/api/v1/assets/export/openlineage${namespace ? `?namespace=${encodeURIComponent(namespace)}` : ''}`),
  }
}
