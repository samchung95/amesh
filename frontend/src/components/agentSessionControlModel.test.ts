import { describe, expect, it } from 'vitest'

import type { AgentResourceRevision, AgentSessionControlSummary, AgentSessionLifecycleState } from '../api/types'
import { agentPinnedProfile, agentResourceOptions, currentHarnessAlias, harnessCatalogOptions, mergeSessionSummary, sessionCanCancel, sessionCanPause, sessionCanResume, sessionCanRetry, sessionEventLabel, sessionHarnessLabel, sessionIsLive, sessionStateLabel } from './agentSessionControlModel'

const resource = (kind: AgentResourceRevision['kind'], key: string, revision: number): AgentResourceRevision => {
  const spec = {
    kind,
    key,
    namespace: 'demo',
    title: key,
    ...(kind === 'MODEL_POLICY' ? {
      routes: [{ routeId: 'primary', provider: { kind: 'openai-compatible', endpoint: 'https://example.test', credentialRef: 'redacted' }, model: 'openai/gpt-5.6-luna' }],
      outputNondeterminismDisclosure: 'reported',
    } : kind === 'AGENT' ? {
      description: 'agent', prompts: [], skills: [], modelPolicy: { key: 'profile', revision: 1 }, tools: [], inputSchema: {}, outputSchema: {},
      memoryPolicy: { scope: 'NONE', maxBytes: 0 }, permissions: { delegatedCapabilities: [], secretScopes: [], networkHosts: [], allowedEgress: [], filesystemReadRoots: [], filesystemWriteRoots: [], allowHighImpact: false },
      hardLimits: { maxDurationSeconds: 60, maxTotalTokens: 100, maxTurns: 1, maxToolCalls: 1, maxCostUsd: '0.1' }, evaluationPolicy: { requiredEvaluations: [], evaluations: [], requireHumanRelease: false },
    } : { content: 'content' }),
  } as AgentResourceRevision['spec']
  return {
  resourceId: `${key}-${revision}`,
  tenantId: 'tenant',
  namespace: 'demo',
  kind,
  key,
  revision,
  digest: `sha256:${key}`,
  spec,
  createdBy: 'tester',
  createdAt: '2026-01-01T00:00:00Z',
  }
}

const session = (state: AgentSessionLifecycleState): AgentSessionControlSummary => ({ sessionId: 'session-1234567890', state, createdAt: '2026-01-01T00:00:00Z', updatedAt: '2026-01-01T00:00:00Z' })

describe('agent session control model', () => {
  it('offers only revision-pinned agent and model profile resources', () => {
    const resources = [resource('AGENT', 'researcher', 2), resource('MODEL_POLICY', 'safe', 1)]
    expect(agentResourceOptions(resources, 'AGENT')).toEqual([{ value: 'demo/researcher@2', label: 'researcher · demo/researcher@2', description: 'sha256:researcher' }])
    expect(agentResourceOptions(resources, 'MODEL_POLICY')[0]?.value).toBe('demo/safe@1')
    expect(agentPinnedProfile(resources, 'demo/researcher@2')).toBe('profile@1')
  })

  it('maps lifecycle actions to bounded states', () => {
    expect(sessionCanCancel(session('RUNNING'))).toBe(true)
    expect(sessionCanPause(session('RUNNING'))).toBe(true)
    expect(sessionCanResume(session('PAUSED'))).toBe(true)
    expect(sessionCanRetry(session('FAILED'))).toBe(true)
    expect(sessionIsLive(session('QUEUED'))).toBe(true)
    expect(sessionCanCancel(session('SUCCEEDED'))).toBe(false)
    expect(sessionCanPause(session('PAUSED'))).toBe(false)
    expect(sessionStateLabel('WAITING_APPROVAL')).toBe('WAITING APPROVAL')
  })

  it('uses safe event and harness provenance labels', () => {
    expect(sessionEventLabel({ eventId: 'e', sessionId: 's', eventIndex: 1, eventKey: 'model.response', eventType: 'model.response', payload: {}, occurredAt: '' })).toBe('model response')
    expect(sessionEventLabel({ eventId: 'e', sessionId: 's', eventIndex: 1, eventKey: 'tool.result', eventType: 'tool.result', payload: {}, occurredAt: '' })).toBe('tool result')
    expect(sessionHarnessLabel({ ...session('RUNNING'), harness: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' } })).toBe('pi-agent-core · 0.84.3')
  })

  it('derives the service harness catalog and preserves control pins', () => {
    const catalog = { pi: { adapter: 'pi-agent-core', adapterVersion: '0.84.3', protocol: 'amesh.pi-worker/v1' } }
    expect(harnessCatalogOptions(catalog)).toEqual([{ value: 'pi', label: 'pi · pi-agent-core', description: '0.84.3 · amesh.pi-worker/v1' }])
    expect(currentHarnessAlias(catalog)).toBe('pi')
    expect(currentHarnessAlias(catalog, { ...session('RUNNING'), harness: catalog.pi })).toBe('pi')
    const merged = mergeSessionSummary({ ...session('RUNNING'), version: 4, executionEpoch: 2, agentRef: 'demo/agent@1' }, { ...session('RUNNING'), version: 5, executionEpoch: 3 })
    expect(merged).toMatchObject({ version: 5, executionEpoch: 3, agentRef: 'demo/agent@1' })
  })
})
