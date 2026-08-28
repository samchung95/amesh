import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { useAppSettings, SettingsProvider } from './settings'

function ProtectedQueryProbe() {
  const { connected, connectToken, disconnect, settings } = useAppSettings()
  const protectedData = useQuery({
    queryKey: ['protected-resource'],
    queryFn: () => Promise.resolve(settings.token),
    enabled: connected,
    staleTime: Infinity,
  })
  return (
    <>
      <output data-testid="protected-data">{connected ? protectedData.data || 'empty' : 'empty'}</output>
      <button type="button" onClick={disconnect}>Log out</button>
      <button type="button" onClick={() => connectToken('user-a-token', 'tenant-a')}>Sign in as A</button>
      <button type="button" onClick={() => connectToken('user-b-token', 'tenant-a')}>Sign in as B</button>
    </>
  )
}

afterEach(cleanup)

function renderProbe(queryClient: QueryClient) {
  return render(
    <QueryClientProvider client={queryClient}>
      <SettingsProvider>
        <ProtectedQueryProbe />
      </SettingsProvider>
    </QueryClientProvider>,
  )
}

describe('protected query cache lifecycle', () => {
  it('removes protected data on logout before a disconnected view can render it', () => {
    const queryClient = new QueryClient()
    queryClient.setQueryData(['protected-resource'], 'user-a-private-data')
    sessionStorage.setItem('amesh.ui.token', 'user-a-token')
    renderProbe(queryClient)

    expect(screen.getByTestId('protected-data')).toHaveTextContent('user-a-private-data')
    act(() => screen.getByRole('button', { name: 'Log out' }).click())

    expect(queryClient.getQueryData(['protected-resource'])).toBeUndefined()
    expect(screen.getByTestId('protected-data')).toHaveTextContent('empty')
  })

  it('removes same-tenant data across a sign-in identity transition', async () => {
    const queryClient = new QueryClient()
    renderProbe(queryClient)

    act(() => screen.getByRole('button', { name: 'Sign in as A' }).click())
    await waitFor(() => expect(screen.getByTestId('protected-data')).toHaveTextContent('user-a-token'))
    queryClient.setQueryData(['protected-resource'], 'user-a-private-data')

    act(() => screen.getByRole('button', { name: 'Sign in as B' }).click())

    expect(queryClient.getQueryData(['protected-resource'])).not.toBe('user-a-private-data')
    await waitFor(() => expect(screen.getByTestId('protected-data')).not.toHaveTextContent('user-a-private-data'))
  })
})
