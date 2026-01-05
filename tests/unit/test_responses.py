"""Tests for the responses module - GraphQL response builders."""

from typing import Any, Dict

from src.utils.responses import (
    AccountResponse,
    CampaignResponse,
    OrderResponse,
    ProfileResponse,
    build_account_response,
    build_campaign_response,
    build_list_response,
    build_order_response,
    build_profile_response,
)


class TestBuildAccountResponse:
    """Tests for build_account_response function."""

    def test_builds_complete_account_response(self) -> None:
        """Test building account response with all fields."""
        item: Dict[str, Any] = {
            "accountId": "ACCOUNT#user-123",
            "email": "test@example.com",
            "givenName": "John",
            "familyName": "Doe",
            "phoneNumber": "+15551234567",
            "city": "Denver",
            "state": "CO",
            "unitType": "Pack",
            "unitNumber": 123,
            "isAdmin": True,
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_account_response(item)

        assert result["accountId"] == "ACCOUNT#user-123"
        assert result["email"] == "test@example.com"
        assert result["givenName"] == "John"
        assert result["familyName"] == "Doe"
        assert result["phoneNumber"] == "+15551234567"
        assert result["city"] == "Denver"
        assert result["state"] == "CO"
        assert result["unitType"] == "Pack"
        assert result["unitNumber"] == 123
        assert result["isAdmin"] is True
        assert result["createdAt"] == "2025-01-01T00:00:00Z"
        assert result["updatedAt"] == "2025-01-02T00:00:00Z"

    def test_handles_missing_optional_fields(self) -> None:
        """Test that missing optional fields return None."""
        item: Dict[str, Any] = {
            "accountId": "ACCOUNT#user-456",
            "email": "minimal@example.com",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_account_response(item)

        assert result["accountId"] == "ACCOUNT#user-456"
        assert result["email"] == "minimal@example.com"
        assert result["givenName"] is None
        assert result["familyName"] is None
        assert result["phoneNumber"] is None
        assert result["city"] is None
        assert result["state"] is None
        assert result["unitType"] is None
        assert result["unitNumber"] is None
        assert result["isAdmin"] is False

    def test_handles_empty_item(self) -> None:
        """Test handling of empty item dictionary."""
        item: Dict[str, Any] = {}

        result = build_account_response(item)

        assert result["accountId"] == ""
        assert result["email"] == ""
        assert result["isAdmin"] is False
        assert result["createdAt"] == ""
        assert result["updatedAt"] == ""

    def test_converts_string_unit_number_to_int(self) -> None:
        """Test that string unitNumber is converted to int."""
        item: Dict[str, Any] = {
            "accountId": "ACCOUNT#user-789",
            "email": "test@example.com",
            "unitNumber": "456",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_account_response(item)

        assert result["unitNumber"] == 456

    def test_handles_invalid_unit_number(self) -> None:
        """Test that invalid unitNumber results in None."""
        item: Dict[str, Any] = {
            "accountId": "ACCOUNT#user-abc",
            "email": "test@example.com",
            "unitNumber": "not-a-number",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_account_response(item)

        assert result["unitNumber"] is None


class TestBuildProfileResponse:
    """Tests for build_profile_response function."""

    def test_builds_complete_profile_response(self) -> None:
        """Test building profile response with all fields."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "unitType": "Troop",
            "unitNumber": 456,
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item)

        assert result["profileId"] == "PROFILE#profile-123"
        assert result["ownerAccountId"] == "ACCOUNT#user-123"
        assert result["sellerName"] == "Scout Name"
        assert result["unitType"] == "Troop"
        assert result["unitNumber"] == 456
        assert result["createdAt"] == "2025-01-01T00:00:00Z"
        assert result["updatedAt"] == "2025-01-02T00:00:00Z"

    def test_includes_is_owner_when_provided(self) -> None:
        """Test that isOwner is included when explicitly provided."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item, is_owner=True)

        assert result["isOwner"] is True

    def test_includes_permissions_when_provided(self) -> None:
        """Test that permissions are included when explicitly provided."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item, permissions=["READ", "WRITE"])

        assert result["permissions"] == ["READ", "WRITE"]

    def test_excludes_is_owner_when_not_provided(self) -> None:
        """Test that isOwner is not in response when not provided."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item)

        assert "isOwner" not in result

    def test_excludes_permissions_when_not_provided(self) -> None:
        """Test that permissions is not in response when not provided."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item)

        assert "permissions" not in result

    def test_handles_string_unit_number(self) -> None:
        """Test that string unitNumber is converted to int."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "unitNumber": "789",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item)

        assert result["unitNumber"] == 789

    def test_handles_invalid_unit_number(self) -> None:
        """Test that invalid unitNumber results in None."""
        item: Dict[str, Any] = {
            "profileId": "PROFILE#profile-123",
            "ownerAccountId": "ACCOUNT#user-123",
            "sellerName": "Scout Name",
            "unitNumber": "invalid",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_profile_response(item)

        assert result["unitNumber"] is None


class TestBuildCampaignResponse:
    """Tests for build_campaign_response function."""

    def test_builds_complete_campaign_response(self) -> None:
        """Test building campaign response with all fields."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-123",
            "profileId": "PROFILE#profile-123",
            "campaignName": "Fall Sale",
            "campaignYear": 2025,
            "catalogId": "CATALOG#default",
            "startDate": "2025-09-01",
            "endDate": "2025-10-31",
            "goalAmount": 1000.50,
            "unitType": "Pack",
            "unitNumber": 123,
            "city": "Boulder",
            "state": "CO",
            "isShared": True,
            "sharedCampaignCode": "ABC123",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["campaignId"] == "CAMPAIGN#camp-123"
        assert result["profileId"] == "PROFILE#profile-123"
        assert result["campaignName"] == "Fall Sale"
        assert result["campaignYear"] == 2025
        assert result["catalogId"] == "CATALOG#default"
        assert result["startDate"] == "2025-09-01"
        assert result["endDate"] == "2025-10-31"
        assert result["goalAmount"] == 1000.50
        assert result["unitType"] == "Pack"
        assert result["unitNumber"] == 123
        assert result["city"] == "Boulder"
        assert result["state"] == "CO"
        assert result["isShared"] is True
        assert result["sharedCampaignCode"] == "ABC123"

    def test_handles_missing_optional_fields(self) -> None:
        """Test that missing optional fields return None."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-456",
            "profileId": "PROFILE#profile-456",
            "campaignName": "Minimal Campaign",
            "campaignYear": 2025,
            "catalogId": "CATALOG#default",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["startDate"] is None
        assert result["endDate"] is None
        assert result["goalAmount"] is None
        assert result["unitType"] is None
        assert result["unitNumber"] is None
        assert result["city"] is None
        assert result["state"] is None
        assert result["isShared"] is False
        assert result["sharedCampaignCode"] is None

    def test_converts_string_year_to_int(self) -> None:
        """Test that string campaignYear is converted to int."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-789",
            "profileId": "PROFILE#profile-789",
            "campaignName": "String Year Campaign",
            "campaignYear": "2026",
            "catalogId": "CATALOG#default",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["campaignYear"] == 2026

    def test_handles_invalid_campaign_year(self) -> None:
        """Test that invalid campaignYear defaults to 0."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-bad",
            "profileId": "PROFILE#profile-bad",
            "campaignName": "Bad Year Campaign",
            "campaignYear": "not-a-year",
            "catalogId": "CATALOG#default",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["campaignYear"] == 0

    def test_converts_string_goal_amount_to_float(self) -> None:
        """Test that string goalAmount is converted to float."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-goal",
            "profileId": "PROFILE#profile-goal",
            "campaignName": "Goal Campaign",
            "campaignYear": 2025,
            "catalogId": "CATALOG#default",
            "goalAmount": "500.75",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["goalAmount"] == 500.75

    def test_handles_invalid_goal_amount(self) -> None:
        """Test that invalid goalAmount results in None."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-bad-goal",
            "profileId": "PROFILE#profile-bad-goal",
            "campaignName": "Bad Goal Campaign",
            "campaignYear": 2025,
            "catalogId": "CATALOG#default",
            "goalAmount": "not-a-number",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["goalAmount"] is None

    def test_handles_invalid_unit_number(self) -> None:
        """Test that invalid unitNumber results in None."""
        item: Dict[str, Any] = {
            "campaignId": "CAMPAIGN#camp-bad-unit",
            "profileId": "PROFILE#profile-bad-unit",
            "campaignName": "Bad Unit Campaign",
            "campaignYear": 2025,
            "catalogId": "CATALOG#default",
            "unitNumber": "not-a-number",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-02T00:00:00Z",
        }

        result = build_campaign_response(item)

        assert result["unitNumber"] is None

    def test_handles_empty_item(self) -> None:
        """Test handling of empty item dictionary."""
        item: Dict[str, Any] = {}

        result = build_campaign_response(item)

        assert result["campaignId"] == ""
        assert result["profileId"] == ""
        assert result["campaignName"] == ""
        assert result["campaignYear"] == 0
        assert result["catalogId"] == ""
        assert result["isShared"] is False


class TestBuildOrderResponse:
    """Tests for build_order_response function."""

    def test_builds_complete_order_response(self) -> None:
        """Test building order response with all fields."""
        item: Dict[str, Any] = {
            "orderId": "ORDER#order-123",
            "campaignId": "CAMPAIGN#camp-123",
            "profileId": "PROFILE#profile-123",
            "customerName": "Jane Smith",
            "customerPhone": "+15559876543",
            "customerAddress": {
                "street": "123 Main St",
                "city": "Denver",
                "state": "CO",
                "zipCode": "80202",
            },
            "lineItems": [
                {"productId": "PROD1", "productName": "Popcorn", "quantity": 2, "unitPrice": 20.0},
                {"productId": "PROD2", "productName": "Chocolate", "quantity": 1, "unitPrice": 15.0},
            ],
            "totalAmount": 55.0,
            "paymentMethod": "CASH",
            "notes": "Deliver after 5pm",
            "orderDate": "2025-01-15",
            "createdAt": "2025-01-15T10:00:00Z",
            "updatedAt": "2025-01-15T10:00:00Z",
        }

        result = build_order_response(item)

        assert result["orderId"] == "ORDER#order-123"
        assert result["campaignId"] == "CAMPAIGN#camp-123"
        assert result["profileId"] == "PROFILE#profile-123"
        assert result["customerName"] == "Jane Smith"
        assert result["customerPhone"] == "+15559876543"
        assert result["customerAddress"]["street"] == "123 Main St"
        assert len(result["lineItems"]) == 2
        assert result["totalAmount"] == 55.0
        assert result["paymentMethod"] == "CASH"
        assert result["notes"] == "Deliver after 5pm"
        assert result["orderDate"] == "2025-01-15"

    def test_handles_missing_optional_fields(self) -> None:
        """Test that missing optional fields return None or defaults."""
        item: Dict[str, Any] = {
            "orderId": "ORDER#order-456",
            "campaignId": "CAMPAIGN#camp-456",
            "profileId": "PROFILE#profile-456",
            "customerName": "Minimal Order",
            "lineItems": [],
            "totalAmount": 0,
            "paymentMethod": "CASH",
            "orderDate": "2025-01-15",
            "createdAt": "2025-01-15T10:00:00Z",
            "updatedAt": "2025-01-15T10:00:00Z",
        }

        result = build_order_response(item)

        assert result["customerPhone"] is None
        assert result["customerAddress"] is None
        assert result["notes"] is None
        assert result["lineItems"] == []
        assert result["totalAmount"] == 0

    def test_converts_string_total_amount_to_float(self) -> None:
        """Test that string totalAmount is converted to float."""
        item: Dict[str, Any] = {
            "orderId": "ORDER#order-789",
            "campaignId": "CAMPAIGN#camp-789",
            "profileId": "PROFILE#profile-789",
            "customerName": "String Amount Order",
            "lineItems": [],
            "totalAmount": "99.99",
            "paymentMethod": "CHECK",
            "orderDate": "2025-01-15",
            "createdAt": "2025-01-15T10:00:00Z",
            "updatedAt": "2025-01-15T10:00:00Z",
        }

        result = build_order_response(item)

        assert result["totalAmount"] == 99.99

    def test_handles_invalid_total_amount(self) -> None:
        """Test that invalid totalAmount defaults to 0.0."""
        item: Dict[str, Any] = {
            "orderId": "ORDER#order-bad",
            "campaignId": "CAMPAIGN#camp-bad",
            "profileId": "PROFILE#profile-bad",
            "customerName": "Bad Amount Order",
            "lineItems": [],
            "totalAmount": "not-a-number",
            "paymentMethod": "CASH",
            "orderDate": "2025-01-15",
            "createdAt": "2025-01-15T10:00:00Z",
            "updatedAt": "2025-01-15T10:00:00Z",
        }

        result = build_order_response(item)

        assert result["totalAmount"] == 0.0

    def test_handles_missing_total_amount(self) -> None:
        """Test that missing totalAmount defaults to 0.0."""
        item: Dict[str, Any] = {
            "orderId": "ORDER#order-none",
            "campaignId": "CAMPAIGN#camp-none",
            "profileId": "PROFILE#profile-none",
            "customerName": "No Amount Order",
            "lineItems": [],
            "paymentMethod": "CASH",
            "orderDate": "2025-01-15",
            "createdAt": "2025-01-15T10:00:00Z",
            "updatedAt": "2025-01-15T10:00:00Z",
        }

        result = build_order_response(item)

        assert result["totalAmount"] == 0.0

    def test_handles_invalid_line_items(self) -> None:
        """Test that invalid lineItems defaults to empty list."""
        item: Dict[str, Any] = {
            "orderId": "ORDER#order-bad-items",
            "campaignId": "CAMPAIGN#camp-bad-items",
            "profileId": "PROFILE#profile-bad-items",
            "customerName": "Bad Items Order",
            "lineItems": "not-a-list",
            "totalAmount": 0,
            "paymentMethod": "CASH",
            "orderDate": "2025-01-15",
            "createdAt": "2025-01-15T10:00:00Z",
            "updatedAt": "2025-01-15T10:00:00Z",
        }

        result = build_order_response(item)

        assert result["lineItems"] == []

    def test_handles_empty_item(self) -> None:
        """Test handling of empty item dictionary."""
        item: Dict[str, Any] = {}

        result = build_order_response(item)

        assert result["orderId"] == ""
        assert result["campaignId"] == ""
        assert result["profileId"] == ""
        assert result["customerName"] == ""
        assert result["totalAmount"] == 0.0
        assert result["paymentMethod"] == ""
        assert result["orderDate"] == ""
        assert result["lineItems"] == []


class TestBuildListResponse:
    """Tests for build_list_response function."""

    def test_builds_list_of_accounts(self) -> None:
        """Test building a list of account responses."""
        items = [
            {
                "accountId": "ACCOUNT#user-1",
                "email": "user1@example.com",
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-01T00:00:00Z",
            },
            {
                "accountId": "ACCOUNT#user-2",
                "email": "user2@example.com",
                "createdAt": "2025-01-02T00:00:00Z",
                "updatedAt": "2025-01-02T00:00:00Z",
            },
        ]

        result = build_list_response(items, build_account_response)

        assert len(result) == 2
        assert result[0]["accountId"] == "ACCOUNT#user-1"
        assert result[1]["accountId"] == "ACCOUNT#user-2"

    def test_builds_list_of_campaigns(self) -> None:
        """Test building a list of campaign responses."""
        items = [
            {
                "campaignId": "CAMPAIGN#camp-1",
                "profileId": "PROFILE#profile-1",
                "campaignName": "Campaign 1",
                "campaignYear": 2025,
                "catalogId": "CATALOG#default",
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-01T00:00:00Z",
            },
            {
                "campaignId": "CAMPAIGN#camp-2",
                "profileId": "PROFILE#profile-2",
                "campaignName": "Campaign 2",
                "campaignYear": 2026,
                "catalogId": "CATALOG#default",
                "createdAt": "2025-01-02T00:00:00Z",
                "updatedAt": "2025-01-02T00:00:00Z",
            },
        ]

        result = build_list_response(items, build_campaign_response)

        assert len(result) == 2
        assert result[0]["campaignName"] == "Campaign 1"
        assert result[1]["campaignName"] == "Campaign 2"

    def test_handles_empty_list(self) -> None:
        """Test that empty list returns empty list."""
        items: list[Dict[str, Any]] = []

        result = build_list_response(items, build_account_response)

        assert result == []

    def test_builds_list_of_orders(self) -> None:
        """Test building a list of order responses."""
        items = [
            {
                "orderId": "ORDER#order-1",
                "campaignId": "CAMPAIGN#camp-1",
                "profileId": "PROFILE#profile-1",
                "customerName": "Customer 1",
                "lineItems": [],
                "totalAmount": 10.0,
                "paymentMethod": "CASH",
                "orderDate": "2025-01-15",
                "createdAt": "2025-01-15T10:00:00Z",
                "updatedAt": "2025-01-15T10:00:00Z",
            },
        ]

        result = build_list_response(items, build_order_response)

        assert len(result) == 1
        assert result[0]["customerName"] == "Customer 1"


class TestResponseTypes:
    """Tests to ensure TypedDict types work correctly."""

    def test_account_response_type_is_dict(self) -> None:
        """Verify AccountResponse is a valid dict subtype."""
        response: AccountResponse = {
            "accountId": "test",
            "email": "test@example.com",
            "isAdmin": False,
            "createdAt": "",
            "updatedAt": "",
        }
        assert isinstance(response, dict)

    def test_profile_response_type_is_dict(self) -> None:
        """Verify ProfileResponse is a valid dict subtype."""
        response: ProfileResponse = {
            "profileId": "test",
            "ownerAccountId": "test",
            "sellerName": "test",
            "createdAt": "",
            "updatedAt": "",
        }
        assert isinstance(response, dict)

    def test_campaign_response_type_is_dict(self) -> None:
        """Verify CampaignResponse is a valid dict subtype."""
        response: CampaignResponse = {
            "campaignId": "test",
            "profileId": "test",
            "campaignName": "test",
            "campaignYear": 2025,
            "catalogId": "test",
            "isShared": False,
            "createdAt": "",
            "updatedAt": "",
        }
        assert isinstance(response, dict)

    def test_order_response_type_is_dict(self) -> None:
        """Verify OrderResponse is a valid dict subtype."""
        response: OrderResponse = {
            "orderId": "test",
            "campaignId": "test",
            "profileId": "test",
            "customerName": "test",
            "lineItems": [],
            "totalAmount": 0.0,
            "paymentMethod": "CASH",
            "orderDate": "",
            "createdAt": "",
            "updatedAt": "",
        }
        assert isinstance(response, dict)
