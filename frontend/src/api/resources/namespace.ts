import type {
  ImageArtifactRef,
  ArtifactRef,
  NamespaceFile,
  NamespaceFileVersion,
  NamespaceWorkflowMetadataView,
  KeyValueEntry,
  KeyValueType,
  SecretBinding,
} from '../types'
import { filePath, imagePath, namespaceRoot } from '../transport'
import type { ApiTransport } from '../transport'
import type {
  AgentCapabilityPin,
  AgentCapabilityCatalog,
  AgentEnvelopePreview,
  AgentMcpConnectionSpec,
  AgentMcpConnectionTestResult,
  AgentMcpDiscoveryResult,
  AgentMcpConnectionRevision,
  AgentMcpToolCatalogEntry,
  AgentResourceKind,
  AgentResourceRevision,
  AgentResourceSpec,
  AgentRevisionComparison,
} from '../types'

export function createNamespaceResource(transport: ApiTransport) {
  return {
    namespaceFiles: async (namespace: string) =>
      transport.request<NamespaceFile[]>(`${namespaceRoot(namespace)}/files`),
    namespaceArtifacts: async (namespace: string) =>
      transport.request<ArtifactRef[]>(`${namespaceRoot(namespace)}/artifacts`),
    namespaceWorkflowMetadata: async (namespace: string) =>
      transport.request<NamespaceWorkflowMetadataView>(`${namespaceRoot(namespace)}/workflow-metadata`),
    uploadNamespaceFile: async (namespace: string, path: string, file: File) =>
      transport.request<NamespaceFile>(filePath(namespace, path), {
        method: 'PUT',
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
        body: file,
      }),
    uploadNamespaceImage: async (namespace: string, path: string, file: File, altText?: string) => {
      const suffix = altText ? `?altText=${encodeURIComponent(altText)}` : ''
      return transport.request<ImageArtifactRef>(`${imagePath(namespace, path)}${suffix}`, {
        method: 'PUT',
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
        body: file,
      })
    },
    getNamespaceImage: async (namespace: string, path: string, version?: number) => {
      const suffix = version ? `?version=${String(version)}` : ''
      return transport.request<ImageArtifactRef>(`${imagePath(namespace, path)}${suffix}`)
    },
    downloadNamespaceFile: async (namespace: string, path: string, version?: number) =>
      transport.requestBlob(`${filePath(namespace, path)}${version ? `?version=${String(version)}` : ''}`),
    namespaceFileVersions: async (namespace: string, path: string) =>
      transport.request<NamespaceFileVersion[]>(`${filePath(namespace, path)}/versions`),
    moveNamespaceFile: async (namespace: string, path: string, destinationPath: string, expectedVersion: number) =>
      transport.request<NamespaceFile>(`${filePath(namespace, path)}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destinationPath, expectedVersion }),
      }),
    deleteNamespaceFile: async (namespace: string, path: string, expectedVersion: number) =>
      transport.request<void>(`${filePath(namespace, path)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    namespaceKeyValues: async (namespace: string) =>
      transport.request<KeyValueEntry[]>(`${namespaceRoot(namespace)}/key-values`),
    putNamespaceKeyValue: async (namespace: string, key: string, type: KeyValueType, value: unknown, expiresAt?: string) =>
      transport.request<KeyValueEntry>(`${namespaceRoot(namespace)}/key-values/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, value, expiresAt: expiresAt || null }),
      }),
    deleteNamespaceKeyValue: async (namespace: string, key: string, expectedVersion: number) =>
      transport.request<void>(`${namespaceRoot(namespace)}/key-values/${encodeURIComponent(key)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    namespaceSecretBindings: async (namespace: string) =>
      transport.request<SecretBinding[]>(`${namespaceRoot(namespace)}/secret-bindings`),
    putNamespaceSecretBinding: async (namespace: string, key: string, providerReference: string) =>
      transport.request<SecretBinding>(`${namespaceRoot(namespace)}/secret-bindings/${encodeURIComponent(key)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'env', providerReference }),
      }),
    deleteNamespaceSecretBinding: async (namespace: string, key: string, expectedVersion: number) =>
      transport.request<void>(`${namespaceRoot(namespace)}/secret-bindings/${encodeURIComponent(key)}?expectedVersion=${String(expectedVersion)}`, { method: 'DELETE' }),
    exportNamespaceResources: async (namespace: string) =>
      transport.request<Record<string, unknown>>(`${namespaceRoot(namespace)}/resource-bundle`),
    importNamespaceResources: async (namespace: string, bundle: Record<string, unknown>) =>
      transport.request<Record<string, number>>(`${namespaceRoot(namespace)}/resource-bundle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bundle),
      }),
    agentResources: async (namespace: string, kind?: AgentResourceKind) => {
      const suffix = kind ? `?kind=${encodeURIComponent(kind)}` : ''
      return transport.request<AgentResourceRevision[]>(`${namespaceRoot(namespace)}/agent/resources${suffix}`)
    },
    agentMcpConnections: async (namespace: string) =>
      transport.request<AgentMcpConnectionRevision[]>(`${namespaceRoot(namespace)}/agent/mcp-connections`),
    agentCapabilityCatalog: async (namespace: string) =>
      transport.request<AgentCapabilityCatalog>(`${namespaceRoot(namespace)}/agent/capabilities/catalog`),
    discoverAgentMcpConnection: async (namespace: string, input: { endpoint: string; credentialRef: string; timeoutSeconds?: number }) =>
      transport.request<AgentMcpDiscoveryResult>(`${namespaceRoot(namespace)}/agent/mcp-connections/discover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      }),
    createAgentMcpConnection: async (namespace: string, spec: AgentMcpConnectionSpec) =>
      transport.request<AgentMcpConnectionRevision>(`${namespaceRoot(namespace)}/agent/mcp-connections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec),
      }),
    testAgentMcpConnection: async (namespace: string, key: string, revision: number, timeoutSeconds?: number) =>
      transport.request<AgentMcpConnectionTestResult>(`${namespaceRoot(namespace)}/agent/mcp-connections/${encodeURIComponent(key)}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ revision, ...(timeoutSeconds === undefined ? {} : { timeoutSeconds }) }),
      }),
    agentMcpTools: async (namespace: string, key: string, revision: number) =>
      transport.request<AgentMcpToolCatalogEntry[]>(`${namespaceRoot(namespace)}/agent/mcp-connections/${encodeURIComponent(key)}/tools?revision=${String(revision)}`),
    createAgentResource: async (namespace: string, spec: AgentResourceSpec) =>
      transport.request<AgentResourceRevision>(`${namespaceRoot(namespace)}/agent/resources`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spec),
      }),
    agentResource: async (namespace: string, kind: AgentResourceKind, key: string, revision?: number) => {
      const suffix = revision ? `?revision=${String(revision)}` : ''
      return transport.request<AgentResourceRevision>(`${namespaceRoot(namespace)}/agent/resources/${kind}/${encodeURIComponent(key)}${suffix}`)
    },
    resolveAgent: async (namespace: string, key: string, revision: number, subjectRef: string) =>
      transport.request<AgentCapabilityPin>(`${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentRevision: revision, subjectRef }),
      }),
    previewAgent: async (namespace: string, key: string, revision: number) =>
      transport.request<AgentEnvelopePreview>(`${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/preview?agentRevision=${String(revision)}`),
    compareAgent: async (namespace: string, key: string, fromRevision: number, toRevision: number) =>
      transport.request<AgentRevisionComparison>(`${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/compare?fromRevision=${String(fromRevision)}&toRevision=${String(toRevision)}`),
  }
}
