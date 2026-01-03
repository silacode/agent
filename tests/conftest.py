"""Shared fixtures and pytest configuration for the test suite."""

import pytest

# Configure pytest-asyncio to auto-detect async tests
pytest_plugins = ["pytest_asyncio"]


# Sample weather API response fixture
@pytest.fixture
def mock_weather_response():
    """Sample response from OpenWeatherMap API."""
    return {
        "coord": {"lon": 2.35, "lat": 48.85},
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d",
            }
        ],
        "base": "stations",
        "main": {
            "temp": 293.15,
            "feels_like": 292.5,
            "temp_min": 291.15,
            "temp_max": 295.15,
            "pressure": 1015,
            "humidity": 60,
        },
        "visibility": 10000,
        "wind": {"speed": 3.5, "deg": 180},
        "clouds": {"all": 0},
        "dt": 1700000000,
        "sys": {
            "type": 2,
            "id": 2012208,
            "country": "FR",
            "sunrise": 1699950000,
            "sunset": 1699990000,
        },
        "timezone": 3600,
        "id": 2988507,
        "name": "Paris",
        "cod": 200,
    }


# Sample Tavily search response fixture
@pytest.fixture
def mock_search_response():
    """Sample response from Tavily search API."""
    return {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "This is the first test result content.",
                "score": 0.95,
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "content": "This is the second test result content.",
                "score": 0.85,
            },
        ],
        "response_time": 0.5,
    }


# Fixture to temporarily override config values
@pytest.fixture
def mock_api_keys(monkeypatch):
    """Set mock API keys for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("WEATHER_API_KEY", "test-weather-key")
    monkeypatch.setenv("TAVILY-API-KEY", "test-tavily-key")
