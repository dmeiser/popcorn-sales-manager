"""Tests for src/utils/dynamodb.py - centralized table access utilities."""

import os
from typing import Generator
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

from src.utils.dynamodb import (
    TableAccessor,
    _get_dynamodb,
    clear_all_overrides,
    override_table,
    reset_singleton,
    tables,
)


@pytest.fixture(autouse=True)
def reset_between_tests() -> Generator[None, None, None]:
    """Reset singleton and overrides between tests."""
    # Store original env vars
    table_env_vars = [
        "ACCOUNTS_TABLE_NAME",
        "PROFILES_TABLE_NAME",
        "CAMPAIGNS_TABLE_NAME",
        "ORDERS_TABLE_NAME",
        "SHARES_TABLE_NAME",
        "CATALOGS_TABLE_NAME",
        "INVITES_TABLE_NAME",
        "SHARED_CAMPAIGNS_TABLE_NAME",
    ]
    original_values = {k: os.environ.get(k) for k in table_env_vars}

    # Clear table name env vars to test defaults
    for var in table_env_vars:
        if var in os.environ:
            del os.environ[var]

    clear_all_overrides()
    reset_singleton()
    yield
    clear_all_overrides()
    reset_singleton()

    # Restore original env vars
    for k, v in original_values.items():
        if v is not None:
            os.environ[k] = v
        elif k in os.environ:
            del os.environ[k]


