"""Tests for the fixtures module - test data builders."""

from tests.unit.fixtures import (
    MockLambdaContext,
    make_account,
    make_account_id,
    make_appsync_event,
    make_campaign,
    make_campaign_id,
    make_catalog,
    make_catalog_id,
    make_invite,
    make_invite_code,
    make_line_item,
    make_order,
    make_order_id,
    make_product,
    make_profile,
    make_profile_id,
    make_share,
    now_iso,
)


class TestIdGenerators:
    """Tests for ID generator functions."""

    def test_make_account_id_generates_unique_ids(self) -> None:
        """Each call should generate a unique ID."""
        id1 = make_account_id()
        id2 = make_account_id()
        assert id1 != id2
        assert id1.startswith("ACCOUNT#")
        assert id2.startswith("ACCOUNT#")

    def test_make_account_id_with_suffix(self) -> None:
        """Should use provided suffix."""
        result = make_account_id("test-123")
        assert result == "ACCOUNT#test-123"

    def test_make_profile_id_generates_unique_ids(self) -> None:
        """Each call should generate a unique ID."""
        id1 = make_profile_id()
        id2 = make_profile_id()
        assert id1 != id2
        assert id1.startswith("PROFILE#")
        assert id2.startswith("PROFILE#")

    def test_make_profile_id_with_suffix(self) -> None:
        """Should use provided suffix."""
        result = make_profile_id("profile-abc")
        assert result == "PROFILE#profile-abc"

    def test_make_campaign_id_generates_unique_ids(self) -> None:
        """Each call should generate a unique ID."""
        id1 = make_campaign_id()
        id2 = make_campaign_id()
        assert id1 != id2
        assert id1.startswith("CAMPAIGN#")
        assert id2.startswith("CAMPAIGN#")

    def test_make_campaign_id_with_suffix(self) -> None:
        """Should use provided suffix."""
        result = make_campaign_id("camp-xyz")
        assert result == "CAMPAIGN#camp-xyz"

    def test_make_order_id_generates_unique_ids(self) -> None:
        """Each call should generate a unique ID."""
        id1 = make_order_id()
        id2 = make_order_id()
        assert id1 != id2
        assert id1.startswith("ORDER#")
        assert id2.startswith("ORDER#")

    def test_make_order_id_with_suffix(self) -> None:
        """Should use provided suffix."""
        result = make_order_id("order-123")
        assert result == "ORDER#order-123"

    def test_make_catalog_id_generates_unique_ids(self) -> None:
        """Each call should generate a unique ID."""
        id1 = make_catalog_id()
        id2 = make_catalog_id()
        assert id1 != id2
        assert id1.startswith("CATALOG#")
        assert id2.startswith("CATALOG#")

    def test_make_catalog_id_with_suffix(self) -> None:
        """Should use provided suffix."""
        result = make_catalog_id("cat-default")
        assert result == "CATALOG#cat-default"

    def test_make_invite_code_generates_uppercase(self) -> None:
        """Invite codes should be uppercase."""
        code = make_invite_code()
        assert code == code.upper()
        assert len(code) == 8

    def test_make_invite_code_generates_unique_codes(self) -> None:
        """Each call should generate a unique code."""
        code1 = make_invite_code()
        code2 = make_invite_code()
        assert code1 != code2


class TestNowIso:
    """Tests for now_iso function."""

    def test_returns_iso_format_string(self) -> None:
        """Should return a valid ISO 8601 timestamp."""
        result = now_iso()
        # Should contain date and time components
        assert "T" in result
        # Should end with timezone info
        assert "+" in result or "Z" in result

    def test_returns_different_times(self) -> None:
        """Consecutive calls may return same or different times."""
        # Just verify it returns valid strings
        result1 = now_iso()
        result2 = now_iso()
        assert isinstance(result1, str)
        assert isinstance(result2, str)


