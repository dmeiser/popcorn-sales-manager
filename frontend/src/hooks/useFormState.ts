/**
 * Generic form state management hook.
 *
 * Reduces boilerplate for forms with multiple fields by providing
 * a single state object and update handlers.
 */

import { useState, useCallback, useMemo } from 'react';

export interface UseFormStateOptions<T> {
  /** Initial form values */
  initialValues: T;

  /** Optional validation function */
  validate?: (values: T) => Record<string, string> | null;

  /** Optional transform function before update */
  transform?: (key: keyof T, value: unknown) => unknown;
}

export interface UseFormStateReturn<T> {
  /** Current form values */
  values: T;

  /** Update a single field */
  setValue: <K extends keyof T>(key: K, value: T[K]) => void;

  /** Update multiple fields at once */
  setValues: (updates: Partial<T>) => void;

  /** Reset to initial values */
  reset: () => void;

  /** Reset to specific values */
  resetTo: (newValues: T) => void;

  /** Validation errors (if validate provided) */
  errors: Record<string, string>;

  /** Whether form is valid (no errors) */
  isValid: boolean;

  /** Whether form has been modified from initial values */
  isDirty: boolean;
}

export function useFormState<T extends object>(options: UseFormStateOptions<T>): UseFormStateReturn<T> {
  const { initialValues, validate, transform } = options;

  const [values, setValuesState] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [initialSnapshot, setInitialSnapshot] = useState<T>(initialValues);

  const runValidation = useCallback(
    (newValues: T) => {
      if (validate) {
        const validationErrors = validate(newValues);
        setErrors(validationErrors || {});
      }
    },
    [validate],
  );

  const setValue = useCallback(
    <K extends keyof T>(key: K, value: T[K]) => {
      const transformedValue = transform ? (transform(key, value) as T[K]) : value;

      setValuesState((prev) => {
        const newValues = {
          ...prev,
          [key]: transformedValue,
        };
        runValidation(newValues);
        return newValues;
      });
    },
    [transform, runValidation],
  );

  const setValues = useCallback(
    (updates: Partial<T>) => {
      setValuesState((prev) => {
        const newValues = {
          ...prev,
          ...updates,
        };
        runValidation(newValues);
        return newValues;
      });
    },
    [runValidation],
  );

  const reset = useCallback(() => {
    setValuesState(initialSnapshot);
    setErrors({});
  }, [initialSnapshot]);

  const resetTo = useCallback((newValues: T) => {
    setValuesState(newValues);
    setInitialSnapshot(newValues);
    setErrors({});
  }, []);

  const isDirty = useMemo(() => {
    return JSON.stringify(values) !== JSON.stringify(initialSnapshot);
  }, [values, initialSnapshot]);

  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0;
  }, [errors]);

  return {
    values,
    setValue,
    setValues,
    reset,
    resetTo,
    errors,
    isValid,
    isDirty,
  };
}
