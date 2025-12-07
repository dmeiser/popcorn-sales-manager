/**
 * ProfileCard component tests
 */

import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ProfileCard } from '../src/components/ProfileCard';

// Mock navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('ProfileCard', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  test('renders profile information correctly', () => {
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Alpha"
          isOwner={true}
          permissions={[]}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Scout Alpha')).toBeInTheDocument();
    // Profile ID text is split across multiple nodes with whitespace
    expect(screen.getByText(/Profile ID:/i)).toBeInTheDocument();
  });

  test('displays Owner badge for owned profiles', () => {
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Alpha"
          isOwner={true}
          permissions={[]}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Owner')).toBeInTheDocument();
  });

  test('displays Editor badge for shared profiles with WRITE permission', () => {
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Beta"
          isOwner={false}
          permissions={['WRITE']}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Editor')).toBeInTheDocument();
    expect(screen.queryByText('Owner')).not.toBeInTheDocument();
  });

  test('displays Viewer badge for shared profiles with READ-only permission', () => {
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Gamma"
          isOwner={false}
          permissions={['READ']}
        />
      </BrowserRouter>
    );

    expect(screen.getByText('Viewer')).toBeInTheDocument();
  });

  test('navigates to seasons page when View Seasons clicked', async () => {
    const user = userEvent.setup();
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Alpha"
          isOwner={true}
          permissions={[]}
        />
      </BrowserRouter>
    );

    const viewButton = screen.getByRole('button', { name: /View Seasons/i });
    await user.click(viewButton);

    expect(mockNavigate).toHaveBeenCalledWith('/profiles/profile-123/seasons');
  });

  test('shows Edit Name button for owners', () => {
    const onEdit = vi.fn();
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Alpha"
          isOwner={true}
          permissions={[]}
          onEdit={onEdit}
        />
      </BrowserRouter>
    );

    expect(screen.getByRole('button', { name: /Edit Name/i })).toBeInTheDocument();
  });

  test('shows Edit Name button for editors with WRITE permission', () => {
    const onEdit = vi.fn();
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Beta"
          isOwner={false}
          permissions={['WRITE']}
          onEdit={onEdit}
        />
      </BrowserRouter>
    );

    expect(screen.getByRole('button', { name: /Edit Name/i })).toBeInTheDocument();
  });

  test('hides Edit Name button for viewers with READ-only permission', () => {
    const onEdit = vi.fn();
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Gamma"
          isOwner={false}
          permissions={['READ']}
          onEdit={onEdit}
        />
      </BrowserRouter>
    );

    expect(screen.queryByRole('button', { name: /Edit Name/i })).not.toBeInTheDocument();
  });

  test('calls onEdit when Edit Name clicked', async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Alpha"
          isOwner={true}
          permissions={[]}
          onEdit={onEdit}
        />
      </BrowserRouter>
    );

    const editButton = screen.getByRole('button', { name: /Edit Name/i });
    await user.click(editButton);

    expect(onEdit).toHaveBeenCalledTimes(1);
  });

  test('does not show Edit Name button when onEdit is undefined', () => {
    render(
      <BrowserRouter>
        <ProfileCard
          profileId="profile-123"
          sellerName="Scout Alpha"
          isOwner={true}
          permissions={[]}
        />
      </BrowserRouter>
    );

    expect(screen.queryByRole('button', { name: /Edit Name/i })).not.toBeInTheDocument();
  });
});
