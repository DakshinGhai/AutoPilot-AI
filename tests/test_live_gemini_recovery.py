import os

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


@pytest.mark.asyncio
async def test_live_gemini_recovery_selection():

    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not configured.")

    candidate_1 = CandidateContext(
        candidate_id="candidate-product",
        element_id="element-product",
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
        reason="Product button",
    )

    candidate_2 = CandidateContext(
        candidate_id="candidate-cart",
        element_id="element-cart",
        locator_type="role",
        locator_value="button:Cart",
        strategy="role",
        priority=90,
        visible=True,
        enabled=True,
        match_count=1,
        is_unique=True,
        is_valid=True,
        confidence=0.90,
        reason="Cart button",
    )

    request = RecoverySelectionRequest(
        test_step="Click Product",
        target="Product",
        original_error=("Original Product locator failed"),
        page_url="https://www.ikea.com/in/en/",
        page_title="IKEA India",
        candidates=[
            candidate_1,
            candidate_2,
        ],
    )

    client = GeminiRecoveryAIClient()

    result = await client.select_recovery_candidate(request)

    assert result.selected_candidate_id in {
        "candidate-product",
        "candidate-cart",
    }

    assert 0.0 <= result.confidence <= 1.0

    print(
        "\nGemini selected:",
        result.selected_candidate_id,
    )

    print(
        "Reason:",
        result.reason,
    )

    print(
        "Confidence:",
        result.confidence,
    )
