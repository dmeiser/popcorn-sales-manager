"""Tests for validation utilities."""

from typing import Any, Dict

import pytest

from src.utils.errors import AppError, ErrorCode
from src.utils.validation import (
    normalize_phone,
    validate_address,
    validate_customer_input,
    validate_invite_code,
)


class TestNormalizePhone:
    """Tests for normalize_phone function."""

    def test_normalize_plain_10_digits(self) -> None:
        """Test normalizing plain 10-digit phone."""
        result = normalize_phone("1234567890")
        assert result == "+11234567890"

    def test_normalize_with_dashes(self) -> None:
        """Test normalizing phone with dashes."""
        result = normalize_phone("123-456-7890")
        assert result == "+11234567890"

    def test_normalize_with_dots(self) -> None:
        """Test normalizing phone with dots."""
        result = normalize_phone("123.456.7890")
        assert result == "+11234567890"

    def test_normalize_with_spaces(self) -> None:
        """Test normalizing phone with spaces."""
        result = normalize_phone("123 456 7890")
        assert result == "+11234567890"

    def test_normalize_with_parens(self) -> None:
        """Test normalizing phone with parentheses."""
        result = normalize_phone("(123) 456-7890")
        assert result == "+11234567890"

    def test_normalize_with_plus_one(self) -> None:
        """Test normalizing phone with +1 prefix."""
        result = normalize_phone("+1-123-456-7890")
        assert result == "+11234567890"

    def test_invalid_phone_too_short(self) -> None:
        """Test that too-short phone raises error."""
        with pytest.raises(AppError) as exc_info:
            normalize_phone("12345")
        assert exc_info.value.error_code == ErrorCode.INVALID_PHONE

    def test_invalid_phone_with_letters(self) -> None:
        """Test that phone with letters raises error."""
        with pytest.raises(AppError) as exc_info:
            normalize_phone("123-456-ABCD")
        assert exc_info.value.error_code == ErrorCode.INVALID_PHONE


class TestValidateAddress:
    """Tests for validate_address function."""

    def test_valid_address_passes(self) -> None:
        """Test that valid address passes validation."""
        address = {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62701"}

        # Should not raise
        validate_address(address)

    def test_valid_address_with_9_digit_zip(self) -> None:
        """Test that 9-digit ZIP code is valid."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701-1234",
        }

        validate_address(address)

    def test_missing_street_raises_error(self) -> None:
        """Test that missing street raises error."""
        address = {"city": "Springfield", "state": "IL", "zip": "62701"}

        with pytest.raises(AppError) as exc_info:
            validate_address(address)

        assert exc_info.value.error_code == ErrorCode.INVALID_ADDRESS
        assert "street" in exc_info.value.details["missingFields"]

    def test_missing_multiple_fields_raises_error(self) -> None:
        """Test that missing multiple fields raises error."""
        address = {"street": "123 Main St"}

        with pytest.raises(AppError) as exc_info:
            validate_address(address)

        assert exc_info.value.error_code == ErrorCode.INVALID_ADDRESS
        assert "city" in exc_info.value.details["missingFields"]
        assert "state" in exc_info.value.details["missingFields"]
        assert "zip" in exc_info.value.details["missingFields"]

    def test_invalid_zip_raises_error(self) -> None:
        """Test that invalid ZIP code raises error."""
        address = {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "ABC"}

        with pytest.raises(AppError) as exc_info:
            validate_address(address)

        assert exc_info.value.error_code == ErrorCode.INVALID_ADDRESS


class TestValidateCustomerInput:
    """Tests for validate_customer_input function."""

    def test_valid_customer_with_phone(self) -> None:
        """Test valid customer with phone."""
        customer = {"name": "John Doe", "phone": "123-456-7890"}

        result = validate_customer_input(customer)

        assert result["name"] == "John Doe"
        assert result["phone"] == "+11234567890"
        assert "address" not in result

    def test_valid_customer_with_address(self) -> None:
        """Test valid customer with address."""
        customer = {
            "name": "Jane Smith",
            "address": {"street": "456 Oak Ave", "city": "Boston", "state": "MA", "zip": "02101"},
        }

        result = validate_customer_input(customer)

        assert result["name"] == "Jane Smith"
        assert result["address"] == customer["address"]
        assert "phone" not in result

    def test_valid_customer_with_both(self) -> None:
        """Test valid customer with both phone and address."""
        customer = {
            "name": "Bob Johnson",
            "phone": "(555) 123-4567",
            "address": {"street": "789 Elm St", "city": "Austin", "state": "TX", "zip": "78701"},
        }

        result = validate_customer_input(customer)

        assert result["name"] == "Bob Johnson"
        assert result["phone"] == "+15551234567"
        assert result["address"] == customer["address"]

    def test_missing_name_raises_error(self) -> None:
        """Test that missing name raises error."""
        customer = {"phone": "123-456-7890"}

        with pytest.raises(AppError) as exc_info:
            validate_customer_input(customer)

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT
        assert "name" in exc_info.value.message

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises error."""
        customer = {"name": "   ", "phone": "123-456-7890"}

        with pytest.raises(AppError) as exc_info:
            validate_customer_input(customer)

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT

    def test_no_contact_method_raises_error(self) -> None:
        """Test that missing both phone and address raises error."""
        customer = {"name": "Test User"}

        with pytest.raises(AppError) as exc_info:
            validate_customer_input(customer)

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT
        assert "contact method" in exc_info.value.message

    def test_invalid_phone_raises_error(self) -> None:
        """Test that invalid phone raises error."""
        customer = {"name": "Test User", "phone": "invalid"}

        with pytest.raises(AppError) as exc_info:
            validate_customer_input(customer)

        assert exc_info.value.error_code == ErrorCode.INVALID_PHONE

    def test_invalid_address_raises_error(self) -> None:
        """Test that invalid address raises error."""
        customer = {"name": "Test User", "address": {"street": "123 Main"}}

        with pytest.raises(AppError) as exc_info:
            validate_customer_input(customer)

        assert exc_info.value.error_code == ErrorCode.INVALID_ADDRESS


class TestValidateInviteCode:
    """Tests for validate_invite_code function."""

    def test_valid_8_char_code(self) -> None:
        """Test valid 8-character code."""
        result = validate_invite_code("ABC12345")
        assert result == "ABC12345"

    def test_valid_12_char_code(self) -> None:
        """Test valid 12-character code."""
        result = validate_invite_code("ABCD1234EFGH")
        assert result == "ABCD1234EFGH"

    def test_lowercase_converted_to_uppercase(self) -> None:
        """Test that lowercase is converted to uppercase."""
        result = validate_invite_code("abc12345")
        assert result == "ABC12345"

    def test_code_with_whitespace_trimmed(self) -> None:
        """Test that whitespace is trimmed."""
        result = validate_invite_code("  ABC12345  ")
        assert result == "ABC12345"

    def test_too_short_raises_error(self) -> None:
        """Test that code too short raises error."""
        with pytest.raises(AppError) as exc_info:
            validate_invite_code("ABC123")

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT

    def test_too_long_raises_error(self) -> None:
        """Test that code too long raises error."""
        with pytest.raises(AppError) as exc_info:
            validate_invite_code("ABCD1234EFGH5")

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT

    def test_special_chars_raise_error(self) -> None:
        """Test that special characters raise error."""
        with pytest.raises(AppError) as exc_info:
            validate_invite_code("ABC-12345")

        assert exc_info.value.error_code == ErrorCode.INVALID_INPUT