@pytest.fixture
def aws_credentials() -> None:
    """Set fake AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


class TestGetDynamoDB:
    """Tests for _get_dynamodb function."""

    def test_returns_dynamodb_resource(self, aws_credentials: None) -> None:
        """Test that _get_dynamodb returns a DynamoDB resource."""
        with mock_aws():
            result = _get_dynamodb()
            assert result is not None
            # Verify it's a DynamoDB resource by checking for a known attribute
            assert hasattr(result, "Table")

    def test_uses_endpoint_override(self) -> None:
        """Test that endpoint URL is used when set."""
        with patch.dict(os.environ, {"DYNAMODB_ENDPOINT": "http://localhost:8000"}):
            with patch("boto3.resource") as mock_resource:
                mock_resource.return_value = MagicMock()
                _get_dynamodb()
                mock_resource.assert_called_once_with("dynamodb", endpoint_url="http://localhost:8000")


class TestTableAccessor:
    """Tests for TableAccessor class."""

    def test_is_singleton(self) -> None:
        """Test that TableAccessor is a singleton."""
        accessor1 = TableAccessor()
        accessor2 = TableAccessor()
        assert accessor1 is accessor2

    def test_reset_singleton_creates_new_instance(self) -> None:
        """Test that reset_singleton allows creation of new instance."""
        accessor1 = TableAccessor()
        reset_singleton()
        accessor2 = TableAccessor()
        assert accessor1 is not accessor2


class TestTableProperties:
    """Tests for individual table properties."""

    def test_accounts_table_default_name(self, aws_credentials: None) -> None:
        """Test accounts table uses default name."""
        with mock_aws():
            # Create the table for moto
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-accounts-ue1-dev",
                KeySchema=[{"AttributeName": "accountId", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "accountId", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.accounts
            assert table.name == "kernelworx-accounts-ue1-dev"

    def test_accounts_table_custom_name(self, aws_credentials: None) -> None:
        """Test accounts table uses custom name from env."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="custom-accounts",
                KeySchema=[{"AttributeName": "accountId", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "accountId", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            with patch.dict(os.environ, {"ACCOUNTS_TABLE_NAME": "custom-accounts"}):
                reset_singleton()
                table = tables.accounts
                assert table.name == "custom-accounts"

    def test_profiles_table(self, aws_credentials: None) -> None:
        """Test profiles table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-profiles-v2-ue1-dev",
                KeySchema=[
                    {"AttributeName": "ownerAccountId", "KeyType": "HASH"},
                    {"AttributeName": "profileId", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "ownerAccountId", "AttributeType": "S"},
                    {"AttributeName": "profileId", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.profiles
            assert table.name == "kernelworx-profiles-v2-ue1-dev"

    def test_campaigns_table(self, aws_credentials: None) -> None:
        """Test campaigns table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-campaigns-v2-ue1-dev",
                KeySchema=[
                    {"AttributeName": "profileId", "KeyType": "HASH"},
                    {"AttributeName": "campaignId", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "profileId", "AttributeType": "S"},
                    {"AttributeName": "campaignId", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.campaigns
            assert table.name == "kernelworx-campaigns-v2-ue1-dev"

    def test_orders_table(self, aws_credentials: None) -> None:
        """Test orders table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-orders-v2-ue1-dev",
                KeySchema=[
                    {"AttributeName": "campaignId", "KeyType": "HASH"},
                    {"AttributeName": "orderId", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "campaignId", "AttributeType": "S"},
                    {"AttributeName": "orderId", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.orders
            assert table.name == "kernelworx-orders-v2-ue1-dev"

    def test_shares_table(self, aws_credentials: None) -> None:
        """Test shares table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-shares-ue1-dev",
                KeySchema=[
                    {"AttributeName": "profileId", "KeyType": "HASH"},
                    {"AttributeName": "targetAccountId", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "profileId", "AttributeType": "S"},
                    {"AttributeName": "targetAccountId", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.shares
            assert table.name == "kernelworx-shares-ue1-dev"

    def test_catalogs_table(self, aws_credentials: None) -> None:
        """Test catalogs table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-catalogs-ue1-dev",
                KeySchema=[{"AttributeName": "catalogId", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "catalogId", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.catalogs
            assert table.name == "kernelworx-catalogs-ue1-dev"

    def test_invites_table(self, aws_credentials: None) -> None:
        """Test invites table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-invites-ue1-dev",
                KeySchema=[{"AttributeName": "inviteCode", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "inviteCode", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.invites
            assert table.name == "kernelworx-invites-ue1-dev"

    def test_shared_campaigns_table(self, aws_credentials: None) -> None:
        """Test shared_campaigns table property."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-shared-campaigns-ue1-dev",
                KeySchema=[
                    {"AttributeName": "sharedCampaignCode", "KeyType": "HASH"},
                    {"AttributeName": "SK", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "sharedCampaignCode", "AttributeType": "S"},
                    {"AttributeName": "SK", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table = tables.shared_campaigns
            assert table.name == "kernelworx-shared-campaigns-ue1-dev"


class TestTableOverrides:
    """Tests for table override functionality."""

    def test_override_table_uses_override(self) -> None:
        """Test that overriding a table returns the override."""
        mock_table = MagicMock()
        mock_table.name = "override-accounts"

        override_table("accounts", mock_table)
        result = tables.accounts
        assert result is mock_table
        assert result.name == "override-accounts"

    def test_override_table_with_none_clears_override(self, aws_credentials: None) -> None:
        """Test that setting override to None clears it."""
        with mock_aws():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            dynamodb.create_table(
                TableName="kernelworx-accounts-ue1-dev",
                KeySchema=[{"AttributeName": "accountId", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "accountId", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )

            mock_table = MagicMock()
            mock_table.name = "override"

            override_table("accounts", mock_table)
            assert tables.accounts.name == "override"

            override_table("accounts", None)
            # Now it should use the real table
            assert tables.accounts.name == "kernelworx-accounts-ue1-dev"

    def test_clear_all_overrides(self) -> None:
        """Test that clear_all_overrides clears all overrides."""
        mock_table1 = MagicMock()
        mock_table2 = MagicMock()

        override_table("accounts", mock_table1)
        override_table("profiles", mock_table2)

        # Verify overrides are in place
        assert tables.accounts is mock_table1
        assert tables.profiles is mock_table2

        # Clear all
        clear_all_overrides()

        # Verify we can still access the properties (they'll hit real boto3 now)
        # Just verify the override is cleared by checking the dict is empty
        from src.utils.dynamodb import _table_overrides

        assert len(_table_overrides) == 0

    def test_multiple_table_overrides(self) -> None:
        """Test that multiple tables can be overridden independently."""
        mock_accounts = MagicMock()
        mock_accounts.name = "mock-accounts"
        mock_profiles = MagicMock()
        mock_profiles.name = "mock-profiles"
        mock_campaigns = MagicMock()
        mock_campaigns.name = "mock-campaigns"

        override_table("accounts", mock_accounts)
        override_table("profiles", mock_profiles)
        override_table("campaigns", mock_campaigns)

        assert tables.accounts.name == "mock-accounts"
        assert tables.profiles.name == "mock-profiles"
        assert tables.campaigns.name == "mock-campaigns"

    def test_override_orders_shares_catalogs_invites(self) -> None:
        """Test overriding orders, shares, catalogs, and invites tables."""
        mock_orders = MagicMock()
        mock_shares = MagicMock()
        mock_catalogs = MagicMock()
        mock_invites = MagicMock()
        mock_shared_campaigns = MagicMock()

        mock_orders.name = "mock-orders"
        mock_shares.name = "mock-shares"
        mock_catalogs.name = "mock-catalogs"
        mock_invites.name = "mock-invites"
        mock_shared_campaigns.name = "mock-shared-campaigns"

        override_table("orders", mock_orders)
        override_table("shares", mock_shares)
        override_table("catalogs", mock_catalogs)
        override_table("invites", mock_invites)
        override_table("shared_campaigns", mock_shared_campaigns)

        assert tables.orders.name == "mock-orders"
        assert tables.shares.name == "mock-shares"
        assert tables.catalogs.name == "mock-catalogs"
        assert tables.invites.name == "mock-invites"
        assert tables.shared_campaigns.name == "mock-shared-campaigns"
