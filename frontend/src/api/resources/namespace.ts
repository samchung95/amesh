import { apiOperation, type ApiJsonRequestBody } from '../openapi'
import type { KeyValueType } from '../types'
import { filePath, imagePath, namespaceRoot } from '../transport'
import type { ApiTransport } from '../transport'
import type {
  AgentMcpConnectionSpec,
  AgentResourceKind,
  AgentResourceSpec,
} from '../types'

export function createNamespaceResource(transport: ApiTransport) {
  return {
    namespaceFiles: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/files', 'get', `${namespaceRoot(namespace)}/files`)),
    namespaceArtifacts: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/artifacts', 'get', `${namespaceRoot(namespace)}/artifacts`)),
    namespaceWorkflowMetadata: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/workflow-metadata', 'get', `${namespaceRoot(namespace)}/workflow-metadata`)),
    uploadNamespaceFile: async (namespace: string, path: string, file: File) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/files/{path}', 'put', filePath(namespace, path)), {
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
        rawBody: file,
      }),
    uploadNamespaceImage: async (namespace: string, path: string, file: File, altText?: string) => {
      const suffix = altText ? `?altText=${encodeURIComponent(altText)}` : ''
      return transport.request(apiOperation('/api/v1/namespaces/{namespace}/images/{path}', 'put', `${imagePath(namespace, path)}${suffix}`), {
        headers: { 'Content-Type': file.type || 'application/octet-stream' },
        rawBody: file,
      })
    },
    getNamespaceImage: async (namespace: string, path: string, version?: number) => {
      const suffix = version ? `?version=${String(version)}` : ''
      return transport.request(apiOperation('/api/v1/namespaces/{namespace}/images/{path}', 'get', `${imagePath(namespace, path)}${suffix}`))
    },
    downloadNamespaceFile: async (namespace: string, path: string, version?: number) =>
      transport.requestBlob(apiOperation('/api/v1/namespaces/{namespace}/files/{path}', 'get', `${filePath(namespace, path)}${version ? `?version=${String(version)}` : ''}`)),
    namespaceFileVersions: async (namespace: string, path: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/files/{path}/versions', 'get', `${filePath(namespace, path)}/versions`)),
    moveNamespaceFile: async (namespace: string, path: string, destinationPath: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/files/{path}/move', 'post', `${filePath(namespace, path)}/move`), {
        headers: { 'Content-Type': 'application/json' },
        json: { destinationPath, expectedVersion },
      }),
    deleteNamespaceFile: async (namespace: string, path: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/files/{path}', 'delete', `${filePath(namespace, path)}?expectedVersion=${String(expectedVersion)}`), { }),
    namespaceKeyValues: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/key-values', 'get', `${namespaceRoot(namespace)}/key-values`)),
    putNamespaceKeyValue: async (namespace: string, key: string, type: KeyValueType, value: unknown, expiresAt?: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/key-values/{key}', 'put', `${namespaceRoot(namespace)}/key-values/${encodeURIComponent(key)}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { type, value, expiresAt: expiresAt || null },
      }),
    deleteNamespaceKeyValue: async (namespace: string, key: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/key-values/{key}', 'delete', `${namespaceRoot(namespace)}/key-values/${encodeURIComponent(key)}?expectedVersion=${String(expectedVersion)}`), { }),
    namespaceSecretBindings: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/secret-bindings', 'get', `${namespaceRoot(namespace)}/secret-bindings`)),
    putNamespaceSecretBinding: async (namespace: string, key: string, providerReference: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/secret-bindings/{key}', 'put', `${namespaceRoot(namespace)}/secret-bindings/${encodeURIComponent(key)}`), {
        headers: { 'Content-Type': 'application/json' },
        json: { provider: 'env', providerReference },
      }),
    deleteNamespaceSecretBinding: async (namespace: string, key: string, expectedVersion: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/secret-bindings/{key}', 'delete', `${namespaceRoot(namespace)}/secret-bindings/${encodeURIComponent(key)}?expectedVersion=${String(expectedVersion)}`), { }),
    exportNamespaceResources: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/resource-bundle', 'get', `${namespaceRoot(namespace)}/resource-bundle`)),
    importNamespaceResources: async (
      namespace: string,
      bundle: ApiJsonRequestBody<'/api/v1/namespaces/{namespace}/resource-bundle', 'post'>,
    ) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/resource-bundle', 'post', `${namespaceRoot(namespace)}/resource-bundle`), {
        headers: { 'Content-Type': 'application/json' },
        json: bundle,
      }),
    agentResources: async (namespace: string, kind?: AgentResourceKind) => {
      const suffix = kind ? `?kind=${encodeURIComponent(kind)}` : ''
      return transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/resources', 'get', `${namespaceRoot(namespace)}/agent/resources${suffix}`))
    },
    agentMcpConnections: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/mcp-connections', 'get', `${namespaceRoot(namespace)}/agent/mcp-connections`)),
    agentCapabilityCatalog: async (namespace: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/capabilities/catalog', 'get', `${namespaceRoot(namespace)}/agent/capabilities/catalog`)),
    discoverAgentMcpConnection: async (namespace: string, input: { endpoint: string; credentialRef: string; timeoutSeconds?: number }) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/mcp-connections/discover', 'post', `${namespaceRoot(namespace)}/agent/mcp-connections/discover`), {
        headers: { 'Content-Type': 'application/json' },
        json: { ...input, timeoutSeconds: input.timeoutSeconds ?? 30 },
      }),
    createAgentMcpConnection: async (namespace: string, spec: AgentMcpConnectionSpec) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/mcp-connections', 'post', `${namespaceRoot(namespace)}/agent/mcp-connections`), {
        headers: { 'Content-Type': 'application/json' },
        json: spec,
      }),
    testAgentMcpConnection: async (namespace: string, key: string, revision: number, timeoutSeconds?: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test', 'post', `${namespaceRoot(namespace)}/agent/mcp-connections/${encodeURIComponent(key)}/test`), {
        headers: { 'Content-Type': 'application/json' },
        json: { revision, timeoutSeconds: timeoutSeconds ?? 30 },
      }),
    agentMcpTools: async (namespace: string, key: string, revision: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools', 'get', `${namespaceRoot(namespace)}/agent/mcp-connections/${encodeURIComponent(key)}/tools?revision=${String(revision)}`)),
    createAgentResource: async (namespace: string, spec: AgentResourceSpec) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/resources', 'post', `${namespaceRoot(namespace)}/agent/resources`), {
        headers: { 'Content-Type': 'application/json' },
        json: spec.kind === 'AGENT'
          ? {
              ...spec,
              hardLimits: { ...spec.hardLimits, ceilingMode: spec.hardLimits.ceilingMode ?? 'BOUNDED' },
              permissions: { ...spec.permissions, engineScopes: spec.permissions.engineScopes ?? [] },
              tools: spec.tools.map((tool) => ({ ...tool, providerKind: 'mcp' as const })),
            }
          : spec,
      }),
    agentResource: async (namespace: string, kind: AgentResourceKind, key: string, revision?: number) => {
      const suffix = revision ? `?revision=${String(revision)}` : ''
      return transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/resources/{kind}/{key}', 'get', `${namespaceRoot(namespace)}/agent/resources/${kind}/${encodeURIComponent(key)}${suffix}`))
    },
    resolveAgent: async (namespace: string, key: string, revision: number, subjectRef: string) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve', 'post', `${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/resolve`), {
        headers: { 'Content-Type': 'application/json' },
        json: { agentRevision: revision, subjectRef },
      }),
    previewAgent: async (namespace: string, key: string, revision: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/definitions/{key}/preview', 'get', `${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/preview?agentRevision=${String(revision)}`)),
    compareAgent: async (namespace: string, key: string, fromRevision: number, toRevision: number) =>
      transport.request(apiOperation('/api/v1/namespaces/{namespace}/agent/definitions/{key}/compare', 'get', `${namespaceRoot(namespace)}/agent/definitions/${encodeURIComponent(key)}/compare?fromRevision=${String(fromRevision)}&toRevision=${String(toRevision)}`)),
  }
}
