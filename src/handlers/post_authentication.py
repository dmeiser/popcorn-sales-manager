"""
Cognito Post-Authentication Lambda Trigger

Creates or updates the Account record in DynamoDB when a user successfully authenticates.
This ensures that getMyAccount always has data to return.

Trigger: Post Authentication
Event: After user signs in (including first-time social login)
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Post-Authentication Lambda Trigger Handler

    Creates or updates Account record in DynamoDB after successful authentication.

    Event structure:
    {
        "version": "1",
        "triggerSource": "PostAuthentication_Authentication",
        "region": "us-east-1",
        "userPoolId": "us-east-1_EXAMPLE",
        "userName": "google_123456789",
        "callerContext": {...},
        "request": {
            "userAttributes": {
                "sub": "a1b2c3d4-...",
                "email": "user@example.com",
                "email_verified": "true",
                "identities": "[...]"
            }
        },
        "response": {}
    }

    Args:
        event: Cognito Post Authentication trigger event
        context: Lambda context

    Returns:
        event: Must return the event unmodified for Cognito to continue
    """
    try:
        # Get table reference (inside function for testability)
        dynamodb = boto3.resource("dynamodb")
        table_name = os.environ.get("TABLE_NAME", "kernelworx-app-dev")
        table = dynamodb.Table(table_name)

        logger.info(f"Post-authentication trigger invoked: {event.get('triggerSource')}")

        # Extract user attributes
        user_attributes = event.get("request", {}).get("userAttributes", {})
        account_id = user_attributes.get("sub")
        email = user_attributes.get("email", "")
        email_verified = user_attributes.get("email_verified") == "true"

        if not account_id:
            logger.error("Missing sub (account_id) in user attributes")
            return event  # Return event to allow auth to continue

        # Check if Account already exists
        existing_account = table.get_item(
            Key={"PK": f"ACCOUNT#{account_id}", "SK": "METADATA"}
        ).get("Item")

        timestamp = datetime.now(timezone.utc).isoformat()

        if existing_account:
            # Update existing account (email might have changed, update timestamp)
            logger.info(f"Updating existing account: {account_id}")
            table.update_item(
                Key={"PK": f"ACCOUNT#{account_id}", "SK": "METADATA"},
                UpdateExpression="SET email = :email, updatedAt = :updated",
                ExpressionAttributeValues={":email": email, ":updated": timestamp},
            )
        else:
            # Create new Account record
            logger.info(f"Creating new account: {account_id}")

            # Check if this is the first user (make them admin)
            # This is a simple approach - in production, use a more controlled method
            scan_response = table.scan(
                FilterExpression="begins_with(PK, :prefix)",
                ExpressionAttributeValues={":prefix": "ACCOUNT#"},
                Limit=1,
            )
            is_first_user = len(scan_response.get("Items", [])) == 0

            account_item = {
                "PK": f"ACCOUNT#{account_id}",
                "SK": "METADATA",
                "accountId": account_id,
                "email": email,
                "isAdmin": is_first_user,  # First user gets admin rights
                "createdAt": timestamp,
                "updatedAt": timestamp,
                "GSI1PK": f"ACCOUNT#{account_id}",  # For account lookups
                "GSI1SK": "METADATA",
            }

            table.put_item(Item=account_item)

            logger.info(
                f"Account created successfully: {account_id}, email={email}, is_admin={is_first_user}"
            )

        # IMPORTANT: Must return the event for Cognito to continue
        return event

    except Exception as e:
        logger.exception(f"Error in post-authentication trigger: {str(e)}")
        # IMPORTANT: Still return event to allow authentication to succeed
        # Don't fail auth because of DynamoDB issues
        return event
