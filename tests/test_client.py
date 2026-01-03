"""Tests for the client module."""

import pytest
from unittest.mock import patch
from openai import AsyncOpenAI

from src.client import get_client


class TestGetClient:
    """Tests for the get_client function."""

    def test_raises_when_api_key_empty(self):
        """Test that ValueError is raised when API key is empty."""
        with patch("src.client.config") as mock_config:
            mock_config.api_key = ""

            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
                get_client()

    def test_raises_when_api_key_none(self):
        """Test that ValueError is raised when API key is None-ish."""
        with patch("src.client.config") as mock_config:
            mock_config.api_key = None

            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
                get_client()

    def test_returns_async_openai_client_when_configured(self):
        """Test that AsyncOpenAI client is returned when API key is set."""
        with patch("src.client.config") as mock_config:
            mock_config.api_key = "test-api-key"

            client = get_client()

            assert isinstance(client, AsyncOpenAI)

    def test_client_uses_provided_api_key(self):
        """Test that the client is initialized with the correct API key."""
        with patch("src.client.config") as mock_config:
            mock_config.api_key = "my-secret-key"

            client = get_client()

            # The API key is stored internally
            assert client.api_key == "my-secret-key"

