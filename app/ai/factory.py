import os

from app.ai.gemini_client import GeminiAIClient
from app.ai.mock_client import MockAIClient


def create_ai_client():

    provider = os.getenv(
        "AI_PROVIDER",
        "mock",
    ).lower()

    if provider == "gemini":
        return GeminiAIClient()

    return MockAIClient()