class TestMakeAccount:
    """Tests for make_account function."""

    def test_creates_account_with_defaults(self) -> None:
        """Should create account with default values."""
        account = make_account()

        assert "accountId" in account
        assert account["accountId"].startswith("ACCOUNT#")
        assert "email" in account
        assert "@example.com" in account["email"]
        assert account["givenName"] == "Test"
        assert account["familyName"] == "User"
        assert account["isAdmin"] is False
        assert "createdAt" in account
        assert "updatedAt" in account

    def test_creates_account_with_custom_values(self) -> None:
        """Should use provided values."""
        account = make_account(
            account_id="ACCOUNT#custom-123",
            email="custom@test.com",
            given_name="John",
            family_name="Doe",
        )

        assert account["accountId"] == "ACCOUNT#custom-123"
        assert account["email"] == "custom@test.com"
        assert account["givenName"] == "John"
        assert account["familyName"] == "Doe"

    def test_accepts_additional_kwargs(self) -> None:
        """Should include additional keyword arguments."""
        account = make_account(phoneNumber="+15551234567", isAdmin=True)

        assert account["phoneNumber"] == "+15551234567"
        assert account["isAdmin"] is True


class TestMakeProfile:
    """Tests for make_profile function."""

    def test_creates_profile_with_defaults(self) -> None:
        """Should create profile with default values."""
        profile = make_profile()

        assert "profileId" in profile
        assert profile["profileId"].startswith("PROFILE#")
        assert "ownerAccountId" in profile
        assert profile["ownerAccountId"].startswith("ACCOUNT#")
        assert profile["sellerName"] == "Test Scout"
        assert "createdAt" in profile
        assert "updatedAt" in profile

    def test_creates_profile_with_custom_values(self) -> None:
        """Should use provided values."""
        profile = make_profile(
            profile_id="PROFILE#custom-456",
            owner_account_id="ACCOUNT#owner-789",
            seller_name="Custom Scout",
        )

        assert profile["profileId"] == "PROFILE#custom-456"
        assert profile["ownerAccountId"] == "ACCOUNT#owner-789"
        assert profile["sellerName"] == "Custom Scout"

    def test_accepts_additional_kwargs(self) -> None:
        """Should include additional keyword arguments."""
        profile = make_profile(unitType="Pack", unitNumber=123)

        assert profile["unitType"] == "Pack"
        assert profile["unitNumber"] == 123


class TestMakeCampaign:
    """Tests for make_campaign function."""

    def test_creates_campaign_with_defaults(self) -> None:
        """Should create campaign with default values."""
        campaign = make_campaign()

        assert "campaignId" in campaign
        assert campaign["campaignId"].startswith("CAMPAIGN#")
        assert "profileId" in campaign
        assert campaign["profileId"].startswith("PROFILE#")
        assert campaign["campaignName"] == "Fall Campaign"
        assert campaign["campaignYear"] == 2025
        assert campaign["catalogId"] == "CATALOG#default"
        assert "createdAt" in campaign
        assert "updatedAt" in campaign

    def test_creates_campaign_with_custom_values(self) -> None:
        """Should use provided values."""
        campaign = make_campaign(
            campaign_id="CAMPAIGN#camp-custom",
            profile_id="PROFILE#profile-custom",
            campaign_name="Spring Sale",
            campaign_year=2026,
            catalog_id="CATALOG#special",
        )

        assert campaign["campaignId"] == "CAMPAIGN#camp-custom"
        assert campaign["profileId"] == "PROFILE#profile-custom"
        assert campaign["campaignName"] == "Spring Sale"
        assert campaign["campaignYear"] == 2026
        assert campaign["catalogId"] == "CATALOG#special"

    def test_accepts_additional_kwargs(self) -> None:
        """Should include additional keyword arguments."""
        campaign = make_campaign(
            startDate="2025-09-01",
            endDate="2025-10-31",
            isShared=True,
        )

        assert campaign["startDate"] == "2025-09-01"
        assert campaign["endDate"] == "2025-10-31"
        assert campaign["isShared"] is True


