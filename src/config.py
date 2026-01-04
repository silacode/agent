# Configuration and settings
import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh"]


@dataclass
class OpenAIConfig:
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-5-nano"
    max_tokens: int = 2048
    reasoning_effort: ReasoningEffort = "medium"


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
