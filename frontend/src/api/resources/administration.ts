import { apiOperation } from '../openapi'
import type {
  AdministrationControlDraft,
  AdministrationImpactPreview,
  AnnouncementDraft,
  OperationalControlAction,
  OperationalControlDraft,
  PrincipalDefinition,
  RoleBinding,
  RoleDefinition,
  CheckedOmit,
} from '../types'

import type { ApiTransport } from '../transport'

export function createAdministrationResource(transport: ApiTransport) {

  return {
    principals: async () => transport.request(apiOperation('/api/v1/admin/principals', 'get', '/api/v1/admin/principals')),
    createPrincipal: async (principalType: PrincipalDefinition['principal_type'], handle: string, displayName: string) =>
      transport.request(apiOperation('/api/v1/admin/principals', 'post', '/api/v1/admin/principals'), {
        headers: { 'Content-Type': 'application/json' },
        json: { principal_type: principalType, handle, display_name: displayName, enabled: true },
      }),
    addGroupMember: async (groupId: string, memberId: string) =>
      transport.request(apiOperation('/api/v1/admin/groups/{group_id}/members/{member_id}', 'put', `/api/v1/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(memberId)}`), { }),
    removeGroupMember: async (groupId: string, memberId: string) =>
      transport.request(apiOperation('/api/v1/admin/groups/{group_id}/members/{member_id}', 'delete', `/api/v1/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(memberId)}`), { }),
    roles: async () => transport.request(apiOperation('/api/v1/admin/roles', 'get', '/api/v1/admin/roles')),
    saveRole: async (name: string, displayName: string, description: string, permissions: RoleDefinition['permissions']) =>
      transport.request(apiOperation('/api/v1/admin/roles/{role_name}', 'put', `/api/v1/admin/roles/${encodeURIComponent(name)}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { name, display_name: displayName, description, permissions, built_in: false },
      }),
    bindings: async () => transport.request(apiOperation('/api/v1/admin/bindings', 'get', '/api/v1/admin/bindings')),
    createBinding: async (binding: CheckedOmit<RoleBinding, 'id'>) =>
      transport.request(apiOperation('/api/v1/admin/bindings', 'post', '/api/v1/admin/bindings'), {
        headers: { 'Content-Type': 'application/json' },
        json: binding,
      }),
    principalCredentials: async (principalId: string) =>
      transport.request(apiOperation('/api/v1/admin/principals/{principal_id}/credentials', 'get', `/api/v1/admin/principals/${encodeURIComponent(principalId)}/credentials`)),
    createCredential: async (principalId: string, name: string, scopes: string[], expiresAt: string) =>
      transport.request(apiOperation('/api/v1/admin/principals/{principal_id}/credentials', 'post', `/api/v1/admin/principals/${encodeURIComponent(principalId)}/credentials`), {
        headers: { 'Content-Type': 'application/json' },
        json: { name, scopes, expiresAt, audience: 'amesh-api', rateLimitPerMinute: 600 },
      }),
    topology: async () => transport.request(apiOperation('/api/v1/operations/topology', 'get', '/api/v1/operations/topology')),
    workers: async () => transport.request(apiOperation('/api/v1/workers', 'get', '/api/v1/workers')),
    admissionDiagnostics: async () => transport.request(apiOperation('/api/v1/admissions/diagnostics', 'get', '/api/v1/admissions/diagnostics')),
    networkDiagnostics: async () => transport.request(apiOperation('/api/v1/operations/network-diagnostics', 'get', '/api/v1/operations/network-diagnostics')),
    configuration: async () => transport.request(apiOperation('/api/v1/configuration', 'get', '/api/v1/configuration')),
    reloadConfiguration: async () => transport.request(apiOperation('/api/v1/configuration/reload', 'post', '/api/v1/configuration/reload'), { }),
    featureFlags: async () => {
      const suffix = transport.connection.namespace ? `?namespace=${encodeURIComponent(transport.connection.namespace)}` : ''
      return transport.request(apiOperation('/api/v1/feature-flags', 'get', `/api/v1/feature-flags${suffix}`))
    },
    saveFeatureFlag: async (key: string, enabled: boolean, description: string, expectedVersion?: number) =>
      transport.request(apiOperation('/api/v1/feature-flags/{key}', 'put', `/api/v1/feature-flags/${encodeURIComponent(key)}`), {
        headers: { 'Content-Type': 'application/json' },
        json: {
          scope: transport.connection.namespace ? 'NAMESPACE' : 'TENANT',
          enabled,
          tenantId: transport.connection.tenant,
          namespace: transport.connection.namespace || null,
          description,
          expectedVersion: expectedVersion || null,
        },
      }),
    administrationControls: async () => transport.request(apiOperation('/api/v1/admin/controls', 'get', '/api/v1/admin/controls')),
    previewAdministrationControl: async (draft: AdministrationControlDraft) =>
      transport.request(apiOperation('/api/v1/admin/controls/preview', 'post', '/api/v1/admin/controls/preview'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    applyAdministrationControl: async (preview: AdministrationImpactPreview, confirmation: string) =>
      transport.request(apiOperation('/api/v1/admin/controls/{key}', 'put', `/api/v1/admin/controls/${preview.draft.key}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { draft: preview.draft, approval: preview.approval, confirmation },
      }),
    administrationAudit: async () => transport.request(apiOperation('/api/v1/admin/audit', 'get', '/api/v1/admin/audit?limit=200')),
    announcements: async (namespace?: string, includeInactive = false) => {
      const params = new URLSearchParams()
      if (namespace) params.set('namespace', namespace)
      if (includeInactive) params.set('includeInactive', 'true')
      return transport.request(apiOperation('/api/v1/announcements', 'get', `/api/v1/announcements${params.size ? `?${params.toString()}` : ''}`))
    },
    publishAnnouncement: async (draft: AnnouncementDraft) =>
      transport.request(apiOperation('/api/v1/announcements', 'post', '/api/v1/announcements'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    deactivateAnnouncement: async (announcementId: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/announcements/{announcement_id}', 'delete', `/api/v1/announcements/${encodeURIComponent(announcementId)}?expectedVersion=${String(expectedVersion)}`), { }),
    operationalControls: async () => transport.request(apiOperation('/api/v1/operational-controls', 'get', '/api/v1/operational-controls')),
    activateOperationalControl: async (draft: OperationalControlDraft) =>
      transport.request(apiOperation('/api/v1/operational-controls', 'post', '/api/v1/operational-controls'), {
        headers: { 'Content-Type': 'application/json' },
        json: draft,
      }),
    changeOperationalControl: async (controlId: string, action: OperationalControlAction) =>
      transport.request(apiOperation('/api/v1/operational-controls/{control_id}/actions', 'post', `/api/v1/operational-controls/${encodeURIComponent(controlId)}/actions`), {
        headers: { 'Content-Type': 'application/json' },
        json: action,
      }),
    operationalControlEvents: async () => transport.request(apiOperation('/api/v1/operational-control-events', 'get', '/api/v1/operational-control-events?limit=200')),
  }
}
