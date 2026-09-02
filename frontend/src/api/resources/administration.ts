import type {
  AdministrationAuditEntry,
  AdministrationControl,
  AdministrationControlDraft,
  AdministrationImpactPreview,
  Announcement,
  AnnouncementDraft,
  AdmissionDiagnostics,
  ConfigurationSnapshot,
  CredentialMetadata,
  FeatureFlag,
  OperationalControl,
  OperationalControlAction,
  OperationalControlDraft,
  OperationalControlEvent,
  NetworkDiagnosticBundle,
  PrincipalDefinition,
  RoleBinding,
  RoleDefinition,
  ServiceTopology,
  WorkerInventory,
  IssuedCredential,
} from '../types'

import type { ApiTransport } from '../transport'

export function createAdministrationResource(transport: ApiTransport) {

  return {
    principals: async () => transport.request<PrincipalDefinition[]>('/api/v1/admin/principals'),
    createPrincipal: async (principalType: PrincipalDefinition['principal_type'], handle: string, displayName: string) =>
      transport.request<PrincipalDefinition>('/api/v1/admin/principals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ principal_type: principalType, handle, display_name: displayName }),
      }),
    addGroupMember: async (groupId: string, memberId: string) =>
      transport.request<void>(`/api/v1/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(memberId)}`, { method: 'PUT' }),
    removeGroupMember: async (groupId: string, memberId: string) =>
      transport.request<void>(`/api/v1/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(memberId)}`, { method: 'DELETE' }),
    roles: async () => transport.request<RoleDefinition[]>('/api/v1/admin/roles'),
    saveRole: async (name: string, displayName: string, description: string, permissions: RoleDefinition['permissions']) =>
      transport.request<RoleDefinition>(`/api/v1/admin/roles/${encodeURIComponent(name)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, display_name: displayName, description, permissions }),
      }),
    bindings: async () => transport.request<RoleBinding[]>('/api/v1/admin/bindings'),
    createBinding: async (binding: Omit<RoleBinding, 'id'>) =>
      transport.request<RoleBinding>('/api/v1/admin/bindings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(binding),
      }),
    principalCredentials: async (principalId: string) =>
      transport.request<CredentialMetadata[]>(`/api/v1/admin/principals/${encodeURIComponent(principalId)}/credentials`),
    createCredential: async (principalId: string, name: string, scopes: string[], expiresAt: string) =>
      transport.request<IssuedCredential>(`/api/v1/admin/principals/${encodeURIComponent(principalId)}/credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, scopes, expiresAt, audience: 'amesh-api', rateLimitPerMinute: 600 }),
      }),
    topology: async () => transport.request<ServiceTopology>('/api/v1/operations/topology'),
    workers: async () => transport.request<WorkerInventory[]>('/api/v1/workers'),
    admissionDiagnostics: async () => transport.request<AdmissionDiagnostics>('/api/v1/admissions/diagnostics'),
    networkDiagnostics: async () => transport.request<NetworkDiagnosticBundle>('/api/v1/operations/network-diagnostics'),
    configuration: async () => transport.request<ConfigurationSnapshot>('/api/v1/configuration'),
    reloadConfiguration: async () => transport.request<ConfigurationSnapshot>('/api/v1/configuration/reload', { method: 'POST' }),
    featureFlags: async () => {
      const suffix = transport.connection.namespace ? `?namespace=${encodeURIComponent(transport.connection.namespace)}` : ''
      return transport.request<FeatureFlag[]>(`/api/v1/feature-flags${suffix}`)
    },
    saveFeatureFlag: async (key: string, enabled: boolean, description: string, expectedVersion?: number) =>
      transport.request<FeatureFlag>(`/api/v1/feature-flags/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scope: transport.connection.namespace ? 'NAMESPACE' : 'TENANT',
          enabled,
          tenantId: transport.connection.tenant,
          namespace: transport.connection.namespace || null,
          description,
          expectedVersion: expectedVersion || null,
        }),
      }),
    administrationControls: async () => transport.request<AdministrationControl[]>('/api/v1/admin/controls'),
    previewAdministrationControl: async (draft: AdministrationControlDraft) =>
      transport.request<AdministrationImpactPreview>('/api/v1/admin/controls/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    applyAdministrationControl: async (preview: AdministrationImpactPreview, confirmation: string) =>
      transport.request<AdministrationControl>(`/api/v1/admin/controls/${preview.draft.key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft: preview.draft, approval: preview.approval, confirmation }),
      }),
    administrationAudit: async () => transport.request<AdministrationAuditEntry[]>('/api/v1/admin/audit?limit=200'),
    announcements: async (namespace?: string, includeInactive = false) => {
      const params = new URLSearchParams()
      if (namespace) params.set('namespace', namespace)
      if (includeInactive) params.set('includeInactive', 'true')
      return transport.request<Announcement[]>(`/api/v1/announcements${params.size ? `?${params.toString()}` : ''}`)
    },
    publishAnnouncement: async (draft: AnnouncementDraft) =>
      transport.request<Announcement>('/api/v1/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    deactivateAnnouncement: async (announcementId: string, expectedVersion: number) =>
      transport.request<Announcement>(`/api/v1/announcements/${encodeURIComponent(announcementId)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    operationalControls: async () => transport.request<OperationalControl[]>('/api/v1/operational-controls'),
    activateOperationalControl: async (draft: OperationalControlDraft) =>
      transport.request<OperationalControl>('/api/v1/operational-controls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      }),
    changeOperationalControl: async (controlId: string, action: OperationalControlAction) =>
      transport.request<OperationalControl>(`/api/v1/operational-controls/${encodeURIComponent(controlId)}/actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      }),
    operationalControlEvents: async () => transport.request<OperationalControlEvent[]>('/api/v1/operational-control-events?limit=200'),
  }
}
