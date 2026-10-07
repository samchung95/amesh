import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { AdministrationPage } from './AdministrationPage'

const role = (name: string, display_name: string) => ({ name, display_name, description: '', permissions: [], built_in: true })

const known: Record<string, ReturnType<typeof vi.fn>> = {
  flows: vi.fn(() => Promise.resolve([])),
  principals: vi.fn(() => Promise.resolve([
    { id: 'p-bob', principal_type: 'USER', handle: 'bob', display_name: 'Bob Lee', enabled: true },
  ])),
  roles: vi.fn(() => Promise.resolve([role('flow-author', 'Flow author'), role('viewer', 'Viewer')])),
  bindings: vi.fn(() => Promise.resolve([])),
  providers: vi.fn(() => Promise.resolve([])),
  principalCredentials: vi.fn(() => Promise.resolve([])),
  createBinding: vi.fn(() => Promise.resolve({})),
}
// Other sections' queries are disabled on the Access view; give them an empty answer anyway.
const api = new Proxy(known, { get: (target, key: string) => (target[key] ??= vi.fn(() => Promise.resolve([]))) })

vi.mock('../../app/queries', () => ({ useApiClient: () => api }))
vi.mock('../../app/settings', () => ({
  useAppSettings: () => ({ settings: { tenant: 'default', namespace: '', token: 'token', locale: 'en', timezone: 'UTC' } }),
}))

afterEach(() => {
  cleanup()
  api.createBinding.mockClear()
})

function renderAccess() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/administration?view=access']}>
        <AdministrationPage session={{ display: 'Root administrator' } as never} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('AdministrationPage access bindings', () => {
  it('grants the role the administrator picked', async () => {
    const user = userEvent.setup()
    renderAccess()

    await user.selectOptions(await screen.findByRole('combobox', { name: 'Principal' }), 'p-bob')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Role' }), 'Viewer · viewer')
    await user.click(screen.getByRole('button', { name: 'Create binding' }))

    expect(api.createBinding).toHaveBeenCalledWith(expect.objectContaining({ principal_id: 'p-bob', role_name: 'viewer' }))
  })

  it('does not grant a role nobody chose', async () => {
    const user = userEvent.setup()
    renderAccess()

    await user.selectOptions(await screen.findByRole('combobox', { name: 'Principal' }), 'p-bob')
    await user.click(screen.getByRole('button', { name: 'Create binding' }))

    expect(screen.getByRole('combobox', { name: 'Role' })).toHaveDisplayValue('Select a role')
    expect(api.createBinding).not.toHaveBeenCalled()
  })
})