class TestMakeOrder:
    """Tests for make_order function."""

    def test_creates_order_with_defaults(self) -> None:
        """Should create order with default values."""
        order = make_order()

        assert "orderId" in order
        assert order["orderId"].startswith("ORDER#")
        assert "campaignId" in order
        assert order["campaignId"].startswith("CAMPAIGN#")
        assert "profileId" in order
        assert order["profileId"].startswith("PROFILE#")
        assert order["customerName"] == "Test Customer"
        assert order["customerPhone"] == "+15551234567"
        assert order["paymentMethod"] == "CASH"
        assert order["lineItems"] == []
        assert order["totalAmount"] == 0.0
        assert "orderDate" in order
        assert "createdAt" in order
        assert "updatedAt" in order

    def test_creates_order_with_custom_values(self) -> None:
        """Should use provided values."""
        line_items = [make_line_item()]
        order = make_order(
            order_id="ORDER#order-custom",
            customer_name="Jane Smith",
            line_items=line_items,
            total_amount=25.50,
            payment_method="CHECK",
        )

        assert order["orderId"] == "ORDER#order-custom"
        assert order["customerName"] == "Jane Smith"
        assert order["lineItems"] == line_items
        assert order["totalAmount"] == 25.50
        assert order["paymentMethod"] == "CHECK"

    def test_accepts_additional_kwargs(self) -> None:
        """Should include additional keyword arguments."""
        order = make_order(notes="Deliver after 5pm")

        assert order["notes"] == "Deliver after 5pm"


class TestMakeLineItem:
    """Tests for make_line_item function."""

    def test_creates_line_item_with_defaults(self) -> None:
        """Should create line item with default values."""
        item = make_line_item()

        assert item["productId"] == "PRODUCT#001"
        assert item["productName"] == "Test Product"
        assert item["quantity"] == 1
        assert item["unitPrice"] == 10.0
        assert item["totalPrice"] == 10.0

    def test_creates_line_item_with_custom_values(self) -> None:
        """Should use provided values and calculate total."""
        item = make_line_item(
            product_id="PRODUCT#popcorn",
            product_name="Popcorn Tin",
            quantity=3,
            unit_price=25.0,
        )

        assert item["productId"] == "PRODUCT#popcorn"
        assert item["productName"] == "Popcorn Tin"
        assert item["quantity"] == 3
        assert item["unitPrice"] == 25.0
        assert item["totalPrice"] == 75.0  # 3 * 25


class TestMakeShare:
    """Tests for make_share function."""

    def test_creates_share_with_defaults(self) -> None:
        """Should create share with default values."""
        share = make_share()

        assert "profileId" in share
        assert share["profileId"].startswith("PROFILE#")
        assert "targetAccountId" in share
        assert share["targetAccountId"].startswith("ACCOUNT#")
        assert share["permissions"] == ["READ"]
        assert "createdAt" in share
        assert "updatedAt" in share

    def test_creates_share_with_custom_values(self) -> None:
        """Should use provided values."""
        share = make_share(
            profile_id="PROFILE#shared-profile",
            target_account_id="ACCOUNT#recipient",
            permissions=["READ", "WRITE"],
        )

        assert share["profileId"] == "PROFILE#shared-profile"
        assert share["targetAccountId"] == "ACCOUNT#recipient"
        assert share["permissions"] == ["READ", "WRITE"]


class TestMakeInvite:
    """Tests for make_invite function."""

    def test_creates_invite_with_defaults(self) -> None:
        """Should create invite with default values."""
        invite = make_invite()

        assert "inviteCode" in invite
        assert len(invite["inviteCode"]) == 8
        assert invite["inviteCode"] == invite["inviteCode"].upper()
        assert "profileId" in invite
        assert invite["profileId"].startswith("PROFILE#")
        assert invite["permissions"] == ["READ"]
        assert "expiresAt" in invite
        assert "createdAt" in invite

    def test_creates_invite_with_custom_values(self) -> None:
        """Should use provided values."""
        invite = make_invite(
            invite_code="TESTCODE",
            profile_id="PROFILE#invite-profile",
            permissions=["READ", "WRITE"],
            expires_at="2025-12-31T23:59:59Z",
        )

        assert invite["inviteCode"] == "TESTCODE"
        assert invite["profileId"] == "PROFILE#invite-profile"
        assert invite["permissions"] == ["READ", "WRITE"]
        assert invite["expiresAt"] == "2025-12-31T23:59:59Z"


