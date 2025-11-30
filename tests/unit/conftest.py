"""
Test fixtures for Lambda function tests.

Provides common test data and mocked AWS resources.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generator

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_credentials() -> None:
    """Set fake AWS credentials for moto."""
    import os

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["TABLE_NAME"] = "PsmApp"


@pytest.fixture
def dynamodb_table(aws_credentials: None) -> Generator[Any, None, None]:
    """Create mock DynamoDB table with GSIs."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create table with GSIs
        table = dynamodb.create_table(
            TableName="PsmApp",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
                {"AttributeName": "GSI2PK", "AttributeType": "S"},
                {"AttributeName": "GSI2SK", "AttributeType": "S"},
                {"AttributeName": "GSI3PK", "AttributeType": "S"},
                {"AttributeName": "GSI3SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "GSI2",
                    "KeySchema": [
                        {"AttributeName": "GSI2PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI2SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "GSI3",
                    "KeySchema": [
                        {"AttributeName": "GSI3PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI3SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield table


@pytest.fixture
def sample_account_id() -> str:
    """Sample account ID (Cognito sub)."""
    return "user-123-456"


@pytest.fixture
def sample_profile_id() -> str:
    """Sample profile ID."""
    return "PROFILE#abc-def-123"


@pytest.fixture
def sample_profile(dynamodb_table: Any, sample_account_id: str, sample_profile_id: str) -> Dict[str, Any]:
    """Create sample profile in DynamoDB."""
    profile = {
        "PK": sample_profile_id,
        "SK": "METADATA",
        "profileId": sample_profile_id,
        "ownerAccountId": sample_account_id,
        "scoutName": "Test Scout",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    dynamodb_table.put_item(Item=profile)
    return profile


@pytest.fixture
def another_account_id() -> str:
    """Another account ID for sharing tests."""
    return "user-789-xyz"


@pytest.fixture
def lambda_context() -> Any:
    """Mock Lambda context."""

    class Context:
        function_name = "test-function"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        aws_request_id = "test-request-id"

    return Context()


@pytest.fixture
def appsync_event(sample_account_id: str) -> Dict[str, Any]:
    """Base AppSync event structure."""
    return {
        "arguments": {},
        "identity": {
            "sub": sample_account_id,
            "username": "testuser",
        },
        "requestContext": {
            "requestId": "test-correlation-id",
        },
        "info": {
            "fieldName": "testField",
            "parentTypeName": "Query",
        },
    }
