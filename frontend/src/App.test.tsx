import '@testing-library/jest-dom/vitest'

import { lazy } from 'react'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { RouteSuspense } from './App'

describe('RouteSuspense', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders an error state when a lazy route chunk fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    const BrokenRoute = lazy(() => Promise.reject(new Error('missing route chunk')))

    render(
      <MemoryRouter initialEntries={['/broken']}>
        <RouteSuspense title="Broken route">
          <BrokenRoute />
        </RouteSuspense>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('alert')).toHaveTextContent('Unable to load this view')
    expect(screen.getByRole('button', { name: /reload/i })).toBeVisible()
  })
})