class TestMakeCatalog:
    """Tests for make_catalog function."""

    def test_creates_catalog_with_defaults(self) -> None:
        """Should create catalog with default values."""
        catalog = make_catalog()

        assert "catalogId" in catalog
        assert catalog["catalogId"].startswith("CATALOG#")
        assert catalog["catalogName"] == "Test Catalog"
        assert "ownerAccountId" in catalog
        assert catalog["ownerAccountId"].startswith("ACCOUNT#")
        assert catalog["isPublic"] is False
        assert catalog["products"] == []
        assert "createdAt" in catalog
        assert "updatedAt" in catalog

    def test_creates_catalog_with_custom_values(self) -> None:
        """Should use provided values."""
        products = [make_product()]
        catalog = make_catalog(
            catalog_id="CATALOG#custom",
            catalog_name="Premium Catalog",
            is_public=True,
            products=products,
        )

        assert catalog["catalogId"] == "CATALOG#custom"
        assert catalog["catalogName"] == "Premium Catalog"
        assert catalog["isPublic"] is True
        assert catalog["products"] == products


class TestMakeProduct:
    """Tests for make_product function."""

    def test_creates_product_with_defaults(self) -> None:
        """Should create product with default values."""
        product = make_product()

        assert "productId" in product
        assert product["productId"].startswith("PRODUCT#")
        assert product["productName"] == "Popcorn"
        assert product["price"] == 20.0
        assert product["category"] == "Snacks"
        assert "sku" in product
        assert len(product["sku"]) == 6

    def test_creates_product_with_custom_values(self) -> None:
        """Should use provided values."""
        product = make_product(
            product_id="PRODUCT#custom",
            product_name="Chocolate",
            price=15.50,
            category="Candy",
            sku="CHOC01",
        )

        assert product["productId"] == "PRODUCT#custom"
        assert product["productName"] == "Chocolate"
        assert product["price"] == 15.50
        assert product["category"] == "Candy"
        assert product["sku"] == "CHOC01"


class TestMakeAppsyncEvent:
    """Tests for make_appsync_event function."""

    def test_creates_event_with_defaults(self) -> None:
        """Should create AppSync event with default values."""
        event = make_appsync_event()

        assert "arguments" in event
        assert event["arguments"] == {}
        assert "identity" in event
        assert "sub" in event["identity"]
        assert "username" in event["identity"]
        assert "requestContext" in event
        assert "requestId" in event["requestContext"]
        assert "info" in event
        assert event["info"]["fieldName"] == "testField"
        assert event["info"]["parentTypeName"] == "Query"

    def test_creates_event_with_custom_values(self) -> None:
        """Should use provided values."""
        event = make_appsync_event(
            account_id="user-123",
            arguments={"profileId": "PROFILE#abc"},
            field_name="getProfile",
            parent_type="Query",
        )

        assert event["identity"]["sub"] == "user-123"
        assert event["arguments"]["profileId"] == "PROFILE#abc"
        assert event["info"]["fieldName"] == "getProfile"
        assert event["info"]["parentTypeName"] == "Query"

    def test_accepts_additional_kwargs(self) -> None:
        """Should include additional keyword arguments."""
        event = make_appsync_event(source={"profileId": "PROFILE#source"})

        assert event["source"]["profileId"] == "PROFILE#source"


class TestMockLambdaContext:
    """Tests for MockLambdaContext class."""

    def test_creates_context_with_defaults(self) -> None:
        """Should create context with default values."""
        ctx = MockLambdaContext()

        assert ctx.function_name == "test-function"
        assert ctx.memory_limit_in_mb == 128
        assert ctx.aws_request_id.startswith("test-")
        assert "test-function" in ctx.invoked_function_arn

    def test_creates_context_with_custom_values(self) -> None:
        """Should use provided values."""
        ctx = MockLambdaContext(
            function_name="custom-function",
            memory_limit_in_mb=256,
            aws_request_id="custom-request-id",
        )

        assert ctx.function_name == "custom-function"
        assert ctx.memory_limit_in_mb == 256
        assert ctx.aws_request_id == "custom-request-id"
        assert "custom-function" in ctx.invoked_function_arn

    def test_get_remaining_time_in_millis(self) -> None:
        """Should return mock remaining time."""
        ctx = MockLambdaContext()
        remaining = ctx.get_remaining_time_in_millis()

        assert remaining == 30000
