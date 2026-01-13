/**
 * useQRUpload - Reusable hook for QR code upload flow
 *
 * Encapsulates the complete QR upload workflow:
 * - Request pre-signed upload URL from server
 * - Upload file to S3 using pre-signed POST
 * - Confirm upload completion with server
 * - Handle errors and loading states
 */

import { useState, useCallback } from 'react';
import { useMutation } from '@apollo/client/react';
import type { ApolloQueryResult } from '@apollo/client';
import {
  REQUEST_PAYMENT_METHOD_QR_UPLOAD,
  CONFIRM_PAYMENT_METHOD_QR_UPLOAD,
  DELETE_PAYMENT_METHOD_QR_CODE,
} from '../lib/graphql';

interface S3UploadInfo {
  uploadUrl: string;
  fields: string;
  s3Key: string;
}

interface RequestQRUploadData {
  requestPaymentMethodQRCodeUpload: S3UploadInfo;
}

interface UseQRUploadOptions {
  /** Callback after successful upload */
  onSuccess?: () => void;
  /** Callback after successful QR deletion */
  onDeleteSuccess?: () => void;
  /** Callback to refetch data after upload/delete */
  refetch?: () => Promise<ApolloQueryResult<unknown>>;
}

interface UseQRUploadReturn {
  /** Upload a QR code for a payment method */
  uploadQRCode: (paymentMethodName: string, file: File) => Promise<void>;
  /** Delete a QR code for a payment method */
  deleteQRCode: (paymentMethodName: string) => Promise<void>;
  /** Whether an upload is in progress */
  isUploading: boolean;
  /** Whether a deletion is in progress */
  isDeleting: boolean;
  /** Current upload error message, null if no error */
  uploadError: string | null;
  /** Clear the current error */
  clearError: () => void;
  /** Name of method currently being deleted (for UI tracking) */
  deletingMethodName: string | null;
}

/**
 * Upload a file to S3 using pre-signed POST.
 */
async function uploadToS3(uploadUrl: string, fields: string, file: File): Promise<void> {
  const parsedFields = typeof fields === 'string' ? JSON.parse(fields) : fields;
  const formData = new FormData();

  // Add all fields from the pre-signed POST policy
  Object.entries(parsedFields).forEach(([key, value]) => {
    formData.append(key, value as string);
  });

  // File must be last in the form data
  formData.append('file', file);

  const response = await fetch(uploadUrl, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload file to S3');
  }
}

/**
 * Hook for managing QR code upload and deletion flows.
 *
 * @example
 * ```tsx
 * const { uploadQRCode, isUploading, uploadError } = useQRUpload({
 *   onSuccess: () => showToast('QR code uploaded!'),
 *   refetch: refetchPaymentMethods,
 * });
 *
 * // In handler:
 * await uploadQRCode('Venmo', file);
 * ```
 */
export function useQRUpload(options: UseQRUploadOptions = {}): UseQRUploadReturn {
  const { onSuccess, onDeleteSuccess, refetch } = options;

  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [deletingMethodName, setDeletingMethodName] = useState<string | null>(null);

  const [requestUpload] = useMutation<RequestQRUploadData>(REQUEST_PAYMENT_METHOD_QR_UPLOAD);
  const [confirmUpload] = useMutation(CONFIRM_PAYMENT_METHOD_QR_UPLOAD);
  const [deleteQR] = useMutation(DELETE_PAYMENT_METHOD_QR_CODE);

  const clearError = useCallback(() => {
    setUploadError(null);
  }, []);

  /* eslint-disable complexity -- Multi-step async upload flow */
  const uploadQRCode = useCallback(
    async (paymentMethodName: string, file: File): Promise<void> => {
      setUploadError(null);
      setIsUploading(true);

      try {
        // Step 1: Request pre-signed upload URL
        const { data: uploadData } = await requestUpload({
          variables: { paymentMethodName },
        });

        if (!uploadData) {
          throw new Error('Failed to get upload URL');
        }

        const { uploadUrl, fields, s3Key } = uploadData.requestPaymentMethodQRCodeUpload;

        // Step 2: Upload file to S3
        await uploadToS3(uploadUrl, fields, file);

        // Step 3: Confirm upload with server
        await confirmUpload({
          variables: {
            paymentMethodName,
            s3Key,
          },
        });

        // Step 4: Refetch data and call success callback
        if (refetch) {
          await refetch();
        }
        onSuccess?.();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to upload QR code';
        setUploadError(message);
        throw err; // Re-throw so caller can handle (e.g., keep dialog open)
      } finally {
        setIsUploading(false);
      }
    },
    [requestUpload, confirmUpload, refetch, onSuccess],
  );

  const deleteQRCode = useCallback(
    async (paymentMethodName: string): Promise<void> => {
      setDeletingMethodName(paymentMethodName);

      try {
        await deleteQR({
          variables: { paymentMethodName },
        });

        if (refetch) {
          await refetch();
        }
        onDeleteSuccess?.();
      } finally {
        setDeletingMethodName(null);
      }
    },
    [deleteQR, refetch, onDeleteSuccess],
  );

  return {
    uploadQRCode,
    deleteQRCode,
    isUploading,
    isDeleting: deletingMethodName !== null,
    uploadError,
    clearError,
    deletingMethodName,
  };
}
