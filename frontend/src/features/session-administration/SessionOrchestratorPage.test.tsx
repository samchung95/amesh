import '@testing-library/jest-dom/vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { UiSession } from '../../api/types'
import { SessionOrchestratorPage } from './SessionOrchestratorPage'

const mocks = vi.hoisted(() => ({ api: { agentSessionFleet: vi.fn(), agentSessionInstanceAggregate: vi.fn(), agentSessionPolicies: vi.fn(), effectiveAgentSessionPolicies: vi.fn(), saveAgentSessionPolicy: vi.fn(), exportAgentSessionProfile: vi.fn(), planAgentSessionProfileTransfer: vi.fn(), importAgentSessionProfile: vi.fn(), exportAgentSessionTransfer: vi.fn(), planAgentSessionTransfer: vi.fn(), importAgentSessionTransfer: vi.fn() }, settings: { settings: { tenant: 'tenant-a', namespace: '', locale: 'en', timezone: 'UTC' } } }))
vi.mock('../../app/queries', () => ({ useApiClient: () => mocks.api }))
vi.mock('../../app/settings', () => ({ useAppSettings: () => mocks.settings }))

const fleetItem = {
  sessionId: 'session-1', attemptSessionId: 'session-1', tenantId: 'tenant-a', namespace: 'platform', agentRef: 'platform/agent@1', ownerId: 'owner-1', executionId: 'execution-1', taskRunId: 'task-1', attempt: 1,
  state: 'RUNNING' as const, phase: 'TOOL', version: 2, executionVersion: 3, executionEpoch: 1, capabilityPinId: 'pin-1', envelopeDigest: 'sha256:envelope', harness: { adapter: 'pi-agent-core', adapterVersion: '1.0', protocol: 'amesh.pi-worker/v1' },
  counters: { turns: 1, loopIterations: 1, toolCalls: 1, totalTokens: 100, costUsd: '0.01', repairAttempts: 0 }, modelInvocationCount: 1, toolInvocationCount: 1, failedInvocationCount: 0, dependencyKeys: [], dependencyHealth: 'HEALTHY', createdAt: '2026-08-30T00:00:00Z', updatedAt: '2026-08-30T00:01:00Z', completedAt: null,
}

const session = { capabilities: { 'agentSessionAdministration.view': true, 'agentSessions.manage': true, 'agentSessionPolicies.view': true, 'agentSessionPolicies.manage': true } } as unknown as UiSession

const policy = { policyId: 'policy-1', tenantId: 'tenant-a', namespace: 'platform', applicationId: null, revision: 4, spec: { admissionEnabled: true, maxConcurrency: 3, maxTotalTokens: 50000, maxCostUsd: '4.50', maxDurationSeconds: 900, retentionSeconds: 86400, allowedProviderIds: ['provider/openai'], allowedHarnessIds: ['pi-agent-core'], allowedToolIds: ['search'] }, digest: 'sha256:policy', createdBy: 'operator', createdAt: '2026-08-30T00:00:00Z' }

