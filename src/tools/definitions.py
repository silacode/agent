# Tool schemas in OpenAI function calling format

weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current and forecast weather data for a location using latitude and longitude coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude of the location (-90 to 90)",
                },
                "lon": {
                    "type": "number",
                    "description": "Longitude of the location (-180 to 180)",
                },
                "exclude": {
                    "type": "string",
                    "description": "Parts to exclude from response (comma-separated). Options: current, minutely, hourly, daily, alerts",
                    "default": "",
                },
            },
            "required": ["lat", "lon"],
        },
    },
}

# ... existing code ...

web_search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information on any topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}

# List of all available tools
tools = [weather_tool, web_search_tool]
