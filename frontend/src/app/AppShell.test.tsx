import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import './i18n'
import { AppShell } from './AppShell'

const api = {
  announcements: vi.fn().mockResolvedValue([]),
  logout: vi.fn().mockResolvedValue(undefined),
}

const settings = {
  tenant: 'default',
  namespace: '',
  token: 'token',
  locale: 'en',
  timezone: 'UTC',
  savedViews: [],
  authenticationMode: 'session',
}

vi.mock('./queries', () => ({
  useApiClient: () => api,
  useFlows: () => ({ data: [{ namespace: 'team.data', flow_id: 'daily' }], isPending: false }),
  useExecutions: () => ({ data: [] }),
  useGlobalSearch: () => ({ data: { items: [] } }),
}))

vi.mock('./settings', () => ({
  useAppSettings: () => ({
    settings,
    disconnect: vi.fn(),
    updateContext: vi.fn(),
    updateLocale: vi.fn(),
    updateTimezone: vi.fn(),
  }),
}))

const session = {
  principalId: 'operator',
  principalType: 'USER',
  display: 'Operator',
  tenantId: 'default',
  namespace: null,
  capabilities: {
    'dashboards.view': true,
    'flows.view': true,
    'executions.view': true,
    'triggers.view': true,
    'checks.view': true,
    'assets.view': true,
    'agents.view': true,
    'namespaceResources.read': true,
    'plugins.view': true,
    'apps.view': false,
    'agentSessions.view': false,
    'agentSessionAdministration.view': false,
    'releases.view': false,
    'administration.manage': false,
  },
  telemetryEnabled: false,
  serverVersion: 'test',
} as never

afterEach(() => {
  cleanup()
  api.announcements.mockClear()
})

describe('AppShell navigation', () => {
  it('hides destinations the current session cannot access', () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Routes>
            <Route element={<AppShell session={session} />}>
              <Route path="/" element={<p>Home</p>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    const navigation = screen.getByRole('navigation')
    expect(within(navigation).getByRole('link', { name: 'Workflows' })).toBeVisible()
    expect(within(navigation).getByRole('link', { name: 'Assets' })).toBeVisible()
    for (const hidden of ['Apps', 'Agent sessions', 'Session orchestrator', 'Releases', 'Administration']) {
      expect(within(navigation).queryByRole('link', { name: hidden })).not.toBeInTheDocument()
      expect(within(navigation).queryByText(hidden)).not.toBeInTheDocument()
    }
    expect(navigation.querySelector('.rail-link-disabled')).not.toBeInTheDocument()
  })
})
