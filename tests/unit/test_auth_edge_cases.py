"""Tests for edge cases in authorization utilities."""

from unittest.mock import MagicMock, patch

import pytest

from src.utils.auth import check_profile_access


class TestAuthEdgeCases:
    """Tests for edge cases in authorization module."""

    def test_check_access_database_error_propagates(
        self,
        sample_account_id: str,
        sample_profile_id: str,
    ) -> None:
        """Test that database errors propagate from check_profile_access."""
        # Mock table to raise exception on query (V2 schema uses Query on profileId-index)
        mock_table = MagicMock()
        mock_table.query.side_effect = Exception("Database error")

        with patch("src.utils.auth.tables") as mock_tables:
            mock_tables.profiles = mock_table
            with pytest.raises(Exception, match="Database error"):
                check_profile_access(sample_account_id, sample_profile_id, "READ")
