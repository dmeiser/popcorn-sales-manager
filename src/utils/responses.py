"""
GraphQL response builders for Lambda resolvers.

Provides consistent response structures and entity builders for
AppSync GraphQL resolvers.
"""

from typing import Any, Dict, List, Optional, TypedDict, cast


class AccountResponse(TypedDict, total=False):
    """GraphQL Account response type."""

    accountId: str
    email: str
    givenName: Optional[str]
    familyName: Optional[str]
    phoneNumber: Optional[str]
    city: Optional[str]
    state: Optional[str]
    unitType: Optional[str]
    unitNumber: Optional[int]
    isAdmin: bool
    createdAt: str
    updatedAt: str


class ProfileResponse(TypedDict, total=False):
    """GraphQL SellerProfile response type."""

    profileId: str
    ownerAccountId: str
    sellerName: str
    unitType: Optional[str]
    unitNumber: Optional[int]
    isOwner: bool
    permissions: List[str]
    createdAt: str
    updatedAt: str


class CampaignResponse(TypedDict, total=False):
    """GraphQL Campaign response type."""

    campaignId: str
    profileId: str
    campaignName: str
    campaignYear: int
    catalogId: str
    startDate: Optional[str]
    endDate: Optional[str]
    goalAmount: Optional[float]
    unitType: Optional[str]
    unitNumber: Optional[int]
    city: Optional[str]
    state: Optional[str]
    isShared: bool
    sharedCampaignCode: Optional[str]
    createdAt: str
    updatedAt: str


class OrderResponse(TypedDict, total=False):
    """GraphQL Order response type."""

    orderId: str
    campaignId: str
    profileId: str
    customerName: str
    customerPhone: Optional[str]
    customerAddress: Optional[Dict[str, str]]
    lineItems: List[Dict[str, Any]]
    totalAmount: float
    paymentMethod: str
    notes: Optional[str]
    orderDate: str
    createdAt: str
    updatedAt: str


def build_account_response(item: Dict[str, Any]) -> AccountResponse:
    """
    Build an Account response from a DynamoDB item.

    Args:
        item: DynamoDB item dictionary

    Returns:
        AccountResponse with normalized field names
    """
    unit_number = item.get("unitNumber")
    if unit_number is not None:
        try:
            unit_number = int(unit_number)
        except (ValueError, TypeError):
            unit_number = None

    return AccountResponse(
        accountId=cast(str, item.get("accountId", "")),
        email=cast(str, item.get("email", "")),
        givenName=item.get("givenName"),
        familyName=item.get("familyName"),
        phoneNumber=item.get("phoneNumber"),
        city=item.get("city"),
        state=item.get("state"),
        unitType=item.get("unitType"),
        unitNumber=unit_number,
        isAdmin=bool(item.get("isAdmin", False)),
        createdAt=cast(str, item.get("createdAt", "")),
        updatedAt=cast(str, item.get("updatedAt", "")),
    )


def build_profile_response(
    item: Dict[str, Any],
    *,
    is_owner: Optional[bool] = None,
    permissions: Optional[List[str]] = None,
) -> ProfileResponse:
    """
    Build a SellerProfile response from a DynamoDB item.

    Args:
        item: DynamoDB item dictionary
        is_owner: Whether the caller owns this profile (optional)
        permissions: List of permissions the caller has (optional)

    Returns:
        ProfileResponse with normalized field names
    """
    unit_number = item.get("unitNumber")
    if unit_number is not None:
        try:
            unit_number = int(unit_number)
        except (ValueError, TypeError):
            unit_number = None

    response = ProfileResponse(
        profileId=cast(str, item.get("profileId", "")),
        ownerAccountId=cast(str, item.get("ownerAccountId", "")),
        sellerName=cast(str, item.get("sellerName", "")),
        unitType=item.get("unitType"),
        unitNumber=unit_number,
        createdAt=cast(str, item.get("createdAt", "")),
        updatedAt=cast(str, item.get("updatedAt", "")),
    )

    if is_owner is not None:
        response["isOwner"] = is_owner
    if permissions is not None:
        response["permissions"] = permissions

    return response


def build_campaign_response(item: Dict[str, Any]) -> CampaignResponse:
    """
    Build a Campaign response from a DynamoDB item.

    Args:
        item: DynamoDB item dictionary

    Returns:
        CampaignResponse with normalized field names
    """
    # Parse numeric fields
    campaign_year = item.get("campaignYear")
    if campaign_year is not None:
        try:
            campaign_year = int(campaign_year)
        except (ValueError, TypeError):
            campaign_year = None

    unit_number = item.get("unitNumber")
    if unit_number is not None:
        try:
            unit_number = int(unit_number)
        except (ValueError, TypeError):
            unit_number = None

    goal_amount = item.get("goalAmount")
    if goal_amount is not None:
        try:
            goal_amount = float(goal_amount)
        except (ValueError, TypeError):
            goal_amount = None

    return CampaignResponse(
        campaignId=cast(str, item.get("campaignId", "")),
        profileId=cast(str, item.get("profileId", "")),
        campaignName=cast(str, item.get("campaignName", "")),
        campaignYear=campaign_year if campaign_year is not None else 0,
        catalogId=cast(str, item.get("catalogId", "")),
        startDate=item.get("startDate"),
        endDate=item.get("endDate"),
        goalAmount=goal_amount,
        unitType=item.get("unitType"),
        unitNumber=unit_number,
        city=item.get("city"),
        state=item.get("state"),
        isShared=bool(item.get("isShared", False)),
        sharedCampaignCode=item.get("sharedCampaignCode"),
        createdAt=cast(str, item.get("createdAt", "")),
        updatedAt=cast(str, item.get("updatedAt", "")),
    )


def build_order_response(item: Dict[str, Any]) -> OrderResponse:
    """
    Build an Order response from a DynamoDB item.

    Args:
        item: DynamoDB item dictionary

    Returns:
        OrderResponse with normalized field names
    """
    total_amount = item.get("totalAmount")
    if total_amount is not None:
        try:
            total_amount = float(total_amount)
        except (ValueError, TypeError):
            total_amount = 0.0
    else:
        total_amount = 0.0

    # Normalize line items
    line_items = item.get("lineItems", [])
    if not isinstance(line_items, list):
        line_items = []

    return OrderResponse(
        orderId=cast(str, item.get("orderId", "")),
        campaignId=cast(str, item.get("campaignId", "")),
        profileId=cast(str, item.get("profileId", "")),
        customerName=cast(str, item.get("customerName", "")),
        customerPhone=item.get("customerPhone"),
        customerAddress=item.get("customerAddress"),
        lineItems=line_items,
        totalAmount=total_amount,
        paymentMethod=cast(str, item.get("paymentMethod", "")),
        notes=item.get("notes"),
        orderDate=cast(str, item.get("orderDate", "")),
        createdAt=cast(str, item.get("createdAt", "")),
        updatedAt=cast(str, item.get("updatedAt", "")),
    )


def build_list_response(items: List[Dict[str, Any]], builder: Any) -> List[Any]:
    """
    Build a list of responses using a builder function.

    Args:
        items: List of DynamoDB items
        builder: Builder function to apply to each item

    Returns:
        List of built responses
    """
    return [builder(item) for item in items]
