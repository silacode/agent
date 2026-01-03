"""Tests for tool handlers - routing and API mocking."""

import pytest
import respx
from httpx import Response
from unittest.mock import AsyncMock, patch

from src.tools.handlers import get_weather, web_search, handle_tool_call
from src.config import weather_config


class TestHandleToolCall:
    """Tests for the handle_tool_call routing function."""

    async def test_routes_to_get_weather(self, mock_weather_response):
        """Test that get_weather is correctly routed."""
        with respx.mock:
            respx.get(weather_config.base_url).mock(
                return_value=Response(200, json=mock_weather_response)
            )

            result = await handle_tool_call(
                "get_weather", {"lat": 48.85, "lon": 2.35}
            )

            assert result["name"] == "Paris"
            assert "weather" in result

    async def test_routes_to_web_search(self, mock_search_response):
        """Test that web_search is correctly routed."""
        with patch("src.tools.handlers.AsyncTavilyClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search.return_value = mock_search_response
            mock_client_class.return_value = mock_client

            result = await handle_tool_call(
                "web_search", {"query": "test query", "max_results": 5}
            )

            assert result["query"] == "test query"
            assert len(result["results"]) == 2

    async def test_raises_for_unknown_tool(self):
        """Test that unknown tool raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
            await handle_tool_call("unknown_tool", {})

    async def test_raises_for_empty_tool_name(self):
        """Test that empty tool name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool:"):
            await handle_tool_call("", {})


class TestGetWeather:
    """Tests for the get_weather function with mocked HTTP."""

    async def test_constructs_correct_url_params(self, mock_weather_response):
        """Test that correct URL params are constructed."""
        with respx.mock:
            route = respx.get(weather_config.base_url).mock(
                return_value=Response(200, json=mock_weather_response)
            )

            await get_weather(lat=48.85, lon=2.35)

            assert route.called
            request = route.calls[0].request
            assert "lat=48.85" in str(request.url)
            assert "lon=2.35" in str(request.url)

    async def test_includes_exclude_param_when_provided(self, mock_weather_response):
        """Test that exclude param is included when provided."""
        with respx.mock:
            route = respx.get(weather_config.base_url).mock(
                return_value=Response(200, json=mock_weather_response)
            )

            await get_weather(lat=48.85, lon=2.35, exclude="minutely,hourly")

            request = route.calls[0].request
            assert "exclude=minutely" in str(request.url) or "exclude=minutely%2Chourly" in str(request.url)

    async def test_returns_parsed_json_response(self, mock_weather_response):
        """Test that JSON response is correctly parsed."""
        with respx.mock:
            respx.get(weather_config.base_url).mock(
                return_value=Response(200, json=mock_weather_response)
            )

            result = await get_weather(lat=48.85, lon=2.35)

            assert result["name"] == "Paris"
            assert result["main"]["temp"] == 293.15
            assert result["weather"][0]["description"] == "clear sky"

    async def test_raises_on_http_error(self):
        """Test that HTTP errors are raised."""
        with respx.mock:
            respx.get(weather_config.base_url).mock(
                return_value=Response(404, json={"message": "Not found"})
            )

            with pytest.raises(Exception):  # httpx.HTTPStatusError
                await get_weather(lat=0, lon=0)

    async def test_raises_on_server_error(self):
        """Test that server errors are raised."""
        with respx.mock:
            respx.get(weather_config.base_url).mock(
                return_value=Response(500, json={"message": "Server error"})
            )

            with pytest.raises(Exception):
                await get_weather(lat=0, lon=0)


class TestWebSearch:
    """Tests for the web_search function with mocked Tavily client."""

    async def test_passes_query_and_max_results(self, mock_search_response):
        """Test that query and max_results are passed correctly."""
        with patch("src.tools.handlers.AsyncTavilyClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search.return_value = mock_search_response
            mock_client_class.return_value = mock_client

            await web_search(query="test query", max_results=10)

            mock_client.search.assert_called_once_with(
                query="test query", max_results=10
            )

    async def test_uses_default_max_results(self, mock_search_response):
        """Test that default max_results is used when not specified."""
        with patch("src.tools.handlers.AsyncTavilyClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search.return_value = mock_search_response
            mock_client_class.return_value = mock_client

            await web_search(query="test query")

            mock_client.search.assert_called_once_with(
                query="test query", max_results=5
            )

    async def test_returns_response_dict(self, mock_search_response):
        """Test that response dict is returned correctly."""
        with patch("src.tools.handlers.AsyncTavilyClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.search.return_value = mock_search_response
            mock_client_class.return_value = mock_client

            result = await web_search(query="test query")

            assert result["query"] == "test query"
            assert len(result["results"]) == 2
            assert result["results"][0]["title"] == "Test Result 1"

