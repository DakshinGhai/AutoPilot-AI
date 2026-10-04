import json
import os
import re

from dotenv import load_dotenv
from google import genai

from app.models.recovery_ai import (
    RecoverySelectionRequest,
    RecoverySelectionResponse,
)

load_dotenv()


class GeminiRecoveryAIClient:

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.client = genai.Client(api_key=self.api_key)

    async def select_recovery_candidate(
        self,
        request: RecoverySelectionRequest,
    ) -> RecoverySelectionResponse:

        if not request.candidates:
            raise ValueError("No recovery candidates available.")

        prompt = self._build_prompt(request)

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return self._parse_response(
            response.text,
            request,
        )

    @staticmethod
    def _build_prompt(
        request: RecoverySelectionRequest,
    ) -> str:

        candidates = [
            candidate.model_dump(exclude_none=True) for candidate in request.candidates
        ]

        payload = {
            "test_step": request.test_step,
            "target": request.target,
            "original_error": request.original_error,
            "page_url": request.page_url,
            "page_title": request.page_title,
            "candidates": candidates,
        }

        return f"""
You are an AI recovery selector for a browser
test automation framework.

Your ONLY task is to select the best recovery
candidate from the candidates supplied below.

STRICT RULES:

1. You MUST select an existing candidate_id.
2. NEVER invent a candidate_id.
3. NEVER create a new locator.
4. NEVER modify locator_value.
5. NEVER generate CSS, XPath, role, text, or any
   other selector.
6. Use the semantic evidence, validation state,
   target and original failure to choose.
7. Prefer candidates that are:
   - valid
   - unique
   - visible
   - enabled
   - semantically related to the target
8. Return ONLY valid JSON.
9. confidence must be between 0 and 1.

Required JSON format:

{{
  "selected_candidate_id": "existing candidate id",
  "reason": "short explanation",
  "confidence": 0.0
}}

Recovery context:

{json.dumps(payload, indent=2)}
"""

    @staticmethod
    def _parse_response(
        response_text: str,
        request: RecoverySelectionRequest,
    ) -> RecoverySelectionResponse:

        cleaned = response_text.strip()

        # Handle accidental markdown fences.
        if cleaned.startswith("```"):
            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

        try:
            data = json.loads(cleaned)

        except json.JSONDecodeError as exc:
            raise ValueError("Gemini returned invalid JSON.") from exc

        result = RecoverySelectionResponse(**data)

        candidate_ids = {candidate.candidate_id for candidate in request.candidates}

        if result.selected_candidate_id not in candidate_ids:
            raise ValueError("Gemini selected a candidate that " "does not exist.")

        return result
