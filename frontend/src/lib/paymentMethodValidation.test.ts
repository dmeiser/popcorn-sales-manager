import { describe, expect, it } from 'vitest';
import { RESERVED_NAMES, MAX_NAME_LENGTH, isReservedName, validatePaymentMethodName } from './paymentMethodValidation';

describe('paymentMethodValidation', () => {
  describe('constants', () => {
    it('has expected reserved names', () => {
      expect(RESERVED_NAMES).toContain('cash');
      expect(RESERVED_NAMES).toContain('check');
      expect(RESERVED_NAMES.length).toBe(2);
    });

    it('has MAX_NAME_LENGTH of 50', () => {
      expect(MAX_NAME_LENGTH).toBe(50);
    });
  });

  describe('isReservedName', () => {
    it('returns true for cash (case-insensitive)', () => {
      expect(isReservedName('cash')).toBe(true);
      expect(isReservedName('Cash')).toBe(true);
      expect(isReservedName('CASH')).toBe(true);
    });

    it('returns true for check (case-insensitive)', () => {
      expect(isReservedName('check')).toBe(true);
      expect(isReservedName('Check')).toBe(true);
      expect(isReservedName('CHECK')).toBe(true);
    });

    it('returns false for non-reserved names', () => {
      expect(isReservedName('Venmo')).toBe(false);
      expect(isReservedName('PayPal')).toBe(false);
      expect(isReservedName('Zelle')).toBe(false);
    });
  });

  describe('validatePaymentMethodName', () => {
    const existingNames = ['Venmo', 'PayPal'];

    describe('required validation', () => {
      it('fails for empty string', () => {
        const result = validatePaymentMethodName('', existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe('Name is required');
      });

      it('fails for whitespace only', () => {
        const result = validatePaymentMethodName('   ', existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe('Name is required');
      });
    });

    describe('length validation', () => {
      it('fails for name exceeding MAX_NAME_LENGTH', () => {
        const longName = 'a'.repeat(MAX_NAME_LENGTH + 1);
        const result = validatePaymentMethodName(longName, existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe(`Name must be ${MAX_NAME_LENGTH} characters or less`);
      });

      it('passes for name at exactly MAX_NAME_LENGTH', () => {
        const exactName = 'a'.repeat(MAX_NAME_LENGTH);
        const result = validatePaymentMethodName(exactName, existingNames);
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });
    });

    describe('reserved name validation', () => {
      it('fails for reserved name cash', () => {
        const result = validatePaymentMethodName('cash', existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe('"cash" is a reserved payment method name');
      });

      it('fails for reserved name check (case-insensitive)', () => {
        const result = validatePaymentMethodName('Check', existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe('"Check" is a reserved payment method name');
      });
    });

    describe('duplicate validation', () => {
      it('fails for duplicate name (case-insensitive)', () => {
        const result = validatePaymentMethodName('venmo', existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe('A payment method named "venmo" already exists');
      });

      it('fails for duplicate name with different case', () => {
        const result = validatePaymentMethodName('PAYPAL', existingNames);
        expect(result.valid).toBe(false);
        expect(result.error).toBe('A payment method named "PAYPAL" already exists');
      });

      it('passes for unique name', () => {
        const result = validatePaymentMethodName('Zelle', existingNames);
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });
    });

    describe('edit mode (with currentName)', () => {
      it('allows keeping the same name in edit mode', () => {
        const result = validatePaymentMethodName('Venmo', existingNames, 'Venmo');
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });

      it('allows keeping same name with different case in edit mode', () => {
        const result = validatePaymentMethodName('venmo', existingNames, 'Venmo');
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });

      it('still fails for duplicate of another method in edit mode', () => {
        const result = validatePaymentMethodName('PayPal', existingNames, 'Venmo');
        expect(result.valid).toBe(false);
        expect(result.error).toBe('A payment method named "PayPal" already exists');
      });

      it('allows unique name in edit mode', () => {
        const result = validatePaymentMethodName('NewName', existingNames, 'Venmo');
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });
    });

    describe('edge cases', () => {
      it('trims whitespace from name', () => {
        const result = validatePaymentMethodName('  Zelle  ', existingNames);
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });

      it('handles empty existingNames array', () => {
        const result = validatePaymentMethodName('Venmo', []);
        expect(result.valid).toBe(true);
        expect(result.error).toBeNull();
      });
    });
  });
});
