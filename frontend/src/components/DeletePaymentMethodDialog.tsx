/**
 * DeletePaymentMethodDialog - Confirmation dialog for deleting a payment method
 *
 * Features:
 * - Clear warning message
 * - Requires confirmation before deletion
 * - Loading state during deletion
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';

interface DeletePaymentMethodDialogProps {
  open: boolean;
  onClose: () => void;
  onDelete: () => Promise<void>;
  methodName: string;
  isLoading?: boolean;
}

export const DeletePaymentMethodDialog: React.FC<DeletePaymentMethodDialogProps> = ({
  open,
  onClose,
  onDelete,
  methodName,
  isLoading = false,
}) => {
  const handleDelete = async () => {
    try {
      await onDelete();
      onClose();
    } catch {
      // Error handling is done in parent component
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Delete Payment Method</DialogTitle>
      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          This action cannot be undone.
        </Alert>
        <Typography>
          Are you sure you want to delete the payment method <strong>"{methodName}"</strong>?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Existing orders using this payment method will keep their payment type unchanged.
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleDelete}
          variant="contained"
          color="error"
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={16} /> : undefined}
        >
          {isLoading ? 'Deleting...' : 'Delete'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
