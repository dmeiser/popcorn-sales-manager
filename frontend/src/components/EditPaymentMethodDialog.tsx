/**
 * EditPaymentMethodDialog - Dialog for renaming an existing custom payment method
 *
 * Features:
 * - Pre-filled name input
 * - Validation against reserved and existing names
 * - Loading state during update
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';

interface EditPaymentMethodDialogProps {
  open: boolean;
  onClose: () => void;
  onUpdate: (oldName: string, newName: string) => Promise<void>;
  currentName: string;
  existingNames: string[];
  reservedNames: string[];
  isLoading?: boolean;
}

/* eslint-disable complexity -- Complex dialog component with validation */
export const EditPaymentMethodDialog: React.FC<EditPaymentMethodDialogProps> = ({
  open,
  onClose,
  onUpdate,
  currentName,
  existingNames,
  reservedNames,
  isLoading = false,
}) => {
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Reset state when dialog opens/closes or currentName changes
  useEffect(() => {
    if (open) {
      setName(currentName);
      setError(null);
    }
  }, [open, currentName]);

  const validateName = (value: string): string | null => {
    const trimmed = value.trim();

    if (!trimmed) {
      return 'Name is required';
    }

    if (trimmed.length > 50) {
      return 'Name must be 50 characters or less';
    }

    // Allow keeping the same name (case-insensitive)
    if (trimmed.toLowerCase() === currentName.toLowerCase()) {
      return null;
    }

    // Check reserved names (case-insensitive)
    if (reservedNames.some((reserved) => reserved.toLowerCase() === trimmed.toLowerCase())) {
      return `"${trimmed}" is a reserved payment method name`;
    }

    // Check for duplicates (case-insensitive), excluding current name
    if (
      existingNames
        .filter((existing) => existing.toLowerCase() !== currentName.toLowerCase())
        .some((existing) => existing.toLowerCase() === trimmed.toLowerCase())
    ) {
      return `A payment method named "${trimmed}" already exists`;
    }

    return null;
  };

  const handleSubmit = async () => {
    const validationError = validateName(name);
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      await onUpdate(currentName, name.trim());
      onClose();
    } catch {
      // Error handling is done in parent component
    }
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setName(newValue);

    // Clear error when user types
    if (error) {
      setError(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const hasChanged = name.trim().toLowerCase() !== currentName.toLowerCase();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Payment Method</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <TextField
          autoFocus
          margin="dense"
          label="Payment Method Name"
          fullWidth
          value={name}
          onChange={handleNameChange}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          helperText={hasChanged ? 'This will update the name for all orders using this payment method' : ''}
          inputProps={{
            maxLength: 50,
            'aria-label': 'Payment method name',
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isLoading || !name.trim()}
          startIcon={isLoading ? <CircularProgress size={16} /> : undefined}
        >
          {isLoading ? 'Updating...' : 'Update'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
/* eslint-enable complexity */
