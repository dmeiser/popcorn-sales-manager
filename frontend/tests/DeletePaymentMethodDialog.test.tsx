/**
 * Tests for DeletePaymentMethodDialog component
 */

import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DeletePaymentMethodDialog } from '../src/components/DeletePaymentMethodDialog';

describe('DeletePaymentMethodDialog', () => {
  const mockOnClose = vi.fn();
  const mockOnDelete = vi.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const defaultProps = {
    open: true,
    onClose: mockOnClose,
    onDelete: mockOnDelete,
    methodName: 'Venmo',
    isLoading: false,
  };

  test('renders dialog when open', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Delete Payment Method')).toBeInTheDocument();
  });

  test('does not render dialog when closed', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} open={false} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  test('displays method name in confirmation message', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} />);
    expect(screen.getByText(/"Venmo"/)).toBeInTheDocument();
  });

  test('renders Delete and Cancel buttons', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} />);
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  test('shows warning alert', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} />);
    expect(screen.getByText(/This action cannot be undone/)).toBeInTheDocument();
  });

  test('shows info about existing orders', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} />);
    expect(screen.getByText(/Existing orders using this payment method/)).toBeInTheDocument();
  });

  test('calls onDelete when Delete clicked', async () => {
    const user = userEvent.setup();
    render(<DeletePaymentMethodDialog {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: 'Delete' }));

    expect(mockOnDelete).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when Cancel clicked', async () => {
    const user = userEvent.setup();
    render(<DeletePaymentMethodDialog {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: 'Cancel' }));

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose after successful delete', async () => {
    const user = userEvent.setup();
    render(<DeletePaymentMethodDialog {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  test('disables buttons when loading', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} isLoading={true} />);

    expect(screen.getByRole('button', { name: /Deleting/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
  });

  test('shows loading indicator when deleting', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} isLoading={true} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.getByText('Deleting...')).toBeInTheDocument();
  });

  test('does not call onClose if onDelete throws error', async () => {
    const user = userEvent.setup();
    const failingOnDelete = vi.fn().mockRejectedValue(new Error('Network error'));
    render(<DeletePaymentMethodDialog {...defaultProps} onDelete={failingOnDelete} />);

    await user.click(screen.getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      expect(failingOnDelete).toHaveBeenCalledTimes(1);
    });
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  test('displays different method name correctly', () => {
    render(<DeletePaymentMethodDialog {...defaultProps} methodName="PayPal" />);
    expect(screen.getByText(/"PayPal"/)).toBeInTheDocument();
  });
});
