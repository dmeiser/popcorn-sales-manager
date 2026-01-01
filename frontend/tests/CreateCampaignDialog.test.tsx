/**
 * CreateCampaignDialog component tests
 * 
 * ⚠️  ALL TESTS CURRENTLY SKIPPED
 * 
 * Issue: MUI components fail to render in Vitest when wrapped with Apollo MockedProvider.
 * Error: "Element type is invalid: expected a string (for built-in components) or 
 * a class/function (for composite components) but got: undefined."
 * 
 * This is a test environment issue, NOT a runtime issue. The CreateCampaignDialog component
 * works correctly in the actual application.
 * 
 * Root cause: Vitest + @apollo/client@4.0.9 + @mui/material@7.3.6 ESM resolution conflict
 * when MockedProvider wraps MUI components (Dialog, TextField, Select, etc.).
 * 
 * Tests written: 13 comprehensive tests covering all functionality
 * Tests passing: 0 (all skipped due to environment issue)
 * 
 * TODO: Re-enable when MUI/Apollo/Vitest compatibility is resolved, or when
 * migrating to a different test setup (e.g., Playwright for component testing).
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CreateCampaignDialog } from '../src/components/CreateCampaignDialog';
import { LIST_PUBLIC_CATALOGS, LIST_MY_CATALOGS } from '../src/lib/graphql';

const mockPublicCatalogs = [
  {
    catalogId: 'catalog-1',
    catalogName: 'Official 2025 Catalog',
    catalogType: 'PUBLIC',
    isDeleted: false,
  },
  {
    catalogId: 'catalog-2',
    catalogName: 'Troop 123 Custom',
    catalogType: 'PUBLIC',
    isDeleted: false,
  },
];

const mockMyCatalogs = [
  {
    catalogId: 'catalog-3',
    catalogName: 'My Private Catalog',
    catalogType: 'PRIVATE',
    isDeleted: false,
  },
];

// Mock @apollo/client/react's useQuery at module scope. We can't spy on ESM named exports in Vitest,
// so provide a variable implementation that tests can replace.
let useQueryMockImpl = (query: any) => ({ data: undefined, loading: false });
vi.mock('@apollo/client/react', () => ({
  useQuery: (query: any) => useQueryMockImpl(query),
}));

describe('CreateCampaignDialog', () => {
  let mockOnClose: ReturnType<typeof vi.fn>;
  let mockOnSubmit: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnClose = vi.fn();
    mockOnSubmit = vi.fn().mockResolvedValue(undefined);

    // useQuery will be spied on per-test via setupUseQueryMock()
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const setupUseQueryMock = (overrides?: {
    publicLoading?: boolean;
    myLoading?: boolean;
    publicData?: any;
    myData?: any;
  }) => {
    useQueryMockImpl = (query: any) => {
      if (query === LIST_PUBLIC_CATALOGS) {
        return {
          data: overrides?.publicData ?? { listPublicCatalogs: mockPublicCatalogs },
          loading: overrides?.publicLoading ?? false,
        } as any;
      }
      if (query === LIST_MY_CATALOGS) {
        return {
          data: overrides?.myData ?? { listMyCatalogs: mockMyCatalogs },
          loading: overrides?.myLoading ?? false,
        } as any;
      }
      return { data: undefined, loading: false } as any;
    };
  };

  const getCatalogSelect = () => {
    // Find the InputLabel element for Product Catalog and find the nearest FormControl root
    const labels = screen.queryAllByText(/catalog/i);
    const label = labels.find((el) => el.tagName === 'LABEL') || labels[0];
    if (!label) return null;
    const form = label.closest('.MuiFormControl-root');
    return form?.querySelector('[role="combobox"]') as HTMLElement | null;
  };

  it('renders when open', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Create New Sales Campaign')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={false} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('displays form fields', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/campaign name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument();
    
    // Wait for catalog label to appear (MUI may not link label to combobox reliably)
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });
  });

  it('start date is empty by default', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const startDateInput = screen.getByLabelText(/start date/i) as HTMLInputElement;
    await waitFor(() => {
      expect(startDateInput.value).toBe('');
    });
  });

  it('loads and displays catalogs', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    // Wait for catalogs to load via label presence
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    // Click the catalog select
    const user = userEvent.setup();
    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    await user.click(catalogSelect!);

    // Should show all catalogs (public + private)
    await waitFor(() => {
      expect(screen.getByText('Official 2025 Catalog')).toBeInTheDocument();
      expect(screen.getByText('Troop 123 Custom')).toBeInTheDocument();
      expect(screen.getByText('My Private Catalog')).toBeInTheDocument();
    });
  });

  it('disables create button when required fields are missing', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    const createButton = screen.getByRole('button', { name: /create/i });
    expect(createButton).toBeDisabled();
  });

  it('enables create button when all required fields are filled', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const user = userEvent.setup();

    // Wait for catalogs to load
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    // Fill in campaign name
    const nameInput = screen.getByLabelText(/campaign name/i);
    await user.clear(nameInput);
    await user.type(nameInput, 'Fall 2025 Fundraiser');

    // Select a catalog via combobox
    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    await user.click(catalogSelect!);
    await waitFor(() => {
      expect(screen.getByText('Official 2025 Catalog')).toBeInTheDocument();
    });
    await user.click(screen.getByText('Official 2025 Catalog'));

    // Create button should now be enabled
    const createButton = screen.getByRole('button', { name: /create/i });
    await waitFor(() => {
      expect(createButton).toBeEnabled();
    });
  });

  it('calls onSubmit with correct data when form is submitted', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const user = userEvent.setup();

    // Wait for catalogs to load
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    // Fill in campaign name
    const nameInput = screen.getByLabelText(/campaign name/i);
    await user.clear(nameInput);
    await user.type(nameInput, 'Fall 2025 Fundraiser');

    // Select a catalog via combobox
    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    await user.click(catalogSelect!);
    await waitFor(() => {
      expect(screen.getByText('Official 2025 Catalog')).toBeInTheDocument();
    });
    await user.click(screen.getByText('Official 2025 Catalog'));

    // Submit the form
    const createButton = screen.getByRole('button', { name: /create/i });
    await waitFor(() => expect(createButton).toBeEnabled());
    await user.click(createButton);

    // Verify onSubmit was called with correct arguments (campaignName, campaignYear, catalogId, startDate?, endDate?)
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        'Fall 2025 Fundraiser',
        expect.any(Number), // year
        'catalog-1', // catalog ID
        undefined,
        undefined
      );
    });
  });

  it('includes end date in submission when provided', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const user = userEvent.setup();

    // Wait for catalogs to load
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    // Fill in all fields including end date
    const nameInput = screen.getByLabelText(/campaign name/i);
    await user.clear(nameInput);
    await user.type(nameInput, 'Fall 2025 Fundraiser');

    const endDateInput = screen.getByLabelText(/end date/i);
    await user.type(endDateInput, '2025-12-31');

    // Select a catalog
    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    await user.click(catalogSelect!);
    await waitFor(() => {
      expect(screen.getByText('Official 2025 Catalog')).toBeInTheDocument();
    });
    await user.click(screen.getByText('Official 2025 Catalog'));

    // Submit the form
    const createButton = screen.getByRole('button', { name: /create/i });
    await waitFor(() => expect(createButton).toBeEnabled());
    await user.click(createButton);

    // Verify onSubmit was called with end date
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        'Fall 2025 Fundraiser',
        expect.any(Number), // year
        'catalog-1',
        undefined,
        '2025-12-31'
      );
    });
  });

  it('resets form after successful submission', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const user = userEvent.setup();

    // Wait for catalogs and fill form
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    const nameInput = screen.getByLabelText(/campaign name/i) as HTMLInputElement;
    await user.type(nameInput, 'Fall 2025');

    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    await user.click(catalogSelect!);
    await waitFor(() => screen.getByText('Official 2025 Catalog'));
    await user.click(screen.getByText('Official 2025 Catalog'));

    const createButton = screen.getByRole('button', { name: /create/i });
    await waitFor(() => expect(createButton).toBeEnabled());
    await user.click(createButton);

    // After successful submission, form should reset
    await waitFor(() => {
      expect(nameInput.value).toBe('');
    });
  });

  it('calls onClose when cancel button is clicked', async () => {
    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const user = userEvent.setup();
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('shows disabled catalog select while catalogs are loading', () => {
    setupUseQueryMock({ publicLoading: true, myLoading: true, publicData: { listPublicCatalogs: [] }, myData: { listMyCatalogs: [] } });

    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    expect(catalogSelect).toHaveAttribute('aria-disabled', 'true');
  });

  it('handles submission error gracefully', async () => {
    const errorSubmit = vi.fn().mockRejectedValue(new Error('Network error'));

    setupUseQueryMock();
    render(<CreateCampaignDialog open={true} onClose={mockOnClose} onSubmit={errorSubmit} />);

    const user = userEvent.setup();

    // Wait and fill form
    await waitFor(() => {
      expect(screen.getAllByText(/catalog/i).length).toBeGreaterThan(0);
    });

    const nameInput = screen.getByLabelText(/campaign name/i);
    await user.type(nameInput, 'Fall 2025');

    const catalogSelect = getCatalogSelect();
    expect(catalogSelect).toBeTruthy();
    await user.click(catalogSelect!);
    await waitFor(() => screen.getByText('Official 2025 Catalog'));
    await user.click(screen.getByText('Official 2025 Catalog'));

    const createButton = screen.getByRole('button', { name: /create/i });
    await waitFor(() => expect(createButton).toBeEnabled());
    await user.click(createButton);

    // Should not crash and should keep dialog open
    await waitFor(() => {
      expect(errorSubmit).toHaveBeenCalled();
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });
});
