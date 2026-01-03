# Configuration and settings
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OpenAIConfig:
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-5-nano"
    max_tokens: int = 2048
    # Note: gpt-5 doesn't support temperature; reasoning.effort supports minimal/low/medium/high


@dataclass
class WeatherConfig:
    api_key: str = os.getenv("WEATHER_API_KEY", "")
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"


@dataclass
class TavilyConfig:
    api_key: str = os.getenv("TAVILY-API-KEY", "")


config = OpenAIConfig()
weather_config = WeatherConfig()
tavily_config = TavilyConfig()
