"""Tests for exception handling in profile sharing handlers.

NOTE: Tests only cover remaining Lambda function (create_profile_invite).
Tests for migrated functions (redeem_profile_invite, share_profile_direct) removed.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from src.handlers.profile_sharing import create_profile_invite
from src.utils.errors import AppError, ErrorCode


class TestExceptionHandling:
    """Tests for exception handling in Lambda handlers."""

    @patch("src.handlers.profile_sharing.get_table")
    def test_create_invite_database_error(
        self,
        mock_get_table: MagicMock,
        sample_profile_id: str,
        appsync_event: Dict[str, Any],
        lambda_context: Any,
    ) -> None:
        """Test that database errors are handled in create_invite."""
        # Mock table to raise exception
        mock_table = MagicMock()
        mock_table.get_item.side_effect = Exception("Database connection failed")
        mock_get_table.return_value = mock_table

        event = {
            **appsync_event,
            "arguments": {
                "profileId": sample_profile_id,
                "permissions": ["READ"],
            },
        }

        with pytest.raises(AppError) as exc_info:
            create_profile_invite(event, lambda_context)

        assert exc_info.value.error_code == ErrorCode.INTERNAL_ERROR


# NOTE: The following test methods have been REMOVED because the Lambda functions
# were migrated to AppSync resolvers:
#
# - test_redeem_invite_database_error: Function migrated to pipeline resolver (Phase 3.3)
# - test_share_direct_database_error: Function migrated to pipeline resolver (Phase 3.2)
# - test_revoke_share_database_error: Function migrated to VTL resolver (Phase 1.2)
#
# Exception handling in AppSync resolvers should be tested via integration tests.
# See docs/APPSYNC_TESTING_STRATEGY.md for testing approach.
