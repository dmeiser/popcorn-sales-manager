"""Unit tests for report generation Lambda handler."""

import csv
import os
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO, StringIO
from typing import Any, Dict

import boto3
import openpyxl
import pytest

from src.handlers.report_generation import request_season_report


@pytest.fixture
def sample_orders(
    dynamodb_table: Any, sample_profile_id: str, sample_season_id: str
) -> list[Dict[str, Any]]:
    """Sample order data for testing."""
    orders = [
        {
            "PK": sample_profile_id,
            "SK": "ORDER#order-1",
            "orderId": "ORDER#order-1",
            "seasonId": sample_season_id,
            "profileId": sample_profile_id,
            "customerName": "John Doe",
            "customerPhone": "555-123-4567",
            "customerAddress": "123 Main St",
            "paymentMethod": "CASH",
            "totalAmount": Decimal("45.00"),
            "lineItems": [
                {"productName": "Product A", "quantity": 2, "price": Decimal("10.00")},
                {"productName": "Product B", "quantity": 1, "price": Decimal("25.00")},
            ],
            "createdAt": "2025-09-15T10:00:00+00:00",
        },
        {
            "PK": sample_profile_id,
            "SK": "ORDER#order-2",
            "orderId": "ORDER#order-2",
            "seasonId": sample_season_id,
            "profileId": sample_profile_id,
            "customerName": "Jane Smith",
            "customerEmail": "jane@example.com",
            "paymentMethod": "CHECK",
            "totalAmount": Decimal("30.00"),
            "lineItems": [
                {"productName": "Product C", "quantity": 3, "price": Decimal("10.00")},
            ],
            "createdAt": "2025-09-20T14:30:00+00:00",
        },
    ]
    
    for order in orders:
        dynamodb_table.put_item(Item=order)
    
    return orders


