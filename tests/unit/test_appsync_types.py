"""Tests for src/utils/appsync_types.py - AppSync event type utilities."""

from typing import Any, Dict

import pytest

from src.utils.appsync_types import (
    get_argument,
    get_argument_required,
    get_caller_id,
    get_caller_id_required,
    get_prev_result,
)


class TestGetCallerId:
    """Tests for get_caller_id function."""

    def test_returns_sub_from_identity(self) -> None:
        """Test extracting sub from identity."""
        event: Dict[str, Any] = {"identity": {"sub": "user-123"}}
        assert get_caller_id(event) == "user-123"

    def test_returns_none_when_no_identity(self) -> None:
        """Test returns None when identity is missing."""
        event: Dict[str, Any] = {}
        assert get_caller_id(event) is None

    def test_returns_none_when_no_sub(self) -> None:
        """Test returns None when sub is missing."""
        event: Dict[str, Any] = {"identity": {}}
        assert get_caller_id(event) is None


class TestGetCallerIdRequired:
    """Tests for get_caller_id_required function."""

    def test_returns_sub_from_identity(self) -> None:
        """Test extracting sub from identity."""
        event: Dict[str, Any] = {"identity": {"sub": "user-123"}}
        assert get_caller_id_required(event) == "user-123"

    def test_raises_when_no_identity(self) -> None:
        """Test raises ValueError when identity is missing."""
        event: Dict[str, Any] = {}
        with pytest.raises(ValueError, match="Caller ID"):
            get_caller_id_required(event)

    def test_raises_when_no_sub(self) -> None:
        """Test raises ValueError when sub is missing."""
        event: Dict[str, Any] = {"identity": {}}
        with pytest.raises(ValueError, match="Caller ID"):
            get_caller_id_required(event)


class TestGetArgument:
    """Tests for get_argument function."""

    def test_returns_argument_value(self) -> None:
        """Test extracting argument value."""
        event: Dict[str, Any] = {"arguments": {"name": "test-value"}}
        assert get_argument(event, "name") == "test-value"

    def test_returns_default_when_missing(self) -> None:
        """Test returns default when argument is missing."""
        event: Dict[str, Any] = {"arguments": {}}
        assert get_argument(event, "name", "default") == "default"

    def test_returns_none_when_no_arguments(self) -> None:
        """Test returns None when arguments is missing."""
        event: Dict[str, Any] = {}
        assert get_argument(event, "name") is None


class TestGetArgumentRequired:
    """Tests for get_argument_required function."""

    def test_returns_argument_value(self) -> None:
        """Test extracting argument value."""
        event: Dict[str, Any] = {"arguments": {"name": "test-value"}}
        assert get_argument_required(event, "name") == "test-value"

    def test_raises_when_missing(self) -> None:
        """Test raises ValueError when argument is missing."""
        event: Dict[str, Any] = {"arguments": {}}
        with pytest.raises(ValueError, match="Argument 'name' is required"):
            get_argument_required(event, "name")

    def test_raises_when_no_arguments(self) -> None:
        """Test raises ValueError when arguments is missing."""
        event: Dict[str, Any] = {}
        with pytest.raises(ValueError, match="Argument 'name' is required"):
            get_argument_required(event, "name")


class TestGetPrevResult:
    """Tests for get_prev_result function."""

    def test_returns_prev_result(self) -> None:
        """Test extracting previous result."""
        event: Dict[str, Any] = {"prev": {"result": {"ownerAccountId": "user-123"}}}
        assert get_prev_result(event) == {"ownerAccountId": "user-123"}

    def test_returns_empty_dict_when_no_prev(self) -> None:
        """Test returns empty dict when prev is missing."""
        event: Dict[str, Any] = {}
        assert get_prev_result(event) == {}

    def test_returns_empty_dict_when_no_result(self) -> None:
        """Test returns empty dict when result is missing."""
        event: Dict[str, Any] = {"prev": {}}
        assert get_prev_result(event) == {}
