"""
Tests for Post-Authentication Lambda trigger
"""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.handlers.post_authentication import lambda_handler


@pytest.fixture
def cognito_event():
    """Sample Cognito Post Authentication event"""
    return {
        "version": "1",
        "triggerSource": "PostAuthentication_Authentication",
        "region": "us-east-1",
        "userPoolId": "us-east-1_TEST123",
        "userName": "google_123456789",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-2.1055.0",
            "clientId": "1example23456789",
        },
        "request": {
            "userAttributes": {
                "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "email": "user@example.com",
                "email_verified": "true",
            },
            "groupConfiguration": {
                "groupsToOverride": [],  # No groups by default (non-admin)
            },
        },
        "response": {},
    }


@pytest.fixture
def lambda_context():
    """Mock Lambda context"""
    context = MagicMock()
    context.function_name = "test-post-auth"
    context.aws_request_id = "test-request-id"
    return context


def test_create_new_account_admin_user(cognito_event, lambda_context, dynamodb_table, monkeypatch):
    """Test creating account for user in ADMIN group"""
    monkeypatch.setenv("TABLE_NAME", "PsmApp")
    
    # Add user to ADMIN group
    cognito_event["request"]["groupConfiguration"]["groupsToOverride"] = ["ADMIN"]
    
    result = lambda_handler(cognito_event, lambda_context)

    # Should return event unmodified
    assert result == cognito_event

    # Check Account was created in DynamoDB
    response = dynamodb_table.get_item(
        Key={
            "PK": "ACCOUNT#a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "SK": "METADATA",
        }
    )

    assert "Item" in response
    account = response["Item"]
    assert account["accountId"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert account["email"] == "user@example.com"
    assert account["isAdmin"] is True  # User in ADMIN group
    assert "createdAt" in account
    assert "updatedAt" in account


def test_create_new_account_regular_user(
    cognito_event, lambda_context, dynamodb_table, monkeypatch
):
    """Test creating account for user not in ADMIN group"""
    monkeypatch.setenv("TABLE_NAME", "PsmApp")
    
    # User has no groups (or only USER group - not ADMIN)
    cognito_event["request"]["groupConfiguration"]["groupsToOverride"] = ["USER"]
    
    result = lambda_handler(cognito_event, lambda_context)

    # Should return event unmodified
    assert result == cognito_event

    # Check Account was created
    response = dynamodb_table.get_item(
        Key={
            "PK": "ACCOUNT#a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "SK": "METADATA",
        }
    )

    assert "Item" in response
    account = response["Item"]
    assert account["isAdmin"] is False  # Not in ADMIN group


def test_update_existing_account(cognito_event, lambda_context, dynamodb_table, monkeypatch):
    """Test updating existing account on subsequent login"""
    monkeypatch.setenv("TABLE_NAME", "PsmApp")
    
    # Add user to ADMIN group
    cognito_event["request"]["groupConfiguration"]["groupsToOverride"] = ["ADMIN"]
    
    # Create existing account with old email and non-admin status
    original_timestamp = "2024-01-01T00:00:00+00:00"
    dynamodb_table.put_item(
        Item={
            "PK": "ACCOUNT#a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "SK": "METADATA",
            "accountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "email": "old@example.com",
            "isAdmin": False,
            "createdAt": original_timestamp,
            "updatedAt": original_timestamp,
        }
    )

    result = lambda_handler(cognito_event, lambda_context)

    # Should return event unmodified
    assert result == cognito_event

    # Check Account was updated
    response = dynamodb_table.get_item(
        Key={
            "PK": "ACCOUNT#a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "SK": "METADATA",
        }
    )

    account = response["Item"]
    assert account["email"] == "user@example.com"  # Updated email
    assert account["isAdmin"] is True  # Updated admin status from group
    assert account["updatedAt"] > original_timestamp  # Updated timestamp
    assert account["createdAt"] == original_timestamp  # Created unchanged


def test_missing_sub_in_event(lambda_context, dynamodb_table, monkeypatch):
    """Test graceful handling of malformed event"""
    monkeypatch.setenv("TABLE_NAME", "PsmApp")
    bad_event = {
        "version": "1",
        "triggerSource": "PostAuthentication_Authentication",
        "request": {"userAttributes": {"email": "user@example.com"}},
        "response": {},
    }

    result = lambda_handler(bad_event, lambda_context)

    # Should still return event (allow auth to continue)
    assert result == bad_event

    # No account should be created
    response = dynamodb_table.scan()
    assert response["Count"] == 0


def test_dynamodb_error_does_not_block_auth(cognito_event, lambda_context):
    """Test that DynamoDB errors don't prevent authentication"""
    # Mock boto3.resource to simulate DynamoDB error
    with patch("boto3.resource") as mock_resource:
        mock_table = MagicMock()
        mock_table.get_item.side_effect = Exception("DynamoDB error")
        mock_resource.return_value.Table.return_value = mock_table

        result = lambda_handler(cognito_event, lambda_context)

        # Should still return event (allow auth to continue)
        assert result == cognito_event


def test_gsi_indexes_created(cognito_event, lambda_context, dynamodb_table, monkeypatch):
    """Test that GSI indexes are properly set on new account"""
    monkeypatch.setenv("TABLE_NAME", "PsmApp")
    result = lambda_handler(cognito_event, lambda_context)

    response = dynamodb_table.get_item(
        Key={
            "PK": "ACCOUNT#a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "SK": "METADATA",
        }
    )

    account = response["Item"]
    assert account["GSI1PK"] == "ACCOUNT#a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert account["GSI1SK"] == "METADATA"
