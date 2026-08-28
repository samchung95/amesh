import { describe, expect, it } from 'vitest'
import { parse } from 'yaml'

import type { AgentResourceRevision, ArtifactRef, FlowEditorSchema } from '../api/types'
import {
  addGuidedStep,
  createIntentSource,
  hasRoundTripDocument,
  readGuidedWorkflow,
  isGuidedRequestCompatible,
  updateGuidedAgentSelection,
  updateGuidedIdentity,
  updateGuidedOutput,
  updateGuidedTask,
  updateGuidedTaskField,
  updateGuidedDocumentArtifact,
  updateGuidedTrigger,
} from './guidedWorkflowModel'

const schema: FlowEditorSchema = {
  schemaVersion: 'amesh.flow-editor/v1',
  flowSchema: {},
  resourceCatalog: {
    schemaVersion: 'amesh.resource-catalog/v1',
    resources: [
      { type: 'core.return', kind: 'task', configurationSchema: { type: 'object', properties: { value: {} } }, editor: { title: 'Return value', description: 'Return output.', category: 'Core', propertyOrder: ['value'] } },
      { type: 'core.log', kind: 'task', configurationSchema: { type: 'object', properties: { message: { type: 'string' } }, required: ['message'] }, editor: { title: 'Log message', description: 'Write a log.', category: 'Core', propertyOrder: ['message'] } },
    ],
  },
  expressionContext: {},
}

const artifact: ArtifactRef = {
  schemaVersion: 'amesh.artifact-ref/v1',
  reference: `nsfile:///documents/report.pdf?version=2&sha256=${'c'.repeat(64)}`,
  contentAddress: `sha256:${'c'.repeat(64)}`,
  tenantId: 'default',
  namespace: 'examples',
  path: 'documents/report.pdf',
  version: 2,
  mediaType: 'application/pdf',
  sizeBytes: 128,
  checksumSha256: 'c'.repeat(64),
  provenance: { source: 'namespace-file', originNamespace: 'examples', createdBy: 'operator', createdAt: '2026-08-26T00:00:00Z', lineage: [] },
  retention: { retentionUntil: null, legalHold: false },
}

