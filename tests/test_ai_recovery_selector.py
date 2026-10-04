import pytest

from app.ai.mock_recovery_client import (
    MockRecoveryAIClient,
)

from app.models.candidate_context import (
    CandidateContext,
)

from app.recovery.ai_recovery_selector import (
    AIRecoverySelector,
)


def create_candidate(
    candidate_id: str,
) -> CandidateContext:

    return CandidateContext(
        candidate_id=candidate_id,
        element_id="product-1",
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
        reason="Valid recovery candidate",
    )


@pytest.mark.asyncio
async def test_ai_recovery_selector_returns_selected_candidate():

    candidates = [
        create_candidate("candidate-1"),
        create_candidate("candidate-2"),
    ]

    client = MockRecoveryAIClient(selected_candidate_id="candidate-2")

    selector = AIRecoverySelector(client)

    response, selected = await selector.select(
        test_step="Click Product",
        target="Product",
        original_error="Locator click failed.",
        candidates=candidates,
        page_url="https://www.ikea.com/in/en/",
        page_title="IKEA",
    )

    assert response.selected_candidate_id == "candidate-2"

    assert selected.candidate_id == ("candidate-2")


@pytest.mark.asyncio
async def test_ai_recovery_selector_rejects_empty_candidates():

    client = MockRecoveryAIClient()

    selector = AIRecoverySelector(client)

    with pytest.raises(
        ValueError,
        match="without candidates",
    ):

        await selector.select(
            test_step="Click Product",
            target="Product",
            original_error="Locator failed.",
            candidates=[],
        )


@pytest.mark.asyncio
async def test_ai_recovery_selector_rejects_unknown_ai_candidate():

    candidates = [
        create_candidate("candidate-1"),
    ]

    client = MockRecoveryAIClient(selected_candidate_id="unknown")

    selector = AIRecoverySelector(client)

    with pytest.raises(
        ValueError,
        match="Selected recovery candidate does not exist",
    ):

        await selector.select(
            test_step="Click Product",
            target="Product",
            original_error="Locator failed.",
            candidates=candidates,
        )


@pytest.mark.asyncio
async def test_ai_recovery_selector_preserves_ai_response():

    candidates = [
        create_candidate("candidate-1"),
    ]

    client = MockRecoveryAIClient(selected_candidate_id="candidate-1")

    selector = AIRecoverySelector(client)

    response, selected = await selector.select(
        test_step="Click Product",
        target="Product",
        original_error="Locator failed.",
        candidates=candidates,
    )

    assert response.reason
    assert response.confidence == 0.90

    assert selected.candidate_id == ("candidate-1")
