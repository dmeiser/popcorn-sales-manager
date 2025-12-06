"""
Input validation utilities.

Validates customer information, phone numbers, addresses, etc.
"""

import re
from typing import Any, Dict, Optional

from .errors import AppError, ErrorCode

# US phone number pattern: 10 digits with optional formatting
PHONE_PATTERN = re.compile(r"^(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$")


def normalize_phone(phone: str) -> str:
    """
    Normalize US phone number to E.164 format (+1XXXXXXXXXX).

    Args:
        phone: Phone number with various formatting

    Returns:
        Normalized phone number

    Raises:
        AppError: If phone number is invalid
    """
    match = PHONE_PATTERN.match(phone.strip())

    if not match:
        raise AppError(
            ErrorCode.INVALID_PHONE,
            "Phone number must be a valid 10-digit US number",
            {"phone": phone},
        )

    # Extract digits and format as E.164
    area_code, prefix, line = match.groups()
    return f"+1{area_code}{prefix}{line}"


def validate_address(address: Dict[str, Any]) -> None:
    """
    Validate address has all required fields.

    Args:
        address: Address dictionary with street, city, state, zip

    Raises:
        AppError: If address is missing required fields
    """
    required_fields = ["street", "city", "state", "zip"]
    missing_fields = [field for field in required_fields if not address.get(field)]

    if missing_fields:
        raise AppError(
            ErrorCode.INVALID_ADDRESS,
            "Address is missing required fields",
            {"missingFields": missing_fields},
        )

    # Validate zip code (5 or 9 digits)
    zip_code = str(address.get("zip", "")).strip()
    if not re.match(r"^\d{5}(-\d{4})?$", zip_code):
        raise AppError(
            ErrorCode.INVALID_ADDRESS, "ZIP code must be 5 or 9 digits", {"zip": zip_code}
        )


def validate_customer_input(customer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate customer information for orders.

    Requirements:
    - Name is required
    - At least one of phone or address is required
    - If address provided, all fields must be present
    - Phone must be valid US format

    Args:
        customer: Customer dictionary

    Returns:
        Validated and normalized customer data

    Raises:
        AppError: If validation fails
    """
    # Name is required
    if not customer.get("name", "").strip():
        raise AppError(ErrorCode.INVALID_INPUT, "Customer name is required")

    # At least one contact method required
    has_phone = bool(customer.get("phone"))
    has_address = bool(customer.get("address"))

    if not has_phone and not has_address:
        raise AppError(
            ErrorCode.INVALID_INPUT,
            "Customer must have at least one contact method (phone or address)",
        )

    # Normalize and validate phone if provided
    validated_customer = {"name": customer["name"].strip()}

    if has_phone:
        validated_customer["phone"] = normalize_phone(customer["phone"])

    # Validate address if provided
    if has_address:
        validate_address(customer["address"])
        validated_customer["address"] = customer["address"]

    return validated_customer


def validate_invite_code(invite_code: str) -> str:
    """
    Validate invite code format.

    Args:
        invite_code: Invite code to validate

    Returns:
        Uppercase invite code

    Raises:
        AppError: If invite code is invalid
    """
    code = invite_code.strip().upper()

    # Invite codes should be 8-12 alphanumeric characters
    if not re.match(r"^[A-Z0-9]{8,12}$", code):
        raise AppError(
            ErrorCode.INVALID_INPUT,
            "Invite code must be 8-12 alphanumeric characters",
            {"inviteCode": invite_code},
        )

    return code
