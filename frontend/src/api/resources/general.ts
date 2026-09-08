import { apiOperation } from '../openapi'
import type {
  HumanTaskActionKind,
} from '../types'
import type { ApiTransport } from '../transport'
import type { AssetDraft } from '../types'

export function createGeneralResource(transport: ApiTransport) {
  return {
    apps: async (namespace?: string) =>
      transport.request(apiOperation('/api/v1/apps', 'get', `/api/v1/apps`, { namespace: namespace || undefined })),
    app: async (namespace: string, appId: string) =>
      transport.request(apiOperation('/api/v1/apps/{namespace}/{app_id}', 'get', `/api/v1/apps/${encodeURIComponent(namespace)}/${encodeURIComponent(appId)}`)),
    launchApp: async (namespace: string, appId: string, inputs: Record<string, unknown>) =>
      transport.request(apiOperation('/api/v1/apps/{namespace}/{app_id}/launch', 'post', `/api/v1/apps/${encodeURIComponent(namespace)}/${encodeURIComponent(appId)}/launch`), {
        headers: { 'Content-Type': 'application/json' },
        json: { inputs, idempotencyKey: crypto.randomUUID() },
      }),
    humanTasks: async (namespace?: string, includeClosed = false) => {
      return transport.request(apiOperation('/api/v1/human-tasks', 'get', `/api/v1/human-tasks`, { includeClosed, namespace: namespace || undefined }))
    },
    actOnHumanTask: async (
      humanTaskId: string,
      action: HumanTaskActionKind,
      payload: { reason?: string; formValues?: Record<string, unknown>; comment?: string; artifactUri?: string },
    ) => transport.request(apiOperation('/api/v1/human-tasks/{human_task_id}/actions', 'post', `/api/v1/human-tasks/${encodeURIComponent(humanTaskId)}/actions`), {
      headers: { 'Content-Type': 'application/json' },
      json: {
        action,
        assigneeIds: [],
        comment: '',
        groupIds: [],
        idempotencyKey: crypto.randomUUID(),
        reason: '',
        ...payload,
      },
    }),
    humanTaskNotifications: async () =>
      transport.request(apiOperation('/api/v1/human-task-notifications', 'get', '/api/v1/human-task-notifications')),
    assets: async (namespace?: string) =>
      transport.request(apiOperation('/api/v1/assets', 'get', `/api/v1/assets`, { namespace: namespace || undefined })),
    asset: async (assetId: string) =>
      transport.request(apiOperation('/api/v1/assets/{asset_id}', 'get', `/api/v1/assets/${encodeURIComponent(assetId)}`)),
    registerAsset: async (draft: AssetDraft) =>
      transport.request(apiOperation('/api/v1/assets', 'post', '/api/v1/assets'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    exportAssetCatalog: async (namespace?: string) =>
      transport.requestBlob(apiOperation('/api/v1/assets/export/openlineage', 'get', `/api/v1/assets/export/openlineage`, { namespace: namespace || undefined })),
  }
}
