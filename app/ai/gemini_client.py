import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.ai.prompts import build_locator_selection_prompt
from app.models.ai import (
    LocatorSelectionRequest,
    LocatorSelectionResponse,
)

load_dotenv()


class GeminiAIClient:
    """
    Real Gemini implementation of the AIClient protocol.

    Gemini is allowed to select only from browser-generated candidates.
    It must not invent selectors.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client=None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        self.model = model or os.getenv("GEMINI_MODEL")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        if not self.model:
            raise ValueError("GEMINI_MODEL is not configured")

        self.client = client or genai.Client(api_key=self.api_key)

    async def select_locator(
        self,
        request: LocatorSelectionRequest,
    ) -> LocatorSelectionResponse:

        if not request.candidates:
            raise ValueError("Cannot select locator without candidates")

        prompt = build_locator_selection_prompt(request)

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=LocatorSelectionResponse,
                temperature=0,
            ),
        )

        return self._parse_response(response, request)

    @staticmethod
    def _parse_response(
        response,
        request: LocatorSelectionRequest,
    ) -> LocatorSelectionResponse:

        response_text = getattr(
            response,
            "text",
            None,
        )

        if not response_text:
            raise ValueError("Gemini returned an empty response")

        try:
            result = LocatorSelectionResponse.model_validate_json(response_text)
        except Exception as exc:
            raise ValueError(
                f"Invalid Gemini locator selection response: {exc}"
            ) from exc

        candidate_ids = {candidate.candidate_id for candidate in request.candidates}

        if result.selected_candidate_id not in candidate_ids:
            raise ValueError(
                "Gemini selected a candidate that was not " "provided in the request"
            )

        return result
