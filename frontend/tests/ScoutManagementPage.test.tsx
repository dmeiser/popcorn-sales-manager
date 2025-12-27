import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// Route parameter and DB id for test
const RAW_ID = 'dd69b3bd-5978-419e-9e55-f7c85817e020';
const DB_ID = `PROFILE#${RAW_ID}`;

// Mock useQuery before importing component
vi.mock('@apollo/client/react', async () => {
  const actual = await vi.importActual('@apollo/client/react');
  return {
    ...actual,
    useQuery: (query: any, _opts: any) => {
      const defs = query?.definitions || [];
      const opNames = defs.map((d: any) => d?.name?.value).filter(Boolean);
      if (opNames.includes('GetProfile')) {
        return {
          data: { getProfile: { profileId: DB_ID, sellerName: 'Tom Test', ownerAccountId: 'ACCOUNT#abc', createdAt: new Date().toISOString(), isOwner: true, permissions: ['READ','WRITE'] } },
          loading: false,
          refetch: vi.fn(),
        };
      }
      if (opNames.includes('ListInvitesByProfile')) {
        return { data: { listInvitesByProfile: [] }, loading: false };
      }
      if (opNames.includes('ListSharesByProfile')) {
        return { data: { listSharesByProfile: [] }, loading: false };
      }
      // Fallback: return a safe no-op response instead of calling actual.useQuery
      return { data: null, loading: false };
    },
    useMutation: (mutation: any, _opts: any) => {
      // Return a mock mutation function and a result object
      const mockFn = vi.fn().mockResolvedValue({ data: {} });
      return [mockFn, { loading: false, data: null }];
    },
  };
});

import { ScoutManagementPage } from '../src/pages/ScoutManagementPage';

describe('ScoutManagementPage', () => {
  it('loads and displays profile when route provides raw id (page normalizes to PROFILE#)', async () => {
    render(
      <MemoryRouter initialEntries={[`/scouts/${encodeURIComponent(RAW_ID)}/manage`]}>
        <Routes>
          <Route path="/scouts/:scoutId/manage" element={<ScoutManagementPage />} />
        </Routes>
      </MemoryRouter>,
    );

    // Wait for seller name to populate the Seller Name input
    await waitFor(() => expect((screen.getByLabelText('Seller Name') as HTMLInputElement).value).toBe('Tom Test'));
  });
});

