from openai import AsyncOpenAI
from src.config import config


def get_client() -> AsyncOpenAI:
    """Initialize and return the async OpenAI client."""
    if not config.api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    return AsyncOpenAI(api_key=config.api_key)
