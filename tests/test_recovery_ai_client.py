import pytest

from app.ai.mock_recovery_client import (
    MockRecoveryAIClient,
)

from app.models.candidate_context import (
    CandidateContext,
)

from app.models.recovery_ai import (
    RecoverySelectionRequest,
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


def create_request(
    candidates,
) -> RecoverySelectionRequest:

    return RecoverySelectionRequest(
        test_step="Click Product",
        target="Product",
        original_error=("Original locator failed."),
        page_url=("https://www.ikea.com/in/en/"),
        page_title="IKEA",
        candidates=candidates,
    )


@pytest.mark.asyncio
async def test_mock_recovery_ai_selects_first_candidate():

    candidates = [
        create_candidate("candidate-1"),
        create_candidate("candidate-2"),
    ]

    request = create_request(candidates)

    client = MockRecoveryAIClient()

    response = await client.select_recovery_candidate(request)

    assert response.selected_candidate_id == "candidate-1"

    assert response.confidence == 0.90
    assert response.reason


@pytest.mark.asyncio
async def test_mock_recovery_ai_selects_requested_candidate():

    candidates = [
        create_candidate("candidate-1"),
        create_candidate("candidate-2"),
    ]

    request = create_request(candidates)

    client = MockRecoveryAIClient(selected_candidate_id="candidate-2")

    response = await client.select_recovery_candidate(request)

    assert response.selected_candidate_id == "candidate-2"


@pytest.mark.asyncio
async def test_mock_recovery_ai_rejects_unknown_candidate():

    candidates = [
        create_candidate("candidate-1"),
    ]

    request = create_request(candidates)

    client = MockRecoveryAIClient(selected_candidate_id="unknown")

    with pytest.raises(ValueError, match="does not exist"):

        await client.select_recovery_candidate(request)


@pytest.mark.asyncio
async def test_mock_recovery_ai_rejects_empty_candidates():

    request = create_request([])

    client = MockRecoveryAIClient()

    with pytest.raises(
        ValueError,
        match="No recovery candidates",
    ):

        await client.select_recovery_candidate(request)
