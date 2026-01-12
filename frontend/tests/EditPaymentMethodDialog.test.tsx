/**
 * Tests for EditPaymentMethodDialog component
 */

import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EditPaymentMethodDialog } from '../src/components/EditPaymentMethodDialog';

describe('EditPaymentMethodDialog', () => {
  const mockOnClose = vi.fn();
  const mockOnUpdate = vi.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const defaultProps = {
    open: true,
    onClose: mockOnClose,
    onUpdate: mockOnUpdate,
    currentName: 'Venmo',
    existingNames: ['Venmo', 'PayPal'],
    reservedNames: ['Cash', 'Check'],
    isLoading: false,
  };

  test('renders dialog when open', () => {
    render(<EditPaymentMethodDialog {...defaultProps} />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Edit Payment Method')).toBeInTheDocument();
  });

  test('does not render dialog when closed', () => {
    render(<EditPaymentMethodDialog {...defaultProps} open={false} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  test('pre-fills input with current name', () => {
    render(<EditPaymentMethodDialog {...defaultProps} />);
    expect(screen.getByLabelText('Payment method name')).toHaveValue('Venmo');
  });

  test('renders Update and Cancel buttons', () => {
    render(<EditPaymentMethodDialog {...defaultProps} />);
    expect(screen.getByRole('button', { name: 'Update' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  test('Update button is enabled when name has changed', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'Venmo - New');

    expect(screen.getByRole('button', { name: 'Update' })).toBeEnabled();
  });

  test('Update button is disabled when name is empty', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);

    expect(screen.getByRole('button', { name: 'Update' })).toBeDisabled();
  });

  test('shows error for reserved name', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'Cash');
    await user.click(screen.getByRole('button', { name: 'Update' }));

    expect(screen.getByText(/"Cash" is a reserved payment method name/)).toBeInTheDocument();
    expect(mockOnUpdate).not.toHaveBeenCalled();
  });

  test('shows error for duplicate name', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'PayPal');
    await user.click(screen.getByRole('button', { name: 'Update' }));

    expect(screen.getByText(/A payment method named "PayPal" already exists/)).toBeInTheDocument();
    expect(mockOnUpdate).not.toHaveBeenCalled();
  });

  test('allows keeping the same name (case-insensitive)', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'venmo');
    await user.click(screen.getByRole('button', { name: 'Update' }));

    expect(mockOnUpdate).toHaveBeenCalledWith('Venmo', 'venmo');
  });

  test('calls onUpdate with old and new name on submit', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'Zelle');
    await user.click(screen.getByRole('button', { name: 'Update' }));

    expect(mockOnUpdate).toHaveBeenCalledWith('Venmo', 'Zelle');
  });

  test('calls onClose when Cancel clicked', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('shows helper text when name has changed', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'New Name');

    expect(screen.getByText(/This will update the name for all orders/)).toBeInTheDocument();
  });

  test('enforces maxLength of 50 characters', () => {
    render(<EditPaymentMethodDialog {...defaultProps} />);
    const input = screen.getByLabelText('Payment method name');
    expect(input).toHaveAttribute('maxLength', '50');
  });

  test('disables input and buttons when loading', () => {
    render(<EditPaymentMethodDialog {...defaultProps} isLoading={true} />);

    expect(screen.getByLabelText('Payment method name')).toBeDisabled();
    expect(screen.getByRole('button', { name: /Updating/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
  });

  test('shows loading indicator when updating', () => {
    render(<EditPaymentMethodDialog {...defaultProps} isLoading={true} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.getByText('Updating...')).toBeInTheDocument();
  });

  test('submits on Enter key press', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'Zelle{Enter}');

    expect(mockOnUpdate).toHaveBeenCalledWith('Venmo', 'Zelle');
  });

  test('resets state when dialog reopens', async () => {
    const { rerender } = render(<EditPaymentMethodDialog {...defaultProps} />);

    // Close and reopen with different currentName
    rerender(<EditPaymentMethodDialog {...defaultProps} open={false} />);
    rerender(<EditPaymentMethodDialog {...defaultProps} open={true} currentName="PayPal" />);

    await waitFor(() => {
      expect(screen.getByLabelText('Payment method name')).toHaveValue('PayPal');
    });
  });

  test('clears error when user types', async () => {
    const user = userEvent.setup();
    render(<EditPaymentMethodDialog {...defaultProps} />);

    const input = screen.getByLabelText('Payment method name');
    await user.clear(input);
    await user.type(input, 'Cash');
    await user.click(screen.getByRole('button', { name: 'Update' }));

    expect(screen.getByText(/"Cash" is a reserved payment method name/)).toBeInTheDocument();

    await user.type(input, 'App');
    expect(screen.queryByText(/"Cash" is a reserved payment method name/)).not.toBeInTheDocument();
  });
});
