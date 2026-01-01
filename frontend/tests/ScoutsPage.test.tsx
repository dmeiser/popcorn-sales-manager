import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock AuthContext (authenticated)
vi.mock('../src/contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: true, loading: false, account: { accountId: 'test-account-id' } }),
}))

// Partially mock apollo hooks: provide a client.query that returns shared profiles
vi.mock('@apollo/client/react', async () => {
  const actual = await vi.importActual<any>('@apollo/client/react')
  return {
    ...actual,
    useApolloClient: () => ({
      query: vi.fn().mockResolvedValue({ data: { listMyShares: [{ profileId: 'p-share-1', sellerName: 'Shared Scout', isOwner: false, permissions: ['READ'] }] } }),
    }),
    // Provide no-op lazy queries and empty results so the component can render
    useLazyQuery: () => [vi.fn(), { data: { listMyProfiles: [] } }],
    useQuery: () => ({ data: { listCampaignsByProfile: [] }, loading: false }),
    useMutation: () => [vi.fn()],
  }
})

import { ScoutsPage } from '../src/pages/ScoutsPage'

describe('ScoutsPage (focused smoke test)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders shared profiles when apollo client returns shares', async () => {
    render(
      <MemoryRouter>
        <ScoutsPage />
      </MemoryRouter>,
    )

    // Wait for the shared profile name to appear
    await waitFor(() => expect(screen.getByText('Shared Scout')).toBeInTheDocument())
  }, 10000)
})