describe('guided workflow YAML projection', () => {
  it('creates every intent as ordinary canonical YAML', () => {
    for (const intent of ['scheduled', 'webhook', 'pipeline', 'approval', 'agent', 'blank'] as const) {
      const source = createIntentSource(intent, 'examples.guided', '00000000-0000-7000-8000-000000000002')
      const document = parse(source) as Record<string, unknown>
      expect(document).toMatchObject({ namespace: 'examples.guided', revision: 1 })
      expect(Array.isArray(document.tasks)).toBe(true)
      expect(hasRoundTripDocument(source)).toBe(true)
    }
  })

  it('creates an agent session starter with an exact definition revision and bounded context policy', () => {
    const agent = { key: 'researcher', revision: 3, kind: 'AGENT', spec: { kind: 'AGENT', title: 'Evidence researcher', description: 'Research safely.', inputSchema: { type: 'object' } } } as unknown as AgentResourceRevision
    const document = parse(createIntentSource('agent', 'examples.guided', '00000000-0000-7000-8000-000000000002', [agent])) as Record<string, unknown>
    expect(document.tasks).toMatchObject([
      { type: 'agent.session', agent: 'researcher', agentRevision: 3, input: { request: '{{ inputs.request }}' }, contract: { secretScopes: [] }, contextPolicy: { maxMessages: 64, maxBytes: 262144, maxEstimatedTokens: 65536 } },
      { type: 'core.return', dependsOn: ['run_agent'], value: '{{ outputs.run_agent.result }}' },
    ])
  })

  it('uses the exact compatible agent selected by a catalog attachment', () => {
    const first = { key: 'alpha', revision: 1, kind: 'AGENT', spec: { kind: 'AGENT', title: 'Alpha', inputSchema: { type: 'object' } } } as unknown as AgentResourceRevision
    const selected = { key: 'zeta', revision: 4, kind: 'AGENT', spec: { kind: 'AGENT', title: 'Zeta', inputSchema: { type: 'object' } } } as unknown as AgentResourceRevision
    const document = parse(createIntentSource('agent', 'examples.guided', '00000000-0000-7000-8000-000000000002', [first, selected], 'zeta@4')) as Record<string, unknown>
    expect((document.tasks as Record<string, unknown>[])[0]).toMatchObject({ type: 'agent.session', agent: 'zeta', agentRevision: 4 })
  })

  it('preserves unsupported agent YAML fields while changing guided context controls', () => {
    const source = `id: agent_flow\nnamespace: examples\ntasks:\n  - id: run\n    type: agent.session\n    agent: researcher\n    agentRevision: 1\n    input: {}\n    x-runtime-note: keep-me\n    contextPolicy:\n      maxMessages: 64\n      maxBytes: 262144\n      maxEstimatedTokens: 65536\n`
    const updated = updateGuidedTaskField(source, 0, ['contextPolicy', 'maxMessages'], 96)
    expect(parse(updated)).toMatchObject({ tasks: [{ 'x-runtime-note': 'keep-me', contextPolicy: { maxMessages: 96 } }] })
  })

  it('filters agent definitions whose required input is not the guided request mapping', () => {
    const compatible = { kind: 'AGENT', spec: { kind: 'AGENT', inputSchema: { type: 'object', required: ['request'] } } } as unknown as AgentResourceRevision
    const incompatible = { kind: 'AGENT', spec: { kind: 'AGENT', inputSchema: { type: 'object', required: ['incident'] } } } as unknown as AgentResourceRevision
    expect(isGuidedRequestCompatible(compatible)).toBe(true)
    expect(isGuidedRequestCompatible(incompatible)).toBe(false)
  })

  it('updates the exact agent revision and its credential contract together', () => {
    const source = `id: agent_flow\nnamespace: examples\ntasks:\n  - id: run\n    type: agent.session\n    agent: old\n    agentRevision: 1\n    input: {}\n    contract:\n      secretScopes: [old-key]\n`
    const updated = updateGuidedAgentSelection(source, 0, 'new', 4, ['new-key'])
    expect(parse(updated)).toMatchObject({ tasks: [{ agent: 'new', agentRevision: 4, contract: { secretScopes: ['new-key'] } }] })
  })

  it('round-trips guided changes without removing comments or code-only fields', () => {
    const source = `# operator note\nid: original\nnamespace: examples\nx-owner: data\ntasks:\n  - id: first\n    type: core.return\n    value: ok\n`
    const renamed = updateGuidedIdentity(source, 'id', 'renamed')
    const withStep = addGuidedStep(renamed, schema)
    const connected = updateGuidedTask(withStep, schema, 1, { dependsOn: 'first' })
    const output = updateGuidedOutput(connected, 'publish')
    expect(output).toContain('# operator note')
    expect(output).toContain('x-owner: data')
    expect(readGuidedWorkflow(output)).toMatchObject({ id: 'renamed', outputTaskId: 'publish', advancedPaths: ['x-owner'] })
  })

  it('uses catalog-derived required defaults when a guided step type changes', () => {
    const source = createIntentSource('blank', 'examples', '00000000-0000-7000-8000-000000000002')
    const updated = updateGuidedTask(source, schema, 0, { type: 'core.log' })
    expect(parse(updated)).toMatchObject({ tasks: [{ id: 'done', type: 'core.log', message: '' }] })
  })

  it('binds a document extractor to the complete artifact reference and input file map', () => {
    const source = `id: document_flow\nnamespace: examples\ntasks:\n  - id: extract\n    type: core.document.extract\n`
    const updated = updateGuidedDocumentArtifact(source, 0, artifact)
    expect(parse(updated)).toMatchObject({ tasks: [{ artifact, source: 'document.pdf', inputFiles: { 'document.pdf': artifact.reference } }] })
    expect(readGuidedWorkflow(updated).tasks[0]).toMatchObject({ artifact, source: 'document.pdf' })
  })


  it('replaces the previous input file key when a document source name changes', () => {
    const source = `id: document_flow\nnamespace: examples\ntasks:\n  - id: extract\n    type: core.document.extract\n    source: document.pdf\n    inputFiles:\n      document.pdf: old-reference\n`
    const updated = updateGuidedDocumentArtifact(source, 0, artifact, 'report.pdf')
    expect(parse(updated)).toMatchObject({ tasks: [{ source: 'report.pdf', inputFiles: { 'report.pdf': artifact.reference } }] })
    const parsed = parse(updated) as { tasks: Array<{ inputFiles: Record<string, unknown> }> }
    expect(parsed.tasks[0]?.inputFiles).not.toHaveProperty('document.pdf')
  })

  it('switches trigger types using valid starter configuration', () => {
    const source = createIntentSource('blank', 'examples', '00000000-0000-7000-8000-000000000002')
    const scheduled = parse(updateGuidedTrigger(source, 'core.cron')) as Record<string, unknown>
    expect(scheduled.triggers).toEqual([{ id: 'start', type: 'core.cron', cron: '0 9 * * *', timezone: 'UTC' }])
  })
})
