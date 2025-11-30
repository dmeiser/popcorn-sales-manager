"""
Authorization utilities for checking profile and resource access.

Implements owner-based and share-based authorization model.
"""

import os
from typing import Any, Dict, Optional

import boto3
from mypy_boto3_dynamodb.service_resource import Table

from .errors import AppError, ErrorCode

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", endpoint_url=os.getenv("DYNAMODB_ENDPOINT"))


def get_table() -> Table:
    """Get DynamoDB table instance."""
    table_name = os.getenv("TABLE_NAME", "PsmApp")
    return dynamodb.Table(table_name)


def check_profile_access(
    caller_account_id: str, profile_id: str, required_permission: str = "READ"
) -> bool:
    """
    Check if caller has access to a profile.
    
    Args:
        caller_account_id: Cognito sub (Account ID) of the caller
        profile_id: Profile ID to check access for
        required_permission: "READ" or "WRITE"
        
    Returns:
        True if caller has access, False otherwise
        
    Raises:
        AppError: If profile not found
    """
    table = get_table()
    
    # Get profile
    response = table.get_item(Key={"PK": profile_id, "SK": "METADATA"})
    
    if "Item" not in response:
        raise AppError(ErrorCode.NOT_FOUND, f"Profile {profile_id} not found")
    
    profile = response["Item"]
    
    # Check if caller is owner
    if profile.get("ownerAccountId") == caller_account_id:  # pragma: no branch
        return True
    
    # Check if caller has appropriate share
    share_response = table.get_item(
        Key={"PK": profile_id, "SK": f"SHARE#{caller_account_id}"}
    )
    
    if "Item" in share_response:
        share = share_response["Item"]
        permissions = share.get("permissions", [])
        
        if required_permission == "READ" and "READ" in permissions:
            return True
        if required_permission == "WRITE" and "WRITE" in permissions:
            return True
    
    return False


def require_profile_access(
    caller_account_id: str, profile_id: str, required_permission: str = "READ"
) -> None:
    """
    Require caller to have profile access or raise FORBIDDEN error.
    
    Args:
        caller_account_id: Cognito sub (Account ID) of the caller
        profile_id: Profile ID to check access for
        required_permission: "READ" or "WRITE"
        
    Raises:
        AppError: If caller doesn't have required access
    """
    if not check_profile_access(caller_account_id, profile_id, required_permission):
        raise AppError(
            ErrorCode.FORBIDDEN,
            f"You do not have {required_permission} access to this profile",
        )


def is_profile_owner(caller_account_id: str, profile_id: str) -> bool:
    """
    Check if caller is the owner of a profile.
    
    Args:
        caller_account_id: Cognito sub (Account ID) of the caller
        profile_id: Profile ID to check
        
    Returns:
        True if caller is owner, False otherwise
        
    Raises:
        AppError: If profile not found
    """
    table = get_table()
    
    response = table.get_item(Key={"PK": profile_id, "SK": "METADATA"})
    
    if "Item" not in response:
        raise AppError(ErrorCode.NOT_FOUND, f"Profile {profile_id} not found")
    
    profile = response["Item"]
    return profile.get("ownerAccountId") == caller_account_id


def get_account(account_id: str) -> Optional[Dict[str, Any]]:
    """
    Get account by ID.
    
    Args:
        account_id: Cognito sub (Account ID)
        
    Returns:
        Account item or None if not found
    """
    table = get_table()
    
    response = table.get_item(Key={"PK": f"ACCOUNT#{account_id}", "SK": "METADATA"})
    
    return response.get("Item")


def is_admin(account_id: str) -> bool:
    """
    Check if account has admin privileges.
    
    Args:
        account_id: Cognito sub (Account ID)
        
    Returns:
        True if account is admin, False otherwise
    """
    account = get_account(account_id)
    if not account:
        return False
    
    return account.get("isAdmin", False)
