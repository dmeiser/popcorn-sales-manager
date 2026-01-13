/**
 * Shared payment method validation rules.
 *
 * These rules are kept consistent with the backend validation
 * in src/utils/payment_methods.py.
 */

// Reserved payment method names (case-insensitive)
export const RESERVED_NAMES = ['cash', 'check'] as const;

// Maximum payment method name length
export const MAX_NAME_LENGTH = 50;

/**
 * Check if a payment method name is reserved.
 */
export function isReservedName(name: string): boolean {
  return RESERVED_NAMES.includes(name.toLowerCase() as (typeof RESERVED_NAMES)[number]);
}

/**
 * Validation result for payment method names.
 */
export interface ValidationResult {
  valid: boolean;
  error: string | null;
}

/**
 * Validate a payment method name.
 *
 * Checks:
 * - Name is not empty
 * - Name does not exceed MAX_NAME_LENGTH characters
 * - Name is not reserved (case-insensitive)
 * - Name is not a duplicate (case-insensitive)
 *
 * @param name - Name to validate
 * @param existingNames - Existing payment method names to check for duplicates
 * @param currentName - Current name (for edit mode, excludes self from duplicate check)
 */
/* eslint-disable complexity -- Sequential validation checks */
export function validatePaymentMethodName(
  name: string,
  existingNames: string[],
  currentName?: string,
): ValidationResult {
  const trimmed = name.trim();

  // Required check
  if (!trimmed) {
    return { valid: false, error: 'Name is required' };
  }

  // Length check
  if (trimmed.length > MAX_NAME_LENGTH) {
    return { valid: false, error: `Name must be ${MAX_NAME_LENGTH} characters or less` };
  }

  // Reserved name check (case-insensitive)
  if (isReservedName(trimmed)) {
    return { valid: false, error: `"${trimmed}" is a reserved payment method name` };
  }

  // Allow keeping the same name in edit mode (case-insensitive)
  if (currentName && trimmed.toLowerCase() === currentName.toLowerCase()) {
    return { valid: true, error: null };
  }

  // Duplicate check (case-insensitive), excluding current name if editing
  const namesToCheck = currentName
    ? existingNames.filter((n) => n.toLowerCase() !== currentName.toLowerCase())
    : existingNames;

  if (namesToCheck.some((n) => n.toLowerCase() === trimmed.toLowerCase())) {
    return { valid: false, error: `A payment method named "${trimmed}" already exists` };
  }

  return { valid: true, error: null };
}