describe('SessionOrchestratorPage', () => {
  afterEach(() => { cleanup(); vi.clearAllMocks() })
  it('renders discoverable fleet fields and applies a filter', async () => {
    mocks.api.agentSessionFleet.mockResolvedValue({ items: [fleetItem], nextCursor: null, readAt: '2026-08-30T00:01:00Z', aggregates: { matchedExecutions: 1, active: 1, terminal: 0, byState: { RUNNING: 1 }, totalTurns: 1, totalToolCalls: 1, totalTokens: 100, totalCostUsd: '0.01', modelInvocations: 1, toolInvocations: 1, failedInvocations: 0, degradedDependencies: 0 } })
    mocks.api.agentSessionInstanceAggregate.mockResolvedValue({ tenants: [], matchedExecutions: 1, active: 1, terminal: 0, readAt: '2026-08-30T00:01:00Z' })
    mocks.api.agentSessionPolicies.mockResolvedValue([policy])
    mocks.api.effectiveAgentSessionPolicies.mockResolvedValue([policy])
    mocks.api.saveAgentSessionPolicy.mockResolvedValue({ ...policy, revision: 5 })
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<QueryClientProvider client={client}><MemoryRouter><SessionOrchestratorPage session={session} /></MemoryRouter></QueryClientProvider>)
    expect(await screen.findByRole('heading', { name: 'Fleet administration' })).toBeVisible()
    expect(screen.getByRole('cell', { name: 'owner-1' })).toBeVisible()
    expect(screen.getByRole('cell', { name: /pi-agent-core/ })).toBeVisible()
    expect(screen.getByLabelText('Agent').tagName).toBe('SELECT')
    expect(screen.getAllByLabelText('Namespace')[0].tagName).toBe('SELECT')
    expect(screen.getByLabelText('Owner').tagName).toBe('SELECT')
    expect(screen.getByLabelText('Harness').tagName).toBe('SELECT')
    expect(await screen.findByRole('heading', { name: 'Session policy administration' })).toBeVisible()
    expect(screen.getByText('sha256:policy')).toBeVisible()
    fireEvent.change(screen.getAllByLabelText('Namespace')[1], { target: { value: 'platform' } })
    expect(await screen.findByText(/Namespace · platform · r4/)).toBeVisible()
    fireEvent.click(screen.getAllByRole('button', { name: 'Edit' })[0])
    expect(screen.getByText('Optimistic update · expects r4')).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Save new revision' }))
    await waitFor(() => expect(mocks.api.saveAgentSessionPolicy).toHaveBeenCalledWith(expect.objectContaining({ expectedRevision: 4, namespace: 'platform' })))
    fireEvent.change(screen.getByLabelText('Owner'), { target: { value: 'owner-1' } })
    fireEvent.click(screen.getByRole('button', { name: /Apply/ }))
    expect(mocks.api.agentSessionFleet).toHaveBeenCalled()
    expect(mocks.api.agentSessionInstanceAggregate).not.toHaveBeenCalled()
  })

  it('shows a revision conflict without hiding the policy editor', async () => {
    mocks.api.agentSessionFleet.mockResolvedValue({ items: [fleetItem], nextCursor: null, readAt: '2026-08-30T00:01:00Z', aggregates: { matchedExecutions: 1, active: 1, terminal: 0, byState: { RUNNING: 1 }, totalTurns: 1, totalToolCalls: 1, totalTokens: 100, totalCostUsd: '0.01', modelInvocations: 1, toolInvocations: 1, failedInvocations: 0, degradedDependencies: 0 } })
    mocks.api.agentSessionPolicies.mockResolvedValue([policy])
    mocks.api.effectiveAgentSessionPolicies.mockResolvedValue([])
    mocks.api.saveAgentSessionPolicy.mockRejectedValue({ status: 409, message: 'stale revision' })
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<QueryClientProvider client={client}><MemoryRouter><SessionOrchestratorPage session={session} /></MemoryRouter></QueryClientProvider>)
    expect(await screen.findByRole('heading', { name: 'Session policy administration' })).toBeVisible()
    fireEvent.click(screen.getAllByRole('button', { name: 'Edit' })[0])
    fireEvent.click(screen.getByRole('button', { name: 'Save new revision' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('policy changed while you were editing it')
    expect(screen.getByText('Optimistic update · expects r4')).toBeVisible()
  })

  it('allows policy evaluation without exposing manage controls', async () => {
    mocks.api.agentSessionFleet.mockResolvedValue({ items: [fleetItem], nextCursor: null, readAt: '2026-08-30T00:01:00Z', aggregates: { matchedExecutions: 1, active: 1, terminal: 0, byState: { RUNNING: 1 }, totalTurns: 1, totalToolCalls: 1, totalTokens: 100, totalCostUsd: '0.01', modelInvocations: 1, toolInvocations: 1, failedInvocations: 0, degradedDependencies: 0 } })
    mocks.api.agentSessionPolicies.mockResolvedValue([policy])
    const viewer = { capabilities: { 'agentSessionAdministration.view': true, 'agentSessionPolicies.view': true, 'agentSessions.manage': false } } as unknown as UiSession
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<QueryClientProvider client={client}><MemoryRouter><SessionOrchestratorPage session={viewer} /></MemoryRouter></QueryClientProvider>)
    expect(await screen.findByRole('heading', { name: 'Session policy administration' })).toBeVisible()
    expect(screen.queryByRole('button', { name: 'New revision' })).not.toBeInTheDocument()
    expect(screen.getByText(/Policy changes require the session policy manage capability/)).toBeVisible()
  })

  it('previews a JSON session bundle and imports only after a compatible plan', async () => {
    mocks.api.agentSessionFleet.mockResolvedValue({ items: [fleetItem], nextCursor: null, readAt: '2026-08-30T00:01:00Z', aggregates: { matchedExecutions: 1, active: 1, terminal: 0, byState: { RUNNING: 1 }, totalTurns: 1, totalToolCalls: 1, totalTokens: 100, totalCostUsd: '0.01', modelInvocations: 1, toolInvocations: 1, failedInvocations: 0, degradedDependencies: 0 } })
    mocks.api.planAgentSessionTransfer.mockResolvedValue({ schemaVersion: 'amesh.session-transfer/v1', eligible: true, mode: 'CLEAN_CHECKPOINT', sourceTenantId: 'source-tenant', targetTenantId: 'tenant-a', bundleDigest: 'sha256:session', flowCompatible: true, capabilityPinCompatible: true, harnessCompatible: true, credentialRebindingDiagnostics: ['provider-main → provider-target'], artifactDiagnostics: ['No artifact remapping required'], issues: [] })
    mocks.api.importAgentSessionTransfer.mockResolvedValue({ importId: 'import-1', bundleDigest: 'sha256:session', mode: 'CLEAN_CHECKPOINT', targetTenantId: 'tenant-a', sessionId: 'session-imported', alreadyPresent: false, idMapping: {}, credentialRebindingDiagnostics: [] })
    const transfer = { schemaVersion: 'amesh.session-transfer/v1', mode: 'CLEAN_CHECKPOINT', sourceTenantId: 'source-tenant', session: { sessionId: 'session-source', credentialRef: 'provider-main' }, checksumSha256: 'sha256:session' }
    const migrationAdmin = { capabilities: { 'agentSessionAdministration.view': true, 'agentSessionMigration.view': true, 'agentSessionMigration.manage': true } } as unknown as UiSession
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<QueryClientProvider client={client}><MemoryRouter><SessionOrchestratorPage session={migrationAdmin} /></MemoryRouter></QueryClientProvider>)
    expect(await screen.findByRole('heading', { name: 'Profile and session transfer' })).toBeVisible()
    const file = new File([JSON.stringify(transfer)], 'session.json', { type: 'application/json' })
    Object.defineProperty(file, 'text', { value: () => Promise.resolve(JSON.stringify(transfer)) })
    const fileInput = screen.getByText('Choose JSON bundle').parentElement?.querySelector('input') as HTMLInputElement
    expect(fileInput).toBeTruthy()
    await userEvent.setup().upload(fileInput, file)
    expect(fileInput.files).toHaveLength(1)
    expect(typeof fileInput.files?.[0]?.text).toBe('function')
    Object.defineProperty(fileInput, 'files', { configurable: true, value: [file] })
    fireEvent.change(fileInput, { target: { files: [file] } })
    expect(await screen.findByText(/source-tenant/)).toBeVisible()
    expect(screen.getByLabelText('provider-main').tagName).toBe('SELECT')
    fireEvent.click(screen.getByRole('button', { name: 'Preview compatibility' }))
    expect(await screen.findByText('Compatibility plan')).toBeVisible()
    expect(screen.getByText(/source-tenant → tenant-a/)).toBeVisible()
    expect(screen.getByText(/provider-main → provider-target/)).toBeVisible()
    fireEvent.change(screen.getByLabelText('provider-main'), { target: { value: '' } })
    expect(screen.getByRole('button', { name: 'Import verified bundle' })).toBeDisabled()
    fireEvent.change(screen.getByLabelText('provider-main'), { target: { value: 'provider-main' } })
    fireEvent.click(screen.getByRole('button', { name: 'Preview compatibility' }))
    await waitFor(() => expect(mocks.api.planAgentSessionTransfer).toHaveBeenCalledTimes(2))
    fireEvent.click(screen.getByRole('button', { name: 'Import verified bundle' }))
    await waitFor(() => expect(mocks.api.importAgentSessionTransfer).toHaveBeenCalledWith(transfer, { 'provider-main': 'provider-main' }))
    expect(await screen.findByText('Session imported')).toBeVisible()
  })
})
