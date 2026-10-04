import pytest

from app.ai.gemini_recovery_client import (
    GeminiRecoveryAIClient,
)

from app.models.candidate_context import (
    CandidateContext,
)

from app.models.recovery_ai import (
    RecoverySelectionRequest,
)


def create_request():

    candidate = CandidateContext(
        candidate_id="candidate-1",
        element_id="element-1",
        locator_type="role",
        locator_value="button:Product",
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

    return RecoverySelectionRequest(
        test_step="Click Product",
        target="Product",
        original_error="Locator timeout",
        page_url="https://example.com",
        page_title="Example",
        candidates=[candidate],
    )


def test_gemini_client_requires_api_key(monkeypatch):

    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="GEMINI_API_KEY",
    ):
        GeminiRecoveryAIClient(
            api_key=None,
        )


def test_build_prompt_contains_candidates():

    client = GeminiRecoveryAIClient(
        api_key="test-key",
    )

    request = create_request()

    prompt = client._build_prompt(request)

    assert "candidate-1" in prompt
    assert "button:Product" in prompt
    assert "Product" in prompt
    assert "NEVER create a new locator" in prompt


def test_parse_valid_response():

    client = GeminiRecoveryAIClient(
        api_key="test-key",
    )

    request = create_request()

    response = client._parse_response(
        """
        {
            "selected_candidate_id": "candidate-1",
            "reason": "The candidate matches the target.",
            "confidence": 0.95
        }
        """,
        request,
    )

    assert response.selected_candidate_id == "candidate-1"

    assert response.confidence == 0.95


def test_parse_markdown_json_response():

    client = GeminiRecoveryAIClient(
        api_key="test-key",
    )

    request = create_request()

    response = client._parse_response(
        """
        ```json
        {
            "selected_candidate_id": "candidate-1",
            "reason": "Semantic match.",
            "confidence": 0.91
        }
        ```
        """,
        request,
    )

    assert response.selected_candidate_id == "candidate-1"


def test_reject_unknown_candidate():

    client = GeminiRecoveryAIClient(
        api_key="test-key",
    )

    request = create_request()

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        client._parse_response(
            """
            {
                "selected_candidate_id": "unknown",
                "reason": "Invalid selection.",
                "confidence": 0.9
            }
            """,
            request,
        )
