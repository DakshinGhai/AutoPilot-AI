import pytest

from app.ai.gemini_client import GeminiAIClient
from app.models.ai import (
    LocatorSelectionRequest,
)
from app.models.candidate_context import CandidateContext


def create_candidate(
    candidate_id: str,
    locator_type: str = "role",
):
    return CandidateContext(
        candidate_id=candidate_id,
        element_id="element-1",
        locator_type=locator_type,
        locator_value="button:Products",
        strategy="role",
        priority=90,
        visible=True,
        enabled=True,
        match_count=1,
        is_unique=True,
        is_valid=True,
        confidence=0.90,
        reason="Semantic role",
    )


def create_request():
    return LocatorSelectionRequest(
        test_step="Click the Products button",
        target="Products button",
        page_url="https://www.ikea.com/in/en/",
        page_title="IKEA India",
        candidates=[
            create_candidate("candidate-1"),
            create_candidate(
                "candidate-2",
                locator_type="text",
            ),
        ],
    )


class FakeResponse:

    def __init__(self, text):
        self.text = text


def test_gemini_response_is_parsed():

    request = create_request()

    response = FakeResponse("""
        {
            "selected_candidate_id": "candidate-1",
            "reason": "The role locator matches the semantic button.",
            "confidence": 0.95
        }
        """)

    result = GeminiAIClient._parse_response(
        response,
        request,
    )

    assert result.selected_candidate_id == "candidate-1"
    assert result.confidence == 0.95


def test_gemini_unknown_candidate_is_rejected():

    request = create_request()

    response = FakeResponse("""
        {
            "selected_candidate_id": "unknown",
            "reason": "Invalid candidate.",
            "confidence": 0.90
        }
        """)

    with pytest.raises(ValueError, match="not.*provided"):
        GeminiAIClient._parse_response(
            response,
            request,
        )


def test_gemini_invalid_json_is_rejected():

    request = create_request()

    response = FakeResponse("not valid json")

    with pytest.raises(
        ValueError,
        match="Invalid Gemini locator selection response",
    ):
        GeminiAIClient._parse_response(
            response,
            request,
        )


def test_gemini_empty_response_is_rejected():

    request = create_request()

    response = FakeResponse("")

    with pytest.raises(
        ValueError,
        match="empty response",
    ):
        GeminiAIClient._parse_response(
            response,
            request,
        )


def test_gemini_confidence_is_validated():

    request = create_request()

    response = FakeResponse("""
        {
            "selected_candidate_id": "candidate-1",
            "reason": "Valid candidate.",
            "confidence": 1.5
        }
        """)

    with pytest.raises(ValueError):
        GeminiAIClient._parse_response(
            response,
            request,
        )