class TestRequestSeasonReport:
    """Tests for requestSeasonReport Lambda handler."""

    def test_owner_can_generate_excel_report(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_season: Dict[str, Any],
        sample_orders: list[Dict[str, Any]],
        sample_account_id: str,
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that profile owner can generate Excel report."""
        # Arrange
        event = {
            **appsync_event,
            "arguments": {"seasonId": sample_season_id, "format": "xlsx"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert "reportId" in result
        assert result["reportId"].startswith("REPORT#")
        assert "reportUrl" in result
        assert result["status"] == "COMPLETED"
        assert "expiresAt" in result

        # Verify S3 upload
        bucket_name = os.environ.get("EXPORTS_BUCKET", "test-exports-bucket")
        objects = s3_bucket.list_objects_v2(Bucket=bucket_name)
        assert objects["KeyCount"] == 1
        assert objects["Contents"][0]["Key"].endswith(".xlsx")

        # Verify Excel content
        obj = s3_bucket.get_object(
            Bucket=bucket_name, Key=objects["Contents"][0]["Key"]
        )
        wb = openpyxl.load_workbook(BytesIO(obj["Body"].read()))
        ws = wb.active

        # Check title
        assert "Fall 2025" in str(ws["A1"].value)

        # Check headers
        assert ws["A3"].value == "Customer Name"
        assert ws["B3"].value == "Contact"

        # Check data rows
        assert ws["A4"].value == "John Doe"
        assert ws["A5"].value == "Jane Smith"

    def test_owner_can_generate_csv_report(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_season: Dict[str, Any],
        sample_orders: list[Dict[str, Any]],
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that profile owner can generate CSV report."""
        # Arrange
        event = {
            **appsync_event,
            "arguments": {"seasonId": sample_season_id, "format": "csv"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert result["status"] == "COMPLETED"
        assert "reportUrl" in result

        # Verify S3 upload
        bucket_name = os.environ.get("EXPORTS_BUCKET", "test-exports-bucket")
        objects = s3_bucket.list_objects_v2(Bucket=bucket_name)
        assert objects["KeyCount"] == 1
        assert objects["Contents"][0]["Key"].endswith(".csv")

        # Verify CSV content
        obj = s3_bucket.get_object(
            Bucket=bucket_name, Key=objects["Contents"][0]["Key"]
        )
        csv_content = obj["Body"].read().decode("utf-8")

        assert "Customer Name" in csv_content
        assert "John Doe" in csv_content
        assert "Jane Smith" in csv_content
        assert "Total Orders,2" in csv_content

    def test_contributor_with_read_can_generate_report(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_profile_id: str,
        sample_season: Dict[str, Any],
        sample_orders: list[Dict[str, Any]],
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
        another_account_id: str,
    ) -> None:
        """Test that contributor with READ permission can generate report."""
        # Create share with READ permission
        dynamodb_table.put_item(
            Item={
                "PK": sample_profile_id,
                "SK": f"SHARE#{another_account_id}",
                "permissions": ["READ"],
                "grantedAt": datetime.now(timezone.utc).isoformat(),
            }
        )

        event = {
            **appsync_event,
            "identity": {"sub": another_account_id},
            "arguments": {"seasonId": sample_season_id, "format": "xlsx"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert result["status"] == "COMPLETED"

    def test_non_owner_without_share_cannot_generate_report(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_season: Dict[str, Any],
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
        another_account_id: str,
    ) -> None:
        """Test that non-owner without share cannot generate report."""
        event = {
            **appsync_event,
            "identity": {"sub": another_account_id},
            "arguments": {"seasonId": sample_season_id, "format": "xlsx"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert "errorCode" in result
        assert result["errorCode"] == "FORBIDDEN"

    def test_nonexistent_season_returns_error(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that requesting report for non-existent season returns error."""
        event = {
            **appsync_event,
            "arguments": {"seasonId": "SEASON#nonexistent", "format": "xlsx"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert "errorCode" in result
        assert result["errorCode"] == "NOT_FOUND"

    def test_default_format_is_xlsx(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_season: Dict[str, Any],
        sample_orders: list[Dict[str, Any]],
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that default format is xlsx when not specified."""
        event = {
            **appsync_event,
            "arguments": {"seasonId": sample_season_id},  # No format specified
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert result["status"] == "COMPLETED"

        # Verify S3 upload is xlsx
        bucket_name = os.environ.get("EXPORTS_BUCKET", "test-exports-bucket")
        objects = s3_bucket.list_objects_v2(Bucket=bucket_name)
        assert objects["Contents"][0]["Key"].endswith(".xlsx")

    def test_empty_season_generates_report_with_no_orders(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_season: Dict[str, Any],
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that empty season (no orders) generates valid report."""
        event = {
            **appsync_event,
            "arguments": {"seasonId": sample_season_id, "format": "csv"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert
        assert result["status"] == "COMPLETED"

        # Verify CSV content shows 0 orders
        bucket_name = os.environ.get("EXPORTS_BUCKET", "test-exports-bucket")
        objects = s3_bucket.list_objects_v2(Bucket=bucket_name)
        obj = s3_bucket.get_object(
            Bucket=bucket_name, Key=objects["Contents"][0]["Key"]
        )
        csv_content = obj["Body"].read().decode("utf-8")

        assert "Total Orders,0" in csv_content

    def test_presigned_url_expiration_is_7_days(
        self,
        dynamodb_table: Any,
        s3_bucket: Any,
        sample_profile: Dict[str, Any],
        sample_season: Dict[str, Any],
        sample_orders: list[Dict[str, Any]],
        sample_season_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that pre-signed URL expires in 7 days."""
        event = {
            **appsync_event,
            "arguments": {"seasonId": sample_season_id, "format": "xlsx"},
        }

        # Act
        result = request_season_report(event, lambda_context)

        # Assert - verify expiresAt is approximately 7 days from now
        expires_at = datetime.fromisoformat(result["expiresAt"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        time_diff = (expires_at - now).total_seconds()

        # Should be approximately 7 days (604800 seconds)
        # Allow 60 second tolerance for test execution time
        assert 604740 <= time_diff <= 604860
