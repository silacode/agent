# Tool execution logic
import httpx
from tavily import AsyncTavilyClient
from src.config import weather_config, tavily_config


async def get_weather(lat: float, lon: float, exclude: str = "") -> dict:
    """
    Fetch weather data from OpenWeatherMap One Call API.

    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        exclude: Comma-separated parts to exclude (current, minutely, hourly, daily, alerts)

    Returns:
        Weather data as a dictionary
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": weather_config.api_key,
    }

    if exclude:
        params["exclude"] = exclude

    async with httpx.AsyncClient() as client:
        response = await client.get(weather_config.base_url, params=params)
        response.raise_for_status()
        return response.json()


async def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web using Tavily API.

    Args:
        query: The search query
        max_results: Maximum number of results to return

    Returns:
        Search results as a dictionary
    """
    client = AsyncTavilyClient(api_key=tavily_config.api_key)
    response = await client.search(query=query, max_results=max_results)
    return response


async def handle_tool_call(name: str, arguments: dict) -> dict:
    """
    Route tool calls to their respective handlers.

    Args:
        name: Name of the tool to execute
        arguments: Arguments for the tool

    Returns:
        Result from the tool execution
    """
    handlers = {
        "get_weather": get_weather,
        "web_search": web_search,
    }

    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")

    return await handlers[name](**arguments)
