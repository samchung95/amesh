import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useNavigate } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { FlowEditorPage } from './FlowEditorPage'

const validValidation = { valid: true, irVersion: '1', semantic_hash: null, canonical: null, issues: [] }
const editorMocks = vi.hoisted(() => ({ focusRange: vi.fn() }))

const api = {
  flowEditorSchema: vi.fn().mockResolvedValue({
    schemaVersion: 'amesh.flow-editor/v1',
    flowSchema: {},
    resourceCatalog: { schemaVersion: 'amesh.resource-catalog/v1', resources: [] },
    expressionContext: {},
  }),
  flowDocument: vi.fn((namespace: string, flowId: string) => Promise.resolve({
    document: { id: flowId, namespace, revision: 1, tasks: [{ id: 'done', type: 'core.return', value: flowId }] },
    revision: 1,
  })),
  flowRevisions: vi.fn().mockResolvedValue([]),
  validateFlow: vi.fn().mockResolvedValue(validValidation),
  validateFlowPolicy: vi.fn().mockResolvedValue({
    allowed: true,
    outcome: 'ALLOW',
    matchedRules: [],
    requiredApprovals: [],
    mutations: [],
    pinnedPolicies: [],
    evaluationDurationMs: 0,
  }),
  saveFlow: vi.fn().mockResolvedValue({
    namespace: 'default',
    flow_id: 'guided_first_run',
    revision: 1,
    etag: 'flow-etag',
  }),
}

vi.mock('../../app/queries', () => ({
  useApiClient: () => api,
  useFlows: () => ({ data: [], isPending: false, error: null }),
}))

vi.mock('../../app/settings', () => ({
  useAppSettings: () => ({ settings: { tenant: 'tenant-a', namespace: '', token: 'user-a-token' } }),
}))

vi.mock('./VisualFlowEditor', () => ({
  VisualFlowEditor: ({ source }: { source: string }) => <pre data-testid="editor-source">{source}</pre>,
}))

vi.mock('./FlowCodeEditor', async () => {
  const React = await import('react')
  return {
    FlowCodeEditor: React.forwardRef<{ focusRange: (from: number, to: number) => void }, { value: string; onReady?: () => void }>(
      function MockFlowCodeEditor({ value, onReady }, ref) {
        React.useImperativeHandle(ref, () => ({ focusRange: editorMocks.focusRange }), [])
        React.useEffect(() => { onReady?.() }, [onReady])
        return <pre data-testid="code-editor">{value}</pre>
      },
    ),
  }
})

vi.mock('./GuidedWorkflowBuilder', () => ({
  GuidedWorkflowBuilder: ({ onChange }: { onChange: (source: string) => void }) => (
    <button
      type="button"
      onClick={() => onChange('id: guided_first_run\nnamespace: default\nrevision: 1\ntasks:\n  - id: done\n    type: core.return\n    value: ok\n')}
    >
      Update guided draft
    </button>
  ),
}))

function RouteReuseHarness() {
  const navigate = useNavigate()
  return (
    <>
      <button type="button" onClick={() => void navigate('/flows/team/b/edit')}>Open B</button>
      <Routes>
        <Route path="/flows/:namespace/:flowId/edit" element={<FlowEditorPageForTest />} />
      </Routes>
    </>
  )
}

function FlowEditorPageForTest() {
  // Keep the route mounted while only its params change, matching the app route.
  return <FlowEditorPage session={session} />
}

const session = {
  principalId: 'user-a',
  principalType: 'user',
  display: 'User A',
  tenantId: 'tenant-a',
  namespace: null,
  capabilities: {
    'flows.update': true,
    'flows.create': true,
    'flows.view': true,
  },
  telemetryEnabled: false,
  serverVersion: 'test',
} as never

afterEach(() => {
  cleanup()
  api.validateFlow.mockResolvedValue(validValidation)
  editorMocks.focusRange.mockClear()
})

describe('flow editor route reuse', () => {
  it('keeps a workflow editable when one plugin resource kind is unsupported', async () => {
    api.flowEditorSchema.mockResolvedValueOnce({
      schemaVersion: 'amesh.flow-editor/v1',
      flowSchema: {},
      resourceCatalog: {
        resources: [
          { type: 'core.return', kind: 'task', configurationSchema: {}, editor: { title: 'Return', description: '', category: 'Core', propertyOrder: [] } },
          { type: 'vendor.future', kind: 'future-resource' },
        ],
      },
      expressionContext: {},
    })
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/flows/team/a/edit']}>
          <RouteReuseHarness />
        </MemoryRouter>
      </QueryClientProvider>,
    )
    expect(await screen.findByTestId('editor-source')).toHaveTextContent('core.return')
    expect(screen.getByText('Editor controls are unavailable for: vendor.future.')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Save revision' })).toBeVisible()
  })

  it('loads the new flow source when navigating between editor identities in place', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const user = userEvent.setup()
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/flows/team/a/edit']}>
          <RouteReuseHarness />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('editor-source')).toHaveTextContent('id: a'))
    await user.click(screen.getByRole('button', { name: 'Open B' }))
    const sourceDuringNavigation = screen.queryByTestId('editor-source')
    if (sourceDuringNavigation) expect(sourceDuringNavigation).not.toHaveTextContent('id: a')
    await waitFor(() => expect(screen.getByTestId('editor-source')).toHaveTextContent('id: b'))
    expect(screen.getByTestId('editor-source')).not.toHaveTextContent('id: a\n')
  })

  it('preserves the saved draft state while adopting its edit route', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const user = userEvent.setup()
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/flows/new']}>
          <Routes>
            <Route path="/flows/new" element={<FlowEditorPageForTest />} />
            <Route path="/flows/:namespace/:flowId/edit" element={<FlowEditorPageForTest />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await user.click(await screen.findByRole('button', { name: 'Update guided draft' }))
    const saveButton = screen.getByRole('button', { name: 'Save revision' })
    await waitFor(() => expect(saveButton).toBeEnabled())
    await user.click(saveButton)

    expect(await screen.findByRole('heading', { level: 1, name: 'guided_first_run' })).toBeVisible()
    expect(await screen.findByText('Saved default.guided_first_run revision 1.')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Update guided draft' })).toBeVisible()
  })

  it('focuses a validation issue after the lazy YAML editor mounts', async () => {
    api.validateFlow.mockResolvedValue({
      valid: false,
      irVersion: '1',
      semantic_hash: null,
      canonical: null,
      issues: [{
        code: 'missing-task',
        message: 'Missing task value',
        path: 'tasks[0].value',
        hint: 'Add a value.',
        sourceRange: {
          start: { offset: 10, line: 2, column: 3 },
          end: { offset: 14, line: 2, column: 7 },
        },
        severity: 'error',
      }],
    })
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const user = userEvent.setup()
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/flows/team/a/edit']}>
          <RouteReuseHarness />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('editor-source')).toHaveTextContent('id: a'))
    await user.click(screen.getByRole('button', { name: 'Validate & check policy' }))
    await user.click(await screen.findByRole('button', { name: /Missing task value/ }))

    expect(await screen.findByTestId('code-editor')).toBeVisible()
    await waitFor(() => expect(editorMocks.focusRange).toHaveBeenCalledWith(10, 14))
  })
})
